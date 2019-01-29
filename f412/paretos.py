# -*- coding: utf-8 -*-
# año/mes/dia
from f412.toString import *
from f412.models import *

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
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

from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from datetime import date

layupList = ["Autoclave", "Conformado", "Corte", "Desmoldeo", "Encintado", "Lay-Up"]
indList = ["Recanteado", "Reparaciones" , "Ultrasonidos"]
pareto380List = ["S_19", "S_19.1", "HTP", "LARGUERO", "COSTILLA", "MOVABLES", "TRAMPAS"]
movList = ["RUDDER", "TIMON"]
tramList = ["T_WING", "T_BLGD"]
MONTH = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

YEAR = datetime.datetime.now().year
LAST_YEAR = YEAR - 1    
YEAR_DATE = parseDate(str(YEAR) + "/01/01")
LAST_YEAR_DATE = parseDate(str(LAST_YEAR) + "/01/01")      

F412_ALL = F412.objects.filter(codigoCausa__name = "ALB") | F412.objects.filter(codigoCausa__name = "RL8")
F412_ALL = F412_ALL.filter(Estado__name = "Concedido")      
f412AntALL = f412Ant.objects.all()
repALL = Reparacion.objects.all()

repEmpty = Reparacion.objects.filter(myID = -5)
f412AntEmpty = f412Ant.objects.filter(myID = -5)
F412Empty = F412.objects.filter(myID = -5)

month31 = [1, 3, 5 , 7, 8, 10, 12]
month30 = [4, 6, 9, 11]

def getLastDay(month):
    if month in month31:
        return "31"
    elif month in month30:
        return "30"
    else:
        return "28"

def getDate(year, month):
    return parseDate(str(year) + "/" + str(month) + "/" + getLastDay(month))

def updateOldF412():
    updateParetosYear("2017")
    updateParetosYear("2018")
    return ""

def updateParetosYear(year):
    
    file = 'xls\\paretos' + year + '.xlsx'
    xl = pd.ExcelFile(file)
    # Load a sheet into a DataFrame by name: df1
    day = "05" #Dia intermedio para cogerlo luego filtrando entre 1 y 1 del mes siguiente
    total = []
    for sheet in xl.sheet_names:
        month = sheet
        date = parseDate(year + "/" + month + "/" + day)
        df = xl.parse(sheet)
        try:
            for i in range(0,500):
                if pd.isnull(df.iat[i,0]) == False:
                    compName = df.iat[i,0]
                    comp = Componente.objects.filter(alias = compName)
                    if comp.count() == 1:
                        comp = comp[0]
                        total.append(comp)
                    else:
                        continue        
                if pd.isnull(df.iat[i,1]) == False:
                    defc = Defecto.objects.filter(name = df.iat[i,1])
                    defc2 = Defecto.objects.filter(alias = df.iat[i,1])
                    if defc.count() == 1:
                        defc = defc[0]
                    elif defc2.count() == 1:
                        defc = defc2[0]
                    else:
                        continue 
                if pd.isnull(df.iat[i,2]) == False:
                    areaName = df.iat[i,2]
                    areaName.replace(" ", "")
                    area = Area.objects.filter(name = areaName)
                    if area.count() == 1:
                        area = area[0]
                    else:
                        continue     
                if pd.isnull(df.iat[i,3]) == False:
                    hours = df.iat[i,3]
                else:
                    continue   
                if pd.isnull(df.iat[i,4]) == False:
                    myID = df.iat[i,4]
                else:
                    continue
                
                try:
                    f412Ant.objects.get(myID = myID)
                except f412Ant.DoesNotExist: 
                    newf412Ant = f412Ant(Componente = comp, Defecto = defc, Area = area, Fecha = date, horas = hours, myID = myID)
                    newf412Ant.save()
        except IndexError:
            indexError = True
    return indexError
 
def getF412List(orList, toFill, pareto, date1, date2):
    f412List = toFill
    if pareto == "MOVABLES":
       for component in movList:
           f412List = f412List | orList.filter(Componente__name = component)
    elif pareto == "TRAMPAS":
        for component in tramList:
           f412List = f412List | orList.filter(Componente__name = component)
    else:
        f412List = orList.filter(Componente__name = pareto)
    f412List = f412List.filter(Fecha__gte = date1).filter(Fecha__lte = date2)

    return f412List

def getHoursDict(f412List):
    hoursDict = {}
    for defect in Defecto.objects.filter(seccion__name = "380"):
        for f412 in f412List.filter(Defecto = defect):
            try:
                defectHours = hoursDict[defect.name]
            except KeyError:
                defectHours = 0.0
            hoursDict[defect.name] = defectHours + toFloat(f412.horas)
        if defect.name not in hoursDict.keys():
            hoursDict[defect.name] = 0.0
    return hoursDict
  
