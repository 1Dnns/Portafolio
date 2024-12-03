from django.db import models

class AcercaDe(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    foto = models.ImageField(upload_to='acerca_de/', blank=True)

    #define cómo se representa un objeto en forma de cadena.
    def __str__(self):
        #hace que los objetos de esta clase se muestren como su atributo nombre.
        return self.nombre
    
class Habilidad(models.Model):
    CATEGORIAS = [
        ('lenguaje', 'Lenguaje de Programación'),
        ('tecnologia', 'Tecnología o Software'),
    ]
    nombre = models.CharField(max_length=50)
    nivel = models.PositiveIntegerField()  # Nivel en porcentaje (0-100)
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"
    
class Experiencia(models.Model):
    cargo = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.cargo} en {self.empresa}"
    
class Proyecto(models.Model):
    CATEGORIAS = [
        ('dashboard', 'Proyectos Interactivos'),
        ('notebook', 'Notebooks en GitHub'),
    ]
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)
    enlace = models.URLField()
    imagen = models.ImageField(upload_to='proyectos/', blank=True)

    def __str__(self):
        return self.titulo
    
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.nombre}"