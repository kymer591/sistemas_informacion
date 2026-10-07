from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError

from catalogos.models import Grado, Unidad, TipoEstado, Cargo
from personal.models import PersonalPolicial, DestinoPolicial, BajaPersonal, Fallecimiento

CI_DEMO = [f'8888{i:03d}' for i in range(1, 7)]
UNIDAD_CODIGO = 'LR-DEMO'


class Command(BaseCommand):
    help = 'Genera un caso de prueba completo para probar Lista de Revista (Excel/PDF)'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Elimina todos los datos de este demo')

    def handle(self, *args, **options):
        if options['delete']:
            self._eliminar()
            return
        self._crear()

    def _crear(self):
        hoy = date.today()

        unidad, _ = Unidad.objects.update_or_create(
            codigo=UNIDAD_CODIGO,
            defaults=dict(
                nombre='Unidad Demo - Lista de Revista',
                descripcion='Unidad sintética para probar Lista de Revista',
                activa=True,
                ciudad='Potosí',
                direccion='Plaza Central 10 de Noviembre',
                correo_electronico='demo.listarevista@uteppi.test',
            ),
        )
        self.stdout.write(self.style.SUCCESS(f'Unidad: {unidad}'))

        grados_data = [
            ('Capitán (Demo)', 'CAP.(D)', 10),
            ('Teniente (Demo)', 'TTE.(D)', 20),
            ('Sargento 1ro (Demo)', 'SGTO.1RO.(D)', 30),
            ('Sargento (Demo)', 'SGTO.(D)', 40),
        ]
        grados = []
        for nombre, abrev, orden in grados_data:
            g, _ = Grado.objects.get_or_create(
                abreviatura=abrev, defaults=dict(nombre=nombre, orden=orden, activo=True)
            )
            grados.append(g)
        self.stdout.write(self.style.SUCCESS(f'Grados demo listos: {[g.abreviatura for g in grados]}'))

        cargo_comandante, _ = Cargo.objects.get_or_create(
            unidad=unidad, nombre='Comandante (Demo)', defaults=dict(orden=1, activo=True)
        )
        cargo_secretaria, _ = Cargo.objects.get_or_create(
            unidad=unidad, nombre='Secretaria (Demo)', defaults=dict(orden=2, activo=True)
        )
        cargo_drones, _ = Cargo.objects.get_or_create(
            unidad=unidad, nombre='Operador de Drones (Demo)', defaults=dict(orden=3, activo=True)
        )
        self.stdout.write(self.style.SUCCESS('Cargos demo listos'))

        estado_activo, _ = TipoEstado.objects.get_or_create(
            nombre='Activo (Demo)', defaults=dict(color='#28a745', cumple_funciones=True)
        )
        estado_comision, _ = TipoEstado.objects.get_or_create(
            nombre='Comisión UNIPOL (Demo)', defaults=dict(color='#6c757d', cumple_funciones=False)
        )
        self.stdout.write(self.style.SUCCESS('Estados demo listos'))

        datos_personas = [
            dict(ci=CI_DEMO[0], nombres='CARLOS ANDRES', apellido_paterno='MAMANI', apellido_materno='QUISPE',
                 grado=grados[0], cargo=cargo_comandante, tipo_carrera='carrera', estado=estado_activo, genero='M'),
            dict(ci=CI_DEMO[1], nombres='MARIA ELENA', apellido_paterno='CONDORI', apellido_materno='FLORES',
                 grado=grados[1], cargo=cargo_secretaria, tipo_carrera='carrera', estado=estado_activo, genero='F'),
            dict(ci=CI_DEMO[2], nombres='JOSE LUIS', apellido_paterno='CHOQUE', apellido_materno='TICONA',
                 grado=grados[2], cargo=cargo_drones, tipo_carrera='servicio', estado=estado_activo, genero='M'),
            dict(ci=CI_DEMO[3], nombres='ANA PATRICIA', apellido_paterno='LOPEZ', apellido_materno='MAMANI',
                 grado=grados[3], cargo=cargo_secretaria, tipo_carrera='servicio', estado=estado_activo, genero='F'),
            dict(ci=CI_DEMO[4], nombres='LUIS FERNANDO', apellido_paterno='VARGAS', apellido_materno='ROJAS',
                 grado=grados[2], cargo=cargo_drones, tipo_carrera='carrera', estado=estado_comision, genero='M'),
            dict(ci=CI_DEMO[5], nombres='ROSA ISABEL', apellido_paterno='GUTIERREZ', apellido_materno='PINTO',
                 grado=grados[3], cargo=cargo_comandante, tipo_carrera='carrera', estado=estado_activo, genero='F'),
        ]

        personas = []
        for i, d in enumerate(datos_personas, start=1):
            persona, _ = PersonalPolicial.objects.update_or_create(
                ci=d['ci'],
                defaults=dict(
                    codigo_identificacion=f'LRDEMO-{i:03d}',
                    expedido='PT',
                    nombres=d['nombres'],
                    apellido_paterno=d['apellido_paterno'],
                    apellido_materno=d['apellido_materno'],
                    fecha_nacimiento=date(1988, 5, 15),
                    genero=d['genero'],
                    grado=d['grado'],
                    unidad=unidad,
                    estado_actual=d['estado'],
                    fecha_ingreso=date(2018, 3, 1),
                    cargo=d['cargo'],
                    tipo_carrera=d['tipo_carrera'],
                    activo=True,
                    telefono_personal='70000000',
                    correo_institucional=f"{d['nombres'].split()[0].lower()}@uteppi.test",
                    direccion_domicilio='Zona Central, calle demo',
                    otra_profesion='',
                ),
            )
            personas.append(persona)
        self.stdout.write(self.style.SUCCESS(f'{len(personas)} personas demo creadas'))

        unidad.comandante = personas[0]
        unidad.save(update_fields=['comandante'])
        self.stdout.write(self.style.SUCCESS(f'Comandante asignado: {personas[0]}'))

        # FORM-07: alta reciente (destino que inicia dentro del periodo)
        DestinoPolicial.objects.get_or_create(
            personal=personas[1],
            unidad_destino=unidad,
            fecha_inicio=hoy - timedelta(days=10),
            defaults=dict(
                tipo_destino='traslado',
                lugar_destino='Unidad Demo - Lista de Revista',
                fecha_fin=None,
                activo=True,
                descripcion='Traslado demo para probar FORM-07',
                numero_resolucion='DEMO-RES-001',
                registrado_por=None,
            ),
        )

        # FORM-08: baja reciente (destino que termina dentro del periodo)
        DestinoPolicial.objects.get_or_create(
            personal=personas[2],
            unidad_destino=unidad,
            fecha_fin=hoy - timedelta(days=5),
            defaults=dict(
                tipo_destino='traslado',
                lugar_destino='Unidad Demo - Lista de Revista',
                fecha_inicio=hoy - timedelta(days=200),
                activo=False,
                descripcion='Fin de destino demo para probar FORM-08',
                numero_resolucion='DEMO-RES-002',
                registrado_por=None,
            ),
        )
        self.stdout.write(self.style.SUCCESS('Destinos demo (alta y baja) creados'))

        BajaPersonal.objects.get_or_create(
            personal=personas[4],
            defaults=dict(
                tipo_baja='retiro_temporal',
                fecha_baja=hoy - timedelta(days=3),
                motivo='Retiro temporal demo para probar FORM-13',
                resolucion_tds='DEMO-TDS-001',
                numero_memo_escalafon='DEMO-MEMO-001',
                autoridad_firma='CNL. DEMO AUTORIDAD',
                cargo_autoridad_firma='Director Nacional de Personal (Demo)',
                fecha_notificacion=hoy - timedelta(days=2),
            ),
        )
        self.stdout.write(self.style.SUCCESS(f'Baja demo registrada para: {personas[4]}'))

        Fallecimiento.objects.get_or_create(
            personal=personas[5],
            defaults=dict(
                fecha_fallecimiento=hoy - timedelta(days=2),
                causa_deceso='Causa demo para probar FORM-13',
                numero_certificado_defuncion='DEMO-CERT-001',
                entidad='SERECI (Demo)',
                autoridad_firma='CNL. DEMO AUTORIDAD',
                numero_informe_trabajo_social='DEMO-INF-001',
                fecha_informe=hoy - timedelta(days=1),
                direccion_departamental_salud='SEDES Potosí (Demo)',
            ),
        )
        self.stdout.write(self.style.SUCCESS(f'Fallecimiento demo registrado para: {personas[5]}'))

        periodo_inicio = (hoy - timedelta(days=60)).isoformat()
        periodo_fin = hoy.isoformat()

        self.stdout.write(self.style.WARNING('\n────────────────────────────────────────'))
        self.stdout.write(self.style.WARNING('Para ver el reporte, ve a esta URL (ajusta el dominio):'))
        self.stdout.write(self.style.SUCCESS(
            f'/reportes/lista-revista/?unidad={unidad.pk}&fecha_inicio={periodo_inicio}&fecha_fin={periodo_fin}'
        ))
        self.stdout.write(self.style.WARNING('────────────────────────────────────────'))
        self.stdout.write(self.style.WARNING('Qué deberías ver:'))
        self.stdout.write('  FORM-01/03: 6 personas repartidas en 3 cargos, por grado y carrera/servicio')
        self.stdout.write('  FORM-02 Sección B: 1 persona en "Comisión UNIPOL (Demo)"')
        self.stdout.write('  FORM-07: 1 alta (MARIA ELENA CONDORI)')
        self.stdout.write('  FORM-08: 1 baja (JOSE LUIS CHOQUE)')
        self.stdout.write('  FORM-11: 6 personas activas ordenadas por grado')
        self.stdout.write('  FORM-12: agrupado por los 3 cargos')
        self.stdout.write('  FORM-13: 1 retiro temporal (LUIS FERNANDO VARGAS) + 1 fallecido (ROSA ISABEL GUTIERREZ)')

    def _eliminar(self):
        PersonalPolicial.objects.filter(ci__in=CI_DEMO).delete()
        Unidad.objects.filter(codigo=UNIDAD_CODIGO).delete()
        Cargo.objects.filter(nombre__endswith='(Demo)').delete()
        TipoEstado.objects.filter(nombre__endswith='(Demo)').delete()
        Grado.objects.filter(abreviatura__endswith='(D)').delete()
        self.stdout.write(self.style.SUCCESS('Datos demo de Lista de Revista eliminados.'))