"""
Constantes del formato oficial de la LISTA DE REVISTA (Policía Boliviana).

Se extrajeron del archivo UTEPPI_LISTA_DE_REVISTA_2026_MARZO_ACTUALIZADO.xlsx.
Centralizar esto aquí evita que las columnas dependan de cómo esté cargado el
catálogo de grados: el formulario oficial SIEMPRE tiene las mismas 14 columnas
de carrera y las mismas 14 de servicio.
"""
import re
import unicodedata

# (clave, encabezado carrera, encabezado servicio, alias normalizados de Grado.nombre / abreviatura)
GRADOS_OFICIALES = [
    ('cnl',     'CNL.',      'CNL. SERV.',        ['coronel', 'cnl', 'crnl']),
    ('tcnl',    'TCNL.',     'TCNL. SERV.',       ['teniente coronel', 'tcnl', 'tcrnl']),
    ('my',      'MAYOR',     'MY. SERV.',         ['mayor', 'my']),
    ('cap',     'CAPITAN',   'CAP. SERV.',        ['capitan', 'cap']),
    ('tte',     'TENIENTE',  'TTE. SERV.',        ['teniente', 'tte']),
    ('sbtte',   'SBTTE.',    'SBTTE. SERV.',      ['subteniente', 'sbtte', 'stte', 'sbte']),
    ('sof_sup', 'SOF. SUP.', 'SOF.SUP.SERV.',     ['suboficial superior', 'sof sup', 'sof. sup.', 'sof.sup']),
    ('sof_my',  'SOF. MY.',  'SOF. MY. SERV.',    ['suboficial maestre', 'suboficial mayor', 'sof my', 'sof. my.']),
    ('sof_1',   'SOF. 1RO.', 'SOF. 1RO. SERV.',   ['suboficial primero', 'sof 1ro', 'sof. 1ro.']),
    ('sof_2',   'SOF. 2DO.', 'SOF. 2DO. SERV.',   ['suboficial segundo', 'sof 2do', 'sof. 2do.']),
    ('sgto_my', 'SGTO. MY',  'SGTO. MY. SERV.',   ['sargento mayor', 'sgto my', 'sgto. my']),
    ('sgto_1',  'SGTO. 1RO.', 'SGTO. 1RO. SERV.', ['sargento primero', 'sgto 1ro', 'sgto. 1ro.']),
    ('sgto_2',  'SGTO. 2DO.', 'SGTO. 2DO. SERV.', ['sargento segundo', 'sgto 2do', 'sgto. 2do.']),
    ('sgto',    'SGTO.',     'SGTO. SERV.',       ['sargento', 'sgto']),
]

CLAVES_GRADO = [g[0] for g in GRADOS_OFICIALES]
ENCABEZADOS_CARRERA = [g[1] for g in GRADOS_OFICIALES]
ENCABEZADOS_SERVICIO = [g[2] for g in GRADOS_OFICIALES]


def _norm(texto):
    texto = re.sub(r'\([^)]*\)', ' ', texto or '')      # ignora sufijos como '(Demo)'
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.lower()
    for a, b in (('.', ' '), ('1º', '1ro'), ('2º', '2do'), ('1°', '1ro'), ('2°', '2do'), ('sub oficial', 'suboficial'), ('º', ''), ('°', ''), ('primero', '1ro'), ('segundo', '2do'),
                 ('1er', '1ro'), ('maestre', 'my'), ('mayor', 'my')):
        texto = texto.replace(a, b)
    return ' '.join(texto.split())


_ALIAS = {}
for _clave, _h1, _h2, _aliases in GRADOS_OFICIALES:
    for _a in _aliases:
        _ALIAS[_norm(_a)] = _clave


def clave_grado(grado):
    """Devuelve la clave oficial ('cap', 'sgto_2', ...) para un catalogos.Grado, o None si no mapea."""
    if grado is None:
        return None
    # primero el nombre completo (más específico), luego la abreviatura
    return _ALIAS.get(_norm(grado.nombre)) or _ALIAS.get(_norm(grado.abreviatura))


# Filas fijas de la sección "PERSONAL QUE NO CUMPLEN FUNCIONES" del FORMULARIO 2.
# (etiqueta, palabras clave para reconocer el TipoEstado, color de relleno hex o None)
SITUACIONES_OFICIALES = [
    ('DESERTORES - DET. PREVENTIVAS - DET. DOM.', ['desert', 'detenido', 'detencion'], 'FF66CC'),
    ('BAJA DEFINITIVA DE LA INSTITUCION',          ['baja'],                            'FFFF00'),
    ('RETIRO TEMPORAL  (CAT. B)',                  ['retiro'],                          'FFFF00'),
    ('LICENCIA INDEFINIDA',                        ['licencia'],                        'FFFF00'),
    ('FALLECIDOS',                                 ['fallec'],                          'FFFF00'),
    ('COMISION UNIPOL',                            ['unipol'],                          None),
    ('COMISION  F. T. C.',                         ['ftc', 'f t c'],                    None),
    ('COMISION CURSO CANES',                       ['canes'],                           None),
    ('COMISION CURSO GARRAS',                      ['garras'],                          None),
    ('COMISION II.T.V.',                           ['itv', 'i t v', 'ii t v'],          None),
    ('COMISION DIR. NAL. Y OTROS',                 ['comision'],                        None),
    ('ITEM 0  GOBERNACION (CAT. "D")',             ['item 0', 'gobernacion'],           None),
    ('SUSPENSIONES INDEFINIDAS',                   ['suspen'],                          'D9D9D9'),
    ('A DISPONIBILIDAD DE CATEGORIA "A" Y "C"',    ['disponibilidad'],                  'D9D9D9'),
    ('A DISPOSICION DE LA DIDIPI. / FISCALIA',     ['disposicion', 'didipi', 'fiscalia'], 'D9D9D9'),
]


def indice_situacion(nombre_estado):
    """Índice de la fila oficial a la que corresponde un TipoEstado, o None si no coincide."""
    n = _norm(nombre_estado)
    # orden de prioridad: las filas específicas primero; 'comision' genérico y 'baja' al final
    for i, (_etq, claves, _color) in enumerate(SITUACIONES_OFICIALES):
        if i == 10:          # 'COMISION DIR. NAL. Y OTROS' es el comodín de comisiones
            continue
        if any(k in n for k in claves):
            return i
    if 'comision' in n:
        return 10
    return None


def nombres_split(nombres):
    """'VICTOR HUGO' -> ('VICTOR', 'HUGO'); 'DANIELA' -> ('DANIELA', '')."""
    partes = (nombres or '').split(None, 1)
    return (partes[0] if partes else '', partes[1] if len(partes) > 1 else '')
