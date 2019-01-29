import datetime
from f412.models import *

def dateToString(date):
    try:
        return date.strftime("%Y/%m/%d")
    except:
        date = parseDate(date)
        return date.strftime("%Y/%m/%d")

def dateToComment(date):
    if date.weekday() == 0:
        date = date - datetime.timedelta(days=3)
    else:
        date = date - datetime.timedelta(days=1)
    return date.strftime("%y%m%d")
    

#FUncion por si en algun momento es necesaria depuracion
def F412ToString(f412):
    toReturn = "Programa: " + f412.Programa.name + "\n"
    toReturn += "Componente: " + f412.Componente.name + "\n"
    toReturn += "PN: " + f412.PN.name + "\n"
    toReturn += "Area: " + f412.Area.name + "\n"
    toReturn += "Defecto: " + f412.Defecto.name + "\n"
    toReturn += "Fecha: " + dateToString(f412.Fecha) + "\n"
    toReturn += "Estado: " + f412.Estado.name + "\n"
    toReturn += "SGM: " + f412.SGM.number + "\n"
    toReturn += "Horas: "+ f412.horas + "\n"
    toReturn += "Ref: " + f412.Referencia + "\n"
    toReturn += "Descripcion: " + f412.Descripcion + "\n"
    return toReturn

def parseDate(dateToParse):
    dateToParse = str(dateToParse)
    first = dateToParse.find('-')
    if first == -1:
        first = dateToParse.find('/')
    year = int(dateToParse[:first])
    dateToParse = dateToParse[first+1:]
    
    second = dateToParse.find('-')
    if second == -1:
        second = dateToParse.find('/')
    month = int(dateToParse[:second])
    
    space = dateToParse.find(" ")
    if space == -1:
        space = len(dateToParse)
    day = int(dateToParse[second+1:space])
    
    if year < 2000:
        year += 2000
    toReturn = datetime.datetime(year, month, day)
    return toReturn

def toList(df):
    prev = df.values.tolist()
    toReturn = []
    for dfList in prev:
        toReturn = toReturn + dfList
        
    return toReturn

def toFloat(toConvert):
    try:
        return float(toConvert.replace(',','.'))
    except:
        return 0.0