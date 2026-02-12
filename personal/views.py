"""
Ejemplo de vistas actualizadas con el nuevo sistema de control de acceso
Archivo: personal/views.py (ACTUALIZADO)
"""

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.utils import timezone

from .models import (
    PersonalPolicial, 
    PermisoLicencia,
    SancionAplicada, 
    FelicitacionAplicada,
    KardexDigital
)
from catalogos.models import TipoFelicitacion

# IMPORTAR MIXINS ACTUALIZADOS
from core.mixins import (
    AdminRequiredMixin,
    OficialAdministrativoRequiredMixin,
    UsuarioAutorizadoRequiredMixin,
    PuedeCrearMixin,
    PuedeEditarMixin,
    PuedeEliminarMixin,
    PuedeAprobarPermisosMixin,
    PuedeGestionarSancionesMixin
)


# ==========================================
# VISTAS PARA PERSONAL
# ==========================================

class PersonalListView(UsuarioAutorizadoRequiredMixin, ListView):
    """
    Lista de personal policial
    Acceso: Todos los roles (solo consulta)
    """
    model = PersonalPolicial
    template_name = 'personal/personal_list.html'
    context_object_name = 'personal'
    ordering = ['grado__orden', 'apellido_paterno']


class PersonalCreateView(PuedeCrearMixin, CreateView):
    """
    Crear nuevo personal
    Acceso: Administrador + Oficial Administrativo
    """
    model = PersonalPolicial
    template_name = 'personal/personal_form.html'
    fields = [
        'codigo_identificacion', 'ci', 'expedido',
        'nombres', 'apellido_paterno', 'apellido_materno',
        'fecha_nacimiento', 'genero', 'grado', 'unidad',
        'estado_actual', 'fecha_ingreso', 'telefono_personal',
        'telefono_emergencia', 'correo_institucional', 'activo'
    ]
    success_url = reverse_lazy('personal_list')


class PersonalUpdateView(PuedeEditarMixin, UpdateView):
    """
    Editar personal existente
    Acceso: Administrador + Oficial Administrativo
    """
    model = PersonalPolicial
    template_name = 'personal/personal_form.html'
    fields = [
        'codigo_identificacion', 'ci', 'expedido',
        'nombres', 'apellido_paterno', 'apellido_materno',
        'fecha_nacimiento', 'genero', 'grado', 'unidad',
        'estado_actual', 'fecha_ingreso', 'telefono_personal',
        'telefono_emergencia', 'correo_institucional', 'activo'
    ]
    success_url = reverse_lazy('personal_list')


class PersonalDetailView(UsuarioAutorizadoRequiredMixin, DetailView):
    """
    Ver detalle de personal
    Acceso: Todos los roles
    """
    model = PersonalPolicial
    template_name = 'personal/personal_detail.html'
    context_object_name = 'persona'


class PersonalDeleteView(PuedeEliminarMixin, DeleteView):
    """
    Eliminar personal
    Acceso: Solo Administrador
    """
    model = PersonalPolicial
    template_name = 'personal/personal_confirm_delete.html'
    success_url = reverse_lazy('personal_list')


# ==========================================
# VISTAS PARA KARDEX
# ==========================================

