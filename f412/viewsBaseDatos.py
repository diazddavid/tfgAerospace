import datetime
from datetime import date

from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.template.loader import get_template
from django.template import Context

from f412.models import *
from f412.toString import *
from f412.manageDB import initEstadoDB, initSeccionDB, initProgramaDB, initTypeUser
from f412.mails import *

from django.contrib.auth import authenticate
from django.contrib.auth.views import logout
# import win32com.client as win32


# Declaro constantes, con try except para evitar fallos en el caso de que no existan en la base de datos
# si no existen y por lo tanto salta una excepcion los creamos, pues sabemos que estos están si o si
try:
    PROGRAMA_380 = Programa.objects.get(name = "380")
    PROGRAMA_350 = Programa.objects.get(name = "350")
except Programa.DoesNotExist:
    initProgramaDB()
    PROGRAMA_380 = Programa.objects.get(name = "380")
    PROGRAMA_350 = Programa.objects.get(name = "350")

try:
    SECTION_380 = Seccion.objects.get(programa = PROGRAMA_380)
    SECTION_APT1 = Seccion.objects.get(name = "APT1")
    SECTION_APT2 = Seccion.objects.get(name = "APT2")
    SECTION_APT3 = Seccion.objects.get(name = "APT3")
    SECTION_APT4 = Seccion.objects.get(name = "APT4")
    SECTION_APT5 = Seccion.objects.get(name = "APT5")
except Seccion.DoesNotExist:
    initSeccionDB()
    SECTION_380 = Seccion.objects.get(programa = PROGRAMA_380)
    SECTION_APT1 = Seccion.objects.get(name = "APT1")
    SECTION_APT2 = Seccion.objects.get(name = "APT2")
    SECTION_APT3 = Seccion.objects.get(name = "APT3")
    SECTION_APT4 = Seccion.objects.get(name = "APT4")
    SECTION_APT5 = Seccion.objects.get(name = "APT5")

try:
    ACTIVE_Status = Estado.objects.get(name = "Activo")
    GRANTED_Status = Estado.objects.get(name = "Concedido")
    REJECTED_Status = Estado.objects.get(name = "Rechazado")
    VALIDATED_Status = Estado.objects.get(name = "Validado")
except Estado.DoesNotExist:
    initEstadoDB()
    ACTIVE_Status = Estado.objects.get(name = "Activo")
    GRANTED_Status = Estado.objects.get(name = "Concedido")
    REJECTED_Status = Estado.objects.get(name = "Rechazado")
    VALIDATED_Status = Estado.objects.get(name = "Validado")
  
try:
    TYPE_ME = tipoUsuario.objects.get(name = "ME")
except:
    initTypeUser()

################################################## FUNCIONES #################################################

#Funcion para obtener contexto basico necesario en la template base.html
def getBasicContext(request):
    myContext = Context({'user': request.user})
    myContext['myPath'] = request.path
    try:
        myContext['myUser'] = myUser.objects.get(user = request.user)
    except:
        print("Usuario No Encontrado")
    return myContext

def returnError(request, message):
    myContext = getBasicContext(request)
    myContext["errorMessage"] = message
    template = get_template("html/base.html")
    return HttpResponse(template.render(myContext))

def toFloat(toConvert):
    return float(toConvert.replace(',','.'))

def totalH(f412List, typeH):
    toReturn = 0
    for f412 in f412List:
        if typeH == "con" or f412.horasAntiguas == "":
            toReturn = toFloat(f412.horas) + toReturn
        else:
            toReturn = toFloat(f412.horasAntiguas) + toReturn
    return str(toReturn)[:5]

