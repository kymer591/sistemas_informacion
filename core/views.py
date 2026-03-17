from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from catalogos.models import Unidad, Grado
from personal.models import PersonalPolicial, KardexDigital, DestinoPolicial

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Usuario
from .mixins import AdminRequiredMixin

from reportes.utils import registrar_log


# ==========================================
# AUTENTICACIÓN
# ==========================================

def custom_login(request):
    # Login/logout ya se registran automáticamente via señales en reportes/signals.py
    if request.user.is_authenticated:
        if not request.user.activo:
            return render(request, 'core/cuenta_desactivada.html', {'user': request.user})
        if request.user.es_usuario_autorizado():
            return redirect('mi_perfil')
        else:
            return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                if not user.activo:
                    return render(request, 'core/cuenta_desactivada.html', {'user': user})
                messages.success(request, f'✅ Bienvenido {username}!')
                if user.es_usuario_autorizado():
                    return redirect('mi_perfil')
                else:
                    return redirect('dashboard')
        else:
            messages.error(request, '❌ Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, '👋 Has cerrado sesión correctamente')
    return redirect('login')


# ==========================================
# DASHBOARD Y PERFIL
# ==========================================

@login_required
def dashboard(request):
    if not request.user.activo:
        return render(request, 'core/cuenta_desactivada.html', {'user': request.user})

    if request.user.es_usuario_autorizado():
        return redirect('mi_perfil')

    total_personal    = PersonalPolicial.objects.count()
    personal_activo   = PersonalPolicial.objects.filter(estado_actual__nombre='Activo').count()
    personal_licencia = PersonalPolicial.objects.filter(estado_actual__nombre='Licencia').count()

    personal_por_unidad = Unidad.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'total')

    personal_por_grado = Grado.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'abreviatura', 'total')

    ultimos_registros = KardexDigital.objects.select_related('personal').order_by('-fecha_creacion')[:10]

    context = {
        'total_personal'    : total_personal,
        'personal_activo'   : personal_activo,
        'personal_licencia' : personal_licencia,
        'personal_por_unidad': personal_por_unidad,
        'personal_por_grado': personal_por_grado,
        'ultimos_registros' : ultimos_registros,
    }
    return render(request, 'dashboard.html', context)


@login_required
def mi_perfil(request):
    if not request.user.activo:
        return render(request, 'core/cuenta_desactivada.html', {'user': request.user})

    if not request.user.es_usuario_autorizado():
        messages.warning(request, "⚠️ Esta página es solo para usuarios autorizados")
        return redirect('dashboard')

    try:
        personal = request.user.personal
        if not personal:
            raise Exception("Sin personal")
    except Exception:
        return render(request, 'core/sin_personal_asignado.html', {'user': request.user})

    kardex         = personal.kardex.all()[:10]
    permisos       = personal.permisos.all()[:10]
    sanciones      = personal.sanciones_aplicadas.all()[:10]
    felicitaciones = personal.felicitaciones_aplicadas.all()[:10]
    destinos       = personal.destinos.all()
    destino_activo = personal.destinos.filter(activo=True).first()

    context = {
        'personal'      : personal,
        'kardex'        : kardex,
        'permisos'      : permisos,
        'sanciones'     : sanciones,
        'felicitaciones': felicitaciones,
        'destinos'      : destinos,
        'destino_activo': destino_activo,
    }
    return render(request, 'core/mi_perfil.html', context)


# ==========================================
# ASIGNAR ROLES
# ==========================================

class AsignarRolForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Dejar vacío para mantener la contraseña actual'
    )

    class Meta:
        model  = Usuario
        fields = ['username', 'rol', 'activo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'rol'     : forms.Select(attrs={'class': 'form-control'}),
            'activo'  : forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AsignarRolListView(AdminRequiredMixin, ListView):
    model               = PersonalPolicial
    template_name       = 'core/asignar_rol_list.html'
    context_object_name = 'personal'
    paginate_by         = 20

    def get_queryset(self):
        queryset = PersonalPolicial.objects.select_related('grado', 'unidad').all()
        search = self.request.GET.get('buscar', '')
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search)               |
                Q(apellido_paterno__icontains=search)      |
                Q(apellido_materno__icontains=search)      |
                Q(ci__icontains=search)                    |
                Q(codigo_identificacion__icontains=search)
            )
        return queryset.order_by('apellido_paterno', 'apellido_materno', 'nombres')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buscar'] = self.request.GET.get('buscar', '')
        for persona in context['personal']:
            persona.usuario_relacionado = self._buscar_usuario(persona)
        return context

    @staticmethod
    def _buscar_usuario(persona):
        try:
            return Usuario.objects.get(personal=persona)
        except Usuario.DoesNotExist:
            pass
        try:
            u = Usuario.objects.get(username=persona.ci)
            u.personal = persona
            u.save(update_fields=['personal'])
            return u
        except Usuario.DoesNotExist:
            return None


