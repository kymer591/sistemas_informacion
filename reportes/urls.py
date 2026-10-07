from django.urls import path
from . import views
 
app_name = 'reportes'
 
urlpatterns = [
    path('personal/',          views.ReportePersonalView.as_view(), name='reporte_personal'),
    path('personal/exportar/', views.exportar_personal_excel,       name='exportar_personal_excel'),
    path('bitacora/', views.BitacoraView.as_view(), name='bitacora'),
    path('bitacora/exportar/', views.exportar_bitacora_pdf, name='exportar_bitacora_pdf'),
    path('lista-revista/', views.lista_revista_preview, name='lista_revista_preview'),
    path('lista-revista/exportar/', views.exportar_lista_revista_excel, name='exportar_lista_revista_excel'),
    path('lista-revista/exportar-pdf/', views.exportar_lista_revista_pdf, name='exportar_lista_revista_pdf'),
]
 


