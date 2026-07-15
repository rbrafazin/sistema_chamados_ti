from django import forms
from .models import Chamado

class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['titulo', 'descricao', 'solicitante', 'setor', 'categoria', 'prioridade', 'status', 'tecnico', 'observacoes', 'imagem_tecnica', 'imagem_solicitante']
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
        self.fields['categoria'].required = True
        self.fields['categoria'].choices = [(k, v) for k, v in self.fields['categoria'].choices if k]
        self.fields['prioridade'].required = True
        self.fields['prioridade'].choices = [(k, v) for k, v in self.fields['prioridade'].choices if k]
        if self.instance and self.instance.pk:
            self.fields['titulo'].disabled = True
            self.fields['descricao'].disabled = True
            self.fields['solicitante'].disabled = True
            self.fields['setor'].disabled = True
            self.fields['imagem_solicitante'].disabled = True
        else:
            self.fields['setor'].choices = [('', 'Selecionar...')] + [(k, v) for k, v in self.fields['setor'].choices if k]
            self.fields['setor'].initial = ''
            self.fields['solicitante'].widget = forms.Select(choices=[('', 'Primeiro escolha o setor...')])


class ChamadoFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', 'Status...')] + Chamado.STATUS_CHOICES, required=False, label='Status')
    prioridade = forms.ChoiceField(choices=[('', 'Prioridade...')] + Chamado.PRIORIDADE_CHOICES, required=False, label='Prioridade')
    categoria = forms.ChoiceField(choices=[('', 'Categoria...')] + Chamado.CATEGORIA_CHOICES, required=False, label='Categoria')
    busca = forms.CharField(required=False, label='', initial='', widget=forms.TextInput(attrs={'placeholder': 'Pesquisar...'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select form-select-sm' if isinstance(field.widget, forms.Select) else 'form-control form-control-sm'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['onchange'] = "this.form.submit()"
