from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_index, name='portal_index'),
    path('stats/', views.portal_stats, name='portal_stats'),
    path('<int:pk>/', views.portal_detail, name='portal_detail'),
]
