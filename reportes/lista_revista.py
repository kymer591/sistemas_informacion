from collections import OrderedDict

from catalogos.models import Grado, Cargo
from personal.models import PersonalPolicial, DestinoPolicial, BajaPersonal, Fallecimiento
from .formato_oficial import (
    CLAVES_GRADO, ENCABEZADOS_CARRERA, ENCABEZADOS_SERVICIO,
    SITUACIONES_OFICIALES, clave_grado, indice_situacion, nombres_split,
)


def _vacio():
    return OrderedDict((k, 0) for k in CLAVES_GRADO)


def _cuadro_por_cargo(unidad, solo_carrera=False, solo_cumple=False):
    """
    Motor común para FORM-01 (todo el personal que cumple funciones) y FORM-03 (solo de carrera).
    Filas = cargos de la unidad. Columnas = las 14 jerarquías oficiales, en dos bloques:
    personal de carrera y personal de servicio. Los grados del catálogo que no se
    puedan asociar a una columna oficial se informan en 'grados_sin_columna'.
    """
    cargos = list(Cargo.objects.filter(unidad=unidad, activo=True).order_by('orden'))

    qs = PersonalPolicial.objects.filter(
        unidad=unidad, activo=True, cargo__isnull=False,
    ).select_related('grado')
    if solo_cumple:     # solo FORM-02 sección A, para que A + B no cuente dos veces a la misma persona
        qs = qs.filter(estado_actual__cumple_funciones=True)
    if solo_carrera:
        qs = qs.filter(tipo_carrera='carrera')

    filas = []
    totales_carrera, totales_servicio = _vacio(), _vacio()
    total_general = 0
    sin_columna = set()

    for cargo in cargos:
        conteo_carrera, conteo_servicio = _vacio(), _vacio()
        subtotal_fila = 0
        for persona in qs.filter(cargo=cargo):
            clave = clave_grado(persona.grado)
            if clave is None:
                sin_columna.add(persona.grado.nombre)
                continue
            if persona.tipo_carrera == 'servicio':
                conteo_servicio[clave] += 1
                totales_servicio[clave] += 1
            else:
                conteo_carrera[clave] += 1
                totales_carrera[clave] += 1
            subtotal_fila += 1
            total_general += 1

        filas.append({
            'cargo': cargo.nombre,
            'carrera': list(conteo_carrera.values()),
            'servicio': list(conteo_servicio.values()),
            'total': subtotal_fila,
        })

    # Personal de la unidad cuyo cargo NO está en el catálogo de cargos de esa unidad
    # (cargo de otra unidad, inactivo, etc.): se muestra en una fila aparte en vez de perderse.
    otros = qs.exclude(cargo__in=cargos)
    if otros.exists():
        conteo_carrera, conteo_servicio = _vacio(), _vacio()
        subtotal_fila = 0
        for persona in otros:
            clave = clave_grado(persona.grado)
            if clave is None:
                sin_columna.add(persona.grado.nombre)
                continue
            if persona.tipo_carrera == 'servicio':
                conteo_servicio[clave] += 1
                totales_servicio[clave] += 1
            else:
                conteo_carrera[clave] += 1
                totales_carrera[clave] += 1
            subtotal_fila += 1
            total_general += 1
        filas.append({
            'cargo': 'OTROS (cargo fuera del catálogo de la unidad)',
            'carrera': list(conteo_carrera.values()),
            'servicio': list(conteo_servicio.values()),
            'total': subtotal_fila,
        })

    return {
        # 'grados' se mantiene (14 encabezados de carrera) para la vista previa y el PDF
        'grados': list(ENCABEZADOS_CARRERA),
        'grados_servicio': list(ENCABEZADOS_SERVICIO),
        'filas': filas,
        'total_carrera': list(totales_carrera.values()),
        'total_servicio': list(totales_servicio.values()),
        'total_general': total_general,
        'grados_sin_columna': sorted(sin_columna),
    }


def generar_form_01(unidad):
    """CUADRO NUMERICO DEL PERSONAL POR UNIDADES (que cumplen funciones)."""
    return _cuadro_por_cargo(unidad, solo_carrera=False)


def generar_form_03(unidad):
    """CUADRO NUMERICO CLASIFICADO POR UNIDADES (solo personal de carrera)."""
    return _cuadro_por_cargo(unidad, solo_carrera=True)


