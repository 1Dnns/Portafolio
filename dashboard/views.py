from django.shortcuts import render
from .dash_app import app

def vista_dashboard(request):
    return render(request, 'dashboard/dashboard.html')