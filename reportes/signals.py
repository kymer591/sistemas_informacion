from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .models import BitacoraLog
from .utils import get_ip


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    BitacoraLog.objects.create(
        usuario     = user,
        accion      = 'LOGIN',
        modulo      = 'sistema',
        descripcion = f'Inicio de sesión exitoso: {user.username}',
        ip_address  = get_ip(request),
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        BitacoraLog.objects.create(
            usuario     = user,
            accion      = 'LOGOUT',
            modulo      = 'sistema',
            descripcion = f'Cierre de sesión: {user.username}',
            ip_address  = get_ip(request),
        )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    BitacoraLog.objects.create(
        usuario     = None,
        accion      = 'ERROR',
        modulo      = 'sistema',
        descripcion = f'Intento de login fallido — usuario: {credentials.get("username", "desconocido")}',
        ip_address  = get_ip(request),
    )