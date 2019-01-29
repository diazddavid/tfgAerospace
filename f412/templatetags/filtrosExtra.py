from django import template
from f412.models import modificaciones

register = template.Library()

@register.filter
def getFirstModComm(f412):
    try:
        return modificaciones.objects.filter(f412 = f412).get(numero = 1).comentarios
    except:
        return "No hay comentarios"
