"""peticiones URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
# from f412 import manageDB, views
from django.contrib import admin

from f412 import views, manageUsers, manageDB
from f412.manageDB import updateDB

from django.views.static import serve

urlpatterns = [
    url(r'^Reparaciones', views.repRoot),   
    url(r'^filtroFechaRep', views.repRoot),        
    url(r'^Accidentales(.*)', views.home),
       
    url(r'^nuevaRep', views.serveFormRep),
    url(r'^(.+)/nuevaRep', views.newRep),
       
    url(r'^admin/', include(admin.site.urls)),
    url(r'^cerrarSesion', views.logOut),
    url(r'^updateDB', updateDB),
    url(r'^cambiarCntr', manageUsers.changePassword),
    
    url(r'^rep/programa/seccion/(.*)', views.programSectionRep),
    url(r'^rep/programa/(.+)', views.programRep),    

    url(r'^nuevoF412', views.serveFormGeneric),
    url(r'^(.+)/nuevoF412', views.newF412),
    url(r'^f412/(.*)/(.*)', views.f412Page),
    url(r'^rep/(.*)/(.*)', views.repPage),
    url(r'^historial/(.*)', views.f412Hist),
    url(r'^reset/(.*)', views.f412Reset),
    url(r'^cambiarRT/(.*)', views.f412CambiarRT),
       
    url(r'^(.+)/(.+)/filtroFecha', views.serveTableStatus),   
    url(r'^(.+)/(activos)', views.serveTableStatus),
    url(r'^(.+)/(validados)', views.serveTableStatus),
    url(r'^(.+)/(concedidos)',views.serveTableStatus),
    url(r'^(.+)/(rechazados)',views.serveTableStatus),
#    url(r'^(.+)/multipleAcept', views.multipleAcept), Valido si queremos permitir que se acepten varios a la vez

    url(r'^programa/seccion/(.*)', views.programSectionF412),
    url(r'^programa/(.+)', views.programF412),   
    
    url(r'^grafico', views.simple),
    
    url(r'^administrador', manageUsers.adminPage),
    url(r'^rep/administrador', manageUsers.adminPageRep),   
    url(r'^crearUsuario', manageUsers.newUser),
    url(r'^autenticar', manageUsers.validateUser),
    url(r'^cambiarCon', manageUsers.changePassword),
       
    url(r'^ExportarF412/(.+)/(.+)', manageDB.exportCSV),
    url(r'^ExportarF412/(.*)()', manageDB.exportCSV),
    url(r'^ExportarF412', manageDB.exportPage),
       
    url(r'^css/(.*.css)$', serve, {'document_root': 'templates/styles'}),
    url(r'^js/(.*.js)$', serve, {'document_root': 'templates/js'}),
    url(r'^images/(.+)', serve, {'document_root': 'templates/images'}, name = "Serve Images"),
    
    url(r'^rep/(380)', views.serveTableRep),
    url(r'^rep/(350)', views.serveTableRep),   
    url(r'^(filtroFecha)', views.home),
    url(r'^(.*)', views.home),
]
