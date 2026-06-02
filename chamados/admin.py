from django.contrib import admin
from .models import Chamado, HistoricoChamado

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'solicitante', 'setor', 'prioridade', 'status', 'tecnico', 'criado_em']
    list_filter = ['status', 'prioridade', 'setor']
    search_fields = ['titulo', 'descricao', 'solicitante']
    date_hierarchy = 'criado_em'

@admin.register(HistoricoChamado)
class HistoricoChamadoAdmin(admin.ModelAdmin):
    list_display = ['chamado', 'usuario', 'acao', 'criado_em']
