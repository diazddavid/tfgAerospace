import pandas as pd

import xlsxwriter

from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse, HttpResponseRedirect

import f412.toString as toString
from f412.toString import *
from f412.paretos import *
from f412.models import *

import datetime
from datetime import date

from django.template import Context, loader
from django.template.loader import get_template

import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from base64 import b64encode

from numpy import arange, array, ones
from scipy import stats

import io
from io import *

F412_VALID = F412.objects.filter(Estado__name="Concedido") | F412.objects.filter(Estado__name="Rechazado") | F412.objects.filter(Estado__name="Validado") | F412.objects.filter(Estado__name="Activo")

#Inicializar codigos causa, solo por si en algún momento se borran de la base de datos
@csrf_exempt
def initCodCaus():
    try:
        codCaus.objects.get(name = "ALB")
    except codCaus.DoesNotExist:
        cod = codCaus(name = "ALB")
        cod.save()
        
    try:
        codCaus.objects.get(name = "V10")
    except codCaus.DoesNotExist:
        cod = codCaus(name = "V10")
        cod.save()
        
    try:
        codCaus.objects.get(name = "RL8")
    except codCaus.DoesNotExist:
        cod = codCaus(name = "RL8")
        cod.save()
        
    try:
        codCaus.objects.get(name = "M60")
    except codCaus.DoesNotExist:
        cod = codCaus(name = "M60")
        cod.save()
    return

#Para meter en bd los programas 380 y 350 en caso de que no estén por cualquier motivo
@csrf_exempt
def initProgramaDB():
    p380 = Programa(name = "380")
    p350 = Programa(name = "350")
    p380.save()
    p350.save()

    return

#Para meter en bd las secciones 380 y APT1 APT2... en caso de que no estén por cualquier motivo
@csrf_exempt
def initSeccionDB():
    try:
        PROGRAMA_380 = Programa.objects.get(name = "380")
        PROGRAMA_350 = Programa.objects.get(name = "350")
    except Programa.DoesNotExist:
        initProgramaDB()
        PROGRAMA_380 = Programa.objects.get(name = "380")
        PROGRAMA_350 = Programa.objects.get(name = "350")

    s380 = Seccion(programa = PROGRAMA_380, name = "380")
    s350APT1 = Seccion(programa = PROGRAMA_350, name = "APT1")
    s350APT2 = Seccion(programa = PROGRAMA_350, name = "APT2")
    s350APT3 = Seccion(programa = PROGRAMA_350, name = "APT3")
    s350APT4 = Seccion(programa = PROGRAMA_350, name = "APT4")
    s350APT5 = Seccion(programa = PROGRAMA_350, name = "APT5")

    s380.save()
    s350APT1.save()
    s350APT2.save()
    s350APT3.save()
    s350APT4.save()
    s350APT5.save()

    return

#Inicializar tipos de usuarios
@csrf_exempt
def initTypeUser():
   ME_USER = tipoUsuario(name = "ME")
   SUB_USER = tipoUsuario(name = "Subcontrata")
   OP_USER = tipoUsuario(name = "Operario")
   MANDOTL_USER = tipoUsuario(name = "MANDOTL")
   LECTURE_USER = tipoUsuario(name = "Lectura")
   HO_CDT = tipoUsuario(name = "HO_CDT")

   ME_USER.save()
   SUB_USER.save()
   OP_USER.save()
   MANDOTL_USER.save()
   LECTURE_USER.save()
   HO_CDT.save()
   return

#Para meter en bd los estados
@csrf_exempt
def initEstadoDB():
    
    try:
        ACTIVE_Status = Estado.objects.get(name = "Activo")
    except Estado.DoesNotExist:
        ACTIVE_Status = Estado(name = "Activo", color = "#ffff00")
        ACTIVE_Status.save()
    
    try:
        VALIDATED_Status = Estado.objects.get(name = "Validado")
    except Estado.DoesNotExist:
        VALIDATED_Status = Estado(name = "Validado", color = "#fe5000")
        VALIDATED_Status.save()
        
    try:
        REJECTED_Status = Estado.objects.get(name = "Rechazado")
    except Estado.DoesNotExist:
        REJECTED_Status = Estado(name = "Rechazado", color = "#e4002b")
        REJECTED_Status.save()
        
    try:
        GRANTED_Status = Estado.objects.get(name = "Concedido")
    except Estado.DoesNotExist:
        GRANTED_Status = Estado(name = "Concedido", color = "#29e329")
        GRANTED_Status.save()
        
    return

