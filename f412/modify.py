#import datetime
#from datetime import date, timedelta

#from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.template.loader import get_template
#from django.template import Context

from f412.models import PNEvol, areaCaus, costeHora, codCaus, Programa, ComponenteAPT5, reasonTreeField, Pieza, Componente, myUser, PN, Area, Defecto, Designacion, Estado, SGM, Seccion#, F412, avion, reasonTree, tipoUsuario, modificaciones, Reparacion
from f412.toString import *
#from f412.manageDB import updateHours, getAvList, initEstadoDB, initSeccionDB, initProgramaDB, initTypeUser, initCodCaus, sumPlaneRepF412, updateGraph#, checkPlane
from f412.views import getBasicContext

#import f412.manageDB as manageDB

def checkUser(request):
    try:
        currentUser = myUser.objects.get(user = request.user)
    except:
        return False
        
    if currentUser.isSuperUser == False:
        return False
    
    return True

@csrf_exempt
def serveModifyPage(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    myContext = getBasicContext(request)
    template = get_template("html/modify/modifyPage.html")    
    myContext["isBase"] = True
    
    return HttpResponse(template.render(myContext))

"""
PROGRAMA
"""


@csrf_exempt
def serveModifyProgram(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    programList = Programa.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = programList
    myContext["model"] = "Program"
    myContext["modelName"] = "Programa"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyProgram(request, programID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/program.html")
    myContext["modeModify"] = "modify"
    myContext["hasLastPage"] = True
    myContext["model"] = "Program"
    myContext["modelName"] = "Programa"

    try:
        programToModify = Programa.objects.get(id = programID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["programName"]
            programToModify.name = newName
            programToModify.save()
            myContext["statusModify"] = "Programa modificado"
            
        except:
            myContext["statusModify"] = "Programa no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["programToModify"] = programToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newProgram(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/program.html")
    myContext["modeModify"] = "new"
    myContext ["modifyModel"] = "Crear"
    myContext["hasLastPage"] = True
    myContext["model"] = "Program"
    myContext["modelName"] = "Programa"


    if request.method == "POST":
        try:
            newName = request.POST["programName"]
            programToModify = Programa(name = newName)
            programToModify.save()
            myContext["statusModify"] = "Programa creado"
            
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["programToModify"] = programToModify
            
    return HttpResponse(template.render(myContext))

"""
SECCION
"""

@csrf_exempt
def serveModifySection(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    sectionList = Seccion.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = sectionList
    myContext["model"] = "Section"
    myContext["modelName"] = "Seccion"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def newSection(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/section.html")
    myContext["modeModify"] = "new"
    myContext["modifyModel"] = "Crear"
    myContext["programList"] = Programa.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Section"
    myContext["modelName"] = "Seccion"

    if request.method == "POST":
        try:
            newName = request.POST["sectionName"]
            sectionProgram = request.POST["sectionProgram"]
            sectionProgramObj = Programa.objects.get(name = sectionProgram)
            sectionToModify = Seccion(name = newName, programa = sectionProgramObj)
            sectionToModify.save()
            myContext["statusModify"] = "Sección creada"
            
        except:
            myContext["statusModify"] = "Error de campo"
            return HttpResponse(template.render(myContext))
        
        myContext ["sectionToModify"] = sectionToModify
            
    return HttpResponse(template.render(myContext))

@csrf_exempt 
def modifySection(request, sectionID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/section.html")
    myContext["modeModify"] = "modify"
    myContext["programList"] = Programa.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Section"
    myContext["modelName"] = "Seccion"

    try:
        sectionToModify = Seccion.objects.get(id = sectionID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["sectionName"]
            programName = request.POST["sectionProgram"]
            sectionProgram = Programa.objects.get(name = programName)
            sectionToModify.programa = sectionProgram
            sectionToModify.name = newName
            sectionToModify.save()
            myContext["statusModify"] = "Seccion modificada"
            
        except:
            myContext["statusModify"] = "Seccion no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["sectionToModify"] = sectionToModify
            
    return HttpResponse(template.render(myContext))

"""
COMPONENTE
"""

@csrf_exempt
def serveModifyComponent(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    ComponentList = Componente.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = ComponentList
    myContext["modelList2"] = ComponenteAPT5.objects.all()
    myContext["model"] = "Component"
    myContext["modelName"] = "Componente"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def newComponent(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/component.html")
    myContext["modeModify"] = "new"
    myContext["modifyModel"] = "Crear"
    myContext["programList"] = Programa.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Component"
    myContext["modelName"] = "Componente"

    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["componentName"]
            componentProgram = request.POST["componentProgram"]
            ComponentProgram = Programa.objects.get(name = componentProgram)
            componentToModify = Componente(name = newName, programa = ComponentProgram)
            componentToModify.save()
            myContext["statusModify"] = "Componente creado"
            
        except:
            myContext["statusModify"] = "Error de campo"
            return HttpResponse(template.render(myContext))
        
        myContext ["componentToModify"] = componentToModify
            
    return HttpResponse(template.render(myContext))

@csrf_exempt 
def modifyComponent(request, ComponentID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/component.html")
    myContext["modeModify"] = "modify"
    myContext["programList"] = Programa.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Component"
    myContext["modelName"] = "Componente"

    try:
        componentToModify = Componente.objects.get(id = ComponentID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["componentName"]
            programName = request.POST["componentProgram"]
            componentProgram = Programa.objects.get(name = programName)
            componentToModify.programa = componentProgram
            componentToModify.name = newName
            shouldShow = request.POST["componentShouldShow"]
            
            if shouldShow == "True":
                shouldShow = True
            else:
                shouldShow = False
            
            componentToModify.shouldShow = shouldShow
            componentToModify.save()
            myContext["statusModify"] = "Componente modificado"
            
        except:
            myContext["statusModify"] = "Componente no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["componentToModify"] = componentToModify
            
    return HttpResponse(template.render(myContext))

"""
DESIGNACION
"""

@csrf_exempt
def serveModifyDesignation(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    DesignacionList = Designacion.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = DesignacionList
    myContext["model"] = "Designation"
    myContext["modelName"] = "Designacion"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyDesignation(request, ComponentID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/designation.html")
    myContext["modeModify"] = "modify"
    myContext["componentList"] = Componente.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Designation"
    myContext["modelName"] = "Designacion"

    try:
        designationToModify = Designacion.objects.get(id = ComponentID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["designationName"]
            designationComponent = request.POST["designationComponent"]
            designationComponent = Componente.objects.get(name = designationComponent)
            designationToModify.Componente = designationComponent
            designationToModify.name = newName
            designationToModify.save()
            myContext["statusModify"] = "Designacion modificada"
            
            pnToModify = designationToModify.PN
            pnToModify.programa = designationComponent.programa
            pnToModify.save()
                     
        except:
            myContext["statusModify"] = "Designacion no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["designationToModify"] = designationToModify
            
    return HttpResponse(template.render(myContext))


@csrf_exempt 
def newDesignaPN(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/newDesignationPN.html")
    myContext["modeModify"] = "new"
    myContext["modifyModel"] = "Crear"
    myContext["programList"] = Programa.objects.all()
    myContext["componentList"] = Componente.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Designation"
    myContext["modelName"] = "Designacion"

    if request.method == "POST":
        try:
#        if True:
            designaName = request.POST["designationName"]
            designaComponent = request.POST["designationComponent"]
            designaComponent = Componente.objects.get(name = designaComponent)
            designationToModify = Designacion(Componente = designaComponent, name = designaName)
            designationToModify.save()
            
            pnName = request.POST["pnName"]
            pnProgram = Programa.objects.get(name = request.POST["pnProgram"])
            pnToModify = PN(name = pnName, Designacion = designationToModify, programa = pnProgram)
            pnToModify.save()
            myContext["statusModify"] = "Area creada"
            
        except:
            myContext["statusModify"] = "Error de campo"
            return HttpResponse(template.render(myContext))
        
        myContext ["pnToModify"] = pnToModify
        newPNEv(pnToModify.id, pnToModify.name)                  
            
    return HttpResponse(template.render(myContext))

"""
PN
"""

@csrf_exempt
def serveModifyPN(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    pnList = PN.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = pnList
    myContext["model"] = "PN"
    myContext["modelName"] = "Par Number"
    
    return HttpResponse(template.render(myContext)) 


@csrf_exempt
def evolvePN(request, pnID):
    return servePNPage(request, pnID, "evolve", "")

@csrf_exempt
def modifyPN(request, pnID):
    
    return servePNPage(request, pnID, "one", "")

@csrf_exempt 
def servePNPage(request, pnID, typePN, newInfo):
    print(typePN)
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    if typePN == "one":
        template = get_template("html/modify/pn.html")
    else:
        template = get_template("html/modify/evPN.html")
    myContext["modeModify"] = "modify"
    myContext["hasLastPage"] = True
    myContext["model"] = "PN"
    myContext["modelName"] = "Par Number"
    myContext["infoNewPN"] = newInfo
    
    try:
        pnToModify = PN.objects.get(id = pnID)
    except:
        return HttpResponseRedirect("/modifyPage")
    
    if request.method == "POST" and typePN != "evolve":
        try:
#        if True:
            newName = request.POST["pnName"]
            pnToModify.name = newName
            pnToModify.save()
            myContext["statusModify"] = "Par Number modificada"
            
        except:
            myContext["statusModify"] = "Designacion no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["pnToModify"] = pnToModify
     
    if typePN == "evolve":
        myContext["pnEvList"] = PNEvol.objects.filter(pn = pnToModify)
              
    return HttpResponse(template.render(myContext))

@csrf_exempt
def changeName(request, pnID, pnEvID):  
    try:
        pnToModify = PN.objects.get(id = pnID)
    except:
        return HttpResponseRedirect("/modifyPage")
    
    try:
        pnEVToModify = PNEvol.objects.get(id = pnEvID)
    except:
        return HttpResponseRedirect("/modifyPage")
    
    pnToModify.name = pnEVToModify.name
    pnToModify.save()
    
    for pn in PNEvol.objects.filter(pn = pnToModify):
        if pn.name == pnEVToModify.name:
            pn.currentPN = True
        else:
            pn.currentPN = False
        pn.save()
    
    return servePNPage(request, pnID, "evolve", "")

@csrf_exempt
def createEv(request, pnID):
    try:
        newName = request.POST["newPN"]
        return servePNPage(request, pnID, "evolve", newPNEv(pnID, newName))
    except:
        return servePNPage(request, pnID, "evolve", "Error de nombre")
        
    return servePNPage(request, pnID, "evolve", newPNEv(pnID, newName))

@csrf_exempt
def newPNEv(pnID, newName):
    toReturn = ""
    pn = PN.objects.get(id = pnID)
    
    try:
        pn = PNEvol.objects.get(name = newName)
        toReturn = "Ya existe ese PN"
    except:
        newPN = PNEvol(pn = pn, designation = pn.Designacion, name = newName, shouldShow = False, currentPN = False)
        newPN.save()
        toReturn = "PNEv Creado"
    
    return toReturn 

@csrf_exempt
def changeVisiblePN(request, pnId, pnEvId):
    
    try:
        pnEv = PNEvol.objects.get(id = pnEvId)
        if pnEv.shouldShow == True:
            pnEv.shouldShow = False
        else:
            pnEv.shouldShow = True
        pnEv.save()
        
    except:
        print("Error")
    
    return HttpResponseRedirect("/evolucionPN/" + str(pnId))

"""
AREA
"""

@csrf_exempt
def serveModifyArea(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    areaList = Area.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = areaList
    myContext["model"] = "Area"
    myContext["modelName"] = "Area"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def newArea(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/area.html")
    myContext["modeModify"] = "new"
    myContext["modifyModel"] = "Crear"
    myContext["sectionList"] = Seccion.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Area"
    myContext["modelName"] = "Area"

    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["areaName"]
            areaToModify = Area(name = newName)
            areaToModify.save()
            
            newSections = request.POST.getlist("areaSection")
            for section in newSections:
                areaToModify.seccion.add(Seccion.objects.get(name = section))
            myContext["statusModify"] = "Area creada"
            
        except:
            myContext["statusModify"] = "Error de campo"
            return HttpResponse(template.render(myContext))
        
        myContext ["areaToModify"] = areaToModify 
            
    return HttpResponse(template.render(myContext))

@csrf_exempt 
def modifyArea(request, areaID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/area.html")
    myContext["modeModify"] = "modify"
    myContext["sectionList"] = Seccion.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Area"
    myContext["modelName"] = "Area"

    try:
        areaToModify = Area.objects.get(id = areaID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["areaName"]
            areaToModify.seccion.clear()
            areaToModify.name = newName
            newSections = request.POST.getlist("areaSection")
            for section in newSections:
                areaToModify.seccion.add(Seccion.objects.get(name = section))
                
            areaToModify.save()
            myContext["statusModify"] = "Designacion modificada"
            
        except:
            myContext["statusModify"] = "Designacion no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["areaToModify"] = areaToModify
            
    return HttpResponse(template.render(myContext))

"""
DEFECTO
"""

@csrf_exempt
def serveModifyDefect(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    defectList = Defecto.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = defectList
    myContext["model"] = "Defect"
    myContext["modelName"] = "Defecto"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def newDefect(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/defect.html")
    myContext["modeModify"] = "new"
    myContext["modifyModel"] = "Crear"
    myContext["sectionList"] = Seccion.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Defect"
    myContext["modelName"] = "Defect"

    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["defectName"]
            defectToModify = Defecto(name = newName)
            
            newSections = request.POST.getlist("defectSection")
            for section in newSections:
                defectToModify.seccion.add(Seccion.objects.get(name = section))
                
            defectToModify.save()
            myContext["statusModify"] = "Defecto creado"
            
        except:
            myContext["statusModify"] = "Error de campo"
            return HttpResponse(template.render(myContext))
#        
        myContext ["defectToModify"] = defectToModify 
            
    return HttpResponse(template.render(myContext))


@csrf_exempt 
def modifyDefect(request, defectID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/defect.html")
    myContext["modeModify"] = "modify"
    myContext["sectionList"] = Seccion.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "Defect"
    myContext["modelName"] = "Defecto"

    try:
        defectToModify = Defecto.objects.get(id = defectID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
            newName = request.POST["defectName"]
            defectToModify.seccion.clear()
            defectToModify.name = newName
            newSections = request.POST.getlist("defectSection")
            
            for section in newSections:
                newSection = Seccion.objects.get(name = section)
                defectToModify.seccion.add(newSection)
                
            defectToModify.save()
            myContext["statusModify"] = "Defecto modificado"
            
        except:
            myContext["statusModify"] = "Designacion no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["defectToModify"] = defectToModify
            
    return HttpResponse(template.render(myContext))

"""
PIEZA pieza estado programa y codigo causa se pueden hacer iguales ahorrando mucho código
"""

@csrf_exempt
def serveModifyPiece(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    pieceList = Pieza.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = pieceList
    myContext["model"] = "Piece"
    myContext["modelName"] = "Pieza"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyPiece(request, pieceID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/piece.html")
    myContext["modeModify"] = "modify"
    myContext["hasLastPage"] = True
    myContext["model"] = "Piece"
    myContext["modelName"] = "Pieza"

    try:
        pieceToModify = Pieza.objects.get(id = pieceID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["pieceName"]
            pieceToModify.name = newName
            pieceToModify.save()
            myContext["statusModify"] = "Pieza modificada"
            
        except:
            myContext["statusModify"] = "Pieza no encontrada"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["pieceToModify"] = pieceToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newPiece(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/piece.html")
    myContext["modeModify"] = "new"
    myContext ["modifyModel"] = "Crear"
    myContext["hasLastPage"] = True
    myContext["model"] = "Piece"
    myContext["modelName"] = "Pieza"


    if request.method == "POST":
        try:
            newName = request.POST["pieceName"]
            pieceToModify = Pieza(name = newName)
            pieceToModify.save()
            myContext["statusModify"] = "Pieza creada"
            
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["pieceToModify"] = pieceToModify
            
    return HttpResponse(template.render(myContext))

"""
ESTADOS
"""

@csrf_exempt
def serveModifyStatus(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    statusList = Estado.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = statusList
    myContext["model"] = "Status"
    myContext["modelName"] = "Estado"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyStatus(request, statusID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/status.html")
    myContext["modeModify"] = "modify"
    myContext["hasLastPage"] = True
    myContext["model"] = "Status"
    myContext["modelName"] = "Estado"

    try:
        statusToModify = Estado.objects.get(id = statusID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["statusName"]
            statusToModify.name = newName
            statusToModify.save()
            myContext["statusModify"] = "Estado modificado"
            
        except:
            myContext["statusModify"] = "Estado no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["statusToModify"] = statusToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newStatus(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/status.html")
    myContext["modeModify"] = "new"
    myContext ["modifyModel"] = "Crear"
    myContext["hasLastPage"] = True
    myContext["model"] = "Status"
    myContext["modelName"] = "Estado"


    if request.method == "POST":
        try:
            newName = request.POST["statusName"]
            statusToModify = Estado(name = newName)
            statusToModify.save()
            myContext["statusModify"] = "Estado creado"
            
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["statusToModify"] = statusToModify
            
    return HttpResponse(template.render(myContext))

"""
SGM
"""

@csrf_exempt
def serveModifySGM(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    SGMList = SGM.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = SGMList
    myContext["model"] = "SGM"
    myContext["modelName"] = "SGM"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifySGM(request, SGMID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/SGM.html")
    myContext["modeModify"] = "modify"
    myContext["sectionList"] = Seccion.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "SGM"
    myContext["modelName"] = "SGM"

    try:
        SGMToModify = SGM.objects.get(id = SGMID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["SGMnumber"]
            SGMToModify.name = newName
            myContext["statusModify"] = "SGM modificado"
              
            SGMToModify.seccion.clear()                     
            newSections = request.POST.getlist("SGMSection")
            for section in newSections:
                SGMToModify.seccion.add(Seccion.objects.get(name = section))
                
            SGMToModify.save()
        except:
            myContext["statusModify"] = "SGM no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["SGMToModify"] = SGMToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newSGM(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/SGM.html")
    myContext["modeModify"] = "new"
    myContext["modifyModel"] = "Crear"
    myContext["sectionList"] = Seccion.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "SGM"
    myContext["modelName"] = "SGM"


    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["SGMnumber"]
            SGMToModify = SGM(number= newName)
            myContext["statusModify"] = "SGM creado"
            
            newSections = request.POST.getlist("SGMSection")
            for section in newSections:
                SGMToModify.seccion.add(Seccion.objects.get(name = section))
                
            SGMToModify.save()
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["SGMToModify"] = SGMToModify
            
    return HttpResponse(template.render(myContext))

"""
Reason Tree
"""

@csrf_exempt
def serveModifyRT(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    RTList = reasonTreeField.objects.all().order_by("nivel")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = RTList
    myContext["model"] = "RT"
    myContext["modelName"] = "Reason Tree"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyRT(request, RTID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/rt.html")
    myContext["modeModify"] = "modify"
    myContext["RTList"] = reasonTreeField.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "RT"
    myContext["modelName"] = "Reason Tree"

    try:
        RTToModify = reasonTreeField.objects.get(id = RTID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["RTName"]
            RTLevel = int(request.POST["RTLevel"])
            RTCod = request.POST["RTCod"]
            RTToModify.nombre = newName
            RTToModify.nivel = RTLevel
            RTToModify.codigo = RTCod
            myContext["statusModify"] = "Reason Tree Modificado"
            
            if RTLevel == 1:
                superiorRT = RTToModify
                shortName = RTCod
            else:
                superiorRTid = request.POST["superiorRT"]
                superiorRT = reasonTreeField.objects.get(id =superiorRTid)
                shortName = superiorRT.codigo + "." + RTCod
            
            RTToModify.superior = superiorRT 
            RTToModify.shortName = shortName
            
            RTToModify.save()
        except:
            myContext["statusModify"] = "Reason Tree no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["RTToModify"] = RTToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newRT(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/rt.html")
    myContext["modeModify"] = "new"
    myContext["modifyModel"] = "Crear"
    myContext["RTList"] = reasonTreeField.objects.all()
    myContext["hasLastPage"] = True
    myContext["model"] = "RT"
    myContext["modelName"] = "Reason Tree"


    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["RTName"]
            RTLevel = int(request.POST["RTLevel"])
            RTCod = request.POST["RTCod"]
            
            RTToModify = reasonTreeField(nombre = newName, nivel = RTLevel, codigo = RTCod)
            myContext["statusModify"] = "Reason Tree creado"
                
            RTToModify.save()
                        
            if RTLevel != 1: 
                superiorRTid = request.POST["superiorRT"]
                superiorRT = reasonTreeField.objects.get(id =superiorRTid)
                shortName = superiorRT.codigo + "." + RTCod
            else:
                shortName = RTCod
                superiorRT = RTToModify
                
            RTToModify.superior = superiorRT
            RTToModify.shortName = shortName
            RTToModify.save()
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["RTToModify"] = RTToModify
            
    return HttpResponse(template.render(myContext))

"""
CodCausa pieza estado programa y codigo causa se pueden hacer iguales ahorrando mucho código
"""

@csrf_exempt
def serveModifyCodCaus(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    codCausList = codCaus.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = codCausList
    myContext["model"] = "CodCaus"
    myContext["modelName"] = "Código Causa"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyCodCaus(request, codCausID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/codCaus.html")
    myContext["modeModify"] = "modify"
    myContext["hasLastPage"] = True
    myContext["model"] = "CodCaus"
    myContext["modelName"] = "Código Causa"

    try:
        codCausToModify = codCaus.objects.get(id = codCausID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["codCausName"]
            codCausToModify.name = newName
            codCausToModify.save()
            myContext["statusModify"] = "Código Causa modificado"
            
        except:
            myContext["statusModify"] = "Código Causa no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["codCausToModify"] = codCausToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newCodCaus(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/codCaus.html")
    myContext["modeModify"] = "new"
    myContext ["modifyModel"] = "Crear"
    myContext["hasLastPage"] = True
    myContext["model"] = "CodCaus"
    myContext["modelName"] = "Código Causa"


    if request.method == "POST":
        try:
            newName = request.POST["codCausName"]
            codCausToModify = codCaus(name = newName)
            codCausToModify.save()
            myContext["statusModify"] = "Código Causa creado"
            
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["codCausToModify"] = codCausToModify
            
    return HttpResponse(template.render(myContext))

"""
Coste Horas
"""

@csrf_exempt
def serveModifyCostHour(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    codCausList = costeHora.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = codCausList
    myContext["model"] = "CostHour"
    myContext["modelName"] = "Coste Hora"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyCostHour(request, costHourID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/costHour.html")
    myContext["modeModify"] = "modify"
    myContext["hasLastPage"] = True
    myContext["model"] = "CostHour"
    myContext["modelName"] = "Coste Hora"

    try:
        costHourToModify = costeHora.objects.get(id = costHourID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            year = request.POST["costYear"]
            price = request.POST["price"]
            costHourToModify.precio = float(price.replace(",","."))
            costHourToModify.year = int(year)
            costHourToModify.save()
            myContext["statusModify"] = "Coste modificado"
            
        except:
            myContext["statusModify"] = "Coste no encontrado"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["costHourToModify"] = costHourToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newCostHour(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/costHour.html")
    myContext["modeModify"] = "new"
    myContext ["modifyModel"] = "Crear"
    myContext["hasLastPage"] = True
    myContext["model"] = "CostHour"
    myContext["modelName"] = "Coste Horas"


    if request.method == "POST":
        try:
#        if True:
            year = request.POST["costYear"]
            price = request.POST["price"]
            costHourToModify = costeHora(year = year, precio = price)
            costHourToModify.save()
            myContext["statusModify"] = "Coste Hora creado"
            
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["costHourToModify"] = costHourToModify
            
    return HttpResponse(template.render(myContext))

"""
Area Causante
"""

@csrf_exempt
def serveModifyAreaCaus(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
        
    areaCausList = areaCaus.objects.all()
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/modelList.html")
    myContext["modelList"] = areaCausList
    myContext["model"] = "AreaCaus"
    myContext["modelName"] = "Area Causante"
    
    return HttpResponse(template.render(myContext)) 

@csrf_exempt 
def modifyAreaCaus(request, areaCausID):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/areaCaus.html")
    myContext["modeModify"] = "modify"
    myContext["hasLastPage"] = True
    myContext["model"] = "AreaCaus"
    myContext["modelName"] = "Area Causante"

    try:
        areaCausToModify = areaCaus.objects.get(id = areaCausID)
    except:
        return HttpResponseRedirect("/")
    
    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["newName"]
            newCod = request.POST["newCod"]
            areaCausToModify.name = newName
            areaCausToModify.code = newCod
            areaCausToModify.save()
            myContext["statusModify"] = "Area Causante modificada"
            
        except:
            myContext["statusModify"] = "Area Causante no encontrada"
            return HttpResponse(template.render(myContext))
        
    myContext ["modifyModel"] = "Modificar"
    myContext ["areaCausToModify"] = areaCausToModify
            
    return HttpResponse(template.render(myContext))
    
@csrf_exempt 
def newAreaCaus(request):
    if checkUser(request) == False:
        HttpResponseRedirect("/")
    
    myContext = getBasicContext(request)
    template = get_template("html/modify/areaCaus.html")
    myContext["modeModify"] = "new"
    myContext ["modifyModel"] = "Crear"
    myContext["hasLastPage"] = True
    myContext["model"] = "AreaCaus"
    myContext["modelName"] = "Area Causante"


    if request.method == "POST":
        try:
#        if True:
            newName = request.POST["newName"]
            newCod = request.POST["newCod"]
            areaCausToModify = areaCaus(name = newName, code = newCod)
            areaCausToModify.save()
            myContext["statusModify"] = "Coste Hora creado"
            
        except:
            myContext["statusModify"] = "NewName mal"
            return HttpResponse(template.render(myContext))
        
        myContext ["areaCausToModify"] = areaCausToModify
            
    return HttpResponse(template.render(myContext))