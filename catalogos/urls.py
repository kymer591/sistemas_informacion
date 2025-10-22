from django.urls import path
from . import views

urlpatterns = [
    path('grados/', views.GradoListView.as_view(), name='grado_list'),
    path('grados/nuevo/', views.GradoCreateView.as_view(), name='grado_create'),
    path('grados/editar/<int:pk>/', views.GradoUpdateView.as_view(), name='grado_update'),
    path('grados/eliminar/<int:pk>/', views.GradoDeleteView.as_view(), name='grado_delete'),
    # Agrega estas URLs después de las de grados
    path('unidades/', views.UnidadListView.as_view(), name='unidad_list'),
    path('unidades/nueva/', views.UnidadCreateView.as_view(), name='unidad_create'),
    path('unidades/editar/<int:pk>/', views.UnidadUpdateView.as_view(), name='unidad_update'),
    path('unidades/eliminar/<int:pk>/', views.UnidadDeleteView.as_view(), name='unidad_delete'),
    # Agrega estas URLs después de las de estados
    path('sanciones/', views.TipoSancionListView.as_view(), name='tiposancion_list'),
    path('sanciones/nueva/', views.TipoSancionCreateView.as_view(), name='tiposancion_create'),
    path('sanciones/editar/<int:pk>/', views.TipoSancionUpdateView.as_view(), name='tiposancion_update'),
    path('sanciones/eliminar/<int:pk>/', views.TipoSancionDeleteView.as_view(), name='tiposancion_delete'),
]