
from f412.toString import *
from f412.models import *

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import matplotlib
from numpy import arange, array, ones
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

import datetime
import operator

from django.http import HttpResponse
from django.http import HttpResponseRedirect

import pandas as pd

from django.http import FileResponse
from reportlab.pdfgen import canvas as canvasPDF
from django.views.generic import View
from django.conf import settings
from reportlab.lib.pagesizes import A4, landscape

from django.template.loader import get_template
from django.template import Context

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from datetime import date

component380 = ["S_19", "S_19.1", "HTP", "LARGUERO", "COSTILLA", "RUDDER", "TIMON", "T_WING", "T_BLGD"]
componentToPrint = ["S_19", "S_19.1", "HTP", "LARGUERO", "COSTILLA", "RUDDER", "TIMON", "T_WING", "T_BLGD", "MOVABLES"]
movList = ["RUDDER", "TIMON"]
MONTH = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

YEAR = datetime.datetime.now().year
LAST_YEAR = YEAR - 1
LAST_LAST_YEAR = YEAR - 2

YEAR_DATE = parseDate(str(YEAR) + "/01/01")
LAST_YEAR_DATE = parseDate(str(LAST_YEAR) + "/01/01")
LAST_LAST_YEAR_DATE = parseDate(str(LAST_LAST_YEAR) + "/01/01")

repEmpty = Reparacion.objects.filter(myID = -5)
F412Empty = F412.objects.filter(myID = -5)

daysMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

month31 = [1, 3, 5 , 7, 8, 10, 12]
month30 = [4, 6, 9, 11]

def getBasicContext(request):
    myContext = {'user': request.user}
    myContext["mode"] = "Reparaciones"
    myContext['myPath'] = request.path
    myContext["codCausList"] = codCaus.objects.all()
    myContext["request"] = request
    try:
        myContext['myUser'] = myUser.objects.get(user = request.user)
    except:
        print("Usuario No Encontrado")

    return myContext

@csrf_exempt
def updatePlaneNumbers(request, program):
    return serveUpdatePlaneNumbers(request, program, datetime.datetime.now().month - 1, YEAR, False)

@csrf_exempt
def changeMonthYear(request, program):
    try:
        month = request.POST["month"]
        year = request.POST["year"]
    except:
        year = YEAR
        month = datetime.datetime.now().month - 1

    return serveUpdatePlaneNumbers(request, program, month, year, True)

@csrf_exempt
def serveUpdatePlaneNumbers(request, program, month, year, changeDate):
    myContext = getBasicContext(request)
    myContext["program"] = program
    myContext["defYear"] = int(year)
    myContext["defMonth"] = int(month)

    if program == "380":
        myContext["componentList"] = component380

    template = get_template("html/mensual/updatePlanes.html")

    if request.method == "POST" and changeDate == False:
        savePlanes(request, program, month, year)

    myContext = getContextYears(request, myContext)

    return HttpResponse(template.render(myContext))

@csrf_exempt
def savePlanes(request, program, month, year):
    program = Programa.objects.get(name = program)
    year = request.POST["year"]
    month = request.POST["month"]

    if program.name == "380":

        for component in component380:
            formName = component + "Number"
            numPlane = request.POST[formName]
            numPlane = float(str(numPlane).replace(",","."))
            componentObj = Componente.objects.get(name = component)
            try:
                plane = planesCount.objects.filter(program = program).filter(year = year).filter(mes = month).get(component = componentObj)
                plane.numPlanes = numPlane
            except:
                plane = planesCount(program = program, year = year, mes = month, component = componentObj, numPlanes = numPlane)
            plane.save()

    else:
        numPlane = request.POST["350Number"]
        numPlane = float(str(numPlane).replace(",","."))
        try:
            plane = planesCount.objects.filter(program = program).filter(year = year).get(mes = month)
            plane.numPlanes = numPlane
        except:
            plane = planesCount(program = program, year = year, mes = month, numPlanes = numPlane)
        plane.save()

    return

@csrf_exempt
def changeMonthHour(request, program, codCausName):
    try:
        month = request.POST["month"]
        year = request.POST["year"]
    except:
        year = YEAR
        month = datetime.datetime.now().month - 1

    if request.method == "POST":
        shouldSave = True
    else:
        shouldSave = False

    return serveUpdateHours(request, program, month, year, codCausName, shouldSave)

@csrf_exempt
def changeHours(request, program, codCausName):
    return serveUpdateHours(request, program, datetime.datetime.now().month - 1, YEAR, codCausName, False)

