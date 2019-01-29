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

from f412 import views, manageUsers, manageDB, paretos, modify, mensual #prueba
from f412.manageDB import updateDB

from django.views.static import serve

urlpatterns = [
    url(r'^Reparaciones', views.repRoot),
    url(r'^filtroFechaRep', views.repRoot),
    url(r'^Accidentales(.*)', views.home),

    url(r'^nuevaRep', views.serveFormRep),
    url(r'^(.+)/nuevaRep', views.newRep),

    url(r'^admin/', admin.site.urls),
    url(r'^cerrarSesion', views.logOut),
    url(r'^updateDB', updateDB),
    url(r'^cambiarCntr', manageUsers.changePassword),

    url(r'^rep/programa/seccion/(.*)', views.programSectionRep),
    url(r'^rep/programa/(.+)', views.programRep),

    url(r'^nuevoF412', views.serveFormGeneric),
    url(r'^(.+)/nuevoF412', views.newF412),
    url(r'^f412/(.*)/(.*)', views.f412Page),
    url(r'^f412edit/(.*)', views.f412Edit),
    url(r'^rep/(.*)/(.*)', views.repPage),
    url(r'^repEdit/(.*)', views.repEdit),
    url(r'^historial/(.*)', views.f412Hist),
    url(r'^reset/(.*)', views.f412Reset),
    url(r'^cambiarRT/(.*)', views.f412CambiarRT),
    url(r'^topMV/(.*)', views.topMV),
    url(r'^topLessTime', views.topLessTime),
    url(r'^exportAllMV', views.exportAllMV),

    url(r'^(.+)/(.+)/filtroFecha', views.serveTableStatus),
    url(r'^(.+)/(activos)', views.serveTableStatus),
    url(r'^(.+)/(validados)', views.serveTableStatus),
    url(r'^(.+)/(concedidos)',views.serveTableStatus),
    url(r'^(.+)/(rechazados)',views.serveTableStatus),
#    url(r'^(.+)/multipleAcept', views.multipleAcept), Valido si queremos permitir que se acepten varios a la vez

    url(r'^programa/seccion/(.*)', views.programSectionF412),
    url(r'^programa/(.+)', views.programF412),

    url(r'^grafico', views.simple),
    url(r'^updateGraph', manageDB.updateBothGraph),

    url(r'^administrador', manageUsers.adminPage),
    url(r'^rep/administrador', manageUsers.adminPageRep),
    url(r'^crearUsuario', manageUsers.newUser),
    url(r'^autenticar', manageUsers.validateUser),
    url(r'^cambiarCon', manageUsers.changePassword),
    url(r'^changePsswd/(.*)', manageUsers.changePasswordAdmin),
    url(r'^changeEmail', manageDB.changeEmail),

    url(r'^ExportarF412/(.+)/(.+)', manageDB.exportCSV),
    url(r'^ExportarF412/(.*)()', manageDB.exportCSV),
    url(r'^ExportarF412', manageDB.exportPage),

    url(r'^ExportarAvion', views.exportPlane),
    url(r'^F412Avion', views.getF412Plane),

    url(r'^paretos(.*)', views.paretos),
    url(r'^rep/paretos(.*)', views.repParetos),
    url(r'^updateParetos/(.*)/(.*)', paretos.updateParetos),
    url(r'^exportarParetos/(.*)/(.*)', views.exportParetos),
    url(r'^guardarTabla', paretos.saveTablePar),
    url(r'^exportPDFPareto', paretos.exportPDFPar),
    url(r'^(.*)/(.*)/exportPDFPareto', paretos.exportPDFParMonth), #por hacer
    url(r'^(.*)/(.*)/exportPDFTableMonth', paretos.exportPDFTableMonth), #por hacer
    url(r'^eliminados', views.serveDeletedTable),
    url(r'^f412Eliminado/(.*)', views.serveDeletedF412),

    url(r'^css/(.*.css)$', serve, {'document_root': 'templates/styles'}),
    url(r'^js/(.*.js)$', serve, {'document_root': 'templates/js'}),
    url(r'^images/(.+)', serve, {'document_root': 'templates/images'}, name = "Serve Images"),

#    url(r'^prueba', prueba.index),
    url(r'^exportF412Ant', views.exportF412Ant),

    url(r'^receiveEmail', views.receiveEmail),
    url(r'^changeEmail/(.*)', views.changeEmail),
    url(r'^exportUser', views.exportUsers),

    url(r'^rep/(380)', views.serveTableRep),
    url(r'^rep/(350)', views.serveTableRep),
    url(r'^(filtroFecha)', views.home),

    #MODIFICACIONES
    url(r'^modifyPage', modify.serveModifyPage),
    url(r'^modifyProgramPage', modify.serveModifyProgram),
    url(r'^newProgram', modify.newProgram),
    url(r'^Program/(.*)', modify.modifyProgram),

    url(r'^modifySectionPage', modify.serveModifySection),
    url(r'^newSection', modify.newSection),
    url(r'^Section/(.*)', modify.modifySection),

    url(r'^modifyComponentPage', modify.serveModifyComponent),
    url(r'^newComponent', modify.newComponent),
    url(r'^Component/(.*)', modify.modifyComponent),

    url(r'^modifyDesignationPage', modify.serveModifyDesignation),
    url(r'^newDesignation', modify.newDesignaPN),
    url(r'^Designation/(.*)', modify.modifyDesignation),

    url(r'^modifyPNPage', modify.serveModifyPN),
    url(r'^newPN', modify.newDesignaPN),
    url(r'^evolucionPN/(.*)', modify.evolvePN),
    url(r'^newEV/(.*)', modify.createEv),
    url(r'^activate/(.*)/(.*)', modify.changeName),
    url(r'^changeVisible/(.*)/(.*)', modify.changeVisiblePN),
    url(r'^PN/(.*)', modify.modifyPN),

    url(r'^modifyAreaCausPage', modify.serveModifyAreaCaus),
    url(r'^newAreaCaus', modify.newAreaCaus),
    url(r'^AreaCaus/(.*)', modify.modifyAreaCaus),

    url(r'^modifyAreaPage', modify.serveModifyArea),
    url(r'^newArea', modify.newArea),
    url(r'^Area/(.*)', modify.modifyArea),

    url(r'^modifyDefectPage', modify.serveModifyDefect),
    url(r'^newDefect', modify.newDefect),
    url(r'^Defect/(.*)', modify.modifyDefect),

    url(r'^modifyPiecePage', modify.serveModifyPiece),
    url(r'^newPiece', modify.newPiece),
    url(r'^Piece/(.*)', modify.modifyPiece),

    url(r'^modifyStatusPage', modify.serveModifyStatus),
    url(r'^newStatus', modify.newStatus),
    url(r'^Status/(.*)', modify.modifyStatus),

    url(r'^modifySGMPage', modify.serveModifySGM),
    url(r'^newSGM', modify.newSGM),
    url(r'^SGM/(.*)', modify.modifySGM),

    url(r'^modifyRTPage', modify.serveModifyRT),
    url(r'^newRT', modify.newRT),
    url(r'^RT/(.*)', modify.modifyRT),

    url(r'^modifyCodCausPage', modify.serveModifyCodCaus),
    url(r'^newCodCaus', modify.newCodCaus),
    url(r'^CodCaus/(.*)', modify.modifyCodCaus),

    url(r'^modifyCostHourPage', modify.serveModifyCostHour),
    url(r'^newCostHour', modify.newCostHour),
    url(r'^CostHour/(.*)', modify.modifyCostHour),

#    MENSUAL
    url(r'^avionesMensual/(.*)', mensual.updatePlaneNumbers),
    url(r'^changeMonthYear/(.*)', mensual.changeMonthYear),
    url(r'^changeHour/(.*)/(.*)', mensual.changeHours),
    url(r'^changeMonthHour/(.*)/(.*)', mensual.changeMonthHour),

    url(r'^updateHours', mensual.handleUpdateHours),
    url(r'^rootMensual', mensual.serveRootMensual),
    url(r'^updateFromXls', mensual.updatePlanes),

    url(r'^updateCharts/(.*)/(.*)', mensual.printAllDataMonthYear),
    url(r'^updateCharts/(.*)', mensual.printAllDataMonth),
    url(r'^updateCharts', mensual.printAllData),

    url(r'^exportPDFMens/(.*)/(.*)', mensual.exportPDFMenMonthYear),
    url(r'^exportPDFMens/(.*)', mensual.exportPDFMenMonth),
    url(r'^exportPDFMens', mensual.exportPDFMen),

    url(r'^(.*)', views.home),
]