def hoursToData(hoursDict, year):
    sortedDict = sorted(hoursDict.items(), key=operator.itemgetter(1))   
    data = []
    xticksNames = []
    
    for element in sortedDict:
        xticksNames.append(element[0])
        data.append(element[1] * costeHora.objects.get(year = year).precio)
        
    return data, xticksNames

def sumDictHours(dic1, dic2):
    toReturn = {}
    
    for key in dic1.keys():
        if key in dic2.keys():
            toReturn[key] = dic1[key] + dic2[key]
        else:
            toReturn[key] = dic1[key]
    
    for key in dic2.keys():
        if key not in dic1.keys() and key not in toReturn.keys():
            toReturn[key] = dic2[key]        
    
    return toReturn    

def getLastYear(names, month, pareto, typeGraph):
    monthDate = getDate(LAST_YEAR, month)
    f412Dots = F412Empty
    f412Dots2 = f412AntEmpty   
    repDots = repEmpty
    
    if typeGraph == "ind": 
        f412List = F412_ALL.filter(Area__name = pareto).filter(Fecha__gte = LAST_YEAR_DATE).filter(Fecha__lte = monthDate)
        f412List2 = f412AntALL.filter(Area__name = pareto).filter(Fecha__gte = LAST_YEAR_DATE).filter(Fecha__lte = monthDate)
        repList = repALL.filter(Area__name = pareto).filter(Fecha__gte = LAST_YEAR_DATE).filter(Fecha__lte = monthDate)
    else:    
        f412List = getF412List(F412_ALL, f412Dots, pareto, LAST_YEAR_DATE, monthDate)  
        f412List2 = getF412List(f412AntALL, f412Dots2, pareto, LAST_YEAR_DATE, monthDate)
        repList = getF412List(repALL, repDots, pareto, LAST_YEAR_DATE, monthDate)
    
    for name in names:
        f412Dots = f412Dots | f412List.filter(Defecto__name = name)
        f412Dots2 = f412Dots2 | f412List2.filter(Defecto__name = name)
        repDots = repDots | repList.filter(Defecto__name = name)
    
    if typeGraph == "lay":
        f412Dots = getLayList(f412Dots, F412Empty)
        f412Dots2 = getLayList(f412Dots2, f412AntEmpty)
        repDots = getLayList(repDots, repEmpty)
    
    hoursDict = getHoursDict(f412Dots)
    hoursDict2 = getHoursDict(f412Dots2)
    hoursDict3 = getHoursDict(repDots) 
    
    hoursDict = sumDictHours(hoursDict2, hoursDict)
    hoursDict = sumDictHours(hoursDict3, hoursDict)
    
    dotsList, xticks = hoursToData(hoursDict, LAST_YEAR)
    dotsList = dotsList[::-1][:5]
    
    return dotsList

def getDataEv(names, month, pareto, typeGraph):
    data1 = []
    data2 = []
    data3 = []
    data4 = []
    data5 = []
    data = [data1, data2, data3, data4, data5]
    
    for dataMonth in range(1, month+1):
        monthDate = getDate(YEAR, dataMonth)
        repListEmp = repEmpty 
        f412AntEmp = f412AntEmpty
        f412Emp = F412Empty
        
        if typeGraph == "ind":
            f412List = F412_ALL.filter(Area__name = pareto).filter(Fecha__gte = YEAR_DATE).filter(Fecha__lte = monthDate)
            f412AntList = f412AntALL.filter(Area__name = pareto).filter(Fecha__gte = YEAR_DATE).filter(Fecha__lte = monthDate)
            repList = repALL.filter(Area__name = pareto).filter(Fecha__gte = YEAR_DATE).filter(Fecha__lte = monthDate)
        else:
            f412List = getF412List(F412_ALL, f412Emp, pareto, YEAR_DATE, monthDate)
            f412AntList = getF412List(f412AntALL, f412AntEmp, pareto, YEAR_DATE, monthDate)
            repList = getF412List(repALL, repListEmp, pareto, YEAR_DATE, monthDate) 
        
        if typeGraph == "lay":
            f412List = getLayList(f412List, f412Emp)
            f412AntList = getLayList(f412AntList, f412AntEmp)
            repList = getLayList(repList, repListEmp)
        
        topN = 0
        for nameInd in names:
            hoursDict = getHoursDict(f412List.filter(Defecto__name = nameInd))
            hoursDict2 = getHoursDict(f412AntList.filter(Defecto__name = nameInd))
            hoursDict3 = getHoursDict(repList.filter(Defecto__name = nameInd))
            
            hoursDict = sumDictHours(hoursDict, hoursDict2)
            hoursDict = sumDictHours(hoursDict, hoursDict3)
            
            oneByOneList, xticks = hoursToData(hoursDict, YEAR)
            oneByOne = oneByOneList[::-1][0]
            
            if len(data[topN]) != 0:
                toAdd = oneByOne - sum(data[topN])
            else:
                toAdd = oneByOne
            data[topN].append(toAdd)
            topN += 1

    toReturn = []
    xticks = []
    lenDefc = []
    for row in data:
        monthList = MONTH[:len(row)]
        rowAux = row
        while 0 in rowAux:
            index0 = rowAux.index(0)
            toRemove = monthList[index0]
            monthList.remove(toRemove)
            rowAux.remove(0)
        xticks = xticks + monthList
        lenDefc.append(len(rowAux))
        toReturn = toReturn + rowAux
    
    return toReturn, xticks, lenDefc