@csrf_exempt
def serveUpdateHours(request, program, month, year, codCausName, changeDate):
    myContext = getBasicContext(request)
    myContext["program"] = program
    myContext["defYear"] = int(year)
    myContext["defMonth"] = int(month)
    myContext["codCausName"] = codCausName

    year = int(year)
    month = int(month)

    if year < 2016 or year > YEAR:
        myContext["errorMessage2"] = "Elija un año entre 2016 y 2017."
    elif codCausName == "ALB" or codCausName == "M60":
        if year >= 2018 and month >= 6:
            myContext["errorMessage2"] = "En 2018 a partir de Junio las horas " + codCausName + " se calculan con los F412 de la app.\n No es aconsejable cambiarlo"
    elif codCausName == "RL8":
        if year >= 2018 and month >= 9:
            myContext["errorMessage2"] = "En 2018 a partir de Septiembre las horas " + codCausName + " se calculan con los F412 de la app.\n No es aconsejable cambiarlo"

    if program == "380":
        myContext["componentList"] = component380

    template = get_template("html/mensual/updateHours.html")

    if request.method == "POST" and changeDate == False:
        saveHours(request, program, month, codCausName, year)

    myContext = getContextYears(request, myContext)

    return HttpResponse(template.render(myContext))


@csrf_exempt
def saveHours(request, program, month, codCausName, year):
    program = Programa.objects.get(name = program)
    codCausObj = codCaus.objects.get(name = codCausName)
    year = request.POST["year"]
    month = request.POST["month"]

    if program.name == "380":

        for component in component380:
            formName = component + "Number"
            hoursForm = request.POST[formName]
            hoursForm = float(str(hoursForm).replace(",","."))
            componentObj = Componente.objects.get(name = component)
            try:
                hour = oldHour.objects.filter(program = program).filter(year = year).filter(month = month).filter(codCaus = codCausObj).get(component = componentObj)
                hour.hours = hoursForm
            except:
                hour = oldHour(program = program, year = year, month = month, component = componentObj, hours = hoursForm, codCaus = codCausObj)
            hour.save()

    else:
        hoursForm = request.POST["350Number"]
        hoursForm = float(str(hoursForm).replace(",","."))
        try:
            hour = oldHour.objects.filter(program = program).filter(year = year).filter(codCaus = codCausObj).get(month = month)
            hour.hours = hoursForm
        except:
            hour = oldHour(program = program, year = year, month = month, hours = hoursForm, codCaus = codCausObj)
        hour.save()

    return

@csrf_exempt
def getHours(month, year, program, component, codCausName):
    f412List = F412.objects.filter(Estado__name = "Concedido")
    repList = Reparacion.objects.all()

    if program == "380":
        f412List = f412List.filter(Componente__name = component)
        repList = repList.filter(Componente__name = component)

    codCausObj = codCaus.objects.get(name = codCausName)

    f412List = f412List.filter(programa__name = program)
    repList = repList.filter(programa__name = program)
    f412List = f412List.filter(codigoCausa = codCausObj)
    repList = repList.filter(codigoCausa = codCausObj)

    date_sup = parseDate(str(year) + "/" + str(month) + "/" + str(daysMonth[month-1]))
    date_inf = parseDate(str(year) + "/" + str(month) + "/01" )

    f412List = f412List.filter(Fecha__gte = date_inf).filter(Fecha__lte = date_sup)
    repList = repList.filter(Fecha__gte = date_inf).filter(Fecha__lte = date_sup)

    return sumHours(f412List, repList)


@csrf_exempt
def updateHours(month, year, program, component, codCausName):
    if year <= 2018 and month < 6:
        return False

    if program == "380":
        hourList = oldHour.objects.filter(program__name = program).filter(component__name = component)
    else:
        hourList = oldHour.objects.filter(program__name = program)

    try:
        oldHourObj = hourList.filter(year = year).filter(month = month).get(codCaus__name = codCausName)
    except:
        programObj = Programa.objects.get(name = program)
        codCausObj = codCaus.objects.get(name = codCausName)
        componentObj = Componente.objects.get(name = component)
        oldHourObj = oldHour(year = year, month = month, codCaus = codCausObj, program = programObj, component = componentObj)
        oldHourObj.save()

    hoursToUpdate = getHours(month, year, program, component, codCausName)
    if hoursToUpdate != 0.0:
        oldHourObj.hours = hoursToUpdate
        oldHourObj.save()

    return True

