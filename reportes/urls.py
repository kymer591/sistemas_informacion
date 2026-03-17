from django.urls import path
from . import views
 
app_name = 'reportes'
 
urlpatterns = [
    path('personal/',          views.ReportePersonalView.as_view(), name='reporte_personal'),
    path('personal/exportar/', views.exportar_personal_excel,       name='exportar_personal_excel'),
    path('bitacora/', views.BitacoraView.as_view(), name='bitacora'),
]
 


