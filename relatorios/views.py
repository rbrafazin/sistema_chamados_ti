from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import datetime, timedelta
import calendar
from chamados.models import Chamado
from inventario.models import Equipamento
from tarefas.models import Tarefa

@login_required
def relatorios_index(request):
    chamados_status = Chamado.objects.values('status').annotate(total=Count('id'))
    chamados_prioridade = Chamado.objects.values('prioridade').annotate(total=Count('id'))
    equipamentos_categoria = Equipamento.objects.values('categoria').annotate(total=Count('id'))

    chamados_mes = []
    tarefas_mes = []
    labels_mes = []

    hoje = datetime.now().date()
    for i in range(5, -1, -1):
        mes_inicio = (hoje.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
        labels_mes.append(f'{meses[mes_inicio.month - 1]}/{mes_inicio.year}')

        _, last_day = calendar.monthrange(mes_inicio.year, mes_inicio.month)
        mes_fim = mes_inicio.replace(day=last_day)
        chamados_mes.append(Chamado.objects.filter(criado_em__date__gte=mes_inicio, criado_em__date__lte=mes_fim).count())
        tarefas_mes.append(Tarefa.objects.filter(status='concluido', atualizado_em__date__gte=mes_inicio, atualizado_em__date__lte=mes_fim).count())

    labels_status = [dict(Chamado.STATUS_CHOICES).get(item['status'], item['status']) for item in chamados_status]
    data_status = [item['total'] for item in chamados_status]

    labels_prioridade = [dict(Chamado.PRIORIDADE_CHOICES).get(item['prioridade'], item['prioridade']) for item in chamados_prioridade]
    data_prioridade = [item['total'] for item in chamados_prioridade]

    labels_categoria = [dict(Equipamento.CATEGORIA_CHOICES).get(item['categoria'], item['categoria']) for item in equipamentos_categoria]
    data_categoria = [item['total'] for item in equipamentos_categoria]

    total_chamados = Chamado.objects.count()
    chamados_resolvidos = Chamado.objects.filter(status='resolvido').count()
    taxa_resolucao = round((chamados_resolvidos / total_chamados * 100) if total_chamados > 0 else 0, 1)

    context = {
        'labels_status': labels_status, 'data_status': data_status,
        'labels_prioridade': labels_prioridade, 'data_prioridade': data_prioridade,
        'labels_categoria': labels_categoria, 'data_categoria': data_categoria,
        'labels_mes': labels_mes, 'chamados_mes': chamados_mes, 'tarefas_mes': tarefas_mes,
        'total_chamados': total_chamados, 'chamados_resolvidos': chamados_resolvidos,
        'taxa_resolucao': taxa_resolucao,
    }
    return render(request, 'relatorios/index.html', context)