@csrf_exempt
def updateHoursMonthYear(year, month):
    codCausList = ["ALB", "M60", "RL8"]
    component350 = Componente.objects.all()[0].name

    for codCausName in codCausList:
        updateHours(month, year, "350", component350, codCausName)

        for component in component380:
            updateHours(month, year, "380", component, codCausName)

    return True

@csrf_exempt
def handleUpdateHours(request):

    try:
        monthToUpdate = request.POST["monthToUpdate"]
        yearToUpdate = request.POST["yearToUpdate"]
    except:
        monthToUpdate = datetime.datetime.now().month
        yearToUpdate = YEAR

    monthToUpdate = int(monthToUpdate)
    yearToUpdate = int(yearToUpdate)

    if monthToUpdate == "Todos":
        if yearToUpdate == int(YEAR):
            monthRef = int(datetime.datetime.now().month)
        else:
            monthRef = 12
    else:
        monthRef = monthToUpdate

    for month in range(1, monthRef):
        updateHoursMonthYear(yearToUpdate, month)

    return HttpResponseRedirect("/rootMensual")

@csrf_exempt
def sumHours(f412List, repList):
    totalHours = 0.0

    for f412 in f412List:
        if f412.programa.name == 350:
            hoursToSum = float(f412.horasRecurrentes.replace(",",".").replace("..","."))
        else:
            hoursToSum = float(f412.horas.replace(",",".").replace("..","."))
        totalHours = totalHours + hoursToSum

    for rep in repList:
        hoursToSum = float(rep.horas.replace(",",".").replace("..","."))
        totalHours = totalHours + hoursToSum

    return totalHours

def getContextYears(request, myContext):
    monthList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    lastMonth = datetime.datetime.now().month

    yearMonthList = monthList[:lastMonth]
    currentYear = YEAR

    yearList = []
    for year in range(2016, YEAR + 1):
        yearList.append(year)

    myContext["monthList"] = monthList
    myContext["yearMonthList"] = yearMonthList
    myContext["currentYear"] = currentYear
    myContext["yearList"] = yearList

    return myContext

@csrf_exempt
def serveRootMensual(request):
    myContext = getBasicContext(request)
    template = get_template("html/mensual/rootMensual.html")

    myContext = getContextYears(request, myContext)

    return HttpResponse(template.render(myContext))

@csrf_exempt
def updatePlanes(request):
    template = get_template("html/mensual/rootMensual.html")
    myContext = getBasicContext(request)
    myContext = getContextYears(request, myContext)

    updateFromXls(request)
    updateFromApp(request)

    return HttpResponse(template.render(myContext))

@csrf_exempt
def updateFromXls(request):
    template = get_template("html/mensual/rootMensual.html")
    myContext = getBasicContext(request)
    myContext = getContextYears(request, myContext)

    parseXls("350")
    parseXls("380")

    return HttpResponse(template.render(myContext))

@csrf_exempt
def updateFromApp(request):
    template = get_template("html/mensual/rootMensual.html")
    myContext = getBasicContext(request)
    myContext = getContextYears(request, myContext)

    parseXls("350")
    parseXls("380")

    return HttpResponse(template.render(myContext))


def parseXls(program):

    file = 'xls\\mensual' + program + '.xlsx'
    xl = pd.ExcelFile(file)

    programObj = Programa.objects.get(name = program)

    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        if sheet.find("AVIONES") == -1:
            codCausObj = codCaus.objects.get(name = sheet)
            readRow(df, 0, codCausObj, programObj, "Hours")
        elif sheet == "AVIONES380":
            readRow(df, 0, "", programObj, "Planes380Tot")
        else:
            readRow(df, 0, "", programObj, "Planes")

    return "HECHO"

def readRow(df, row, codCausObj, program, typeRow):

    try:
#    if True:
        month = df.iat[row, 0]
        data2016 = df.iat[row, 1]
        data2017 = df.iat[row, 2]
        data2018 = df.iat[row, 3]

        if program.name == "380" and typeRow != "Planes380Tot":
            component = Componente.objects.get(name = df.iat[row, 4])
        else:
            component = Componente.objects.all()[0]

        if typeRow == "Hours":
            saveHoursXls(program, component, 2016, month, data2016, codCausObj)
            saveHoursXls(program, component, 2017, month, data2017, codCausObj)
            saveHoursXls(program, component, 2018, month, data2018, codCausObj)
        elif typeRow == "Planes380Tot":