#Funcion para recorrer un dataframe, que proviene de un excel y obtener todos los componentes
@csrf_exempt
def updateComponent(df, program):
    for i in range(0,200):
        try:
            name = df.iat[i,0]
            if pd.isnull(df.iat[i,1]) == True or df.iat[i,1].startswith("V"):
                alias = ""
            else:
                alias = df.iat[i,1]
                print(alias)
            if pd.isnull(name):
                return
            try:
                comp = Componente.objects.get(name = name)
                comp.alias = alias
                comp.save()
            except Componente.DoesNotExist:
                componente = Componente(name = name, alias = alias, programa = program)
                componente.save()
        except IndexError:
            break        
    return


#funcion para de datafrem obtener las secciones grupo maquina
@csrf_exempt
def updateSGM(df, section):
    s380 = True
    if section == "350":
        s380 = False
    for i in range(0,200):
        try:
            number = df.iat[i,0]
            if s380:
                name = df.iat[i,1]
                section = Seccion.objects.get(name = "380")
            else:
                name = ""
                section = Seccion.objects.get(name = df.iat[i,1])
            #evitar desbordes
            if pd.isnull(name) or pd.isnull(number):
                return
            number = str(number)
            #Las que empiezan por 0 en excel se quedan en 3 digitos, correccions
            while len(number) < 4:
                number = "0" + str(number)
            try:
                go = SGM.objects.get(number=number)
                go.seccion.add(section) 
            except SGM.DoesNotExist:
                sgm = SGM(number = number, name = name)
                sgm.save()
                sgm.seccion.add(section)
                sgm.save()
        except IndexError:
            return

# Para obtener defectos en 380 o desviaciones en 350
@csrf_exempt
def updateDefect(df, section):
    for i in range(0,200):
        try:
            name = df.iat[i,0]
            if pd.isnull(df.iat[i,1]):
                alias = ""
            else:
                alias = df.iat[i,1]
            if pd.isnull(name):
                break
            try:
                dft = Defecto.objects.get(name=name)
            except Defecto.DoesNotExist:
                dft = Defecto(name = name)
            dft.alias = alias
            dft.save()
            dft.seccion.add(section)
        except IndexError:
            break
    
    for dfct in Defecto.objects.filter(seccion = section):
        if ( dfct.name in toList(df) )== False:
            if F412.objects.filter(Defecto = dfct).count() == 0 and f412Ant.objects.filter(Defecto = dfct).count() == 0:
                print("Borrado " + dfct.name)
                dfct.delete()

    return

#Para actualizar las aereas desde una hoja excel(df) asignandolas a una seccion
@csrf_exempt
def updateArea(df, section):
    for i in range(0,200):
        try:
            name = df.iat[i,0]
            if pd.isnull(name):
                return
            try:
                area = Area.objects.get(name=name)
            except Area.DoesNotExist:
                area = Area(name = name)
                area.save()
            area.seccion.add(section)
        except IndexError:
            return

