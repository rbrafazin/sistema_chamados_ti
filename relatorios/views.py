from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from datetime import datetime
import calendar
import csv
import logging
import requests
from weasyprint import HTML
from chamados.models import Chamado
from inventario.models import Equipamento
from tarefas.models import Tarefa
from .forms import MesAnoFilterForm


def _gerar_dados(mes, ano, setor=None):
    hoje = datetime.now()
    mes_inicio = datetime(ano, mes, 1).date()
    _, last_day = calendar.monthrange(ano, mes)
    mes_fim = datetime(ano, mes, last_day).date()

    chamados_mes = Chamado.objects.filter(criado_em__date__gte=mes_inicio, criado_em__date__lte=mes_fim)
    if setor:
        chamados_mes = chamados_mes.filter(setor=setor)
    total_chamados = chamados_mes.count()
    chamados_resolvidos = chamados_mes.filter(status='resolvido').count()
    taxa_resolucao = round((chamados_resolvidos / total_chamados * 100) if total_chamados > 0 else 0, 1)

    # Comparação com mês anterior
    prev_mes_num = mes - 1 if mes > 1 else 12
    prev_ano_num = ano - 1 if mes == 1 else ano
    prev_inicio = datetime(prev_ano_num, prev_mes_num, 1).date()
    _, prev_last_day = calendar.monthrange(prev_ano_num, prev_mes_num)
    prev_fim = datetime(prev_ano_num, prev_mes_num, prev_last_day).date()
    prev_chamados = Chamado.objects.filter(criado_em__date__gte=prev_inicio, criado_em__date__lte=prev_fim)
    prev_total = prev_chamados.count()
    prev_resolvidos = prev_chamados.filter(status='resolvido').count()
    prev_taxa = round((prev_resolvidos / prev_total * 100) if prev_total > 0 else 0, 1)

    meses_full = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    mes_anterior_nome = meses_full[prev_mes_num - 1]

    variacao_total = round(((total_chamados - prev_total) / prev_total * 100) if prev_total > 0 else 0, 1)
    variacao_resolvidos = round(((chamados_resolvidos - prev_resolvidos) / prev_resolvidos * 100) if prev_resolvidos > 0 else 0, 1)
    variacao_taxa = round(taxa_resolucao - prev_taxa, 1)

    chamados_categoria = chamados_mes.values('categoria').annotate(total=Count('id'))
    top_solicitantes = chamados_mes.values('solicitante').annotate(total=Count('id')).order_by('-total')[:8]
    equipamentos_qs = Equipamento.objects.all()
    if setor:
        equipamentos_qs = equipamentos_qs.filter(setor=setor)
    equipamentos_categoria = equipamentos_qs.values('categoria').annotate(total=Count('id'))
    equipamentos_status = equipamentos_qs.values('status').annotate(total=Count('id'))

    chamados_mes_list = []
    tarefas_mes_list = []
    labels_mes_list = []

    for i in range(5, -1, -1):
        ano_mes = hoje.year * 12 + hoje.month - 1 - i
        mi = datetime(ano_mes // 12, ano_mes % 12 + 1, 1)
        _, ld = calendar.monthrange(mi.year, mi.month)
        mf = datetime(mi.year, mi.month, ld)
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
        'mes_anterior_nome': mes_anterior_nome,
        'variacao_total': variacao_total,
        'variacao_resolvidos': variacao_resolvidos,
        'variacao_taxa': variacao_taxa,
        'prev_total': prev_total,
        'prev_resolvidos': prev_resolvidos,
        'prev_taxa': prev_taxa,
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
        'equip_ativos': sum(e['total'] for e in equipamentos_status if e['status'] == 'ativo'),
        'equip_manutencao': sum(e['total'] for e in equipamentos_status if e['status'] == 'manutencao'),
        'equip_inativo': sum(e['total'] for e in equipamentos_status if e['status'] == 'inativo'),
        'equip_descartado': sum(e['total'] for e in equipamentos_status if e['status'] == 'descartado'),
        'equip_total': equipamentos_qs.count(),
    }


def _chart_url(config):
    try:
        r = requests.post('https://quickchart.io/chart/create', json={'chart': config, 'width': 360, 'height': 220, 'format': 'png'}, timeout=10)
        if r.status_code == 200:
            return r.json().get('url', '')
    except Exception:
        logging.getLogger('chamados').exception('Erro ao gerar grafico via QuickChart')
    return ''


@login_required
def relatorios_index(request):
    hoje = datetime.now()
    try:
        mes = int(request.GET.get('mes', hoje.month))
        ano = int(request.GET.get('ano', hoje.year))
    except (ValueError, TypeError):
        mes = hoje.month
        ano = hoje.year
    setor = request.GET.get('setor', '')

    dados = _gerar_dados(mes, ano, setor or None)
    filter_form = MesAnoFilterForm(initial={'mes': mes, 'ano': ano, 'setor': setor})

    dados['filter_form'] = filter_form
    dados['current_setor'] = setor
    return render(request, 'relatorios/index.html', dados)


@login_required
@require_POST
def enviar_relatorio(request):
    hoje = datetime.now()
    try:
        mes = int(request.POST.get('mes', hoje.month))
        ano = int(request.POST.get('ano', hoje.year))
    except (ValueError, TypeError):
        mes = hoje.month
        ano = hoje.year
    setor = request.POST.get('setor', '')

    dados = _gerar_dados(mes, ano, setor or None)
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


@login_required
def exportar_csv(request):
    hoje = datetime.now()
    meses = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
             'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
    try:
        mes = int(request.GET.get('mes', hoje.month))
        ano = int(request.GET.get('ano', hoje.year))
    except (ValueError, TypeError):
        mes = hoje.month
        ano = hoje.year
    setor = request.GET.get('setor', '')

    dados = _gerar_dados(mes, ano, setor or None)
    chamados = dados['chamados_lista']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="chamados_{meses[mes-1].lower()}_{ano}.csv"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['#', 'Título', 'Solicitante', 'Setor', 'Categoria', 'Prioridade', 'Status', 'Técnico', 'Data'])
    for c in chamados:
        writer.writerow([
            c.pk, c.titulo, c.solicitante, c.get_setor_display(),
            c.get_categoria_display(), c.get_prioridade_display(),
            c.get_status_display(), c.tecnico.get_full_name() if c.tecnico else '—',
            c.criado_em.strftime('%d/%m/%Y %H:%M'),
        ])

    return response
