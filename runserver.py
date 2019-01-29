#!/usr/bin/env python3
import os
import socket

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "peticiones.settings")

    from django.core.management import call_command
    from django.core.wsgi import get_wsgi_application

    application = get_wsgi_application()
    call_command('makemigrations')
    call_command('migrate')
    call_command('runserver', socket.gethostbyname(socket.gethostname()) + ":8080")
    
  #   call_command('runserver', socket.gethostbyname(socket.gethostname()) + ":8080")