#Funcion para actualizar la bd del 380
@csrf_exempt
def update380():
    file = 'xls\\380.xlsx'
    xl = pd.ExcelFile(file)
    #Cargar variables comprobando que no hay errores
    try:
        PROGRAMA_380 = Programa.objects.get(name = "380")
    except Programa.DoesNotExist:
        initProgramaDB()
        PROGRAMA_380 = Programa.objects.get(name = "380")
    try:
        SECTION_380 = Seccion.objects.get(programa = PROGRAMA_380)
    except Seccion.DoesNotExist:
        initSeccionDB()
        SECTION_380 = Seccion.objects.get(programa = PROGRAMA_380)

    #Bucle para recorrer todas las hojas
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if sheet == "Componentes":
            updateComponent(df, PROGRAMA_380)
        elif sheet == "SGM":
            updateSGM(df, SECTION_380)
        elif sheet == "DEFECTOS":
            updateDefect(df, SECTION_380)
        elif sheet == "AREA":
            updateArea(df, SECTION_380)
        #Obtener par number y designacion, dado que en 380 están ligadas
        else:
            for i in range(0,200):
                try:
                    DesignaName = df.iat[i,0]
                    PNname = df.iat[i,1]
                    if pd.isnull(df.iat[i,2]) == False:
                        alias = df.iat[i,2]
                    else:
                        alias = ""
                    if pd.isnull(DesignaName) or pd.isnull(PNname):
                        break
                    try:
                        designa = Designacion.objects.get(name = DesignaName)
                        designa.alias = alias
                        designa.save()
                    except Designacion.DoesNotExist:
                        designa = Designacion(name = DesignaName, alias = alias,  Componente = Componente.objects.get(name = sheet))
                        designa.save()
                    try:
                        PN.objects.get(name = PNname)
                        pn = PN.objects.get(Designacion = designa)
                        if pn.name != PNname:
                            pn.name = PNname
                            pn.save()
                    except PN.DoesNotExist:
                        pn = PN(name = PNname, programa = PROGRAMA_380, Designacion = Designacion.objects.get(name = DesignaName))
                        pn.save()
                except IndexError:
                    break

    return "HECHO"

#Limpiar los PN de un componente, por si cambian
def resetCompObject():
    for comp in ComponenteAPT5.objects.all():
        comp.parNumber.clear()
        comp.save()

#Actualizar los componentes del APT5, están en un excel aparte, por eso se hace aqui
@csrf_exempt
def updateCompAPT5(df):
    resetCompObject()
    for i in range(0,300):
        try:
            CompName = df.iat[i,0]  #Misma designacion que componente
            PNname2 =  df.iat[i,2]
            PNname = df.iat[i,1]
        except IndexError:
            break
        if pd.isnull(CompName):
            break
        try:
            compAPT5 = ComponenteAPT5.objects.get(name = CompName)
        except ComponenteAPT5.DoesNotExist:
            compAPT5 = ComponenteAPT5(name = CompName, componente = Componente.objects.get(name = CompName))
        compAPT5.save()
#        compList = ["LAMINADO_NUT_PLATES_OPP_&_NACA","ENC/COR_ATL_NACA_&_OPP_RH","ENC/COR_ATL_NACA_&_OPP_LH","KIT_FV_GASKETS_NACA_&_OPP"]

        pieza = "V900V1000"
        if pd.isnull(PNname) == False:  
            PNname = PNname.replace("\n","")
            try:
                pn = PN.objects.get(name = PNname)    
                
            except PN.DoesNotExist:
                DesignaName = "V900" + CompName + "_" + PNname
                designa = Designacion(name = DesignaName,  Componente = Componente.objects.get(name = CompName))
                designa.save()
            
                pn = PN(name = PNname, programa = Programa.objects.get(name = "350"),
                        Designacion = designa)
                pn.save()
            compAPT5.parNumber.add(pn)
            compAPT5.save()
        else:
            pieza="V1000"
            
        if pd.isnull(PNname2) == False:   
            PNname2 = PNname2.replace("\n","")     
            try:
                pn2 = PN.objects.get(name = PNname2)

            except PN.DoesNotExist:
                DesignaName2 = "V1000" + CompName
                designa2 = Designacion(name = DesignaName2,  Componente = Componente.objects.get(name = df.iat[i,0]))
                designa2.save()
                
                pn2 = PN(name = PNname2, programa = Programa.objects.get(name = "350"),
                         Designacion = designa2)
                pn2.save()
            compAPT5.parNumber.add(pn2)
            compAPT5.save()        
        else:
            pieza="V900"
#        
#        if CompName in compList:
#            print("Se guarda: " + CompName)
#            print(compAPT5.parNumber.count())
        compAPT5.pieza = pieza
        compAPT5.save()
    return "Hecho"

