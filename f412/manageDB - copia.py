import pandas as pd

import xlsxwriter

from django.views.decorators.csrf import csrf_exempt

from f412.models import *

from django.http import HttpResponse, HttpResponseRedirect

import f412.toString as toString

import datetime
from datetime import date

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
            if pd.isnull(name):
                return
            try:
                Componente.objects.get(name = name)
            except Componente.DoesNotExist:
                componente = Componente(name = name, programa = program)
                componente.save()
        except IndexError:
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
            if pd.isnull(name):
                return
            try:
                dft = Defecto.objects.get(name=name)
            except Defecto.DoesNotExist:
                dft = Defecto(name = name)
                dft.save()
            dft.seccion.add(section)
        except IndexError:
            return

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
                    if pd.isnull(DesignaName) or pd.isnull(PNname):
                        break
                    try:
                        Designacion.objects.get(name = DesignaName)
                    except Designacion.DoesNotExist:
                        designa = Designacion(name = DesignaName,  Componente = Componente.objects.get(name = sheet))
                        designa.save()
                    try:
                        PN.objects.get(name = PNname)
                    except PN.DoesNotExist:
                        pn = PN(name = PNname, programa = PROGRAMA_380,Designacion = Designacion.objects.get(name = DesignaName))
                        pn.save()
                except IndexError:
                    break

    return "HECHO"

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
                DesignaName = "V900" + CompName
                DesignaName2 = "V1000" + CompName
                if pd.isnull(DesignaName) or pd.isnull(PNname):
                    break
                try:
                    Designacion.objects.get(name = DesignaName)
                except Designacion.DoesNotExist:
                    designa = Designacion(name = DesignaName,  Componente = Componente.objects.get(name = df.iat[i,0]))
                    designa.save()
                try:
                    Designacion.objects.get(name = DesignaName2)
                except Designacion.DoesNotExist:
                    designa = Designacion(name = DesignaName2,  Componente = Componente.objects.get(name = df.iat[i,0]))
                    designa.save()
                try:
                    PN.objects.get(name = PNname)
                except PN.DoesNotExist:
                    pn = PN(name = PNname, programa = PROGRAMA_350, Designacion = Designacion.objects.get(name = DesignaName))
                    pn.save()
                try:
                        PN.objects.get(name = PNname2)
                except PN.DoesNotExist:
                    pn2 = PN(name = PNname2, programa = PROGRAMA_350, Designacion = Designacion.objects.get(name = DesignaName2))
                    pn2.save()
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
   
@csrf_exempt
def copyToEquals(rt1, rtRef):
    for rt in reasonTreeField.objects.filter(superior = rt1):
        for rt3 in reasonTreeField.objects.filter(superior = rtRef):
            try:
                reasonTreeField.objects.filter(superior = rt).get(codigo = rt3.codigo)
            except reasonTreeField.DoesNotExist:
                createRt(rt3.nombre, rt3.codigo, 3, rt)
     
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
        print("Acabado")
    return "Not Error"

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
            print("eS : " + newItem)
            toReturn.append(Programa.objects.get(name = newItem))
        else:
            while len(newItem) < 4:
                newItem = "0" + newItem
            toReturn.append(SGM.objects.get(number = newItem))
        last = index
        strToParse = strToParse[index + 1:]
        index = strToParse.find(',')
    return toReturn

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
    else:
        print("Ya existe el usuario " + name + ", Ignorado" )

@csrf_exempt
def updateUserDB():
    file = "xls\\usuarios.csv"
    df = pd.read_csv(file, sep=";", header=None)
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
            if typeUser == "ME":
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
                print("Ya existe el usuario " + name + ", Ignorado" )
    except IndexError:
        print("Acabado")
    return "Acabado"

@csrf_exempt
def updateDB(request):
    toReturn = update380()
    toReturn = update350()
    toReturn = updateRsnTree()
    toReturn = updateUserDB()

    return HttpResponseRedirect("/administrador")

