from django.urls import path
from . import views

urlpatterns = [
    path('', views.relatorios_index, name='relatorios_index'),
]
