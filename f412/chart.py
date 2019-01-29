#from django.shortcuts import render, render_to_response
#
#from bokeh.plotting import figure, output_file, show 
#from bokeh.embed import components
#
#def index(request):
#    x= [1,3,5,7,9,11,13]
#    y= [1,2,3,4,5,6,7]
#    title = 'y = f(x)'
#
#    plot = figure(title= title , 
#        x_axis_label= 'X-Axis', 
#        y_axis_label= 'Y-Axis', 
#        plot_width =400,
#        plot_height =400)
#
#    plot.line(x, y, legend= 'f(x)', line_width = 2)
#    #Store components 
#    script, div = components(plot)
#
#    #Feed them to the Django template.
#    return render_to_response( 'bokeh/index.html',
#            {'script' : script , 'div' : div} )
## -*- coding: utf-8 -*-
#


#def simple(request):
#
#    fig=Figure()
#
#    ax=fig.add_subplot(111)
#    
#    N = 5
#    menMeans = (20, 35, 30, 35, 27)
#    womenMeans = (25, 32, 34, 20, 25)
#    ind = np.arange(N)    # the x locations for the groups
#    width = 0.35       # the width of the bars: can also be len(x) sequence
#    
#    p1 = ax.bar(ind, menMeans, width)
#    p2 = ax.bar(ind, womenMeans, width,
#                 bottom=menMeans)
#    
#    ax.set_ylabel('Scores')
#    ax.set_title('Scores by group and gender')
#    ax.set_xticks(ind, ('','G1', 'G2', 'G3', 'G4', 'G5'))
#    ax.set_xticklabels(('', 'G1', 'G2', 'G3', 'G4', 'G5'))
#    ax.legend((p1[0], p2[0]), ('Men', 'Women'))
#
#    canvas=FigureCanvas(fig)
##    response=HttpResponse(content_type='image/png')
#    graphic = io.BytesIO()    
#    canvas.print_figure(graphic)
##    fig.savefig(graphic, format="png")
#    fig.clf()
##    canvas.print_png(graphic)
#    
#    template = get_template("html/chart.html")
#    myContext = getBasicContext(request)
#    
#    myContext["chart"] = graphic.getvalue()
#    return HttpResponse(template.render(myContext))
