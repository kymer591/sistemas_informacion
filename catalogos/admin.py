from django.contrib import admin
from .models import Grado, Unidad, TipoEstado, TipoSancion, TipoFelicitacion

@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviatura', 'orden', 'activo']
    list_editable = ['orden', 'activo']
    ordering = ['orden']

@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'activa']
    list_editable = ['activa']
    search_fields = ['codigo', 'nombre']

@admin.register(TipoEstado)
class TipoEstadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'color']

@admin.register(TipoSancion)
class TipoSancionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'gravedad', 'activo']
    list_editable = ['activo']
    list_filter = ['gravedad']

@admin.register(TipoFelicitacion)
class TipoFelicitacionAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']