from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Grado, Unidad, TipoEstado, TipoSancion, TipoFelicitacion

from core.mixins import (
    UsuarioAutorizadoRequiredMixin,
    PuedeCrearMixin,
    PuedeEditarMixin,
    PuedeEliminarMixin
)

from reportes.utils import BitacoraMixin


# ===== GRADOS =====
class GradoListView(UsuarioAutorizadoRequiredMixin, ListView):
    model = Grado
    template_name = 'catalogos/grado_list.html'
    context_object_name = 'grados'
    login_url = 'login'

class GradoCreateView(BitacoraMixin, PuedeCrearMixin, CreateView):
    bitacora_modulo = 'catalogos'
    model = Grado
    template_name = 'catalogos/grado_form.html'
    fields = ['nombre', 'abreviatura', 'orden', 'activo']
    success_url = reverse_lazy('grado_list')
    login_url = 'login'

class GradoUpdateView(BitacoraMixin, PuedeEditarMixin, UpdateView):
    bitacora_modulo = 'catalogos'
    model = Grado
    template_name = 'catalogos/grado_form.html'
    fields = ['nombre', 'abreviatura', 'orden', 'activo']
    success_url = reverse_lazy('grado_list')
    login_url = 'login'

class GradoDeleteView(BitacoraMixin, PuedeEliminarMixin, DeleteView):
    bitacora_modulo = 'catalogos'
    model = Grado
    template_name = 'catalogos/grado_confirm_delete.html'
    success_url = reverse_lazy('grado_list')
    login_url = 'login'


# ===== UNIDADES =====
class UnidadListView(UsuarioAutorizadoRequiredMixin, ListView):
    model = Unidad
    template_name = 'catalogos/unidad_list.html'
    context_object_name = 'unidades'
    login_url = 'login'

class UnidadCreateView(BitacoraMixin, PuedeCrearMixin, CreateView):
    bitacora_modulo = 'catalogos'
    model = Unidad
    template_name = 'catalogos/unidad_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activa']
    success_url = reverse_lazy('unidad_list')
    login_url = 'login'

class UnidadUpdateView(BitacoraMixin, PuedeEditarMixin, UpdateView):
    bitacora_modulo = 'catalogos'
    model = Unidad
    template_name = 'catalogos/unidad_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activa']
    success_url = reverse_lazy('unidad_list')
    login_url = 'login'

class UnidadDeleteView(BitacoraMixin, PuedeEliminarMixin, DeleteView):
    bitacora_modulo = 'catalogos'
    model = Unidad
    template_name = 'catalogos/unidad_confirm_delete.html'
    success_url = reverse_lazy('unidad_list')
    login_url = 'login'


# ===== TIPOS DE ESTADO =====
class TipoEstadoListView(UsuarioAutorizadoRequiredMixin, ListView):
    model = TipoEstado
    template_name = 'catalogos/tipoestado_list.html'
    context_object_name = 'estados'

class TipoEstadoCreateView(BitacoraMixin, PuedeCrearMixin, CreateView):
    bitacora_modulo = 'catalogos'
    model = TipoEstado
    template_name = 'catalogos/tipoestado_form.html'
    fields = ['nombre', 'color']
    success_url = reverse_lazy('tipoestado_list')

class TipoEstadoUpdateView(BitacoraMixin, PuedeEditarMixin, UpdateView):
    bitacora_modulo = 'catalogos'
    model = TipoEstado
    template_name = 'catalogos/tipoestado_form.html'
    fields = ['nombre', 'color']
    success_url = reverse_lazy('tipoestado_list')

class TipoEstadoDeleteView(BitacoraMixin, PuedeEliminarMixin, DeleteView):
    bitacora_modulo = 'catalogos'
    model = TipoEstado
    template_name = 'catalogos/tipoestado_confirm_delete.html'
    success_url = reverse_lazy('tipoestado_list')


# ===== TIPOS DE SANCIÓN =====
class TipoSancionListView(UsuarioAutorizadoRequiredMixin, ListView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_list.html'
    context_object_name = 'sanciones'
    login_url = 'login'

class TipoSancionCreateView(BitacoraMixin, PuedeCrearMixin, CreateView):
    bitacora_modulo = 'catalogos'
    model = TipoSancion
    template_name = 'catalogos/tiposancion_form.html'
    fields = ['nombre', 'gravedad', 'activo']
    success_url = reverse_lazy('tiposancion_list')
    login_url = 'login'

class TipoSancionUpdateView(BitacoraMixin, PuedeEditarMixin, UpdateView):
    bitacora_modulo = 'catalogos'
    model = TipoSancion
    template_name = 'catalogos/tiposancion_form.html'
    fields = ['nombre', 'gravedad', 'activo']
    success_url = reverse_lazy('tiposancion_list')
    login_url = 'login'

class TipoSancionDeleteView(BitacoraMixin, PuedeEliminarMixin, DeleteView):
    bitacora_modulo = 'catalogos'
    model = TipoSancion
    template_name = 'catalogos/tiposancion_confirm_delete.html'
    success_url = reverse_lazy('tiposancion_list')
    login_url = 'login'


# ===== TIPOS DE FELICITACIÓN =====
class TipoFelicitacionListView(UsuarioAutorizadoRequiredMixin, ListView):
    model = TipoFelicitacion
    template_name = 'catalogos/tipofelicitacion_list.html'
    context_object_name = 'felicitaciones'

class TipoFelicitacionCreateView(BitacoraMixin, PuedeCrearMixin, CreateView):
    bitacora_modulo = 'catalogos'
    model = TipoFelicitacion
    template_name = 'catalogos/tipofelicitacion_form.html'
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('tipofelicitacion_list')

class TipoFelicitacionUpdateView(BitacoraMixin, PuedeEditarMixin, UpdateView):
    bitacora_modulo = 'catalogos'
    model = TipoFelicitacion
    template_name = 'catalogos/tipofelicitacion_form.html'
    fields = ['nombre', 'descripcion']
    success_url = reverse_lazy('tipofelicitacion_list')

class TipoFelicitacionDeleteView(BitacoraMixin, PuedeEliminarMixin, DeleteView):
    bitacora_modulo = 'catalogos'
    model = TipoFelicitacion
    template_name = 'catalogos/tipofelicitacion_confirm_delete.html'
    success_url = reverse_lazy('tipofelicitacion_list')