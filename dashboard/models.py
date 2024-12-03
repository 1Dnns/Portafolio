from django.db import models

# Create your models here.

'''  
Este código lo debes incluir dentro de los modelos 
class Meta:
    app_label = 'dashboard'
ejemplo
class Proyecto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        app_label = 'dashboard'  # Esto asegura que el modelo pertenezca a la app 'dashboard'

    def __str__(self):
        return self.nombre
'''