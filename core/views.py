from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from catalogos.models import Unidad, Grado
from personal.models import PersonalPolicial, KardexDigital

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

@login_required
def dashboard(request):
    # Estadísticas básicas
    total_personal = PersonalPolicial.objects.count()
    personal_activo = PersonalPolicial.objects.filter(estado_actual__nombre='Activo').count()
    personal_licencia = PersonalPolicial.objects.filter(estado_actual__nombre='Licencia').count()
    
    # Personal por unidad
    personal_por_unidad = Unidad.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'total')
    
    # Personal por grado
    personal_por_grado = Grado.objects.annotate(
        total=Count('personalpolicial')
    ).values('nombre', 'abreviatura', 'total')
    
    # Últimos registros de kardex
    ultimos_registros = KardexDigital.objects.select_related('personal').order_by('-fecha_creacion')[:10]
    
    context = {
        'total_personal': total_personal,
        'personal_activo': personal_activo,
        'personal_licencia': personal_licencia,
        'personal_por_unidad': personal_por_unidad,
        'personal_por_grado': personal_por_grado,
        'ultimos_registros': ultimos_registros,
    }
    
    return render(request, 'dashboard.html', context)