class AsignarRolUpdateView(AdminRequiredMixin, UpdateView):
    model         = PersonalPolicial
    template_name = 'core/asignar_rol_form.html'
    form_class    = AsignarRolForm
    success_url   = reverse_lazy('asignar_rol_list')

    def _get_usuario(self):
        try:
            return Usuario.objects.get(personal=self.object)
        except Usuario.DoesNotExist:
            pass
        try:
            usuario = Usuario.objects.get(username=self.object.ci)
            usuario.personal = self.object
            usuario.save(update_fields=['personal'])
            return usuario
        except Usuario.DoesNotExist:
            return None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self._get_usuario()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self._get_usuario()
        context['persona']       = self.object
        context['tiene_usuario'] = usuario is not None
        context['usuario']       = usuario
        return context

    def form_valid(self, form):
        personal = self.object
        usuario  = form.save(commit=False)
        es_nuevo = not usuario.pk

        usuario.personal = personal

        password = form.cleaned_data.get('password')
        if password:
            usuario.set_password(password)
        elif es_nuevo:
            usuario.set_password(personal.ci[::-1])

        usuario.save()

        # Registrar en bitácora
        accion = 'CREAR' if es_nuevo else 'EDITAR'
        desc   = (
            f'{"Creó" if es_nuevo else "Editó"} usuario "{usuario.username}" '
            f'— rol: {usuario.get_rol_display()} '
            f'— personal: {personal}'
        )
        registrar_log(self.request, accion, 'usuarios', desc, objeto=usuario)

        messages.success(
            self.request,
            f'✅ Usuario {"creado" if es_nuevo else "actualizado"} correctamente'
        )
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, '❌ Corrige los errores en el formulario')
        return super().form_invalid(form)


@login_required
def cambiar_rol_usuario(request, personal_id):
    if not request.user.es_administrador():
        messages.error(request, "❌ Solo administradores pueden cambiar roles")
        return redirect('personal_detail', pk=personal_id)

    personal = get_object_or_404(PersonalPolicial, pk=personal_id)

    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        if hasattr(personal, 'usuario_acceso'):
            usuario = personal.usuario_acceso
            rol_anterior = usuario.get_rol_display()
            usuario.rol  = nuevo_rol
            usuario.save()

            registrar_log(
                request, 'EDITAR', 'usuarios',
                f'Cambió rol de {personal} de "{rol_anterior}" a "{usuario.get_rol_display()}"',
                objeto=usuario,
            )
            messages.success(request, f"✅ Rol actualizado: {usuario.get_rol_display()}")
        else:
            messages.error(request, "❌ Este personal no tiene usuario asignado")

        return redirect('personal_detail', pk=personal_id)

    context = {
        'personal': personal,
        'usuario' : personal.usuario_acceso if hasattr(personal, 'usuario_acceso') else None,
    }
    return render(request, 'users/cambiar_rol.html', context)


# ==========================================
# TOGGLE USUARIO ACTIVO (AJAX)
# ==========================================

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def toggle_usuario_activo(request, user_id):
    if not request.user.es_administrador():
        return JsonResponse({'error': 'No autorizado'}, status=403)

    try:
        usuario = Usuario.objects.get(pk=user_id)

        if usuario.id == request.user.id:
            return JsonResponse({'error': 'No puedes desactivarte a ti mismo'}, status=400)

        usuario.activo = not usuario.activo
        usuario.save()

        accion = 'EDITAR'
        estado = 'activó' if usuario.activo else 'desactivó'
        registrar_log(
            request, accion, 'usuarios',
            f'{estado.capitalize()} cuenta del usuario "{usuario.username}"',
            objeto=usuario,
        )

        return JsonResponse({
            'success' : True,
            'activo'  : usuario.activo,
            'username': usuario.username,
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)