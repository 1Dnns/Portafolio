"""
ASGI config for Portafolio project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

#configuracion adicional para utilizzr dash

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from django_plotly_dash.routing import application as plotly_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Portafolio.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                # Añade las rutas necesarias aquí
                path("django_plotly_dash/", plotly_application),
            ]
        )
    ),
})

