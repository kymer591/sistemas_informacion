from django.urls import path
from . import views

urlpatterns = [
    path('', views.PersonalListView.as_view(), name='personal_list'),
    path('nuevo/', views.PersonalCreateView.as_view(), name='personal_create'),
    path('editar/<int:pk>/', views.PersonalUpdateView.as_view(), name='personal_update'),
    path('detalle/<int:pk>/', views.PersonalDetailView.as_view(), name='personal_detail'),
    path('eliminar/<int:pk>/', views.PersonalDeleteView.as_view(), name='personal_delete'),
    path('<int:personal_id>/kardex/', views.KardexPersonalListView.as_view(), name='kardex_list'),
    path('<int:personal_id>/kardex/nuevo/', views.KardexCreateView.as_view(), name='kardex_create'),
    path('permisos/', views.PermisoListView.as_view(), name='permiso_list'),
    path('permisos/nuevo/', views.PermisoCreateView.as_view(), name='permiso_create'),
    path('permisos/editar/<int:pk>/', views.PermisoUpdateView.as_view(), name='permiso_update'),
    path('permisos/aprobar/<int:pk>/', views.PermisoAprobarView.as_view(), name='permiso_aprobar'),
    path('permisos/detalle/<int:pk>/', views.PermisoDetailView.as_view(), name='permiso_detail'),
    # Sanciones
    path('sanciones/', views.SancionListView.as_view(), name='sancion_list'),
    path('sanciones/nueva/', views.SancionCreateView.as_view(), name='sancion_create'),
    path('sanciones/editar/<int:pk>/', views.SancionUpdateView.as_view(), name='sancion_update'),
    path('sanciones/detalle/<int:pk>/', views.SancionDetailView.as_view(), name='sancion_detail'),

    # Felicitaciones
    path('felicitaciones/', views.FelicitacionListView.as_view(), name='felicitacion_list'),
    path('felicitaciones/nueva/', views.FelicitacionCreateView.as_view(), name='felicitacion_create'),
    path('felicitaciones/editar/<int:pk>/', views.FelicitacionUpdateView.as_view(), name='felicitacion_update'),
    path('felicitaciones/detalle/<int:pk>/', views.FelicitacionDetailView.as_view(), name='felicitacion_detail'),
     
     
     # Destinos — lista general
    path('destinos/', views.DestinoListView.as_view(), name='destino_list'),
    path('destinos/nuevo/', views.DestinoCreateView.as_view(), name='destino_create'),
    path('destinos/editar/<int:pk>/', views.DestinoUpdateView.as_view(), name='destino_update'),
    path('destinos/detalle/<int:pk>/', views.DestinoDetailView.as_view(), name='destino_detail'),
    path('destinos/eliminar/<int:pk>/', views.DestinoDeleteView.as_view(), name='destino_delete'),

    # Destinos — por personal específico
    path('<int:personal_id>/destinos/', views.DestinoPersonalListView.as_view(), name='destino_personal_list'),
    path('<int:personal_id>/destinos/nuevo/', views.DestinoCreateView.as_view(), name='destino_personal_create'),

    # Reportes
    path('reporte/',          views.ReportePersonalView.as_view(), name='reporte_personal'),
    path('reporte/exportar/', views.exportar_personal_excel,       name='exportar_personal_excel'),
]