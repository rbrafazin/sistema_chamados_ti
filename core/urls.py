from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomLoginView

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
    path('portal/', include('portal.urls')),
    path('apoio/', include('apoio.urls')),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
