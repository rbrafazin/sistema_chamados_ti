from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class HistoricoProduto(models.Model):
    produto = models.ForeignKey('Produto', on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Usuário')
    acao = models.CharField('Ação', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    criado_em = models.DateTimeField('Data', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Histórico do Produto'
        verbose_name_plural = 'Históricos dos Produtos'

    def __str__(self):
        return f'{self.produto} - {self.acao}'


class HistoricoPatrimonio(models.Model):
    patrimonio = models.ForeignKey('Patrimonio', on_delete=models.CASCADE, related_name='historico')
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Usuário')
    acao = models.CharField('Ação', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    criado_em = models.DateTimeField('Data', auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Histórico do Patrimônio'
        verbose_name_plural = 'Históricos dos Patrimônios'

    def __str__(self):
        return f'{self.patrimonio} - {self.acao}'


class Produto(models.Model):
    CATEGORIA_CHOICES = [
        ('alimentos', 'Alimentos'),
        ('limpeza', 'Limpeza'),
        ('escritorio', 'Escritório'),
        ('higiene', 'Higiene'),
        ('descartaveis', 'Descartáveis'),
        ('informatica', 'Informática'),
        ('ferramentas', 'Ferramentas'),
        ('outro', 'Outro'),
    ]

    UNIDADE_CHOICES = [
        ('unidade', 'Unidade'),
        ('caixa', 'Caixa'),
        ('pacote', 'Pacote'),
        ('litro', 'Litro'),
        ('kg', 'Kg'),
        ('metro', 'Metro'),
        ('fardo', 'Fardo'),
        ('galão', 'Galão'),
    ]

    nome = models.CharField('Nome', max_length=200)
    marca = models.CharField('Marca', max_length=100, blank=True)
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES, default='outro')
    unidade_medida = models.CharField('Unidade de Medida', max_length=20, choices=UNIDADE_CHOICES, default='unidade')
    quantidade_estoque = models.IntegerField('Quantidade em Estoque', default=0)
    estoque_minimo = models.IntegerField('Estoque Mínimo', default=0)
    valor_custo = models.DecimalField('Preço de Custo (R$)', max_digits=10, decimal_places=2, default=0)
    descricao = models.TextField('Descrição', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self):
        return self.nome

    @property
    def status_estoque(self):
        if self.quantidade_estoque == 0:
            return 'sem_estoque'
        if self.quantidade_estoque <= self.estoque_minimo:
            return 'baixo'
        return 'normal'

    @property
    def valor_total(self):
        return self.quantidade_estoque * self.valor_custo

    @property
    def unidade_display_plural(self):
        nome = self.get_unidade_medida_display()
        qtd = self.quantidade_estoque
        if qtd == 1:
            return nome
        return {
            'Unidade': 'Unidades', 'Caixa': 'Caixas', 'Pacote': 'Pacotes',
            'Litro': 'Litros', 'Kg': 'Kg', 'Metro': 'Metros',
            'Fardo': 'Fardos', 'Galão': 'Galões',
        }.get(nome, nome + 's')


class Fornecedor(models.Model):
    CATEGORIA_FORNECEDOR_CHOICES = [
        ('material_limpeza', 'Material de Limpeza'),
        ('material_expediente', 'Material de Expediente'),
        ('material_construcao', 'Material de Construção'),
        ('tintas', 'Tintas'),
        ('engenharia_obra', 'Engenharia e Obras'),
        ('madeireira', 'Madeireira'),
        ('vidracaria', 'Vidraçaria e Alumínio'),
        ('marcenaria', 'Marcenaria e Divisórias'),
        ('material_eletrico', 'Material Elétrico e Câmeras'),
        ('eletricista', 'Eletricista'),
        ('ar_condicionado', 'Ar Condicionado'),
        ('poda', 'Serviço de Poda'),
        ('limpeza_carpete', 'Limpeza de Carpete e Cadeiras'),
        ('cadeira_rodas', 'Cadeira de Rodas e Maca'),
        ('manutencao', 'Manutenção'),
        ('grafica', 'Serviço Gráfico'),
        ('prestador_servico', 'Prestador de Serviços'),
    ]

    nome = models.CharField('Nome da Empresa', max_length=200)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True)
    categoria = models.CharField('Categoria', max_length=30, choices=CATEGORIA_FORNECEDOR_CHOICES, default='prestador_servico')
    contato = models.CharField('Vendedor', max_length=100, blank=True)
    telefone = models.CharField('Telefone', max_length=30, blank=True)
    email = models.EmailField('E-mail', blank=True)
    observacoes = models.TextField('Observações', blank=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'

    def __str__(self):
        return self.nome


class ProdutoFornecedor(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='fornecedores')
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE, related_name='produtos')
    preco_unitario = models.DecimalField('Preço Unitário (R$)', max_digits=10, decimal_places=2, default=0)
    quantidade = models.IntegerField('Quantidade', default=0)

    class Meta:
        verbose_name = 'Produto-Fornecedor'
        verbose_name_plural = 'Produtos-Fornecedores'
        unique_together = ['produto', 'fornecedor']

    def __str__(self):
        return f'{self.produto.nome} — {self.fornecedor.nome}'


class Patrimonio(models.Model):
    CATEGORIA_CHOICES = [
        ('moveis', 'Móveis'),
        ('equipamentos', 'Equipamentos'),
        ('informatica', 'Informática'),
        ('eletrodomesticos', 'Eletrodomésticos'),
        ('ferramentas', 'Ferramentas'),
        ('outros', 'Outros'),
    ]

    SITUACAO_CHOICES = [
        ('em_uso', 'Em Uso'),
        ('manutencao', 'Em Manutenção'),
        ('baixado', 'Baixado'),
        ('disponivel', 'Disponível'),
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

    numero_patrimonio = models.CharField('Nº Patrimônio', max_length=50, unique=True)
    nome = models.CharField('Nome do Bem', max_length=200)
    marca = models.CharField('Marca', max_length=100, blank=True)
    modelo = models.CharField('Modelo', max_length=100, blank=True)
    categoria = models.CharField('Categoria', max_length=30, choices=CATEGORIA_CHOICES, default='outros')
    setor = models.CharField('Setor', max_length=200, choices=SETOR_CHOICES, default='apoio')
    responsavel = models.CharField('Responsável', max_length=150, blank=True)
    situacao = models.CharField('Situação', max_length=20, choices=SITUACAO_CHOICES, default='em_uso')
    data_aquisicao = models.DateField('Data de Aquisição', blank=True, null=True)
    valor_aquisicao = models.DecimalField('Valor de Aquisição (R$)', max_digits=12, decimal_places=2, blank=True, null=True)
    descricao = models.TextField('Descrição', blank=True)
    observacoes = models.TextField('Observações', blank=True)
    imagem = models.ImageField('Nota Fiscal', upload_to='apoio/patrimonio/', blank=True, null=True)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Patrimônio'
        verbose_name_plural = 'Patrimônios'

    def __str__(self):
        return f'{self.numero_patrimonio} — {self.nome}'


class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    MOTIVO_CHOICES = [
        ('compra', 'Compra'),
        ('transferencia', 'Transferência'),
        ('perda_avaria', 'Perda / Avaria'),
        ('devolucao_fornecedor', 'Devolução ao fornecedor'),
        ('consumo_interno', 'Consumo interno'),
        ('exclusao_produto', 'Exclusão de produto'),
        ('outro', 'Outro'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='movimentacoes')
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    motivo = models.CharField('Motivo', max_length=30, choices=MOTIVO_CHOICES, blank=True)
    quantidade = models.IntegerField('Quantidade')
    saldo_apos = models.IntegerField('Saldo após', default=0)
    custo = models.DecimalField('Custo (R$)', max_digits=10, decimal_places=2, blank=True, null=True)
    nota_fiscal = models.ImageField('Nota Fiscal', upload_to='apoio/movimentacoes/', blank=True, null=True)
    data_hora = models.DateTimeField('Data/Hora', auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='movimentacoes_apoio')
    observacao = models.TextField('Observação', blank=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Fornecedor')

    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.produto.nome} ({self.quantidade})'