def generar_form_02(unidad):
    """
    Sección A: personal que cumple funciones, por cargo (igual que FORM-01).
    Sección B: las 15 situaciones fijas del formulario oficial. Cada TipoEstado con
    cumple_funciones=False se ubica en la fila oficial que corresponda por su nombre
    (ver formato_oficial.indice_situacion). Los que no coincidan con ninguna se
    suman a la última fila ('COMISION DIR. NAL. Y OTROS') y quedan listados en
    'estados_sin_fila' para que el usuario ajuste el nombre del estado.
    """
    seccion_a = _cuadro_por_cargo(unidad, solo_carrera=False, solo_cumple=True)

    personal_no_activo = PersonalPolicial.objects.filter(
        unidad=unidad, estado_actual__cumple_funciones=False
    ).select_related('grado', 'estado_actual')

    filas_b = [{
        'situacion': etiqueta, 'color': color,
        'carrera': [0] * len(CLAVES_GRADO), 'servicio': [0] * len(CLAVES_GRADO),
        'total': 0,
    } for etiqueta, _claves, color in SITUACIONES_OFICIALES]

    estados_sin_fila, grados_sin_columna = set(), set()
    for persona in personal_no_activo:
        clave = clave_grado(persona.grado)
        if clave is None:
            grados_sin_columna.add(persona.grado.nombre)
            continue
        idx = indice_situacion(persona.estado_actual.nombre)
        if idx is None:
            estados_sin_fila.add(persona.estado_actual.nombre)
            idx = 10
        bloque = 'servicio' if persona.tipo_carrera == 'servicio' else 'carrera'
        filas_b[idx][bloque][CLAVES_GRADO.index(clave)] += 1
        filas_b[idx]['total'] += 1

    for f in filas_b:
        # compatibilidad con la vista previa / PDF: cantidades = carrera + servicio por jerarquía
        f['cantidades'] = [a + b for a, b in zip(f['carrera'], f['servicio'])]

    total_b = sum(f['total'] for f in filas_b)
    return {
        'grados': list(ENCABEZADOS_CARRERA),
        'grados_servicio': list(ENCABEZADOS_SERVICIO),
        'seccion_a': seccion_a,
        'seccion_b': {'filas': filas_b, 'total': total_b},
        'total_general': seccion_a['total_general'] + total_b,
        'estados_sin_fila': sorted(estados_sin_fila),
        'grados_sin_columna': sorted(grados_sin_columna | set(seccion_a['grados_sin_columna'])),
    }


def generar_form_07(unidad, fecha_inicio, fecha_fin):
    """ALTAS por cambio de destino A la unidad, dentro del periodo."""
    destinos = DestinoPolicial.objects.filter(
        unidad_destino=unidad,
        fecha_inicio__gte=fecha_inicio,
        fecha_inicio__lte=fecha_fin,
    ).select_related('personal', 'personal__grado', 'personal__cargo').order_by('fecha_inicio')

    filas = []
    for d in destinos:
        p = d.personal
        filas.append({
            'grado': p.grado.abreviatura,
            'apellido_paterno': p.apellido_paterno,
            'apellido_materno': p.apellido_materno,
            'nombres': p.nombres,
            'nombre1': nombres_split(p.nombres)[0],
            'nombre2': nombres_split(p.nombres)[1],
            'ci': p.ci,
            'expedido': p.expedido,
            'direccion': p.direccion_domicilio,
            'sexo': p.get_genero_display(),
            'cargo': p.cargo.nombre if p.cargo else '',
            'unidad_destino': unidad.nombre,
            'fecha_destino': d.fecha_inicio,
            'destino_anterior': d.lugar_destino,
            'celular': p.telefono_personal,
            'correo': p.correo_institucional,
            'otra_profesion': p.otra_profesion,
        })
    return filas


def generar_form_08(unidad, fecha_inicio, fecha_fin):
    """
    BAJAS por cambio de destino DE la unidad, dentro del periodo.
    Ver nota sobre la interpretación (no existe 'unidad_origen' explícita en el modelo).
    """
    destinos = DestinoPolicial.objects.filter(
        unidad_destino=unidad,
        fecha_fin__isnull=False,
        fecha_fin__gte=fecha_inicio,
        fecha_fin__lte=fecha_fin,
    ).select_related('personal', 'personal__grado', 'personal__cargo', 'personal__unidad').order_by('fecha_fin')

    filas = []
    for d in destinos:
        p = d.personal
        filas.append({
            'grado': p.grado.abreviatura,
            'apellido_paterno': p.apellido_paterno,
            'apellido_materno': p.apellido_materno,
            'nombres': p.nombres,
            'nombre1': nombres_split(p.nombres)[0],
            'nombre2': nombres_split(p.nombres)[1],
            'ci': p.ci,
            'expedido': p.expedido,
            'direccion': p.direccion_domicilio,
            'cargo': p.cargo.nombre if p.cargo else '',
            'fecha_cambio': d.fecha_fin,
            'unidad_actual': unidad.nombre,
            'unidad_destino_nueva': p.unidad.nombre if p.unidad_id != unidad.pk else 'No registrado',
            'celular': p.telefono_personal,
            'correo': p.correo_institucional,
            'otra_profesion': p.otra_profesion,
        })
    return filas


def generar_form_11(unidad):
    """Listado nominal completo, ordenado por grado jerárquico."""
    personal = PersonalPolicial.objects.filter(
        unidad=unidad, activo=True
    ).select_related('grado', 'cargo').order_by('grado__orden', 'apellido_paterno')

    filas = []
    for p in personal:
        destino_activo = p.destinos.filter(activo=True).first()
        filas.append({
            'grado': p.grado.abreviatura,
            'apellido_paterno': p.apellido_paterno,
            'apellido_materno': p.apellido_materno,
            'nombres': p.nombres,
            'nombre1': nombres_split(p.nombres)[0],
            'nombre2': nombres_split(p.nombres)[1],
            'ci': p.ci,
            'expedido': p.expedido,
            'direccion': p.direccion_domicilio,
            'cargo': p.cargo.nombre if p.cargo else '',
            'fecha_destino': destino_activo.fecha_inicio if destino_activo else p.fecha_ingreso,
            'destino_anterior': destino_activo.lugar_destino if destino_activo else '',
            'celular': p.telefono_personal,
            'correo': p.correo_institucional,
            'otra_profesion': p.otra_profesion,
        })
    return filas


