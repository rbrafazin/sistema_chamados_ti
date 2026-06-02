from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('chamados/', include('chamados.urls')),
    path('inventario/', include('inventario.urls')),
    path('conhecimento/', include('conhecimento.urls')),
    path('tarefas/', include('tarefas.urls')),
    path('calendario/', include('calendario.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
