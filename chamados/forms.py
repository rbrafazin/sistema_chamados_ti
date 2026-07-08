from django import forms
from .models import Chamado

class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['titulo', 'descricao', 'solicitante', 'setor', 'categoria', 'prioridade', 'status', 'tecnico', 'observacoes', 'imagem_tecnica']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4, 'class': 'auto-resize'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'auto-resize'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
        self.fields['tecnico'].required = False
        self.fields['tecnico'].empty_label = 'Selecionar...'


class ChamadoFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', 'Todos')] + Chamado.STATUS_CHOICES, required=False, label='Status')
    prioridade = forms.ChoiceField(choices=[('', 'Todas')] + Chamado.PRIORIDADE_CHOICES, required=False, label='Prioridade')
    categoria = forms.ChoiceField(choices=[('', 'Todas')] + Chamado.CATEGORIA_CHOICES, required=False, label='Categoria')
    busca = forms.CharField(required=False, label='', initial='', widget=forms.TextInput(attrs={'placeholder': 'Pesquisar...'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select form-select-sm' if isinstance(field.widget, forms.Select) else 'form-control form-control-sm'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['onchange'] = "document.querySelector('#id_busca').value=''; this.form.submit()"
