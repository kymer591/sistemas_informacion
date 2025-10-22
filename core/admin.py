from django.contrib import admin
from .models import SistemaConfig

@admin.register(SistemaConfig)
class SistemaConfigAdmin(admin.ModelAdmin):
    list_display = ['nombre_institucion', 'mantenimiento', 'tiempo_sesion']
    list_editable = ['mantenimiento']