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
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    # Estadísticas básicas
    total_personal = PersonalPolicial.objects.count()
    personal_activo = PersonalPolicial.objects.filter(estado_actual__nombre='Activo').count()
    personal_licencia = PersonalPolicial.objects.filter(estado_actual__nombre='Licencia').count()
    
    # Personal por unidad
    personal_por_unidad = Unidad.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'total')
    
    # Personal por grado
    personal_por_grado = Grado.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'abreviatura', 'total')
    
    # Últimos registros de kardex
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


# Vista para asignar/editar rol
class AsignarRolUpdateView(AdminRequiredMixin, UpdateView):
    model = PersonalPolicial
    template_name = 'core/asignar_rol_form.html'
    fields = []  # No editamos PersonalPolicial
    success_url = reverse_lazy('asignar_rol_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        persona = self.get_object()
        
        # Buscar si existe usuario con este CI
        try:
            usuario = Usuario.objects.get(username=persona.ci)
        except Usuario.DoesNotExist:
            usuario = None
        
        if self.request.POST:
            context['form'] = AsignarRolForm(self.request.POST, instance=usuario)
        else:
            # Prellenar username con CI
            initial = {'username': persona.ci}
            if usuario:
                context['form'] = AsignarRolForm(instance=usuario)
            else:
                context['form'] = AsignarRolForm(initial=initial)
        
        context['persona'] = persona
        context['usuario_existe'] = usuario is not None
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        persona = self.object
        
        # Buscar si existe usuario
        try:
            usuario = Usuario.objects.get(username=persona.ci)
        except Usuario.DoesNotExist:
            usuario = None
        
        form = AsignarRolForm(request.POST, instance=usuario)
        
        if form.is_valid():
            usuario_obj = form.save(commit=False)
            
            # Si es nuevo usuario, configurar datos adicionales
            if not usuario:
                usuario_obj.first_name = persona.nombres
                usuario_obj.last_name = f"{persona.apellido_paterno} {persona.apellido_materno}"
                usuario_obj.email = persona.correo_institucional or f"{persona.ci}@uteppi.gob.bo"
                
                # Establecer contraseña (CI por defecto si se proporciona)
                password = form.cleaned_data.get('password')
                if password:
                    usuario_obj.set_password(password)
                else:
                    usuario_obj.set_password(persona.ci)  # CI como contraseña por defecto
            else:
                # Si se proporciona nueva contraseña, actualizarla
                password = form.cleaned_data.get('password')
                if password:
                    usuario_obj.set_password(password)
            
            usuario_obj.unidad = persona.unidad
            usuario_obj.telefono = persona.telefono_personal
            usuario_obj.save()
            
            messages.success(request, f'✅ Rol asignado correctamente a {persona.nombre_completo()}')
            return redirect(self.success_url)
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

def custom_logout(request):
    """Vista personalizada de logout"""
    logout(request)
    messages.success(request, '👋 Has cerrado sesión correctamente')
    return redirect('login')