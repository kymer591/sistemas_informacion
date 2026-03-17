from django.db.models.signals import post_save
from django.dispatch import receiver
from personal.models import PersonalPolicial, KardexDigital
from .models import Usuario


@receiver(post_save, sender=PersonalPolicial)
def crear_usuario_automatico(sender, instance, created, **kwargs):
    """Crea usuario automático para cada nuevo policía"""
    if not created:
        return

    # Evitar duplicados
    if Usuario.objects.filter(personal=instance).exists():
        return
    if Usuario.objects.filter(username=instance.ci).exists():
        Usuario.objects.filter(username=instance.ci).update(personal=instance)
        return

    if not instance.correo_institucional:
        return

    try:
        usuario = Usuario.objects.create(
            username=instance.ci,
            email=instance.correo_institucional,
            first_name=instance.nombres,
            last_name=f"{instance.apellido_paterno} {instance.apellido_materno}",
            telefono=instance.telefono_personal or '',
            rol='usuario_autorizado',
            personal=instance,
            is_active=True
        )
        usuario.set_password(instance.ci[::-1])
        usuario.save()
    except Exception as e:
        print(f"Error creando usuario automático: {e}")


@receiver(post_save, sender=PersonalPolicial)
def crear_kardex_ingreso(sender, instance, created, **kwargs):
    """Crea automáticamente el primer registro de kardex al ingresar personal"""
    if not created:
        return

    # Evitar duplicados por si la señal se dispara más de una vez
    if KardexDigital.objects.filter(
        personal=instance,
        tipo_registro='ingreso'
    ).exists():
        return

    try:
        KardexDigital.objects.create(
            personal=instance,
            tipo_registro='ingreso',
            fecha_registro=instance.fecha_ingreso,
            descripcion=(
                f"Ingreso a la institución. "
                f"Grado: {instance.grado.nombre}. "
                f"Unidad asignada: {instance.unidad.nombre}."
            ),
            grado_nuevo=instance.grado,
            unidad_nueva=instance.unidad,
            estado_nuevo=instance.estado_actual,
            registrado_por=None  # automático, sin usuario
        )
    except Exception as e:
        print(f"Error creando kardex de ingreso: {e}")
