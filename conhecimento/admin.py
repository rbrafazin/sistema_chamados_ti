from django.contrib import admin
from .models import Categoria, Artigo, Tag

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'criado_em']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['nome']

@admin.register(Artigo)
class ArtigoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'autor', 'visualizacoes', 'criado_em']
    list_filter = ['categoria', 'tags']
    search_fields = ['titulo', 'conteudo']
