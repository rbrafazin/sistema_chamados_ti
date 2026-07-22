from django.contrib import admin
from .models import Produto, Fornecedor, ProdutoFornecedor, Patrimonio, Movimentacao, HistoricoProduto, HistoricoPatrimonio


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'quantidade_estoque', 'estoque_minimo', 'valor_custo']
    list_filter = ['categoria']
    search_fields = ['nome', 'marca']


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'contato', 'telefone', 'email']


@admin.register(ProdutoFornecedor)
class ProdutoFornecedorAdmin(admin.ModelAdmin):
    list_display = ['produto', 'fornecedor', 'preco_unitario', 'quantidade']
    list_filter = ['fornecedor']
    search_fields = ['produto__nome', 'fornecedor__nome']


@admin.register(Patrimonio)
class PatrimonioAdmin(admin.ModelAdmin):
    list_display = ['numero_patrimonio', 'nome', 'categoria', 'setor', 'situacao']
    list_filter = ['categoria', 'situacao', 'setor']
    search_fields = ['numero_patrimonio', 'nome', 'marca', 'modelo']


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'tipo', 'motivo', 'quantidade', 'saldo_apos', 'fornecedor', 'nota_fiscal', 'data_hora', 'usuario']
    list_filter = ['tipo', 'motivo', 'data_hora']
    search_fields = ['produto__nome', 'observacao']


@admin.register(HistoricoProduto)
class HistoricoProdutoAdmin(admin.ModelAdmin):
    list_display = ['produto', 'acao', 'usuario', 'criado_em']
    list_filter = ['acao']
    search_fields = ['produto__nome', 'descricao']


@admin.register(HistoricoPatrimonio)
class HistoricoPatrimonioAdmin(admin.ModelAdmin):
    list_display = ['patrimonio', 'acao', 'usuario', 'criado_em']
    list_filter = ['acao']
    search_fields = ['patrimonio__nome', 'patrimonio__numero_patrimonio', 'descricao']
