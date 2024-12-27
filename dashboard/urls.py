from django.urls import path
from .views import vista_dashboard

urlpatterns = [
    path('', vista_dashboard, name='vista_dashboard'),
]