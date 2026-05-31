from pathlib import Path

from app.database import SessionLocal

from app.domain.services.reporte_pdf_service import (
    ReportePdfService
)


def test_generar_todos_los_reportes_pdf():

    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)

    db = SessionLocal()

    try:

        service = ReportePdfService(db)

        # ==========================================
        # REPORTE MOVILIDAD
        # ==========================================

        pdf_movilidad = (
            service.generar_pdf_movilidad()
        )

        with open(
            output_dir / "reporte_movilidad.pdf",
            "wb",
        ) as archivo:

            archivo.write(
                pdf_movilidad.getvalue()
            )

        # ==========================================
        # REPORTE OPERACIONAL
        # ==========================================

        pdf_operacional = (
            service.generar_pdf_operacional(
                mes=5,
                anio=2026,
            )
        )

        with open(
            output_dir / "reporte_operacional.pdf",
            "wb",
        ) as archivo:

            archivo.write(
                pdf_operacional.getvalue()
            )

        # ==========================================
        # REPORTE MULTIPLEX
        # ==========================================

        pdf_multiplex = (
            service.generar_pdf_desempeno_multiplex(
                mes=5,
                anio=2026,
            )
        )

        with open(
            output_dir / "reporte_multiplex.pdf",
            "wb",
        ) as archivo:

            archivo.write(
                pdf_multiplex.getvalue()
            )

        # ==========================================
        # VALIDACIONES
        # ==========================================

        assert (
            output_dir / "reporte_movilidad.pdf"
        ).exists()

        assert (
            output_dir / "reporte_operacional.pdf"
        ).exists()

        assert (
            output_dir / "reporte_multiplex.pdf"
        ).exists()

        assert (
            output_dir
            / "reporte_movilidad.pdf"
        ).stat().st_size > 0

        assert (
            output_dir
            / "reporte_operacional.pdf"
        ).stat().st_size > 0

        assert (
            output_dir
            / "reporte_multiplex.pdf"
        ).stat().st_size > 0

    finally:

        db.close()