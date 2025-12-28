from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.rol == 'admin'

    def handle_no_permission(self):
        raise PermissionDenied("No tienes permisos de administrador para acceder a esta página.")

class EncargadoRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.rol == 'encargado' or user.rol == 'admin')

    def handle_no_permission(self):
        raise PermissionDenied("No tienes permisos de encargado para acceder a esta página.")

class PolicialRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        # Permitir policial, encargado Y admin
        return user.is_authenticated and (user.rol == 'policial' or user.rol == 'encargado' or user.rol == 'admin')

    def handle_no_permission(self):
        raise PermissionDenied("No tienes permisos para acceder a esta página.")

# Mixin para cualquier usuario autenticado
class AuthenticatedRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        raise PermissionDenied("Debes iniciar sesión para acceder a esta página.")