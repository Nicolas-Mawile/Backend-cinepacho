from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    KeepTogether
)


# ==========================================
# PALETA DE COLORES PROFESIONAL (Corporativa y Equilibrada)
# ==========================================
COLOR_PRIMARIO = colors.HexColor("#3F3293")      # Indigo profundo para encabezados principales
COLOR_SECUNDARIO = colors.HexColor("#E58A1F")    # Ámbar/Naranja para acentos sutiles
COLOR_TEXTO_DARK = colors.HexColor("#2B2D42")    # Gris oscuro (más suave que el negro puro)
COLOR_TEXTO_MUTED = colors.HexColor("#6C757D")   # Gris secundario para metadatos/footers
COLOR_FONDO_LIGHT = colors.HexColor("#F8F9FA")   # Fondo gris muy claro para tablas y tarjetas
COLOR_LINEA = colors.HexColor("#E9ECEF")         # Líneas divisorias claras


class PDFGenerator:

    @staticmethod
    def _crear_estilos():
        estilos = getSampleStyleSheet()

        # Modificaciones sobre los estilos base para evitar colisiones
        estilos['Normal'].textColor = COLOR_TEXTO_DARK
        estilos['Normal'].fontSize = 10
        estilos['Normal'].leading = 15

        # Nuevos estilos tipográficos con proporciones correctas de leading (interlineado)
        estilos.add(ParagraphStyle(
            name="PortadaTitulo",
            parent=estilos['Normal'],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=32,
            leading=38,
            textColor=COLOR_PRIMARIO,
            spaceAfter=12
        ))

        estilos.add(ParagraphStyle(
            name="PortadaSubtitulo",
            parent=estilos['Normal'],
            alignment=TA_CENTER,
            fontName="Helvetica",
            fontSize=16,
            leading=22,
            textColor=COLOR_TEXTO_MUTED,
            spaceAfter=30
        ))

        estilos.add(ParagraphStyle(
            name="PortadaMeta",
            parent=estilos['Normal'],
            alignment=TA_CENTER,
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=14,
            textColor=COLOR_TEXTO_MUTED
        ))

        estilos.add(ParagraphStyle(
            name="SeccionTitulo",
            parent=estilos['Normal'],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=COLOR_PRIMARIO,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True  # Evita que el título quede huérfano al final de la página
        ))

        estilos.add(ParagraphStyle(
            name="TextoCuerpo",
            parent=estilos['Normal'],
            fontSize=10.5,
            leading=16,
            textColor=COLOR_TEXTO_DARK,
            spaceAfter=12
        ))

        # Estilos específicos para celdas de tablas y KPIs
        estilos.add(ParagraphStyle(
            name="KPITitulo",
            parent=estilos['Normal'],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=COLOR_TEXTO_MUTED
        ))

        estilos.add(ParagraphStyle(
            name="KPIValor",
            parent=estilos['Normal'],
            alignment=TA_CENTER,
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=COLOR_PRIMARIO
        ))

        estilos.add(ParagraphStyle(
            name="TablaHeader",
            parent=estilos['Normal'],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=12,
            textColor=colors.white
        ))

        estilos.add(ParagraphStyle(
            name="TablaCelda",
            parent=estilos['Normal'],
            fontSize=9.5,
            leading=13,
            textColor=COLOR_TEXTO_DARK
        ))

        return estilos

    @staticmethod
    def _decoracion_paginas(canvas, doc):
        """Dibuja el fondo, encabezado y pie de página de forma limpia y moderna."""
        canvas.saveState()
        
        # Ancho de la página para cálculos dinámicos
        ancho_pág = doc.pagesize[0]
        alto_pág = doc.pagesize[1]

        # --- ENCABEZADO (Solo en páginas posteriores a la portada) ---
        if doc.page > 1:
            canvas.setFont("Helvetica-Bold", 8)
            canvas.setFillColor(COLOR_PRIMARIO)
            canvas.drawString(2 * cm, alto_pág - 1.5 * cm, "CINEPACHO")
            
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(COLOR_TEXTO_MUTED)
            canvas.drawRightString(ancho_pág - 2 * cm, alto_pág - 1.5 * cm, "Sistema Centralizado de Gestión")
            
            # Línea sutil decorativa superior
            canvas.setStrokeColor(COLOR_LINEA)
            canvas.setLineWidth(0.5)
            canvas.line(2 * cm, alto_pág - 1.7 * cm, ancho_pág - 2 * cm, alto_pág - 1.7 * cm)

        # --- PIE DE PÁGINA (En todas las páginas excepto opcionalmente la portada) ---
        canvas.setStrokeColor(COLOR_LINEA)
        canvas.setLineWidth(0.5)
        canvas.line(2 * cm, 2 * cm, ancho_pág - 2 * cm, 2 * cm)

        canvas.setFont("Helvetica", 9)
        canvas.setFillColor(COLOR_TEXTO_MUTED)
        canvas.drawString(2 * cm, 1.4 * cm, "Reporte Automatizado — Confidencial")
        canvas.drawRightString(ancho_pág - 2 * cm, 1.4 * cm, f"Página {doc.page}")
        
        canvas.restoreState()

    @staticmethod
    def _crear_portada(contenido, estilos, titulo, subtitulo):
        # Espaciado inicial superior para centrar verticalmente el peso visual
        contenido.append(Spacer(1, 4 * cm))

        # Intento de cargar logo corporativo
        try:
            logo = Image("app/assets/logo_cinepacho.png", width=5 * cm, height=5 * cm)
            logo.hAlign = "CENTER"
            contenido.append(logo)
            contenido.append(Spacer(1, 1.5 * cm))
        except Exception:
            # Reemplazo estético si no existe la imagen (Banner de texto refinado)
            contenido.append(Paragraph("<b>[ CINEPACHO MULTIPLEX ]</b>", estilos["PortadaSubtitulo"]))
            contenido.append(Spacer(1, 1 * cm))

        # Título y subtítulo estructurados
        contenido.append(Paragraph(titulo, estilos["PortadaTitulo"]))
        if subtitulo:
            contenido.append(Paragraph(subtitulo, estilos["PortadaSubtitulo"]))

        # Línea de acento de la marca en la portada
        linea_acento = Table([[""]], colWidths=[4 * cm], rowHeights=[3])
        linea_acento.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), COLOR_SECUNDARIO),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]))
        linea_acento.hAlign = 'CENTER'
        contenido.append(linea_acento)

        contenido.append(Spacer(1, 6 * cm))

        # Metadatos al pie de la portada
        contenido.append(Paragraph("Generado por: Sistema Centralizado de Gestión", estilos["PortadaMeta"]))
        fecha_str = f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        contenido.append(Paragraph(fecha_str, estilos["PortadaMeta"]))
        
        contenido.append(PageBreak())

    @staticmethod
    def _crear_resumen(contenido, estilos, descripcion):
        if not descripcion:
            return
        contenido.append(Paragraph("Resumen Ejecutivo", estilos["SeccionTitulo"]))
        contenido.append(Paragraph(descripcion, estilos["TextoCuerpo"]))
        contenido.append(Spacer(1, 0.5 * cm))

    @staticmethod
    def _crear_kpis(contenido, estilos, indicadores):
        if not indicadores:
            return

        contenido.append(Paragraph("Indicadores Clave de Rendimiento (KPIs)", estilos["SeccionTitulo"]))
        
        cards_procesadas = []
        for titulo, valor in indicadores:
            # Reemplazamos la clase Flowable customizada por una Mini-Tabla nativa autogestionada.
            # Esto soluciona problemas de fuentes, alineaciones y desbordamientos.
            kpi_data = [
                [Paragraph(titulo.upper(), estilos["KPITitulo"])],
                [Spacer(1, 0.2 * cm)],
                [Paragraph(str(valor), estilos["KPIValor"])]
            ]
            
            # Ancho de la tarjeta: ~8.2 cm (para que quepan exactamente 2 en el ancho de la hoja)
            card_table = Table(kpi_data, colWidths=[8.2 * cm])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_FONDO_LIGHT),
                ('BOX', (0, 0), (-1, -1), 1, COLOR_LINEA),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            cards_procesadas.append(card_table)

        # Emparejar las tarjetas de dos en dos en una estructura de cuadrícula (Dashboard)
        filas_dashboard = []
        for i in range(0, len(cards_procesadas), 2):
            fila = cards_procesadas[i:i+2]
            if len(fila) < 2:
                fila.append("") # Celda vacía si es impar
            filas_dashboard.append(fila)

        # El ancho total disponible de impresión es 17.59 cm (21.59 - 4 cm de márgenes)
        # Dividimos en dos columnas de 8.5 cm con espacio en medio embebido automáticamente
        dashboard = Table(filas_dashboard, colWidths=[8.6 * cm, 8.6 * cm])
        dashboard.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15), # Espacio entre filas del dashboard
        ]))
        
        contenido.append(dashboard)
        contenido.append(Spacer(1, 0.5 * cm))

    @staticmethod
    def _crear_tablas(contenido, estilos, tablas):
        if not tablas:
            return

        contenido.append(Paragraph("Detalle de Datos e Indicadores", estilos["SeccionTitulo"]))

        for tabla_data in tablas:
            # CRITICAL: Convertimos todos los strings de las celdas en objetos 'Paragraph'
            # Esto evita que textos largos se salgan de las celdas y activa el auto-wrap.
            tabla_convertida = []
            for r_idx, fila in enumerate(tabla_data):
                nueva_fila = []
                for celda in fila:
                    if r_idx == 0:
                        nueva_fila.append(Paragraph(str(celda), estilos["TablaHeader"]))
                    else:
                        nueva_fila.append(Paragraph(str(celda), estilos["TablaCelda"]))
                tabla_convertida.append(nueva_fila)

            # Proporciones dinámicas para Letter (17.2 cm totales disponibles para perfecta simetría)
            # 10cm para descripciones/nombres, 7.2cm para métricas/valores.
            tabla_pdf = Table(tabla_convertida, repeatRows=1, colWidths=[10.0 * cm, 7.2 * cm])
            
            tabla_pdf.setStyle(TableStyle([
                # Encabezado elegante
                ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARIO),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                
                # Cuerpo de la tabla y filas alternas (Zebra striping moderno)
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_FONDO_LIGHT]),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                
                # Líneas divisorias minimalistas (No una cuadrícula negra pesada)
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, COLOR_LINEA),
            ]))
            
            # Garantiza que la tabla y su título no se rompan feamente entre páginas si hay espacio
            contenido.append(KeepTogether([tabla_pdf, Spacer(1, 0.6 * cm)]))

    @staticmethod
    def _crear_graficas(contenido, estilos, imagenes):
        if not imagenes:
            return

        contenido.append(Paragraph("Visualizaciones y Análisis Gráfico", estilos["SeccionTitulo"]))

        for indice, imagen in enumerate(imagenes, start=1):
            imagen.seek(0)
            # Escalado proporcional seguro para no romper márgenes en hojas Letter/A4
            grafica = Image(imagen, width=16 * cm, height=9.5 * cm)
            grafica.hAlign = "CENTER"
            
            # Encapsulamos la gráfica con su título para una presentación limpia
            bloque_grafica = [
                Paragraph(f"Gráfico {indice}: Histórico y Tendencias", estilos["TextoCuerpo"]),
                Spacer(1, 0.2 * cm),
                grafica,
                Spacer(1, 0.8 * cm)
            ]
            contenido.append(KeepTogether(bloque_grafica))

    @staticmethod
    def generar_pdf(
        titulo: str,
        subtitulo: str | None = None,
        descripcion: str | None = None,
        indicadores: list | None = None,
        tablas: list | None = None,
        imagenes: list | None = None,
    ):
        buffer = BytesIO()

        # Cambiado a tamaño 'letter' (estándar global/latino) con márgenes balanceados de 2cm
        documento = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2.2 * cm,
            bottomMargin=2.2 * cm,
        )

        estilos = PDFGenerator._crear_estilos()
        contenido = []

        # Construcción del flujo secuencial (Platypus Story)
        PDFGenerator._crear_portada(contenido, estilos, titulo, subtitulo)
        PDFGenerator._crear_resumen(contenido, estilos, descripcion)
        PDFGenerator._crear_kpis(contenido, estilos, indicadores)
        PDFGenerator._crear_tablas(contenido, estilos, tablas)
        PDFGenerator._crear_graficas(contenido, estilos, imagenes)

        # Compilación del documento asignando la decoración como callback de páginas de fondo
        documento.build(
            contenido,
            onFirstPage=PDFGenerator._decoracion_paginas,
            onLaterPages=PDFGenerator._decoracion_paginas,
        )

        buffer.seek(0)
        return buffer