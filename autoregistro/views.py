from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db import transaction

from core.models import Usuario
from personal.models import PersonalPolicial
from reportes.utils import registrar_log
from .models import RegistroTemporal
from .forms import CompletarRegistroForm


# ══════════════════════════════════════════════════════════════════
#  ADMINISTRATIVO — Crear usuario temporal desde personal_detail
# ══════════════════════════════════════════════════════════════════

@login_required
@require_POST
def crear_usuario_temporal(request, personal_id):
    """
    Crea el usuario temporal desde el modal en personal_detail.html.
    """
    if not (request.user.puede_crear() or request.user.es_administrador()):
        messages.error(request, '❌ No tienes permisos para realizar esta acción.')
        return redirect('personal_detail', pk=personal_id)

    personal = get_object_or_404(PersonalPolicial, pk=personal_id)

    # Verificar que no tenga ya un usuario vinculado
    if hasattr(personal, 'usuario_acceso') and personal.usuario_acceso:
        messages.warning(
            request,
            f'⚠️ {personal.nombre_completo()} ya tiene un usuario asignado '
            f'({personal.usuario_acceso.username}).'
        )
        return redirect('personal_detail', pk=personal_id)

    # Verificar que no exista ya un usuario con ese CI
    if Usuario.objects.filter(username=personal.ci).exists():
        messages.error(
            request,
            f'❌ Ya existe un usuario con el nombre "{personal.ci}". '
            f'Usa "Asignar Rol" para vincularlo manualmente.'
        )
        return redirect('personal_detail', pk=personal_id)

    with transaction.atomic():
        password = request.POST.get('password', '').strip() or personal.ci[::-1]

        usuario = Usuario.objects.create(
            username   = personal.ci,
            first_name = personal.nombres,
            last_name  = f"{personal.apellido_paterno} {personal.apellido_materno}",
            email      = personal.correo_institucional or '',
            rol        = 'temporal',
            personal   = personal,
            is_active  = True,
            activo     = True,
        )
        usuario.set_password(password)
        usuario.save()

        RegistroTemporal.objects.create(
            personal   = personal,
            usuario    = usuario,
            creado_por = request.user,
        )

        registrar_log(
            request, 'CREAR', 'personal',
            f'Habilitó autoregistro temporal para {personal} '
            f'— usuario: {usuario.username}',
            objeto=personal,
        )

    messages.success(
        request,
        f'✅ Usuario temporal creado. '
        f'Usuario: <strong>{personal.ci}</strong> — '
        f'Contraseña: <strong>{password}</strong>. '
        f'Entrégasela al policía para que complete su registro.'
    )
    return redirect('personal_detail', pk=personal_id)


# ══════════════════════════════════════════════════════════════════
#  ADMINISTRATIVO — Lista y revisión de registros temporales
# ══════════════════════════════════════════════════════════════════

@login_required
def lista_temporales(request):
    """Lista de todos los registros temporales."""
    if not request.user.puede_crear():
        messages.error(request, '❌ Acceso denegado.')
        return redirect('dashboard')

    estado = request.GET.get('estado', '')
    qs = RegistroTemporal.objects.select_related(
        'personal__grado', 'personal__unidad', 'usuario', 'creado_por'
    )
    if estado:
        qs = qs.filter(estado=estado)

    pendientes  = RegistroTemporal.objects.filter(estado='pendiente').count()
    completados = RegistroTemporal.objects.filter(estado='completado').count()

    return render(request, 'autoregistro/lista_temporales.html', {
        'registros'  : qs,
        'estado_sel' : estado,
        'pendientes' : pendientes,
        'completados': completados,
    })


@login_required
def revisar_registro(request, pk):
    """
    El administrativo revisa lo que completó el policía.
    Puede editar directamente antes de aprobar o rechazar.
    """
    if not request.user.puede_editar():
        messages.error(request, '❌ No tienes permisos para revisar registros.')
        return redirect('dashboard')

    reg      = get_object_or_404(RegistroTemporal, pk=pk)
    personal = reg.personal

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'aprobar':
            form = CompletarRegistroForm(request.POST, request.FILES, instance=personal)
            if form.is_valid():
                with transaction.atomic():
                    form.save()

                    # Promover a cuenta normal
                    reg.usuario.rol    = 'usuario_autorizado'
                    reg.usuario.activo = True
                    reg.usuario.save(update_fields=['rol', 'activo'])

                    reg.estado            = 'aprobado'
                    reg.revisado_por      = request.user
                    reg.fecha_aprobacion  = timezone.now()
                    reg.observaciones_rev = request.POST.get('observaciones_rev', '')
                    reg.save()

                    registrar_log(
                        request, 'EDITAR', 'personal',
                        f'Aprobó registro temporal de {personal}',
                        objeto=reg,
                    )
                messages.success(
                    request,
                    f'✅ Registro de {personal.nombre_completo()} aprobado. '
                    f'Su cuenta es ahora Usuario Autorizado.'
                )
                return redirect('autoregistro:lista_temporales')
            # Si el form tiene errores, caer al GET y mostrarlos
        
        elif accion == 'rechazar':
            with transaction.atomic():
                reg.estado            = 'rechazado'
                reg.revisado_por      = request.user
                reg.fecha_aprobacion  = timezone.now()
                reg.observaciones_rev = request.POST.get('observaciones_rev', '')
                reg.save()

                reg.usuario.activo = False
                reg.usuario.save(update_fields=['activo'])

                registrar_log(
                    request, 'EDITAR', 'personal',
                    f'Rechazó registro temporal de {personal}',
                    objeto=reg,
                )
            messages.warning(
                request,
                f'⚠️ Registro de {personal.nombre_completo()} rechazado.'
            )
            return redirect('autoregistro:lista_temporales')

    form = CompletarRegistroForm(instance=personal)
    return render(request, 'autoregistro/revisar_registro.html', {
        'reg'     : reg,
        'personal': personal,
        'form'    : form,
    })


# ══════════════════════════════════════════════════════════════════
#  POLICÍA — Completar su propio registro (rol temporal)
# ══════════════════════════════════════════════════════════════════

@login_required
def completar_registro(request):
    """
    Vista exclusiva para usuarios con rol 'temporal'.
    Al iniciar sesión son redirigidos aquí automáticamente.
    """
    if request.user.rol != 'temporal':
        return redirect('dashboard')

    try:
        reg      = request.user.registro_temporal
        personal = reg.personal
    except Exception:
        messages.error(request, '❌ No se encontró tu registro. Contacta al administrador.')
        return redirect('login')

    # Ya completó — mostrar pantalla de espera
    if reg.estado == 'completado':
        return render(request, 'autoregistro/espera_aprobacion.html', {
            'personal': personal,
            'reg'     : reg,
        })

    if request.method == 'POST':
        form = CompletarRegistroForm(request.POST, request.FILES, instance=personal)
        if form.is_valid():
            form.save()
            reg.estado           = 'completado'
            reg.fecha_completado = timezone.now()
            reg.save(update_fields=['estado', 'fecha_completado'])
            messages.success(request, '✅ Tu información fue enviada. Espera la aprobación.')
            return redirect('autoregistro:completar_registro')
    else:
        form = CompletarRegistroForm(instance=personal)

    return render(request, 'autoregistro/completar_registro.html', {
        'form'    : form,
        'personal': personal,
        'reg'     : reg,
    })