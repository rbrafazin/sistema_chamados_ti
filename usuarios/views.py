from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .models import Perfil
from .forms import PerfilForm, UsuarioForm

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def usuarios_list(request):
    usuarios = User.objects.select_related('perfil').all().order_by('first_name')
    paginator = Paginator(usuarios, 20)
    page = request.GET.get('page')
    usuarios_page = paginator.get_page(page)
    return render(request, 'usuarios/list.html', {'usuarios': usuarios_page})

@login_required
@user_passes_test(is_admin)
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuário {user.username} criado com sucesso!')
            return redirect('usuarios_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/form.html', {'form': form, 'action': 'Novo Usuário'})

@login_required
@user_passes_test(is_admin)
def usuario_detail(request, pk):
    usuario = get_object_or_404(User.objects.select_related('perfil'), pk=pk)
    return render(request, 'usuarios/detail.html', {'usuario': usuario})


@login_required
@user_passes_test(is_admin)
def usuario_edit(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('usuarios_list')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'usuarios/form.html', {'form': form, 'action': 'Editar Usuário', 'usuario': usuario})

@login_required
def perfil_edit(request):
    perfil = request.user.perfil
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'usuarios/perfil_form.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def usuario_delete(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario == request.user:
        messages.error(request, 'Você não pode excluir seu próprio usuário.')
        return redirect('usuarios_list')
    if request.method == 'POST':
        try:
            usuario.delete()
            messages.success(request, 'Usuário excluído!')
        except Exception:
            messages.error(request, 'Erro ao excluir o usuário.')
        return redirect('usuarios_list')
    return render(request, 'usuarios/confirm_delete.html', {'usuario': usuario})