#            print("Entro " + str(row))
            savePlaneXls(program, component, 2016, month, data2016, True)
            savePlaneXls(program, component, 2017, month, data2017, True)
            savePlaneXls(program, component, 2018, month, data2018, True)
        else:
            savePlaneXls(program, component, 2016, month, data2016, False)
            savePlaneXls(program, component, 2017, month, data2017, False)
            savePlaneXls(program, component, 2018, month, data2018, False)

        readRow(df, row + 1, codCausObj, program, typeRow)

    except IndexError:
        print("Acabo A" + program.name + " " + typeRow + " en linea " + str(row))
        return

    return

def saveHoursXls(program, component, year, month, hours, codCausObj):
    try:
#    if True:
        auxList = oldHour.objects.filter(program = program).filter(component = component)
        toModify = auxList.filter(year = year).filter(month = month).get(codCaus = codCausObj)
        if hours != 0.0:
            toModify.hours = hours
    except:
        toModify = oldHour(program = program, component = component, year = year,
                           month = month, codCaus = codCausObj, hours = hours)
#
    toModify.save()

    return

def savePlaneXls(program, component, year, month, numPlanes, is380Tot):
    try:
#    if True:
        auxList = planesCount.objects.filter(program = program).filter(component = component)
        auxList = auxList.filter(is380Tot = is380Tot)
        toModify = auxList.filter(year = year).get(mes = month)
        toModify.numPlanes = numPlanes
    except:
        toModify = planesCount(program = program, component = component, year = year,
                           mes = month, numPlanes = numPlanes, is380Tot = is380Tot)

    toModify.save()

    return

"""
Gráficos
"""

"""
OBTENCION DE DATOS
"""

def getData(year, comp, program):

    dataALB = []
    dataM60 = []
    dataRL8 = []
    nPlanes = []

    if program == "380" and comp == "":
        is380Tot = True
    else:
        is380Tot = False

    if comp == "MOVABLES":
        planesList = planesCount.objects.filter(program__name = program).filter(component__name = "RUDDER").filter(year = year)
        oldHourList = oldHour.objects.filter(program__name = program).filter(component__name = "RUDDER").filter(year = year)
        planesList = planesList | planesCount.objects.filter(program__name = program).filter(component__name = "TIMON").filter(year = year)
        oldHourList = oldHourList | oldHour.objects.filter(program__name = program).filter(component__name = "TIMON").filter(year = year)
    else:
        planesList = planesCount.objects.filter(program__name = program).filter(year = year)
        oldHourList = oldHour.objects.filter(program__name = program).filter(year = year)
        if comp != "":
            planesList = planesList.filter(component__name = comp)
            oldHourList = oldHourList.filter(component__name = comp)

    planesList = planesList.filter(is380Tot = is380Tot)

    for month in range(1,13):
        nPlanes.append(sumPlanesQuery(planesList.filter(mes = month)))
        dataALB.append(sumHourQuery(oldHourList.filter(codCaus__name = "ALB").filter(month = month)))
        dataRL8.append(sumHourQuery(oldHourList.filter(codCaus__name = "RL8").filter(month = month)))
        dataM60.append(sumHourQuery(oldHourList.filter(codCaus__name = "M60").filter(month = month)))

    return dataALB, dataRL8, dataM60, nPlanes

def sumHourQuery(querySetHour):
    toReturn = 0.0
    for oldHour in querySetHour:
        toReturn = toReturn + oldHour.hours

    return round(toReturn, 3)

def sumPlanesQuery(querySetPlane):
    toReturn = 0.0
    for plane in querySetPlane:
        toReturn = toReturn + plane.numPlanes

    return round(toReturn, 3)

def nanToZero(data, month):

    for i in range(0, len(data)):
        if pd.isnull(data[i]):
            data[i] = 0

    for i in range(month, len(data)):
        data[i] = 0.0

    return data

def nanMonth(data, month, typeToInsert):

    if typeToInsert == "nan":
        for i in range(month, len(data)):
            data[i] = float('nan')
    else:
        for i in range(month, len(data)):
            data[i] = 0.0

    return data

@csrf_exempt
def printAllData(request):
    for month in range(1,12):
        printAllDataMonthYear(request, YEAR, month)

    return printAllDataMonthYear(request, YEAR, 12)

@csrf_exempt
def printAllDataMonth(request, month):
    return printAllDataMonthYear(request, YEAR, 12)

@csrf_exempt
def printAllDataMonthYear(request, year, month):
    year = int(year)
    month = int(month)
    printData("", 350, month, year)

    data380 = []
    for comp in componentToPrint:
        toAppend = printData(comp, 380, month, year)
        if comp != "MOVABLES":
            data380.append(sum(nanToZero(toAppend, month)))

    printData("", 380, month, year)

    printPercentGraph(data380, month, year)

    return HttpResponseRedirect("/rootMensual")