class KardexPersonalListView(UsuarioAutorizadoRequiredMixin, ListView):
    """
    Lista de registros del kardex de un personal
    Acceso: Todos los roles
    """
    model = KardexDigital
    template_name = 'personal/kardex_list.html'
    context_object_name = 'registros'

    def get_queryset(self):
        personal_id = self.kwargs['personal_id']
        return KardexDigital.objects.filter(personal_id=personal_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = PersonalPolicial.objects.get(pk=self.kwargs['personal_id'])
        return context


class KardexCreateView(PuedeCrearMixin, CreateView):
    """
    Crear nuevo registro en el kardex
    Acceso: Administrador + Oficial Administrativo
    """
    model = KardexDigital
    template_name = 'personal/kardex_form.html'
    fields = [
        'tipo_registro', 'fecha_registro', 'descripcion',
        'documento_referencia', 'observaciones',
        'grado_anterior', 'grado_nuevo',
        'unidad_anterior', 'unidad_nueva', 
        'estado_anterior', 'estado_nuevo'
    ]

    def form_valid(self, form):
        personal_id = self.kwargs['personal_id']
        form.instance.personal_id = personal_id
        form.instance.registrado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        personal_id = self.kwargs['personal_id']
        return reverse_lazy('kardex_list', kwargs={'personal_id': personal_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = PersonalPolicial.objects.get(pk=self.kwargs['personal_id'])
        return context


# ==========================================
# VISTAS PARA PERMISOS
# ==========================================

class PermisoListView(UsuarioAutorizadoRequiredMixin, ListView):
    """
    Lista de permisos y licencias
    Acceso: Todos los roles
    """
    model = PermisoLicencia
    template_name = 'personal/permiso_list.html'
    context_object_name = 'permisos'
    ordering = ['-fecha_solicitud']


class PermisoCreateView(PuedeCrearMixin, CreateView):
    """
    Crear nueva solicitud de permiso
    Acceso: Administrador + Oficial Administrativo
    """
    model = PermisoLicencia
    template_name = 'personal/permiso_form.html'
    fields = [
        'personal', 'tipo_permiso', 'fecha_inicio', 'fecha_fin',
        'motivo', 'documento_adjunto', 'numero_oficio'
    ]
    success_url = reverse_lazy('permiso_list')

    def form_valid(self, form):
        form.instance.solicitado_por = self.request.user
        return super().form_valid(form)


class PermisoUpdateView(PuedeEditarMixin, UpdateView):
    """
    Editar solicitud de permiso
    Acceso: Administrador + Oficial Administrativo
    """
    model = PermisoLicencia
    template_name = 'personal/permiso_form.html'
    fields = [
        'personal', 'tipo_permiso', 'fecha_inicio', 'fecha_fin',
        'motivo', 'documento_adjunto', 'numero_oficio'
    ]
    success_url = reverse_lazy('permiso_list')


class PermisoAprobarView(PuedeAprobarPermisosMixin, UpdateView):
    """
    Aprobar o rechazar solicitud de permiso
    Acceso: Administrador + Oficial Administrativo
    """
    model = PermisoLicencia
    template_name = 'personal/permiso_aprobar.html'
    fields = ['estado', 'observaciones_aprobacion']

    def form_valid(self, form):
        if form.cleaned_data['estado'] == 'aprobado':
            form.instance.aprobado_por = self.request.user
            form.instance.fecha_aprobacion = timezone.now()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('permiso_list')


class PermisoDetailView(UsuarioAutorizadoRequiredMixin, DetailView):
    """
    Ver detalle de permiso
    Acceso: Todos los roles
    """
    model = PermisoLicencia
    template_name = 'personal/permiso_detail.html'
    context_object_name = 'permiso'


# ==========================================
# VISTAS PARA SANCIONES
# ==========================================

class SancionListView(PuedeGestionarSancionesMixin, ListView):
    """
    Lista de sanciones
    Acceso: Administrador + Oficial Administrativo
    """
    model = SancionAplicada
    template_name = 'personal/sancion_list.html'
    context_object_name = 'sanciones'
    ordering = ['-fecha_sancion']


class SancionCreateView(PuedeGestionarSancionesMixin, CreateView):
    """
    Crear nueva sanción
    Acceso: Administrador + Oficial Administrativo
    """
    model = SancionAplicada
    template_name = 'personal/sancion_form.html'
    fields = [
        'personal', 'tipo_sancion', 'fecha_sancion', 'fecha_inicio', 'fecha_fin',
        'motivo', 'estado', 'observaciones', 'documento_referencia'
    ]
    success_url = reverse_lazy('sancion_list')

    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        return super().form_valid(form)


class SancionUpdateView(PuedeGestionarSancionesMixin, UpdateView):
    """
    Editar sanción
    Acceso: Administrador + Oficial Administrativo
    """
    model = SancionAplicada
    template_name = 'personal/sancion_form.html'
    fields = [
        'personal', 'tipo_sancion', 'fecha_sancion', 'fecha_inicio', 'fecha_fin',
        'motivo', 'estado', 'observaciones', 'documento_referencia'
    ]
    success_url = reverse_lazy('sancion_list')


class SancionDetailView(PuedeGestionarSancionesMixin, DetailView):
    """
    Ver detalle de sanción
    Acceso: Administrador + Oficial Administrativo
    """
    model = SancionAplicada
    template_name = 'personal/sancion_detail.html'
    context_object_name = 'sancion'


# ==========================================
# VISTAS PARA FELICITACIONES
# ==========================================

class FelicitacionListView(UsuarioAutorizadoRequiredMixin, ListView):
    """
    Lista de felicitaciones
    Acceso: Todos los roles
    """
    model = FelicitacionAplicada
    template_name = 'personal/felicitacion_list.html'
    context_object_name = 'felicitaciones'
    ordering = ['-fecha_felicitacion']

    def get_queryset(self):
        queryset = super().get_queryset()
        tipo_id = self.request.GET.get('tipo')
        if tipo_id:
            queryset = queryset.filter(tipo_felicitacion_id=tipo_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_felicitacion'] = TipoFelicitacion.objects.all()
        return context


class FelicitacionCreateView(PuedeCrearMixin, CreateView):
    """
    Crear nueva felicitación
    Acceso: Administrador + Oficial Administrativo
    """
    model = FelicitacionAplicada
    template_name = 'personal/felicitacion_form.html'
    fields = [
        'personal', 'tipo_felicitacion', 'fecha_felicitacion',
        'motivo', 'documento_referencia', 'observaciones'
    ]
    success_url = reverse_lazy('felicitacion_list')

    def form_valid(self, form):
        form.instance.registrado_por = self.request.user
        return super().form_valid(form)


class FelicitacionUpdateView(PuedeEditarMixin, UpdateView):
    """
    Editar felicitación
    Acceso: Administrador + Oficial Administrativo
    """
    model = FelicitacionAplicada
    template_name = 'personal/felicitacion_form.html'
    fields = [
        'personal', 'tipo_felicitacion', 'fecha_felicitacion',
        'motivo', 'documento_referencia', 'observaciones'
    ]
    success_url = reverse_lazy('felicitacion_list')


class FelicitacionDetailView(UsuarioAutorizadoRequiredMixin, DetailView):
    """
    Ver detalle de felicitación
    Acceso: Todos los roles
    """
    model = FelicitacionAplicada
    template_name = 'personal/felicitacion_detail.html'
    context_object_name = 'felicitacion'