@csrf_exempt
def import380(request):
    try:
        file = 'xls\\f412-A380.xlsx'
        xl = pd.ExcelFile(file)
        f412Ignored = 0
        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            for i in range(0,1000):
                notFound = False
                try:
                    myID = df.iat[i,15]
                    if pd.isnull(myID):
                        break
                    try:
                        newF412 = F412.objects.filter(programa__name = "380").get(myID = myID)
                        newF412.delete()
                    except F412.DoesNotExist:
                        pass
                    status = Estado.objects.get(name = sheet)
                    date = toString.parseDate(df.iat[i,0])
                    program = Programa.objects.get(name = "380")
                    try:
                        component = Componente.objects.get(name = df.iat[i,2])
                    except Componente.DoesNotExist:
                        notFound = True
                    try:
                        designa = Designacion.objects.get(name = df.iat[i,3])
                    except Designacion.DoesNotExist:
                        notFound = True
                    try:
                        parNumber = PN.objects.get(name = df.iat[i,4])
                    except PN.DoesNotExist:
                        notFound = True
                    ref = df.iat[i,5]
                    try:
                        defect = Defecto.objects.get(name = df.iat[i,8])
                    except Defecto.DoesNotExist:
                        notFound = True
                    try:   
                        area = Area.objects.get(name = df.iat[i,9])
                    except Area.DoesNotExist:
                        notFound = True
                    h = str(df.iat[i,12])
                    h.replace(",",".")
                    sgm = str(df.iat[i,13])
                    while len(sgm) < 4:
                        sgm = "0" + str(sgm)
                    try:
                        sgm = SGM.objects.get(number = sgm)
                    except SGM.DoesNotExist:
                        notFound = True
                    descp = df.iat[i,14]
                    action = df.iat[i,16]
                    user = request.user
                    user = myUser.objects.get(user = user)
                    section = Seccion.objects.get(name = "380")
                    if notFound:
                        print("F412 NO guardado: " + str(myID) + ", En Pagina: " + sheet)
                        f412Ignored += 1 
                    else:
                        print("Todos guardados")
                    newF412 = F412(myID = myID, Estado = status, seccion = section,
                                   Fecha = date, programa = program,
                                   Componente = component, Designacion = designa,
                                   PN = parNumber, Referencia = ref, Defecto = defect,
                                   Area = area, horas = h, SGM = sgm, Descripcion = descp,
                                   accion = action, Usuario = user)
                    newF412.save()
                except IndexError:
                    print("Index error en: " + str(i))
                    break
    except:
         print("El archivo no existe")    
    print("Total no guardados: " + str(f412Ignored))
    return

@csrf_exempt
def import350(request):
    try:
        file = 'xls\\f412-A350.xlsx'
        xl = pd.ExcelFile(file)
        print("Las hojas son:")
        print(xl.sheet_names)
        for sheet in xl.sheet_names:
            df = xl.parse(sheet)
            section = sheet[:sheet.find('-')]
            statusName = sheet[sheet.find('-')+1:]
            for i in range(0,1000):
                try:
                    myID = int(df.iat[i,22])
                    try:
                        newF412 = F412.objects.filter(seccion__name = section).get(myID = myID)
                        newF412.delete()
                    except F412.DoesNotExist:
                        pass
                    status = Estado.objects.get(name = statusName)
                    date = toString.parseDate(df.iat[i,0])
                    program = Programa.objects.get(name = "350")
                    nAV = df.iat[i,1]
                    parNumber = PN.objects.get(name = df.iat[i,2])
                    designaName = df.iat[i,3]
                    if designaName == "Designacion no guardada":
                        designaName = "default"
                    designa = Designacion.objects.get(name = designaName)
                    part = Pieza.objects.get(name = df.iat[i,4])
                    ref = df.iat[i,5]
                    defect = Defecto.objects.get(name = df.iat[i,6])
                    sectionF412 = Seccion.objects.get(name = section)
                    area = Area.objects.get(name = df.iat[i,9])
                    descp = df.iat[i,17]
                    sgm = str(df.iat[i,18])
                    while len(sgm) < 4:
                        sgm = "0" + str(sgm)
                    sgm = SGM.objects.get(number = sgm)
                    h = df.iat[i,19]
                    action = df.iat[i,21]
                    user = request.user
                    user = myUser.objects.get(user = user)
                    newF412 = F412(myID = myID, Estado = status, seccion = sectionF412,
                                   Fecha = date, programa = program, Designacion = designa,
                                   PN = parNumber, Referencia = ref, Defecto = defect,
                                   Area = area, horas = h, SGM = sgm, Descripcion = descp,
                                   accion = action, Usuario = user)    
                    newF412.save()
                except IndexError:
                    break
    except:
        print("El archivo no existe")
    return HttpResponseRedirect("/administrador")

@csrf_exempt
def importExcel(request):
    import350(request)
    import380(request)

    return HttpResponseRedirect("/administrador")

def first380Row(request, worksheet, status):
    row = 0
    col = 0
    worksheet.write(row, col, 'DIA')
    worksheet.write(row, col + 1, 'PROGRAMA')
    worksheet.write(row, col + 2, 'COMPONENTE')
    worksheet.write(row, col + 3, 'DESIGNACION')
    worksheet.write(row, col + 4, 'P/N')
    worksheet.write(row, col + 5, 'REF.')
    worksheet.write(row, col + 6, 'H.N.C.')
    worksheet.write(row, col + 7, 'DEFECTO')
    worksheet.write(row, col + 8, 'TIPO DEFECTO')
    worksheet.write(row, col + 9, 'AREA')
    worksheet.write(row, col + 10, 'AP')
    worksheet.write(row, col + 11, 'CODIGO CAUSA')
    worksheet.write(row, col + 12, 'HORAS')
    worksheet.write(row, col + 13, 'SGM')
    worksheet.write(row, col + 14, 'DESCRIPCION')
    worksheet.write(row, col + 15, 'Nº F412')
    if status == "Rechazado":
        worksheet.write(row, col + 16, 'MOTIVO DE RECHAZO')
    return

