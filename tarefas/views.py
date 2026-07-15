from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Tarefa
from .forms import TarefaForm

@login_required
def tarefas_kanban(request):
    a_fazer = Tarefa.objects.filter(status='a_fazer').select_related('criado_por', 'responsavel').order_by('-criado_em')[:50]
    andamento = Tarefa.objects.filter(status='andamento').select_related('criado_por', 'responsavel').order_by('-criado_em')[:50]
    concluido = Tarefa.objects.filter(status='concluido').select_related('criado_por', 'responsavel').order_by('-atualizado_em')[:20]
    form = TarefaForm()
    return render(request, 'tarefas/kanban.html', {
        'a_fazer': a_fazer, 'andamento': andamento, 'concluido': concluido, 'form': form,
    })

@login_required
def tarefa_detail(request, pk):
    tarefa = get_object_or_404(Tarefa.objects.select_related('responsavel', 'criado_por'), pk=pk)
    return render(request, 'tarefas/detail.html', {'tarefa': tarefa})


@login_required
def tarefa_create(request):
    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.criado_por = request.user
            tarefa.save()
            messages.success(request, 'Tarefa criada com sucesso!')
        else:
            messages.error(request, 'Erro ao criar tarefa. Verifique os campos.')
    return redirect('tarefas_kanban')

@login_required
@require_POST
def tarefa_update_status(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Tarefa.STATUS_CHOICES):
            tarefa.status = new_status
            tarefa.save()
    return redirect('tarefas_kanban')

@login_required
def tarefa_delete(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if request.method == 'POST':
        try:
            tarefa.delete()
            messages.success(request, 'Tarefa excluída!')
        except Exception:
            messages.error(request, 'Erro ao excluir a tarefa.')
    return redirect('tarefas_kanban')

@login_required
def tarefa_edit(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    if request.method == 'POST':
        form = TarefaForm(request.POST, instance=tarefa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarefa atualizada!')
            return redirect('tarefas_kanban')
    else:
        form = TarefaForm(instance=tarefa)
    return render(request, 'tarefas/edit.html', {'form': form, 'tarefa': tarefa})
