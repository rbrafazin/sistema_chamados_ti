from django.urls import path
from . import views

urlpatterns = [
    path('', views.chamado_list, name='chamados_list'),
    path('novo/', views.chamado_create, name='chamados_create'),
    path('<int:pk>/', views.chamado_detail, name='chamados_detail'),
    path('<int:pk>/editar/', views.chamado_edit, name='chamados_edit'),
    path('<int:pk>/excluir/', views.chamado_delete, name='chamados_delete'),
    path('<int:pk>/status/', views.chamado_update_status, name='chamados_update_status'),
]
