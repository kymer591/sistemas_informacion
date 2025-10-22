from django.core.management.base import BaseCommand
from catalogos.models import Grado, Unidad, TipoEstado, TipoSancion, TipoFelicitacion
from core.models import SistemaConfig


class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema UTEPPI - Grados, Unidades, Estados, etc.'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando carga de datos iniciales...')
        
        # 1. CONFIGURACIÓN DEL SISTEMA
        if not SistemaConfig.objects.exists():
            SistemaConfig.objects.create(
                nombre_institucion='UTEPPI - Unidad de Tecnología Policial',
                tiempo_sesion=60
            )
            self.stdout.write('✅ Configuración del sistema creada')
        else:
            self.stdout.write('ℹ️ Configuración del sistema ya existe')

        # 2. GRADOS POLICIALES (Jerarquía de mayor a menor)
        grados_data = [
            {'nombre': 'General', 'abreviatura': 'GRAL', 'orden': 1},
            {'nombre': 'Coronel', 'abreviatura': 'CRNL', 'orden': 2},
            {'nombre': 'Teniente Coronel', 'abreviatura': 'TCNL', 'orden': 3},
            {'nombre': 'Mayor', 'abreviatura': 'MY', 'orden': 4},
            {'nombre': 'Capitán', 'abreviatura': 'CAP', 'orden': 5},
            {'nombre': 'Teniente', 'abreviatura': 'TTE', 'orden': 6},
            {'nombre': 'Subteniente', 'abreviatura': 'STTE', 'orden': 7},
            {'nombre': 'Sargento Primero', 'abreviatura': 'SGTO 1RO', 'orden': 8},
            {'nombre': 'Sargento Segundo', 'abreviatura': 'SGTO 2DO', 'orden': 9},
            {'nombre': 'Cabo', 'abreviatura': 'CBO', 'orden': 10},
            {'nombre': 'Policía', 'abreviatura': 'PLC', 'orden': 11},
        ]
        
        for grado in grados_data:
            obj, created = Grado.objects.get_or_create(
                nombre=grado['nombre'],
                defaults=grado
            )
            if created:
                self.stdout.write(f'   ✅ Grado creado: {grado["nombre"]}')

        # 3. UNIDADES POLICIALES
        unidades_data = [
            {'codigo': 'UTEPPI', 'nombre': 'Unidad de Tecnología Policial de Prevención e Investigación'},
            {'codigo': 'FELCC', 'nombre': 'Fuerza Especial de Lucha Contra el Crimen'},
            {'codigo': 'FELCV', 'nombre': 'Fuerza Especial de Lucha Contra la Violencia'},
            {'codigo': 'TRANSITO', 'nombre': 'Policía de Tránsito'},
        ]
        
        for unidad in unidades_data:
            obj, created = Unidad.objects.get_or_create(
                codigo=unidad['codigo'],
                defaults=unidad
            )
            if created:
                self.stdout.write(f'   ✅ Unidad creada: {unidad["nombre"]}')

        # 4. TIPOS DE ESTADO (Situación del personal)
        estados_data = [
            {'nombre': 'Activo', 'color': '#28a745'},        # Verde
            {'nombre': 'Licencia', 'color': '#17a2b8'},      # Azul
            {'nombre': 'Comisión', 'color': '#ffc107'},      # Amarillo
            {'nombre': 'Baja', 'color': '#dc3545'},          # Rojo
            {'nombre': 'Suspendido', 'color': '#6c757d'},    # Gris
        ]
        
        for estado in estados_data:
            obj, created = TipoEstado.objects.get_or_create(
                nombre=estado['nombre'],
                defaults=estado
            )
            if created:
                self.stdout.write(f'   ✅ Estado creado: {estado["nombre"]}')

        # 5. TIPOS DE SANCIÓN
        sanciones_data = [
            {'nombre': 'Amonestación Verbal', 'gravedad': 'leve'},
            {'nombre': 'Amonestación Escrita', 'gravedad': 'leve'},
            {'nombre': 'Suspensión Temporal', 'gravedad': 'grave'},
            {'nombre': 'Destitución', 'gravedad': 'muy_grave'},
        ]
        
        for sancion in sanciones_data:
            obj, created = TipoSancion.objects.get_or_create(
                nombre=sancion['nombre'],
                defaults=sancion
            )
            if created:
                self.stdout.write(f'   ✅ Sanción creada: {sancion["nombre"]}')

        # 6. TIPOS DE FELICITACIÓN
        felicitaciones_data = [
            {'nombre': 'Felicitación por Servicio', 'descripcion': 'Reconocimiento por buen servicio'},
            {'nombre': 'Felicitación por Mérito', 'descripcion': 'Reconocimiento por acto meritorio'},
            {'nombre': 'Felicitación por Antigüedad', 'descripcion': 'Reconocimiento por años de servicio'},
        ]
        
        for felicitacion in felicitaciones_data:
            obj, created = TipoFelicitacion.objects.get_or_create(
                nombre=felicitacion['nombre'],
                defaults=felicitacion
            )
            if created:
                self.stdout.write(f'   ✅ Felicitación creada: {felicitacion["nombre"]}')

        self.stdout.write(
            self.style.SUCCESS('🎉 ¡CARGA COMPLETADA! Todos los datos iniciales están listos.')
        )