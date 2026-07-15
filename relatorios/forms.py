from django import forms
from datetime import datetime
from inventario.models import Equipamento


class MesAnoFilterForm(forms.Form):
    MESES = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro'),
    ]

    hoje = datetime.now()
    mes = forms.ChoiceField(choices=MESES, initial=hoje.month, label='', required=False)
    ano = forms.ChoiceField(
        choices=[(y, str(y)) for y in range(2024, hoje.year + 2)],
        initial=hoje.year, label='', required=False
    )
    setor = forms.ChoiceField(choices=[('', 'Setor...')] + Equipamento.SETOR_CHOICES, label='', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-select form-select-sm'
            field.widget.attrs['style'] = 'width:auto;'
