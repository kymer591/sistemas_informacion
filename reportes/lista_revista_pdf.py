from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

from .lista_revista_excel import _info_elaborador

_styles = getSampleStyleSheet()

_titulo = ParagraphStyle('lr_titulo', parent=_styles['Title'], fontSize=12,
                          textColor=colors.HexColor('#1F3864'), alignment=TA_CENTER, spaceAfter=2)
_sub = ParagraphStyle('lr_sub', parent=_styles['Normal'], fontSize=9, alignment=TA_CENTER, spaceAfter=2)
_form_num = ParagraphStyle('lr_form', parent=_styles['Normal'], fontSize=10, alignment=TA_CENTER,
                            spaceAfter=6, textColor=colors.HexColor('#1F3864'))
_pie_style = ParagraphStyle('lr_pie', parent=_styles['Normal'], fontSize=8, alignment=TA_LEFT, spaceBefore=2)
_celda = ParagraphStyle('lr_celda', parent=_styles['Normal'], fontSize=7, leading=9)
_celda_header = ParagraphStyle('lr_celda_h', parent=_styles['Normal'], fontSize=7, leading=9,
                                textColor=colors.white, alignment=TA_CENTER)
_seccion_titulo = ParagraphStyle('lr_seccion', parent=_styles['Normal'], fontSize=9, spaceBefore=8,
                                  spaceAfter=4, textColor=colors.HexColor('#1F3864'))


def _celda_p(texto):
    return Paragraph(str(texto) if texto not in (None, '') else '—', _celda)


def _encabezado_flowables(unidad, periodo, formulario_num):
    return [
        Paragraph('POLICIA BOLIVIANA', _titulo),
        Paragraph(unidad.nombre, _sub),
        Paragraph(f'{unidad.ciudad or ""} - BOLIVIA', _sub),
        Paragraph('LISTA DE REVISTA', _titulo),
        Paragraph(f'FORMULARIO Nº {formulario_num}', _form_num),
        Paragraph(f'UNIDAD: {unidad.nombre}', _sub),
        Paragraph(f'CORREO ELECTRONICO DE LA UNIDAD: {unidad.correo_electronico or "No registrado"}', _sub),
        Paragraph(f'PERIODO: DEL {periodo["inicio"]} AL {periodo["fin"]}', _sub),
        Spacer(1, 10),
    ]


def _pie_flowables(unidad, elaborado_por, fecha_elaboracion):
    flow = [
        Spacer(1, 14),
        Paragraph(f'DIRECCION DE LA UNIDAD: {unidad.direccion or "No registrada"}', _pie_style),
        Paragraph(
            f'ELABORADO POR: {elaborado_por["grado"]} {elaborado_por["nombre"]}   '
            f'CEL: {elaborado_por["celular"]}   CARGO: {elaborado_por["cargo"]}   FIRMA…….……..……………….',
            _pie_style,
        ),
        Paragraph(f'FECHA: {unidad.ciudad or ""}, {fecha_elaboracion.strftime("%d/%m/%Y")}', _pie_style),
    ]
    if unidad.comandante:
        flow.append(Paragraph(f'{unidad.comandante.grado.abreviatura} {unidad.comandante.nombre_completo()}', _pie_style))
        flow.append(Paragraph(f'COMANDANTE DE LA UNIDAD {unidad.nombre}', _pie_style))
    return flow