def printData(comp, program, month, year):

    """
    CY = Current year
    PY = Past year
    PPY = past past year
    """
    folder = "templates/images/mensual/" + str(year) + "/"

    ALB_cy, RL8_cy, M60_cy, nPlaneCy = getData(year, comp, str(program))
    ALB_py, RL8_py, M60_py, nPlanePy = getData(year - 1 , comp, str(program))
    ALB_ppy, RL8_ppy, M60_ppy, nPlanePpy = getData(year - 2, comp, str(program))

    totalCY, normCY = getTotal(ALB_cy, RL8_cy, M60_cy, nPlaneCy, year, month)
    totalPY, normPY = getTotal(ALB_py, RL8_py, M60_py, nPlanePy, year - 1, 12)
    totalPPY, normPPY = getTotal(ALB_ppy, RL8_ppy, M60_ppy, nPlanePpy, year - 2, 12)

    if comp == "":
        nameFig = folder + str(month) + "/" + comp.lower() + "Total" + str(program) + ".png"
        title = "Comparativa Horas de Desviaciones en A" + str(program) + "(ALB, M60 y RL8)"

        nameFigNorm = nameFig.replace("Total", "TotalNorm")
        titleNorm = title.replace("Desviaciones", "Desviaciones Normalizadas")

        totalCY = nanMonth(totalCY, month, "nan")
        normCY = nanMonth(normCY, month, "nan")
        saveGraphTotal(totalCY, totalPY, totalPPY, title, nameFig, month)
        saveGraphTotal(normCY, normPY, normPPY, titleNorm, nameFigNorm, month)

    else:
        printLongBarChart(nanMonth(ALB_cy, month, ""), ALB_py, ALB_ppy, comp, "Accidentales", month, year)
        printLongBarChart(nanMonth(RL8_cy, month, ""), RL8_py, RL8_ppy, comp, "Reparaciones", month, year)
        printLongBarChart(nanMonth(M60_cy, month, ""), M60_py, M60_ppy, comp, "Manuales", month, year)

    if program != 380 or comp != "":

        if program == 350:
            name = "A350"
        else:
            name = comp

        dataCy = [sum(ALB_cy[:month]), sum(RL8_cy[:month]), sum(M60_cy[:month])]
        dataPy = [sum(ALB_py[:month]), sum(RL8_py[:month]), sum(M60_py[:month])]
        dataPpy = [sum(ALB_ppy[:month]), sum(RL8_ppy[:month]), sum(M60_ppy[:month])]
        printBarChart(dataCy, dataPy, dataPpy, nPlaneCy, nPlanePy, nPlanePpy, month, year, name)

    return totalCY

def getTotal(dataALB, dataRL8, dataM60, nPlanes, year, month):
    acum = 0.0
    totPlane = 0.0
    total = []
    norm = []

    for i in range(0,12):
        monthData = dataALB[i] + dataRL8[i] + dataM60[i]
        acum = monthData + acum
        total.append(round(acum,3))
        totPlane = totPlane + nPlanes[i]

        try:
            norm.append(round(acum/totPlane ,3))
        except:
            norm.append(0.0)

    if year == YEAR:
        startIndex = month
        for i in range(startIndex, 12):
            total[i] = float('nan')
            norm[i] = float('nan')

    return total, norm


def printBarChart(dataCy, dataPy, dataPpy, nPlaneCy, nPlanePy, nPlanePpy, month, year, name):
    folder = "templates/images/mensual/" + str(year) + "/" + str(month) + "/"
    codCausList = ["Accidentales", "Reparaciones", "Manuales"]
    i = 0

    x = [str(year - 2), str(year - 1), str(year)]

    for codCausName in codCausList:
        nameFig = folder + codCausName[:3] + name + "Acum.png"
        title = "Horas " + codCausName + " " + name + " Acum " + MONTH[month-1]

        data = [dataPpy[i], dataPy[i], dataCy[i]]
        tot = []
        tot.append(sum(nPlanePpy[:month]))
        tot.append(sum(nPlanePy[:month]))
        tot.append(sum(nPlaneCy[:month]))

        for j in range(0, len(data)):
            if tot[j] == 0.0:
                data[j] = 0
            else:
                data[j] = data[j] / tot[j]

        saveBarChart(data, x, title, nameFig, codCausName[:-2], "")

        if name == "A350":
            nameFig = nameFig.replace("Acum", "Norm")
            title = title.replace("Acum", "Normalizado")
            dataToPrint = []
            for j in range(0, len(tot)):
                if tot[j] == 0.0:
                    dataToPrint.append(0.0)
                else:
                    dataToPrint.append(data[j]/tot[j])

            saveBarChart(dataToPrint, x, title, nameFig, "Total P/avión", "")

        i = i + 1

    if name != "A350":
        dataAcum = []
        tot = []
        data = [dataPpy, dataPy, dataCy]
        tot.append(sum(nPlanePpy[:month]))
        tot.append(sum(nPlanePy[:month]))
        tot.append(sum(nPlaneCy[:month]))

        for j in range(0, len(tot)):
            if tot[j] == 0.0:
                dataAcum.append(0.0)
            else:
                dataAcum.append(sum(data[j])/tot[j])

        title = "Horas de desviaciones acum. " + MONTH[month-1]  + "\n" + name
        title = title + " A380 Normalizado (A, R y M)"
        nameFig = folder + "TotNorm" + name  + ".png"
        print(nameFig)
        saveBarChart(dataAcum, x, title, nameFig, "Total P/avión", "")

    return ""

