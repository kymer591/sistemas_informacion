from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado con sistema de roles
    
    Roles disponibles:
    - admin: Administrador del sistema (acceso completo)
    - oficial_administrativo: Oficial Administrativo (gestión de personal y catálogos)
    - usuario_autorizado: Usuario Autorizado (solo consulta)
    """
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('oficial_administrativo', 'Oficial Administrativo'),
        ('usuario_autorizado', 'Usuario Autorizado'),
    ]

    
    rol = models.CharField(
        max_length=25, 
        choices=ROL_CHOICES, 
        default='usuario_autorizado',
        help_text='Define el nivel de acceso del usuario en el sistema'
    )
    telefono = models.CharField(max_length=15, blank=True, null=True)
    unidad = models.ForeignKey(
        'catalogos.Unidad', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    personal = models.OneToOneField(
        'personal.PersonalPolicial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuario_acceso',
        verbose_name='Personal vinculado'
    )

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
        """Retorna True si el usuario es administrador"""
        return self.rol == 'admin'
    
    def es_oficial_administrativo(self):
        """Retorna True si el usuario es oficial administrativo"""
        return self.rol == 'oficial_administrativo'
    
    def es_usuario_autorizado(self):
        """Retorna True si el usuario es usuario autorizado"""
        return self.rol == 'usuario_autorizado'
    
    def puede_crear(self):
        """Retorna True si el usuario puede crear registros"""
        return self.rol in ['admin', 'oficial_administrativo']
    
    def puede_editar(self):
        """Retorna True si el usuario puede editar registros"""
        return self.rol in ['admin', 'oficial_administrativo']
    
    def puede_eliminar(self):
        """Retorna True si el usuario puede eliminar registros"""
        return self.rol == 'admin'
    
    def puede_consultar(self):
        """Retorna True si el usuario puede consultar registros"""
        return True  # Todos los roles autenticados pueden consultar
    
    def puede_gestionar_usuarios(self):
        """Retorna True si el usuario puede gestionar otros usuarios"""
        return self.rol == 'admin'
    
    def puede_aprobar_permisos(self):
        """Retorna True si el usuario puede aprobar permisos"""
        return self.rol in ['admin', 'oficial_administrativo']
    
    def puede_gestionar_sanciones(self):
        """Retorna True si el usuario puede gestionar sanciones"""
        return self.rol in ['admin', 'oficial_administrativo']


class SistemaConfig(models.Model):
    nombre_institucion = models.CharField(max_length=200, default='UTEPPI')
    logo_url = models.CharField(max_length=500, blank=True, null=True)
    tiempo_sesion = models.IntegerField(
        default=60, 
        help_text='Minutos de inactividad para cerrar sesión'
    )
    mantenimiento = models.BooleanField(
        default=False, 
        help_text='Activar modo mantenimiento'
    )
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return f"Configuración - {self.nombre_institucion}"

    def save(self, *args, **kwargs):
        if SistemaConfig.objects.exists() and not self.pk:
            return
        super().save(*args, **kwargs)