from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Grado, Unidad, TipoSancion

class GradoListView(ListView):
    model = Grado
    template_name = 'catalogos/grado_list.html'
    context_object_name = 'grados'

class GradoCreateView(CreateView):
    model = Grado
    template_name = 'catalogos/grado_form.html'
    fields = ['nombre', 'abreviatura', 'orden', 'activo']
    success_url = reverse_lazy('grado_list')

class GradoUpdateView(UpdateView):
    model = Grado
    template_name = 'catalogos/grado_form.html'
    fields = ['nombre', 'abreviatura', 'orden', 'activo']
    success_url = reverse_lazy('grado_list')

class GradoDeleteView(DeleteView):
    model = Grado
    template_name = 'catalogos/grado_confirm_delete.html'
    success_url = reverse_lazy('grado_list')

# Agrega estas clases después de las vistas de Grado
class UnidadListView(ListView):
    model = Unidad
    template_name = 'catalogos/unidad_list.html'
    context_object_name = 'unidades'

class UnidadCreateView(CreateView):
    model = Unidad
    template_name = 'catalogos/unidad_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activa']
    success_url = reverse_lazy('unidad_list')

class UnidadUpdateView(UpdateView):
    model = Unidad
    template_name = 'catalogos/unidad_form.html'
    fields = ['codigo', 'nombre', 'descripcion', 'activa']
    success_url = reverse_lazy('unidad_list')

class UnidadDeleteView(DeleteView):
    model = Unidad
    template_name = 'catalogos/unidad_confirm_delete.html'
    success_url = reverse_lazy('unidad_list')

# Agrega estas clases después de las vistas de TipoEstado
class TipoSancionListView(ListView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_list.html'
    context_object_name = 'sanciones'

class TipoSancionCreateView(CreateView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_form.html'
    fields = ['nombre', 'gravedad', 'activo']
    success_url = reverse_lazy('tiposancion_list')

class TipoSancionUpdateView(UpdateView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_form.html'
    fields = ['nombre', 'gravedad', 'activo']
    success_url = reverse_lazy('tiposancion_list')

class TipoSancionDeleteView(DeleteView):
    model = TipoSancion
    template_name = 'catalogos/tiposancion_confirm_delete.html'
    success_url = reverse_lazy('tiposancion_list')