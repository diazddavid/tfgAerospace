import datetime
from datetime import date, timedelta

from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.template.loader import get_template
from django.template import Context

from f412.models import *
from f412.toString import *
from f412.manageDB import getAvList, initEstadoDB, initSeccionDB, initProgramaDB, initTypeUser, initCodCaus, checkPlane, updateGraph
from f412.mails import *

from django.contrib.auth import authenticate
from django.contrib.auth.views import logout

import f412.manageDB as manageDB

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

try:
    v10 = codCaus.objects.get(name = "V10")
except:
    initCodCaus()
################################################## FUNCIONES #################################################

#Funcion para obtener contexto basico necesario en la template base.html
def getBasicContext(request):
    return getContext(request, "Reparaciones")

def getBasicContextRep(request):
    return getContext(request, "Accidentales")

def getContext(request, mode):
    myContext = Context({'user': request.user})
    myContext["mode"] = mode
    myContext['myPath'] = request.path
    myContext["codCausList"] = codCaus.objects.all()
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
    try:
        return float(toConvert.replace(',','.'))
    except:
        return 0.0
    
def totalH(f412List, typeH):
    toReturn = 0
    is380 = False
    try:
        if f412List[0].programa.name == "380":
            is380 = True
    except:
        return 0.0
    for f412 in f412List:
        if (typeH == "con" or f412.horasAntiguas == "") and is380:
            toReturn = toFloat(f412.horas) + toReturn
        elif typeH == "con" or f412.horasAntiguas == "":
            toReturn = toFloat(f412.horasRecurrentes) + toReturn  
        else:
            if is380:
                toReturn = toFloat(f412.horasAntiguas) + toReturn
            else:
                toReturn = toFloat(f412.horasAntRec) + toReturn
    return str(toReturn)[:5]

def getHours(myContext, request, F412List):
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

    return myContext   

def totalHRep(hourList):
    toReturn = 0.0
    for rep in hourList:
        toReturn += toFloat(rep.horas)
    return toReturn    

@csrf_exempt
def repRoot(request):
#    AÑADIR FILTROFECHA
    myContext = getBasicContextRep(request)
    template = get_template("html/rootRep.html")
    
    myContext, repList = getDatesList(request, myContext, "rep")
    
    myContext["380num"] = repList.filter(programa__name = "380").count()
    myContext["380hour"] = totalHRep(repList.filter(programa__name = "380"))
    
    aptList = []
    for apt in Seccion.objects.filter(programa__name = "350"):
        toAdd = {}
        toAdd['name'] = apt.name
        toAdd["num"] = repList.filter(seccion = apt).count()
        toAdd['hour'] = totalHRep(Reparacion.objects.filter(seccion = apt))
        aptList.append(toAdd)
    myContext["repAPT"] = aptList    
        
    myContext["350num"] = repList.filter(programa__name = "350").count()
    myContext["350hour"] = totalHRep(repList.filter(programa__name = "350"))
    
    return HttpResponse(template.render(myContext))

def getDatesList(request, myContext, typeList):
    try:
        minDate = parseDate(request.POST["fromDate"])
        maxDate = parseDate(request.POST["toDate"])
        toFilter = True
    except:
        minDate = date.today()
        maxDate = date.today()
        toFilter = False
    
#    Chapuza
    if toFilter == True and typeList == "rep":
        repList = Reparacion.objects.filter(Fecha__lte = maxDate)
        repList = repList.filter(Fecha__gte = minDate)
    else:
        repList = Reparacion.objects.all()
        
    myContext['currentDate'] = dateToString(minDate)
    myContext['currentDate1'] = dateToString(maxDate)
    myContext["tomorrow"] = ""
    myContext['currentDay'] = ""
    myContext['yesterday'] = dateToString(date.today() - timedelta(1))         
    if maxDate == minDate and request.method != "GET" and dateToString(maxDate) != dateToString(date.today()):
        myContext['currentDay'] = dateToString(minDate)
        if minDate != date.today():
            myContext['yesterday'] = dateToString(minDate - timedelta(1))  
            myContext["tomorrow"] = dateToString(minDate + timedelta(1))
        else:
            myContext["tomorrow"] = ""   
    myContext['date'] = dateToString(datetime.datetime.now())
    
    return myContext, repList

