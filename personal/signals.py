from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import (
    SancionAplicada,
    FelicitacionAplicada,
    DestinoPolicial,
    PermisoLicencia,
    KardexDigital,
)


@receiver(post_save, sender=SancionAplicada)
def kardex_desde_sancion(sender, instance, created, **kwargs):
    if not created:
        return
    KardexDigital.objects.create(
        personal=instance.personal,
        tipo_registro='sancion',
        fecha_registro=instance.fecha_sancion,
        descripcion=f"Sanción aplicada: {instance.tipo_sancion.nombre}. {instance.motivo}",
        documento_referencia=instance.documento_referencia,
        observaciones=instance.observaciones,
        registrado_por=instance.registrado_por,
    )


@receiver(post_save, sender=FelicitacionAplicada)
def kardex_desde_felicitacion(sender, instance, created, **kwargs):
    if not created:
        return
    KardexDigital.objects.create(
        personal=instance.personal,
        tipo_registro='felicitacion',
        fecha_registro=instance.fecha_felicitacion,
        descripcion=f"Felicitación: {instance.tipo_felicitacion.nombre}. {instance.motivo}",
        documento_referencia=instance.documento_referencia,
        observaciones=instance.observaciones,
        registrado_por=instance.registrado_por,
    )


@receiver(post_save, sender=DestinoPolicial)
def kardex_desde_destino(sender, instance, created, **kwargs):
    if not created:
        return
    KardexDigital.objects.create(
        personal=instance.personal,
        tipo_registro='traslado',
        fecha_registro=instance.fecha_inicio,
        descripcion=f"{instance.get_tipo_destino_display()}: {instance.lugar_destino}. {instance.descripcion}",
        documento_referencia=instance.numero_resolucion,
        observaciones=instance.observaciones,
        unidad_nueva=instance.unidad_destino,
        registrado_por=instance.registrado_por,
    )


@receiver(post_save, sender=PermisoLicencia)
def kardex_desde_permiso_aprobado(sender, instance, created, **kwargs):
    if instance.estado != 'aprobado':
        return

    marcador = f'PERMISO-{instance.pk}'
    ya_existe = KardexDigital.objects.filter(
        personal=instance.personal,
        tipo_registro='permiso',
        documento_referencia=marcador,
    ).exists()
    if ya_existe:
        return

    KardexDigital.objects.create(
        personal=instance.personal,
        tipo_registro='permiso',
        fecha_registro=instance.fecha_inicio,
        descripcion=(
            f"{instance.get_tipo_permiso_display()} aprobado: "
            f"{instance.fecha_inicio} al {instance.fecha_fin} "
            f"({instance.dias_solicitados} días)."
        ),
        documento_referencia=marcador,
        observaciones=instance.observaciones_aprobacion,
        registrado_por=instance.aprobado_por,
    )
from .models import BajaPersonal, Fallecimiento


@receiver(post_save, sender=BajaPersonal)
def al_registrar_baja(sender, instance, created, **kwargs):
    if not created:
        return
    instance.personal.activo = False
    instance.personal.save(update_fields=['activo'])
    KardexDigital.objects.create(
        personal=instance.personal,
        tipo_registro='estado',
        fecha_registro=instance.fecha_baja,
        descripcion=f"{instance.get_tipo_baja_display()}. {instance.motivo or ''}".strip(),
        documento_referencia=instance.resolucion_tds,
        observaciones=instance.observaciones,
        registrado_por=instance.registrado_por,
    )


@receiver(post_save, sender=Fallecimiento)
def al_registrar_fallecimiento(sender, instance, created, **kwargs):
    if not created:
        return
    instance.personal.activo = False
    instance.personal.save(update_fields=['activo'])
    KardexDigital.objects.create(
        personal=instance.personal,
        tipo_registro='estado',
        fecha_registro=instance.fecha_fallecimiento,
        descripcion=f"Fallecimiento. {instance.causa_deceso or ''}".strip(),
        documento_referencia=instance.numero_certificado_defuncion,
        observaciones=instance.observaciones,
        registrado_por=instance.registrado_por,
    )