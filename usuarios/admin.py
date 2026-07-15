from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'setor', 'telefone']
    search_fields = ['usuario__username', 'usuario__first_name']
