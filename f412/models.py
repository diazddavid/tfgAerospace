from django.db import models
import django.contrib.auth.models as modelsAuth

class Programa(models.Model):
    name = models.CharField(max_length = 128)

class costeHora(models.Model):
    year = models.IntegerField(default = 1)
    precio = models.FloatField(default = 1.0)
    
class Seccion(models.Model):
    name = models.CharField(max_length = 128)
    programa = models.ForeignKey(Programa, default = 1)

class Componente(models.Model):
    name = models.CharField(max_length = 128)
    alias = models.CharField(max_length = 128, default = "")
    programa = models.ForeignKey(Programa, default = 1)

class Designacion(models.Model):
    name = models.CharField(max_length = 128)
    alias = models.CharField(max_length = 128, default = "")
    Componente = models.ForeignKey(Componente, default = 1)

class PN(models.Model):
    name = models.CharField(max_length = 128)
    programa = models.ForeignKey(Programa, default = 1)
    Designacion = models.OneToOneField(Designacion, unique=True)

class ComponenteAPT5(models.Model):
    name = models.CharField(max_length = 128, default = "")
    componente = models.ForeignKey(Componente, default = 1)
    pieza = models.CharField(max_length = 128, default = "")
    parNumber = models.ManyToManyField(PN, default = 1)

class Area(models.Model):
    name = models.CharField(max_length = 128)
    seccion = models.ManyToManyField(Seccion, default = 1)

class Defecto(models.Model):
    name = models.CharField(max_length = 128)
    alias = models.CharField(max_length = 128, default = "")
    seccion = models.ManyToManyField(Seccion, default = 1)

class Estado(models.Model):
    name = models.CharField(max_length = 128)
    color = models.CharField(max_length = 128, default = 1)

class Pieza(models.Model):
    name = models.CharField(max_length = 128)

class tipoUsuario(models.Model):
    name = models.CharField(max_length = 128)

class myUser(models.Model):
    name = models.CharField(max_length = 256, default = 1)
    email = models.CharField(max_length = 256)
    programa = models.ManyToManyField(Programa) #Many to many para poder tener un admin con acceso directo a todoS
    user = models.OneToOneField(modelsAuth.User)
    typeUser = models.ForeignKey(tipoUsuario, default = 1)
    passwd = models.CharField(max_length = 128)
    admin = models.BooleanField(default = False)
    NA = models.CharField(max_length = 64, default = "")
    nombreCompleto = models.CharField(max_length = 128, default = "")
    seccion = models.ManyToManyField(Seccion, default = 1)
    
class SGM(models.Model):
    number = models.CharField(max_length = 128)
    name = models.CharField(max_length = 128)
    seccion = models.ManyToManyField(Seccion, default = 1)
    user = models.ManyToManyField(myUser, default = 1)
    
    def getUser(userToSearch):
        return SGM.objects.filter(user = userToSearch)

class reasonTreeField(models.Model):
    nivel = models.IntegerField(default = 1)
    nombre = models.CharField(max_length = 100, default = "")
    codigo = models.CharField(max_length = 3, default = "")
    superior = models.ForeignKey("self", default = 1)
    shortName = models.CharField(max_length = 7, default = "")
    
class reasonTree(models.Model):
    nivel1 = models.ForeignKey(reasonTreeField, related_name = 'lvl1' , default=1)
    nivel2 = models.ForeignKey(reasonTreeField, related_name = 'lvl2' , default=1)
    nivel3 = models.ForeignKey(reasonTreeField, related_name = 'lvl3' , default=1)
    shortName = models.CharField(max_length = 13, default = "")
    program = models.ForeignKey(Programa, default = 14)
    
class codCaus(models.Model):
    name = models.CharField(max_length = 64)


class Reparacion(models.Model):
    programa = models.ForeignKey(Programa, default = 1)
    seccion = models.ForeignKey(Seccion, default = 1)
    Componente = models.ForeignKey(Componente, default = 1)
    PN = models.ForeignKey(PN, default = 1)
    Area = models.ForeignKey(Area, default = 1)
    Defecto = models.ForeignKey(Defecto, default = 1) #EN EL CASO DE LOS FORMULARIOS PARA 350 SERAN DESVIACIONES
    Fecha = models.DateField()
    Designacion = models.ForeignKey(Designacion, default = 1)
    reasonTree = models.ForeignKey(reasonTree, default = 1)
    Usuario = models.ForeignKey(myUser, default = 1)
    LastChangeUser = models.ForeignKey(myUser, related_name='%(class)s_requests_created', default = 1)
    SGM = models.ForeignKey(SGM, default = 1)
    Pieza = models.ForeignKey(Pieza, default = 1)
    Referencia = models.CharField(max_length = 128, default = "")
    hnc = models.CharField(max_length = 128, default = "")
    
    horas = models.CharField(max_length = 64, default = "")

    nOp = models.CharField(max_length = 64, default = "")
    horasLeadTime = models.CharField(max_length = 64, default = "")
    
    Descripcion = models.CharField(max_length = 1024, default = "")
    
    nAV = models.IntegerField(default = 1)
    
    codigoCausa = models.ForeignKey(codCaus, default = 1)

    myID = models.IntegerField(default = 1)
    