#    return dataToReturn, monthStart, xticks

def getLayList(listToDepurate, listToFill):
    for area in layupList:
        listToFill = listToFill | listToDepurate.filter(Area__name = area)
        
    return listToFill        

def parseData380(xticks, dict380):
    data = []
    for i in range(0,len(pareto380List)):
        data.append([])
        
        for name in xticks:    
            data[i].append(dict380[pareto380List[i]][name])
   
    return data
 
def fillData(dataToFill, xticksMat, xticksRef):
    i = 0
    dataToReturn = []
    for row in dataToFill:
        if len(xticksMat[i]) != len(xticksRef):
            j = 0
            for element in xticksRef:
                try:
                    if element != xticksMat[i][j]:
                        row.insert(j, 0)
                    else:
                        j += 1
                except:
                    row.append(0)
        dataToReturn.append(row)
        i += 1    
        
    return dataToReturn
 
def findPos(monthRefArray, month):
    pos = len(monthRefArray) -1
    try:
        while MONTH.index(monthRefArray[pos]) >= MONTH.index(month):
            pos += -1
    except:
        return 0
    return pos + 1

def checkMonths(monthRefArray, monthToCheck):
    for month in monthToCheck:
        if month in monthRefArray:
            continue
        else:
            if len(monthRefArray) -1 < MONTH.index(month) and len(monthRefArray) > 0 :
                if MONTH.index(monthRefArray[len(monthRefArray) - 1]) > MONTH.index(month):
                    monthRefArray.insert(findPos(monthRefArray, month), month)
                    continue
            monthRefArray.insert(MONTH.index(month), month)
            
def getxRef(xticks, lenMat):
    xRefMat = [[],[],[],[],[]]
    lenRef = []
    for i in range(0,len(xticks)):
        aux = xticks[i]
        for j in range(0, len(lenMat[i])):
            lenJ = lenMat[i][j]
            currentParMonth = aux[:lenJ]
            checkMonths(xRefMat[j], currentParMonth)
            aux = aux[lenJ:]    
    
    xRef = []
    for row in xRefMat:
        xRef = xRef + row
        lenRef.append(len(row))
    return xRef, lenRef

def updateParetos(request, month):
    ylabel = "Coste €"
    if month == "todos":
        init = 1
        end = 13
    else:
        init = int(month)
        end = int(month) +1
    for month in range(init, end): 
        dict380 = {}
        dict380["total"] = {}
        dict380Lay = {}
        dict380Lay["total"] = {}
        
        ylabel = "Coste €"
        monthDate = getDate(YEAR, month)
        for pareto in pareto380List:
            
            f412List = getF412List(F412_ALL, F412Empty, pareto, YEAR_DATE, monthDate)
            f412List2 = getF412List(f412AntALL, f412AntEmpty, pareto, YEAR_DATE, monthDate)
            repList = getF412List(repALL, repEmpty, pareto, YEAR_DATE, monthDate)
            
#           A380 sin lay up ni ind
            hoursDict = getHoursDict(f412List)      
            hoursDict2 = getHoursDict(f412List2) 
            hoursDict3 = getHoursDict(repList)
            
            hoursDict = sumDictHours(hoursDict, hoursDict2)
            hoursDict = sumDictHours(hoursDict, hoursDict3)


            data, xticksNames = hoursToData(hoursDict, YEAR)
            
            dict380[pareto] = hoursDict
            dict380["total"] = sumDictHours(hoursDict, dict380["total"])
            
            title = "PARETO costes de Desviaciones  generadas  sobre " + pareto + " \n"
            title += "(Coste € / (Horas de Reparación/F412) que ha generado la desviación)"
            xlabel = pareto
            name = "templates/images/pareto/" + str(month) + "/" + pareto.lower() + "Top5.png"
            data = data[::-1][:5]
            xticksNames = xticksNames[::-1][:5]
            dots = getLastYear(xticksNames, month, pareto, "")
            
