from django.db import models
from django.urls import reverse

class Equipamento(models.Model):
    CATEGORIA_CHOICES = [
        ('computador', 'Computador'),
        ('notebook', 'Notebook'),
        ('impressora', 'Impressora'),
        ('monitor', 'Monitor'),
        ('roteador', 'Roteador'),
        ('switch', 'Switch'),
        ('outro', 'Outro'),
    ]
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('manutencao', 'Em Manutenção'),
        ('inativo', 'Inativo'),
        ('descartado', 'Descartado'),
    ]

    patrimonio = models.CharField('Patrimônio', max_length=50, unique=True)
    hostname = models.CharField('Hostname', max_length=100, blank=True)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES, default='computador')
    marca = models.CharField('Marca', max_length=100)
    modelo = models.CharField('Modelo', max_length=100)
    numero_serie = models.CharField('Número de Série', max_length=100, blank=True)
    processador = models.CharField('Processador', max_length=200, blank=True)
    memoria_ram = models.CharField('Memória RAM', max_length=50, blank=True)
    armazenamento = models.CharField('Armazenamento', max_length=200, blank=True)
    sistema_operacional = models.CharField('Sistema Operacional', max_length=100, blank=True)
    ip = models.GenericIPAddressField('Endereço IP', blank=True, null=True)
    mac_address = models.CharField('MAC Address', max_length=50, blank=True)
    localizacao = models.CharField('Localização', max_length=200)
    responsavel = models.CharField('Responsável', max_length=150, blank=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='ativo')
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'

    def __str__(self):
        return f'{self.patrimonio} - {self.marca} {self.modelo}'

    def get_absolute_url(self):
        return reverse('inventario_detail', args=[self.pk])


class HistoricoEquipamento(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, verbose_name='Usuário')
    acao = models.CharField('Ação', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    criado_em = models.DateTimeField('Data', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Histórico do Equipamento'
        verbose_name_plural = 'Históricos dos Equipamentos'

    def __str__(self):
        return f'{self.equipamento} - {self.acao}'