# Vista para página principal y paginas que no estén en el resto de reglas
@csrf_exempt
def home(request, aux):
#    print("\n" + request.META['HTTP_USER_AGENT'] + "\n")
    myContext = getBasicContext(request)
    if aux == "" or aux == "filtroFecha":
        if aux == "filtroFecha":
            minDate = parseDate(request.POST["fromDate"])
            maxDate = parseDate(request.POST["toDate"])
            F412List = F412.objects.filter(Fecha__lte=maxDate)
            F412List = F412List.filter(Fecha__gte=minDate)
        else:
            F412List = F412.objects.all()
        template = get_template("html/root.html")
        for status in Estado.objects.all():
            if status.name == "Activo":
                statName = "act"
            elif status.name == "Concedido":
                statName = "gran"
            elif status.name == "Rechazado":
                statName = "reject"
            else:
                statName = "val"
            for section in Seccion.objects.all():
                if section.programa.name == "350":
                    sectName = "350" + section.name
                else:
                    sectName = section.name
                myContext[statName + sectName] = F412List.filter(Estado = status).filter(seccion = section).count()
                myContext[statName + sectName + "Horas"] = totalH(F412List.filter(Estado = status).filter(seccion = section), "")
                myContext[statName + sectName + "HorasConcedidas"] = totalH(F412List.filter(Estado = status).filter(seccion = section), "con")
        myContext['errorMessage'] = "Pagina principal"
        myContext['date'] = dateToString(datetime.datetime.now())
    else:
        template = get_template("html/base.html")
        myContext['errorMessage'] = "Pagina no encontrada"
    return HttpResponse(template.render(myContext))

# Funcion especifica para servir el formulario del 350
@csrf_exempt
def serveForm350(request):
    sectionList = Seccion.objects.filter(programa = PROGRAMA_350)
    areaList = []
    desvList = []
    SGMList = []
    # Preparo la lista de una forma adecuada para poder manejarla con javascript en la templates
    #Para poder hacer luego selección dinámica
    for section in sectionList:
        areas = Area.objects.filter(seccion = section)
        for area in areas:
            areaList.append(section.name + "." + area.name)
        desvs = Defecto.objects.filter(seccion = section)
        for desv in desvs:
            desvList.append(section.name + "." + desv.name)
        everySGM = SGM.objects.all()
        for sgm in everySGM:
            if section in sgm.seccion.all():
                SGMList.append(section.name + "." + sgm.number)

    #Preparo el contexto
    myContext = getBasicContext(request)
    reqUser = myUser.objects.get(user = request.user)
    areaUser = []
    for sectionArea in reqUser.seccion.all():
        for area in Area.objects.filter(seccion = sectionArea):
            areaUser.append(area)
    if len(areaUser) == 0:
        areaUser = Area.objects.filter(seccion = SECTION_APT1 )    
    myContext['areaUserSection'] = areaUser
    desvUser = Defecto.objects.filter(seccion__programa = PROGRAMA_350).filter(seccion = reqUser.seccion.all())
    if desvUser.count() == 0:
        desvUser = Defecto.objects.filter(seccion = SECTION_APT1 )
    PNList = []
    for parNumber in PN.objects.filter(programa = PROGRAMA_350):
        try:
            PNList.append(parNumber.Designacion.name + "." + parNumber.name)
        except Designacion.DoesNotExist:
            continue    
    myContext['desvUser'] = desvUser
    myContext['sgmUser'] = SGM.objects.filter(seccion = reqUser.seccion.all())
    myContext['program'] = Programa.objects.get(name = "350")
    myContext['sectionList'] = sectionList
    myContext['componentList'] = Componente.objects.filter(programa = PROGRAMA_350)
    myContext['piezaList'] = Pieza.objects.all()
    myContext['areaList'] = areaList
    myContext['desvList'] = desvList
    myContext['date'] = dateToString(date.today())
    myContext['SGMList'] = SGMList
    myContext['PNList'] = PNList

    return myContext

