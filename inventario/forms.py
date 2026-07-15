from django import forms
from django.contrib.auth.models import User
from .models import Equipamento

class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = [
            'patrimonio', 'hostname', 'categoria', 'marca', 'modelo',
            'numero_serie', 'processador', 'memoria_ram', 'armazenamento',
            'sistema_operacional', 'ip', 'mac_address', 'setor',
            'responsavel', 'status', 'observacoes', 'imagem',
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
        if not self.instance.pk:
            self.fields['setor'].choices = [('', 'Selecionar...')] + [(k, v) for k, v in self.fields['setor'].choices if k]
            self.fields['setor'].initial = ''
            self.fields['responsavel'].queryset = User.objects.none()
            self.fields['responsavel'].empty_label = 'Primeiro escolha o setor...'
        else:
            self.fields['responsavel'].empty_label = 'Selecionar...'
