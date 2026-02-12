# core/signals.py (crea este archivo)
from django.db.models.signals import post_save
from django.dispatch import receiver
from personal.models import PersonalPolicial
from .models import Usuario

@receiver(post_save, sender=PersonalPolicial)
def crear_usuario_automatico(sender, instance, created, **kwargs):
    """Crea usuario automático para cada nuevo policía"""
    if created and instance.correo_institucional:
        try:
            # Verificar si ya existe usuario para este personal
            if not hasattr(instance, 'usuario_acceso'):
                # Generar username único (CI o código)
                username = f"{instance.ci}"
                
                # Crear usuario con contraseña temporal
                usuario = Usuario.objects.create(
                    username=username,
                    email=instance.correo_institucional,
                    first_name=instance.nombres,
                    last_name=f"{instance.apellido_paterno} {instance.apellido_materno}",
                    telefono=instance.telefono_personal or '',
                    rol='usuario_autorizado',  # Rol mínimo por defecto
                    personal=instance,
                    is_active=True
                )
                
                # Contraseña temporal: CI invertido
                password = instance.ci[::-1]
                usuario.set_password(password)
                usuario.save()
        except Exception as e:
            print(f"Error creando usuario automático: {e}")