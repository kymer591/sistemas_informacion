"""
Seed AMPLIADO para probar la Lista de Revista con un escenario más realista.

Uso:
    python manage.py seed_lista_revista_demo_ampliado              # crea el escenario base
    python manage.py seed_lista_revista_demo_ampliado --mover      # aplica una ronda de movimientos
    python manage.py seed_lista_revista_demo_ampliado --mover --veces 3
    python manage.py seed_lista_revista_demo_ampliado --casos-borde
    python manage.py seed_lista_revista_demo_ampliado --delete     # borra solo lo que creó este comando

Es independiente de `seed_lista_revista_demo` (el de 6 personas): comparte la unidad LR-DEMO y
los grados/cargos/estados que ya existan, y agrega los suyos. Todo lleva el sufijo "(Demo)" y los
CI de las personas empiezan con 9999, así --delete nunca toca datos reales.
"""
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db.models import ProtectedError

from catalogos.models import Cargo, Grado, TipoEstado, Unidad
from personal.models import (
    BajaPersonal, DestinoPolicial, Fallecimiento, KardexDigital, PersonalPolicial,
)

UNIDAD_CODIGO = 'LR-DEMO'
UNIDAD_B_CODIGO = 'LR-DEMO-B'
PREFIJO_CI = '9999'

# (clave, nombre, abreviatura, orden) — de mayor a menor jerarquía
GRADOS = [
    ('cnl',     'Coronel (Demo)',              'CNL.(D)',       10),
    ('tcnl',    'Teniente Coronel (Demo)',     'TCNL.(D)',      20),
    ('my',      'Mayor (Demo)',                'MY.(D)',        30),
    ('cap',     'Capitán (Demo)',              'CAP.(D)',       40),
    ('tte',     'Teniente (Demo)',             'TTE.(D)',       50),
    ('sbtte',   'Subteniente (Demo)',          'SBTTE.(D)',     60),
    ('sof_sup', 'Suboficial Superior (Demo)',  'SOF.SUP.(D)',   70),
    ('sof_my',  'Suboficial Maestre (Demo)',   'SOF.MY.(D)',    80),
    ('sof_1',   'Suboficial Primero (Demo)',   'SOF.1RO.(D)',   90),
    ('sof_2',   'Suboficial Segundo (Demo)',   'SOF.2DO.(D)',  100),
    ('sgto_my', 'Sargento Mayor (Demo)',       'SGTO.MY.(D)',  110),
    ('sgto_1',  'Sargento 1ro (Demo)',         'SGTO.1RO.(D)', 120),
    ('sgto_2',  'Sargento Segundo (Demo)',     'SGTO.2DO.(D)', 130),
    ('sgto',    'Sargento (Demo)',             'SGTO.(D)',     140),
]
ORDEN_GRADOS = [g[0] for g in GRADOS]
# estos 4 grados, 3 cargos y 2 estados ya los crea el seed original: no se borran con --delete
COMPARTIDOS_GRADOS = {'CAP.(D)', 'TTE.(D)', 'SGTO.1RO.(D)', 'SGTO.(D)'}

CARGOS = [
    'Comandante (Demo)', 'Jefe de Sección Personal (Demo)', 'Secretaria (Demo)',
    'Encargada de Soporte y Mantenimiento (Demo)', 'Encargado de Drones (Demo)',
    'Operador de Drones (Demo)', 'Analista de Información (Demo)',
    'Auxiliar Administrativo (Demo)', 'Chofer (Demo)', 'Seguridad y Guardia (Demo)',
]
COMPARTIDOS_CARGOS = {'Comandante (Demo)', 'Secretaria (Demo)', 'Operador de Drones (Demo)'}

