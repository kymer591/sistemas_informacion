from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


# ───────────────────────── helpers de estilo ─────────────────────────

def _info_elaborador(usuario):
    persona = getattr(usuario, 'personal', None)
    if persona:
        return {
            'grado': persona.grado.abreviatura if persona.grado else '',
            'nombre': persona.nombre_completo(),
            'celular': persona.telefono_personal or '',
            'cargo': persona.cargo.nombre if persona.cargo else '',
        }
    return {'grado': '', 'nombre': usuario.username, 'celular': '', 'cargo': ''}


def _encabezado(ws, unidad, periodo_inicio, periodo_fin, formulario_num, num_cols):
    bold = Font(bold=True, size=11)
    small = Font(size=9, color='555555')
    center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    last_col = get_column_letter(num_cols)

    filas = [
        'POLICIA BOLIVIANA',
        unidad.nombre,
        f'{unidad.ciudad or ""} - BOLIVIA',
        'LISTA DE REVISTA',
        f'FORMULARIO Nº {formulario_num}',
        f'UNIDAD: {unidad.nombre}',
        f'CORREO ELECTRONICO DE LA UNIDAD: {unidad.correo_electronico or "No registrado"}',
        f'PERIODO: DEL {periodo_inicio} AL {periodo_fin}',
    ]
    for i, texto in enumerate(filas, start=1):
        ws.merge_cells(f'A{i}:{last_col}{i}')
        c = ws.cell(row=i, column=1, value=texto)
        c.font = bold if i <= 4 else small
        c.alignment = center
    return len(filas) + 2  # fila donde deben ir los encabezados de columna


def _pie(ws, unidad, elaborado_por, fecha_elaboracion, start_row, num_cols):
    last_col = get_column_letter(num_cols)
    small = Font(size=9)

    filas = [
        f'DIRECCION DE LA UNIDAD: {unidad.direccion or "No registrada"}',
        f'ELABORADO POR: {elaborado_por["grado"]} {elaborado_por["nombre"]}   '
        f'CEL: {elaborado_por["celular"]}   CARGO: {elaborado_por["cargo"]}',
        f'FECHA: {unidad.ciudad or ""}, {fecha_elaboracion.strftime("%d/%m/%Y")}',
    ]
    if unidad.comandante:
        filas.append(f'{unidad.comandante.grado.abreviatura} {unidad.comandante.nombre_completo()}')
        filas.append(f'COMANDANTE DE LA UNIDAD {unidad.nombre}')

    row = start_row
    for texto in filas:
        ws.merge_cells(f'A{row}:{last_col}{row}')
        c = ws.cell(row=row, column=1, value=texto)
        c.font = small
        row += 1


def _estilo_header_tabla(ws, fila, num_cols):
    fill = PatternFill('solid', start_color='1F3864')
    font = Font(bold=True, color='FFFFFF', size=9)
    center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    for col in range(1, num_cols + 1):
        c = ws.cell(row=fila, column=col)
        c.fill = fill
        c.font = font
        c.alignment = center


def _bordear(ws, fila_inicio, fila_fin, num_cols):
    thin = Side(style='thin', color='AAAAAA')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for row in ws.iter_rows(min_row=fila_inicio, max_row=fila_fin, min_col=1, max_col=num_cols):
        for cell in row:
            cell.border = border


def _anchos(ws, num_cols, ancho_primera=30, ancho_resto=12):
    ws.column_dimensions['A'].width = ancho_primera
    for i in range(2, num_cols + 1):
        ws.column_dimensions[get_column_letter(i)].width = ancho_resto


# ───────────────────────── hojas numéricas (FORM-01 / 03) ─────────────────────────

