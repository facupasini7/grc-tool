"""
Generador de reportes PDF — ISO 27001:2022 Gap Analysis
"""
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

MADUREZ_LABELS = {
    0: "Inexistente",
    1: "Inicial",
    2: "Repetible",
    3: "Definido",
    4: "Gestionado",
    5: "Optimizado",
}

DOMINIOS_NOMBRE = {
    "A.5": "Controles Organizacionales",
    "A.6": "Controles de Personas",
    "A.7": "Controles Físicos",
    "A.8": "Controles Tecnológicos",
}


def _color_madurez(m):
    colores = {0: "#dc3545", 1: "#dc3545", 2: "#fd7e14", 3: "#ffc107", 4: "#20c997", 5: "#198754"}
    return colores.get(m, "#6c757d")


def generar_pdf(evaluacion: dict, stats: dict, controles: list) -> Path:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, PageBreak,
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        out = REPORTS_DIR / f"gap_analysis_{evaluacion['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        estilos = getSampleStyleSheet()
        story = []

        # ── Portada ──────────────────────────────────────────────────────────
        titulo_style = ParagraphStyle("titulo", fontSize=22, spaceAfter=6, alignment=TA_CENTER, textColor=colors.HexColor("#1a1a2e"), fontName="Helvetica-Bold")
        subtitulo_style = ParagraphStyle("subtitulo", fontSize=13, spaceAfter=4, alignment=TA_CENTER, textColor=colors.HexColor("#16213e"))
        info_style = ParagraphStyle("info", fontSize=10, spaceAfter=3, alignment=TA_CENTER, textColor=colors.HexColor("#4a4a6a"))

        story.append(Spacer(1, 3*cm))
        story.append(Paragraph("ISO/IEC 27001:2022", titulo_style))
        story.append(Paragraph("Análisis de Brechas (Gap Analysis)", subtitulo_style))
        story.append(HRFlowable(width="80%", thickness=2, color=colors.HexColor("#1a1a2e"), spaceAfter=20))
        story.append(Paragraph(f"Empresa: <b>{evaluacion['empresa']}</b>", info_style))
        story.append(Paragraph(f"Evaluación: <b>{evaluacion['nombre']}</b>", info_style))
        if evaluacion.get("alcance"):
            story.append(Paragraph(f"Alcance: {evaluacion['alcance']}", info_style))
        story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", info_style))
        story.append(Spacer(1, 1*cm))

        # ── Resumen ejecutivo ─────────────────────────────────────────────────
        story.append(PageBreak())
        h1 = ParagraphStyle("h1", fontSize=14, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#1a1a2e"), fontName="Helvetica-Bold")
        normal = ParagraphStyle("normal", fontSize=9, spaceAfter=4, leading=14)

        story.append(Paragraph("1. Resumen Ejecutivo", h1))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dee2e6"), spaceAfter=8))

        mg = stats["madurez_global"]
        nivel = MADUREZ_LABELS.get(round(mg), "N/D")
        story.append(Paragraph(
            f"La organización alcanzó una <b>madurez global de {mg}/5 ({nivel})</b> sobre los controles evaluados. "
            f"Se evaluaron <b>{stats['respondidos']} de {stats['total']} controles aplicables</b> "
            f"({stats['progreso_pct']}% de completitud).",
            normal
        ))
        story.append(Spacer(1, 0.4*cm))

        # Tabla resumen por dominio
        tabla_data = [["Dominio", "Controles", "Evaluados", "Madurez promedio", "Brechas"]]
        for dom, d in stats["dominios"].items():
            tabla_data.append([
                f"{dom} — {d['nombre']}",
                str(d["total"]),
                str(d["respondidos"]),
                f"{d['promedio_madurez']}/5",
                str(len(d["brechas"])),
            ])

        t = Table(tabla_data, colWidths=[8*cm, 2*cm, 2.2*cm, 3*cm, 2*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.8*cm))

        # ── Detalle de brechas por dominio ────────────────────────────────────
        story.append(Paragraph("2. Brechas por Dominio", h1))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dee2e6"), spaceAfter=8))

        h2 = ParagraphStyle("h2", fontSize=11, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#16213e"), fontName="Helvetica-Bold")

        for dom, d in stats["dominios"].items():
            if not d["brechas"]:
                continue
            story.append(Paragraph(f"{dom} — {d['nombre']}", h2))
            brecha_data = [["Control", "Madurez actual", "Nivel"]]
            for b in sorted(d["brechas"], key=lambda x: x["madurez"]):
                brecha_data.append([
                    f"{b['id']} — {b['nombre']}",
                    f"{b['madurez']}/5",
                    MADUREZ_LABELS.get(b["madurez"], "N/D"),
                ])
            bt = Table(brecha_data, colWidths=[10*cm, 2.5*cm, 4.5*cm])
            bt.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343a40")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fff3cd"), colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(bt)
            story.append(Spacer(1, 0.4*cm))

        # ── Roadmap priorizado ────────────────────────────────────────────────
        story.append(PageBreak())
        story.append(Paragraph("3. Roadmap de Remediación Priorizado", h1))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dee2e6"), spaceAfter=8))
        story.append(Paragraph(
            "Los controles con madurez 0 o 1 son críticos y deben priorizarse en la primera fase de implementación.",
            normal
        ))
        story.append(Spacer(1, 0.4*cm))

        todas_brechas = []
        for dom, d in stats["dominios"].items():
            for b in d["brechas"]:
                b["dominio"] = dom
                todas_brechas.append(b)
        todas_brechas.sort(key=lambda x: x["madurez"])

        road_data = [["#", "Control", "Dominio", "Madurez", "Prioridad"]]
        for i, b in enumerate(todas_brechas, 1):
            prioridad = "CRÍTICA" if b["madurez"] <= 1 else ("ALTA" if b["madurez"] == 2 else "MEDIA")
            road_data.append([str(i), f"{b['id']} — {b['nombre']}", b["dominio"], f"{b['madurez']}/5", prioridad])

        rt = Table(road_data, colWidths=[0.8*cm, 9*cm, 2*cm, 2*cm, 2.5*cm])
        rt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (3, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(rt)

        story.append(Spacer(1, 1*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#dee2e6")))
        story.append(Paragraph(
            f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | ISO 27001:2022 Gap Analysis Tool",
            ParagraphStyle("footer", fontSize=7, textColor=colors.HexColor("#6c757d"), alignment=TA_CENTER),
        ))

        doc.build(story)
        return out

    except ImportError:
        # Fallback: reporte en texto plano si no hay reportlab
        out = REPORTS_DIR / f"gap_analysis_{evaluacion['id']}.txt"
        lines = [
            "ISO/IEC 27001:2022 — Gap Analysis Report",
            f"Empresa: {evaluacion['empresa']}",
            f"Evaluación: {evaluacion['nombre']}",
            f"Fecha: {datetime.now().strftime('%d/%m/%Y')}",
            f"Madurez global: {stats['madurez_global']}/5",
            "",
        ]
        for dom, d in stats["dominios"].items():
            lines.append(f"\n{dom} — {d['nombre']}: {d['promedio_madurez']}/5")
            for b in d["brechas"]:
                lines.append(f"  BRECHA: {b['id']} — {b['nombre']} (madurez: {b['madurez']})")
        out.write_text("\n".join(lines), encoding="utf-8")
        return out