#            Evolucion sin lay up ni ind           
            titleEv = title.replace("PARETO", "EVOLUCIÓN")
            nameEv = "templates/images/pareto/" + str(month) + "/" + pareto.lower() + "Ev.png"
            dataEv, xticksNamesEv, lenDefc = getDataEv(xticksNames, month, pareto, "")
            
#           TOP5 LAY-UP            
            hoursDictLay = getHoursDict(getLayList(f412List, F412Empty))      
            hoursDict2Lay = getHoursDict(getLayList(f412List2, f412AntEmpty)) 
            hoursDict3Lay = getHoursDict(getLayList(repList, repEmpty))
           
            hoursDictLay = sumDictHours(hoursDictLay, hoursDict2Lay)
            hoursDictLay = sumDictHours(hoursDictLay, hoursDict3Lay)
            
            dict380Lay[pareto] = hoursDictLay
            dict380Lay["total"] = sumDictHours(hoursDictLay, dict380Lay["total"])
            
            dataLay, xticksNamesLay = hoursToData(hoursDictLay, YEAR)
            dataLay = dataLay[::-1][:5]
            xticksNamesLay = xticksNamesLay[::-1][:5]
            titleLay = title.replace("\n", "por LAY-UP\n")
            nameLay = name.replace("Top5", "Top5lay")
            dotsLay = getLastYear(xticksNamesLay, month, pareto, "lay")

#           Evolucion LAY-UP           
            titleEvLay = titleLay.replace("PARETO", "EVOLUCIÓN")
            nameEvLay = "templates/images/pareto/" + str(month) + "/" + pareto.lower() + "EvLay.png"
            dataEvLay, xticksNamesEvLay, lenDefcLay = getDataEv(xticksNamesLay, month, pareto, "lay")
            
                    
            saveTop5(xticksNames, data, pareto, month, False)
            saveTop5(xticksNamesLay, dataLay, pareto, month, True)
        
            
            saveGraphTop5(data, title, xlabel, ylabel, xticksNames, dots, name)
            saveGraphTop5(dataLay, titleLay, xlabel, ylabel, xticksNamesLay, dotsLay, nameLay)
            
            saveGraphEv(dataEv, titleEv, ylabel, xticksNames, xticksNamesEv, nameEv, lenDefc)
            saveGraphEv(dataEvLay, titleEvLay, ylabel, xticksNamesLay, xticksNamesEvLay, nameEvLay, lenDefcLay)
            
        for area in indList:
            title = "PARETO costes de Desviaciones  generadas  por " + area + " A380 sobre pieza\n"
            title += "(Coste € / (Horas de Reparación/F412) que ha generadola desviación)"
            name = "templates/images/pareto/" + str(month) + "/" + area.lower() + "Top5.png"
            xlabel = area
                                                   
            f412List = F412_ALL.filter(Area__name = area).filter(Fecha__gte = YEAR_DATE).filter(Fecha__lte = monthDate)
            f412List2 = f412AntALL.filter(Area__name = area).filter(Fecha__gte = YEAR_DATE).filter(Fecha__lte = monthDate)
            repList = repALL.filter(Area__name = area).filter(Fecha__gte = YEAR_DATE).filter(Fecha__lte = monthDate)
            
