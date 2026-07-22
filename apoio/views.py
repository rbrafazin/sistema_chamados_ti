from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum, F, Q, Value, DecimalField, IntegerField, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse
from datetime import datetime, date
import calendar
import csv
import json
from .models import Produto, Fornecedor, Patrimonio, Movimentacao, ProdutoFornecedor, HistoricoProduto, HistoricoPatrimonio
from .forms import ProdutoForm, FornecedorForm, PatrimonioForm


MESES_NOMES = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
]


@login_required
def apoio_dashboard(request):
    total_produtos = Produto.objects.count()
    total_itens = Produto.objects.aggregate(t=Coalesce(Sum('quantidade_estoque'), 0, output_field=IntegerField()))['t']
    estoque_baixo = Produto.objects.filter(quantidade_estoque__gt=0, quantidade_estoque__lte=F('estoque_minimo')).count()
    sem_estoque = Produto.objects.filter(quantidade_estoque=0).count()
    valor_total = Produto.objects.aggregate(
        t=Coalesce(Sum(F('quantidade_estoque') * F('valor_custo'), output_field=DecimalField()), 0, output_field=DecimalField())
    )['t']

    alertas = list(Produto.objects.filter(quantidade_estoque__lte=F('estoque_minimo')).order_by('quantidade_estoque')[:10])
    alertas_sem = [p for p in alertas if p.quantidade_estoque == 0]
    alertas_baixo = [p for p in alertas if p.quantidade_estoque > 0]
    movimentacoes = Movimentacao.objects.select_related('produto', 'usuario', 'fornecedor').order_by('-data_hora')[:10]

    # Patrimônio
    total_patrimonios = Patrimonio.objects.count()
    valor_patrimonio = Patrimonio.objects.aggregate(
        t=Coalesce(Sum('valor_aquisicao'), 0, output_field=DecimalField())
    )['t']
    patrimonios_em_uso = Patrimonio.objects.filter(situacao='em_uso').count()
    patrimonios_manutencao = Patrimonio.objects.filter(situacao='manutencao').count()

    return render(request, 'apoio/dashboard.html', {
        'total_produtos': total_produtos,
        'total_itens': total_itens,
        'estoque_baixo': estoque_baixo,
        'sem_estoque': sem_estoque,
        'valor_total': valor_total,
        'alertas_sem': alertas_sem,
        'alertas_baixo': alertas_baixo,
        'movimentacoes': movimentacoes,
        'total_patrimonios': total_patrimonios,
        'valor_patrimonio': valor_patrimonio,
        'patrimonios_em_uso': patrimonios_em_uso,
        'patrimonios_manutencao': patrimonios_manutencao,
    })


@login_required
def estoque_list(request):
    produtos = Produto.objects.prefetch_related('fornecedores__fornecedor')
    busca = request.GET.get('busca')
    categoria = request.GET.get('categoria')
    status = request.GET.get('status')
    fornecedor_id = request.GET.get('fornecedor', '')

    if busca:
        produtos = produtos.filter(Q(nome__icontains=busca) | Q(marca__icontains=busca) | Q(fornecedores__fornecedor__nome__icontains=busca)).distinct()
    if categoria:
        produtos = produtos.filter(categoria=categoria)
    if fornecedor_id:
        produtos = produtos.filter(fornecedores__fornecedor_id=fornecedor_id).distinct()
    if status:
        if status == 'baixo':
            produtos = produtos.filter(quantidade_estoque__gt=0, quantidade_estoque__lte=F('estoque_minimo'))
        elif status == 'sem_estoque':
            produtos = produtos.filter(quantidade_estoque=0)
        elif status == 'normal':
            produtos = produtos.filter(quantidade_estoque__gt=F('estoque_minimo'))

    paginator = Paginator(produtos, 20)
    page = request.GET.get('page')
    produtos_page = paginator.get_page(page)

    return render(request, 'apoio/estoque/list.html', {
        'produtos': produtos_page,
        'categorias': Produto.CATEGORIA_CHOICES,
        'fornecedores_list': Fornecedor.objects.all().order_by('nome'),
        'current_categoria': categoria,
        'current_status': status,
        'current_fornecedor': fornecedor_id,
        'busca': busca,
    })


