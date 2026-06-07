from django.urls import path
from . import views

app_name = 'autoregistro'

urlpatterns = [
    # Administrativo — lista y revisión
    path('temporales/',                           views.lista_temporales,        name='lista_temporales'),
    path('revisar/<int:pk>/',                     views.revisar_registro,        name='revisar_registro'),

    # Desde personal_detail — crear usuario temporal
    path('crear-desde-detalle/<int:personal_id>/', views.crear_usuario_temporal, name='crear_usuario_temporal'),

    # Policía — completar su propio registro
    path('completar/',                             views.completar_registro,      name='completar_registro'),
]