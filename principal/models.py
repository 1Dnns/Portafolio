from django.db import models

class Portada(models.Model):
    nombre_completo = models.CharField(max_length=100, default="Nombre por defecto")
    profesion = models.TextField(help_text="Lista tus profesiones separadas por comas", default="Profesión por defecto")  # Ej: Data Scientist, Ingeniero Físico

    def __str__(self):
        return self.nombre_completo

class AcercaDe(models.Model):
    foto = models.ImageField(upload_to='acerca_de/', blank=True) #se guardara en la ruta MEDIA_ROOT/acercaDe
    descripcion = models.TextField(blank=True, null=True)  # Descripción opcional
    fecha_nacimiento = models.DateField(default="2000-01-01")  # Fecha predeterminada
    direccion = models.CharField(max_length=255, default="Dirección no especificada")
    telefono = models.CharField(max_length=20, default="000000000")
    correo = models.EmailField(default="correo@ejemplo.com")
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    otra_red_social = models.URLField(blank=True, null=True, help_text="Opcionalmente agrega otra red social")

    cv = models.FileField(upload_to='cv/', blank=True, null=True, help_text="Sube tu CV en formato PDF")

    def __str__(self):
        return f"Acerca de {self.correo}"

class Habilidad(models.Model):
    CATEGORIAS = [
        ('lenguaje', 'Lenguaje de Programación'),
        ('tecnologia', 'Tecnología o Software'),
    ]
    nombre = models.CharField(max_length=50, default="Habilidad por defecto")
    nivel = models.PositiveIntegerField(default=50)  # Nivel en porcentaje (0-100)
    categoria = models.CharField(max_length=10, choices=CATEGORIAS, default='lenguaje')

    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()})"

class Formacion(models.Model):
    nivel = models.CharField(max_length=50, choices=[('Pregrado', 'Pregrado'), ('Certificado', 'Certificado')], default="Pregrado")
    institucion = models.CharField(max_length=200, default="Institución por defecto")
    titulo = models.CharField(max_length=200, default="Título por defecto")
    fecha_inicio = models.DateField(default="2000-01-01")
    fecha_fin = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} - {self.institucion}"

class ExperienciaLaboral(models.Model):
    cargo = models.CharField(max_length=100, default="Cargo por defecto")
    empresa = models.CharField(max_length=100, default="Empresa por defecto")
    descripcion = models.TextField(default="Descripción por defecto")
    fecha_inicio = models.DateField(default="2000-01-01")
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.cargo} en {self.empresa}"

class Proyecto(models.Model):
    CATEGORY_CHOICES = [
        ('notebooks', 'Notebooks (GitHub)'),
        ('dashboards & Apps Interactivas', 'Dashboards & Apps Interactivas'),
        ('web Development', 'Web Development'),
    ]

    title = models.CharField(max_length=100, default='Titulo por defecto')  
    description = models.TextField(default='Mensaje por defecto')          
    skills = models.CharField(max_length=255, default='Habilidades por defecto')  # Habilidades clave separadas por comas
    category = models.CharField(
        max_length=40, 
        choices=CATEGORY_CHOICES,
        default='Otros'
    ) 
    image = models.ImageField(upload_to='projects/', blank=True, null=True)  
    link = models.URLField(blank=True, null=True)                 

    def __str__(self):
        return self.title
    
    def get_skills_list(self):
        """Convierte la cadena de habilidades en una lista."""
        return self.skills.split(',')

class Contacto(models.Model):
    nombre = models.CharField(max_length=100, default="Nombre por defecto")
    email = models.EmailField(default="correo@ejemplo.com")
    mensaje = models.TextField(default="Mensaje por defecto")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje de {self.nombre}"