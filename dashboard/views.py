from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from chamados.models import Chamado
from inventario.models import Equipamento
from tarefas.models import Tarefa
from calendario.models import Evento

@login_required
def index(request):
    chamados_abertos = Chamado.objects.filter(status='aberto').count()
    chamados_criticos = Chamado.objects.filter(prioridade='critica', status__in=['aberto', 'andamento']).count()
    equipamentos_ativos = Equipamento.objects.filter(status='ativo').count()
    eventos_hoje = Evento.objects.filter(data_inicio__date=date.today()).count()

    chamados_recentes = Chamado.objects.select_related('criado_por', 'tecnico').all().order_by('-criado_em')[:10]

    tarefas_pendentes_list = Tarefa.objects.filter(status__in=['a_fazer', 'andamento']).order_by('-prazo')[:10]

    context = {
        'chamados_abertos': chamados_abertos,
        'chamados_criticos': chamados_criticos,
        'equipamentos_ativos': equipamentos_ativos,
        'eventos_hoje': eventos_hoje,
        'chamados_recentes': chamados_recentes,
        'tarefas_pendentes_list': tarefas_pendentes_list,
    }
    return render(request, 'dashboard/index.html', context)
