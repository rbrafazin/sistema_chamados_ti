from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from .models import Artigo, Categoria
from .forms import ArtigoForm, CategoriaForm

@login_required
def conhecimento_list(request):
    artigos = Artigo.objects.select_related('categoria', 'autor').all()
    categorias = Categoria.objects.annotate(total_artigos=Count('artigos')).all()
    busca = request.GET.get('busca')
    categoria_id = request.GET.get('categoria')

    if categoria_id:
        artigos = artigos.filter(categoria_id=categoria_id)
    if busca:
        artigos = artigos.filter(Q(titulo__icontains=busca) | Q(conteudo__icontains=busca))

    paginator = Paginator(artigos, 10)
    page = request.GET.get('page')
    artigos_page = paginator.get_page(page)

    return render(request, 'conhecimento/list.html', {
        'artigos': artigos_page, 'categorias': categorias,
        'busca': busca, 'current_categoria': categoria_id,
    })

@login_required
def conhecimento_create(request):
    if request.method == 'POST':
        form = ArtigoForm(request.POST, request.FILES)
        if form.is_valid():
            artigo = form.save(commit=False)
            artigo.autor = request.user
            artigo.save()
            messages.success(request, 'Artigo criado com sucesso!')
            return redirect('conhecimento_list')
    else:
        form = ArtigoForm()
    return render(request, 'conhecimento/form.html', {'form': form, 'action': 'Novo Artigo'})

@login_required
def conhecimento_detail(request, pk):
    artigo = get_object_or_404(Artigo, pk=pk)
    Artigo.objects.filter(pk=pk).update(visualizacoes=F('visualizacoes') + 1)
    artigo.refresh_from_db()
    return render(request, 'conhecimento/detail.html', {'artigo': artigo})

@login_required
def conhecimento_edit(request, pk):
    artigo = get_object_or_404(Artigo, pk=pk)
    if request.method == 'POST':
        form = ArtigoForm(request.POST, request.FILES, instance=artigo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artigo atualizado com sucesso!')
            return redirect('conhecimento_detail', pk=artigo.pk)
    else:
        form = ArtigoForm(instance=artigo)
    return render(request, 'conhecimento/form.html', {'form': form, 'action': 'Editar Artigo', 'artigo': artigo})

@login_required
def conhecimento_delete(request, pk):
    artigo = get_object_or_404(Artigo, pk=pk)
    if request.method == 'POST':
        try:
            artigo.delete()
            messages.success(request, 'Artigo excluído!')
        except Exception:
            messages.error(request, 'Erro ao excluir o artigo.')
        return redirect('conhecimento_list')
    return render(request, 'conhecimento/confirm_delete.html', {'artigo': artigo})

@login_required
def categoria_create(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada!')
        else:
            messages.error(request, 'Erro ao criar categoria. Verifique o nome.')
    return redirect('conhecimento_list')


@login_required
def categoria_edit(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada!')
            return redirect('conhecimento_list')
        else:
            messages.error(request, 'Erro ao atualizar categoria.')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'conhecimento/categoria_form.html', {'form': form, 'categoria': categoria})


@login_required
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nome = categoria.nome
        categoria.delete()
        messages.success(request, f'Categoria "{nome}" excluída!')
        return redirect('conhecimento_list')
    return render(request, 'conhecimento/categoria_confirm_delete.html', {'categoria': categoria})
