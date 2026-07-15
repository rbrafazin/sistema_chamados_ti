from django.urls import path
from . import views

urlpatterns = [
    path('', views.relatorios_index, name='relatorios_index'),
    path('enviar/', views.enviar_relatorio, name='enviar_relatorio'),
    path('exportar/', views.exportar_csv, name='exportar_csv'),
]
