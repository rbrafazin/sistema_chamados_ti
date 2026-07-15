from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from core.utils import usuarios_por_setor_json
from .models import Equipamento, HistoricoEquipamento
from .forms import EquipamentoForm

@login_required
def inventario_list(request):
    equipamentos = Equipamento.objects.all()
    categoria = request.GET.get('categoria')
    setor = request.GET.get('setor')
    status = request.GET.get('status')
    busca = request.GET.get('busca')

    if categoria:
        equipamentos = equipamentos.filter(categoria=categoria)
    if setor:
        equipamentos = equipamentos.filter(setor=setor)
    if status:
        equipamentos = equipamentos.filter(status=status)
    if busca:
        equipamentos = equipamentos.filter(
            Q(patrimonio__icontains=busca) | Q(hostname__icontains=busca) |
            Q(marca__icontains=busca) | Q(modelo__icontains=busca) |
            Q(setor__icontains=busca) | Q(numero_serie__icontains=busca)
        )

    paginator = Paginator(equipamentos, 20)
    page = request.GET.get('page')
    equipamentos_page = paginator.get_page(page)

    context = {
        'equipamentos': equipamentos_page,
        'categorias': Equipamento.CATEGORIA_CHOICES,
        'status_list': Equipamento.STATUS_CHOICES,
        'setores': Equipamento.SETOR_CHOICES,
        'current_categoria': categoria,
        'current_setor': setor,
        'current_status': status,
        'busca': busca,
    }
    return render(request, 'inventario/list.html', context)

@login_required
def inventario_create(request):
    if request.method == 'POST':
        form = EquipamentoForm(request.POST, request.FILES)
        form.fields['responsavel'].queryset = User.objects.all()
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
    return render(request, 'inventario/form.html', {
        'form': form, 'action': 'Novo Equipamento',
        'usuarios_json': usuarios_por_setor_json(),
    })

@login_required
def inventario_detail(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    historico = equipamento.historico.all()
    return render(request, 'inventario/detail.html', {'equipamento': equipamento, 'historico': historico})

@login_required
def inventario_edit(request, pk):
    equipamento = get_object_or_404(Equipamento, pk=pk)
    if request.method == 'POST':
        old = {
            'patrimonio': equipamento.patrimonio,
            'hostname': equipamento.hostname,
            'categoria': equipamento.get_categoria_display(),
            'marca': equipamento.marca,
            'modelo': equipamento.modelo,
            'numero_serie': equipamento.numero_serie,
            'processador': equipamento.processador,
            'memoria_ram': equipamento.memoria_ram,
            'armazenamento': equipamento.armazenamento,
            'sistema_operacional': equipamento.sistema_operacional,
            'ip': str(equipamento.ip or ''),
            'mac_address': equipamento.mac_address,
            'setor': equipamento.get_setor_display(),
            'responsavel': equipamento.responsavel.get_full_name() if equipamento.responsavel else '',
            'status': equipamento.get_status_display(),
            'observacoes': equipamento.observacoes,
        }
        form = EquipamentoForm(request.POST, request.FILES, instance=equipamento)
        form.fields['responsavel'].queryset = User.objects.all()
        if form.is_valid():
            form.save()
            mudancas = []
            campos = [
                ('patrimonio', 'Patrimônio'), ('hostname', 'Hostname'), ('categoria', 'Categoria'),
                ('marca', 'Marca'), ('modelo', 'Modelo'), ('numero_serie', 'Nº Série'),
                ('processador', 'Processador'), ('memoria_ram', 'Memória RAM'), ('armazenamento', 'Armazenamento'),
                ('sistema_operacional', 'S.O.'), ('ip', 'IP'), ('mac_address', 'MAC Address'),
                ('setor', 'Setor'), ('responsavel', 'Responsável'), ('status', 'Status'), ('observacoes', 'Observações'),
            ]
            for campo, label in campos:
                if campo in ('status', 'categoria', 'setor'):
                    novo = getattr(equipamento, f'get_{campo}_display')()
                elif campo == 'responsavel':
                    novo = equipamento.responsavel.get_full_name() if equipamento.responsavel else ''
                elif campo == 'ip':
                    novo = str(getattr(equipamento, campo) or '')
                else:
                    novo = getattr(equipamento, campo) or ''
                if old[campo] != novo:
                    mudancas.append(f'{label} alterado de "{old[campo] or "—"}" para "{novo or "—"}"')
            descricao = '. '.join(mudancas) if mudancas else 'Dados do equipamento foram alterados'
            HistoricoEquipamento.objects.create(
                equipamento=equipamento, usuario=request.user, acao='Equipamento atualizado',
                descricao=descricao
            )
            messages.success(request, 'Equipamento atualizado com sucesso!')
            return redirect('inventario_detail', pk=equipamento.pk)
    else:
        form = EquipamentoForm(instance=equipamento)
    return render(request, 'inventario/form.html', {
        'form': form, 'action': 'Editar Equipamento', 'equipamento': equipamento,
        'usuarios_json': usuarios_por_setor_json(),
    })

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
