from django import forms
from .models import Equipamento

class EquipamentoForm(forms.ModelForm):
    class Meta:
        model = Equipamento
        fields = [
            'patrimonio', 'hostname', 'categoria', 'marca', 'modelo',
            'numero_serie', 'processador', 'memoria_ram', 'armazenamento',
            'sistema_operacional', 'ip', 'mac_address', 'localizacao',
            'responsavel', 'status', 'observacoes',
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