def _hoja_numerica(wb, titulo_hoja, formulario_num, bloque, unidad, periodo, elaborado_por, fecha_elab):
    ws = wb.create_sheet(titulo_hoja)
    cols = ['CARGO'] + bloque['grados'] + ['TOTAL']
    fila_header = _encabezado(ws, unidad, periodo['inicio'], periodo['fin'], formulario_num, len(cols))

    ws.cell(row=fila_header, column=1, value='CARGO')
    for i, g in enumerate(bloque['grados'], start=2):
        ws.cell(row=fila_header, column=i, value=g)
    ws.cell(row=fila_header, column=len(cols), value='TOTAL')
    _estilo_header_tabla(ws, fila_header, len(cols))

    row = fila_header + 1
    primera_fila_datos = row
    for fila in bloque['filas']:
        ws.cell(row=row, column=1, value=fila['cargo'])
        for i, val in enumerate(fila['carrera'], start=2):
            ws.cell(row=row, column=i, value=val)
        ws.cell(row=row, column=len(cols), value=fila['total'])
        row += 1

    ws.cell(row=row, column=1, value='T O T A L').font = Font(bold=True)
    for i, val in enumerate(bloque['total_carrera'], start=2):
        ws.cell(row=row, column=i, value=val).font = Font(bold=True)
    ws.cell(row=row, column=len(cols), value=bloque['total_general']).font = Font(bold=True)

    _bordear(ws, fila_header, row, len(cols))
    _anchos(ws, len(cols))
    _pie(ws, unidad, elaborado_por, fecha_elab, row + 2, len(cols))
    return ws


# ───────────────────────── FORM-02 (dos secciones) ─────────────────────────

def _hoja_form02(wb, datos, unidad, periodo, elaborado_por, fecha_elab):
    bloque = datos['form_02']
    ws = wb.create_sheet('FORM-02')
    cols = ['CARGO'] + bloque['grados'] + ['TOTAL']
    fila_header = _encabezado(ws, unidad, periodo['inicio'], periodo['fin'], 2, len(cols))

    ws.cell(row=fila_header, column=1, value='SECCION A — PERSONAL QUE CUMPLE FUNCIONES').font = Font(bold=True)
    fila_header += 1

    ws.cell(row=fila_header, column=1, value='CARGO')
    for i, g in enumerate(bloque['grados'], start=2):
        ws.cell(row=fila_header, column=i, value=g)
    ws.cell(row=fila_header, column=len(cols), value='TOTAL')
    _estilo_header_tabla(ws, fila_header, len(cols))

    row = fila_header + 1
    seccion_a = bloque['seccion_a']
    for fila in seccion_a['filas']:
        ws.cell(row=row, column=1, value=fila['cargo'])
        for i, val in enumerate(fila['carrera'], start=2):
            ws.cell(row=row, column=i, value=val)
        ws.cell(row=row, column=len(cols), value=fila['total'])
        row += 1
    ws.cell(row=row, column=1, value='SUB TOTAL A').font = Font(bold=True)
    ws.cell(row=row, column=len(cols), value=seccion_a['total_general']).font = Font(bold=True)
    row += 2

    ws.cell(row=row, column=1, value='SECCION B — PERSONAL QUE NO CUMPLE FUNCIONES').font = Font(bold=True)
    row += 1
    ws.cell(row=row, column=1, value='SITUACION')
    ws.cell(row=row, column=len(cols), value='TOTAL')
    _estilo_header_tabla(ws, row, len(cols))
    row += 1

    for fila in bloque['seccion_b']['filas']:
        ws.cell(row=row, column=1, value=fila['situacion'])
        ws.cell(row=row, column=len(cols), value=fila['total'])
        row += 1
    ws.cell(row=row, column=1, value='SUB TOTAL B').font = Font(bold=True)
    ws.cell(row=row, column=len(cols), value=bloque['seccion_b']['total']).font = Font(bold=True)
    row += 1
    ws.cell(row=row, column=1, value='T O T A L   G R A L.').font = Font(bold=True)
    ws.cell(row=row, column=len(cols), value=bloque['total_general']).font = Font(bold=True)

    _anchos(ws, len(cols))
    _pie(ws, unidad, elaborado_por, fecha_elab, row + 2, len(cols))
    return ws


# ───────────────────────── hojas nominales (FORM-07 / 08 / 11) ─────────────────────────

def _hoja_nominal(wb, titulo_hoja, formulario_num, columnas, filas_datos, unidad, periodo, elaborado_por, fecha_elab):
    ws = wb.create_sheet(titulo_hoja)
    num_cols = len(columnas)
    fila_header = _encabezado(ws, unidad, periodo['inicio'], periodo['fin'], formulario_num, num_cols)

    for i, (etiqueta, _clave) in enumerate(columnas, start=1):
        ws.cell(row=fila_header, column=i, value=etiqueta)
    _estilo_header_tabla(ws, fila_header, num_cols)

    row = fila_header + 1
    if not filas_datos:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=num_cols)
        ws.cell(row=row, column=1, value='SIN NOVEDAD').alignment = Alignment(horizontal='center')
        row += 1
    else:
        for fila in filas_datos:
            for i, (_etiqueta, clave) in enumerate(columnas, start=1):
                ws.cell(row=row, column=i, value=fila.get(clave, ''))
            row += 1

    _bordear(ws, fila_header, row - 1, num_cols)
    _anchos(ws, num_cols, ancho_primera=10, ancho_resto=16)
    _pie(ws, unidad, elaborado_por, fecha_elab, row + 2, num_cols)
    return ws


