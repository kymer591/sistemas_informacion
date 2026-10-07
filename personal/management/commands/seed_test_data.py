from datetime import date

from django.core.management.base import BaseCommand, CommandError

from catalogos.models import Grado, Unidad, TipoEstado, Cargo
from personal.models import PersonalPolicial, BajaPersonal, Fallecimiento

CI_PRUEBA = ['9999001', '9999002', '9999003']


class Command(BaseCommand):
    help = 'Crea (o elimina) datos de prueba sintéticos para verificar Unidad/Cargo/TipoEstado/Baja/Fallecimiento'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Elimina todos los datos de prueba creados por este comando',
        )

    def handle(self, *args, **options):
        if options['delete']:
            self._eliminar()
            return
        self._crear()

    def _crear(self):
        grado = Grado.objects.first()
        if not grado:
            raise CommandError(
                'No hay ningún Grado registrado todavía. '
                'Crea al menos uno desde Catálogos > Grados antes de correr este comando.'
            )

        unidad, _ = Unidad.objects.update_or_create(
            codigo='TEST-UNI',
            defaults=dict(
                nombre='Unidad de Pruebas',
                descripcion='Unidad sintética para verificar Fase 1-3',
                activa=True,
                ciudad='La Paz',
                direccion='Calle de Pruebas 123',
                correo_electronico='pruebas@uteppi.test',
            ),
        )
        self.stdout.write(self.style.SUCCESS(f'Unidad lista: {unidad}'))

        cargo1, _ = Cargo.objects.get_or_create(
            unidad=unidad, nombre='Comandante (Prueba)', defaults=dict(orden=1, activo=True)
        )
        cargo2, _ = Cargo.objects.get_or_create(
            unidad=unidad, nombre='Secretaria (Prueba)', defaults=dict(orden=2, activo=True)
        )
        cargo3, _ = Cargo.objects.get_or_create(
            unidad=unidad, nombre='Operador de Drones (Prueba)', defaults=dict(orden=3, activo=True)
        )
        self.stdout.write(self.style.SUCCESS(f'Cargos listos: {cargo1}, {cargo2}, {cargo3}'))

        estado_activo, _ = TipoEstado.objects.get_or_create(
            nombre='Activo (Prueba)', defaults=dict(color='#28a745', cumple_funciones=True)
        )
        estado_retiro, _ = TipoEstado.objects.get_or_create(
            nombre='Retiro Temporal (Prueba)', defaults=dict(color='#6c757d', cumple_funciones=False)
        )
        self.stdout.write(self.style.SUCCESS(
            f'TipoEstado listos: {estado_activo} (cumple={estado_activo.cumple_funciones}), '
            f'{estado_retiro} (cumple={estado_retiro.cumple_funciones})'
        ))

        personas = []
        datos_personas = [
            dict(ci=CI_PRUEBA[0], nombres='PRUEBA UNO', apellido_paterno='TESTIGO', apellido_materno='DEMO',
                 cargo=cargo1, tipo_carrera='carrera'),
            dict(ci=CI_PRUEBA[1], nombres='PRUEBA DOS', apellido_paterno='TESTIGO', apellido_materno='DEMO',
                 cargo=cargo2, tipo_carrera='servicio'),
            dict(ci=CI_PRUEBA[2], nombres='PRUEBA TRES', apellido_paterno='TESTIGO', apellido_materno='DEMO',
                 cargo=cargo3, tipo_carrera='carrera'),
        ]

        for i, datos in enumerate(datos_personas, start=1):
            persona, _ = PersonalPolicial.objects.update_or_create(
                ci=datos['ci'],
                defaults=dict(
                    codigo_identificacion=f'TEST-00{i}',
                    expedido='LP',
                    nombres=datos['nombres'],
                    apellido_paterno=datos['apellido_paterno'],
                    apellido_materno=datos['apellido_materno'],
                    fecha_nacimiento=date(1990, 1, 1),
                    genero='M',
                    grado=grado,
                    unidad=unidad,
                    estado_actual=estado_activo,
                    fecha_ingreso=date(2020, 1, 1),
                    cargo=datos['cargo'],
                    tipo_carrera=datos['tipo_carrera'],
                    activo=True,
                ),
            )
            personas.append(persona)
            self.stdout.write(self.style.SUCCESS(f'Personal de prueba listo: {persona}'))

        BajaPersonal.objects.get_or_create(
            personal=personas[1],
            defaults=dict(
                tipo_baja='retiro_temporal',
                fecha_baja=date.today(),
                motivo='Registro de prueba para verificar Fase 3',
                resolucion_tds='TEST-RES-001',
            ),
        )
        self.stdout.write(self.style.SUCCESS(f'Baja de prueba lista para: {personas[1]}'))

        Fallecimiento.objects.get_or_create(
            personal=personas[2],
            defaults=dict(
                fecha_fallecimiento=date.today(),
                causa_deceso='Causa de prueba',
                numero_certificado_defuncion='TEST-CERT-001',
            ),
        )
        self.stdout.write(self.style.SUCCESS(f'Fallecimiento de prueba listo para: {personas[2]}'))

        personas[1].refresh_from_db()
        personas[2].refresh_from_db()
        self.stdout.write(self.style.WARNING(
            f'Verifica: {personas[1]} debería tener activo={personas[1].activo} (esperado: False)'
        ))
        self.stdout.write(self.style.WARNING(
            f'Verifica: {personas[2]} debería tener activo={personas[2].activo} (esperado: False)'
        ))
        self.stdout.write(self.style.SUCCESS(
            'Listo. Revisa el Kardex de esas dos personas: deberían tener una entrada '
            'automática tipo "Cambio de Estado".'
        ))

    def _eliminar(self):
        PersonalPolicial.objects.filter(ci__in=CI_PRUEBA).delete()
        Unidad.objects.filter(codigo='TEST-UNI').delete()
        TipoEstado.objects.filter(nombre__in=['Activo (Prueba)', 'Retiro Temporal (Prueba)']).delete()
        self.stdout.write(self.style.SUCCESS('Datos de prueba eliminados.'))
        