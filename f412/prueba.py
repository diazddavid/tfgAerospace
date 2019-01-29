from django.shortcuts import render, render_to_response

from bokeh.plotting import figure, output_file, show 
from bokeh.embed import components

from django.template.loader import get_template
from django.template import Context

from django.http import HttpResponse

from f412.models import Reparacion, codCaus, Programa, ComponenteAPT5, avion, reasonTree, reasonTreeField, Pieza, tipoUsuario, modificaciones, Componente, myUser, PN, Area, Defecto, Designacion, Estado, SGM, F412, Seccion


def getContext(request, mode):
    myContext = Context({'user': request.user})
    myContext["mode"] = mode
    myContext['myPath'] = request.path
    myContext["codCausList"] = codCaus.objects.all()
    try:
        myContext['myUser'] = myUser.objects.get(user = request.user)
    except:
        print("Usuario No Encontrado")
    return myContext


def index(request):
    x= [1,3,5,7,9,11,13]
    y= [1,2,3,4,5,6,7]
    title = 'y = f(x)'

    plot = figure(title= title , 
        x_axis_label= 'X-Axis', 
        y_axis_label= 'Y-Axis', 
        plot_width =400,
        plot_height =400)

    plot.line(x, y, legend= 'f(x)', line_width = 2)
    #Store components 
    script, div = components(plot)
    
    myContext = getContext(request, "Reparaciones")
    template = get_template('html/pruebas.html')
    myContext['script'] = script
    myContext['div'] = div
    #Feed them to the Django template.
    return HttpResponse(template.render(myContext))
