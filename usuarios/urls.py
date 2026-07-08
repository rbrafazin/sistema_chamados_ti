from django.urls import path
from . import views

urlpatterns = [
    path('', views.usuarios_list, name='usuarios_list'),
    path('novo/', views.usuario_create, name='usuario_create'),
    path('<int:pk>/', views.usuario_detail, name='usuario_detail'),
    path('<int:pk>/editar/', views.usuario_edit, name='usuario_edit'),
    path('<int:pk>/excluir/', views.usuario_delete, name='usuario_delete'),
    path('perfil/', views.perfil_edit, name='perfil_edit'),
]