class F412(models.Model):
    programa = models.ForeignKey(Programa, default = 1)
    seccion = models.ForeignKey(Seccion, default = 1)
    Componente = models.ForeignKey(Componente, default = 1)
    PN = models.ForeignKey(PN, default = 1)
    Area = models.ForeignKey(Area, default = 1)
    Defecto = models.ForeignKey(Defecto, default = 1) #EN EL CASO DE LOS FORMULARIOS PARA 350 SERAN DESVIACIONES
    Fecha = models.DateField()
    Designacion = models.ForeignKey(Designacion, default = 1)
    Estado = models.ForeignKey(Estado, default = 1)
    Usuario = models.ForeignKey(myUser, default = 1)
    LastChangeUser = models.ForeignKey(myUser, related_name='%(class)s_requests_created', default = 1)
    SGM = models.ForeignKey(SGM, default = 1)
    Pieza = models.ForeignKey(Pieza, default = 1)
    Referencia = models.CharField(max_length = 128, default = "")
    
#    Horas son Horas por Operario, de LT
    horas = models.CharField(max_length = 64, default = "")
#    Horas antiguas por Operario, de LT
    horasAntiguas = models.CharField(max_length = 64, default = "", null = True)
    nOp = models.CharField(max_length = 64, default = "", null = True)
#    Las que hay que pagar
    horasRecurrentes = models.CharField(max_length = 64, default = "", null = True)
    horasAntRec = models.CharField(max_length = 64, default = "", null = True)
    
    Descripcion = models.CharField(max_length = 1024, default = "")
    accion = models.CharField(max_length = 512, default = "", null = True)
    
    nAV = models.IntegerField(default = 1, null = True)
    
    descripcionAcortada = models.CharField(max_length = 40, default = "", null = True)
    reasonTree = models.ForeignKey(reasonTree, default = 1, null = True)
    rtMod = models.BooleanField(default = False)
    operacion = models.CharField(max_length = 40, default = 1, null = True)
    codigoCausa = models.ForeignKey(codCaus, default = 1, null = True)

    myID = models.IntegerField(default = 1)
    
class avion(models.Model):
    numero = models.IntegerField(default = 1)
    hRecALB = models.CharField(default = "", max_length = 200)
    hRecV10 = models.CharField(default = "", max_length = 200)
    hRecRL8 = models.CharField(default = "", max_length = 200)
    hRecM60 = models.CharField(default = "", max_length = 200)
    hLTALB = models.CharField(default = "", max_length = 200)
    hLTV10 = models.CharField(default = "", max_length = 200)
    hLTRL8 = models.CharField(default = "", max_length = 200)
    hLTM60 = models.CharField(default = "", max_length = 200)
    v1000 = models.BooleanField(default = False)
    f412List = models.ManyToManyField(F412, default = 1)
    repList = models.ManyToManyField(Reparacion, default = 1)
    
class modificaciones(models.Model):
    numero = models.IntegerField(default = 1)
    usuario = models.ForeignKey(myUser, default = 1)
    fecha = models.DateField()
    f412 = models.ForeignKey(F412, default = 1)
    estadoViejo = models.ForeignKey(Estado, related_name = 'estadoViejo', default = 1)
    estadoNuevo = models.ForeignKey(Estado, related_name = 'estadoNuevo', default = 1)
    comentarios = models.CharField(max_length = 256, default = "")
    
class f412Ant(models.Model):
    Componente = models.ForeignKey(Componente, default = 1)
    Defecto = models.ForeignKey(Defecto, default = 1)
    Area = models.ForeignKey(Area, default = 1)
    Fecha = models.DateField()
    horas = models.CharField(max_length = 128, default = "")
    myID = models.IntegerField(default = 1)    
    
class paretoDefecto(models.Model):
    defecto = models.ForeignKey(Defecto, default = 1)
    accion = models.CharField(max_length = 1024, default = "")
    ppsCod = models.CharField(max_length = 256, default = "")
    fechaApertura = models.DateField(null = True)
    fechaCierre = models.DateField(null = True)
    area = models.CharField(max_length = 256, default = "")
    ahorro = models.CharField(max_length = 256, default = "")
    isPPS = models.BooleanField(default = False)
    modificadaFechaAp = models.BooleanField(default = False)
    modificadaFechaCie = models.BooleanField(default = False)
    number = models.IntegerField(default = 1)
    
class paretoTabla(models.Model):
    isLay = models.BooleanField(default = False)
#    topDefc = models.ManyToManyField(paretoDefecto, related_name='topList', through='OrderPareto')
    topDefc = models.ManyToManyField(paretoDefecto)
    year = models.IntegerField(default = 2018)
    mes = models.IntegerField(default = 1)
    pareto = models.CharField(default = "", max_length = 128)
    
#class OrderPareto(models.Model):
#    number = models.IntegerField(default = 1)
#    parDefecto = models.ForeignKey(paretoDefecto, related_name = 'pareto1', default = 1)
#    tabla = models.ForeignKey(paretoTabla, default = 1)