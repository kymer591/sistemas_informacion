from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

class AdminRequiredMixin(UserPassesTestMixin):
    """
    Mixin que requiere que el usuario sea Administrador
    Acceso: Solo Administrador
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.es_administrador()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ Acceso denegado. Solo los Administradores pueden acceder a esta sección."
        )
        raise PermissionDenied(
            "Solo los usuarios con rol de Administrador pueden acceder a esta página."
        )


class OficialAdministrativoRequiredMixin(UserPassesTestMixin):
    """
    Mixin que requiere que el usuario sea Oficial Administrativo o Administrador
    Acceso: Administrador + Oficial Administrativo
    """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (
            user.es_oficial_administrativo() or user.es_administrador()
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ Acceso denegado. Necesitas permisos de Oficial Administrativo o superior."
        )
        raise PermissionDenied(
            "Solo los usuarios con rol de Oficial Administrativo o Administrador "
            "pueden acceder a esta página."
        )


class UsuarioAutorizadoRequiredMixin(UserPassesTestMixin):
    """
    Mixin que requiere que el usuario esté autenticado (cualquier rol)
    Acceso: Todos los roles autenticados
    """
    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ Debes iniciar sesión para acceder a esta página."
        )
        raise PermissionDenied("Debes iniciar sesión para acceder a esta página.")


class PuedeCrearMixin(UserPassesTestMixin):
    """
    Mixin que verifica si el usuario puede crear registros
    Acceso: Administrador + Oficial Administrativo
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.puede_crear()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ No tienes permisos para crear nuevos registros."
        )
        raise PermissionDenied("No tienes permisos para crear nuevos registros.")


class PuedeEditarMixin(UserPassesTestMixin):
    """
    Mixin que verifica si el usuario puede editar registros
    Acceso: Administrador + Oficial Administrativo
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.puede_editar()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ No tienes permisos para editar registros."
        )
        raise PermissionDenied("No tienes permisos para editar registros.")


class PuedeEliminarMixin(UserPassesTestMixin):
    """
    Mixin que verifica si el usuario puede eliminar registros
    Acceso: Solo Administrador
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.puede_eliminar()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ Solo los Administradores pueden eliminar registros."
        )
        raise PermissionDenied("Solo los Administradores pueden eliminar registros.")


class PuedeAprobarPermisosMixin(UserPassesTestMixin):
    """
    Mixin que verifica si el usuario puede aprobar permisos
    Acceso: Administrador + Oficial Administrativo
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.puede_aprobar_permisos()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ No tienes permisos para aprobar solicitudes."
        )
        raise PermissionDenied("No tienes permisos para aprobar solicitudes.")


class PuedeGestionarSancionesMixin(UserPassesTestMixin):
    """
    Mixin que verifica si el usuario puede gestionar sanciones
    Acceso: Administrador + Oficial Administrativo
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.puede_gestionar_sanciones()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(
            self.request, 
            "❌ No tienes permisos para gestionar sanciones."
        )
        raise PermissionDenied("No tienes permisos para gestionar sanciones.")


# ============================================
# MIXINS DE COMPATIBILIDAD (para migración)
# ============================================
# Estos mantienen la compatibilidad con el código existente

class EncargadoRequiredMixin(OficialAdministrativoRequiredMixin):
    """
    Alias de compatibilidad: EncargadoRequiredMixin -> OficialAdministrativoRequiredMixin
    DEPRECADO: Usar OficialAdministrativoRequiredMixin en su lugar
    """
    pass


class PolicialRequiredMixin(UsuarioAutorizadoRequiredMixin):
    """
    Alias de compatibilidad: PolicialRequiredMixin -> UsuarioAutorizadoRequiredMixin
    DEPRECADO: Usar UsuarioAutorizadoRequiredMixin en su lugar
    """
    pass


class AuthenticatedRequiredMixin(UsuarioAutorizadoRequiredMixin):
    """
    Alias de compatibilidad: AuthenticatedRequiredMixin -> UsuarioAutorizadoRequiredMixin
    DEPRECADO: Usar UsuarioAutorizadoRequiredMixin en su lugar
    """
    pass