def printPercentGraph(data, monthRef, year):
    total = sum(data)
    dataPercent = []

    for datum in data:
        try:
            dataPercent.append(datum/total * 100)
        except ZeroDivisionError:
            dataPercent.append(0.0)
    savePieChart(data, monthRef, year)

    return ""

def printLongBarChart(dataCy, dataPy, dataPpy, component, typeChart, month, year):
    folder = "templates/images/mensual/" + str(year) + "/" + str(month) + "/"
    title = "Horas de " + typeChart + " En " + component + " " + str(year - 2) + "/" + str(year)
    nameFig = folder + typeChart[:3] + "All" + component + ".png"

    saveChartBarLarge(dataCy, dataPy, dataPpy, MONTH, title, nameFig, "", "")

    return ""


"""
GRAFICO TOTAL
"""


def saveGraphTotal(dataCY, dataPY, dataPPY, title, fileName, monthToBold):
    fig=Figure(figsize=(16,14))
    ax=fig.add_subplot(111)

    N = len(dataCY)

    ind = np.arange(N)    # the x locations for the groups

    ax.plot(ind, dataCY, 'ro--')
    ax.plot(ind, dataPY, 'go--')
    ax.plot(ind, dataPPY, 'bo--')
    ax.set_title(title, fontsize = 20)

    cellText = []
    cellText.append(dataCY)
    cellText.append(dataPY)
    cellText.append(dataPPY)

    rows = [str(YEAR), str(YEAR - 1), str(YEAR-  2)]

    ax.table(cellText=cellText,
             rowLabels=rows,
             colLabels=MONTH,
             loc='bottom')

    ax.set_xlabel("Mes")
    ax.set_ylabel("Coste", fontsize = 15)
    ax.set_xticks(ind)

    ax.tick_params(
            axis='x',
            which='both',
            bottom=False,
            labelbottom=False)

    lastlastYearField = str(YEAR - 2)
    lastYearField = str(YEAR - 1)
    yearField = str(YEAR)
    currentYear = mpatches.Patch(color="r", label=yearField)
    lastYear = mpatches.Patch(color="g", label=lastYearField)
    lastlastYear = mpatches.Patch(color="b", label=lastlastYearField)

    ax.legend(handles=[lastYear, lastlastYear, currentYear], loc = "upper left")

    i = 0
    for xy in zip(ind, dataCY):
        if monthToBold == i-1:
            ax.annotate(str(round(dataCY[i], 3)), xy=xy, weight="bold")
        else:
            ax.annotate(str(round(dataCY[i], 3)), xy=xy)
        i = i + 1

    i = 0
    for xy in zip(ind, dataPY):
        if monthToBold == i-1:
            ax.annotate(str(round(dataPY[i], 3)), xy=xy, weight="bold")
        else:
            ax.annotate(str(round(dataPY[i], 3)), xy=xy)
        i = i + 1

    i = 0
    for xy in zip(ind, dataPPY):
        if monthToBold == i-1:
            ax.annotate(str(round(dataPPY[i], 3)), xy=xy, weight="bold")
        else:
            ax.annotate(str(round(dataPPY[i], 3)), xy=xy)
        i = i + 1

    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()

    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)

    return

