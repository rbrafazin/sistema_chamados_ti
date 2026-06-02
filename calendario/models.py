from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    TIPO_CHOICES = [
        ('manutencao', 'Manutenção'),
        ('visita', 'Visita Técnica'),
        ('backup', 'Backup'),
        ('vencimento', 'Vencimento'),
        ('reuniao', 'Reunião'),
        ('outro', 'Outro'),
    ]
    COR_CHOICES = [
        ('#0d6efd', 'Azul'),
        ('#dc3545', 'Vermelho'),
        ('#198754', 'Verde'),
        ('#ffc107', 'Amarelo'),
        ('#6f42c1', 'Roxo'),
        ('#fd7e14', 'Laranja'),
    ]

    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='outro')
    cor = models.CharField('Cor', max_length=7, choices=COR_CHOICES, default='#0d6efd')
    data_inicio = models.DateTimeField('Data/Hora Início')
    data_fim = models.DateTimeField('Data/Hora Fim')
    dia_todo = models.BooleanField('Dia todo', default=False)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_inicio']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return self.titulo
