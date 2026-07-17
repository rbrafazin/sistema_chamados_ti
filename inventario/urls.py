from django.urls import path
from . import views

urlpatterns = [
    path('', views.inventario_list, name='inventario_list'),
    path('novo/', views.inventario_create, name='inventario_create'),
    path('<int:pk>/', views.inventario_detail, name='inventario_detail'),
    path('<int:pk>/editar/', views.inventario_edit, name='inventario_edit'),
]