#           ind
            hoursDict = getHoursDict(f412List)      
            hoursDict2 = getHoursDict(f412List2) 
            hoursDict3 = getHoursDict(repList)
           
            hoursDict = sumDictHours(hoursDict, hoursDict2)
            hoursDict = sumDictHours(hoursDict, hoursDict3)
            data, xticksNames = hoursToData(hoursDict, YEAR)  
            data = data[::-1][:5]
            xticksNames = xticksNames[::-1][:5]
            dots = getLastYear(xticksNames, month, area, "ind")
            
            titleEv = title.replace("PARETO", "EVOLUCIÓN")
            nameEv = "templates/images/pareto/" + str(month) + "/" + area.lower() + "Ev.png"
            dataEv, xticksNamesEv, lenDefc = getDataEv(xticksNames, month, area, "ind")
                                                
            saveGraphTop5(data, title, xlabel, ylabel, xticksNames, dots, name)
            saveGraphEv(dataEv, titleEv, ylabel, xticksNames, xticksNamesEv, nameEv, lenDefc)
            saveTop5(xticksNames, data, area, month, False)
            
            
        _ , xticks380 = hoursToData(dict380["total"], YEAR)
        xticks380 = xticks380[::-1][:5]        
        data380 = parseData380(xticks380, dict380)
        data380Copy = data380.copy()
        for row in data380Copy:
            for k in range(0, len(row)):
                row[k] = row[k] * costeHora.objects.get(year = YEAR).precio
        title = "PARETO costes de Desviaciones  generadas sobre A380 y Nº Concesiones del TOP 5 de Desviaciones\n"
        title += "(Coste € / (Horas de Reparación/F412) que ha generado la desviación)"
        xlabel = "A380"
        ylabel = "Coste"
        fileName = "templates/images/pareto/" + str(month) + "/a380Top5.png"
        
        _ , xticks380Lay = hoursToData(dict380Lay["total"], YEAR)
        xticks380Lay = xticks380Lay[::-1][:5]        
        data380Lay = parseData380(xticks380Lay, dict380Lay)
        data380LayCopy = data380Lay.copy()
        for row in data380LayCopy:
            for k in range(0, len(row)):
                row[k] = row[k] * costeHora.objects.get(year = YEAR).precio
        titleLay = title.replace("\n", " por LAY-UP\n")
        fileNameLay = fileName.replace(".png", "Lay.png")                                           
        maxXticks = []
        xticksMat = []
        dataMat = []
        lenDefcMat = []
        fileNameEv = fileName.replace("Top5", "Ev") 
        titleEv = title.replace("PARETO", "EVOLUCION")    
        
        for pareto in pareto380List:
            dataEv, xticksNamesEv, lenDefc = getDataEv(xticks380, month, pareto, "")
            xticksMat.append(xticksNamesEv)
            dataMat.append(dataEv)
            lenDefcMat.append(lenDefc)
        
        maxXticks, maxlenDefc = getxRef(xticksMat, lenDefcMat)
        dataMat = fillData(dataMat, xticksMat , maxXticks)
        
        maxXticksLay = []
        xticksMatLay = []
        dataMatLay = []
        lenDefcMatLay = []
        fileNameEvLay = fileNameLay.replace("Top5", "Ev") 
        titleEvLay = title.replace("PARETO", "EVOLUCION")      
        for pareto in pareto380List:
            dataEvLay, xticksNamesEvLay, lenDefcLay = getDataEv(xticks380Lay, month, pareto, "")
            xticksMatLay.append(xticksNamesEvLay)
            dataMatLay.append(dataEvLay)
            lenDefcMatLay.append(lenDefcLay)
        
        maxXticksLay, maxlenDefcLay = getxRef(xticksMatLay, lenDefcMatLay)
        dataMatLay = fillData(dataMatLay, xticksMatLay, maxXticksLay)
        saveGraph380(data380Copy, title, xlabel, ylabel, xticks380, dots, fileName) 
        saveGraph380(data380LayCopy, titleLay, xlabel, ylabel, xticks380Lay, dots, fileNameLay)      
        saveGraph380Ev(dataMat, titleEv, ylabel, xticks380, maxXticks, fileNameEv, maxlenDefc)    
        saveGraph380Ev(dataMatLay, titleEvLay, ylabel, xticks380Lay, maxXticksLay, fileNameEvLay, maxlenDefcLay)    
            
    return HttpResponseRedirect("/paretos")

def createParDefc(i, defcObj, month):
    paretoDef = paretoDefecto(number = i, defecto = defcObj, fechaApertura = YEAR_DATE, fechaCierre = YEAR_DATE)
    paretoDef.save()
    
    return paretoDef

def saveTop5(top5List, data, pareto, month, isLay):
    exist = True
    try:
        paretoTab = paretoTabla.objects.filter(isLay = isLay).filter(year = YEAR).filter(mes = month).get(pareto = pareto)
    except:
        paretoTab = paretoTabla(isLay = isLay, year = YEAR, mes = month, pareto = pareto)
        paretoTab.save()
        exist = False
        
    if exist:
        
        top5Aux = top5List.copy()
        for defcPar in paretoTab.topDefc.all():
            try:
                newNumber = top5Aux.index(defcPar.defecto.name)
                defcPar.number = newNumber
                defcPar.save()
                top5Aux.remove(defcPar.defecto.name)
            except ValueError:
                paretoTab.topDefc.remove(defcPar)
           
        for defcPar in top5Aux:
            if data[top5List.index(defcPar)] != 0.0:
                queryDefcPar = paretoDefecto.objects.annotate(num_parTab=Count('paretotabla')).filter(num_parTab=0).filter(defecto__name = defcPar)
                if queryDefcPar.count() != 0:
                    defcParObj = queryDefcPar[0]
                    defcParObj.number = top5List.index(defcPar)
                    defcParObj.save()
                else:
                    defcParObj = createParDefc(top5List.index(defcPar), Defecto.objects.get(name = defcPar), month)
                    defcParObj.save()
                paretoTab.topDefc.add(defcParObj)
                paretoTab.save()   
                
    else:
        i = 0
        for defcPar in top5List:
            if data[i] != 0.0: 
                print(defcPar)
                print(pareto)
                defcParObj = createParDefc(top5List.index(defcPar), Defecto.objects.get(name = defcPar), month)
                defcParObj.save()      
                paretoTab.topDefc.add(defcParObj)
                paretoTab.save()     
            i = i + 1
    
    return ""
    