# Vista para página principal y paginas que no estén en el resto de reglas
@csrf_exempt
def home(request, aux):
#     print("\n" + request.META['HTTP_USER_AGENT'] + "\n")
    myContext = getBasicContext(request)
    template = get_template("html/root.html")
    if aux == "" or aux == "filtroFecha":
        if aux == "filtroFecha":
            try:
                minDate = parseDate(request.POST["fromDate"])
                maxDate = parseDate(request.POST["toDate"])
                F412List = F412.objects.filter(Fecha__lte=maxDate)
                F412List = F412List.filter(Fecha__gte=minDate)
                myContext["filtro"] = True
            except:
                return HttpResponseRedirect("/")
        else:
            F412List = F412.objects.all()
            minDate = date.today()
            maxDate = date.today()
        myContext = getHours(myContext, request, F412List)
        myContext['page'] = "/"
        myContext, _ = getDatesList(request, myContext, "acc")

        try:
            user = myUser.objects.get(user = request.user)
            for section in user.seccion.all():
                myContext["show" + section.name] = True
        except:
            print("Usuario no encontrado")
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
        areas = Area.objects.filter(seccion = section).order_by("name")
        for area in areas:
            areaList.append(section.name + "." + area.name)
        desvs = Defecto.objects.filter(seccion = section).order_by("name")
        for desv in desvs:
            desvList.append(section.name + "." + desv.name)
        everySGM = SGM.objects.all().order_by("name")
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
            name = parNumber.Designacion.name + "." + parNumber.name
            name = name.replace("\n","")
            PNList.append(name)
        except Designacion.DoesNotExist:
            continue
    
    APT5CompList = []
    
    for compAPT5 in ComponenteAPT5.objects.all():
        APT5CompList.append(compAPT5.componente)
        
    myContext['compAPT5List'] = ComponenteAPT5.objects.all().order_by("name")
    myContext['APT5CompList'] = APT5CompList
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
    alldesigna = Designacion.objects.filter(Componente__programa = PROGRAMA_380).order_by("name")
    designaList = []

    #Preparo el formato para poder manejarlo facilmente con javascript
    for designa in alldesigna:
        try:
            designaList.append(designa.Componente.name + "." + designa.name)
        except Componente.DoesNotExist:
            continue

    allPN = PN.objects.filter(programa = PROGRAMA_380).order_by("name")
    PNList = []
    #Preparo el formato para poder manejarlo facilmente con javascript
    for parNumber in allPN:
        try:
            PNList.append(parNumber.Designacion.name + "." + parNumber.name)
        except Designacion.DoesNotExist:
            continue

    areaList = Area.objects.filter(seccion =SECTION_380).order_by("name")
    defectList = Defecto.objects.filter(seccion =SECTION_380).order_by("name")
    SGMList = []
    for sgm in SGM.objects.all().order_by("name"):
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

@csrf_exempt
# Funcion que según el programa sirve un formulario u otro
def serveForm(program, request):
    if program == "380":
        toReturn = serveForm380(request)
    elif program == "350":
        toReturn = serveForm350(request)
    else:
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

@csrf_exempt
def serveFormGeneric(request):
    user = request.user
    myCurrentUser = myUser.objects.get(user = user)
    if myCurrentUser.programa.all().count() == 0:
        template = get_template("html/380form.html")
        return HttpResponse(template.render(serveForm("380",request)))
    name = myCurrentUser.programa.all()[0].name
    template = get_template("html/" + name + "form.html")           
    return HttpResponse(template.render(serveForm(name, request)))

@csrf_exempt
def getContextFormRep(request, program):
    if program == "350":
        myContext = serveForm350(request)
        rt1 = reasonTreeField.objects.filter(nivel = 1)        
        myContext["rt2"] = reasonTreeField.objects.filter(nivel = 2) 
        myContext["rt3"] = reasonTreeField.objects.filter(nivel = 3) 
    elif program == "380":
        myContext = serveForm380(request)
        rt1 = []
        for rt in reasonTree.objects.filter(program__name = "380" ):
            rt1.append(rt.nivel1)
    myContext["rt1"] = rt1
    myContext["mode"] = "Accidentales"
    myContext["program380"] = True
    myContext["program350"] = True
    return myContext

