from django.urls import path
from . import views

urlpatterns = [
    path('', views.apoio_dashboard, name='apoio_dashboard'),

    # Estoque
    path('estoque/', views.estoque_list, name='apoio_estoque_list'),
    path('estoque/novo/', views.estoque_create, name='apoio_estoque_create'),
    path('estoque/<int:pk>/', views.estoque_detail, name='apoio_estoque_detail'),
    path('estoque/<int:pk>/editar/', views.estoque_edit, name='apoio_estoque_edit'),
    path('estoque/<int:pk>/excluir/', views.estoque_delete, name='apoio_estoque_delete'),
    path('estoque/<int:pk>/movimentar/', views.estoque_movimentar, name='apoio_estoque_movimentar'),
    path('estoque/<int:pk>/fornecedores-json/', views.estoque_fornecedores_json, name='apoio_estoque_fornecedores_json'),
    path('estoque/<int:produto_pk>/vincular-fornecedor/', views.fornecedor_vincular, name='apoio_fornecedor_vincular'),

    # Fornecedores
    path('fornecedores/', views.fornecedor_list, name='apoio_fornecedor_list'),
    path('fornecedores/novo/', views.fornecedor_create, name='apoio_fornecedor_create'),
    path('fornecedores/<int:pk>/', views.fornecedor_detail, name='apoio_fornecedor_detail'),
    path('fornecedores/<int:pk>/editar/', views.fornecedor_edit, name='apoio_fornecedor_edit'),
    path('fornecedores/<int:pk>/excluir/', views.fornecedor_delete, name='apoio_fornecedor_delete'),
    path('fornecedores/novo-ajax/', views.fornecedor_create_ajax, name='apoio_fornecedor_create_ajax'),
    path('fornecedor/<int:pf_pk>/remover-vinculo/', views.fornecedor_remover, name='apoio_fornecedor_remover'),

    # Patrimônios
    path('patrimonio/', views.patrimonio_list, name='apoio_patrimonio_list'),
    path('patrimonio/novo/', views.patrimonio_create, name='apoio_patrimonio_create'),
    path('patrimonio/<int:pk>/', views.patrimonio_detail, name='apoio_patrimonio_detail'),
    path('patrimonio/<int:pk>/editar/', views.patrimonio_edit, name='apoio_patrimonio_edit'),
    path('patrimonio/<int:pk>/excluir/', views.patrimonio_delete, name='apoio_patrimonio_delete'),

    # Movimentações
    path('movimentacoes/', views.movimentacoes_list, name='apoio_movimentacoes_list'),
    path('movimentacoes/<int:pk>/estornar/', views.movimentacao_estornar, name='apoio_movimentacao_estornar'),

    # Relatórios
    path('relatorios/', views.apoio_relatorios, name='apoio_relatorios'),
    path('relatorios/exportar/', views.apoio_exportar_csv, name='apoio_exportar_csv'),
]
