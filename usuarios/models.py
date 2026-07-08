from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    CARGO_CHOICES = [
        ('ti', 'TI'),
        ('usuario', 'Usuário'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cargo = models.CharField('Cargo', max_length=20, choices=CARGO_CHOICES, default='usuario')
    telefone = models.CharField('Ramal', max_length=20, blank=True)
    setor = models.CharField('Setor', max_length=100, default='TI')
    avatar = models.ImageField('Avatar', upload_to='usuarios/avatares/', blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'Perfil de {self.usuario.get_full_name() or self.usuario.username}'


@receiver(post_save, sender=User)
def gerenciar_perfil_usuario(sender, instance, created, **kwargs):
    Perfil.objects.get_or_create(usuario=instance)
