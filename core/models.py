from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('encargado', 'Encargado de Información'),
        ('policial', 'Usuario Policial'),
    ]
    
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='policial')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    unidad = models.ForeignKey('catalogos.Unidad', on_delete=models.SET_NULL, null=True, blank=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    def es_administrador(self):
        return self.rol == 'admin'
    
    def es_encargado(self):
        return self.rol == 'encargado'
    
    def es_policial(self):
        return self.rol == 'policial'

class SistemaConfig(models.Model):
    nombre_institucion = models.CharField(max_length=200, default='UTEPPI')
    logo_url = models.CharField(max_length=500, blank=True, null=True)
    tiempo_sesion = models.IntegerField(default=60, help_text='Minutos de inactividad para cerrar sesión')
    mantenimiento = models.BooleanField(default=False, help_text='Activar modo mantenimiento')
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return f"Configuración - {self.nombre_institucion}"

    def save(self, *args, **kwargs):
        if SistemaConfig.objects.exists() and not self.pk:
            return
        super().save(*args, **kwargs)