# ───────────────────────── FORM-12 (agrupado por sección) ─────────────────────────

def _hoja_form12(wb, datos, unidad, periodo, elaborado_por, fecha_elab):
    ws = wb.create_sheet('FORM-12')
    columnas = [
        ('N°', 'n_general'), ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'),
        ('AP. MATERNO', 'apellido_materno'), ('NOMBRES', 'nombres'), ('C.I.', 'ci'),
        ('SEXO', 'sexo'), ('CARGO', None), ('CELULAR', 'celular'), ('CORREO', 'correo'),
    ]
    num_cols = len(columnas)
    fila_header = _encabezado(ws, unidad, periodo['inicio'], periodo['fin'], 12, num_cols)

    row = fila_header
    if not datos['form_12']:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=num_cols)
        ws.cell(row=row, column=1, value='SIN NOVEDAD').alignment = Alignment(horizontal='center')
        row += 1
    else:
        for seccion in datos['form_12']:
            ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=num_cols)
            c = ws.cell(row=row, column=1, value=seccion['seccion'])
            c.font = Font(bold=True)
            c.fill = PatternFill('solid', start_color='D9E2F3')
            row += 1

            for i, (etiqueta, _clave) in enumerate(columnas, start=1):
                ws.cell(row=row, column=i, value=etiqueta)
            _estilo_header_tabla(ws, row, num_cols)
            row += 1

            for fila in seccion['filas']:
                ws.cell(row=row, column=1, value=fila['n_general'])
                ws.cell(row=row, column=2, value=fila['grado'])
                ws.cell(row=row, column=3, value=fila['apellido_paterno'])
                ws.cell(row=row, column=4, value=fila['apellido_materno'])
                ws.cell(row=row, column=5, value=fila['nombres'])
                ws.cell(row=row, column=6, value=fila['ci'])
                ws.cell(row=row, column=7, value=fila['sexo'])
                ws.cell(row=row, column=8, value='')
                ws.cell(row=row, column=9, value=fila['celular'])
                ws.cell(row=row, column=10, value=fila['correo'])
                row += 1

    _anchos(ws, num_cols, ancho_primera=6, ancho_resto=16)
    _pie(ws, unidad, elaborado_por, fecha_elab, row + 2, num_cols)
    return ws


# ───────────────────────── FORM-13 (dos secciones) ─────────────────────────

def _hoja_form13(wb, datos, unidad, periodo, elaborado_por, fecha_elab):
    bloque = datos['form_13']
    ws = wb.create_sheet('FORM-13')
    num_cols = 7
    fila_header = _encabezado(ws, unidad, periodo['inicio'], periodo['fin'], 13, num_cols)

    ws.cell(row=fila_header, column=1,
            value='SECCION 1 — BAJAS DEFINITIVAS / RETIRO TEMPORAL / LICENCIA INDEFINIDA').font = Font(bold=True)
    fila_header += 1
    cols_baja = ['GRADO', 'AP. PATERNO', 'AP. MATERNO', 'NOMBRES', 'C.I.', 'FECHA BAJA', 'MOTIVO']
    for i, c in enumerate(cols_baja, start=1):
        ws.cell(row=fila_header, column=i, value=c)
    _estilo_header_tabla(ws, fila_header, num_cols)
    row = fila_header + 1

    if not bloque['bajas']:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=num_cols)
        ws.cell(row=row, column=1, value='SIN NOVEDAD').alignment = Alignment(horizontal='center')
        row += 1
    else:
        for b in bloque['bajas']:
            ws.cell(row=row, column=1, value=b['grado'])
            ws.cell(row=row, column=2, value=b['apellido_paterno'])
            ws.cell(row=row, column=3, value=b['apellido_materno'])
            ws.cell(row=row, column=4, value=b['nombres'])
            ws.cell(row=row, column=5, value=b['ci'])
            ws.cell(row=row, column=6, value=str(b['fecha_baja']))
            ws.cell(row=row, column=7, value=b['motivo'])
            row += 1

    row += 1
    ws.cell(row=row, column=1, value='SECCION 2 — FALLECIDOS').font = Font(bold=True)
    row += 1
    cols_fall = ['GRADO', 'AP. PATERNO', 'AP. MATERNO', 'NOMBRES', 'C.I.', 'FECHA FALLECIMIENTO', 'CAUSA']
    for i, c in enumerate(cols_fall, start=1):
        ws.cell(row=row, column=i, value=c)
    _estilo_header_tabla(ws, row, num_cols)
    row += 1

    if not bloque['fallecidos']:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=num_cols)
        ws.cell(row=row, column=1, value='SIN NOVEDAD').alignment = Alignment(horizontal='center')
        row += 1
    else:
        for f in bloque['fallecidos']:
            ws.cell(row=row, column=1, value=f['grado'])
            ws.cell(row=row, column=2, value=f['apellido_paterno'])
            ws.cell(row=row, column=3, value=f['apellido_materno'])
            ws.cell(row=row, column=4, value=f['nombres'])
            ws.cell(row=row, column=5, value=f['ci'])
            ws.cell(row=row, column=6, value=str(f['fecha_fallecimiento']))
            ws.cell(row=row, column=7, value=f['causa'])
            row += 1

    _anchos(ws, num_cols, ancho_primera=10, ancho_resto=16)
    _pie(ws, unidad, elaborado_por, fecha_elab, row + 2, num_cols)
    return ws


