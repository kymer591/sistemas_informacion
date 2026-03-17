from django.db import models
from django.conf import settings


class BitacoraLog(models.Model):

    ACCION_CHOICES = [
        ('LOGIN',    '🔐 Inicio de sesión'),
        ('LOGOUT',   '🚪 Cierre de sesión'),
        ('CREAR',    '➕ Crear'),
        ('EDITAR',   '✏️ Editar'),
        ('ELIMINAR', '🗑️ Eliminar'),
        ('VER',      '👁️ Ver'),
        ('ERROR',    '❌ Error'),
        ('OTRO',     '⚙️ Otro'),
    ]

    MODULO_CHOICES = [
        ('personal',      'Personal'),
        ('destinos',      'Destinos'),
        ('catalogos',     'Catálogos'),
        ('permisos',      'Permisos'),
        ('sanciones',     'Sanciones'),
        ('felicitaciones','Felicitaciones'),
        ('kardex',        'Kardex'),
        ('usuarios',      'Usuarios'),
        ('reportes',      'Reportes'),
        ('sistema',       'Sistema'),
    ]

    usuario     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='logs',
        verbose_name='Usuario'
    )
    accion      = models.CharField(max_length=20, choices=ACCION_CHOICES, verbose_name='Acción')
    modulo      = models.CharField(max_length=30, choices=MODULO_CHOICES, default='sistema', verbose_name='Módulo')
    descripcion = models.TextField(verbose_name='Descripción')
    objeto_id   = models.CharField(max_length=50, blank=True, null=True, verbose_name='ID del objeto')
    objeto_repr = models.CharField(max_length=300, blank=True, null=True, verbose_name='Objeto afectado')
    ip_address  = models.GenericIPAddressField(blank=True, null=True, verbose_name='Dirección IP')
    fecha_hora  = models.DateTimeField(auto_now_add=True, verbose_name='Fecha y hora')

    class Meta:
        verbose_name        = 'Log de bitácora'
        verbose_name_plural = 'Bitácora / Logs'
        ordering            = ['-fecha_hora']

    def __str__(self):
        usuario = self.usuario.username if self.usuario else 'Sistema'
        return f"[{self.fecha_hora:%d/%m/%Y %H:%M}] {usuario} — {self.get_accion_display()} en {self.modulo}"

    @property
    def accion_color(self):
        colores = {
            'LOGIN':    'success',
            'LOGOUT':   'secondary',
            'CREAR':    'primary',
            'EDITAR':   'warning',
            'ELIMINAR': 'danger',
            'VER':      'info',
            'ERROR':    'dark',
            'OTRO':     'light',
        }
        return colores.get(self.accion, 'secondary')