# Vista para servir el formulario para f412 del 380
@csrf_exempt
def serveForm380(request):
    alldesigna = Designacion.objects.filter(Componente__programa = PROGRAMA_380)
    designaList = []

    #Preparo el formato para poder manejarlo facilmente con javascript
    for designa in alldesigna:
        try:
            designaList.append(designa.Componente.name + "." + designa.name)
        except Componente.DoesNotExist:
            continue

    allPN = PN.objects.filter(programa = PROGRAMA_380)
    PNList = []
    #Preparo el formato para poder manejarlo facilmente con javascript
    for parNumber in allPN:
        try:
            PNList.append(parNumber.Designacion.name + "." + parNumber.name)
        except Designacion.DoesNotExist:
            continue

    areaList = Area.objects.filter(seccion =SECTION_380)
    defectList = Defecto.objects.filter(seccion =SECTION_380)
    SGMList = []
    for sgm in SGM.objects.all():
        if SECTION_380 in sgm.seccion.all():
            SGMList.append(sgm)
    #Preparo el contexto
    myContext = getBasicContext(request)
    myContext['program'] = Programa.objects.get(name ="380")
    myContext['sectionList'] = Seccion.objects.filter(programa = PROGRAMA_380)
    myContext['componentList'] = Componente.objects.filter(programa = PROGRAMA_380)
    myContext['designaList'] = designaList
    myContext['PNList'] = PNList
    myContext['areaList'] = areaList
    myContext['defectList'] = defectList
    myContext['date'] = dateToString(date.today())
    myContext['SGMList'] = SGMList

    return myContext

# Funcion que según el programa sirve un formulario u otro
def serveForm(program, request):
    if program == "380":
        toReturn = serveForm380(request)
    elif program == "350":
        toReturn = serveForm350(request)
    else:
        print("Inalcanzable")
        toReturn = Context()
    user = request.user
    myCurrentUser = myUser.objects.get(user = user)
    if myCurrentUser.programa.all().count() > 1:
        for program in myCurrentUser.programa.all():
            fieldName = "program" + program.name
            toReturn[fieldName] = True
    elif myCurrentUser.typeUser.name == "ME":
        for program in Programa.objects.all():
            fieldName = "program" + program.name
            toReturn[fieldName] = True
    return toReturn

def serveFormGeneric(request):
    user = request.user
    myCurrentUser = myUser.objects.get(user = user)
    return newF412(request, myCurrentUser.programa.all()[0].name)

#Funcion que devuelve un par number especifico, para el caso del 350 donde no hay desplegable y puedeCrear
#llegar cualquier PN, si este no existe asignamos un por defecto
def getParNumber(request, component):
    print("\n\nGET PAR NUMBER")
    try:
        print("QUE NO, QUE ENTRA AQUI\n\n")
        parNumber = PN.objects.get(name = request.POST["parNumber"])
    except PN.DoesNotExist:
        print("ENTRA AQUI\n\n")
        try:
            parNumber = PN.objects.get(name = "default")
        except PN.DoesNotExist:
            defaultDesigna = Designacion(name = "default", Componente = component)
            defaultDesigna.save()
            parNumber = PN(name = "default", programa = PROGRAMA_350, Designacion = defaultDesigna)
            parNumber.save()
    return parNumber

