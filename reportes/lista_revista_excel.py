"""
Exportación de la LISTA DE REVISTA a Excel con el formato oficial
(réplica de UTEPPI_LISTA_DE_REVISTA_*.xlsx): logos, encabezados verdes,
numeración verde, totales naranja, firmas y configuración de impresión.

Formularios incluidos: 01, 02, 03, 07, 08, 11, 12 y 13.
"""
from datetime import date, datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.properties import PageSetupProperties

# ───────────────────────── estilos del formato oficial ─────────────────────────

FUENTE = 'Arial'
VERDE_CLARO = '99FF66'     # encabezados de tabla
VERDE = '00FF00'           # columna de numeración
NARANJA = 'FFC000'         # totales
SALMON = 'E6B8B7'          # total general
GRIS = 'D9D9D9'

_thin = Side(style='thin', color='000000')
BORDE = Border(left=_thin, right=_thin, top=_thin, bottom=_thin)

MESES = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO',
         'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

IMG_DIR = Path(__file__).resolve().parent.parent / 'static' / 'image' / 'reportes'


def _f(bold=False, underline=False, color=None, size=10):
    return Font(name=FUENTE, size=size, bold=bold, underline='single' if underline else None, color=color)


def _fill(hex_):
    return PatternFill('solid', start_color=hex_, end_color=hex_)


def _fecha(valor):
    """Acepta date, datetime o 'YYYY-MM-DD' y devuelve date (o None)."""
    if valor in (None, ''):
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    return date.fromisoformat(str(valor)[:10])


def _periodo_texto(inicio, fin):
    i, f = _fecha(inicio), _fecha(fin)
    if i.year == f.year:
        return f'PERIODO: DEL {i.day} DE {MESES[i.month - 1]} AL {f.day} DE {MESES[f.month - 1]} DE {f.year}'
    return (f'PERIODO: DEL {i.day} DE {MESES[i.month - 1]} DE {i.year} '
            f'AL {f.day} DE {MESES[f.month - 1]} DE {f.year}')


def _info_elaborador(usuario):
    persona = getattr(usuario, 'personal', None)
    if persona:
        return {
            'grado': persona.grado.abreviatura if persona.grado else '',
            'nombre': persona.nombre_completo(),
            'celular': persona.telefono_personal or '',
            'cargo': persona.cargo.nombre if persona.cargo else '',
        }
    nombre = usuario.get_full_name() or usuario.username
    return {'grado': '', 'nombre': nombre, 'celular': '', 'cargo': ''}


# ───────────────────────── bloques comunes ─────────────────────────

def _merge(ws, fila, c1, c2, valor=None, font=None, align='left', valign='center', wrap=False, fila2=None):
    ws.merge_cells(start_row=fila, start_column=c1, end_row=fila2 or fila, end_column=c2)
    c = ws.cell(row=fila, column=c1, value=valor)
    c.font = font or _f()
    c.alignment = Alignment(horizontal=align, vertical=valign, wrap_text=wrap)
    return c


def _ancho_px(ws, ncols):
    total = 0
    for i in range(1, ncols + 1):
        w = ws.column_dimensions[L(i)].width or 8.43
        total += int(w * 7 + 5)
    return total


def _configurar_hoja(ws, ncols, ultima_fila, papel=5, una_pagina=False):
    """Impresión horizontal, ajustada a 1 página de ancho, como en el original."""
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = papel          # 5 = Oficio/Legal
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1 if una_pagina else 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_margins.left = ws.page_margins.right = 0.4
    ws.page_margins.top = 0.5
    ws.page_margins.bottom = 0.5
    ws.print_options.horizontalCentered = True
    ws.print_area = f'A1:{L(ncols)}{ultima_fila}'