#Funcion para actualizar la bd del 350
@csrf_exempt
def update350():
    file = 'xls\\350.xlsx'
    xl = pd.ExcelFile(file)
    # Load a sheet into a DataFrame by name: df1

    try:
        PROGRAMA_350 = Programa.objects.get(name = "350")
    except Programa.DoesNotExist:
        initProgramaDB()
        PROGRAMA_350 = Programa.objects.get(name = "350")
    try:
        SECTION_APT1 = Seccion.objects.get(name = "APT1")
    except Seccion.DoesNotExist:
        initSeccionDB()

    for sheet in xl.sheet_names:
#        print("HOJA " + sheet + "\n")
        df = xl.parse(sheet)
        if sheet == "Componentes":
            updateComponent(df, PROGRAMA_350)
            for i in range(0,100):
                try:
                    CompName = df.iat[i,0]  #Misma designacion que componente
                    PNname2 =  df.iat[i,2]
                    PNname = df.iat[i,1]
                except IndexError:
                    break
                if pd.isnull(CompName):
                    break
                DesignaName = "V900" + CompName
                DesignaName2 = "V1000" + CompName
                try:
                    designa = Designacion.objects.get(name = DesignaName)
                except Designacion.DoesNotExist:
                    designa = Designacion(name = DesignaName,  Componente = Componente.objects.get(name = df.iat[i,0]))
                    designa.save()
                try:
                    designa2 = Designacion.objects.get(name = DesignaName2)
                except Designacion.DoesNotExist:
                    designa2 = Designacion(name = DesignaName2,  Componente = Componente.objects.get(name = df.iat[i,0]))
                    designa2.save()
                if pd.isnull(PNname) == False:
                    try:
                        pn = PN.objects.get(Designacion = designa)
                        if pn.name != PNname:
                                pn.name = PNname
                                pn.save()
                    except PN.DoesNotExist:
                        pn = PN(name = PNname, programa = PROGRAMA_350, Designacion = Designacion.objects.get(name = DesignaName))
                        pn.save()
                if pd.isnull(PNname2) == False:
                    try:
                        pn2 = PN.objects.get(Designacion = designa2)
                        if pn2.name != PNname2:
                                pn2.name = PNname2
                                pn2.save()
                    except PN.DoesNotExist:
                        pn2 = PN(name = PNname2, programa = PROGRAMA_350, Designacion = Designacion.objects.get(name = DesignaName2))
                        pn2.save()  
        elif "Componentes_APT5" == sheet:
            updateComponent(df, PROGRAMA_350)
            updateCompAPT5(df)                        
        elif "SGM" == sheet:
            updateSGM(df, "350")
        elif "DESVIACION" in sheet:
            updateDefect(df, Seccion.objects.get(name = sheet.replace("DESVIACION_","")))
        elif "AREA" in sheet:
            updateArea(df, Seccion.objects.get(name = sheet.replace("AREA_","")))
        elif sheet == "PIEZA":
            for i in range(0,200):
                try:
                    name = df.iat[i,0]
                    if pd.isnull(name):
                        break
                    try:
                        Pieza.objects.get(name = name)
                    except Pieza.DoesNotExist:
                        pieza = Pieza(name = name)
                        pieza.save()
                except IndexError:
                    break
    return "HECHO"

#Crea el objeto RT a partir de nombre, codigo, nivel y el rt del nivel superior
@csrf_exempt
def createRt(name, code, level, superior):   
    if level == 1:
        shortName = code
    else:
        shortName = superior.codigo + "." + code
    try:
        rt = reasonTreeField.objects.get(shortName = shortName)
    except reasonTreeField.DoesNotExist:
        if level == 1:
            rt = reasonTreeField(nivel = level, nombre = name, codigo = code, shortName = code)
        else:
            rt = reasonTreeField(nivel = level, nombre = name, codigo = code, superior = superior, shortName = shortName)
        rt.save()
    return rt    
   
