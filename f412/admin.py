from django.contrib import admin
from f412.models import codCaus, Reparacion, Programa, ComponenteAPT5, avion, reasonTree, reasonTreeField, Pieza, tipoUsuario, modificaciones, Componente, myUser, PN, Area, Defecto, Designacion, Estado, SGM, F412, Seccion

# Register your models here.

admin.site.register(Programa)
admin.site.register(Componente)
admin.site.register(myUser)
admin.site.register(PN)
admin.site.register(Area)
admin.site.register(Defecto)
admin.site.register(Designacion)
admin.site.register(Estado)
admin.site.register(SGM)
admin.site.register(F412)
admin.site.register(Seccion)
admin.site.register(tipoUsuario)
admin.site.register(Pieza)
admin.site.register(reasonTreeField)
admin.site.register(modificaciones)
admin.site.register(avion)
admin.site.register(ComponenteAPT5)
admin.site.register(reasonTree)
admin.site.register(Reparacion)
admin.site.register(codCaus)