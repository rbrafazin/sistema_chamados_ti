from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Equipamento, HistoricoEquipamento
from .forms import EquipamentoForm

@login_required
def inventario_list(request):
    equipamentos = Equipamento.objects.all()
    categoria = request.GET.get('categoria')
    status = request.GET.get('status')
    busca = request.GET.get('busca')

    if categoria:
        equipamentos = equipamentos.filter(categoria=categoria)
    if status:
        equipamentos = equipamentos.filter(status=status)
    if busca:
        equipamentos = equipamentos.filter(
            Q(patrimonio__icontains=busca) | Q(hostname__icontains=busca) |
            Q(marca__icontains=busca) | Q(modelo__icontains=busca) |
            Q(localizacao__icontains=busca) | Q(numero_serie__icontains=busca)
        )

    paginator = Paginator(equipamentos, 20)
    page = request.GET.get('page')
    equipamentos_page = paginator.get_page(page)

    context = {
        'equipamentos': equipamentos_page,
        'categorias': Equipamento.CATEGORIA_CHOICES,
        'status_list': Equipamento.STATUS_CHOICES,
        'current_categoria': categoria,
        'current_status': status,
        'busca': busca,
    }
    return render(request, 'inventario/list.html', context)

@login_required
def inventario_create(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST)
        if form.is_valid():
            equipamento = form.save()
            HistoricoEquipamento.objects.create(
                equipamento=equipamento, usuario=request.user, acao='Equipamento cadastrado',
                descricao=f'Cadastro inicial do equipamento {equipamento.patrimonio}'
            )
            messages.success(request, 'Equipamento cadastrado com sucesso!')
            return redirect('inventario_list')
    else:
        form = EquipamentoForm()
    return render(request, 'inventario/form.html', {'form': form, 'action': 'Novo Equipamento'})

@login_required
def inventario_detail(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    historico = equipamento.historico.all()
    return render(request, 'inventario/detail.html', {'equipamento': equipamento, 'historico': historico})

@login_required
def inventario_edit(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, instance=equipamento)
        if form.is_valid():
            form.save()
            HistoricoEquipamento.objects.create(
                equipamento=equipamento, usuario=request.user, acao='Equipamento atualizado',
                descricao='Dados do equipamento foram alterados'
            )
            messages.success(request, 'Equipamento atualizado com sucesso!')
            return redirect('inventario_detail', pk=equipamento.pk)
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'inventario/form.html', {'form': form, 'action': 'Editar Equipamento', 'equipamento': equipamento})

@login_required
def inventario_delete(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        try:
            equipamento.delete()
            messages.success(request, 'Equipamento excluído!')
        except Exception:
            messages.error(request, 'Erro ao excluir. O registro pode estar vinculado a outros dados.')
        return redirect('inventario_list')
    return render(request, 'inventario/confirm_delete.html', {'equipamento': equipamento})