#Vista correspondiente a todos los F412, tanto para recibir el formulario como para enviarlo
#Depende del método
@csrf_exempt
def newF412(request, program):
    template = get_template("html/" + program + "form.html")
    if request.method == "GET":
        toReturn = serveForm(program,request)
        return HttpResponse(template.render(toReturn))
    elif request.method == "POST":
        #Para evitar que se puedan pedir nuevos F412 sin ser usuario logueado
        try:
            currentUser = myUser.objects.get(user = request.user)
        except:
            currentUser = None
            Error = "Usuario no identificado, Inicie sesion"
            print(request.user.username) #Traza
        program = Programa.objects.get(name = program)
        section = Seccion.objects.get(name = request.POST["section"])
        #Para evitar que un usuario de APT4 ponga f412 en 380 por ejemplo, a excepcion de los ME UNIT
        #Todos los ME UNIT podrán crear en todos y aceptar o rechazar
        if (section in currentUser.seccion.all() and currentUser.typeUser.name != "Subcontrata") or currentUser.typeUser.name == "ME":
            component = Componente.objects.get(name = request.POST["Component"])
            parNumber = getParNumber(request,component)
            area = Area.objects.get(name = request.POST["Area"])
            f412date = date.today()
            defect = Defecto.objects.get(name = request.POST["Defect"])
            try:
                designa = Designacion.objects.get(name = request.POST["Designation"])
                a380 = True
            except:
                a380 = False
            try:
                part = Pieza.objects.get(name = request.POST["Pieza"])
                nAV = int(request.POST["nAV"])
            except:
                print("Pieza no encontrada, 380")
                nAV = 0
            Status = Estado.objects.get(name = "Activo")
            numH = request.POST["numH"]
            descp = request.POST["Descp"]
            SGMf412 = SGM.objects.get(number = request.POST["SGM"])
            #Por si hemos reseteado base de datos y es el primer f412
            try:
                myID = F412.objects.filter(seccion =section).latest('id').myID + 1
            except F412.DoesNotExist:
                myID = 1
            F412toSave = F412(programa = program, Componente = component, PN = parNumber, Area = area,
                            Defecto = defect, Fecha = f412date, Estado = Status,
                            Referencia = request.POST["Ref"], horas = numH, SGM = SGMf412,
                            Descripcion = descp, Usuario = currentUser, seccion =section,
                            LastChangeUser = currentUser, myID = myID, nAV = nAV)
            F412toSave.save()
            if a380:
                F412toSave.Designacion = designa
            else:
                F412toSave.Pieza = part
            F412toSave.save()
            sendMail("f412", F412toSave.id, currentUser.email)
            Error = "None"
        else:
            myID = 0
            Error = "No tiene permisos para crear en esta seccion"
        toReturn = serveForm(program.name, request)
        toReturn['newID'] = True
        toReturn['myID'] = myID
        toReturn["error"] = Error
        return HttpResponse(template.render(toReturn))
    else:
        return HttpResponse("Error OTRO")
    return HttpResponse("Inalcanzable")

#Para devolver las tablas de Activos, Rechazados y Aceptados, asi como los de todos los programas
def returnTable(f412List, request, program, isProgram, section, typePage,status):
    myContext = getBasicContext(request)
    myContext['F412list'] = f412List
    myContext['isProgram'] = isProgram
    myContext['program'] = program
    myContext['userSection'] = section
    myContext['Status'] = status
    if typePage == "act":
        myContext['activePage'] = True
    elif typePage == "val":
        myContext['validatedPage'] = True   
    if isProgram:
        programObject = Programa.objects.get(name = program)
        myContext['sectionList'] = Seccion.objects.filter(programa = programObject)
    template = get_template("html/tabla.html")
    return HttpResponse(template.render(myContext))

#Sirve en caso de que se quiera habilitar la aceptación multiple de usuarios
#@csrf_exempt
#def multipleAcept(request, section):
#    sectionObject = Seccion.objects.get(name = section)
#    for f412 in F412.objects.filter(seccion = sectionObject):
#        strToSearch = "accept" + str(f412.myID)
#        if strToSearch in request.POST:
#            changeStatus(f412, Estado.objects.get(name = "Aceptado"), "", request)
#        strToSearch = "preAccept" + str(f412.myID)
#        if strToSearch in request.POST:
#            changeStatus(f412, Estado.objects.get(name = "Pre-Aceptado"), "", request)
#    return HttpResponseRedirect(request.POST["next"])

#Preparacion servir tabla
#@csrf_exempt
#def serveTableStatus(request, section, status):
#    if  section == "350":
#        programName = "350"
#        sectionName = "Todos"
#        f412List = F412.objects.filter(Estado__name = status).filter(programa = PROGRAMA_350).order_by('Fecha').order_by('-myID')
#    else:
#        print(status)
#        section = Seccion.objects.get(name = section)
#        programName = section.programa.name
#        sectionName = section.name
#        f412List = F412.objects.filter(Estado__name = status).filter(seccion = section).order_by('Fecha').order_by('-myID')
#    return returnTable(f412List, request, programName, False, sectionName, "act", status)
#    

