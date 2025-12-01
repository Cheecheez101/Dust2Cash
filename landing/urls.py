"""
URL configuration for the landing app.

This module defines URL patterns for the landing page application.
"""

from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.index, name='index'),
]
