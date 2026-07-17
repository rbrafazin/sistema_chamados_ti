from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from chamados.models import Chamado
from .forms import PortalChamadoForm


@login_required
def portal_index(request):
    if request.method == 'POST':
        form = PortalChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.solicitante = request.user.get_full_name() or request.user.username
            chamado.setor = request.user.perfil.setor
            chamado.status = 'aberto'
            chamado.criado_por = request.user
            if form.cleaned_data.get('imagem'):
                chamado.imagem_solicitante = form.cleaned_data['imagem']
            chamado.save()
            messages.success(request, 'Chamado enviado com sucesso! Nossa equipe de TI vai analisar.')
            return redirect('portal_index')
        else:
            messages.error(request, 'Erro ao enviar. Verifique os campos.')
    else:
        form = PortalChamadoForm()

    chamados_qs = Chamado.objects.filter(criado_por=request.user).order_by('-criado_em')
    total_chamados = chamados_qs.count()
    paginator = Paginator(chamados_qs, 10)
    page = request.GET.get('page')
    meus_chamados = paginator.get_page(page)

    return render(request, 'portal/index.html', {
        'form': form,
        'meus_chamados': meus_chamados,
        'total_chamados': total_chamados,
    })


@login_required
def portal_detail(request, pk):
    chamado = get_object_or_404(Chamado.objects.filter(criado_por=request.user), pk=pk)
    return render(request, 'portal/detail.html', {'chamado': chamado})


@login_required
def portal_stats(request):
    chamados = Chamado.objects.filter(criado_por=request.user).order_by('-criado_em')[:10]
    return JsonResponse({
        'total': Chamado.objects.filter(criado_por=request.user).count(),
        'chamados': [{
            'pk': c.pk,
            'titulo': c.titulo,
            'status': c.get_status_display(),
            'status_class': c.status,
            'data': c.criado_em.strftime('%d/%m/%Y %H:%M'),
            'categoria': c.get_categoria_display(),
        } for c in chamados]
    })
