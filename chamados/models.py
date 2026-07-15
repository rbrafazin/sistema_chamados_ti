from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Chamado(models.Model):
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('critica', 'Crítica'),
    ]
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('andamento', 'Em Andamento'),
        ('resolvido', 'Resolvido'),
    ]
    CATEGORIA_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('rede', 'Rede'),
        ('email', 'E-mail'),
        ('impressora', 'Impressora'),
        ('outro', 'Outro'),
    ]
    SETOR_CHOICES = [
        ('apoio', 'APOIO'),
        ('atendimento', 'ATENDIMENTO'),
        ('comunicacao', 'COMUNICAÇÃO'),
        ('consorcio', 'CONSÓRCIO'),
        ('convenios', 'CONVÊNIOS'),
        ('educacao_permanente', 'EDUCAÇÃO PERMANENTE'),
        ('gerencia', 'GERÊNCIA'),
        ('iness', 'INESS'),
        ('nac', 'NAC'),
        ('rh', 'RH'),
        ('secretaria', 'SECRETARIA'),
        ('sinam', 'SINAM'),
        ('ti', 'T.I'),
        ('tesouraria', 'TESOURARIA'),
    ]

    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição')
    solicitante = models.CharField('Solicitante', max_length=150)
    setor = models.CharField('Setor', max_length=100, choices=SETOR_CHOICES, default='ti', blank=True)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES, default='outro')
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='media', blank=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='aberto')
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Técnico Responsável', related_name='chamados_atribuidos')
    observacoes = models.TextField('Observações Técnicas', blank=True)
    imagem_tecnica = models.ImageField('Imagem Técnica', upload_to='chamados/tecnicas/', blank=True, null=True)
    imagem_solicitante = models.ImageField('Imagem do Solicitante', upload_to='chamados/solicitante/', blank=True, null=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='chamados_criados', verbose_name='Criado por')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'

    def __str__(self):
        return f'#{self.pk} - {self.titulo}'

    def get_absolute_url(self):
        return reverse('chamados_detail', args=[self.pk])


class HistoricoChamado(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    acao = models.CharField('Ação', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    criado_em = models.DateTimeField('Data', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Histórico do Chamado'
        verbose_name_plural = 'Históricos dos Chamados'

    def __str__(self):
        return f'{self.chamado} - {self.acao}'
