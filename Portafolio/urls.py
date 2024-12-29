from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('principal.urls')),
    path('diputados/', include('dashboard.urls')),
    path('dashboard/', include('django_plotly_dash.urls')),  # Dash URLs
]
#el primer argumento es el nombre de la url, el segundo indica los url de la app

#para acceder a los dashboard directamente sin cargarlo en un html
from django_plotly_dash.urls import urlpatterns as dash_urls

urlpatterns += dash_urls

