# core/middleware.py — reemplazar el archivo completo

from django.shortcuts import render, redirect


class CheckActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:

            # Rutas que NUNCA se interceptan
            excluded = [
                '/logout/',
                '/admin/',
                '/static/',
                '/autoregistro/completar/',
            ]

            if not any(request.path.startswith(p) for p in excluded):

                # 1. Usuario desactivado
                if not request.user.activo:
                    return render(request, 'core/cuenta_desactivada.html',
                                  {'user': request.user})

                # 2. Usuario temporal → solo puede ir a completar su registro
                if request.user.rol == 'temporal':
                    return redirect('autoregistro:completar_registro')

        return self.get_response(request)