def export380(request):
    workbook = xlsxwriter.Workbook('xls\\f412-A380.xlsx')

    program = Programa.objects.get(name = "380")

    for status in Estado.objects.all():
        pageName = status.name
        worksheet = workbook.add_worksheet(pageName)
        first380Row(request, worksheet, status.name)
        row = 1
        col = 0
        for f412 in F412.objects.filter(programa = program).filter(Estado = status):
            try:
                worksheet.write(row, col, f412.Fecha.strftime("%d-%m-%y"))
            except ValueError:
                worksheet.write(row, col, toString.parseDate(f412.Fecha))
            worksheet.write(row, col + 1, '380')
            worksheet.write(row, col + 2, f412.Componente.name)
            worksheet.write(row, col + 3, f412.Designacion.name)
            worksheet.write(row, col + 4, f412.PN.name)
            worksheet.write(row, col + 5, f412.Referencia)
            worksheet.write(row, col + 8, f412.Defecto.name)
            worksheet.write(row, col + 9, f412.Area.name)
            worksheet.write(row, col + 12, f412.horas)
            worksheet.write(row, col + 13, f412.SGM.number)
            worksheet.write(row, col + 14, f412.Descripcion)
            worksheet.write(row, col + 15, f412.myID)
            if status.name == "Rechazado":
                worksheet.write(row, col + 16, f412.accion)
            row += 1
    workbook.close()
    return
        

def first350Row(request, worksheet, status):
    row = 0
    col = 0
    worksheet.write(row, col, 'Fecha')
    worksheet.write(row, col + 1, 'Nº AV')
    worksheet.write(row, col + 2, 'P/N')
    worksheet.write(row, col + 3, 'Designacion')
    worksheet.write(row, col + 4, 'LH/RH')
    worksheet.write(row, col + 5, 'REFERENCIA')
    worksheet.write(row, col + 6, 'Desviacion')
    worksheet.write(row, col + 7, 'Nº HNC')
    worksheet.write(row, col + 8, 'Nº CGI')
    worksheet.write(row, col + 9, 'ORIGEN ACC. + M.V')
    worksheet.write(row, col + 10, 'DEFECTO')
    worksheet.write(row, col + 11, 'TIPO DEFECTO')
    worksheet.write(row, col + 12, 'COMENTARIOS')
    worksheet.write(row, col + 13, 'unique_number')
    worksheet.write(row, col + 14, 'COD.CAUSA')
    worksheet.write(row, col + 15, 'P/N PZA ESPECIAL')
    worksheet.write(row, col + 16, 'REF PZA ESPECIAL')
    worksheet.write(row, col + 17, 'OPERACION')
    worksheet.write(row, col + 18, 'SGM')
    worksheet.write(row, col + 19, 'HORAS')
    worksheet.write(row, col + 20, 'DESCRIPCION')
    if status == "Rechazado":
        worksheet.write(row, col + 21, 'MOTIVO DE RECHAZO')
    worksheet.write(row, col + 22, 'Nº F412')
    return

def export350(request):
    workbook = xlsxwriter.Workbook('xls\\f412-A350.xlsx')

    program = Programa.objects.get(name = "350")

    for section in Seccion.objects.filter(programa = program):
        for status in Estado.objects.all():
            sheetName = section.name + "-" + status.name
            worksheet = workbook.add_worksheet(sheetName)
            first350Row(request, worksheet, status.name)
            row = 1
            col = 0
            for f412 in F412.objects.filter(seccion = section).filter(Estado = status):
                worksheet.write(row, col, f412.Fecha.strftime("%d-%m-%y"))
                worksheet.write(row, col + 1, f412.nAV)
                worksheet.write(row, col + 2, f412.PN.name)
                try:
                    worksheet.write(row, col + 3, f412.Designacion.name)
                except:
                    worksheet.write(row, col + 3, "Designacion no guardada")
                worksheet.write(row, col + 4, f412.Pieza.name)
                worksheet.write(row, col + 5, f412.Referencia)
                worksheet.write(row, col + 6, f412.Defecto.name)
                worksheet.write(row, col + 9, f412.Area.name)
                worksheet.write(row, col + 17, f412.Descripcion)
                worksheet.write(row, col + 18, f412.SGM.number)
                worksheet.write(row, col + 19, f412.horas)
                if status == "Rechazado":
                    worksheet.write(row, col + 21, f412.accion)
                worksheet.write(row, col + 22, f412.myID)
                row += 1
    workbook.close()
    return

@csrf_exempt
def exportExcel(request):
    export380(request)
    export350(request)

    return HttpResponseRedirect("/administrador")
