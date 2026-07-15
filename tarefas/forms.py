from django import forms
from django.contrib.auth.models import User
from .models import Tarefa

class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'prioridade', 'status', 'responsavel', 'prazo']
        widgets = {
            'prazo': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
        self.fields['responsavel'].queryset = User.objects.filter(perfil__setor='ti').order_by('first_name')
        self.fields['responsavel'].required = False
        self.fields['responsavel'].empty_label = 'Selecionar...'
        self.fields['responsavel'].label_from_instance = lambda obj: obj.get_full_name() or obj.username
        self.fields['prazo'].required = False