# ───────────────────────── Punto de entrada ─────────────────────────

def generar_excel_lista_revista(datos, usuario, fecha_elaboracion):
    unidad = datos['unidad']
    periodo = datos['periodo']
    elaborado_por = _info_elaborador(usuario)

    wb = Workbook()
    wb.remove(wb.active)  # quitar la hoja vacía por defecto

    _hoja_numerica(wb, 'FORM-01', 1, datos['form_01'], unidad, periodo, elaborado_por, fecha_elaboracion)
    _hoja_form02(wb, datos, unidad, periodo, elaborado_por, fecha_elaboracion)
    _hoja_numerica(wb, 'FORM-03', 3, datos['form_03'], unidad, periodo, elaborado_por, fecha_elaboracion)

    _hoja_nominal(wb, 'FORM-07', 7, [
        ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'), ('AP. MATERNO', 'apellido_materno'),
        ('NOMBRES', 'nombres'), ('C.I.', 'ci'), ('EXP.', 'expedido'), ('DIRECCION', 'direccion'),
        ('SEXO', 'sexo'), ('CARGO', 'cargo'), ('UNIDAD DESTINO', 'unidad_destino'),
        ('FECHA DESTINO', 'fecha_destino'), ('DESTINO ANTERIOR', 'destino_anterior'),
        ('CELULAR', 'celular'), ('CORREO', 'correo'), ('OTRA PROFESION', 'otra_profesion'),
    ], datos['form_07'], unidad, periodo, elaborado_por, fecha_elaboracion)

    _hoja_nominal(wb, 'FORM-08', 8, [
        ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'), ('AP. MATERNO', 'apellido_materno'),
        ('NOMBRES', 'nombres'), ('C.I.', 'ci'), ('EXP.', 'expedido'), ('DIRECCION', 'direccion'),
        ('CARGO', 'cargo'), ('FECHA CAMBIO', 'fecha_cambio'), ('NUEVA UNIDAD', 'unidad_destino_nueva'),
        ('CELULAR', 'celular'), ('CORREO', 'correo'), ('OTRA PROFESION', 'otra_profesion'),
    ], datos['form_08'], unidad, periodo, elaborado_por, fecha_elaboracion)

    _hoja_nominal(wb, 'FORM-11', 11, [
        ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'), ('AP. MATERNO', 'apellido_materno'),
        ('NOMBRES', 'nombres'), ('C.I.', 'ci'), ('EXP.', 'expedido'), ('DIRECCION', 'direccion'),
        ('CARGO', 'cargo'), ('FECHA DESTINO', 'fecha_destino'), ('DESTINO ANTERIOR', 'destino_anterior'),
        ('CELULAR', 'celular'), ('CORREO', 'correo'), ('OTRA PROFESION', 'otra_profesion'),
    ], datos['form_11'], unidad, periodo, elaborado_por, fecha_elaboracion)

    _hoja_form12(wb, datos, unidad, periodo, elaborado_por, fecha_elaboracion)
    _hoja_form13(wb, datos, unidad, periodo, elaborado_por, fecha_elaboracion)

    return wb