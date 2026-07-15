from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from core.utils import usuarios_por_setor_json
from .models import Chamado, HistoricoChamado
from .forms import ChamadoForm, ChamadoFilterForm

@login_required
def chamado_list(request):
    chamados = Chamado.objects.select_related('tecnico', 'criado_por').all()
    filter_form = ChamadoFilterForm(request.GET)

    if filter_form.is_valid():
        data = filter_form.cleaned_data
        if data.get('status'):
            chamados = chamados.filter(status=data['status'])
        if data.get('prioridade'):
            chamados = chamados.filter(prioridade=data['prioridade'])
        if data.get('categoria'):
            chamados = chamados.filter(categoria=data['categoria'])
        if data.get('busca'):
            q = data['busca']
            chamados = chamados.filter(
                Q(titulo__icontains=q) | Q(descricao__icontains=q) | Q(solicitante__icontains=q)
            )

    paginator = Paginator(chamados, 20)
    page = request.GET.get('page')
    chamados_page = paginator.get_page(page)

    return render(request, 'chamados/list.html', {
        'chamados': chamados_page,
        'filter_form': filter_form,
    })

@login_required
def chamado_create(request):
    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.criado_por = request.user
            chamado.save()
            HistoricoChamado.objects.create(
                chamado=chamado, usuario=request.user,
                acao='Chamado criado', descricao='Chamado registrado no sistema'
            )
            messages.success(request, 'Chamado criado com sucesso!')
            return redirect('chamados_list')
    else:
        form = ChamadoForm()
    return render(request, 'chamados/form.html', {'form': form, 'action': 'Novo Chamado', 'usuarios_json': usuarios_por_setor_json()})

@login_required
def chamado_detail(request, pk):
    chamado = get_object_or_404(Chamado.objects.select_related('tecnico', 'criado_por'), pk=pk)
    historico = chamado.historico.select_related('usuario').all()
    return render(request, 'chamados/detail.html', {'chamado': chamado, 'historico': historico})

@login_required
def chamado_edit(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    if chamado.status == 'resolvido':
        messages.error(request, 'Chamado finalizado não pode ser alterado.')
        return redirect('chamados_detail', pk=chamado.pk)
    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES, instance=chamado)
        if form.is_valid():
            old_display = chamado.get_status_display()
            form.save()
            if old_display != chamado.get_status_display():
                HistoricoChamado.objects.create(
                    chamado=chamado, usuario=request.user,
                    acao='Status alterado',
                    descricao=f'Status alterado de "{old_display}" para "{chamado.get_status_display()}"'
                )
            messages.success(request, 'Chamado atualizado com sucesso!')
            return redirect('chamados_detail', pk=chamado.pk)
    else:
        form = ChamadoForm(instance=chamado)
    return render(request, 'chamados/form.html', {'form': form, 'action': 'Editar Chamado', 'chamado': chamado})

@login_required
@require_POST
def chamado_update_status(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk)
    if chamado.status == 'resolvido':
        messages.error(request, 'Chamado finalizado não pode ter o status alterado.')
        return redirect('chamados_detail', pk=chamado.pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Chamado.STATUS_CHOICES):
            old_status = chamado.get_status_display()
            chamado.status = new_status
            chamado.save()
            HistoricoChamado.objects.create(
                chamado=chamado, usuario=request.user,
                acao='Status alterado',
                descricao=f'Status alterado de "{old_status}" para "{chamado.get_status_display()}"'
            )
            messages.success(request, 'Status atualizado!')
    return redirect('chamados_detail', pk=chamado.pk)