#para copiar los RT entre mismos lvl, dado que el lvl3 es comun para varios rt de lvl2    
@csrf_exempt
def copyToEquals(rt1, rtRef):
    for rt in reasonTreeField.objects.filter(superior = rt1):
        for rt3 in reasonTreeField.objects.filter(superior = rtRef):
            try:
                reasonTreeField.objects.filter(superior = rt).get(codigo = rt3.codigo)
            except reasonTreeField.DoesNotExist:
                createRt(rt3.nombre, rt3.codigo, 3, rt)

#Actualizar desde el archivo     
@csrf_exempt
def updateRsnTree():
    file = "xls\\reasonTree.xlsx"
    xl = pd.ExcelFile(file)
    df = xl.parse("CVAT")
    first = ""
    try:
        for i in range(1, 10000):
            if pd.isnull(df.iat[i,0]) == False:
                if i != 1:
                    copyToEquals(rt1, first)
                    first = ""
                name1 = df.iat[i,0]
                cod1 = df.iat[i,1]
                rt1 = createRt(name1, cod1, 1, None)
                level2 = []
            if pd.isnull(df.iat[i,3]) == False:
                name2 = df.iat[i,2]
                cod2 = df.iat[i,3]
                rt2 = createRt(name2, cod2, 2, rt1)
                if first == "":
                    first = rt2
                level2.append(rt2)
            if pd.isnull(df.iat[i,4]) == False:
                name3 = df.iat[i,4]
                cod3 = df.iat[i,5]
                for rtLvl2 in level2:
                    createRt(name3, cod3, 3, rtLvl2) 
        copyToEquals(rt1, first)                
    except IndexError:
        indexError = True
        
    df = xl.parse("380CVAT")
    try:
        for i in range(0,100):
            if pd.isnull(df.iat[i,0]) == False:
               name1 = df.iat[i,0] 
               cod1 = df.iat[i,1]
               rt1 = createRt(name1, cod1, 1, None)
               
               shortName = cod1
               rt = reasonTree(nivel1 = rt1, nivel2 = rt1, nivel3 = rt1, shortName = shortName, program = Programa.objects.get(name = "380"))
               rt.save()
    except IndexError:
        indexError = True               
                
    return "Not Error"

#Para quitar comas de las lineas de los csv
def parseCSV(typeToParse, strToParse):
    toReturn = []
    strToParse = str(strToParse)
    index = strToParse.find(',')
    last = 0
    if pd.isnull(strToParse) == True:
        return toReturn
    while last != -1:
        if index == -1:
            newItem = strToParse[:len(strToParse)]
        else:
            newItem = strToParse[:index]
        if typeToParse == "section":
            toReturn.append(Seccion.objects.get(name = newItem))
        elif typeToParse == "programa":
            while len(newItem) < 3:
                newItem = newItem + "0"
            toReturn.append(Programa.objects.get(name = newItem))
        else:
            while len(newItem) < 4:
                newItem = "0" + newItem
            toReturn.append(SGM.objects.get(number = newItem))
        last = index
        strToParse = strToParse[index + 1:]
        index = strToParse.find(',')
    return toReturn

#Crear usuario desde csv
@csrf_exempt
def createMyUser(name, email,passwd, fullName, userAuth, typeUserObject, admin, NG, programList, sgmList, sectionList):
    if myUser.objects.filter(user=userAuth).count() == 0:
        newUser = myUser(name = name, email = email, passwd = passwd,nombreCompleto = fullName,
                         user = userAuth, typeUser = typeUserObject, admin = admin, NA = NG)
        newUser.save()
        if pd.isnull(programList) == False:
            for program in parseCSV("programa", programList):
                newUser.programa.add(program)
                newUser.save()
        if pd.isnull(sectionList) == False:        
            for section in parseCSV("section", sectionList):
                if section.programa in parseCSV("programa", programList):
                    newUser.seccion.add(section)
                else:
                    print("No guardado, seccion y programa no coinciden")
        if pd.isnull(sgmList) == False:
            for sgm in parseCSV("SGM", sgmList):
                sgm.user.add(newUser)
                sgm.save()
