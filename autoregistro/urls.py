from django.urls import path
from . import views

app_name = 'autoregistro'

urlpatterns = [
    # Admin — mismo nivel que "Agregar Personal"
    path('crear/',             views.crear_temporal,   name='crear_temporal'),
    path('temporales/',        views.lista_temporales, name='lista_temporales'),
    path('revisar/<int:pk>/',  views.revisar_registro, name='revisar_registro'),

    # Policía — completar su registro al iniciar sesión
    path('completar/',         views.completar_registro, name='completar_registro'),
]