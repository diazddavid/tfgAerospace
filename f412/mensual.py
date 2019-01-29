
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
    myContext = Context({'user': request.user})
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
    myContext["defYear"] = year
    myContext["defMonth"] = month        
    
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
    myContext["defYear"] = year
    myContext["defMonth"] = month   
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
        saveHours(request, program, month, year)
    
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
                hour = oldHour.objects.filter(program = program).filter(year = year).filter(mes = month).filter(codCaus = codCausObj).get(component = componentObj)
                hour.hours = hoursForm
            except:
                hour = oldHour(program = program, year = year, mes = month, component = componentObj, hours = hoursForm, codCaus = codCausObj)
            hour.save()
            
    else:
        hoursForm = request.POST["350Number"]
        hoursForm = float(str(hoursForm).replace(",","."))
        try:
            hour = oldHour.objects.filter(program = program).filter(year = year).filter(codCaus = codCausObj).get(mes = month)
            hour.hours = hoursForm
        except:
            hour = oldHour(program = program, year = year, mes = month, hours = hoursForm, codCaus = codCausObj)
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
        oldHourObj= oldHour(year = year, month = month, codCaus = codCausObj, program = programObj, component = componentObj)
        oldHourObj.save()
    
    oldHourObj.hours = getHours(month, year, program, component, codCausName)
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
    lastMonth = datetime.datetime.now().month - 1
    
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