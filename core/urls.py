from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.custom_login, name='login'),  # ← Usa la función, no la clase
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # core/urls.py
    path('cambiar-rol/<int:personal_id>/', views.cambiar_rol_usuario, name='cambiar_rol'),

    # Gestión de roles
    path('asignar-roles/', views.AsignarRolListView.as_view(), name='asignar_rol_list'),
    path('asignar-roles/<int:pk>/', views.AsignarRolUpdateView.as_view(), name='asignar_rol'),
]