from django.apps import AppConfig


class ReportesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'reportes'
    verbose_name       = 'Reportes y Bitácora'

    def ready(self):
        import reportes.signals  # noqa: F401 — activa las señales de login/logout