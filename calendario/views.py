from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Evento
from .forms import EventoForm

PRIORIDADE_CORES = {
    'baixa': '#0e6027',
    'media': '#0f62fe',
    'alta': '#b85c00',
    'critica': '#da1e28',
}
COR_PRIORIDADE = {v: k for k, v in PRIORIDADE_CORES.items()}

@login_required
def calendario_index(request):
    return render(request, 'calendario/index.html')

@login_required
def eventos_json(request):
    eventos = Evento.objects.all()
    data = []
    for e in eventos:
        data.append({
            'id': e.pk,
            'title': e.titulo,
            'start': e.data_inicio.isoformat(),
            'end': e.data_fim.isoformat(),
            'color': e.cor,
            'allDay': e.dia_todo,
            'extendedProps': {
                'descricao': e.descricao,
                'tipo': e.tipo,
                'tipo_display': e.get_tipo_display(),
                'prioridade': COR_PRIORIDADE.get(e.cor, 'media'),
            }
        })
    return JsonResponse(data, safe=False)

@login_required
def evento_create(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.criado_por = request.user
            prioridade = request.POST.get('prioridade', 'media')
            evento.cor = PRIORIDADE_CORES.get(prioridade, '#0f62fe')
            evento.save()
            messages.success(request, 'Evento criado!')
        else:
            messages.error(request, 'Erro ao criar evento. Verifique os campos.')
    return redirect('calendario_index')

@login_required
def evento_edit(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            evento = form.save(commit=False)
            prioridade = request.POST.get('prioridade', 'media')
            evento.cor = PRIORIDADE_CORES.get(prioridade, '#0f62fe')
            evento.save()
            messages.success(request, 'Evento atualizado!')
            return redirect('calendario_index')
        else:
            messages.error(request, 'Erro ao atualizar evento. Verifique os campos.')
            return redirect('calendario_index')
    return redirect('calendario_index')

@login_required
def evento_delete(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if request.method == 'POST':
        try:
            evento.delete()
            messages.success(request, 'Evento excluído!')
        except Exception:
            messages.error(request, 'Erro ao excluir o evento.')
    return redirect('calendario_index')
