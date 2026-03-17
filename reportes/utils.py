"""
Utilidades de bitácora.

Uso en cualquier vista o función:
    from reportes.utils import registrar_log
    registrar_log(request, 'CREAR', 'personal', 'Creó personal Juan Pérez', objeto=instancia)

Uso en CBVs (agregar el mixin):
    from reportes.utils import BitacoraMixin
    class PersonalCreateView(BitacoraMixin, PuedeCrearMixin, CreateView):
        bitacora_modulo = 'personal'
        bitacora_accion_create = 'CREAR'
        bitacora_accion_update = 'EDITAR'
        bitacora_accion_delete = 'ELIMINAR'
"""

from .models import BitacoraLog


def get_ip(request):
    """Obtiene la IP real del cliente."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def registrar_log(request, accion, modulo, descripcion, objeto=None):
    """
    Registra una entrada en la bitácora.

    Parámetros:
        request     — HttpRequest (para obtener usuario e IP)
        accion      — str: 'LOGIN', 'LOGOUT', 'CREAR', 'EDITAR', 'ELIMINAR', 'VER', 'ERROR', 'OTRO'
        modulo      — str: 'personal', 'destinos', 'catalogos', etc.
        descripcion — str: texto libre describiendo la acción
        objeto      — instancia del modelo afectado (opcional)
    """
    usuario = request.user if request.user.is_authenticated else None
    ip      = get_ip(request)

    BitacoraLog.objects.create(
        usuario     = usuario,
        accion      = accion,
        modulo      = modulo,
        descripcion = descripcion,
        objeto_id   = str(objeto.pk) if objeto else None,
        objeto_repr = str(objeto)    if objeto else None,
        ip_address  = ip,
    )


# ── Mixin para Class-Based Views ──────────────────────────────────

class BitacoraMixin:
    """
    Mixin para CreateView, UpdateView y DeleteView.
    Registra automáticamente la acción al completarse el form.

    Configuración en la vista:
        bitacora_modulo        = 'personal'   ← obligatorio
        bitacora_accion_create = 'CREAR'      ← opcional, por defecto 'CREAR'
        bitacora_accion_update = 'EDITAR'     ← opcional, por defecto 'EDITAR'
        bitacora_accion_delete = 'ELIMINAR'   ← opcional, por defecto 'ELIMINAR'
    """
    bitacora_modulo        = 'sistema'
    bitacora_accion_create = 'CREAR'
    bitacora_accion_update = 'EDITAR'
    bitacora_accion_delete = 'ELIMINAR'

    def _descripcion(self, accion, objeto):
        nombre = str(objeto)
        mapa = {
            'CREAR':    f'Creó: {nombre}',
            'EDITAR':   f'Editó: {nombre}',
            'ELIMINAR': f'Eliminó: {nombre}',
        }
        return mapa.get(accion, f'{accion}: {nombre}')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Detectar si es create o update según si el objeto tenía pk antes
        accion = self.bitacora_accion_update if self.object.pk and hasattr(self, '_es_update') else self.bitacora_accion_create
        registrar_log(
            self.request,
            accion,
            self.bitacora_modulo,
            self._descripcion(accion, self.object),
            objeto=self.object,
        )
        return response

    def post(self, request, *args, **kwargs):
        # Marca si es update para distinguirlo en form_valid
        if hasattr(self, 'get_object'):
            try:
                self.object = self.get_object()
                self._es_update = True
            except Exception:
                self._es_update = False
        return super().post(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        objeto = self.get_object()
        registrar_log(
            request,
            self.bitacora_accion_delete,
            self.bitacora_modulo,
            self._descripcion(self.bitacora_accion_delete, objeto),
            objeto=objeto,
        )
        return super().delete(request, *args, **kwargs)