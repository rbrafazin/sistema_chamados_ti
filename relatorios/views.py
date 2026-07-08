from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime, timedelta
import calendar
import json
import requests
from weasyprint import HTML
from chamados.models import Chamado
from inventario.models import Equipamento
from tarefas.models import Tarefa
from .forms import MesAnoFilterForm


def _gerar_dados(mes, ano):
    hoje = datetime.now()
    mes_inicio = datetime(ano, mes, 1).date()
    _, last_day = calendar.monthrange(ano, mes)
    mes_fim = datetime(ano, mes, last_day).date()

    chamados_mes = Chamado.objects.filter(criado_em__date__gte=mes_inicio, criado_em__date__lte=mes_fim)
    total_chamados = chamados_mes.count()
    chamados_resolvidos = chamados_mes.filter(status='resolvido').count()
    taxa_resolucao = round((chamados_resolvidos / total_chamados * 100) if total_chamados > 0 else 0, 1)

    chamados_categoria = chamados_mes.values('categoria').annotate(total=Count('id'))
    top_solicitantes = chamados_mes.values('solicitante').annotate(total=Count('id')).order_by('-total')[:8]
    equipamentos_categoria = Equipamento.objects.values('categoria').annotate(total=Count('id'))

    chamados_mes_list = []
    tarefas_mes_list = []
    labels_mes_list = []

    for i in range(5, -1, -1):
        mi = (hoje.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        _, ld = calendar.monthrange(mi.year, mi.month)
        mf = mi.replace(day=ld)
        meses = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
        labels_mes_list.append(f'{meses[mi.month - 1]}/{mi.year}')
        chamados_mes_list.append(Chamado.objects.filter(criado_em__date__gte=mi, criado_em__date__lte=mf).count())
        tarefas_mes_list.append(Tarefa.objects.filter(status='concluido', atualizado_em__date__gte=mi, atualizado_em__date__lte=mf).count())

    labels_categoria_chamado = [dict(Chamado.CATEGORIA_CHOICES).get(item['categoria'], item['categoria']) for item in chamados_categoria]
    data_categoria_chamado = [item['total'] for item in chamados_categoria]

    labels_solicitantes = [item['solicitante'] for item in top_solicitantes]
    data_solicitantes = [item['total'] for item in top_solicitantes]

    labels_categoria_equip = [dict(Equipamento.CATEGORIA_CHOICES).get(item['categoria'], item['categoria']) for item in equipamentos_categoria]
    data_categoria_equip = [item['total'] for item in equipamentos_categoria]

    chamados_lista = chamados_mes.select_related('tecnico').order_by('-criado_em')

    cores = ['#0f62fe','#b85c00','#0e6027','#da1e28','#8b5cf6','#0891b2']

    return {
        'mes_ano': f'{meses[mes - 1]}/{ano}',
        'total_chamados': total_chamados,
        'chamados_resolvidos': chamados_resolvidos,
        'taxa_resolucao': taxa_resolucao,
        'labels_categoria_chamado': labels_categoria_chamado,
        'data_categoria_chamado': data_categoria_chamado,
        'labels_solicitantes': labels_solicitantes,
        'data_solicitantes': data_solicitantes,
        'labels_categoria_equip': labels_categoria_equip,
        'data_categoria_equip': data_categoria_equip,
        'labels_mes': labels_mes_list,
        'chamados_mes': chamados_mes_list,
        'tarefas_mes': tarefas_mes_list,
        'chamados_lista': chamados_lista,
        'cores': cores,
    }


def _chart_url(config):
    try:
        r = requests.post('https://quickchart.io/chart/create', json={'chart': config, 'width': 360, 'height': 220, 'format': 'png'}, timeout=10)
        if r.status_code == 200:
            return r.json().get('url', '')
    except Exception:
        pass
    return ''


@login_required
def relatorios_index(request):
    hoje = datetime.now()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    dados = _gerar_dados(mes, ano)
    filter_form = MesAnoFilterForm(initial={'mes': mes, 'ano': ano})

    dados['filter_form'] = filter_form
    return render(request, 'relatorios/index.html', dados)


@login_required
def enviar_relatorio(request):
    hoje = datetime.now()
    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    dados = _gerar_dados(mes, ano)
    cores = dados.pop('cores')

    # Gerar URLs das imagens dos gráficos via QuickChart
    chart_opts = {
        'type': 'bar', 'options': {
            'legend': {'display': False},
            'scales': {'x': {'ticks': {'maxRotation': 45}}, 'y': {'ticks': {'stepSize': 1, 'beginAtZero': True}}}
        }
    }

    dados['chart_categoria_chamado'] = _chart_url(dict(chart_opts, data={
        'labels': dados['labels_categoria_chamado'],
        'datasets': [{'data': dados['data_categoria_chamado'], 'backgroundColor': cores, 'borderRadius': 4}]
    }))
    dados['chart_solicitantes'] = _chart_url(dict(chart_opts, data={
        'labels': dados['labels_solicitantes'],
        'datasets': [{'data': dados['data_solicitantes'], 'backgroundColor': cores, 'borderRadius': 4}]
    }))
    dados['chart_categoria_equip'] = _chart_url(dict(chart_opts, data={
        'labels': dados['labels_categoria_equip'],
        'datasets': [{'data': dados['data_categoria_equip'], 'backgroundColor': cores, 'borderRadius': 4}]
    }))
    dados['chart_mensal'] = _chart_url({
        'type': 'line', 'options': {'legend': {'display': False}},
        'data': {
            'labels': dados['labels_mes'],
            'datasets': [
                {'label': 'Chamados', 'data': dados['chamados_mes'], 'borderColor': '#0f62fe', 'backgroundColor': 'rgba(15,98,254,0.08)', 'fill': True, 'pointBackgroundColor': '#0f62fe'},
                {'label': 'Tarefas', 'data': dados['tarefas_mes'], 'borderColor': '#0e6027', 'backgroundColor': 'rgba(14,96,39,0.06)', 'fill': True, 'pointBackgroundColor': '#0e6027'}
            ]
        }
    })
    dados['data_geracao'] = hoje

    html_str = render_to_string('relatorios/pdf.html', dados)
    pdf = HTML(string=html_str).write_pdf()

    email = EmailMessage(
        subject=f'[ABM TI] Relatório {dados["mes_ano"]}',
        body=f'Relatório de {dados["mes_ano"]} em anexo.\n\nTotal: {dados["total_chamados"]} chamados | {dados["taxa_resolucao"]}% resolvidos.',
        from_email=settings.EMAIL_HOST_USER,
        to=[settings.RELATORIO_EMAIL],
    )
    email.attach(f'relatorio_{ano}_{mes:02d}.pdf', pdf, 'application/pdf')
    email.send(fail_silently=False)
    messages.success(request, f'Relatório {dados["mes_ano"]} enviado com sucesso!')
    return redirect(f'{request.path_info}?mes={mes}&ano={ano}')