@csrf_exempt
def serveFormRepProg(request, program):
    template = get_template("html/" + program + "form.html")
    return HttpResponse(template.render(getContextFormRep(request, program)))

@csrf_exempt
def serveFormRep(request):
    return serveFormRepProg(request, "350")

#Funcion que devuelve un par number especifico, para el caso del 350 donde no hay desplegable y puedeCrear
#llegar cualquier PN, si este no existe asignamos un por defecto
def getParNumber(request, component):
    try:
        parNumber = PN.objects.get(name = request.POST["parNumber"])
    except PN.DoesNotExist:
        try:
            parNumber = PN.objects.get(name = "default")
        except PN.DoesNotExist:
            defaultDesigna = Designacion(name = "default", Componente = component)
            defaultDesigna.save()
            parNumber = PN(name = "default", programa = PROGRAMA_350, Designacion = defaultDesigna)
            parNumber.save()
    return parNumber

def getRT(rt1, rt2, rt3, program):
    try:
        rt = reasonTree.objects.filter(nivel1__codigo = rt1).filter(nivel2__codigo = rt2).get(nivel3__codigo = rt3)
    except reasonTree.DoesNotExist:
        if rt2 != "" and rt3 != "":
            name = rt1 + "." + rt2 + "." + rt3 + ". "
        else:
            name = rt1
        
        try:
            rt1 = reasonTreeField.objects.get(codigo = rt1)
        except reasonTreeField.DoesNotExist:
            rt1 = None
        try:
            rt2 = reasonTreeField.objects.filter(superior = rt1).get(codigo = rt2)
        except reasonTreeField.DoesNotExist:
            rt2 = None
        try:
            rt3 = reasonTreeField.objects.filter(superior = rt2).get(codigo = rt3)
        except reasonTreeField.DoesNotExist:
            rt3 = None
        
        
        rt = reasonTree(nivel1 = rt1, nivel2 = rt2, nivel3 = rt3, shortName = name, program = program)
        rt.save()
    
    return rt
    
#Vista correspondiente a todos los F412, tanto para recibir el formulario como para enviarlo
#Depende del método
@csrf_exempt
def newRep(request, program):
    template = get_template("html/" + program + "form.html")
    try:
        currentUser = myUser.objects.get(user = request.user)
    except:
        currentUser = None
        Error = "Usuario no identificado, Inicie sesion"
        
    if request.method == "GET":
        return serveFormRepProg(request, program)
    
    elif request.method == "POST":
        myContext = getContextFormRep(request, program)
        if currentUser.typeUser.name != "ME" and currentUser.typeUser.name != "Subcontrata":
            Error = "No tiene permisos para crear en esta seccion"
            myContext["error"] = Error
            return HttpResponse(template.render(myContext))
        
        section = request.POST["section"]
        comp = request.POST["Component"]
        parNumber = request.POST["parNumber"]
        area = request.POST["Area"]
        defect = request.POST["Defect"]
        sgm = request.POST["SGM"]
        rt1 = request.POST["rt1"]
        hnc = request.POST["hnc"]
        ref = request.POST["Ref"]
        horas = request.POST["horas"]
        descp = request.POST["Descp"]
        hnc = request.POST["hnc"]
        
        sectionObj = Seccion.objects.get(name = section)
        compObj = Componente.objects.get(name = comp)
        parNumberObj = PN.objects.get(name = parNumber)
        areaObj = Area.objects.get(name = area)
        defectObj = Defecto.objects.get(name = defect)
        sgmObj = SGM.objects.get(number = sgm)
        codCausa = codCaus.objects.get(name = "RL8")
        programObj = Programa.objects.get(name = program)
        
        if Reparacion.objects.filter(seccion = sectionObj).count() == 0:
            myID = 1
        else:
            myID = Reparacion.objects.filter(seccion = sectionObj).latest('id').myID + 1
        
        print(myID)                   
        
        myContext['newID'] = True
        myContext["myID"] = myID                 
        
        print(section)
        if section == "380":
            designa = request.POST["Designation"]
            nAV = 1
            designaObj = Designacion.objects.get(name = designa)
            hLT = "0"
            nOp = "1"
            rtObj = getRT(rt1, rt1, rt1, programObj)
            rep = Reparacion(programa = programObj, seccion = sectionObj, Componente = compObj,
                             PN = parNumberObj, Area = areaObj, Defecto = defectObj,
                             Fecha = date.today(), Designacion = designaObj, 
                             reasonTree = rtObj, Usuario = currentUser, LastChangeUser = currentUser, 
                             SGM = sgmObj, Referencia = ref, horas = horas, hnc = hnc, 
                             nOp = nOp, horasLeadTime = hLT, Descripcion = descp, 
                             nAV = nAV, añadidoAv = True, codigoCausa = codCausa, myID = myID)
            rep.save()
            
        else:
            nAV = request.POST["nAV"]
            try:
                plane = avion.objects.get(numero = nAV)
            except avion.DoesNotExist:
                plane = avion(numero = nAV)
            nOp = request.POST["nOp"]
            hLT = request.POST["numH"]
            pieza = request.POST["Pieza"]
            piezaObj = Pieza.objects.get(name = pieza)
            rt2 = request.POST["rt2"]
            rt3 = request.POST["rt3"]
            
            plane.hRecRL8 = manageDB.sumHour(plane.hRecRL8, horas)
            plane.hLTRL8 = manageDB.sumHour(plane.hLTRL8, hLT)    
            
            plane.save()
            
            rtObj = getRT(rt1, rt2, rt3, programObj)
            rep = Reparacion(programa = programObj, seccion = sectionObj, Componente = compObj,
                             PN = parNumberObj, Area = areaObj, Defecto = defectObj, hnc = hnc,
                             Fecha = date.today(), reasonTree = rtObj, Usuario = currentUser,
                             LastChangeUser = currentUser, SGM = sgmObj, Pieza = piezaObj, myID = myID, 
                             Referencia = ref, horas = horas, nOp = nOp, horasLeadTime = hLT,
                             Descripcion = descp, nAV = nAV, añadidoAv = True, codigoCausa = codCausa)
            rep.save()
            
        
        
        return HttpResponse(template.render(myContext))
        
    return HttpResponseRedirect("/Reparaciones")

