from django import template
from f412.models import *

register = template.Library()

@register.filter
def getFirstModComm(f412):
    try:
        return modificaciones.objects.filter(f412 = f412).get(numero = 1).comentario
    except:
        return "No hay comentarios"

@register.filter
def pruebas(name):
    try:
        return Componente.objects.get(name = name).alias
    except:
        return name
    
@register.assignment_tag
def getPareto(namePareto, month, year, typePar):
    try:
        return paretoTabla.objects.filter(year = year).filter(isLay = typePar).filter(mes = month).get(pareto = namePareto)
    except:
        return ""
        
@register.filter
def orderQuery(querySet, param):
    return querySet.order_by(param)

@register.filter
def toSTR(toConvert, baseType):
    if baseType == "int":
        return str(toConvert)
    else:
        return ""
        
@register.filter
def changeDot(string):
    return string.replace(".",",")    