@login_required
def estoque_create(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save()
            HistoricoProduto.objects.create(
                produto=produto, usuario=request.user, acao='Produto cadastrado',
                descricao=f'Cadastro inicial do produto {produto.nome}'
            )
            messages.success(request, 'Produto cadastrado! Use "Movimentar" para registrar a primeira compra.')
            return redirect('apoio_estoque_detail', pk=produto.pk)
    else:
        form = ProdutoForm()
    return render(request, 'apoio/estoque/form.html', {'form': form, 'action': 'Novo Produto'})


@login_required
def estoque_detail(request, pk):
    produto = get_object_or_404(Produto.objects.prefetch_related('fornecedores__fornecedor'), pk=pk)
    movimentacoes = produto.movimentacoes.select_related('usuario', 'fornecedor').order_by('-data_hora')[:10]
    historico = produto.historico.select_related('usuario')[:20]
    total_movimentacoes = produto.movimentacoes.count()

    # Última entrada com custo (independente de fornecedor) — destaque no topo
    ultima_entrada = (
        produto.movimentacoes
        .filter(tipo='entrada', custo__isnull=False)
        .select_related('fornecedor')
        .order_by('-data_hora')
        .first()
    )

    # Comparação por fornecedor: deriva das movimentações reais de entrada com custo
    entradas_com_custo = (
        produto.movimentacoes
        .filter(tipo='entrada', custo__isnull=False, fornecedor__isnull=False)
        .select_related('fornecedor')
        .order_by('-data_hora')
    )
    dados_por_forn = {}
    for m in entradas_com_custo:
        fid = m.fornecedor_id
        d = dados_por_forn.get(fid)
        if d is None:
            d = {
                'fornecedor': m.fornecedor,
                'ultimo_preco': m.custo,
                'ultima_compra': m.data_hora,
                'soma_custo': m.custo * m.quantidade,
                'soma_qtd': m.quantidade,
            }
        else:
            d['soma_custo'] += m.custo * m.quantidade
            d['soma_qtd'] += m.quantidade
        dados_por_forn[fid] = d
    # Calcula preço médio
    for d in dados_por_forn.values():
        d['preco_medio'] = d['soma_custo'] / d['soma_qtd'] if d['soma_qtd'] else 0
        d['total_comprado'] = d['soma_qtd']

    # Merge com ProdutoFornecedor vinculados (catálogo, ainda sem compra real)
    # Todos os fornecedores são iguais — não há mais "principal"
    for pf in produto.fornecedores.all().select_related('fornecedor'):
        fid = pf.fornecedor_id
        if fid not in dados_por_forn:
            dados_por_forn[fid] = {
                'fornecedor': pf.fornecedor,
                'ultimo_preco': None,
                'preco_medio': None,
                'ultima_compra': None,
                'total_comprado': 0,
                'preco_catalogo': pf.preco_unitario,
                'pf_id': pf.pk,
                'estoque': pf.quantidade,
            }
        else:
            dados_por_forn[fid]['preco_catalogo'] = pf.preco_unitario
            dados_por_forn[fid]['pf_id'] = pf.pk
            dados_por_forn[fid]['estoque'] = pf.quantidade

    # Ordena pelo último preço (None vai pro fim); marca o mais barato
    comparacao = sorted(
        dados_por_forn.values(),
        key=lambda d: (d['ultimo_preco'] is None, d['ultimo_preco'] or 0)
    )
    if comparacao and comparacao[0]['ultimo_preco'] is not None:
        comparacao[0]['mais_barato'] = True

    # Breakdown de estoque por fornecedor (para o resumo no topo do card)
    estoque_forn = sorted(
        [{'nome': d['fornecedor'].nome, 'quantidade': d.get('estoque', 0)}
         for d in dados_por_forn.values() if d.get('estoque', 0) > 0],
        key=lambda x: -x['quantidade']
    )
    total_fornecedores = len(dados_por_forn)

    return render(request, 'apoio/estoque/detail.html', {
        'produto': produto,
        'movimentacoes': movimentacoes,
        'total_movimentacoes': total_movimentacoes,
        'historico': historico,
        'ultima_entrada': ultima_entrada,
        'comparacao': comparacao,
        'estoque_forn': estoque_forn,
        'total_fornecedores': total_fornecedores,
        'todos_fornecedores': Fornecedor.objects.all().order_by('nome'),
    })


@login_required
def estoque_edit(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        old = {
            'nome': produto.nome,
            'marca': produto.marca,
            'categoria': produto.get_categoria_display(),
            'unidade_medida': produto.get_unidade_medida_display(),
            'estoque_minimo': produto.estoque_minimo,
            'valor_custo': str(produto.valor_custo),
            'descricao': produto.descricao,
            'observacoes': produto.observacoes,
        }
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            mudancas = []
            campos = [
                ('nome', 'Nome'), ('marca', 'Marca'), ('categoria', 'Categoria'),
                ('unidade_medida', 'Unidade'), ('estoque_minimo', 'Estoque mínimo'),
                ('valor_custo', 'Preço de custo'),
                ('descricao', 'Descrição'), ('observacoes', 'Observações'),
            ]
            for campo, label in campos:
                if campo in ('categoria', 'unidade_medida'):
                    novo = getattr(produto, f'get_{campo}_display')()
                elif campo == 'valor_custo':
                    novo = str(produto.valor_custo)
                else:
                    novo = getattr(produto, campo) or ''
                if old[campo] != novo:
                    mudancas.append(f'{label} alterado de "{old[campo] or "—"}" para "{novo or "—"}"')
            descricao = '. '.join(mudancas) if mudancas else 'Dados do produto foram alterados'
            HistoricoProduto.objects.create(
                produto=produto, usuario=request.user, acao='Produto atualizado',
                descricao=descricao
            )
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('apoio_estoque_detail', pk=produto.pk)
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'apoio/estoque/form.html', {'form': form, 'action': 'Editar Produto', 'produto': produto})


@login_required
def estoque_delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if produto.quantidade_estoque > 0:
        messages.error(
            request,
            f'Não é possível excluir "{produto.nome}" pois ainda há {produto.quantidade_estoque} unidade(s) em estoque. '
            'Zere o estoque via movimentações de saída antes de excluir.'
        )
        return redirect('apoio_estoque_detail', pk=produto.pk)
    if request.method == 'POST':
        Movimentacao.objects.create(
            produto=produto, tipo='saida', motivo='exclusao_produto',
            quantidade=0, saldo_apos=0, usuario=request.user,
            observacao=f'Produto excluído por: {request.user.get_full_name() or request.user.username}',
        )
        nome = produto.nome
        produto.delete()
        messages.success(request, f'Produto "{nome}" excluído com sucesso.')
        return redirect('apoio_estoque_list')
    return render(request, 'apoio/estoque/delete.html', {'produto': produto})


@login_required
@require_POST
def estoque_movimentar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    tipo = request.POST.get('tipo', '')
    quantidade = int(request.POST.get('quantidade', 0) or 0)
    custo_raw = request.POST.get('custo', '').strip()
    custo = None
    if custo_raw:
        try:
            custo = float(custo_raw.replace(',', '.'))
        except ValueError:
            custo = None
    fornecedor_id = request.POST.get('fornecedor_id', '') or None
    fornecedor = None
    if fornecedor_id:
        fornecedor = Fornecedor.objects.filter(pk=fornecedor_id).first()
    motivo = request.POST.get('motivo', '').strip()
    observacao = request.POST.get('observacao', '').strip()
    nota_fiscal = request.FILES.get('nota_fiscal')

    if tipo not in ('entrada', 'saida'):
        messages.error(request, 'Tipo de movimentação inválido.')
        return redirect('apoio_estoque_detail', pk=produto.pk)
    if quantidade <= 0:
        messages.error(request, 'Quantidade deve ser maior que zero.')
        return redirect('apoio_estoque_detail', pk=produto.pk)
    if not fornecedor:
        messages.error(request, 'Selecione um fornecedor.')
        return redirect('apoio_estoque_detail', pk=produto.pk)

    with transaction.atomic():
        pf, created = ProdutoFornecedor.objects.select_for_update().get_or_create(
            produto=produto, fornecedor=fornecedor,
            defaults={'preco_unitario': custo or 0, 'quantidade': 0}
        )

        if tipo == 'entrada':
            pf.quantidade += quantidade
            novo_saldo = produto.quantidade_estoque + quantidade
            # Atualiza custo do fornecedor + produto (último preço de compra)
            if custo is not None and custo > 0:
                pf.preco_unitario = custo
                produto.valor_custo = custo
            pf.save()
            produto.quantidade_estoque = novo_saldo
            produto.save()

        else:  # saida
            if quantidade > pf.quantidade:
                messages.error(
                    request,
                    f'Quantidade de saída maior que o saldo deste fornecedor ({pf.quantidade}).'
                )
                return redirect('apoio_estoque_detail', pk=produto.pk)
            pf.quantidade -= quantidade
            novo_saldo = produto.quantidade_estoque - quantidade
            pf.save()
            produto.quantidade_estoque = novo_saldo
            produto.save()

        Movimentacao.objects.create(
            produto=produto, tipo=tipo, motivo=motivo, quantidade=quantidade,
            saldo_apos=novo_saldo, custo=custo, nota_fiscal=nota_fiscal,
            usuario=request.user, fornecedor=fornecedor, observacao=observacao,
        )

    msg = f'{produto.nome}: {tipo} de {quantidade} registrada. Saldo total: {novo_saldo}.'
    if tipo == 'entrada' and custo is not None and custo > 0:
        msg += f' Preço de custo atualizado para R$ {custo:.2f}.'
    messages.success(request, msg)
    return redirect('apoio_estoque_detail', pk=produto.pk)


@login_required
def estoque_fornecedores_json(request, pk):
    """Retorna os fornecedores vinculados ao produto com seus saldos.
    Usado pelo modal de movimentar em saída/ajuste para popular o select."""
    produto = get_object_or_404(Produto, pk=pk)
    pfs = produto.fornecedores.select_related('fornecedor').all()
    return JsonResponse({
        'fornecedores': [
            {'id': pf.fornecedor_id, 'nome': pf.fornecedor.nome, 'quantidade': pf.quantidade}
            for pf in pfs
        ],
        'total': produto.quantidade_estoque,
    })


@login_required
def fornecedor_list(request):
    fornecedores = Fornecedor.objects.all()
    busca = request.GET.get('busca', '')
    categoria = request.GET.get('categoria', '')

    if busca:
        fornecedores = fornecedores.filter(Q(nome__icontains=busca) | Q(contato__icontains=busca))
    if categoria:
        fornecedores = fornecedores.filter(categoria=categoria)

    paginator = Paginator(fornecedores, 20)
    page = request.GET.get('page')
    return render(request, 'apoio/fornecedor/list.html', {
        'fornecedores': paginator.get_page(page),
        'busca': busca,
        'categorias': Fornecedor.CATEGORIA_FORNECEDOR_CHOICES,
        'current_categoria': categoria,
    })


@login_required
def fornecedor_create(request):
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor cadastrado com sucesso!')
            return redirect('apoio_fornecedor_list')
    else:
        form = FornecedorForm()
    return render(request, 'apoio/fornecedor/form.html', {'form': form, 'action': 'Novo Fornecedor'})


@login_required
def fornecedor_detail(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    # Produtos vinculados com saldo atual e total comprado
    vinculos = (
        ProdutoFornecedor.objects
        .filter(fornecedor=fornecedor)
        .select_related('produto')
        .order_by('-quantidade', 'produto__nome')
    )
    total_itens_estoque = sum(pf.quantidade for pf in vinculos)

    # Total já comprado (soma de entradas)
    total_comprado = (
        Movimentacao.objects
        .filter(fornecedor=fornecedor, tipo='entrada')
        .aggregate(t=Coalesce(Sum('quantidade'), 0, output_field=IntegerField()))['t']
    )

    # Últimas compras (entradas)
    ultimas_compras = (
        Movimentacao.objects
        .filter(fornecedor=fornecedor, tipo='entrada')
        .select_related('produto', 'usuario')
        .order_by('-data_hora')[:10]
    )

    return render(request, 'apoio/fornecedor/detail.html', {
        'fornecedor': fornecedor,
        'vinculos': vinculos,
        'total_itens_estoque': total_itens_estoque,
        'total_comprado': total_comprado,
        'ultimas_compras': ultimas_compras,
    })


@login_required
def fornecedor_edit(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fornecedor atualizado com sucesso!')
            return redirect('apoio_fornecedor_detail', pk=fornecedor.pk)
    else:
        form = FornecedorForm(instance=fornecedor)
    return render(request, 'apoio/fornecedor/form.html', {'form': form, 'action': 'Editar Fornecedor', 'fornecedor': fornecedor})


@login_required
def patrimonio_list(request):
    patrimonios = Patrimonio.objects.all()
    categoria = request.GET.get('categoria', '')
    setor = request.GET.get('setor', '')
    situacao = request.GET.get('situacao', '')
    responsavel = request.GET.get('responsavel', '')
    busca = request.GET.get('busca', '')

    if categoria:
        patrimonios = patrimonios.filter(categoria=categoria)
    if setor:
        patrimonios = patrimonios.filter(setor=setor)
    if situacao:
        patrimonios = patrimonios.filter(situacao=situacao)
    if responsavel:
        patrimonios = patrimonios.filter(responsavel=responsavel)
    if busca:
        patrimonios = patrimonios.filter(Q(nome__icontains=busca) | Q(numero_patrimonio__icontains=busca) | Q(marca__icontains=busca) | Q(modelo__icontains=busca))

    paginator = Paginator(patrimonios, 20)
    page = request.GET.get('page')
    return render(request, 'apoio/patrimonio/list.html', {
        'patrimonios': paginator.get_page(page),
        'categorias': Patrimonio.CATEGORIA_CHOICES,
        'setores': Patrimonio.SETOR_CHOICES,
        'situacoes': Patrimonio.SITUACAO_CHOICES,
        'responsaveis': Patrimonio.objects.exclude(responsavel='').values_list('responsavel', flat=True).distinct().order_by('responsavel'),
        'current_categoria': categoria,
        'current_setor': setor,
        'current_situacao': situacao,
        'current_responsavel': responsavel,
        'busca': busca,
    })


@login_required
def patrimonio_create(request):
    if request.method == 'POST':
        form = PatrimonioForm(request.POST, request.FILES)
        if form.is_valid():
            patrimonio = form.save()
            HistoricoPatrimonio.objects.create(
                patrimonio=patrimonio, usuario=request.user, acao='Patrimônio cadastrado',
                descricao=f'Cadastro inicial do patrimônio {patrimonio.numero_patrimonio}'
            )
            messages.success(request, 'Patrimônio cadastrado com sucesso!')
            return redirect('apoio_patrimonio_list')
    else:
        form = PatrimonioForm()
    return render(request, 'apoio/patrimonio/form.html', {'form': form, 'action': 'Novo Patrimônio'})


@login_required
def patrimonio_detail(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    historico = patrimonio.historico.select_related('usuario')
    return render(request, 'apoio/patrimonio/detail.html', {
        'patrimonio': patrimonio,
        'historico': historico,
    })


@login_required
def patrimonio_edit(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    if request.method == 'POST':
        old = {
            'numero_patrimonio': patrimonio.numero_patrimonio,
            'nome': patrimonio.nome,
            'marca': patrimonio.marca,
            'modelo': patrimonio.modelo,
            'categoria': patrimonio.get_categoria_display(),
            'setor': patrimonio.get_setor_display(),
            'responsavel': patrimonio.responsavel,
            'situacao': patrimonio.get_situacao_display(),
            'data_aquisicao': patrimonio.data_aquisicao.strftime('%d/%m/%Y') if patrimonio.data_aquisicao else '',
            'valor_aquisicao': str(patrimonio.valor_aquisicao) if patrimonio.valor_aquisicao else '',
            'descricao': patrimonio.descricao,
            'observacoes': patrimonio.observacoes,
        }
        form = PatrimonioForm(request.POST, request.FILES, instance=patrimonio)
        if form.is_valid():
            form.save()
            mudancas = []
            campos = [
                ('numero_patrimonio', 'Nº Patrimônio'), ('nome', 'Nome'), ('marca', 'Marca'),
                ('modelo', 'Modelo'), ('categoria', 'Categoria'), ('setor', 'Setor'),
                ('responsavel', 'Responsável'), ('situacao', 'Situação'),
                ('data_aquisicao', 'Data de aquisição'), ('valor_aquisicao', 'Valor de aquisição'),
                ('descricao', 'Descrição'), ('observacoes', 'Observações'),
            ]
            for campo, label in campos:
                if campo in ('categoria', 'setor', 'situacao'):
                    novo = getattr(patrimonio, f'get_{campo}_display')()
                elif campo == 'data_aquisicao':
                    novo = patrimonio.data_aquisicao.strftime('%d/%m/%Y') if patrimonio.data_aquisicao else ''
                elif campo == 'valor_aquisicao':
                    novo = str(patrimonio.valor_aquisicao) if patrimonio.valor_aquisicao else ''
                else:
                    novo = getattr(patrimonio, campo) or ''
                if old[campo] != novo:
                    mudancas.append(f'{label} alterado de "{old[campo] or "—"}" para "{novo or "—"}"')
            descricao = '. '.join(mudancas) if mudancas else 'Dados do patrimônio foram alterados'
            HistoricoPatrimonio.objects.create(
                patrimonio=patrimonio, usuario=request.user, acao='Patrimônio atualizado',
                descricao=descricao
            )
            messages.success(request, 'Patrimônio atualizado com sucesso!')
            return redirect('apoio_patrimonio_detail', pk=patrimonio.pk)
    else:
        form = PatrimonioForm(instance=patrimonio)
    return render(request, 'apoio/patrimonio/form.html', {'form': form, 'action': 'Editar Patrimônio', 'patrimonio': patrimonio})


@login_required
def patrimonio_delete(request, pk):
    patrimonio = get_object_or_404(Patrimonio, pk=pk)
    if request.method == 'POST':
        HistoricoPatrimonio.objects.create(
            patrimonio=patrimonio, usuario=request.user, acao='Patrimônio excluído',
            descricao=f'Patrimônio {patrimonio.numero_patrimonio} ({patrimonio.nome}) excluído por {request.user.get_full_name() or request.user.username}'
        )
        numero = patrimonio.numero_patrimonio
        patrimonio.delete()
        messages.success(request, f'Patrimônio "{numero}" excluído com sucesso.')
        return redirect('apoio_patrimonio_list')
    return render(request, 'apoio/patrimonio/delete.html', {'patrimonio': patrimonio})


@login_required
def fornecedor_delete(request, pk):
    fornecedor = get_object_or_404(Fornecedor, pk=pk)
    vinculos = ProdutoFornecedor.objects.filter(fornecedor=fornecedor).count()
    if request.method == 'POST':
        if vinculos > 0:
            messages.error(request, f'Não é possível excluir "{fornecedor.nome}" pois existem {vinculos} produto(s) vinculado(s) a este fornecedor. Remova os vínculos antes de excluir.')
            return redirect('apoio_fornecedor_detail', pk=fornecedor.pk)
        nome = fornecedor.nome
        fornecedor.delete()
        messages.success(request, f'Fornecedor "{nome}" excluído com sucesso.')
        return redirect('apoio_fornecedor_list')
    return render(request, 'apoio/fornecedor/delete.html', {
        'fornecedor': fornecedor,
        'vinculos': vinculos,
    })


@login_required
@require_POST
def fornecedor_create_ajax(request):
    nome = request.POST.get('nome', '').strip()
    if not nome:
        return JsonResponse({'error': 'Nome é obrigatório'}, status=400)
    fornecedor = Fornecedor.objects.create(
        nome=nome,
        contato=request.POST.get('contato', ''),
        telefone=request.POST.get('telefone', ''),
    )
    return JsonResponse({'id': fornecedor.pk, 'nome': fornecedor.nome})


@login_required
def fornecedor_vincular(request, produto_pk):
    produto = get_object_or_404(Produto, pk=produto_pk)
    fornecedor_id = request.POST.get('fornecedor_id')
    preco = request.POST.get('preco', 0) or 0
    if fornecedor_id:
        ProdutoFornecedor.objects.get_or_create(
            produto=produto, fornecedor_id=fornecedor_id,
            defaults={'preco_unitario': preco}
        )
        messages.success(request, 'Fornecedor vinculado!')
    return redirect('apoio_estoque_detail', pk=produto.pk)


@login_required
def fornecedor_remover(request, pf_pk):
    pf = get_object_or_404(ProdutoFornecedor, pk=pf_pk)
    pk = pf.produto.pk
    produto = pf.produto
    saldo_removido = pf.quantidade
    pf.delete()
    # Recomputa o total do produto (caso o vínculo removido tivesse saldo)
    if saldo_removido:
        total = ProdutoFornecedor.objects.filter(produto=produto).aggregate(
            t=Coalesce(Sum('quantidade'), 0, output_field=IntegerField())
        )['t']
        produto.quantidade_estoque = total
        produto.save()
        messages.success(request, f'Fornecedor removido. Saldo de {saldo_removido} foi abatido do total.')
    else:
        messages.success(request, 'Fornecedor removido.')
    return redirect('apoio_estoque_detail', pk=pk)


# ---------------------------------------------------------------------------
# Fase 3 — Movimentações + Relatórios
# ---------------------------------------------------------------------------

@login_required
def movimentacoes_list(request):
    movs = Movimentacao.objects.select_related('produto', 'usuario', 'fornecedor')

    tipo = request.GET.get('tipo', '')
    motivo = request.GET.get('motivo', '')
    fornecedor_id = request.GET.get('fornecedor', '')
    produto_busca = request.GET.get('produto', '').strip()
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    if tipo:
        movs = movs.filter(tipo=tipo)
    if motivo:
        movs = movs.filter(motivo=motivo)
    if fornecedor_id:
        movs = movs.filter(fornecedor_id=fornecedor_id)
    if produto_busca:
        movs = movs.filter(produto__nome__icontains=produto_busca)
    if data_inicio:
        movs = movs.filter(data_hora__date__gte=data_inicio)
    if data_fim:
        movs = movs.filter(data_hora__date__lte=data_fim)

    paginator = Paginator(movs, 25)
    page = request.GET.get('page')
    return render(request, 'apoio/movimentacoes/list.html', {
        'movimentacoes': paginator.get_page(page),
        'tipos': Movimentacao.TIPO_CHOICES,
        'motivos': Movimentacao.MOTIVO_CHOICES,
        'fornecedores_list': Fornecedor.objects.all().order_by('nome'),
        'current_tipo': tipo,
        'current_motivo': motivo,
        'current_fornecedor': fornecedor_id,
        'current_produto': produto_busca,
        'current_data_inicio': data_inicio,
        'current_data_fim': data_fim,
    })


@login_required
@require_POST
def movimentacao_estornar(request, pk):
    """Estorna uma movimentação criando a operação inversa e recalculando saldos."""
    mov = get_object_or_404(Movimentacao.objects.select_related('produto', 'fornecedor'), pk=pk)
    if not mov.fornecedor:
        messages.error(request, 'Movimentação sem fornecedor — não é possível estornar.')
        return redirect('apoio_movimentacoes_list')

    produto = mov.produto
    fornecedor = mov.fornecedor
    qtd = mov.quantidade
    tipo_inverso = 'saida' if mov.tipo == 'entrada' else 'entrada'
    motivo_estorno = 'outro'

    with transaction.atomic():
        pf = ProdutoFornecedor.objects.select_for_update().get(produto=produto, fornecedor=fornecedor)

        if tipo_inverso == 'saida':
            # Estornando uma entrada → saída inversa
            if qtd > pf.quantidade:
                messages.error(request, f'Não é possível estornar: saldo do fornecedor ({pf.quantidade}) é menor que a quantidade ({qtd}).')
                return redirect('apoio_movimentacoes_list')
            pf.quantidade -= qtd
            novo_saldo = produto.quantidade_estoque - qtd
        else:
            # Estornando uma saída → entrada inversa
            pf.quantidade += qtd
            novo_saldo = produto.quantidade_estoque + qtd

        pf.save()
        produto.quantidade_estoque = novo_saldo
        produto.save()

        Movimentacao.objects.create(
            produto=produto, tipo=tipo_inverso, motivo=motivo_estorno,
            quantidade=qtd, saldo_apos=novo_saldo, custo=mov.custo,
            usuario=request.user, fornecedor=fornecedor,
            observacao=f'Estorno da movimentação #{mov.pk} ({mov.get_tipo_display()} de {qtd})',
        )

    messages.success(request, f'Movimentação #{mov.pk} estornada com sucesso. Saldo total: {novo_saldo}.')
    return redirect('apoio_movimentacoes_list')


def _periodo_movimentacoes(movs, mes, ano):
    """Filtra queryset de movimentações para um mês/ano específicos."""
    mes_inicio = date(ano, mes, 1)
    _, last_day = calendar.monthrange(ano, mes)
    mes_fim = date(ano, mes, last_day)
    return movs.filter(data_hora__date__gte=mes_inicio, data_hora__date__lte=mes_fim)


@login_required
def apoio_relatorios(request):
    hoje = datetime.now()
    try:
        mes = int(request.GET.get('mes', hoje.month))
        ano = int(request.GET.get('ano', hoje.year))
    except (ValueError, TypeError):
        mes = hoje.month
        ano = hoje.year

    movs_ano = Movimentacao.objects.filter(data_hora__year=ano)
    movs_mes = _periodo_movimentacoes(movs_ano, mes, ano)

    # Resumo do mês
    entradas_mes = movs_mes.filter(tipo='entrada').aggregate(t=Coalesce(Sum('quantidade'), 0, output_field=IntegerField()))['t']
    saidas_mes = movs_mes.filter(tipo='saida').aggregate(t=Coalesce(Sum('quantidade'), 0, output_field=IntegerField()))['t']
    custo_consumo = movs_mes.filter(tipo='saida').aggregate(
        t=Coalesce(Sum(F('quantidade') * F('custo'), output_field=DecimalField()), 0, output_field=DecimalField())
    )['t']

    # Consumo por produto (mês)
    consumo_por_produto = movs_mes.values('produto__nome', 'produto__marca', 'produto__categoria', 'produto__unidade_medida').annotate(
        entradas=Coalesce(Sum('quantidade', filter=Q(tipo='entrada')), 0, output_field=IntegerField()),
        saidas=Coalesce(Sum('quantidade', filter=Q(tipo='saida')), 0, output_field=IntegerField()),
    ).order_by('-saidas')

    # Saídas por motivo (mês)
    saidas_por_motivo = movs_mes.filter(tipo='saida').values('motivo').annotate(
        total=Coalesce(Sum('quantidade'), 0, output_field=IntegerField()),
        count=Count('id'),
    ).order_by('-total')

    # Totais anuais por mês (12 meses)
    monthly_totals = []
    for i in range(1, 13):
        m = movs_ano.filter(data_hora__month=i)
        monthly_totals.append({
            'mes': MESES_NOMES[i - 1][:3],
            'entradas': m.filter(tipo='entrada').aggregate(t=Coalesce(Sum('quantidade'), 0, output_field=IntegerField()))['t'],
            'saidas': m.filter(tipo='saida').aggregate(t=Coalesce(Sum('quantidade'), 0, output_field=IntegerField()))['t'],
        })
    ano_total_entradas = sum(mt['entradas'] for mt in monthly_totals)
    ano_total_saidas = sum(mt['saidas'] for mt in monthly_totals)

    # Anos disponíveis (do histórico de movimentações + atual)
    anos_disponiveis = sorted(
        {int(y) for y in Movimentacao.objects.dates('data_hora', 'year') for y in [y.year]} | {hoje.year, hoje.year - 1},
        reverse=True,
    )

    # Stats de patrimônio
    patrimonios = Patrimonio.objects.all()
    total_patrimonios = patrimonios.count()
    valor_patrimonio = patrimonios.aggregate(t=Coalesce(Sum('valor_aquisicao'), 0, output_field=DecimalField()))['t']
    por_setor = patrimonios.values('setor').annotate(total=Count('id')).order_by('-total')
    por_situacao = patrimonios.values('situacao').annotate(total=Count('id')).order_by('-total')

    # Stats de estoque
    produtos = Produto.objects.all()
    total_produtos = produtos.count()
    valor_custo_total = produtos.aggregate(
        t=Coalesce(Sum(F('quantidade_estoque') * F('valor_custo'), output_field=DecimalField()), 0, output_field=DecimalField())
    )['t']
    baixo = produtos.filter(quantidade_estoque__gt=0, quantidade_estoque__lte=F('estoque_minimo')).count()
    zerado = produtos.filter(quantidade_estoque=0).count()
    por_categoria = produtos.values('categoria').annotate(total=Count('id')).order_by('-total')

    # Dados para gráficos (Chart.js)
    # 1. Entradas vs Saídas ao longo do ano (linha, 12 meses)
    chart_labels_mes = [mt['mes'] for mt in monthly_totals]
    chart_entradas = [mt['entradas'] for mt in monthly_totals]
    chart_saidas = [mt['saidas'] for mt in monthly_totals]

    # 2. Saídas por motivo (doughnut, mês atual)
    chart_motivo_labels = [dict(Movimentacao.MOTIVO_CHOICES).get(s['motivo'], s['motivo'] or 'Sem motivo') for s in saidas_por_motivo]
    chart_motivo_data = [s['total'] for s in saidas_por_motivo]

    # 3. Top 10 produtos por consumo (saídas do mês, barra horizontal)
    top_consumo = list(consumo_por_produto[:10])
    chart_top_labels = [c['produto__nome'] for c in top_consumo]
    chart_top_saidas = [c['saidas'] for c in top_consumo]
    chart_top_entradas = [c['entradas'] for c in top_consumo]

    return render(request, 'apoio/relatorios/index.html', {
        'mes': mes,
        'ano': ano,
        'mes_nome': MESES_NOMES[mes - 1],
        'anos_disponiveis': anos_disponiveis,
        'meses_choices': list(enumerate(MESES_NOMES, start=1)),
        # Resumo mês
        'entradas_mes': entradas_mes,
        'saidas_mes': saidas_mes,
        'custo_consumo': custo_consumo,
        'consumo_por_produto': consumo_por_produto,
        'saidas_por_motivo': saidas_por_motivo,
        # Resumo ano
        'monthly_totals': monthly_totals,
        'ano_total_entradas': ano_total_entradas,
        'ano_total_saidas': ano_total_saidas,
        # Patrimônio
        'total_patrimonios': total_patrimonios,
        'valor_patrimonio': valor_patrimonio,
        'por_setor': por_setor,
        'por_situacao': por_situacao,
        # Estoque
        'total_produtos': total_produtos,
        'valor_custo_total': valor_custo_total,
        'baixo': baixo,
        'zerado': zerado,
        'por_categoria': por_categoria,
        # Gráficos
        'chart_labels_mes': json.dumps(chart_labels_mes),
        'chart_entradas': json.dumps(chart_entradas),
        'chart_saidas': json.dumps(chart_saidas),
        'chart_motivo_labels': json.dumps(chart_motivo_labels),
        'chart_motivo_data': json.dumps(chart_motivo_data),
        'chart_top_labels': json.dumps(chart_top_labels),
        'chart_top_saidas': json.dumps(chart_top_saidas),
        'chart_top_entradas': json.dumps(chart_top_entradas),
    })


@login_required
def apoio_exportar_csv(request):
    tipo_export = request.GET.get('tipo', 'produtos')
    hoje = datetime.now()
    try:
        mes = int(request.GET.get('mes', hoje.month))
        ano = int(request.GET.get('ano', hoje.year))
    except (ValueError, TypeError):
        mes = hoje.month
        ano = hoje.year

    response = HttpResponse(content_type='text/csv')
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')

    if tipo_export == 'patrimonios':
        response['Content-Disposition'] = f'attachment; filename="patrimonios_{hoje.strftime("%Y%m%d")}.csv"'
        writer.writerow(['Nº Patrimônio', 'Nome', 'Marca', 'Modelo', 'Categoria', 'Setor', 'Responsável', 'Situação', 'Data Aquisição', 'Valor Aquisição'])
        for p in Patrimonio.objects.all().order_by('numero_patrimonio'):
            writer.writerow([
                p.numero_patrimonio, p.nome, p.marca, p.modelo,
                p.get_categoria_display(), p.get_setor_display(), p.responsavel,
                p.get_situacao_display(),
                p.data_aquisicao.strftime('%d/%m/%Y') if p.data_aquisicao else '',
                str(p.valor_aquisicao).replace('.', ',') if p.valor_aquisicao else '',
            ])
        return response

    if tipo_export == 'movimentacoes':
        response['Content-Disposition'] = f'attachment; filename="movimentacoes_{MESES_NOMES[mes-1].lower()}_{ano}.csv"'
        writer.writerow(['Data/Hora', 'Produto', 'Tipo', 'Motivo', 'Quantidade', 'Saldo após', 'Custo', 'Fornecedor', 'Usuário', 'Observação'])
        movs = _periodo_movimentacoes(Movimentacao.objects.select_related('produto', 'usuario', 'fornecedor'), mes, ano)
        for m in movs.order_by('-data_hora'):
            writer.writerow([
                m.data_hora.strftime('%d/%m/%Y %H:%M'),
                m.produto.nome, m.get_tipo_display(), m.get_motivo_display() if m.motivo else '—',
                m.quantidade, m.saldo_apos,
                str(m.custo).replace('.', ',') if m.custo else '',
                m.fornecedor.nome if m.fornecedor else '',
                m.usuario.get_full_name() if m.usuario else '—',
                m.observacao,
            ])
        return response

    # Padrão: produtos
    sufixo = hoje.strftime('%Y%m%d')
    response['Content-Disposition'] = f'attachment; filename="estoque_{sufixo}.csv"'
    writer.writerow(['Nome', 'Marca', 'Categoria', 'Unidade', 'Quantidade', 'Estoque Mínimo', 'Preço Custo', 'Valor Total', 'Fornecedores', 'Status'])
    for p in Produto.objects.prefetch_related('fornecedores__fornecedor').order_by('nome'):
        fornecedores_nomes = ', '.join(pf.fornecedor.nome for pf in p.fornecedores.all())
        writer.writerow([
            p.nome, p.marca, p.get_categoria_display(), p.get_unidade_medida_display(),
            p.quantidade_estoque, p.estoque_minimo,
            str(p.valor_custo).replace('.', ','),
            str(p.valor_total).replace('.', ','),
            fornecedores_nomes,
            p.status_estoque.replace('_', ' ').title(),
        ])
    return response
