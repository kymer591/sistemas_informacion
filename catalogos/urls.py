from django.urls import path
from . import views

urlpatterns = [
    # Grados
    path('grados/', views.GradoListView.as_view(), name='grado_list'),
    path('grados/nuevo/', views.GradoCreateView.as_view(), name='grado_create'),
    path('grados/editar/<int:pk>/', views.GradoUpdateView.as_view(), name='grado_update'),
    path('grados/eliminar/<int:pk>/', views.GradoDeleteView.as_view(), name='grado_delete'),
    
    # Unidades
    path('unidades/', views.UnidadListView.as_view(), name='unidad_list'),
    path('unidades/nueva/', views.UnidadCreateView.as_view(), name='unidad_create'),
    path('unidades/editar/<int:pk>/', views.UnidadUpdateView.as_view(), name='unidad_update'),
    path('unidades/eliminar/<int:pk>/', views.UnidadDeleteView.as_view(), name='unidad_delete'),
    
    # Estados
    path('estados/', views.TipoEstadoListView.as_view(), name='tipoestado_list'),
    path('estados/nuevo/', views.TipoEstadoCreateView.as_view(), name='tipoestado_create'),
    path('estados/editar/<int:pk>/', views.TipoEstadoUpdateView.as_view(), name='tipoestado_update'),
    path('estados/eliminar/<int:pk>/', views.TipoEstadoDeleteView.as_view(), name='tipoestado_delete'),
    
    # Sanciones
    path('sanciones/', views.TipoSancionListView.as_view(), name='tiposancion_list'),
    path('sanciones/nueva/', views.TipoSancionCreateView.as_view(), name='tiposancion_create'),
    path('sanciones/editar/<int:pk>/', views.TipoSancionUpdateView.as_view(), name='tiposancion_update'),
    path('sanciones/eliminar/<int:pk>/', views.TipoSancionDeleteView.as_view(), name='tiposancion_delete'),

    # Felicitaciones
    path('felicitaciones/', views.TipoFelicitacionListView.as_view(), name='tipofelicitacion_list'),
    path('felicitaciones/nueva/', views.TipoFelicitacionCreateView.as_view(), name='tipofelicitacion_create'),
    path('felicitaciones/editar/<int:pk>/', views.TipoFelicitacionUpdateView.as_view(), name='tipofelicitacion_update'),
    path('felicitaciones/eliminar/<int:pk>/', views.TipoFelicitacionDeleteView.as_view(), name='tipofelicitacion_delete'),
]