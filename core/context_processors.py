from chamados.models import Chamado


def contadores(request):
    if request.user.is_authenticated:
        chamados_abertos = Chamado.objects.filter(status='aberto').count()
        return {'chamados_abertos_sidebar': chamados_abertos}
    return {'chamados_abertos_sidebar': 0}