@csrf_exempt
def newF412(request, program):
    template = get_template("html/" + program + "form.html")
    if request.method == "GET":
        toReturn = serveForm(program, request)
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
            try:
                hRec = request.POST["hRec"]
                nOp = request.POST["nOp"]
            except:
                hRec = ""
                nOp = ""
            descp = request.POST["Descp"]
            SGMf412 = SGM.objects.get(number = request.POST["SGM"])
            #Por si hemos reseteado base de datos y es el primer f412
            try:
                myID = F412.objects.filter(seccion =section).latest('id').myID + 1
            except F412.DoesNotExist:
                myID = 1
            F412toSave = F412(programa = program, Componente = component, PN = parNumber, Area = area,
                            Defecto = defect, Fecha = f412date, Estado = Status, horasRecurrentes = hRec,
                            nOp = nOp, Referencia = request.POST["Ref"], horas = numH, SGM = SGMf412,
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
def returnTable(f412List, request, program, isProgram, section, typePage, status,  minDate, maxDate):
    myContext = getBasicContext(request)
    myContext['F412list'] = f412List
    myContext['isProgram'] = isProgram
    myContext['program'] = program
    myContext['userSection'] = section
    myContext['Status'] = status
    myContext['currentDate'] = minDate
    myContext['currentDate1'] = maxDate  
    myContext['date'] = dateToString(datetime.datetime.now())
    myContext['yesterday'] = dateToString(date.today() - timedelta(1))
    
    if typePage == "act":
        myContext['activePage'] = True
    elif typePage == "val":
        myContext['validatedPage'] = True   
    if isProgram:
        programObject = Programa.objects.get(name = program)
        myContext['sectionList'] = Seccion.objects.filter(programa = programObject)
    template = get_template("html/tabla.html")
    return template, myContext

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
@csrf_exempt
def serveTableStatus(request, section, status):
    F412List = F412.objects.all()
    minDate = ""
    maxDate = ""
    if request.method == "POST":
        minDate = parseDate(request.POST["fromDate"])
        maxDate = parseDate(request.POST["toDate"])
        F412List = F412.objects.filter(Fecha__lte=maxDate)
        F412List = F412List.filter(Fecha__gte=minDate)
        minDate = dateToString(minDate)
        maxDate = dateToString(maxDate)
    status = status.title()[:-1]
    if status == "activos" or "validados":
        shortName = status[:3]
    else:
        shortName = ""
    if  section == "350":
        programName = "350"
        sectionName = "A350 Todos"
        try:
            currentUser = myUser.objects.get(user = request.user)
            if currentUser.typeUser.name == "MANDOTL" or currentUser.typeUser.name == "Operario":
                f412List = F412List.filter(Estado__name = status)
                f412List = f412List.filter(seccion = currentUser.seccion.all()[0])
                for section in currentUser.seccion.all():
                    f412List = f412List.filter(seccion = section) | f412List
            else:
                f412List = F412List.filter(Estado__name = status).filter(programa = PROGRAMA_350).order_by('Fecha').order_by('-myID')  
        except:
            f412List = F412List.filter(Estado__name = status).filter(programa = PROGRAMA_350).order_by('Fecha').order_by('-myID')
    else:
        section = Seccion.objects.get(name = section)
        programName = section.programa.name
        sectionName = section.name
        f412List = F412List.filter(Estado__name = status).filter(seccion = section).order_by('Fecha').order_by('-myID')
    
    status = status + "s"
    template, myContext = returnTable(f412List, request, programName, False, sectionName, shortName, status, minDate, maxDate)
    return HttpResponse(template.render(myContext))
    
#Preparacion servir tabla
@csrf_exempt
def programF412(request,program):
    minDate = ""
    maxDate = ""
    if request.method == "POST":
        minDate = parseDate(request.POST["fromDate"])
        maxDate = parseDate(request.POST["toDate"])
        F412List = F412.objects.filter(Fecha__lte=maxDate)
        F412List = F412List.filter(Fecha__gte=minDate)
        minDate = dateToString(minDate)
        maxDate = dateToString(maxDate)
    user = myUser.objects.get(user = request.user)
    if user.typeUser.name == "Subcontrata" or user.typeUser.name == "Operario":
        return returnError(request, "No tienes permisos para acceder")
    program = Programa.objects.get(name = program)
    if user.typeUser.name == "TL":
        f412List = F412.objects.filter(seccion = user.seccion.all()).order_by('-myID').order_by('-Fecha')
    else:
        f412List = F412.objects.filter(programa = program).order_by('-myID').order_by('-Fecha')
    template, myContext = returnTable(f412List, request, program.name, True, "", "", "", minDate, maxDate)    
    return HttpResponse(template.render(myContext))

def programRep(request, program):
    minDate = ""
    maxDate = ""
    if request.method == "POST":
        minDate = parseDate(request.POST["fromDate"])
        maxDate = parseDate(request.POST["toDate"])
        RepList = Reparacion.objects.filter(Fecha__lte=maxDate)
        RepList = RepList.filter(Fecha__gte=minDate)
        minDate = dateToString(minDate)
        maxDate = dateToString(maxDate)
    user = myUser.objects.get(user = request.user)
    if user.typeUser.name == "Subcontrata" or user.typeUser.name == "Operario":
        return returnError(request, "No tienes permisos para acceder")
    program = Programa.objects.get(name = program)
    
    RepList = Reparacion.objects.filter(programa = program).order_by('-myID').order_by('-Fecha')
    template, myContext = returnTable(RepList, request, program.name, True, "", "", "", minDate, maxDate)    
    myContext["mode"] = "Accidentales"
    return HttpResponse(template.render(myContext))

def serveTableRep(request, program):
    minDate = ""
    maxDate = ""
    if request.method == "POST":
        minDate = parseDate(request.POST["fromDate"])
        maxDate = parseDate(request.POST["toDate"])
        F412List = F412.objects.filter(Fecha__lte=maxDate)
        F412List = F412List.filter(Fecha__gte=minDate)
        minDate = dateToString(minDate)
        maxDate = dateToString(maxDate)
    user = myUser.objects.get(user = request.user)
    if user.typeUser.name == "Subcontrata" or user.typeUser.name == "Operario":
        return returnError(request, "No tienes permisos para acceder")
    program = Programa.objects.get(name = program)
    f412List = Reparacion.objects.filter(programa = program).order_by('-myID').order_by('-Fecha')
    template, myContext = returnTable(f412List, request, program.name, True, "", "", "", minDate, maxDate)    
    myContext["mode"] = "Accidentales"
    return HttpResponse(template.render(myContext))

#Preparacion servir tabla, correspondiente a las distintas secciones del 350
@csrf_exempt
def programSectionF412(request,section):
    minDate = ""
    maxDate = ""
    if request.method == "POST":
        minDate = parseDate(request.POST["fromDate"])
        maxDate = parseDate(request.POST["toDate"])
        F412List = F412.objects.filter(Fecha__lte=maxDate)
        F412List = F412List.filter(Fecha__gte=minDate)
        minDate = dateToString(minDate)
        maxDate = dateToString(maxDate)
    user = myUser.objects.get(user = request.user)
    if user.typeUser.name == "Subcontrata" or user.typeUser.name == "Operario":
        return returnError(request, "No tienes permisos para acceder")
    f412List = F412.objects.filter(seccion__name = section).order_by('-myID').order_by('-Fecha')
    if user.typeUser.name == "TL":
        f412List = f412List.filter(seccion = user.seccion.all())
    template, myContext = returnTable(f412List, request, "350", True, section, "", "",minDate, maxDate)    
    return HttpResponse(template.render(myContext))

@csrf_exempt
def programSectionRep(request,section):
    minDate = ""
    maxDate = ""
    if request.method == "POST":
        minDate = parseDate(request.POST["fromDate"])
        maxDate = parseDate(request.POST["toDate"])
        RepList = Reparacion.objects.filter(Fecha__lte=maxDate)
        RepList = RepList.filter(Fecha__gte=minDate)
        minDate = dateToString(minDate)
        maxDate = dateToString(maxDate)
    user = myUser.objects.get(user = request.user)
    if user.typeUser.name == "Subcontrata" or user.typeUser.name == "Operario":
        return returnError(request, "No tienes permisos para acceder")
    RepList = Reparacion.objects.filter(seccion__name = section).order_by('-myID').order_by('-Fecha')
    
    template, myContext = returnTable(RepList, request, "350", True, section, "", "",minDate, maxDate)    
    myContext["mode"] = "Accidentales"
    return HttpResponse(template.render(myContext))

def getReasonTree(request, f412):
    if f412.rtMod:
        return f412.reasonTree
    else:
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

def saveChange(f412Mod, newStatus, action, request):
    oldStatus = f412Mod.Estado
    newUser = myUser.objects.get(user = request.user)
    dateMod = date.today()
    if modificaciones.objects.filter(f412 = f412Mod).count() == 0:
        number = 1
    else:
        number = modificaciones.objects.filter(f412 = f412Mod).latest('id').numero + 1
    
    try:                                              
        comment = request.POST['comment']                                              
    except:
        comment = action
                                                                                        
    newMod = modificaciones(numero = number, usuario = newUser, fecha = dateMod, f412 = f412Mod, 
                            estadoViejo = oldStatus, estadoNuevo = newStatus, comentarios = comment)
    newMod.save()      
        
    return

def changeStatus(f412, newStatus, action, request):
    saveChange(f412, newStatus, action, request)
    currentUser = myUser.objects.get(user = request.user)
    f412.LastChangeUser = currentUser
    f412.Estado = newStatus
    try:
        newStatus = Estado.objects.get(name = request.POST["newStatusForm"])
        print(request.POST["codCausSelect"])
        f412.codigoCausa = codCaus.objects.get(name = request.POST["codCausSelect"])
        checkPlane(f412)
    except:
        print("NO COD CAUS")
    try:
        operacion = request.POST["operacion"]
        if operacion != "default" and operacion !="":
            print(operacion)
            f412.operacion = operacion
    except:
        print("No hay operacion")
    if newStatus.name == "Concedido" or newStatus.name == "Validado":
        if request.POST["newH"] != "":
            if f412.programa == PROGRAMA_380:
                f412.horasAntiguas = f412.horas
                f412.horas = request.POST["newH"] 
            else:    
                f412.horasAntiguas = f412.horas
                f412.horas = str(float(request.POST["newH"]) / float(f412.nOp))
                f412.horasAntRec = f412.horasRecurrentes
                f412.horasRecurrentes = request.POST["newH"] 
        if f412.programa.name == "350":
            rt = getReasonTree(request, f412)
            f412.reasonTree = rt
            f412.rtMod = True
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

def repPage(request, sectionName, myID):
    rep = Reparacion.objects.filter(seccion__name = sectionName).get(myID = myID)
    if rep.seccion.name == "380":
        a380 = True
    else:
        a380 = False
    myContext = getBasicContext(request)
    myContext['f412'] = rep
    myContext['statusList'] = Estado.objects.all()
    myContext['a380'] = a380
    myContext['date'] = dateToString(rep.Fecha)
    myContext['week'] = rep.Fecha.isocalendar()[1]
    myContext["mode"] = "Accidentales"
    template = get_template("html/f412A" + rep.programa.name + ".html")
    return HttpResponse(template.render(myContext))


def f412Hist(request, f412ID):
    template = get_template("html/hist.html")
    myContext = getBasicContext(request)
    try:
        f412 = F412.objects.get(id=f412ID)
        myContext["f412"] = f412
        myContext["histMod"] = modificaciones.objects.filter(f412 = f412)
    except:
        print("F412 no encontrado")
        myContext["MSGerror"] = "El f412 elegido no tiene historial"
    return HttpResponse(template.render(myContext))   

def f412Reset(request, f412ID):
    try:
        f412 = F412.objects.get(id=f412ID)
        saveChange(f412, Estado.objects.get(name ="Activo"), "Reseteado", request)
    except:
        print("F412 no encontrado")
        return HttpResponseRedirect("/")
    if f412.horasAntiguas != "":
        f412.horas = f412.horasAntiguas
        f412.horasAntiguas = ""
    if f412.horasAntRec != "":
        f412.horasRecurrentes = f412.horasAntRec
        f412.horasAntRec = ""
    f412.rtMod = False
    f412.operacion = ""
    f412.accion = ""
    f412.Estado = Estado.objects.get(name = "Activo")
    f412.descripcionAcortada = ""
    f412.save()
    return HttpResponseRedirect("/f412/" + f412.seccion.name + "/" + str(f412.myID))   

@csrf_exempt
def f412CambiarRT(request, f412ID):
    print(f412ID)
    if True:
        f412 = F412.objects.get(id=f412ID)
    else:
        print("F412 no encontrado")
        return HttpResponseRedirect("/")
    myContext = getBasicContext(request)
    myContext["f412"]  = f412       
    myContext['level1RT'] = reasonTreeField.objects.filter(nivel = 1)
    myContext['level2RT'] = reasonTreeField.objects.filter(nivel = 2)
    myContext['level3RT'] = reasonTreeField.objects.filter(nivel = 3)      
    template = get_template("html/f412CambiarRT.html")        
    
    if request.method == "POST":
        f412.rtMod = False
        rt = getReasonTree(request, f412)
        f412.reasonTree = rt
        f412.rtMod = True
        descp = f412.descripcionAcortada
        f412.descripcionAcortada = rt.shortName + descp[13:] 
        f412.save()
    
    return HttpResponse(template.render(myContext))

#Funcion para cerrar sesion
@csrf_exempt
def logOut(request):
    logout(request)
    return HttpResponseRedirect("/")

@csrf_exempt
def simple(request):
    av1 = ""
    av2 = ""
    typeGraph = ""
    if request.method == "POST":
        av1 = request.POST["av1"]
        av2 = request.POST["av2"]
        typeGraph = request.POST["typeGraph"]
    if typeGraph == "TL":
        updateGraph(request, av1, av2, "TL")
    else:
        updateGraph(request, av1, av2, "") 
    planeList = getAvList(av1, av2)
    wholeAvList = avion.objects.all().order_by("numero")
    
    template = get_template("html/chart.html")
    myContext = getBasicContext(request)
    myContext['planeList'] = wholeAvList
    myContext['lastPlane'] = planeList.latest('numero')
    myContext["av1"] = wholeAvList[0]
    myContext["av2"] = planeList.latest("numero")
    myContext["av1TL"] = wholeAvList[0]
    myContext["av2TL"] = planeList.latest("numero")
    if request.method == "POST":
        if typeGraph == "TL":
            myContext["av1TL"] = avion.objects.get(numero = av1)
            myContext["av2TL"] = avion.objects.get(numero = av2)
        else:
            myContext["av1"] = avion.objects.get(numero = av1)
            myContext["av2"] = avion.objects.get(numero = av2)
        
        
   
    return HttpResponse(template.render(myContext))