def add_line(ax, xpos, ypos):
    line = plt.Line2D([xpos, xpos], [ypos + .05, ypos - 0.1],
                      transform=ax.transAxes, color='black')
    line.set_clip_on(False)
    ax.add_line(line)
    return

def saveGraphTop5(data, title, xlabel, ylabel, xticksNames, dots, fileName):
    fig=Figure(figsize=(16,10))
    ax=fig.add_subplot(111)
    
    N = len(data)   
    
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence
                                                              
#    p = ax.bar(ind, data, width, color ='b')
    p = ax.bar(ind, data, width, color = '#0085ad')
    ax.set_title(title, fontsize = 20)
            
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel, fontsize = 15)
    ax.set_xticks(ind)
    
    yDots = dots   
    
    ax.set_xticklabels(xticksNames, fontsize = 15)
    ax.plot(yDots, 'o', color="#e4002b")
    
    xDots = np.arange(len(dots))
    for i,j in zip(xDots,yDots):
        name = "%f" % j
        dec = name.find(".") + 2
        ax.text(i+0.05, j, name[:dec], va="bottom", fontsize = 15);
    
    textField = "Suma de Costes de "
    lastYearField = textField + str(LAST_YEAR)
    yearField = textField + str(YEAR)
    lastYear = mpatches.Patch(color="#e4002b", label=lastYearField)
    currentYear = mpatches.Patch(color="#0085ad", label=yearField)
    ax.legend(handles=[lastYear, currentYear], loc = "upper right")

    for i, patch in enumerate(p.get_children()):
        bl = patch.get_xy()
        x = patch.get_width()/2.0 + bl[0]
        y = patch.get_height() + bl[1]
            
        if data[i] != 0:
            name = "%f" % (data[i])
            dec = name.find(".") + 2
            ax.text(x,y, name[0:dec], ha="center", va="bottom", fontsize = 15)

    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()
 
    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)
   
    return
    
def saveGraphEv(data, title, ylabel, xticksNames, xticksNamesEv, fileName, lenDefc):    
    ly = len(data)
    if ly == 0:
        return
    scale = 1/ly
    
    fig=Figure(figsize=(16,10))
    ax=fig.add_subplot(111)
    
    N = len(data)   
    ind = np.arange(N)    # the x locations for the groups
    
    width = 0.35       # the width of the bars: can also be len(x) sequence
                                                              
    ax.bar(ind, data, width, color = '#0085ad')
    ax.set_title(title, fontsize = 20)
            
    ax.set_ylabel(ylabel)
    ax.set_xticks(ind)    
    ax.set_xticklabels(xticksNamesEv, fontsize = 15)
    
#    for pos in range(ly + 1):
#        add_line(ax, pos * scale, -.5)
    
    i = 0
    pos = 0
    if N > 16:
        ypos = -0.1
    else:
        ypos = -0.075
    
    for name in xticksNames:
        
        rpos = lenDefc[i]
        if rpos == 0:
            break
        lxpos = (pos + 0.5*rpos) * scale
        ax.text(lxpos, ypos, name, ha='center', transform=ax.transAxes, fontsize = 15)
        add_line(ax, pos * scale, -.05)
        i += 1
        pos += rpos
    
    add_line(ax, pos * scale, -.05)
    
    if N > 16:    
        for tick in ax.get_xticklabels():
            tick.set_rotation(60)    
    
    
    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()    
    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)
   
    return
    
def saveGraph380(data, title, xlabel, ylabel, xticksNames, dots, fileName):
    fig=Figure(figsize=(16, 12))
    ax=fig.add_subplot(111)
    
    N = 5
    
    ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence
    
    p = []                                                               
    p.append(ax.bar(ind, data[0], width))
    p.append(ax.bar(ind, data[1], width, bottom=data[0], color ="#84bd00"))
    p.append(ax.bar(ind, data[2], width, bottom=np.array(data[0]) + np.array(data[1]), color="#a51890"))
    p.append(ax.bar(ind, data[3], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]), color ="#fe5000"))
    p.append(ax.bar(ind, data[4], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]) + np.array(data[3]), color = "#00aec7"))
    p.append(ax.bar(ind, data[5], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]) + np.array(data[3]) + np.array(data[4]), color = "#e1e000"))
    p.append(ax.bar(ind, data[6], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]) + np.array(data[3]) + np.array(data[4]) + np.array(data[5]), color="#00205b"))
    
    ax.set_title(title, fontsize = 20)
        
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(ind)
        
    ax.set_xticklabels(xticksNames, fontsize = 15)
    
    ax.legend(p, pareto380List)
    for j in range(len(p)):
        for i, patch in enumerate(p[j].get_children()):
            bl = patch.get_xy()
            x = patch.get_width() + bl[0]
            y = 0.5*patch.get_height() + bl[1]
            
            if data[j][i] != 0:
                name = "%f" % (data[j][i])
                dec = name.find(".") + 2
                ax.text(x,y, name[0:dec], fontsize = 15)
    
