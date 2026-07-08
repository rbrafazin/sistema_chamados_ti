from django import forms
from .models import Artigo, Categoria, Tag


class ArtigoForm(forms.ModelForm):
    tags_input = forms.CharField(label='Tags', required=False, help_text='Separe as tags por vírgula', widget=forms.TextInput(attrs={'placeholder': 'Ex: windows, rede, impressora'}))

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
        if self.instance and self.instance.pk:
            self.fields['tags_input'].initial = ', '.join(t.nome for t in self.instance.tags.all())

    def save(self, commit=True):
        artigo = super().save(commit=False)
        if commit:
            artigo.save()
            self.save_m2m()
            self._save_tags(artigo)
        return artigo

    def _save_tags(self, artigo):
        tag_names = [t.strip().lower() for t in self.cleaned_data.get('tags_input', '').split(',') if t.strip()]
        artigo.tags.clear()
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(nome=name)
            artigo.tags.add(tag)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'descricao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