def generar_form_12(unidad):
    """Listado nominal agrupado por Cargo (sección) dentro de la unidad."""
    cargos = Cargo.objects.filter(unidad=unidad, activo=True).order_by('orden')

    secciones = []
    numero_general = 0
    for cargo in cargos:
        personal = PersonalPolicial.objects.filter(
            unidad=unidad, activo=True, cargo=cargo
        ).select_related('grado').order_by('apellido_paterno')

        filas = []
        for p in personal:
            numero_general += 1
            filas.append({
                'n_general': numero_general,
                'grado': p.grado.abreviatura,
                'apellido_paterno': p.apellido_paterno,
                'apellido_materno': p.apellido_materno,
                'nombres': p.nombres,
                'nombre1': nombres_split(p.nombres)[0],
                'nombre2': nombres_split(p.nombres)[1],
                'ci': p.ci,
                'expedido': p.expedido,
                'sexo': p.get_genero_display(),
                'direccion': p.direccion_domicilio,
                'celular': p.telefono_personal,
                'correo': p.correo_institucional,
                'otra_profesion': p.otra_profesion,
                'codigo': p.codigo_identificacion,
            })

        if filas:
            secciones.append({'seccion': cargo.nombre, 'filas': filas})

    return secciones


def generar_form_13(unidad, fecha_inicio, fecha_fin):
    """Bajas definitivas / retiro / licencia indefinida, y fallecidos, en el periodo."""
    bajas = BajaPersonal.objects.filter(
        personal__unidad=unidad,
        fecha_baja__gte=fecha_inicio,
        fecha_baja__lte=fecha_fin,
    ).select_related('personal', 'personal__grado').order_by('fecha_baja')

    fallecidos = Fallecimiento.objects.filter(
        personal__unidad=unidad,
        fecha_fallecimiento__gte=fecha_inicio,
        fecha_fallecimiento__lte=fecha_fin,
    ).select_related('personal', 'personal__grado').order_by('fecha_fallecimiento')

    filas_bajas = [{
        'grado': b.personal.grado.abreviatura,
        'apellido_paterno': b.personal.apellido_paterno,
        'apellido_materno': b.personal.apellido_materno,
        'nombres': b.personal.nombres,
        'nombre1': nombres_split(b.personal.nombres)[0],
        'nombre2': nombres_split(b.personal.nombres)[1],
        'ci': b.personal.ci,
        'expedido': b.personal.expedido,
        'fecha_baja': b.fecha_baja,
        'motivo': b.get_tipo_baja_display(),
        'resolucion_tds': b.resolucion_tds,
        'numero_memo': b.numero_memo_escalafon,
        'autoridad_firma': b.autoridad_firma,
        'cargo_autoridad': b.cargo_autoridad_firma,
        'fecha_notificacion': b.fecha_notificacion,
        'observaciones': b.observaciones,
    } for b in bajas]

    filas_fallecidos = [{
        'grado': f.personal.grado.abreviatura,
        'apellido_paterno': f.personal.apellido_paterno,
        'apellido_materno': f.personal.apellido_materno,
        'nombres': f.personal.nombres,
        'nombre1': nombres_split(f.personal.nombres)[0],
        'nombre2': nombres_split(f.personal.nombres)[1],
        'ci': f.personal.ci,
        'expedido': f.personal.expedido,
        'fecha_fallecimiento': f.fecha_fallecimiento,
        'causa': f.causa_deceso,
        'numero_certificado': f.numero_certificado_defuncion,
        'entidad': f.entidad,
        'autoridad_firma': f.autoridad_firma,
        'numero_informe': f.numero_informe_trabajo_social,
        'fecha_informe': f.fecha_informe,
        'dir_salud': f.direccion_departamental_salud,
    } for f in fallecidos]

    return {'bajas': filas_bajas, 'fallecidos': filas_fallecidos}


def generar_lista_revista(unidad, fecha_inicio, fecha_fin):
    """Punto de entrada único: arma los 8 formularios para una unidad y periodo."""
    return {
        'unidad': unidad,
        'periodo': {'inicio': fecha_inicio, 'fin': fecha_fin},
        'form_01': generar_form_01(unidad),
        'form_02': generar_form_02(unidad),
        'form_03': generar_form_03(unidad),
        'form_07': generar_form_07(unidad, fecha_inicio, fecha_fin),
        'form_08': generar_form_08(unidad, fecha_inicio, fecha_fin),
        'form_11': generar_form_11(unidad),
        'form_12': generar_form_12(unidad),
        'form_13': generar_form_13(unidad, fecha_inicio, fecha_fin),
    }
    