from django.urls import path
from . import views

urlpatterns = [
    path('', views.tarefas_kanban, name='tarefas_kanban'),
    path('nova/', views.tarefa_create, name='tarefa_create'),
    path('<int:pk>/', views.tarefa_detail, name='tarefa_detail'),
    path('<int:pk>/status/', views.tarefa_update_status, name='tarefa_update_status'),
    path('<int:pk>/excluir/', views.tarefa_delete, name='tarefa_delete'),
    path('<int:pk>/editar/', views.tarefa_edit, name='tarefa_edit'),
]
