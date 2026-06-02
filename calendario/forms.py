from django import forms
from datetime import timedelta
from .models import Evento


class EventoForm(forms.ModelForm):
    data = forms.DateField(label='Data', required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Evento
        fields = ['titulo', 'descricao', 'tipo', 'data_inicio', 'data_fim', 'dia_todo']
        widgets = {
            'data_inicio': forms.HiddenInput(),
            'data_fim': forms.HiddenInput(),
            'dia_todo': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_inicio'].required = False
        self.fields['data_fim'].required = False
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs') and field.widget.__class__.__name__ != 'HiddenInput':
                css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{css} {existing}'.strip()
        if self.instance and self.instance.pk:
            self.fields['data'].initial = self.instance.data_inicio.date()

    def clean(self):
        cleaned = super().clean()
        data = cleaned.get('data')
        if data:
            from datetime import datetime
            dt = datetime.combine(data, datetime.min.time())
            cleaned['data_inicio'] = dt
            cleaned['data_fim'] = dt + timedelta(hours=1)
        return cleaned
