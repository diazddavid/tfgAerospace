from django import template
from f412.models import *

register = template.Library()

@register.assignment_tag
def getPareto(namePareto, month, year, typePar):
    try:
        return paretoTabla.objects.filter(year = year).filter(isLay = typePar).filter(mes = month).get(pareto = namePareto)
    except:
        return ""
    
@register.assignment_tag
def getParteroDefc(paretoDefc):
    try:
        lastParetoTabla = paretoDefc.paretoTablaList.all()[0]
        paretoTablaPrev = paretoTabla.objects.filter(year = lastParetoTabla.year).filter(isLay = lastParetoTabla.isLay).filter(mes = lastParetoTabla.mes - 1).get(pareto = lastParetoTabla.pareto)
        return paretoTablaPrev.topDefc.all().get(defecto = paretoDefc.defecto)
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

@register.filter
def getFirstModComm(f412):
    try:
        return modificaciones.objects.filter(f412 = f412).get(numero = 1).comentario
    except:
        return "No hay comentarios"

@register.assignment_tag
def getMailSection(dictEmails, sectionName):
    try:
        return dictEmails.get(sectionName)
    except:
        return sectionName

@register.assignment_tag
def getNumberPlane(component, year, month, program):
    if program == "380":
        try:
            return planesCount.objects.filter(program__name = program).filter(year = year).filter(mes = month).get(component__name = component).numPlanes
        except:
            return 0.0
    else:
        
        try:
            return planesCount.objects.filter(program__name = program).filter(year = year).get(mes = month).numPlanes
        except:
            return 0.0

@register.assignment_tag
def getNumberHours(component, year, month, program, codCaus):
    if program == "380":
        try:
            return planesCount.objects.filter(program__name = program).filter(year = year).filter(codCaus = codCaus).filter(mes = month).get(component__name = component).hours
        except:
            return 0.0
    else:
        
        try:
            return planesCount.objects.filter(program__name = program).filter(year = year).filter(codCaus = codCaus).get(mes = month).hours
        except:
            return 0.0    

#@register.filter
#def pruebas(name):
#    try:
#        return Componente.objects.get(name = name).alias
#    except:
#        return name
#    