# clave -> (nombre, color, cumple_funciones)
ESTADOS = {
    'activo':     ('Activo (Demo)',                    '#28a745', True),
    'unipol':     ('Comisión UNIPOL (Demo)',           '#6c757d', False),
    'canes':      ('Comisión CANES (Demo)',            '#6c757d', False),
    'dirnal':     ('Comisión Dir. Nal. (Demo)',        '#6c757d', False),
    'suspension': ('Suspensión Indefinida (Demo)',     '#fd7e14', False),
    'desertor':   ('Desertor (Demo)',                  '#dc3545', False),
    'fiscalia':   ('A Disposición Fiscalía (Demo)',    '#dc3545', False),
    'item0':      ('Item 0 Gobernación (Demo)',        '#17a2b8', False),
    'baja':       ('Baja Definitiva (Demo)',           '#343a40', False),
    'retiro':     ('Retiro Temporal (Demo)',           '#343a40', False),
    'licencia':   ('Licencia Indefinida (Demo)',       '#343a40', False),
    'fallecido':  ('Fallecido (Demo)',                 '#000000', False),
}
COMPARTIDOS_ESTADOS = {'Activo (Demo)', 'Comisión UNIPOL (Demo)'}

NOMBRES_M = ['CARLOS ANDRES', 'JOSE LUIS', 'LUIS FERNANDO', 'JUAN CARLOS', 'MARIO', 'RENE', 'EDGAR',
             'FREDDY', 'OSCAR', 'WILLIAM', 'DAVID', 'RICHARD', 'HUGO', 'MARCELO', 'PABLO', 'VICTOR']
NOMBRES_F = ['MARIA ELENA', 'ANA PATRICIA', 'ROSA ISABEL', 'DANIELA', 'CLAUDIA', 'SANDRA', 'LILIANA',
             'VERONICA', 'PATRICIA', 'GABRIELA', 'KAREN', 'JULIA']
APELLIDOS = ['MAMANI', 'QUISPE', 'CONDORI', 'FLORES', 'CHOQUE', 'TICONA', 'LOPEZ', 'VARGAS', 'ROJAS',
             'GUTIERREZ', 'PINTO', 'COPA', 'APAZA', 'COLQUE', 'HUANCA', 'CRUZ', 'MENDOZA', 'ARIAS',
             'GARCIA', 'FERNANDEZ', 'SILES', 'CLAROS', 'MIRANDA', 'ROMERO']
EXPEDIDOS = ['PT', 'LP', 'CB', 'OR', 'SC', 'CH']
CALLES = ['Calle Perú', 'Av. Camacho', 'Calle Bolívar', 'Zona Central', 'Barrio Minero', 'Av. Villazón',
          'Calle Linares', 'Plan 3000']
PROFESIONES = ['', '', '', 'LIC. EN DERECHO', 'TEC. SUP. EN SISTEMAS', 'LIC. EN CONTADURIA', '']

