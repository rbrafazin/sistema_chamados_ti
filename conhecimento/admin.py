from django.contrib import admin
from .models import Categoria, Artigo

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'criado_em']

@admin.register(Artigo)
class ArtigoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'autor', 'visualizacoes', 'criado_em']
    list_filter = ['categoria']
    search_fields = ['titulo', 'conteudo']
