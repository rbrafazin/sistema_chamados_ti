from django.shortcuts import redirect


class StaffRequiredMiddleware:
    SISTEMA_PATHS = [
        '/dashboard', '/chamados', '/inventario', '/conhecimento',
        '/tarefas', '/calendario', '/relatorios', '/usuarios',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            path = request.path
            if request.path == '/' or any(path.startswith(p) for p in self.SISTEMA_PATHS):
                if hasattr(request.user, 'perfil') and request.user.perfil.setor == 'apoio':
                    return redirect('apoio_dashboard')
                return redirect('portal_index')
        return self.get_response(request)
