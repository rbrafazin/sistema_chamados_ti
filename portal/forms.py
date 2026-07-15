from django import forms
from chamados.models import Chamado


class PortalChamadoForm(forms.ModelForm):
    imagem = forms.ImageField(label='Anexar imagem', required=False)

    class Meta:
        model = Chamado
        fields = ['titulo', 'descricao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'imagem':
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
        self.fields['descricao'].widget.attrs['rows'] = 4
