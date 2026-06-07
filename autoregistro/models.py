from django.db import models
from django.conf import settings


class RegistroTemporal(models.Model):
    """
    Registro incompleto creado por el administrativo.
    El policía lo completa al iniciar sesión con su usuario temporal.
    Una vez aprobado, el usuario pasa a ser cuenta normal.
    """
    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente — esperando que el policía complete sus datos'),
        ('completado', 'Completado — esperando revisión del administrativo'),
        ('aprobado',   'Aprobado — cuenta activada como normal'),
        ('rechazado',  'Rechazado'),
    ]

    personal   = models.OneToOneField(
        'personal.PersonalPolicial',
        on_delete=models.CASCADE,
        related_name='registro_temporal',
    )
    usuario    = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='registro_temporal',
    )
    estado     = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='pendiente')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_creados',
    )
    revisado_por      = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='registros_revisados',
    )
    observaciones_rev = models.TextField(blank=True, null=True)
    fecha_creacion    = models.DateTimeField(auto_now_add=True)
    fecha_completado  = models.DateTimeField(null=True, blank=True)
    fecha_aprobacion  = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name        = 'Registro Temporal'
        verbose_name_plural = 'Registros Temporales'
        ordering            = ['-fecha_creacion']

    def __str__(self):
        return f"RegistroTemp {self.personal} — {self.get_estado_display()}"

    def es_pendiente(self):
        return self.estado == 'pendiente'

    def es_completado(self):
        return self.estado == 'completado'