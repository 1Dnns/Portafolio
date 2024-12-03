from django.shortcuts import render
from .models import Portada, AcercaDe, Habilidad, Formacion, ExperienciaLaboral, Proyecto


def pagina_principal(request):
    # Obtenemos la información necesaria para la página principal
    portada = Portada.objects.first()
    acerca_de = AcercaDe.objects.first()
    habilidades = Habilidad.objects.all()
    formacion = Formacion.objects.all()
    experiencias = ExperienciaLaboral.objects.all()
    proyectos = Proyecto.objects.all()

    context = {
        'portada': portada,
        'acerca_de': acerca_de,
        'habilidades': habilidades,
        'formacion': formacion,
        'experiencias': experiencias,
        'proyectos': proyectos,
    }
    return render(request, 'principal/pagina_principal.html', context)