#    else:
#        print("Ya existe el usuario " + name + ", Ignorado" )
    return "Acabado"

#actualizar usuarios desde archivo csv
@csrf_exempt
def updateUserDB():
    file = "xls\\usuarios.csv"
    df = pd.read_csv(file, sep=";", header=None)
    adminList = ["c18130", "c41011", "c40162", "c42051", "airbus"]
    try:
        for i in range(1,200):
            name = df.iat[i,0]
            if(pd.isnull(name)):
                break;
            email = df.iat[i,1]
            programList = df.iat[i,2]
            sectionList = df.iat[i,3]
            typeUser = df.iat[i,4]
            sgmList = df.iat[i,7]
            typeUserObject = tipoUsuario.objects.get(name = typeUser)
            if name in adminList:
                admin = True
            else:
                admin = False
            passwd = df.iat[i,5]
            NG = df.iat[i,6]
            fullName = df.iat[i,8]
            if modelsAuth.User.objects.filter(username = name).count() == 0:
                userAuth = modelsAuth.User.objects.create_user(username = name, password = passwd)
                userAuth.save()
                createMyUser(name, email,passwd, fullName, userAuth, typeUserObject, admin, NG, programList, sgmList, sectionList)
            else:
                userAuth = modelsAuth.User.objects.filter(username = name)[0]
                createMyUser(name, email,passwd, fullName, userAuth, typeUserObject, admin, NG, programList, sgmList, sectionList)
#                print("Ya existe el usuario " + name + ", Ignorado" )
    except IndexError:
        indexError = True
    return "Acabado"

#Suma las horas en string y las devuelve en string
def sumHour(current, toAdd):
    if current == "":
        current = "0"
    try:
        return str(float(current.replace(',','.')) + float(toAdd.replace(',','.')))
    except:
        return "0.0"

#Para cambiar el error de agregar en descripcion como posible defecto.
#Ya no tiene sentido pero se deja por si acaso
def changeDescpTBD380():
    TBDdefc = Defecto.objects.filter(seccion__name = "380").get(name = "TBD")
    for f412 in F412_VALID.filter(programa__name = "380"):
        if f412.Defecto.name == "En_Descripcion":
            f412.Defecto = TBDdefc
            f412.save()
    for f412 in f412Ant.objects.all():
        f412.Defecto = TBDdefc
        if f412.Defecto.name == "En_Descripcion":
            f412.Defecto = TBDdefc
            f412.save()
    return ""

#Añade las horasa cada avion desde el f412        
def sumPlaneRepF412(f412Rep, plane, isF412):
    if isF412:
        hour = f412Rep.horasRecurrentes
        hourLT = f412Rep.horas
        plane.f412List.add(f412Rep)
    else:
        hour = f412Rep.horas
        hourLT = f412Rep.horasLeadTime
        plane.repList.add(f412Rep)
    if f412Rep.codigoCausa.name == "M60":
        plane.hRecM60 = hour
        plane.hLTM60 = hourLT
    elif f412Rep.codigoCausa.name == "RL8":
        plane.hRecRL8 = hour
        plane.hLTRL8 = hourLT
    elif f412Rep.codigoCausa.name == "ALB":
        plane.hRecALB = hour
        plane.hLTALB = hourLT
    elif f412Rep.codigoCausa.name == "V10":  
        plane.hRecV10 = hour
        plane.hLTV10 = hourLT 
    plane.save()
    return ""

#Actualiza un avion
def updatePlane():
    f412List = F412.objects.filter(programa__name = "")
    repList = Reparacion.objects.filter(programa__name = "")
    for i in range(1,5):
        aptName = "APT" + str(i)
        repList = repList | Reparacion.objects.filter(seccion__name = aptName)
        f412List = f412List | F412_VALID.filter(seccion__name = aptName)
    for f412 in f412List:
        try:
            plane = avion.objects.get(numero = f412.nAV)
            if f412 in plane.f412List.all():
                continue
            else:
                sumPlaneRepF412(f412, plane, True)
        except:
            if "V9" in f412.Pieza.name :
                v1000 = False
            else:
                v1000 = True
            plane = avion(numero = f412.nAV, v1000 = v1000)    
            plane.save()
            sumPlaneRepF412(f412, plane, True)
    for rep in repList:            
        try:
            plane = avion.objects.get(numero = rep.nAV)
            if rep in plane.repList.all():
                continue
            else:
                sumPlaneRepF412(rep, plane, False)
        except:
            if "V9" in rep.Pieza.name :
                v1000 = False
            else:
                v1000 = True
            plane = avion(numero = rep.nAV, v1000 = v1000)    
            plane.save()
            sumPlaneRepF412(rep, plane, False)
    return ""

