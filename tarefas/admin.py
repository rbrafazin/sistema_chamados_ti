from django.contrib import admin
from .models import Tarefa

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'prioridade', 'status', 'responsavel', 'prazo', 'criado_em']
    list_filter = ['status', 'prioridade']
    search_fields = ['titulo']