def savePieChart(data, month, year):
    fig=Figure(figsize=(16,14))
    ax=fig.add_subplot(111)
    ax.pie(data, labels=component380, autopct='%1.00f%%', pctdistance=1.2, labeldistance=1.3)
    title = "% Distribución Horas de Desviaciones por Programa y Componente"
    ax.set_title(title, fontsize = 20)

    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()

    fileName = "templates/images/mensual/" + str(year) + "/" + str(month) + "/Percent380.png"
    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)

    return

def saveBarChart(data, xticksNames, title, fileName, xlabel, ylabel):
    fig=Figure(figsize=(16,14))
    ax=fig.add_subplot(111)

    N = len(data)
    ind = np.arange(N)
    width = 0.35

    pm, pc, pn = ax.bar(ind, data, width)
    pm.set_facecolor('blue')
    pc.set_facecolor('red')
    pn.set_facecolor('green')

    ax.set_title(title, fontsize = 20)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel, fontsize = 15)
    ax.set_xticks(ind)
    ax.set_xticklabels(xticksNames, fontsize = 15)

    pChildren = [pm, pc, pn]

    for i, patch in enumerate(pChildren):
        bl = patch.get_xy()
        x = patch.get_width()/2.0 + bl[0]
        y = patch.get_height() + bl[1]

        if data[i] != 0:
            name = str(round(data[i], 3))
            ax.text(x,y, name, ha="center", va="bottom", fontsize = 15)

    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()

    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)

    return

def saveChartBarLarge(dataCy, dataPy, dataPpy, xticksNames, title, fileName, xlabel, ylabel):
    fig=Figure(figsize=(16,14))
    ax=fig.add_subplot(111)

    N = len(dataCy)
    ind = np.arange(N)
    width = 0.25

    p = []
    p.append(ax.bar(ind, dataPpy, width=width, color = 'blue'))
    p.append(ax.bar(ind + width, dataPy, width=width, color='red'))
    p.append(ax.bar(ind + 2*width, dataCy, width=width, color='green'))

    ax.set_title(title, fontsize = 20)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel, fontsize = 15)
    ax.set_xticks(ind + 2*width / 3)
    ax.set_xticklabels(xticksNames, fontsize = 15)

    for tick in ax.get_xticklabels():
        tick.set_rotation(90)

    j = 0
    data = [dataPpy, dataPy, dataCy]

    ax.legend(p, [2016, 2017, 2018])

    for rect in p:
        for i, patch in enumerate(rect.get_children()):
            bl = patch.get_xy()
            x = patch.get_width()/2.0 + bl[0]
            y = patch.get_height() + bl[1]

            if data[j][i] != 0:
                name = str(round(data[j][i], 3))
                ax.text(x,y, name, ha="center", va="bottom", fontsize = 15)
        j = j + 1

    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()

    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)

    return

"""
PDF
"""

def drawInPDF(pdf, nameFig, x, y, widhtGraph, heightGraph):

    try:
        pdf.drawImage(nameFig, x, y, widhtGraph, heightGraph, preserveAspectRatio=False)
    except:
        nameError = "templates/images/mensual/pdf/notFound.png"
        pdf.drawImage(nameError, x, y, widhtGraph, heightGraph, preserveAspectRatio=False)

    return pdf

def drawImages(pdf, width, height, extractionDate, nameFig, nameHeader, isPer):

    xCenter = width/4 - 50
    yPos1 = height/2 - 25
    widhtGraph = 2*width/3 - 100
    heightGraph = height/2 - 50

    widhtGraph = widhtGraph * 1.85
    heightGraph = heightGraph * 2
    difCenter = 160

    if isPer:
        widhtGraph = widhtGraph - 100
        difCenter = difCenter - 20

    hHeader = height - (height / 5) + 30
    wHeader = 7 * width / 8

    strLeft = 40
    strDown = 40

    pdf.setFontSize(size = 15)
    pdf.drawString(strLeft, strDown, extractionDate)

    pdf = drawInPDF(pdf, nameFig, xCenter - difCenter, yPos1 - 220, widhtGraph, heightGraph)
    pdf.drawImage(nameHeader, xCenter - 100, hHeader, wHeader)

    pdf.showPage()


    return pdf


