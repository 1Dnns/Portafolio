from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.pagina_principal, name='pagina_principal'),  # Página principal
    # Nueva ruta para descargar CV
    path('descargar-cv/', views.download_cv, name='download_cv'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

