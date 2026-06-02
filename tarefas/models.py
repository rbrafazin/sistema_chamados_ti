from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Tarefa(models.Model):
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    STATUS_CHOICES = [
        ('a_fazer', 'A Fazer'),
        ('andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
    ]

    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='a_fazer')
    responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Responsável', related_name='tarefas')
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tarefas_criadas', verbose_name='Criado por')
    prazo = models.DateField('Prazo', blank=True, null=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('tarefas_kanban')
