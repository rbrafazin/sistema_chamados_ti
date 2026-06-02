from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
import logging
from .models import Chamado

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Chamado)
def notificar_novo_chamado(sender, instance, created, **kwargs):
    if created:
        url = reverse('chamados_detail', args=[instance.pk])
        assunto = f'[ABM TI] Novo Chamado #{instance.pk} - {instance.titulo}'
        mensagem = f"""
Novo chamado registrado no sistema ABM TI.

#{instance.pk} - {instance.titulo}
Solicitante: {instance.solicitante}
Setor: {instance.setor}
Prioridade: {instance.get_prioridade_display()}
Status: {instance.get_status_display()}

Descrição:
{instance.descricao}

Acesse: {url}
"""
        try:
            send_mail(
                assunto,
                mensagem,
                settings.EMAIL_HOST_USER,
                [settings.NOTIFICACAO_EMAIL],
                fail_silently=False,
            )
        except Exception:
            logger.exception('Erro ao enviar email de notificacao do chamado #%s', instance.pk)
