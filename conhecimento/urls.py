from django.urls import path
from . import views

urlpatterns = [
    path('', views.conhecimento_list, name='conhecimento_list'),
    path('novo/', views.conhecimento_create, name='conhecimento_create'),
    path('<int:pk>/', views.conhecimento_detail, name='conhecimento_detail'),
    path('<int:pk>/editar/', views.conhecimento_edit, name='conhecimento_edit'),
    path('<int:pk>/excluir/', views.conhecimento_delete, name='conhecimento_delete'),
    path('categoria/nova/', views.categoria_create, name='categoria_create'),
    path('categoria/<int:pk>/editar/', views.categoria_edit, name='categoria_edit'),
    path('categoria/<int:pk>/excluir/', views.categoria_delete, name='categoria_delete'),
]