#    fig.subplots_adjust(top = 0.95)
    
    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()    
    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)
    
    return

def saveGraph380Ev(data, title, ylabel, xticksNames, xticksNamesEv, fileName, lenDefc): 
    ly = len(xticksNamesEv)
    if ly == 0:
        return
    scale = 1/ly
    
    fig=Figure(figsize=(16,12))
    ax=fig.add_subplot(111)
    
    N = len(xticksNamesEv)   
    ind = np.arange(N)    # the x locations for the groups
    
    width = 0.35       # the width of the bars: can also be len(x) sequence
                                                              
    p = []                                                               
    p.append(ax.bar(ind, data[0], width))
    p.append(ax.bar(ind, data[1], width, bottom=data[0], color ="#84bd00"))
    p.append(ax.bar(ind, data[2], width, bottom=np.array(data[0]) + np.array(data[1]), color="#a51890"))
    p.append(ax.bar(ind, data[3], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]), color ="#fe5000"))
    p.append(ax.bar(ind, data[4], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]) + np.array(data[3]), color = "#00aec7"))
    p.append(ax.bar(ind, data[5], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]) + np.array(data[3]) + np.array(data[4]), color = "#e1e000"))
    p.append(ax.bar(ind, data[6], width, bottom=np.array(data[0]) + np.array(data[1]) + np.array(data[2]) + np.array(data[3]) + np.array(data[4]) + np.array(data[5]), color="#00205b"))
    ax.set_title(title, fontsize = 20)
            
    ax.set_ylabel(ylabel)
    ax.set_xticks(ind)    
    ax.set_xticklabels(xticksNamesEv, fontsize = 15)
        
    i = 0
    pos = 0
    if N > 16:
        ypos = -0.125
    else:
        ypos = -0.075
        
    for name in xticksNames:
        rpos = lenDefc[i]
        if rpos == 0:
            break
        lxpos = (pos + 0.5*rpos) * scale
        ax.text(lxpos, ypos, name, ha='center', transform=ax.transAxes, fontsize = 15)
        add_line(ax, pos * scale, -0.5)
        i += 1
        pos += rpos
    
    add_line(ax, pos * scale, -.05)
    
    if N > 16:    
        for tick in ax.get_xticklabels():
            tick.set_rotation(90)    
    
    ax.legend(p, pareto380List)
    
    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()    
    fig.savefig(graphic, format="png")
    fig.savefig(fileName, format="png")
    canvas.print_png(graphic)
   
    return

def saveTable(pareto, month, data, isLay):
    if isLay:
        toAdd = "Lay"
    else:
        toAdd = ""
    nameTable = "templates/images/pareto/" + str(month) + "/" + pareto.lower() + toAdd + "table.png"
    columns = ("Tipo de Defecto", "Acción", "PPS - código", "Fecha de\n apertura del\nPPS", "Fecha de Cierre\ndel PPS")

    fig=Figure(figsize=(16,10))
    ax=fig.add_subplot(111)
    
    colColours = []
    for n in range(0, len(columns)):
        colColours.append('black')
    
    table = ax.table(cellText=data, colLabels=columns, colColours=colColours, loc="upper center", cellLoc='center' )
    
    ax.axis("off")
    
    cellDict = table.get_celld()
    
    for cell in cellDict.values():
        cell.set_width(0.2)
        cell.set_height(0.1)

    for i in range(0, len(columns)):
        cellDict[(0,i)]._text.set_color('w')    
    
    canvas=FigureCanvas(fig)
    graphic = io.BytesIO()    
    fig.savefig(graphic, format="png")
    fig.savefig(nameTable, format="png")
    canvas.print_png(graphic)
    
    return ""