def drawImages3(pdf, width, height, baseFolder, component, extractionDate):

    xCenter = width/4 - 50
    yPos1 = height/2 - 25
    widhtGraph = 2*width/3 - 100
    heightGraph = height/2 - 10

    hHeader = height - (height / 5) + 30
    wHeader = 7 * width / 8

    strLeft = 40
    strDown = 40

    pdf.setFontSize(size = 15)
    pdf.drawString(strLeft, strDown, extractionDate)

    nameFigALB = "AccAll" + component
    nameFigALB = baseFolder + nameFigALB + ".png"
    nameFigRL8 = "RepAll" + component
    nameFigRL8 = baseFolder + nameFigRL8 + ".png"
    nameFigM60 = "ManAll" + component
    nameFigM60 = baseFolder + nameFigM60 + ".png"
    nameHeader = "templates/images/mensual/pdf/desv" + component + ".png"

    pdf = drawInPDF(pdf, nameFigALB, xCenter - 180, yPos1, widhtGraph, heightGraph - 40)
    pdf = drawInPDF(pdf, nameFigRL8, xCenter + 240, yPos1, widhtGraph, heightGraph - 40)
    pdf = drawInPDF(pdf, nameFigM60, xCenter, yPos1 - 245, widhtGraph, heightGraph - 40)
    pdf.drawImage(nameHeader, xCenter - 100 , hHeader, wHeader)

    pdf.showPage()


    return pdf

def drawImages4(pdf, width, height, baseFolder, component, extractionDate):

    xCenter = width/4 - 50
    yPos1 = height/2 - 25
    widhtGraph = 2*width/3 - 100
    heightGraph = height/2 - 10
    heightGraph = heightGraph - 40

    heightGraphSmall = heightGraph * 7 / 11
    widhtGraphSmall = widhtGraph * 7 / 11

    heightGraphBig = heightGraph * 13/9
    widhtGraphSBig = widhtGraph * 9/7

    hHeader = height - (height / 5) + 30
    wHeader = 7 * width / 8

    strLeft = 40
    strDown = 40

    pdf.setFontSize(size = 15)
    pdf.drawString(strLeft, strDown, extractionDate)

    nameFigALB = "Acc" + component
    nameFigALB = baseFolder + nameFigALB + "Acum.png"
    nameFigRL8 = "Rep" + component
    nameFigRL8 = baseFolder + nameFigRL8 + "Acum.png"
    nameFigM60 = "Man" + component
    nameFigM60 = baseFolder + nameFigM60 + "Acum.png"
    nameFig = baseFolder + "TotNorm" + component + ".png"
    nameHeader = "templates/images/mensual/pdf/desv" + component + ".png"

    pdf = drawInPDF(pdf, nameFigALB, xCenter - 160, yPos1 + 90, widhtGraphSmall, heightGraphSmall)
    pdf = drawInPDF(pdf, nameFigRL8, xCenter - 160, yPos1 - 60, widhtGraphSmall, heightGraphSmall)
    pdf = drawInPDF(pdf, nameFigM60, xCenter - 160, yPos1 - 220, widhtGraphSmall, heightGraphSmall)
    pdf = drawInPDF(pdf, nameFig, xCenter + 110, yPos1 - 150, widhtGraphSBig, heightGraphBig)
    pdf.drawImage(nameHeader, xCenter - 100 , hHeader, wHeader)

    pdf.showPage()


    return pdf

@csrf_exempt
def exportPDFMen(request):
    month = datetime.datetime.now().month

    return exportPDFMenMonth(request, month)

@csrf_exempt
def exportPDFMenMonth(request, month):

    return exportPDFMenMonthYear(request, YEAR, month)

@csrf_exempt
def exportPDFMenMonthYear(request, year, month):
    response = HttpResponse(content_type = "application/pdf")

    buffer = io.BytesIO()
    pdf = canvasPDF.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    day = datetime.datetime.now().day
    curMonth = datetime.datetime.now().month
    extractionDate = str(day) + " " + MONTH[curMonth - 1] + ", " + str(YEAR)

    baseFolder = "templates/images/mensual/"
    baseFolder = baseFolder + str(year) + "/" + str(month) + "/"
    headerFolder = "templates/images/mensual/pdf/"

    for program in ["350", "380"]:
        nameFig = baseFolder + "Total"  + program + ".png"
        nameHeader = headerFolder + "tot" + program + ".png"
        pdf = drawImages(pdf, width, height, extractionDate, nameFig, nameHeader, False)
        nameFig = nameFig.replace("Total", "TotalNorm")
        pdf = drawImages(pdf, width, height, extractionDate, nameFig, nameHeader, False)

    nameFig = baseFolder + "Percent380.png"
    nameHeader = headerFolder + "percent380.png"
    pdf = drawImages(pdf, width, height, extractionDate, nameFig, nameHeader, True)

    for component in componentToPrint:
        pdf = drawImages3(pdf, width, height, baseFolder, component, extractionDate)
        pdf = drawImages4(pdf, width, height, baseFolder, component, extractionDate)

    pdf.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response
