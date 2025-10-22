from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Grado, Unidad, TipoEstado, TipoSancion

# ===== GRADOS =====
class GradoListView(LoginRequiredMixin, ListView):
    model = Grado
    template_name = 'catalogos/grado_list.html'
    context_object_name = 'grados'
    login_url = 'login'

class GradoCreateView(LoginRequiredMixin, CreateView):
    model = Grado
    template_name = 'catalogos/grado_form.html'
    fields = ['nombre', 'abreviatura', 'orden', 'activo']
    success_url = reverse_lazy('grado_list')
    login_url = 'login'

class GradoUpdateView(LoginRequiredMixin, UpdateView):
    model = Grado
    template_name = 'catalogos/grado_form.html'
    fields = ['nombre', 'abreviatura', 'orden', 'activo']
    success_url = reverse_lazy('grado_list')
    login_url = 'login'

class GradoDeleteView(LoginRequiredMixin, DeleteView):
    model = Grado
    template_name = 'catalogos/grado_confirm_delete.html'
    success_url = reverse_lazy('grado_list')
    login_url = 'login'

# ===== UNIDADES =====
class UnidadListView(LoginRequiredMixin, ListView):
    model = Unidad
    template_name = 'catalogos/unidad_list.html'
    context_object_name = 'unidades'
    login_url = 'login'

class UnidadCreateView(LoginRequiredMixin, CreateView):
    model = Unidad
    template_name = 'catalogos/unidad_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activa']
    success_url = reverse_lazy('unidad_list')
    login_url = 'login'

class UnidadUpdateView(LoginRequiredMixin, UpdateView):
    model = Unidad
    template_name = 'catalogos/unidad_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activa']
    success_url = reverse_lazy('unidad_list')
    login_url = 'login'

class UnidadDeleteView(LoginRequiredMixin, DeleteView):
    model = Unidad
    template_name = 'catalogos/unidad_confirm_delete.html'
    success_url = reverse_lazy('unidad_list')
    login_url = 'login'

# ===== TIPOS DE ESTADO =====
class TipoEstadoListView(LoginRequiredMixin, ListView):
    model = TipoEstado
    template_name = 'catalogos/tipoestado_list.html'
    context_object_name = 'estados'
    login_url = 'login'

class TipoEstadoCreateView(LoginRequiredMixin, CreateView):
    model = TipoEstado
    template_name = 'catalogos/tipoestado_form.html'
    fields = ['nombre', 'color']
    success_url = reverse_lazy('tipoestado_list')
    login_url = 'login'

class TipoEstadoUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoEstado
    template_name = 'catalogos/tipoestado_form.html'
    fields = ['nombre', 'color']
    success_url = reverse_lazy('tipoestado_list')
    login_url = 'login'

class TipoEstadoDeleteView(LoginRequiredMixin, DeleteView):
    model = TipoEstado
    template_name = 'catalogos/tipoestado_confirm_delete.html'
    success_url = reverse_lazy('tipoestado_list')
    login_url = 'login'

# ===== TIPOS DE SANCIÓN =====
class TipoSancionListView(LoginRequiredMixin, ListView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_list.html'
    context_object_name = 'sanciones'
    login_url = 'login'

class TipoSancionCreateView(LoginRequiredMixin, CreateView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_form.html'
    fields = ['nombre', 'gravedad', 'activo']
    success_url = reverse_lazy('tiposancion_list')
    login_url = 'login'

class TipoSancionUpdateView(LoginRequiredMixin, UpdateView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_form.html'
    fields = ['nombre', 'gravedad', 'activo']
    success_url = reverse_lazy('tiposancion_list')
    login_url = 'login'

class TipoSancionDeleteView(LoginRequiredMixin, DeleteView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_confirm_delete.html'
    success_url = reverse_lazy('tiposancion_list')
    login_url = 'login'