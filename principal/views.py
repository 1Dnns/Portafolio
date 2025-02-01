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

    # Filtrar proyectos por categoría
    dashboards_apps = proyectos.filter(category='dashboards & Apps Interactivas')
    notebooks = proyectos.filter(category='notebooks')
    web_dev = proyectos.filter(category='web Development')

    context = {
        'portada': portada,
        'acerca_de': acerca_de,
        'habilidades': habilidades,
        'formacion': formacion,
        'experiencias': experiencias,
        'proyectos': proyectos,
        'dashboards_apps': dashboards_apps,
        'notebooks': notebooks,
        'web_dev': web_dev
    }
    return render(request, 'principal/pagina_principal.html', context)
