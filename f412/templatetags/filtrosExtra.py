from django import template
from f412.models import *

register = template.Library()

@register.simple_tag
def getPareto(namePareto, month, year, typePar):
    try:
        return paretoTabla.objects.filter(year = year).filter(isLay = typePar).filter(mes = month).get(pareto = namePareto)
    except:
        return ""

@register.simple_tag
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
def getType(string):
    return type(string)

@register.filter
def getFirstModComm(f412):
    try:
        return modificaciones.objects.filter(f412 = f412).get(numero = 1).comentario
    except:
        return "No hay comentarios"

@register.simple_tag
def getMailSection(dictEmails, sectionName):
    try:
        return dictEmails.get(sectionName)
    except:
        return sectionName

@register.simple_tag
def getPNEvList(f412):
    try:
        return PNEvol.objects.filter(designation = f412.Designacion).filter(shouldShow = True)
    except:
        designaName = f412.programa.name + f412.Componente.name
        return PNEvol.objects.filter(designation__name = designaName).filter(shouldShow = True)

@register.simple_tag
def getNumberPlane(component, year, month, program, is380Tot):
    if program == "380":
        if is380Tot:
#            try:
            if True:
                auxList = planesCount.objects.filter(program__name = program)
                auxList = auxList.filter(year = year)
                auxList = auxList.filter(is380Tot = is380Tot)
                return round(auxList.get(mes = month).numPlanes, 3)
#            except:
#                return 0.0
        else:
            try:
    #        if True:
                auxList = planesCount.objects.filter(program__name = program)
                auxList = auxList.filter(year = year).filter(mes = month)
                return round(auxList.get(component__name = component).numPlanes, 3)
            except:
                return 0.0
    else:

        try:
#        if True:
            auxList = planesCount.objects.filter(program__name = program)
            return round(auxList.filter(year = year).get(mes = month).numPlanes, 3)
        except:
            return 0.0

@register.simple_tag
def getNumberHours(componentName, year, month, program, codCausName):
    if program == "380":
        try:
#        if True:
            auxList = oldHour.objects.filter(program__name = program).filter(year = year).filter(codCaus__name = codCausName).filter(month = month)
            return round(auxList.get(component__name = componentName).hours, 3)
        except:
            return 0.0
    else:
#
        try:
#        if True:
            return round(oldHour.objects.filter(program__name = program).filter(year = year).filter(codCaus__name = codCausName).get(month = month).hours, 3)
        except:
            return 0.0

#@register.filter
#def pruebas(name):
#    try:
#        return Componente.objects.get(name = name).alias
#    except:
#        return name
#