@csrf_exempt
def updateDataParTable(request, year, month, isLay, listToSearch):
    if isLay:
        layName = "Lay"
    else:
        layName = ""

    for pareto in listToSearch:   
        data = []   
        parTab = paretoTabla.objects.filter(year = year).filter(isLay = isLay).filter(mes = month).get(pareto = pareto)
        for defc in parTab.topDefc.all().order_by("number"):
            sufix = pareto + defc.defecto.name + layName
            actionName = "action" + sufix
            ppsName = "PPSCod" + sufix
            dateStart = "dateInit" + sufix
            dateEnd = "dateEnd" + sufix
            
            action = request.POST[actionName]
            ppsCod = request.POST[ppsName]
            dateStart = request.POST[dateStart]
            dateEnd = request.POST[dateEnd]
            
            if action != "<br>":
                defc.accion = action
                
            if ppsCod != "<br>":
                defc.ppsCod = ppsCod
                
            if dateStart != "<br>":
                try:
                    dateStart = parseDate(dateStart)
                    defc.fechaApertura = dateStart
                    defc.modificadaFechaAp = True
                except:
                    print("Formato fecha erroneo")
                
            if dateEnd != "<br>":
                try:
                    dateEnd = parseDate(dateEnd)
                    defc.fechaCierre = dateEnd
                    defc.modificadaFechaCie = True
                except:
                    print("Formato fecha erroneo")
            
            dateStartTab = ""
            dateEndTab = ""
            
            if defc.modificadaFechaAp:
                dateStartTab = dateToString(defc.fechaApertura)
            if defc.modificadaFechaCie:
                dateEndTab = dateToString(defc.fechaCierre)
                    
            defc.save()
            row = [defc.defecto.name, defc.accion, defc.ppsCod, dateStartTab, dateEndTab]
            data.append(row)
        
        saveTable(pareto, month, data, isLay)
    
    return ""

def drawImages(pdf, width, height, month, isLay, listToDraw):    
    xCenter = width/4 - 50
    yPos1 = height/2 - 10  
    yPos2 = 5
    widhtGraph = 2*width/3 - 90
    heightGraph = height/2 + 10   

    strRig = width - 200
    strLeft = 40
    strUp = height - 50
#    strDown = 40  
    typePareto = " A380  "    
                             
    if isLay:
        toAdd = "Lay"
        typePareto = "LAY-UP  " + typePareto
    elif listToDraw == indList:
        typePareto = "ÁREA INDUSTRIAL"
        toAdd = ""
    else:
        toAdd = ""
        
    month = int(month)
    monthData = "ENERO - " + MONTH[month - 1] + "   " + str(YEAR)
                                  
    for pareto in listToDraw:
        
        pdf.setFontSize(size = 15)
        img = "templates/images/pareto/" + str(month) + "/" + pareto.lower() + "Top5" + toAdd + ".png"
        imgEv = img.replace("Top5", "Ev")  
        table = "templates/images/pareto/" + str(month) + "/" + pareto.lower() + toAdd + "table.png"
        
        pdf.drawString(strRig, strUp, monthData)
        pdf.drawString(strLeft, strUp, typePareto)
        
        pdf.drawImage(img, xCenter, yPos1, widhtGraph, heightGraph, preserveAspectRatio=False) 
        pdf.drawImage(imgEv, xCenter, yPos2, widhtGraph, heightGraph, preserveAspectRatio=False)   
        
        pdf.showPage()
        
        pdf.setFontSize(size = 25)
        pdf.drawImage(table, -40, -40, widhtGraph*2, heightGraph*2, preserveAspectRatio=True) 
        pdf.drawString(xCenter, strUp, typePareto +  pareto)
        pdf.setFontSize(size = 15)
        pdf.drawString(strRig, strUp, monthData)
        pdf.showPage()
        
#    img = "templates/images/pareto/" + str(month) + "/a380Top5.png"
                                          
    return pdf                                        

@csrf_exempt
def saveTablePar(request):
    month = str(datetime.datetime.now().month)
                                     
    if request.method == "POST":
        year = request.POST["year"]
        month = request.POST["month"]
        updateDataParTable(request, year, month, True, pareto380List)
        updateDataParTable(request, year, month, False, pareto380List)
        updateDataParTable(request, year, month, False, indList)
    
    return HttpResponseRedirect("paretos/")
    
@csrf_exempt
def exportPDFPar(request):
    month = datetime.datetime.now().month
                                 
    if request.method == "POST":
        year = request.POST["year"]
        month = request.POST["month"]
        updateDataParTable(request, year, month, True, pareto380List)
        updateDataParTable(request, year, month, False, pareto380List)
        updateDataParTable(request, year, month, False, indList)
    
    response = HttpResponse(content_type = "application/pdf")

    buffer = io.BytesIO()
    pdf = canvasPDF.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    pdf = drawImages(pdf, width, height, month, False, pareto380List)
    pdf = drawImages(pdf, width, height, month, True, pareto380List) 
    pdf = drawImages(pdf, width, height, month, False, indList) 
    pdf.save()                                         
                                          
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    
    return response
