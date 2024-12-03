from django.contrib import admin
from .models import Proyecto, AcercaDe, Contacto, Experiencia, Habilidad

# Registra tus modelos
admin.site.register(Proyecto)
admin.site.register(AcercaDe)
admin.site.register(Contacto)
admin.site.register(Experiencia)
admin.site.register(Habilidad)