def _cabecera(ws, unidad, periodo, nform, titulos, ncols):
    """
    Encabezado oficial. Devuelve la siguiente fila libre (la de la tabla).
    Filas: 1 franja de la bandera · 2-4 escudo · 3 nº de formulario · 5-7 institución ·
           9 LISTA DE REVISTA · 10.. títulos · UNIDAD/CORREO · PERIODO · (fila en blanco)
    """
    for r, h in {1: 11, 2: 12, 3: 12, 4: 12, 5: 12, 6: 26, 7: 12, 8: 8}.items():
        ws.row_dimensions[r].height = h
    franja = XLImage(str(IMG_DIR / 'franja_bandera.png'))
    franja.width, franja.height = _ancho_px(ws, ncols), 9
    ws.add_image(franja, 'A1')
    escudo = XLImage(str(IMG_DIR / 'escudo_policia.png'))
    escudo.width, escudo.height = 46, 47
    ws.add_image(escudo, 'B2')

    izq = min(4, max(2, ncols // 4))
    ciudad = (unidad.ciudad or '').upper()
    _merge(ws, 5, 1, izq, 'POLICIA BOLIVIANA', _f(), 'center')
    _merge(ws, 6, 1, izq, unidad.nombre.upper(), _f(), 'center', wrap=True)
    _merge(ws, 7, 1, izq, f'{ciudad} - BOLIVIA' if ciudad else 'BOLIVIA', _f(underline=True), 'center')

    ini_der = max(izq + 2, ncols - 3)
    _merge(ws, 3, ini_der, ncols, f'FORMULARIO   Nº {nform}', _f(bold=True), 'center')

    fila = 9
    _merge(ws, fila, 1, ncols, 'LISTA DE REVISTA', _f(bold=True, underline=True), 'center')
    fila += 1
    for t in titulos:
        _merge(ws, fila, 1, ncols, t, _f(bold=True, underline=True), 'center')
        fila += 1
    ws.row_dimensions[fila].height = 7
    fila += 1

    correo = unidad.correo_electronico or ''
    linea = f'UNIDAD: {unidad.nombre.upper()}'
    if correo:
        linea += f'    CORREO ELECTRONICO DE LA UNIDAD: {correo}'
    _merge(ws, fila, 1, ncols, linea, _f(bold=True))
    fila += 1
    _merge(ws, fila, 1, ncols, _periodo_texto(periodo['inicio'], periodo['fin']), _f())
    return fila + 2


def _pie(ws, fila, unidad, elaborado, fecha_elab, ncols):
    """Dirección, elaborado por, fecha y firma del comandante. Devuelve la última fila usada."""
    _merge(ws, fila, 1, ncols, f'DIRECCION DE LA UNIDAD: {(unidad.direccion or "").upper()}', _f(bold=True))
    fila += 2
    quien = f'{elaborado["grado"]} {elaborado["nombre"]}'.strip().upper()
    _merge(ws, fila, 1, ncols,
           f'ELABORADO POR: {quien}             CEL:{elaborado["celular"]}             '
           f'CARGO: {elaborado["cargo"].upper()}                 FIRMA…….……..……………….', _f(bold=True))
    fila += 1
    ciudad = (unidad.ciudad or '').upper()
    _merge(ws, fila, 1, ncols, f'FECHA: {ciudad}, {fecha_elab.strftime("%d/%m/%Y")}', _f(bold=True))
    fila += 4

    ancho = max(6, ncols // 2)
    c1 = max(1, (ncols - ancho) // 2 + 1)
    c2 = min(ncols, c1 + ancho - 1)
    cmd = unidad.comandante
    nombre_cmd = f'{cmd.grado.abreviatura} {cmd.nombre_completo()}'.upper() if cmd else ''
    _merge(ws, fila, c1, c2, nombre_cmd, _f(), 'center')
    fila += 1
    _merge(ws, fila, c1, c2, f'COMANDANTE DE LA {unidad.nombre.upper()}', _f(bold=True),
           'center', wrap=True, fila2=fila + 2)
    for r in (fila, fila + 1, fila + 2):
        ws.row_dimensions[r].height = 15
    return fila + 3


def _celda(ws, fila, col, valor=None, bold=False, fill=None, align='center', wrap=True,
           rot=0, fmt=None, borde=True, color=None):
    c = ws.cell(row=fila, column=col, value=valor)
    c.font = _f(bold=bold, color=color)
    c.alignment = Alignment(horizontal=align, vertical='center', wrap_text=wrap, text_rotation=rot)
    if fill:
        c.fill = _fill(fill)
    if borde:
        c.border = BORDE
    if fmt:
        c.number_format = fmt
    return c


# ───────────────────────── formularios numéricos (01, 02, 03) ─────────────────────────

OCULTAR_CERO = '0;-0;;@'


def _encabezado_grados(ws, fila, titulo_col, enc_carrera, enc_servicio):
    """Fila de encabezado con grados rotados. Devuelve la columna del TOTAL."""
    ws.row_dimensions[fila].height = 113
    _celda(ws, fila, 1, 'Nº', bold=True, fill=VERDE_CLARO)
    _celda(ws, fila, 2, titulo_col, bold=True, fill=VERDE_CLARO)
    col = 3
    for h in list(enc_carrera) + list(enc_servicio):
        _celda(ws, fila, col, h, bold=True, fill=VERDE_CLARO, rot=90, wrap=False)
        col += 1
    _celda(ws, fila, col, 'T  O  T  A  L', bold=True, fill=NARANJA, rot=90, wrap=False)
    return col


def _anchos_numericos(ws, ncols_grados, ancho_det=43):
    ws.column_dimensions['A'].width = 5.3
    ws.column_dimensions['B'].width = ancho_det
    for i in range(3, 3 + ncols_grados):
        ws.column_dimensions[L(i)].width = 4.6
    ws.column_dimensions[L(3 + ncols_grados)].width = 6


def _filas_cargo(ws, fila, filas, ngr, con_servicio):
    """Filas por cargo con total por fila como fórmula. Devuelve (primera, ultima, siguiente)."""
    col_tot = 3 + ngr
    primera = fila
    for n, f in enumerate(filas, start=1):
        ws.row_dimensions[fila].height = 21
        _celda(ws, fila, 1, n, bold=True, fill=VERDE)
        _celda(ws, fila, 2, f['cargo'], align='left')
        valores = f['carrera'] + (f['servicio'] if con_servicio else [])
        for j, v in enumerate(valores):
            _celda(ws, fila, 3 + j, v, fmt=OCULTAR_CERO)
        _celda(ws, fila, col_tot, f'=SUM({L(3)}{fila}:{L(col_tot - 1)}{fila})', bold=True, fill=NARANJA, wrap=False)
        fila += 1
    return primera, fila - 1, fila


def _fila_total(ws, fila, etiqueta, primera, ultima, ngr, fill=NARANJA, alto=23):
    col_tot = 3 + ngr
    ws.row_dimensions[fila].height = alto
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=2)
    _celda(ws, fila, 1, etiqueta, bold=True, fill=fill)
    ws.cell(row=fila, column=2).border = BORDE
    for j in range(ngr):
        col = L(3 + j)
        _celda(ws, fila, 3 + j, f'=SUM({col}{primera}:{col}{ultima})', bold=True, fill=fill, wrap=False)
    _celda(ws, fila, col_tot, f'=SUM({L(3)}{fila}:{L(col_tot - 1)}{fila})', bold=True, fill=fill, wrap=False)


def _aviso_grados(ws, fila, ncols, grados_sin_columna):
    if grados_sin_columna:
        _merge(ws, fila, 1, ncols,
               'AVISO: grados del catálogo sin columna oficial (no contados): ' + ', '.join(grados_sin_columna),
               _f(bold=True, color='FF0000'))
        return fila + 1
    return fila


def _hoja_form_numerico(wb, nform, titulos, bloque, con_servicio, unidad, periodo, elab, fecha_elab):
    ws = wb.create_sheet(f'FORM-{nform:02d}')
    ngr = len(bloque['grados']) * (2 if con_servicio else 1)
    ncols = 3 + ngr
    _anchos_numericos(ws, ngr)
    fila = _cabecera(ws, unidad, periodo, nform, titulos, ncols)

    _encabezado_grados(ws, fila, unidad.nombre.upper(), bloque['grados'],
                       bloque['grados_servicio'] if con_servicio else [])
    p, u, fila = _filas_cargo(ws, fila + 1, bloque['filas'], ngr, con_servicio)
    if u < p:       # unidad sin cargos registrados: una fila vacía para que las fórmulas sean válidas
        for c in range(1, ncols + 1):
            _celda(ws, fila, c, None)
        ws.cell(row=fila, column=2).value = 'SIN CARGOS REGISTRADOS'
        u = p
        fila += 1
    _fila_total(ws, fila, '   T O T A L', p, u, ngr)
    fila = _aviso_grados(ws, fila + 1, ncols, bloque.get('grados_sin_columna'))
    fin = _pie(ws, fila + 1, unidad, elab, fecha_elab, ncols)
    _configurar_hoja(ws, ncols, fin, una_pagina=True)
    return ws


def _hoja_form02(wb, datos, unidad, periodo, elab, fecha_elab):
    bloque = datos['form_02']
    A = bloque['seccion_a']
    ws = wb.create_sheet('FORM-02')
    ngr = len(bloque['grados']) * 2
    ncols = 3 + ngr
    _anchos_numericos(ws, ngr)
    fila = _cabecera(ws, unidad, periodo, 2, [
        'CUADRO NUMERICO GENERAL DE SERVIDORES PUBLICOS POLICIALES',
        'QUE CUMPLEN Y QUE NO CUMPLEN FUNCIONES EN LA UNIDAD'], ncols)

    # ── Sección A
    _merge(ws, fila, 1, ncols, 'PERSONAL QUE CUMPLEN FUNCIONES EN LA UNIDAD', _f(bold=True, underline=True), 'center')
    fila += 1
    _encabezado_grados(ws, fila, unidad.nombre.upper(), bloque['grados'], bloque['grados_servicio'])
    pa, ua, fila = _filas_cargo(ws, fila + 1, A['filas'], ngr, True)
    if ua < pa:
        for c in range(1, ncols + 1):
            _celda(ws, fila, c, None)
        ws.cell(row=fila, column=2).value = 'SIN CARGOS REGISTRADOS'
        ua = pa
        fila += 1
    _fila_total(ws, fila, 'SUB TOTAL', pa, ua, ngr, alto=17)
    fila_sub_a = fila
    fila += 2

    # ── Sección B
    _merge(ws, fila, 1, ncols, 'PERSONAL QUE NO CUMPLEN FUNCIONES EN LA UNIDAD', _f(bold=True, underline=True), 'center')
    fila += 1
    _encabezado_grados(ws, fila, 'SITUACION ACTUAL', bloque['grados'], bloque['grados_servicio'])
    fila += 1
    pb = fila
    col_tot = 3 + ngr
    for n, f in enumerate(bloque['seccion_b']['filas'], start=1):
        ws.row_dimensions[fila].height = 15
        _celda(ws, fila, 1, n, bold=True, fill=VERDE)
        _celda(ws, fila, 2, f['situacion'], align='left', fill=f['color'], wrap=False)
        for j, v in enumerate(f['carrera'] + f['servicio']):
            _celda(ws, fila, 3 + j, v, fmt=OCULTAR_CERO, fill=f['color'])
        _celda(ws, fila, col_tot, f'=SUM({L(3)}{fila}:{L(col_tot - 1)}{fila})', bold=True, fill=f['color'], wrap=False)
        fila += 1
    ub = fila - 1
    _fila_total(ws, fila, 'S U B   T O T A L', pb, ub, ngr, fill=GRIS, alto=17)
    fila_sub_b = fila
    fila += 2

    # ── Total general = SUB TOTAL A + SUB TOTAL B
    ws.row_dimensions[fila].height = 17
    ws.merge_cells(start_row=fila, start_column=1, end_row=fila, end_column=2)
    _celda(ws, fila, 1, 'T O T A L     GRAL.', bold=True, fill=SALMON)
    ws.cell(row=fila, column=2).border = BORDE
    for j in range(ngr):
        c = L(3 + j)
        _celda(ws, fila, 3 + j, f'={c}{fila_sub_a}+{c}{fila_sub_b}', bold=True, fill=SALMON, wrap=False)
    _celda(ws, fila, col_tot, f'=SUM({L(3)}{fila}:{L(col_tot - 1)}{fila})', bold=True, fill=SALMON, wrap=False)
    fila += 1

    fila = _aviso_grados(ws, fila, ncols, bloque.get('grados_sin_columna'))
    if bloque.get('estados_sin_fila'):
        _merge(ws, fila, 1, ncols,
               'AVISO: estados sin fila oficial (contados en "COMISION DIR. NAL. Y OTROS"): '
               + ', '.join(bloque['estados_sin_fila']), _f(bold=True, color='FF0000'))
        fila += 1
    fin = _pie(ws, fila + 1, unidad, elab, fecha_elab, ncols)
    _configurar_hoja(ws, ncols, fin, una_pagina=True)
    return ws


# ───────────────────────── formularios nominales (07, 08, 11, 12, 13) ─────────────────────────
# columna = (encabezado, clave, ancho, alineación)

C_GRADO = ('GRADO', 'grado', 9, 'center')
C_PAT = ('APELLIDO PATERNO', 'apellido_paterno', 13, 'center')
C_MAT = ('APELLIDO MATERNO', 'apellido_materno', 13, 'center')
C_N1 = ('1ER. NOMBRE', 'nombre1', 12, 'center')
C_N2 = ('2DO. NOMBRE', 'nombre2', 11, 'center')
C_CI = ('C.  I.', 'ci', 10, 'center')
C_EXP = ('EXP.', 'expedido', 6.5, 'center')
C_DIR = ('DIRECCION DEL DOMICILIO', 'direccion', 30, 'center')
C_SEXO = ('SEXO', 'sexo', 8, 'center')
C_CARGO = ('CARGO ACTUAL', 'cargo', 30, 'center')
C_UDEST = ('UNIDAD DE DESTINO ACTUAL', 'unidad_destino', 18, 'center')
C_FDEST = ('FECHA DESTINO', 'fecha_destino', 12, 'center')
C_DANT = ('DESTINO ANTERIOR', 'destino_anterior', 16, 'center')
C_CEL = ('NUMERO DE CELULAR', 'celular', 13, 'center')
C_MAIL = ('CORREO ELECTRONICO', 'correo', 28, 'center')
C_PROF = ('OTRA PROFESION LICENCIATURA / TECNICO', 'otra_profesion', 22, 'center')

COLS_07 = [C_GRADO, C_PAT, C_MAT, C_N1, C_N2, C_CI, C_EXP, C_DIR, C_SEXO, C_CARGO, C_UDEST,
           C_FDEST, C_DANT, C_CEL, C_MAIL, C_PROF]
COLS_08 = [C_GRADO, C_PAT, C_MAT, C_N1, C_N2, C_CI, C_EXP, C_DIR,
           ('CARGO', 'cargo', 28, 'center'),
           ('UNIDAD DE DESTINO ACTUAL', 'unidad_actual', 18, 'center'),
           ('FECHA DE CAMBIO DE DESTINO', 'fecha_cambio', 14, 'center'),
           ('UNIDAD DONDE ESTA SIENDO DESTINADO', 'unidad_destino_nueva', 20, 'center'),
           C_CEL, C_MAIL, C_PROF]
COLS_11 = [C_GRADO, C_PAT, C_MAT, C_N1, C_N2, C_CI, C_EXP, C_DIR, C_CARGO,
           ('UNIDAD DE DESTINO  ACTUAL', 'unidad_destino', 18, 'center'),
           ('FECHA DESTINO ACTUAL', 'fecha_destino', 12, 'center'), C_DANT, C_CEL, C_MAIL, C_PROF]
COLS_BAJAS = [C_GRADO, C_PAT, C_MAT, C_N1, C_N2, ('C.I.', 'ci', 10, 'center'), C_EXP,
              ('FECHA DE BAJA', 'fecha_baja', 12, 'center'),
              ('MOTIVO DE LA BAJA', 'motivo', 20, 'center'),
              ('RESOLUCION TDS', 'resolucion_tds', 14, 'center'),
              ('Nº MEMO. EMITIDO POR ESCALAFON', 'numero_memo', 15, 'center'),
              ('AUT. QUE FIRMA', 'autoridad_firma', 24, 'center'),
              ('CARGO AUTORIDAD / FIRMA', 'cargo_autoridad', 26, 'center'),
              ('FECHA DE NOTIFICACION', 'fecha_notificacion', 14, 'center'),
              ('OBSERVACIONES', 'observaciones', 22, 'center')]
COLS_FALL = [C_GRADO, C_PAT, C_MAT, C_N1, C_N2, ('C.I.', 'ci', 10, 'center'), C_EXP,
             ('FECHA DE FALLECIMIENTO', 'fecha_fallecimiento', 14, 'center'),
             ('CAUSA DEL DECESO', 'causa', 20, 'center'),
             ('Nº CERTIFICADO DEFUNCION', 'numero_certificado', 15, 'center'),
             ('ENTIDAD', 'entidad', 18, 'center'),
             ('AUT. QUE FIRMA', 'autoridad_firma', 24, 'center'),
             ('N° DE INFORME DE TRABAJO SOCIAL', 'numero_informe', 20, 'center'),
             ('FECHA DEL INFORME', 'fecha_informe', 14, 'center'),
             ('DIR. DPTAL. SALUD QUE REMITE', 'dir_salud', 22, 'center')]

FILAS_MIN = 3


def _valor(v):
    if isinstance(v, (date, datetime)):
        return _fecha(v).strftime('%d/%m/%Y')
    return '' if v is None else v


def _anchos_nominales(ws, columnas):
    """Aplica el ancho máximo de cada columna (útil cuando hay varias tablas en la hoja)."""
    ws.column_dimensions['A'].width = max(ws.column_dimensions['A'].width or 0, 5.5)
    for i, (_h, _k, ancho, _al) in enumerate(columnas, start=2):
        actual = ws.column_dimensions[L(i)].width
        if not actual or actual < ancho:
            ws.column_dimensions[L(i)].width = ancho


def _tabla_nominal(ws, fila, columnas, filas_datos, alto_header=50, alto_fila=27):
    """Tabla nominal oficial. Devuelve la siguiente fila libre."""
    ncols = len(columnas) + 1
    ws.row_dimensions[fila].height = alto_header
    _celda(ws, fila, 1, 'Nº', bold=True, fill=VERDE_CLARO)
    for i, (h, _k, _a, _al) in enumerate(columnas, start=2):
        _celda(ws, fila, i, h, bold=True, fill=VERDE_CLARO)
    fila += 1

    if filas_datos:
        for n, d in enumerate(filas_datos, start=1):
            ws.row_dimensions[fila].height = alto_fila
            _celda(ws, fila, 1, n, bold=True, fill=VERDE)
            for i, (_h, k, _a, al) in enumerate(columnas, start=2):
                _celda(ws, fila, i, _valor(d.get(k)), align=al)
            fila += 1
    else:   # sin registros: filas numeradas vacías con SIN NOVEDAD, como en el original
        for n in range(1, FILAS_MIN + 1):
            ws.row_dimensions[fila].height = 20
            _celda(ws, fila, 1, n, bold=True, fill=VERDE)
            for i in range(2, ncols + 1):
                _celda(ws, fila, i, None)
            if n == 2:
                c = ws.cell(row=fila, column=max(2, ncols // 2))
                c.value = 'SIN NOVEDAD'
                c.font = _f(bold=True)
            fila += 1
    return fila


def _etiqueta_direccion(ws, fila_tabla, ncols):
    """Etiqueta roja que el formato oficial coloca justo encima de la tabla."""
    _merge(ws, fila_tabla - 1, 1, ncols, 'NOMBRE DE SU DIRECCION / COMANDO / UNIDAD',
           _f(bold=True, color='FF0000'), 'center')


def _hoja_nominal(wb, nform, titulos, columnas, filas_datos, unidad, periodo, elab, fecha_elab,
                  etiqueta_direccion=True):
    ws = wb.create_sheet(f'FORM-{nform:02d}')
    ncols = len(columnas) + 1
    _anchos_nominales(ws, columnas)
    fila = _cabecera(ws, unidad, periodo, nform, titulos, ncols)
    if etiqueta_direccion:
        _etiqueta_direccion(ws, fila, ncols)
    fila = _tabla_nominal(ws, fila, columnas, filas_datos)
    fin = _pie(ws, fila + 1, unidad, elab, fecha_elab, ncols)
    _configurar_hoja(ws, ncols, fin)
    return ws


def _hoja_form12(wb, datos, unidad, periodo, elab, fecha_elab):
    ws = wb.create_sheet('FORM-12')
    columnas = [('Nº', 'n_seccion', 5, 'center'), C_GRADO, C_PAT, C_MAT, C_N1, C_N2, C_CI, C_EXP, C_SEXO,
                C_DIR, C_CARGO, C_UDEST, C_FDEST, C_DANT, C_CEL, C_MAIL, C_PROF,
                ('CODIGOS', 'codigo', 12, 'center')]
    ncols = len(columnas) + 1       # +1 por "N° GRAL" en la columna A
    _anchos_nominales(ws, columnas)
    ws.column_dimensions['A'].width = 7
    fila = _cabecera(ws, unidad, periodo, 12, [
        'CUADRO DEMOSTRATIVO DE SERVIDORES PUBLICOS POLICIALES',
        'DESGLOSADO POR UNIDADES Y/O ORGANISMOS'], ncols)
    _etiqueta_direccion(ws, fila, ncols)

    ws.row_dimensions[fila].height = 52
    _celda(ws, fila, 1, 'N°       GRAL', bold=True, fill=VERDE_CLARO)
    for i, (h, _k, _a, _al) in enumerate(columnas, start=2):
        _celda(ws, fila, i, h, bold=True, fill=VERDE_CLARO)
    fila += 1

    secciones = datos['form_12']
    if not secciones:
        for n in range(1, FILAS_MIN + 1):
            for i in range(1, ncols + 1):
                _celda(ws, fila, i, None, fill=VERDE if i == 1 else None)
            if n == 2:
                ws.cell(row=fila, column=ncols // 2).value = 'SIN NOVEDAD'
                ws.cell(row=fila, column=ncols // 2).font = _f(bold=True)
            fila += 1
    for sec in secciones:
        _merge(ws, fila, 1, ncols, sec['seccion'].upper(), _f(bold=True), 'left')
        for i in range(1, ncols + 1):
            ws.cell(row=fila, column=i).fill = _fill(VERDE_CLARO)
            ws.cell(row=fila, column=i).border = BORDE
        ws.row_dimensions[fila].height = 19
        fila += 1
        for n, d in enumerate(sec['filas'], start=1):
            ws.row_dimensions[fila].height = 27
            _celda(ws, fila, 1, d['n_general'], bold=True, fill=VERDE)
            _celda(ws, fila, 2, n, bold=True, fill=VERDE)
            for i, (_h, k, _a, al) in enumerate(columnas[1:], start=3):
                _celda(ws, fila, i, _valor(d.get(k)), align=al)
            fila += 1

    fin = _pie(ws, fila + 1, unidad, elab, fecha_elab, ncols)
    _configurar_hoja(ws, ncols, fin)
    return ws


def _hoja_form13(wb, datos, unidad, periodo, elab, fecha_elab):
    bloque = datos['form_13']
    ws = wb.create_sheet('FORM-13')
    ncols = len(COLS_BAJAS) + 1
    _anchos_nominales(ws, COLS_BAJAS)
    _anchos_nominales(ws, COLS_FALL)
    fila = _cabecera(ws, unidad, periodo, 13, [
        'CUADRO DEMOSTRATIVO DE SERVIDORES PUBLICOS POLICIALES CON',
        'BAJAS DEFINITIVA DE LA INSTITUCION,  RETIRO TEMPORAL (CAT. "B"), LICENCIA INDEFINIDA Y FALLECIDOS'], ncols)
    fila = _tabla_nominal(ws, fila, COLS_BAJAS, bloque['bajas'], alto_header=60, alto_fila=40)
    fila += 1
    _merge(ws, fila, 1, ncols, 'FALLECIDOS', _f(bold=True), 'left')
    fila += 1
    fila = _tabla_nominal(ws, fila, COLS_FALL, bloque['fallecidos'], alto_header=51, alto_fila=40)
    fin = _pie(ws, fila + 1, unidad, elab, fecha_elab, ncols)
    _configurar_hoja(ws, ncols, fin)
    return ws


# ───────────────────────── punto de entrada ─────────────────────────

def generar_excel_lista_revista(datos, usuario, fecha_elaboracion):
    unidad = datos['unidad']
    periodo = datos['periodo']
    elab = _info_elaborador(usuario)

    wb = Workbook()
    wb.remove(wb.active)

    _hoja_form_numerico(wb, 1, ['CUADRO NUMERICO DEL PERSONAL POR UNIDADES (QUE CUMPLEN FUNCIONES)'],
                        datos['form_01'], True, unidad, periodo, elab, fecha_elaboracion)
    _hoja_form02(wb, datos, unidad, periodo, elab, fecha_elaboracion)
    _hoja_form_numerico(wb, 3, ['CUADRO NUMERICO CLASIFICADO - POR UNIDADES',
                                'SERVIDORES PÚBLICOS POLICIALES DE CARRERA  (QUE CUMPLEN FUNCIONES)'],
                        datos['form_03'], False, unidad, periodo, elab, fecha_elaboracion)

    _hoja_nominal(wb, 7, ['CUADRO DEMOSTRATIVO DE ALTAS (POR CAMBIO DE DESTINO A LA UNIDAD)'],
                  COLS_07, datos['form_07'], unidad, periodo, elab, fecha_elaboracion)
    _hoja_nominal(wb, 8, ['CUADRO DEMOSTRATIVO DE BAJAS (POR CAMBIO DE DESTINO DE LA UNIDAD)'],
                  COLS_08, datos['form_08'], unidad, periodo, elab, fecha_elaboracion,
                  etiqueta_direccion=False)
    _hoja_nominal(wb, 11, ['CUADRO DEMOSTRATIVO DE LOS SERVIDORES PUBLICOS POLICIALES  POR GRADO JERARQUICO'],
                  COLS_11, datos['form_11'], unidad, periodo, elab, fecha_elaboracion)
    _hoja_form12(wb, datos, unidad, periodo, elab, fecha_elaboracion)
    _hoja_form13(wb, datos, unidad, periodo, elab, fecha_elaboracion)
    return wb
