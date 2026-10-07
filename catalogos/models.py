from django.db import models

class Grado(models.Model):
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=15)
    orden = models.IntegerField(help_text="Orden jerárquico (1 = mayor grado)")
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"

class Unidad(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    ciudad = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    correo_electronico = models.EmailField(blank=True, null=True)
    comandante = models.ForeignKey(
        'personal.PersonalPolicial',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='unidades_comandadas',
        help_text='Personal designado como comandante de esta unidad'
    )

    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Cargo(models.Model):
    unidad = models.ForeignKey(Unidad, on_delete=models.CASCADE, related_name='cargos')
    nombre = models.CharField(max_length=150)
    orden = models.IntegerField(default=0, help_text='Orden de aparición en los reportes')
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['unidad', 'orden']

    def __str__(self):
        return f"{self.nombre} ({self.unidad.codigo})"


class TipoEstado(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#007bff', help_text='Color en HEX')
    cumple_funciones = models.BooleanField(
        default=True,
        verbose_name='¿Cumple funciones en la unidad?',
        help_text='Desmarcar para estados como Retiro Temporal, Comisión, Baja Definitiva, Fallecido, etc.'
    )
    
    class Meta:
        verbose_name = 'Tipo de Estado'
        verbose_name_plural = 'Tipos de Estado'
    
    def __str__(self):
        return self.nombre

class TipoSancion(models.Model):
    GRAVEDAD_CHOICES = [
        ('leve', 'Leve'),
        ('grave', 'Grave'),
        ('muy_grave', 'Muy Grave'),
    ]
    
    nombre = models.CharField(max_length=100)
    gravedad = models.CharField(max_length=10, choices=GRAVEDAD_CHOICES)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tipo de Sanción'
        verbose_name_plural = 'Tipos de Sanción'
    
    def __str__(self):
        return f"{self.nombre} ({self.get_gravedad_display()})"

class TipoFelicitacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Tipo de Felicitación'
        verbose_name_plural = 'Tipos de Felicitación'
    
    def __str__(self):
        return self.nombre