from django.db import models
from django.conf import settings

class PersonalPolicial(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    # Información básica
    codigo_identificacion = models.CharField(max_length=20, unique=True)
    ci = models.CharField(max_length=15, unique=True)
    expedido = models.CharField(max_length=5, default='LP')
    nombres = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    
    # Información laboral
    grado = models.ForeignKey('catalogos.Grado', on_delete=models.PROTECT)
    unidad = models.ForeignKey('catalogos.Unidad', on_delete=models.PROTECT)
    estado_actual = models.ForeignKey('catalogos.TipoEstado', on_delete=models.PROTECT)
    fecha_ingreso = models.DateField()
    
    # Contacto
    telefono_personal = models.CharField(max_length=15, blank=True, null=True)
    telefono_emergencia = models.CharField(max_length=15, blank=True, null=True)
    correo_institucional = models.EmailField(blank=True, null=True)
    
    # Control
    foto = models.ImageField(upload_to='personal/fotos/', blank=True, null=True)
    qr_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Personal Policial'
        verbose_name_plural = 'Personal Policial'
        ordering = ['grado__orden', 'apellido_paterno']

    def __str__(self):
        return f"{self.grado.abreviatura} {self.nombres} {self.apellido_paterno}"

    def nombre_completo(self):
        return f"{self.nombres} {self.apellido_paterno} {self.apellido_materno}"

class KardexDigital(models.Model):
    TIPO_REGISTRO_CHOICES = [
        ('ingreso', 'Ingreso a la Institución'),
        ('ascenso', 'Ascenso de Grado'),
        ('traslado', 'Traslado de Unidad'),
        ('estado', 'Cambio de Estado'),
        ('sancion', 'Sanción Aplicada'),
        ('felicitacion', 'Felicitación'),
        ('permiso', 'Permiso o Licencia'),
        ('otro', 'Otro'),
    ]

    personal = models.ForeignKey(PersonalPolicial, on_delete=models.CASCADE, related_name='kardex')
    tipo_registro = models.CharField(max_length=15, choices=TIPO_REGISTRO_CHOICES)
    fecha_registro = models.DateField()
    descripcion = models.TextField()
    documento_referencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Campos específicos según tipo
    grado_anterior = models.ForeignKey('catalogos.Grado', on_delete=models.SET_NULL, null=True, blank=True, related_name='kardex_anterior')
    grado_nuevo = models.ForeignKey('catalogos.Grado', on_delete=models.SET_NULL, null=True, blank=True, related_name='kardex_nuevo')
    unidad_anterior = models.ForeignKey('catalogos.Unidad', on_delete=models.SET_NULL, null=True, blank=True, related_name='kardex_anterior')
    unidad_nueva = models.ForeignKey('catalogos.Unidad', on_delete=models.SET_NULL, null=True, blank=True, related_name='kardex_nuevo')
    estado_anterior = models.ForeignKey('catalogos.TipoEstado', on_delete=models.SET_NULL, null=True, blank=True, related_name='kardex_anterior')
    estado_nuevo = models.ForeignKey('catalogos.TipoEstado', on_delete=models.SET_NULL, null=True, blank=True, related_name='kardex_nuevo')
    
    # Control - CORREGIDO
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Registro de Kardex'
        verbose_name_plural = 'Registros de Kardex'
        ordering = ['-fecha_registro', '-fecha_creacion']

    def __str__(self):
        return f"Kardex {self.personal} - {self.get_tipo_registro_display()}"

class PermisoLicencia(models.Model):
    TIPO_PERMISO_CHOICES = [
        ('administrativo', 'Permiso Administrativo'),
        ('medico', 'Permiso Médico'),
        ('personal', 'Permiso Personal'),
        ('comision', 'Comisión de Servicio'),
        ('vacaciones', 'Vacaciones'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]

    personal = models.ForeignKey(PersonalPolicial, on_delete=models.CASCADE, related_name='permisos')
    tipo_permiso = models.CharField(max_length=15, choices=TIPO_PERMISO_CHOICES)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_solicitados = models.IntegerField(editable=False)
    motivo = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    
    # Aprobación - CORREGIDO
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='permisos_aprobados')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    observaciones_aprobacion = models.TextField(blank=True, null=True)
    
    # Documentación
    documento_adjunto = models.FileField(upload_to='permisos/documentos/', blank=True, null=True)
    numero_oficio = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = 'Permiso o Licencia'
        verbose_name_plural = 'Permisos y Licencias'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Permiso {self.personal} - {self.get_tipo_permiso_display()}"

    def save(self, *args, **kwargs):
        if self.fecha_inicio and self.fecha_fin:
            delta = self.fecha_fin - self.fecha_inicio
            self.dias_solicitados = delta.days + 1
        super().save(*args, **kwargs)

class SancionAplicada(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('cumplida', 'Cumplida'),
        ('anulada', 'Anulada'),
    ]

    personal = models.ForeignKey(PersonalPolicial, on_delete=models.CASCADE, related_name='sanciones_aplicadas')
    tipo_sancion = models.ForeignKey('catalogos.TipoSancion', on_delete=models.PROTECT)
    fecha_sancion = models.DateField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    motivo = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activa')
    observaciones = models.TextField(blank=True, null=True)
    documento_referencia = models.CharField(max_length=100, blank=True, null=True)
    
    # Control - CORREGIDO
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Sanción Aplicada'
        verbose_name_plural = 'Sanciones Aplicadas'
        ordering = ['-fecha_sancion']

    def __str__(self):
        return f"Sanción {self.personal} - {self.tipo_sancion.nombre}"

class FelicitacionAplicada(models.Model):
    personal = models.ForeignKey(PersonalPolicial, on_delete=models.CASCADE, related_name='felicitaciones_aplicadas')
    tipo_felicitacion = models.ForeignKey('catalogos.TipoFelicitacion', on_delete=models.PROTECT)
    fecha_felicitacion = models.DateField()
    motivo = models.TextField()
    documento_referencia = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    
    # Control - CORREGIDO
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Felicitación Aplicada'
        verbose_name_plural = 'Felicitaciones Aplicadas'
        ordering = ['-fecha_felicitacion']

    def __str__(self):
        return f"Felicitación {self.personal} - {self.tipo_felicitacion.nombre}"