# Plantilla del escenario base.
#   mov: None | alta | alta_vieja | baja_traslado | baja_traslado_vieja |
#        baja_def | retiro | licencia | baja_vieja | fallecido | fallecido_viejo
ROSTER = [
    # grado,   cargo,                                              tipo,      estado,       mov
    ('cnl',    'Comandante (Demo)',                                'carrera', 'activo',     None),
    ('tcnl',   'Jefe de Sección Personal (Demo)',                  'carrera', 'activo',     None),
    ('my',     'Jefe de Sección Personal (Demo)',                  'carrera', 'activo',     None),
    ('cap',    'Analista de Información (Demo)',                   'carrera', 'activo',     None),
    ('cap',    'Analista de Información (Demo)',                   'carrera', 'activo',     'alta'),
    ('tte',    'Encargado de Drones (Demo)',                       'carrera', 'activo',     None),
    ('tte',    'Encargado de Drones (Demo)',                       'carrera', 'activo',     'alta'),
    ('sbtte',  'Analista de Información (Demo)',                   'carrera', 'activo',     None),
    ('sof_sup', 'Secretaria (Demo)',                               'servicio', 'activo',    None),
    ('sof_my', 'Encargada de Soporte y Mantenimiento (Demo)',      'servicio', 'activo',    None),
    ('sof_1',  'Encargada de Soporte y Mantenimiento (Demo)',      'carrera', 'activo',     'alta'),
    ('sof_2',  'Auxiliar Administrativo (Demo)',                   'servicio', 'activo',    None),
    ('sgto_my', 'Operador de Drones (Demo)',                       'carrera', 'activo',     None),
    ('sgto_my', 'Operador de Drones (Demo)',                       'servicio', 'activo',    None),
    ('sgto_1', 'Operador de Drones (Demo)',                        'carrera', 'activo',     'alta'),
    ('sgto_1', 'Operador de Drones (Demo)',                        'servicio', 'activo',    None),
    ('sgto_2', 'Chofer (Demo)',                                    'carrera', 'activo',     None),
    ('sgto_2', 'Chofer (Demo)',                                    'servicio', 'activo',    None),
    ('sgto',   'Seguridad y Guardia (Demo)',                       'carrera', 'activo',     None),
    ('sgto',   'Seguridad y Guardia (Demo)',                       'carrera', 'activo',     None),
    ('sgto',   'Seguridad y Guardia (Demo)',                       'servicio', 'activo',    'alta'),
    ('sgto',   'Seguridad y Guardia (Demo)',                       'servicio', 'activo',    None),
    ('sgto',   'Auxiliar Administrativo (Demo)',                   'servicio', 'activo',    'alta_vieja'),
    # --- se fueron a otra unidad (FORM-08) ---
    ('cap',    'Analista de Información (Demo)',                   'carrera', 'activo',     'baja_traslado'),
    ('sbtte',  'Operador de Drones (Demo)',                        'carrera', 'activo',     'baja_traslado'),
    ('sgto_1', 'Chofer (Demo)',                                    'servicio', 'activo',    'baja_traslado'),
    ('sgto',   'Seguridad y Guardia (Demo)',                       'carrera', 'activo',     'baja_traslado'),
    ('tte',    'Encargado de Drones (Demo)',                       'carrera', 'activo',     'baja_traslado_vieja'),
    # --- no cumplen funciones (FORM-02 sección B) ---
    ('tte',    'Encargado de Drones (Demo)',                       'carrera', 'unipol',     None),
    ('sgto_1', 'Operador de Drones (Demo)',                        'servicio', 'unipol',    None),
    ('sof_2',  'Analista de Información (Demo)',                   'carrera', 'canes',      None),
    ('cap',    'Jefe de Sección Personal (Demo)',                  'carrera', 'dirnal',     None),
    ('sgto',   'Seguridad y Guardia (Demo)',                       'servicio', 'suspension', None),
    ('sgto_2', 'Chofer (Demo)',                                    'carrera', 'desertor',   None),
    ('sof_1',  'Auxiliar Administrativo (Demo)',                   'servicio', 'fiscalia',  None),
    ('sbtte',  'Analista de Información (Demo)',                   'carrera', 'item0',      None),
    # --- bajas y fallecimientos (FORM-13) ---
    ('sgto_my', 'Chofer (Demo)',                                   'carrera', 'baja',       'baja_def'),
    ('tte',    'Operador de Drones (Demo)',                        'carrera', 'retiro',     'retiro'),
    ('sof_my', 'Secretaria (Demo)',                                'servicio', 'licencia',  'licencia'),
    ('sgto_2', 'Seguridad y Guardia (Demo)',                       'carrera', 'baja',       'baja_vieja'),
    ('sof_1',  'Auxiliar Administrativo (Demo)',                   'servicio', 'fallecido', 'fallecido'),
    ('sgto',   'Chofer (Demo)',                                    'carrera', 'fallecido',  'fallecido'),
    ('my',     'Analista de Información (Demo)',                   'carrera', 'fallecido',  'fallecido_viejo'),
]

# días atrás para cada tipo de movimiento (el periodo por defecto del reporte es de 60 días)
FECHAS = {
    'alta': [5, 12, 20, 33, 45],
    'alta_vieja': [150],
    'baja_traslado': [4, 15, 28, 50],
    'baja_traslado_vieja': [120],
    'baja_def': [7], 'retiro': [18], 'licencia': [40], 'baja_vieja': [200],
    'fallecido': [9, 35], 'fallecido_viejo': [300],
}


