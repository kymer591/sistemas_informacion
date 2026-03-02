from django.shortcuts import render

class CheckActiveUserMiddleware:
    """
    Middleware que verifica si el usuario sigue activo.
    Si fue desactivado, muestra página de cuenta desactivada.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar solo si el usuario está autenticado
        if request.user.is_authenticated:
            # Lista de rutas que NO deben verificar
            excluded_paths = [
                '/logout/',
                '/admin/',
                '/static/',
            ]
            
            # No verificar en rutas excluidas
            if not any(request.path.startswith(path) for path in excluded_paths):
                # Si el usuario está desactivado, mostrar página especial
                if not request.user.activo:
                    return render(request, 'core/cuenta_desactivada.html', {
                        'user': request.user
                    })
        
        response = self.get_response(request)
        return response