@csrf_exempt
def activeF412(request,section):
    if section == "Todos":
        f412List = F412.objects.filter(Estado = ACTIVE_Status).order_by('Fecha').order_by('-myID')
        programName = "Todos"
        sectionName = ""
    elif  section == "350":
        programName = "350"
        sectionName = "A350"
        f412List = F412.objects.filter(Estado = ACTIVE_Status).filter(programa = PROGRAMA_350).order_by('Fecha').order_by('-myID')
    else:
        section = Seccion.objects.get(name = section)
        programName = section.programa.name
        sectionName = section.name
        f412List = F412.objects.filter(Estado = ACTIVE_Status).filter(seccion = section).order_by('Fecha').order_by('-myID')
    return returnTable(f412List, request, programName, False, sectionName, "act", "Activos")

#Preparacion servir tabla
@csrf_exempt
def grantedF412(request,section):
    if section == "Todos":
        f412List = F412.objects.filter(Estado = GRANTED_Status).order_by('Fecha').order_by('-myID')
        programName = "Todos"
        sectionName = ""
    elif  section == "350":
        programName = "350"
        sectionName = "A350"
        f412List = F412.objects.filter(Estado = GRANTED_Status).filter(programa = PROGRAMA_350).order_by('Fecha').order_by('-myID')
    else:
        section = Seccion.objects.get(name = section)
        programName = section.programa.name
        sectionName = section.name
        f412List = F412.objects.filter(Estado = GRANTED_Status).filter(seccion = section).order_by('Fecha').order_by('-myID')
    return returnTable(f412List, request, programName, False, sectionName, "", "Concedidos")

#Preparacion servir tabla
@csrf_exempt
def rejectedF412(request,section):
    if section == "Todos":
        f412List = F412.objects.filter(Estado = REJECTED_Status).order_by('Fecha').order_by('-myID')
        programName = "Todos"
        sectionName = ""
    elif  section == "350":
        programName = "350"
        sectionName = "A350"
        f412List = F412.objects.filter(Estado = REJECTED_Status).filter(programa = PROGRAMA_350).order_by('Fecha').order_by('-myID')
    else:
        section = Seccion.objects.get(name = section)
        programName = section.programa.name
        sectionName = section.name
        f412List = F412.objects.filter(Estado = REJECTED_Status).filter(seccion = section).order_by('Fecha').order_by('-myID')
    return returnTable(f412List, request, programName, False, sectionName, "", "Rechazados")

#Preparacion servir tabla
@csrf_exempt
def validatedF412(request,section):
    if section == "Todos":
        f412List = F412.objects.filter(Estado = VALIDATED_Status).order_by('Fecha').order_by('-myID')
        programName = "Todos"
        sectionName = ""
    elif  section == "350":
        programName = "350"
        sectionName = "A350"
        f412List = F412.objects.filter(Estado = VALIDATED_Status).filter(programa = PROGRAMA_350).order_by('Fecha').order_by('-myID')
    else:
        section = Seccion.objects.get(name = section)
        programName = section.programa.name
        sectionName = section.name
        f412List = F412.objects.filter(Estado = VALIDATED_Status).filter(seccion = section).order_by('Fecha').order_by('-myID')
    return returnTable(f412List, request, programName, False, sectionName, "val", "Validados")

#Preparacion servir tabla
@csrf_exempt
def programF412(request,program):
    user = myUser.objects.get(user = request.user)
    if user.typeUser.name == "Subcontrata" or user.typeUser.name == "Operario":
        return returnError(request, "No tienes permisos para acceder")
    program = Programa.objects.get(name = program)
    if user.typeUser.name == "TL":
        f412List = F412.objects.filter(seccion = user.seccion.all()).order_by('-myID').order_by('-Fecha')
    else:
        f412List = F412.objects.filter(programa = program).order_by('-myID').order_by('-Fecha')
    return returnTable(f412List, request, program.name, True, "", "", "")

