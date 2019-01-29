from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseRedirect

from django.template.loader import get_template
from django.template import Context

from f412.models import *
from f412.toString import *
from f412.manageDB import initEstadoDB, initSeccionDB, initProgramaDB

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

#Contexto necesario para todas las cosas relacionadas con los usuarios
def userContext(myContext):
    programList = Programa.objects.all()
    sectionList = Seccion.objects.all()
    myContext['programList'] = programList
    myContext['sectionList'] =  sectionList
    return myContext

#Contexto necesario para base
def getBasicContext(myContext, request):
    myContext['user'] = request.user
    myContext["mode"] = "Accidentales"
    myContext['myPath'] = request.path
    myContext["codCausList"] = codCaus.objects.all()
    try:
        myContext['myUser'] = myUser.objects.get(user = request.user)
    except:
        print("Usuario No Encontrado")
    return myContext

#Funcion para crear usuario a partir del formulario del admin
@csrf_exempt
def newUser(request):
    myContext = Context({'NameError': False, 'UserCreated' : False})
    newMail = request.POST["email"]
    username = request.POST["username"]
    password = request.POST["passwd"]
    programName = request.POST["program"]
    sectionList = request.POST.getlist("section1")
    typeName = request.POST["typeUser"]
    fullName = request.POST["fullName"]
    sgmList = request.POST.getlist('sgmList')
    program = Programa.objects.get(name = programName)
    typeUser = tipoUsuario.objects.get(name = typeName)
    NG = request.POST["username"]
    if typeName == "ME":
        isAdmin = True
    else:
        isAdmin = False
    #Comprobar usuario no existe
    try:
        userAuth = modelsAuth.User.objects.get(username = username)
        myContext['NameError'] = True
    except modelsAuth.User.DoesNotExist:
        userAuth = modelsAuth.User.objects.create_user(username = username, password = password)
        userAuth.save()
        myContext['UserCreated'] = True
    try:
        myUser.objects.get(user=userAuth)
        myContext['NameError'] = True
        myContext['UserCreated'] = False
    except myUser.DoesNotExist:
        newUser = myUser(name = username, email = newMail, passwd = password, nombreCompleto = fullName,
                        user = userAuth, typeUser = typeUser, admin = isAdmin, NA = NG)
        newUser.save()    
        for sgm in sgmList:
            dotNumber = sgm.find('.')
            dbSGM = SGM.objects.filter(seccion__name = sgm[:dotNumber]).get(number = sgm[dotNumber+1:])
            dbSGM.user.add(newUser)
            dbSGM.save()
        print(sectionList)
        for section in sectionList:
            print(section)
            sectionObject = Seccion.objects.get(name = section)
            newUser.seccion.add(sectionObject)
        newUser.programa.add(program)
        newUser.save()
        myContext['NameError'] = False
        myContext['UserCreated'] = True
    myContext= getBasicContext(myContext, request)
    myContext = userContext(myContext)
    return myContext

def getRedirectPage(path, myUser):
    if path == "/cambiarCon" or path == "/" :
        return "/"
    else:
        return myUser.seccion.all()[0].name + path

#Necesario para inicio de sesion
@csrf_exempt
def validateUser(request):
    myContext = Context({'NameError': False, 'UserCreated' : False})
    if request.method == "POST":
        username = request.POST["username"].lower()
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is None:
            myContext['NameError'] = True
        else:
            myContext['notNameError'] = True
            login(request, user)
        myContext['user'] = user
    try:
        currentUser = myUser.objects.get(user = user)   
        myContext['myUser'] = currentUser
    except:
        currentUser = None
        print("Usuario No Encontrado")
        template = get_template("html/root.html")
        return HttpResponse(template.render(myContext))
    return HttpResponseRedirect("/")
#    return HttpResponseRedirect(getRedirectPage(request.POST['toRedirect'], currentUser))

#Vista para modificar informacion de un usuario desde la pagina de admin
@csrf_exempt
def modifyUser(request):
    userID = request.POST["userID"]
    userToChange = myUser.objects.get(id=userID)
    userToChange.programa.clear()
    newPrograms = request.POST.getlist('programs')
    newSectionList = request.POST.getlist('section')
    for program in newPrograms:
        userToChange.programa.add(Programa.objects.get(name = program))
    if "380" in newPrograms and len(newPrograms) == 1 :
        newSection = Seccion.objects.get(name = "380")
    elif "350" in newPrograms and len(newPrograms) == 1 and "380":
        newSection = Seccion.objects.get(name = "APT1")
    print(len(newPrograms))
    userToChange.seccion.clear()
    if len(newSectionList) == 0:
        userToChange.seccion.add(newSection)
    else:
        for section in newSectionList:
            sectionObject = Seccion.objects.get(name = section)
            userToChange.seccion.add(sectionObject)
    userToChange.save()
    return

#Modificar tipo de un usuario
@csrf_exempt
def modifyType(request):
    userID = request.POST["userID"]
    newType = tipoUsuario.objects.get(name = request.POST["newType"])
    userToChange = myUser.objects.get(id = userID)
    userToChange.typeUser = newType
    userToChange.save()
    return

#Borrar usuario
@csrf_exempt
def removeUser(request):
    userID = request.POST["userID"]
    userToRemove = myUser.objects.get(id=userID)
    user = modelsAuth.User.objects.get(username = userToRemove.name)
    user.delete()
    userToRemove.delete()
    return

#Vista para pagina de administracion
@csrf_exempt
def adminPage(request):
    
    return serveAdminPage(request, "Reparaciones")
 
def adminPageRep(request):
    
    return serveAdminPage(request, "Accidentales")    
    
@csrf_exempt
def serveAdminPage(request, mode):    
    template = get_template("html/adminPage.html")
    myContext = Context()
    myContext = getBasicContext(myContext, request)
    if request.method == "POST":
        typeForm = request.POST['type']
        if typeForm == "newUser":
            myContext = newUser(request)
        elif typeForm == "changeType":
            modifyType(request)
        elif typeForm == "remove":
            removeUser(request)
        else:
            modifyUser(request)
    myContext['userList'] = myUser.objects.all().order_by('id')
    myContext['programList'] = Programa.objects.all()
    sectionList = []
    for section in Seccion.objects.all():
        sectionList.append(section.programa.name + section.name)
    myContext['sectionObjectList'] = Seccion.objects.all()
    myContext['sectionList'] = sectionList
    SGMList = []
    for sgm in SGM.objects.all():
        for sgmSection in sgm.seccion.all():
            SGMList.append(sgmSection.name + "." + sgm.number)
    myContext['SGMList'] = SGMList
    myContext['sgmAll'] = SGM.objects.all()
    myContext['typeList'] = tipoUsuario.objects.all()
    myContext["mode"] = mode
    return HttpResponse(template.render(myContext))

@csrf_exempt
def changePassword(request):
    myContext = Context()
    myContext = getBasicContext(myContext, request)
    myContext['changePassword'] = True
    if request.method == "POST":
        username = request.POST["name"]
        userPasswd = request.POST["currentPasswd"]
        newPasswd = request.POST["newPasswd"]
        user = authenticate(username=username, password=userPasswd)
        if user is None:
            myContext['aux'] = "El usuario no existe o la contraseña son erroneos"
        else:
            user.set_password(newPasswd)
            user.save()
            myUsr = myUser.objects.get(user = user)
            myUsr.passwd = newPasswd
            myUsr.save()
            myContext['aux'] = "Contraseña cambiada con exito"
    template = get_template("html/pass.html")
    return HttpResponse(template.render(myContext))
