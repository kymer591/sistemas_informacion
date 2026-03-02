from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from catalogos.models import Unidad, Grado
from personal.models import PersonalPolicial, KardexDigital
from django.contrib import messages

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Usuario
from .mixins import AdminRequiredMixin


def custom_login(request):
    # Si ya está autenticado
    if request.user.is_authenticated:
        # Si está desactivado, mostrar página de desactivado
        if not request.user.activo:
            return render(request, 'core/cuenta_desactivada.html', {'user': request.user})
        
        # Si está activo, redirigir según su rol
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
                # Login exitoso
                login(request, user)
                
                # Si está desactivado, mostrar página de desactivado
                if not user.activo:
                    return render(request, 'core/cuenta_desactivada.html', {'user': user})
                
                # Si está activo, redirigir según rol
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
def dashboard(request):
    """Dashboard principal - redirige según rol"""
    
    # Si el usuario está desactivado, mostrar página de desactivado
    if not request.user.activo:
        return render(request, 'core/cuenta_desactivada.html', {'user': request.user})
    
    # Si es usuario autorizado, redirigir a su perfil
    if request.user.es_usuario_autorizado():
        return redirect('mi_perfil')
    
    # Si es Admin u Oficial Admin, mostrar dashboard completo
    total_personal = PersonalPolicial.objects.count()
    personal_activo = PersonalPolicial.objects.filter(estado_actual__nombre='Activo').count()
    personal_licencia = PersonalPolicial.objects.filter(estado_actual__nombre='Licencia').count()
    
    personal_por_unidad = Unidad.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'total')
    
    personal_por_grado = Grado.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'abreviatura', 'total')
    
    ultimos_registros = KardexDigital.objects.select_related('personal').order_by('-fecha_creacion')[:10]
    
    context = {
        'total_personal': total_personal,
        'personal_activo': personal_activo,
        'personal_licencia': personal_licencia,
        'personal_por_unidad': personal_por_unidad,
        'personal_por_grado': personal_por_grado,
        'ultimos_registros': ultimos_registros,
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def cambiar_rol_usuario(request, personal_id):
    """Vista simple para cambiar rol de usuario"""
    # Solo administradores pueden cambiar roles
    if not request.user.es_administrador():
        messages.error(request, "❌ Solo administradores pueden cambiar roles")
        return redirect('personal_detail', pk=personal_id)
    
    # Obtener el personal
    personal = get_object_or_404(PersonalPolicial, pk=personal_id)
    
    if request.method == 'POST':
        nuevo_rol = request.POST.get('rol')
        
        # Verificar si el personal ya tiene usuario
        if hasattr(personal, 'usuario_acceso'):
            usuario = personal.usuario_acceso
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(request, f"✅ Rol actualizado: {usuario.get_rol_display()}")
        else:
            messages.error(request, "❌ Este personal no tiene usuario asignado")
        
        return redirect('personal_detail', pk=personal_id)
    
    # Si es GET, mostrar formulario
    context = {
        'personal': personal,
        'usuario': personal.usuario_acceso if hasattr(personal, 'usuario_acceso') else None
    }
    return render(request, 'users/cambiar_rol.html', context)

class AsignarRolForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Dejar vacío para mantener la contraseña actual'
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'rol', 'activo']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }


# Vista de lista de personal para asignar roles
class AsignarRolListView(AdminRequiredMixin, ListView):
    model = PersonalPolicial
    template_name = 'core/asignar_rol_list.html'
    context_object_name = 'personal'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = PersonalPolicial.objects.select_related('grado', 'unidad').all()
        
        # Búsqueda
        search = self.request.GET.get('buscar', '')
        if search:
            queryset = queryset.filter(
                Q(nombres__icontains=search) |
                Q(apellido_paterno__icontains=search) |
                Q(apellido_materno__icontains=search) |
                Q(ci__icontains=search) |
                Q(codigo_identificacion__icontains=search)
            )
        
        return queryset.order_by('apellido_paterno', 'apellido_materno', 'nombres')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buscar'] = self.request.GET.get('buscar', '')
        
        # Agregar usuario relacionado a cada persona
        for persona in context['personal']:
            try:
                persona.usuario_relacionado = Usuario.objects.get(username=persona.ci)
            except Usuario.DoesNotExist:
                persona.usuario_relacionado = None
        
        return context
class AsignarRolUpdateView(AdminRequiredMixin, UpdateView):
    model = PersonalPolicial
    template_name = 'core/asignar_rol_form.html'
    form_class = AsignarRolForm   # <-- aquí indicas el formulario
    success_url = reverse_lazy('asignar_roles')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Si estás editando un usuario existente, puedes pasar la instancia
        # del usuario relacionado al formulario
        try:
            kwargs['instance'] = self.object.usuario
        except:
            kwargs['instance'] = None
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personal = self.object
        context['tiene_usuario'] = hasattr(personal, 'usuario') and personal.usuario is not None
        context['usuario'] = personal.usuario if context['tiene_usuario'] else None
        return context
    
    def form_valid(self, form):
        personal = self.object
        usuario = form.save(commit=False)
        # Si es nuevo, asignamos el personal
        if not usuario.pk:
            # Verificar si el username ya existe (lo hace el formulario, pero podemos reforzar)
            pass
        usuario.save()
        # Vincular con personal
        personal.usuario = usuario
        personal.save()
        messages.success(self.request, '✅ Usuario guardado correctamente')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, '❌ Corrige los errores en el formulario')
        return super().form_invalid(form)

def custom_logout(request):
    """Vista personalizada de logout"""
    logout(request)
    messages.success(request, '👋 Has cerrado sesión correctamente')
    return redirect('login')

@login_required
def mi_perfil(request):
    """Vista personalizada para usuarios autorizados - solo ven su información"""
    
    # Si el usuario está desactivado, mostrar página de desactivado
    if not request.user.activo:
        return render(request, 'core/cuenta_desactivada.html', {'user': request.user})
    
    # Verificar que el usuario sea autorizado
    if not request.user.es_usuario_autorizado():
        messages.warning(request, "⚠️ Esta página es solo para usuarios autorizados")
        return redirect('dashboard')
    
    # Obtener el personal asociado (puede no existir)
    try:
        personal = request.user.personal
        if not personal:
            raise Exception("Sin personal")
    except:
        # Si no tiene personal, mostrar mensaje
        return render(request, 'core/sin_personal_asignado.html', {'user': request.user})
    
    # Obtener datos del personal
    kardex = personal.kardex.all()[:10]
    permisos = personal.permisos.all()[:10]
    sanciones = personal.sanciones_aplicadas.all()[:10]
    felicitaciones = personal.felicitaciones_aplicadas.all()[:10]
    
    context = {
        'personal': personal,
        'kardex': kardex,
        'permisos': permisos,
        'sanciones': sanciones,
        'felicitaciones': felicitaciones,
    }
    
    return render(request, 'core/mi_perfil.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def toggle_usuario_activo(request, user_id):
    """Vista para activar/desactivar usuarios vía AJAX"""
    
    # Solo admins pueden hacer esto
    if not request.user.es_administrador():
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        usuario = Usuario.objects.get(pk=user_id)
        
        # No permitir desactivar al propio usuario
        if usuario.id == request.user.id:
            return JsonResponse({'error': 'No puedes desactivarte a ti mismo'}, status=400)
        
        # Toggle del estado
        usuario.activo = not usuario.activo
        usuario.save()
        
        return JsonResponse({
            'success': True,
            'activo': usuario.activo,
            'username': usuario.username
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)