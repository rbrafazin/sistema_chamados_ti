from django import forms
from .models import Artigo, Categoria


class ArtigoForm(forms.ModelForm):
    class Meta:
        model = Artigo
        fields = ['titulo', 'conteudo', 'categoria']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if hasattr(field.widget, 'attrs'):
                css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{css} {existing}'.strip()
        self.fields['conteudo'].widget.attrs['rows'] = 12
        self.fields['categoria'].required = False
        self.fields['categoria'].empty_label = 'Selecionar...'


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