#Funcion principal que actualiza todos los campos actualizables en la aplicacion
@csrf_exempt
def updateDB(request):
#    toReturn = update380()
#    toReturn = update350()
#    toReturn = updateRsnTree()
#    toReturn = updateUserDB()
#    toReturn = changeDescpTBD380()   #Funcion puntual para cambiar a TBD los f412 que salian como en_descripcion
    toReturn = updatePlane()
#    toReturn = updateOldF412()   #Comentar cuando se haga 1 vez

    return HttpResponseRedirect("/administrador")

#Exporta el 380
@csrf_exempt
def export380(request, status):
    response = HttpResponse(content_type='text/csv')
    
    f412List = F412_VALID.filter(programa__name = "380")      
    WholeProgram = True
            
    if status != "" :
        WholeProgram = False
        f412List = f412List.filter(Estado__name = status)
        status = "_" + status
    fileName = "F412_A380" + status + "(" + dateToString(date.today()) + ").csv"
    response['Content-Disposition'] = 'attachment; filename=' + fileName 
    
    myContext = Context({'f412List': f412List})
    myContext["WholeProgram"] = WholeProgram
    
    template = get_template("csv/A380.txt")
    response.write(template.render(myContext))
    
    return response

#Exporta el 350 
@csrf_exempt
def export350(request, sectionName, status):
    response = HttpResponse(content_type='text/csv')
    
    f412List = F412.objects.filter(programa__name = "350").order_by("Fecha") 
    WholeSection = True
            
    if status != "":
        f412List = f412List.filter(Estado__name = status)
        status = "_" + status
        WholeSection = False
    if sectionName == "all":
        WholeProgram = True
        section = ""
    else:
        WholeProgram = False
        section = "_" + sectionName
        f412List = f412List.filter(seccion__name = sectionName)
    fileName = "F412_A350" + section + status + "(" + dateToString(date.today()) + ").csv"
    response['Content-Disposition'] = 'attachment; filename=' + fileName 

    myContext = Context({'f412List': f412List})
    myContext["WholeProgram"] = WholeProgram
    myContext["WholeSection"] = WholeSection
    
    if sectionName == "APT2":
        template = get_template("csv/APT2.txt")
    else:
        template = get_template("csv/A350.txt")
    response.write(template.render(myContext))
    
    return response

#Vista de /exportarCSV
@csrf_exempt
def exportCSV(request, section, status):
    if status == "":
        if section == "380":
            toReturn = export380(request, "")
        elif section == "350":
            toReturn = export350(request, "all", "")
        else:
            toReturn = export350(request, section, "")
    else:
        if section == "380":
            toReturn = export380(request, status)
        else:
            toReturn = export350(request, section, status)
    return toReturn

#Pagina de HTML exporta
@csrf_exempt
def exportPage(request):
#    if request.method == "POST":
#        multipleExport(request)
    template = get_template("html/CSVPage.html")
    myContext = Context({'user': request.user})
    myContext['myPath'] = request.path
    myContext['mode'] = "Reparaciones"             
    try:
        myContext['myUser'] = myUser.objects.get(user = request.user)
    except:
        print("Usuario No Encontrado")
        
    return HttpResponse(template.render(myContext))

#Pasa string a float
def toFloat(toConvert):  #En este archivo tambien pues daba problemas al importar del otro
    try:
        return float(toConvert.replace(',','.'))
    except:
        return 0.0

