from django import forms
from .models import Produto, Fornecedor, Patrimonio


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome', 'marca', 'categoria', 'unidade_medida', 'quantidade_estoque', 'estoque_minimo', 'valor_custo', 'descricao', 'observacoes']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
        if not self.instance.pk:
            self.fields['categoria'].choices = [('', 'Selecionar...')] + [(k, v) for k, v in self.fields['categoria'].choices if k]
            self.fields['categoria'].initial = ''
            del self.fields['quantidade_estoque']
            del self.fields['valor_custo']
        else:
            self.fields['quantidade_estoque'].disabled = True
            self.fields['valor_custo'].disabled = True


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'cnpj', 'categoria', 'contato', 'telefone', 'email', 'observacoes']
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
            self.fields['categoria'].choices = [('', 'Selecionar...')] + [(k, v) for k, v in self.fields['categoria'].choices if k]
            self.fields['categoria'].initial = ''


class PatrimonioForm(forms.ModelForm):
    class Meta:
        model = Patrimonio
        fields = ['numero_patrimonio', 'nome', 'marca', 'modelo', 'categoria', 'setor', 'responsavel', 'situacao', 'data_aquisicao', 'valor_aquisicao', 'descricao', 'observacoes', 'imagem']
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'data_aquisicao': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} {existing}'.strip()
