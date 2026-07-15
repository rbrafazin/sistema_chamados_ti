from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Categoria(models.Model):
    nome = models.CharField('Nome', max_length=100)
    descricao = models.TextField('Descrição', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome


class Artigo(models.Model):
    titulo = models.CharField('Título', max_length=200)
    conteudo = models.TextField('Conteúdo')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='artigos')
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='artigos')
    anexo = models.FileField('Anexo', upload_to='conhecimento/anexos/', blank=True, null=True)
    visualizacoes = models.PositiveIntegerField('Visualizações', default=0)
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-visualizacoes', '-atualizado_em']
        verbose_name = 'Artigo'
        verbose_name_plural = 'Artigos'

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('conhecimento_detail', args=[self.pk])
