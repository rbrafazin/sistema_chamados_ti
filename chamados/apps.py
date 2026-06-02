from django.apps import AppConfig


class ChamadosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chamados'
    verbose_name = 'Chamados'

    def ready(self):
        import chamados.signals
