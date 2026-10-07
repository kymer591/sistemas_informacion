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
from .forms import CrearTemporalForm, CompletarRegistroForm


# ══════════════════════════════════════════════════════════════════
#  ADMINISTRATIVO — Crear usuario temporal (solo CI + nombre)
# ══════════════════════════════════════════════════════════════════

@login_required
def crear_temporal(request):
    if not request.user.puede_crear():
        messages.error(request, '❌ No tienes permisos para crear personal.')
        return redirect('personal_list')

    if request.method == 'POST':
        form = CrearTemporalForm(request.POST)
        if form.is_valid():
            ci               = form.cleaned_data['ci']
            nombres          = form.cleaned_data['nombres']
            apellido_paterno = form.cleaned_data['apellido_paterno']
            apellido_materno = form.cleaned_data.get('apellido_materno', '')
            password         = form.cleaned_data.get('password', '').strip() or ci[::-1]

            with transaction.atomic():
                # Crear personal con datos mínimos — placeholders que el policía corregirá
                from catalogos.models import Grado, Unidad, TipoEstado
                grado         = Grado.objects.order_by('orden').last()
                unidad        = Unidad.objects.filter(activa=True).first()
                estado_actual = TipoEstado.objects.filter(nombre='Activo').first() \
                                or TipoEstado.objects.first()

                personal = PersonalPolicial.objects.create(
                    ci                    = ci,
                    codigo_identificacion = ci,
                    nombres               = nombres,
                    apellido_paterno      = apellido_paterno,
                    apellido_materno      = apellido_materno,
                    expedido              = 'LP',
                    fecha_nacimiento      = '2000-01-01',
                    genero                = 'M',
                    grado                 = grado,
                    unidad                = unidad,
                    estado_actual         = estado_actual,
                    fecha_ingreso         = timezone.now().date(),
                    activo                = True,
                )

                usuario = Usuario.objects.create(
                    username   = ci,
                    first_name = nombres,
                    last_name  = f"{apellido_paterno} {apellido_materno}".strip(),
                    email      = '',
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
                    f'Creó registro temporal: {personal} — usuario: {ci}',
                    objeto=personal,
                )

            messages.success(
                request,
                f'✅ Usuario temporal creado. '
                f'<strong>Usuario: {ci}</strong> — '
                f'<strong>Contraseña: {password}</strong>. '
                f'Entrégasela al policía.'
            )
            return redirect('autoregistro:lista_temporales')
    else:
        form = CrearTemporalForm()

    return render(request, 'autoregistro/crear_temporal.html', {'form': form})


# ══════════════════════════════════════════════════════════════════
#  ADMINISTRATIVO — Lista de registros temporales
# ══════════════════════════════════════════════════════════════════

@login_required
def lista_temporales(request):
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


# ══════════════════════════════════════════════════════════════════
#  ADMINISTRATIVO — Revisar y aprobar registro completado
# ══════════════════════════════════════════════════════════════════

@login_required
def revisar_registro(request, pk):
    if not request.user.puede_editar():
        messages.error(request, '❌ No tienes permisos.')
        return redirect('dashboard')

    reg      = get_object_or_404(RegistroTemporal, pk=pk)
    personal = reg.personal

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'aprobar':
            form = CompletarRegistroForm(request.POST, request.FILES, instance=personal)
            if form.is_valid():
                campos_editados = form.changed_data
                with transaction.atomic():
                    form.save()
                    reg.usuario.rol    = 'usuario_autorizado'
                    reg.usuario.activo = True
                    reg.usuario.save(update_fields=['rol', 'activo'])
                    reg.estado            = 'aprobado'
                    reg.revisado_por      = request.user
                    reg.fecha_aprobacion  = timezone.now()
                    reg.observaciones_rev = request.POST.get('observaciones_rev', '')
                    reg.save()

                    if campos_editados:
                        registrar_log(
                            request, 'EDITAR', 'personal',
                            f'Editó datos de {personal} durante la revisión. '
                            f'Campos modificados: {", ".join(campos_editados)}',
                            objeto=personal,
                        )

                    registrar_log(
                        request, 'EDITAR', 'personal',
                        f'Aprobó registro temporal de {personal}',
                        objeto=reg,
                    )
                messages.success(
                    request,
                    f'Registro de {personal.nombre_completo()} aprobado. '
                    f'Cuenta activada como Usuario Autorizado.'
                )
                return redirect('autoregistro:lista_temporales')

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
#  POLICÍA — Completar su propio registro
# ══════════════════════════════════════════════════════════════════

@login_required
def completar_registro(request):
    if request.user.rol != 'temporal':
        return redirect('dashboard')

    try:
        reg      = request.user.registro_temporal
        personal = reg.personal
    except Exception:
        messages.error(request, '❌ No se encontró tu registro. Contacta al administrador.')
        return redirect('login')

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

# ══════════════════════════════════════════════════════════════════
#  ADMINISTRATIVO — Habilitar autoregistro para personal YA existente
# ══════════════════════════════════════════════════════════════════

@login_required
@require_POST
def crear_usuario_temporal(request, personal_id):
    if not request.user.puede_crear():
        messages.error(request, 'No tienes permisos para crear usuarios.')
        return redirect('personal_list')

    personal = get_object_or_404(PersonalPolicial, pk=personal_id)

    if hasattr(personal, 'usuario_acceso') and personal.usuario_acceso:
        messages.error(request, f'{personal.nombre_completo()} ya tiene un usuario de acceso.')
        return redirect('personal_detail', pk=personal.pk)

    ci = personal.ci
    password = request.POST.get('password', '').strip() or ci[::-1]

    with transaction.atomic():
        usuario = Usuario.objects.create(
            username   = ci,
            first_name = personal.nombres,
            last_name  = f"{personal.apellido_paterno} {personal.apellido_materno}".strip(),
            email      = '',
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
            f'Habilitó autoregistro para {personal} — usuario: {ci}',
            objeto=personal,
        )

    messages.success(
        request,
        f'Usuario temporal creado. Usuario: {ci} — Contraseña: {password}. '
        f'Entrégasela al policía.'
    )
    return redirect('personal_detail', pk=personal.pk)