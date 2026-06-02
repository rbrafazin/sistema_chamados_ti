from django.contrib import admin
from .models import Evento

@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'data_inicio', 'data_fim', 'criado_por']
    list_filter = ['tipo']
    search_fields = ['titulo']
