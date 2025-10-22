from django.db import models

class Grado(models.Model):
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=10)
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
    
    class Meta:
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class TipoEstado(models.Model):
    nombre = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#007bff', help_text='Color en HEX')
    
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