class Command(BaseCommand):
    help = 'Escenario ampliado (≈40 personas y varios movimientos) para probar la Lista de Revista'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Elimina lo creado por este comando')
        parser.add_argument('--mover', action='store_true',
                            help='Aplica una ronda de movimientos (ascensos, cambios de cargo/estado, altas, bajas)')
        parser.add_argument('--veces', type=int, default=1, help='Cuántas rondas de movimientos aplicar')
        parser.add_argument('--casos-borde', action='store_true',
                            help='Agrega casos que deben dar avisos: grado sin columna oficial y cargo de otra unidad')
        parser.add_argument('--semilla', type=int, default=None, help='Semilla para repetir los mismos movimientos')

    # ───────────────────────────── entrada ─────────────────────────────
    def handle(self, *args, **o):
        self.rng = random.Random(o['semilla'])
        self.hoy = date.today()
        if o['delete']:
            return self._eliminar()
        self._preparar_catalogos()
        if o['mover']:
            if not PersonalPolicial.objects.filter(ci__startswith=PREFIJO_CI).exists():
                self.stdout.write(self.style.WARNING('No hay escenario base: lo creo primero.'))
                self._crear_base()
            for n in range(1, o['veces'] + 1):
                self.stdout.write(self.style.MIGRATE_HEADING(f'\n── Ronda de movimientos {n} ──'))
                self._ronda_movimientos()
        elif not PersonalPolicial.objects.filter(ci__startswith=PREFIJO_CI).exists():
            self._crear_base()
        else:
            self.stdout.write(self.style.WARNING(
                'El escenario base ya existe. Usa --mover para simular movimientos o --delete para empezar de cero.'))
        if o['casos_borde']:
            self._casos_borde()
        self._resumen()

    # ───────────────────────────── catálogos ─────────────────────────────
    def _preparar_catalogos(self):
        self.unidad, _ = Unidad.objects.get_or_create(
            codigo=UNIDAD_CODIGO,
            defaults=dict(nombre='Unidad Demo - Lista de Revista', activa=True, ciudad='Potosí',
                          descripcion='Unidad sintética para probar Lista de Revista',
                          direccion='Plaza Central 10 de Noviembre',
                          correo_electronico='demo.listarevista@uteppi.test'),
        )
        self.unidad_b, _ = Unidad.objects.get_or_create(
            codigo=UNIDAD_B_CODIGO,
            defaults=dict(nombre='Unidad Demo Destino B', activa=True, ciudad='Sucre',
                          descripcion='Unidad a la que se trasladan los destinados (demo)'),
        )
        self.grados = {}
        for clave, nombre, abrev, orden in GRADOS:
            g, _ = Grado.objects.get_or_create(
                abreviatura=abrev, defaults=dict(nombre=nombre, orden=orden, activo=True))
            self.grados[clave] = g
        self.cargos = {}
        for i, nombre in enumerate(CARGOS, start=1):
            c, _ = Cargo.objects.get_or_create(
                unidad=self.unidad, nombre=nombre, defaults=dict(orden=i, activo=True))
            self.cargos[nombre] = c
        self.estados = {}
        for clave, (nombre, color, cumple) in ESTADOS.items():
            e, _ = TipoEstado.objects.get_or_create(
                nombre=nombre, defaults=dict(color=color, cumple_funciones=cumple))
            self.estados[clave] = e

    # ───────────────────────────── helpers ─────────────────────────────
    def _siguiente_ci(self):
        usados = PersonalPolicial.objects.filter(ci__startswith=PREFIJO_CI).values_list('ci', flat=True)
        n = max([int(ci[len(PREFIJO_CI):]) for ci in usados if ci[len(PREFIJO_CI):].isdigit()] or [0]) + 1
        return f'{PREFIJO_CI}{n:03d}'

    def _crear_persona(self, grado, cargo, tipo, estado, unidad=None):
        genero = self.rng.choice(['M', 'M', 'F'])
        nombres = self.rng.choice(NOMBRES_F if genero == 'F' else NOMBRES_M)
        ap1, ap2 = self.rng.sample(APELLIDOS, 2)
        ci = self._siguiente_ci()
        return PersonalPolicial.objects.create(
            codigo_identificacion=f'LRD2-{ci}', ci=ci, expedido=self.rng.choice(EXPEDIDOS),
            nombres=nombres, apellido_paterno=ap1, apellido_materno=ap2,
            fecha_nacimiento=date(self.rng.randint(1975, 1999), self.rng.randint(1, 12), self.rng.randint(1, 28)),
            genero=genero, grado=self.grados[grado], unidad=unidad or self.unidad,
            estado_actual=self.estados[estado], fecha_ingreso=date(self.rng.randint(2005, 2022), 3, 1),
            cargo=self.cargos[cargo] if cargo else None, tipo_carrera=tipo, activo=True,
            telefono_personal=f'7{self.rng.randint(1000000, 7999999)}',
            correo_institucional=f'{nombres.split()[0].lower()}.{ap1.lower()}{ci[-3:]}@uteppi.test',
            direccion_domicilio=f'{self.rng.choice(CALLES)} Nº {self.rng.randint(1, 300)}',
            otra_profesion=self.rng.choice(PROFESIONES),
        )

    def _destino(self, persona, tipo, unidad_destino, inicio, fin, lugar, descripcion):
        return DestinoPolicial.objects.create(
            personal=persona, tipo_destino=tipo, unidad_destino=unidad_destino, lugar_destino=lugar,
            fecha_inicio=inicio, fecha_fin=fin, activo=fin is None, descripcion=descripcion,
            numero_resolucion=f'DEMO-RES-{self.rng.randint(100, 999)}',
        )

    def _baja(self, persona, tipo, dias):
        BajaPersonal.objects.create(
            personal=persona, tipo_baja=tipo, fecha_baja=self.hoy - timedelta(days=dias),
            motivo=f'{tipo.replace("_", " ").capitalize()} (demo)',
            resolucion_tds=f'DEMO-TDS-{self.rng.randint(100, 999)}',
            numero_memo_escalafon=f'DEMO-MEMO-{self.rng.randint(100, 999)}',
            autoridad_firma='CNL. DEMO AUTORIDAD', cargo_autoridad_firma='Director Nacional de Personal (Demo)',
            fecha_notificacion=self.hoy - timedelta(days=max(dias - 1, 0)),
        )

    def _fallecimiento(self, persona, dias):
        Fallecimiento.objects.create(
            personal=persona, fecha_fallecimiento=self.hoy - timedelta(days=dias),
            causa_deceso=self.rng.choice(['Enfermedad (demo)', 'Accidente de tránsito (demo)']),
            numero_certificado_defuncion=f'DEMO-CERT-{self.rng.randint(100, 999)}', entidad='SERECI (Demo)',
            autoridad_firma='CNL. DEMO AUTORIDAD', numero_informe_trabajo_social=f'DEMO-INF-{self.rng.randint(100, 999)}',
            fecha_informe=self.hoy - timedelta(days=max(dias - 1, 0)),
            direccion_departamental_salud='SEDES Potosí (Demo)',
        )

    # ───────────────────────────── escenario base ─────────────────────────────
    def _crear_base(self):
        contadores = {k: 0 for k in FECHAS}
        creadas = 0
        for grado, cargo, tipo, estado, mov in ROSTER:
            en_otra = mov in ('baja_traslado', 'baja_traslado_vieja')
            p = self._crear_persona(grado, cargo, tipo, estado, unidad=self.unidad_b if en_otra else None)
            creadas += 1
            if mov is None:
                continue
            dias = FECHAS[mov][contadores[mov] % len(FECHAS[mov])]
            contadores[mov] += 1
            if mov in ('alta', 'alta_vieja'):
                self._destino(p, 'asignacion', self.unidad, self.hoy - timedelta(days=dias), None,
                              'Unidad Demo - Lista de Revista', 'Alta por traslado (demo)')
            elif en_otra:
                self._destino(p, 'asignacion', self.unidad, self.hoy - timedelta(days=dias + 200),
                              self.hoy - timedelta(days=dias), 'Unidad Demo - Lista de Revista',
                              'Destino concluido, pasa a otra unidad (demo)')
            elif mov == 'baja_def' or mov == 'baja_vieja':
                self._baja(p, 'baja_definitiva', dias)
            elif mov == 'retiro':
                self._baja(p, 'retiro_temporal', dias)
            elif mov == 'licencia':
                self._baja(p, 'licencia_indefinida', dias)
            elif mov in ('fallecido', 'fallecido_viejo'):
                self._fallecimiento(p, dias)

        if self.unidad.comandante_id is None:
            cmd = PersonalPolicial.objects.filter(ci__startswith=PREFIJO_CI, unidad=self.unidad,
                                                  grado=self.grados['cnl']).first()
            if cmd:
                self.unidad.comandante = cmd
                self.unidad.save(update_fields=['comandante'])
        self.stdout.write(self.style.SUCCESS(f'Escenario base creado: {creadas} personas.'))

    # ───────────────────────────── movimientos ─────────────────────────────
    def _demo_activos(self):
        return list(PersonalPolicial.objects.filter(
            ci__startswith=PREFIJO_CI, unidad=self.unidad, activo=True,
            estado_actual__cumple_funciones=True).select_related('grado', 'cargo'))

    def _ronda_movimientos(self):
        log = self.stdout.write
        activos = self._demo_activos()

        # 1) ascensos
        candidatos = [p for p in activos if self._clave(p.grado) not in (None, 'cnl')]
        for p in self.rng.sample(candidatos, min(2, len(candidatos))):
            actual = self._clave(p.grado)
            nuevo = ORDEN_GRADOS[max(ORDEN_GRADOS.index(actual) - 1, 0)]
            ant = p.grado
            p.grado = self.grados[nuevo]
            p.save(update_fields=['grado'])
            KardexDigital.objects.create(
                personal=p, tipo_registro='ascenso', fecha_registro=self.hoy,
                descripcion=f'Ascenso de {ant.nombre} a {p.grado.nombre} (demo)',
                grado_anterior=ant, grado_nuevo=p.grado)
            log(f'  ASCENSO        {p.nombre_completo()}: {ant.abreviatura} → {p.grado.abreviatura}')

        # 2) a comisión / de vuelta a activo
        for p in self.rng.sample(activos, min(1, len(activos))):
            clave = self.rng.choice(['unipol', 'canes', 'dirnal'])
            p.estado_actual = self.estados[clave]
            p.save(update_fields=['estado_actual'])
            log(f'  A COMISIÓN     {p.nombre_completo()} → {self.estados[clave].nombre}')
        en_comision = list(PersonalPolicial.objects.filter(
            ci__startswith=PREFIJO_CI, unidad=self.unidad, activo=True,
            estado_actual__cumple_funciones=False))
        for p in self.rng.sample(en_comision, min(1, len(en_comision))):
            anterior = p.estado_actual.nombre
            p.estado_actual = self.estados['activo']
            p.save(update_fields=['estado_actual'])
            log(f'  RETORNA        {p.nombre_completo()}: {anterior} → Activo')

        # 3) cambios de cargo
        for p in self.rng.sample(activos, min(2, len(activos))):
            otros = [c for n, c in self.cargos.items() if c.pk != (p.cargo_id or 0) and n != 'Comandante (Demo)']
            nuevo = self.rng.choice(otros)
            anterior = p.cargo.nombre if p.cargo else '(sin cargo)'
            p.cargo = nuevo
            p.save(update_fields=['cargo'])
            log(f'  CAMBIO CARGO   {p.nombre_completo()}: {anterior} → {nuevo.nombre}')

        # 4) alta nueva (FORM-07)
        grado = self.rng.choice(ORDEN_GRADOS[4:])
        nueva = self._crear_persona(grado, self.rng.choice([c for c in CARGOS if c != 'Comandante (Demo)']),
                                    self.rng.choice(['carrera', 'servicio']), 'activo')
        self._destino(nueva, 'asignacion', self.unidad, self.hoy - timedelta(days=self.rng.randint(0, 3)), None,
                      'Unidad Demo - Lista de Revista', 'Alta por traslado (demo, simulación)')
        log(f'  ALTA           {nueva.nombre_completo()} ({nueva.grado.abreviatura}) como {nueva.cargo.nombre}')

        # 5) traslado a otra unidad (FORM-08)
        activos = self._demo_activos()
        candidatos = [p for p in activos if p.pk != nueva.pk and self._clave(p.grado) not in (None, 'cnl')]
        if candidatos:
            p = self.rng.choice(candidatos)
            self._destino(p, 'asignacion', self.unidad, self.hoy - timedelta(days=300),
                          self.hoy - timedelta(days=self.rng.randint(0, 3)),
                          'Unidad Demo - Lista de Revista', 'Concluye destino, pasa a otra unidad (demo)')
            p.unidad = self.unidad_b
            p.save(update_fields=['unidad'])
            log(f'  BAJA TRASLADO  {p.nombre_completo()} → {self.unidad_b.nombre}')

        # 6) eventos poco frecuentes
        activos = self._demo_activos()
        if activos and self.rng.random() < 0.4:
            p = self.rng.choice([a for a in activos if self._clave(a.grado) not in (None, 'cnl')] or activos)
            tipo, clave = self.rng.choice([('baja_definitiva', 'baja'), ('retiro_temporal', 'retiro'),
                                           ('licencia_indefinida', 'licencia')])
            p.estado_actual = self.estados[clave]
            p.save(update_fields=['estado_actual'])
            self._baja(p, tipo, self.rng.randint(0, 3))
            log(f'  BAJA           {p.nombre_completo()}: {tipo}')
        activos = self._demo_activos()
        if activos and self.rng.random() < 0.2:
            p = self.rng.choice([a for a in activos if self._clave(a.grado) not in (None, 'cnl')] or activos)
            p.estado_actual = self.estados['fallecido']
            p.save(update_fields=['estado_actual'])
            self._fallecimiento(p, self.rng.randint(0, 3))
            log(f'  FALLECIMIENTO  {p.nombre_completo()}')

    @staticmethod
    def _clave(grado):
        for clave, _n, abrev, _o in GRADOS:
            if grado.abreviatura == abrev:
                return clave
        return None

    # ───────────────────────────── casos borde ─────────────────────────────
    def _casos_borde(self):
        cabo, _ = Grado.objects.get_or_create(
            abreviatura='CBO.(D)', defaults=dict(nombre='Cabo (Demo)', orden=150, activo=True))
        self.grados['cabo'] = cabo
        if not PersonalPolicial.objects.filter(ci__startswith=PREFIJO_CI, grado=cabo).exists():
            self._crear_persona('cabo', 'Chofer (Demo)', 'servicio', 'activo')
            self.stdout.write(self.style.WARNING(
                '  Caso borde: 1 persona con grado "Cabo (Demo)" → debe salir el AVISO de grado sin columna.'))
        otro = Cargo.objects.filter(unidad=self.unidad_b, nombre='Cargo de otra unidad (Demo)').first()
        if otro is None:
            otro = Cargo.objects.create(unidad=self.unidad_b, nombre='Cargo de otra unidad (Demo)', orden=1)
        if not PersonalPolicial.objects.filter(ci__startswith=PREFIJO_CI, cargo=otro).exists():
            p = self._crear_persona('tte', 'Chofer (Demo)', 'carrera', 'activo')
            p.cargo = otro
            p.save(update_fields=['cargo'])
            self.stdout.write(self.style.WARNING(
                '  Caso borde: 1 persona con cargo de OTRA unidad → debe salir en la fila "OTROS" del FORM-01.'))

    # ───────────────────────────── resumen ─────────────────────────────
    def _resumen(self):
        u = self.unidad
        ini, fin = self.hoy - timedelta(days=60), self.hoy
        activos = PersonalPolicial.objects.filter(unidad=u, activo=True, cargo__isnull=False)
        total_activos = activos.count()
        sin_columna = activos.exclude(grado__abreviatura__in=[g[2] for g in GRADOS]).count()
        no_cumple = PersonalPolicial.objects.filter(unidad=u, estado_actual__cumple_funciones=False).count()
        w, ok = self.stdout.write, self.style.SUCCESS
        w(ok('\n════════════ QUÉ DEBERÍAS VER (periodo: últimos 60 días) ════════════'))
        w(f'URL:  /reportes/lista-revista/?unidad={u.pk}&fecha_inicio={ini.isoformat()}&fecha_fin={fin.isoformat()}')
        w(f'FORM-01 total (activos con cargo, unidad {u.codigo}): {total_activos}'
          + (f'   (de ellos {sin_columna} con grado sin columna oficial → aviso)' if sin_columna else ''))
        w('FORM-01 por cargo (carrera + servicio):')
        for cargo in Cargo.objects.filter(unidad=u, activo=True).order_by('orden'):
            n = activos.filter(cargo=cargo).count()
            c = activos.filter(cargo=cargo, tipo_carrera='carrera').count()
            w(f'    {cargo.nombre:<46} {n:>3}   (carrera {c}, servicio {n - c})')
        w(f'FORM-02 sección B (no cumplen funciones, unidad {u.codigo}): {no_cumple}')
        for e in TipoEstado.objects.filter(cumple_funciones=False, nombre__endswith='(Demo)').order_by('nombre'):
            n = PersonalPolicial.objects.filter(unidad=u, estado_actual=e).count()
            if n:
                w(f'    {e.nombre:<40} {n:>3}')
        w(f'FORM-07 altas en el periodo:   {DestinoPolicial.objects.filter(unidad_destino=u, fecha_inicio__gte=ini, fecha_inicio__lte=fin).count()}')
        w(f'FORM-08 bajas por destino:     {DestinoPolicial.objects.filter(unidad_destino=u, fecha_fin__isnull=False, fecha_fin__gte=ini, fecha_fin__lte=fin).count()}')
        w(f'FORM-11 personal activo:       {PersonalPolicial.objects.filter(unidad=u, activo=True).count()}')
        w(f'FORM-13 bajas en el periodo:   {BajaPersonal.objects.filter(personal__unidad=u, fecha_baja__gte=ini, fecha_baja__lte=fin).count()}')
        w(f'FORM-13 fallecidos en periodo: {Fallecimiento.objects.filter(personal__unidad=u, fecha_fallecimiento__gte=ini, fecha_fallecimiento__lte=fin).count()}')
        w(ok('Nota: si también cargaste el seed original (6 personas), sus datos están sumados en estos totales.'))

    # ───────────────────────────── borrar ─────────────────────────────
    def _eliminar(self):
        personas = PersonalPolicial.objects.filter(ci__startswith=PREFIJO_CI)
        n = personas.count()
        Unidad.objects.filter(comandante__in=personas).update(comandante=None)
        personas.delete()
        Cargo.objects.filter(unidad__codigo=UNIDAD_B_CODIGO).delete()
        for nombre in CARGOS + ['Cargo de otra unidad (Demo)']:
            if nombre in COMPARTIDOS_CARGOS:
                continue
            try:
                Cargo.objects.filter(unidad__codigo=UNIDAD_CODIGO, nombre=nombre).delete()
            except ProtectedError:
                pass
        for _clave, (nombre, _c, _f) in ESTADOS.items():
            if nombre in COMPARTIDOS_ESTADOS:
                continue
            try:
                TipoEstado.objects.filter(nombre=nombre).delete()
            except ProtectedError:
                self.stdout.write(self.style.WARNING(f'Estado en uso, no se borró: {nombre}'))
        for _k, _n, abrev, _o in GRADOS + [('cabo', 'Cabo (Demo)', 'CBO.(D)', 150)]:
            if abrev in COMPARTIDOS_GRADOS:
                continue
            try:
                Grado.objects.filter(abreviatura=abrev).delete()
            except ProtectedError:
                self.stdout.write(self.style.WARNING(f'Grado en uso, no se borró: {abrev}'))
        try:
            Unidad.objects.filter(codigo=UNIDAD_B_CODIGO).delete()
        except ProtectedError:
            self.stdout.write(self.style.WARNING('Unidad B en uso, no se borró.'))
        self.stdout.write(self.style.SUCCESS(
            f'Eliminado: {n} personas del seed ampliado y los catálogos que creó. '
            'La unidad LR-DEMO y los datos del seed original (6 personas) no se tocan.'))
