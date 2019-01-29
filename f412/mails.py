import win32com.client
import os
import subprocess
import pythoncom

from f412.models import *
from f412.toString import *

def sendEmail(to, subject, body):
    pythoncom.CoInitialize()
    outlook = win32com.client.Dispatch('outlook.application')    
    mail = outlook.CreateItem(0)
    mail.To = to
    mail.Subject = subject
    mail.body = body
    mail.send
    return "Enviado"

def openOutlook():
    try:
        subprocess.call(['C:\Program Files\Microsoft Office\Office15\Outlook.exe'])
        os.system("C:\Program Files\Microsoft Office\Office15\Outlook.exe");
    except:
        print("Outlook no abierto")
    return "Abierto"

def isMailValid(mail):
    if "@" in mail and ".com" in mail:
        return True
    else:
        return False
        
def getDestination(f412Id, userEmail):
    newf412 = F412.objects.get(id = f412Id)
    toReturn = ""
    nDest = 0
    if newf412.Estado.name == "Activo":
        typeME = tipoUsuario.objects.get(name = "ME")
        for user in myUser.objects.filter(typeUser = typeME).filter(seccion = newf412.seccion):
            if user.email != userEmail:
                if isMailValid(user.email):
                    nDest = 1
                    toReturn += user.email + ";"
    elif newf412.Estado.name == "Rechazado":
        print(newf412.Usuario.email)
        if isMailValid(newf412.Usuario.email):
            toReturn = newf412.Usuario.email
    return toReturn
    
def getSubject(f412Id):
    newf412 = F412.objects.get(id = f412Id)
    if newf412.Estado.name == "Activo":
        toReturn = "Adjunto el formulario de F412 Nº: "
    elif newf412.Estado.name == "Rechazado":
        toReturn = "Rechazo de F412 Nº: "
    elif newf412.Estado.name == "Concedido":
        toReturn = "Validación de F412 Nº: "
    else:
        print("Error de estado")
        toReturn = ""
    toReturn += str(newf412.myID)
    return toReturn 

def getBody(f412Id):
    toReturn = "Buenos días,\n\n"
    toReturn += "Se acaba de "
    newf412 = F412.objects.get(id = f412Id)
    if newf412.Estado.name == "Activo":
        toReturn += "Crear "
        because = ""
    elif newf412.Estado.name == "Rechazado":
        toReturn += "Rechazar "
        because = "\n\nEl motivo de rechazo es el siguiente: \n\n" + newf412.accion
    elif newf412.Estado.name == "Concedido":
        toReturn += "Validar " 
        because = ""
    else:
        print("Error de estado")
        toReturn = ""
    toReturn += "el F412 Nº"
    toReturn += str(newf412.myID)
    if newf412.programa.name == "350":
        toReturn += "\n\nPara el avión: " + str(newf412.nAV)
    toReturn += "\nCon referencia: " + newf412.Referencia
    toReturn += "\nCon descripción: " + newf412.Descripcion
    toReturn += "\nY un total de: " + newf412.horas + " h"
    if because != "":
        toReturn += because
    toReturn += "\n\nUn saludo y gracias\n"

    return toReturn 


#Funcion para enviar Correo
def sendMail(emailType, f412Id, userEmail):
    if emailType == "f412":
        to = getDestination(f412Id, userEmail)
        subject = getSubject(f412Id)
        body = getBody(f412Id)        
    elif emailType == "newUser":
        to = getDestination(f412Id, userEmail)
        subject = "Usuario creado"
        body = "Por favor, cambie su contraseña en el siguiente link.\n\n"
        body += "localhost:8080/cambiarContraseña"
    try:
        try:
            sendEmail(to, subject, body)
        except:
            openOutlook()
            sendEmail(to, subject, body)
    except:
        print("Correo no enviado")
    return ""