#obtiene datos para el grafico
def getData(avList, typeGraph): 
    N = avList.count()
    data = []
    list0 = []
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    plaList = []
    
    for av in avList:
        name = "Rank " + str(av.numero)
        if av.v1000:
            name = name + "*"
        plaList.append(name)
        if typeGraph == "TL":
            list0.append(toFloat(av.hLTALB))
            list1.append(toFloat(av.hLTV10))
            list2.append(toFloat(av.hLTRL8))
            list3.append(toFloat(av.hLTM60))
            list4.append(toFloat(av.hLTALB) + toFloat(av.hLTV10) + toFloat(av.hLTM60))
        else:    
            list0.append(toFloat(av.hRecALB))
            list1.append(toFloat(av.hRecV10))
            list2.append(toFloat(av.hRecRL8))
            list3.append(toFloat(av.hRecM60))
            list4.append(toFloat(av.hRecALB) + toFloat(av.hRecV10) + toFloat(av.hRecM60))
    data.append(list0)
    data.append(list3)
    data.append(list1)
    data.append(list2)
    data.append(list4)
    return data, N, plaList

#Lista de aviones segun los aviones en los que estemos
def getAvList (av1, av2):
    avList = avion.objects.all().order_by("numero")
    if av1 != "":
        avList = avList.filter(numero__gte=av1)
    if av1 != "":
        avList = avList.filter(numero__lte=av2)   
        
    return avList

#Actualiza las graficas a estado basico
def updateBothGraph(request):
    count = avion.objects.all().count() - 1
    lastAv = avion.objects.all().order_by("numero")[count].numero     
    countFirst = avion.objects.all().count() - 10
    firstAv = avion.objects.all().order_by("numero")[countFirst].numero     
    updateGraph(request, firstAv, lastAv, "")
    updateGraph(request, firstAv, lastAv, "TL")       
    
    return HttpResponseRedirect("/grafico")

#actualiza el grafico
def updateGraph(request, av1, av2, typeGraph):

    fig=Figure(figsize=(6,7))
    ax=fig.add_subplot(111)
    
    N = 5
    
    avList = getAvList(av1, av2)
    data, N, plaList = getData(avList, typeGraph)
    
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence
    
    p = []                                                               
    p.append(ax.bar(ind, data[0], width, color ='r'))
    p.append(ax.bar(ind, data[1], width, color = 'orange', bottom=data[0]))
    p.append(ax.bar(ind, data[2], width, color = 'g', bottom=np.array(data[0]) + np.array(data[1])))
    p.append(ax.bar(ind, data[3], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2])))
    
    if typeGraph == "TL":
        ax.set_title("Horas LT / Rank")
    else:
        ax.set_title("Horas Recurrentes / Rank")
        
    ax.set_xlabel('Rank')
    ax.set_ylabel('Horas')
    ax.set_xticks(ind)
    
    for tick in ax.get_xticklabels():
        tick.set_rotation(60)
        
    ax.set_xticklabels(plaList)
    ax.legend((p[0],p[1],p[2], p[3]), ('ALB','M60','V10', 'RL8'), loc="upper left")
    for j in range(len(p)):
        for i, patch in enumerate(p[j].get_children()):
            bl = patch.get_xy()
            x = patch.get_width() + bl[0]
            y = 0.5*patch.get_height() + bl[1]
            if data[j][i] != 0:
                name = "%f" % (data[j][i])
                dec = name.find(".") + 2
                ax.text(x,y, name[0:dec])
    
    xi = arange(0,len(data[4]))
    x = ([xi, ones(len(data[4]))])
    y = data[4]
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(xi,y)
    line = slope*xi + intercept
    
    ax.plot(line)
    
    fig.subplots_adjust(top = 0.95)
    
    canvas=FigureCanvas(fig)
#    response=HttpResponse(content_type='image/png')
    graphic = io.BytesIO()    
    fig.savefig(graphic, format="png")
    if typeGraph == "TL":
        fig.savefig("templates/images/chartTL.png", format="png")
    else:    
        fig.savefig("templates/images/chart.png", format="png")
    canvas.print_png(graphic)
    
    return