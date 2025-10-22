from django.db import models

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
        # Asegurar que solo exista una configuración
        if SistemaConfig.objects.exists() and not self.pk:
            return
        super().save(*args, **kwargs)