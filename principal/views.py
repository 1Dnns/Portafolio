from django.shortcuts import render
from .models import Portada, AcercaDe, Habilidad, Formacion, ExperienciaLaboral, Proyecto
from django.http import HttpResponseRedirect
from urllib.parse import urlparse, urlunparse


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

def download_cv(request):
    acerca_de = AcercaDe.objects.first()
    if acerca_de and acerca_de.cv:
        parsed = urlparse(acerca_de.cv.url)
        
        # Divide y reconstruye el path con fl_attachment
        path_parts = parsed.path.split('/')
        
        # Inserta 'fl_attachment' después de 'upload'
        try:
            upload_index = path_parts.index('upload')
            path_parts.insert(upload_index + 1, 'fl_attachment')
        except ValueError:
            # Fallback si la estructura cambia
            path_parts.insert(4, 'fl_attachment')
        
        # Reconstruye la URL completa
        new_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            '/'.join(path_parts),
            parsed.params,
            parsed.query,
            parsed.fragment
        ))
        
        return HttpResponseRedirect(new_url)
    return HttpResponseRedirect('/')