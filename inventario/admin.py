from django.contrib import admin
from .models import Equipamento, HistoricoEquipamento

@admin.register(Equipamento)
class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ['patrimonio', 'categoria', 'marca', 'modelo', 'setor', 'status']
    list_filter = ['categoria', 'status']
    search_fields = ['patrimonio', 'hostname', 'marca', 'modelo', 'numero_serie']

@admin.register(HistoricoEquipamento)
class HistoricoEquipamentoAdmin(admin.ModelAdmin):
    list_display = ['equipamento', 'acao', 'criado_em']