def _estilo_tabla(num_filas_header=1):
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, num_filas_header - 1), colors.HexColor('#1F3864')),
        ('FONTNAME', (0, 0), (-1, num_filas_header - 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#AAAAAA')),
        ('ROWBACKGROUND', (0, num_filas_header), (-1, -1), [colors.HexColor('#EAF0FB'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ])


# ───────────────────────── FORM-01 / 03 (numéricos) ─────────────────────────

def _seccion_numerica(unidad, periodo, formulario_num, bloque, elaborado_por, fecha_elab):
    flow = _encabezado_flowables(unidad, periodo, formulario_num)

    encabezados = ['CARGO'] + bloque['grados'] + ['TOTAL']
    filas = [[Paragraph(h, _celda_header) for h in encabezados]]
    for fila in bloque['filas']:
        filas.append(
            [_celda_p(fila['cargo'])] +
            [_celda_p(v) for v in fila['carrera']] +
            [_celda_p(fila['total'])]
        )
    filas.append(
        [Paragraph('T O T A L', _celda)] +
        [_celda_p(v) for v in bloque['total_carrera']] +
        [_celda_p(bloque['total_general'])]
    )

    col_widths = [4.5 * cm] + [1.3 * cm] * len(bloque['grados']) + [1.6 * cm]
    t = Table(filas, colWidths=col_widths, repeatRows=1)
    t.setStyle(_estilo_tabla())
    flow.append(t)
    flow += _pie_flowables(unidad, elaborado_por, fecha_elab)
    flow.append(PageBreak())
    return flow


# ───────────────────────── FORM-02 (dos secciones) ─────────────────────────

def _seccion_form02(unidad, periodo, datos, elaborado_por, fecha_elab):
    bloque = datos['form_02']
    flow = _encabezado_flowables(unidad, periodo, 2)

    flow.append(Paragraph('SECCION A — PERSONAL QUE CUMPLE FUNCIONES', _seccion_titulo))
    seccion_a = bloque['seccion_a']
    encabezados = ['CARGO'] + bloque['grados'] + ['TOTAL']
    filas = [[Paragraph(h, _celda_header) for h in encabezados]]
    for fila in seccion_a['filas']:
        filas.append(
            [_celda_p(fila['cargo'])] +
            [_celda_p(v) for v in fila['carrera']] +
            [_celda_p(fila['total'])]
        )
    filas.append(
        [Paragraph('SUB TOTAL A', _celda)] +
        [''] * len(bloque['grados']) +
        [_celda_p(seccion_a['total_general'])]
    )
    col_widths = [4.5 * cm] + [1.3 * cm] * len(bloque['grados']) + [1.6 * cm]
    t1 = Table(filas, colWidths=col_widths, repeatRows=1)
    t1.setStyle(_estilo_tabla())
    flow.append(t1)

    flow.append(Paragraph('SECCION B — PERSONAL QUE NO CUMPLE FUNCIONES', _seccion_titulo))
    filas_b = [[Paragraph('SITUACION', _celda_header), Paragraph('TOTAL', _celda_header)]]
    for fila in bloque['seccion_b']['filas']:
        filas_b.append([_celda_p(fila['situacion']), _celda_p(fila['total'])])
    filas_b.append([Paragraph('SUB TOTAL B', _celda), _celda_p(bloque['seccion_b']['total'])])
    filas_b.append([Paragraph('T O T A L   G R A L.', _celda), _celda_p(bloque['total_general'])])
    t2 = Table(filas_b, colWidths=[10 * cm, 2.5 * cm], repeatRows=1)
    t2.setStyle(_estilo_tabla())
    flow.append(t2)

    flow += _pie_flowables(unidad, elaborado_por, fecha_elab)
    flow.append(PageBreak())
    return flow


# ───────────────────────── FORM-07 / 08 / 11 (nominales) ─────────────────────────

def _seccion_nominal(unidad, periodo, formulario_num, columnas, filas_datos, elaborado_por, fecha_elab):
    flow = _encabezado_flowables(unidad, periodo, formulario_num)

    encabezados = [Paragraph(etq, _celda_header) for etq, _clave in columnas]
    filas = [encabezados]

    if not filas_datos:
        filas.append([Paragraph('SIN NOVEDAD', _celda)] + [''] * (len(columnas) - 1))
    else:
        for fila in filas_datos:
            filas.append([_celda_p(fila.get(clave, '')) for _etq, clave in columnas])

    ancho_col = (23 * cm) / len(columnas)
    t = Table(filas, colWidths=[ancho_col] * len(columnas), repeatRows=1)
    t.setStyle(_estilo_tabla())
    flow.append(t)
    flow += _pie_flowables(unidad, elaborado_por, fecha_elab)
    flow.append(PageBreak())
    return flow


# ───────────────────────── FORM-12 (agrupado por sección) ─────────────────────────

def _seccion_form12(unidad, periodo, datos, elaborado_por, fecha_elab):
    flow = _encabezado_flowables(unidad, periodo, 12)

    if not datos['form_12']:
        flow.append(Paragraph('SIN NOVEDAD', _celda))
    else:
        columnas = [('N°', 'n_general'), ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'),
                    ('AP. MATERNO', 'apellido_materno'), ('NOMBRES', 'nombres'), ('C.I.', 'ci'),
                    ('SEXO', 'sexo'), ('CELULAR', 'celular'), ('CORREO', 'correo')]
        ancho_col = (23 * cm) / len(columnas)

        for seccion in datos['form_12']:
            flow.append(Paragraph(seccion['seccion'], _seccion_titulo))
            encabezados = [Paragraph(etq, _celda_header) for etq, _clave in columnas]
            filas = [encabezados]
            for fila in seccion['filas']:
                filas.append([_celda_p(fila.get(clave, '')) for _etq, clave in columnas])
            t = Table(filas, colWidths=[ancho_col] * len(columnas), repeatRows=1)
            t.setStyle(_estilo_tabla())
            flow.append(t)

    flow += _pie_flowables(unidad, elaborado_por, fecha_elab)
    flow.append(PageBreak())
    return flow


# ───────────────────────── FORM-13 (bajas + fallecidos) ─────────────────────────

def _seccion_form13(unidad, periodo, datos, elaborado_por, fecha_elab):
    bloque = datos['form_13']
    flow = _encabezado_flowables(unidad, periodo, 13)

    flow.append(Paragraph('SECCION 1 — BAJAS DEFINITIVAS / RETIRO TEMPORAL / LICENCIA INDEFINIDA', _seccion_titulo))
    cols_baja = ['GRADO', 'AP. PATERNO', 'AP. MATERNO', 'NOMBRES', 'C.I.', 'FECHA BAJA', 'MOTIVO']
    filas_baja = [[Paragraph(c, _celda_header) for c in cols_baja]]
    if not bloque['bajas']:
        filas_baja.append([Paragraph('SIN NOVEDAD', _celda)] + [''] * 6)
    else:
        for b in bloque['bajas']:
            filas_baja.append([
                _celda_p(b['grado']), _celda_p(b['apellido_paterno']), _celda_p(b['apellido_materno']),
                _celda_p(b['nombres']), _celda_p(b['ci']), _celda_p(b['fecha_baja']), _celda_p(b['motivo']),
            ])
    t1 = Table(filas_baja, colWidths=[2.2 * cm, 3 * cm, 3 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 6.3 * cm], repeatRows=1)
    t1.setStyle(_estilo_tabla())
    flow.append(t1)

    flow.append(Paragraph('SECCION 2 — FALLECIDOS', _seccion_titulo))
    cols_fall = ['GRADO', 'AP. PATERNO', 'AP. MATERNO', 'NOMBRES', 'C.I.', 'FECHA FALLECIMIENTO', 'CAUSA']
    filas_fall = [[Paragraph(c, _celda_header) for c in cols_fall]]
    if not bloque['fallecidos']:
        filas_fall.append([Paragraph('SIN NOVEDAD', _celda)] + [''] * 6)
    else:
        for f in bloque['fallecidos']:
            filas_fall.append([
                _celda_p(f['grado']), _celda_p(f['apellido_paterno']), _celda_p(f['apellido_materno']),
                _celda_p(f['nombres']), _celda_p(f['ci']), _celda_p(f['fecha_fallecimiento']), _celda_p(f['causa']),
            ])
    t2 = Table(filas_fall, colWidths=[2.2 * cm, 3 * cm, 3 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 6.3 * cm], repeatRows=1)
    t2.setStyle(_estilo_tabla())
    flow.append(t2)

    flow += _pie_flowables(unidad, elaborado_por, fecha_elab)
    return flow


# ───────────────────────── Punto de entrada ─────────────────────────

def generar_pdf_lista_revista(response, datos, usuario, fecha_elaboracion):
    unidad = datos['unidad']
    periodo = datos['periodo']
    elaborado_por = _info_elaborador(usuario)

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        leftMargin=1.3 * cm, rightMargin=1.3 * cm,
        topMargin=1.3 * cm, bottomMargin=1.3 * cm,
    )

    elementos = []
    elementos += _seccion_numerica(unidad, periodo, 1, datos['form_01'], elaborado_por, fecha_elaboracion)
    elementos += _seccion_form02(unidad, periodo, datos, elaborado_por, fecha_elaboracion)
    elementos += _seccion_numerica(unidad, periodo, 3, datos['form_03'], elaborado_por, fecha_elaboracion)

    elementos += _seccion_nominal(unidad, periodo, 7, [
        ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'), ('AP. MATERNO', 'apellido_materno'),
        ('NOMBRES', 'nombres'), ('C.I.', 'ci'), ('CARGO', 'cargo'),
        ('FECHA DESTINO', 'fecha_destino'), ('DESTINO ANTERIOR', 'destino_anterior'), ('CELULAR', 'celular'),
    ], datos['form_07'], elaborado_por, fecha_elaboracion)

    elementos += _seccion_nominal(unidad, periodo, 8, [
        ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'), ('AP. MATERNO', 'apellido_materno'),
        ('NOMBRES', 'nombres'), ('C.I.', 'ci'), ('CARGO', 'cargo'),
        ('FECHA CAMBIO', 'fecha_cambio'), ('NUEVA UNIDAD', 'unidad_destino_nueva'), ('CELULAR', 'celular'),
    ], datos['form_08'], elaborado_por, fecha_elaboracion)

    elementos += _seccion_nominal(unidad, periodo, 11, [
        ('GRADO', 'grado'), ('AP. PATERNO', 'apellido_paterno'), ('AP. MATERNO', 'apellido_materno'),
        ('NOMBRES', 'nombres'), ('C.I.', 'ci'), ('CARGO', 'cargo'),
        ('FECHA DESTINO', 'fecha_destino'), ('DESTINO ANTERIOR', 'destino_anterior'), ('CELULAR', 'celular'),
    ], datos['form_11'], elaborado_por, fecha_elaboracion)

    elementos += _seccion_form12(unidad, periodo, datos, elaborado_por, fecha_elaboracion)
    elementos += _seccion_form13(unidad, periodo, datos, elaborado_por, fecha_elaboracion)

    doc.build(elementos)
    return response