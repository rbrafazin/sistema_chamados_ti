from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendario_index, name='calendario_index'),
    path('eventos/', views.eventos_json, name='eventos_json'),
    path('evento/novo/', views.evento_create, name='evento_create'),
    path('evento/<int:pk>/editar/', views.evento_edit, name='evento_edit'),
    path('evento/<int:pk>/excluir/', views.evento_delete, name='evento_delete'),
]