#Preparacion servir tabla, correspondiente a las distintas secciones del 350
@csrf_exempt
def programSectionF412(request,section):
    user = myUser.objects.get(user = request.user)
    if user.typeUser.name == "Subcontrata" or user.typeUser.name == "Operario":
        return returnError(request, "No tienes permisos para acceder")
    f412List = F412.objects.filter(seccion__name = section).order_by('-myID').order_by('-Fecha')
    if user.typeUser.name == "TL":
        f412List = f412List.filter(seccion = user.seccion.all())
    return returnTable(f412List, request, "350", True, section, "", "")

def getReasonTree(request):
    rt1Cod = request.POST['Level1hid']
    rt2Cod = request.POST['Level2hid']
    rt3Cod = request.POST['Level3hid']
    rt1 = reasonTreeField.objects.get(codigo = rt1Cod)
    rt2 = reasonTreeField.objects.filter(superior = rt1).get(codigo = rt2Cod)
    rt3 = reasonTreeField.objects.filter(superior = rt2).get(codigo = rt3Cod)
    reasonT = reasonTree.objects.filter(nivel2 = rt2, nivel3 = rt3)
    name = rt1Cod + "." + rt2Cod + "." + rt3Cod + ". "
    if reasonT.count() == 0:
        reasonT = reasonTree(nivel1 = rt1, nivel2 = rt2, nivel3 = rt3, shortName = name)
        reasonT.save()
        return reasonT
    else:
        return reasonT[0]

def changeStatus(f412, newStatus, action, request):
    f412.Estado = newStatus
    currentUser = myUser.objects.get(user = request.user)
    f412.LastChangeUser = currentUser
    if newStatus.name == "Concedido" or newStatus.name == "Validado":
        if request.POST["newH"] != "":
            f412.horasAntiguas = f412.horas
            f412.horas = request.POST["newH"]
        if f412.programa.name == "350":
            rt = getReasonTree(request)
            f412.reasonTree = rt
            if action != "":
                f412.descripcionAcortada = rt.shortName + action
            else:
               f412.descripcionAcortada = rt.shortName + f412.Descripcion
        else:
            f412.descripcionAcortada = action
    else:
        f412.accion = action 
    f412.save()
    if newStatus.name == "Rechazado":
        sendMail("f412", f412.id, currentUser.email)
    return

#Vista para cada F412 donde se muestra informacion más detallada que en las tablas
@csrf_exempt
def f412Page(request, sectionName, myID):
    f412 = F412.objects.filter(seccion = Seccion.objects.get(name = sectionName)).get(myID = myID)
    if f412.seccion.name == "380":
        a380 = True
    else:
        a380 = False
    if request.method == "POST":
        newStatus = Estado.objects.get(name = request.POST["newStatusForm"])
        action = request.POST["action"]
        changeStatus(f412, newStatus, action, request)
    myContext = getBasicContext(request)
    myContext['f412'] = f412
    myContext['statusList'] = Estado.objects.all()
    myContext['a380'] = a380
    myContext['date'] = dateToString(f412.Fecha)
    myContext['week'] = f412.Fecha.isocalendar()[1]
    myContext['level1RT'] = reasonTreeField.objects.filter(nivel = 1)
    myContext['level2RT'] = reasonTreeField.objects.filter(nivel = 2)
    myContext['level3RT'] = reasonTreeField.objects.filter(nivel = 3)
    template = get_template("html/f412A" + f412.programa.name + ".html")
    return HttpResponse(template.render(myContext))

#Funcion para cerrar sesion
@csrf_exempt
def logOut(request):
    logout(request)
    return HttpResponseRedirect("/")
