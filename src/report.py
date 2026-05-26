"""
Generador de reportes PDF — NormaLab GRC Tool
Soporta múltiples frameworks y dos formatos: ejecutivo y detallado.
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

MADUREZ_COLORS = {
    0: "#dc3545",
    1: "#dc3545",
    2: "#fd7e14",
    3: "#ffc107",
    4: "#20c997",
    5: "#198754",
}

FRAMEWORK_LABELS = {
    "ISO27001":    "ISO/IEC 27001:2022",
    "NIST_CSF":    "NIST Cybersecurity Framework 2.0",
    "SOC2":        "SOC 2 Type II",
    "CIS":         "CIS Controls v8",
    "A7777":       "ISO/IEC 27701:2019",
    "A7783":       "ISO/IEC 27783",
    "BCRA":        "BCRA Com. A 7724",
    "PCI":         "PCI DSS v4.0",
}


def _fw_label(fw_id: str) -> str:
    return FRAMEWORK_LABELS.get(fw_id, fw_id)


def _get_domains_from_db(eval_id: int, fw_id: str) -> dict:
    """Retorna {dominio: nombre} único de los controles respondidos en esta evaluación."""
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from database import get_conn
        with get_conn() as conn:
            rows = conn.execute(
                """SELECT DISTINCT c.dominio, c.categoria
                   FROM controles_fw c
                   JOIN respuestas r ON r.control_id = c.id AND c.framework = ?
                   WHERE r.evaluacion_id = ? AND c.dominio != ''
                   ORDER BY c.dominio""",
                (fw_id, eval_id),
            ).fetchall()
        return {r["dominio"]: r["categoria"] or r["dominio"] for r in rows}
    except Exception:
        return {}


def _color_madurez(m):
    return MADUREZ_COLORS.get(m, "#6c757d")


# ── Estilos compartidos ──────────────────────────────────────────────────────

def _build_styles():
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    C_DARK  = colors.HexColor("#0f172a")
    C_MED   = colors.HexColor("#1e293b")
    C_BLUE  = colors.HexColor("#3b82f6")
    C_GRAY  = colors.HexColor("#64748b")
    C_LIGHT = colors.HexColor("#f1f5f9")
    C_WHITE = colors.white

    base = getSampleStyleSheet()
    return {
        "portada_fw":   ParagraphStyle("portada_fw",   fontSize=11, spaceAfter=4,  alignment=TA_CENTER, textColor=C_BLUE,  fontName="Helvetica"),
        "portada_title":ParagraphStyle("portada_title",fontSize=26, spaceAfter=8,  alignment=TA_CENTER, textColor=C_DARK,  fontName="Helvetica-Bold"),
        "portada_sub":  ParagraphStyle("portada_sub",  fontSize=14, spaceAfter=6,  alignment=TA_CENTER, textColor=C_MED,   fontName="Helvetica"),
        "portada_info": ParagraphStyle("portada_info", fontSize=10, spaceAfter=4,  alignment=TA_CENTER, textColor=C_GRAY),
        "h1":           ParagraphStyle("h1",           fontSize=14, spaceBefore=14,spaceAfter=6,  textColor=C_DARK,  fontName="Helvetica-Bold"),
        "h2":           ParagraphStyle("h2",           fontSize=11, spaceBefore=10,spaceAfter=4,  textColor=C_MED,   fontName="Helvetica-Bold"),
        "h3":           ParagraphStyle("h3",           fontSize=9.5,spaceBefore=6, spaceAfter=3,  textColor=C_GRAY,  fontName="Helvetica-Bold"),
        "normal":       ParagraphStyle("normal",       fontSize=9,  spaceAfter=4,  leading=14,    textColor=C_MED),
        "small":        ParagraphStyle("small",        fontSize=7.5,spaceAfter=2,  leading=11,    textColor=C_GRAY),
        "footer":       ParagraphStyle("footer",       fontSize=7,  textColor=C_GRAY, alignment=TA_CENTER),
        "kpi_num":      ParagraphStyle("kpi_num",      fontSize=22, spaceAfter=0,  alignment=TA_CENTER, fontName="Helvetica-Bold", textColor=C_BLUE),
        "kpi_label":    ParagraphStyle("kpi_label",    fontSize=8,  spaceAfter=0,  alignment=TA_CENTER, textColor=C_GRAY),
        "C_DARK": C_DARK, "C_MED": C_MED, "C_BLUE": C_BLUE,
        "C_GRAY": C_GRAY, "C_LIGHT": C_LIGHT, "C_WHITE": C_WHITE,
    }


def _portada(story, evaluacion, tipo, fw_id, st):
    from reportlab.platypus import Spacer, Paragraph, HRFlowable
    from reportlab.lib import colors

    tipo_label = "Informe Ejecutivo" if tipo == "ejecutivo" else "Informe Detallado"
    story.append(Spacer(1, 3.5 * 28.35))   # ~3.5 cm in points

    story.append(Paragraph(_fw_label(fw_id), st["portada_fw"]))
    story.append(Paragraph("Análisis de Brechas", st["portada_title"]))
    story.append(Paragraph(tipo_label, st["portada_sub"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="70%", thickness=2, color=st["C_BLUE"], spaceAfter=20))

    story.append(Paragraph(f"<b>Empresa:</b> {evaluacion['empresa']}", st["portada_info"]))
    story.append(Paragraph(f"<b>Evaluación:</b> {evaluacion['nombre']}", st["portada_info"]))
    if evaluacion.get("alcance"):
        story.append(Paragraph(f"<b>Alcance:</b> {evaluacion['alcance']}", st["portada_info"]))
    story.append(Paragraph(f"<b>Fecha de emisión:</b> {datetime.now().strftime('%d/%m/%Y')}", st["portada_info"]))
    story.append(Spacer(1, 28))
    story.append(Paragraph("Generado por NormaLab GRC — Confidencial", st["portada_info"]))


def _pie(story, fw_id, st):
    from reportlab.platypus import Spacer, Paragraph, HRFlowable
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=st["C_GRAY"], spaceAfter=4))
    story.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')} | NormaLab GRC | {_fw_label(fw_id)}",
        st["footer"]
    ))


def _tabla_dominios(stats, st):
    """Tabla de resumen de madurez por dominio."""
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors

    tabla_data = [["Dominio / Categoría", "Controles", "Evaluados", "Madurez", "Brechas"]]
    for dom, d in stats["dominios"].items():
        tabla_data.append([
            f"{dom}",
            str(d["total"]),
            str(d["respondidos"]),
            f"{d['promedio_madurez']}/5",
            str(len(d["brechas"])),
        ])

    t = Table(tabla_data, colWidths=[9*cm, 2*cm, 2.2*cm, 2.5*cm, 2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  st["C_DARK"]),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  st["C_WHITE"]),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [st["C_LIGHT"], colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (0, -1),  6),
    ]))
    return t


# ── Informe Ejecutivo (2-3 páginas) ─────────────────────────────────────────

def generar_ejecutivo(evaluacion: dict, stats: dict, controles: list,
                      fw_id: str, hallazgos: list, riesgos: list) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak,
    )

    out = REPORTS_DIR / f"ejecutivo_{evaluacion['id']}_{fw_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    st  = _build_styles()
    story = []

    # Portada
    _portada(story, evaluacion, "ejecutivo", fw_id, st)
    story.append(PageBreak())

    # ── 1. KPIs ─────────────────────────────────────────────────────────────
    story.append(Paragraph("1. Resumen Ejecutivo", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    mg     = stats["madurez_global"]
    nivel  = MADUREZ_LABELS.get(round(mg), "N/D")
    prog   = stats["progreso_pct"]
    n_hall = len([h for h in hallazgos if h.get("estado") == "abierto"])
    n_risg = len([r for r in riesgos if r.get("estado") == "abierto"])

    story.append(Paragraph(
        f"La organización alcanzó una <b>madurez global de {mg}/5 — {nivel}</b> "
        f"sobre {_fw_label(fw_id)}, con una completitud del <b>{prog}%</b> "
        f"({stats['respondidos']} de {stats['total']} controles evaluados). "
        f"Se identificaron <b>{n_hall} hallazgos abiertos</b> y <b>{n_risg} riesgos activos</b>.",
        st["normal"]
    ))
    story.append(Spacer(1, 8))

    # KPI boxes
    kpi_data = [[
        Paragraph(f"{mg}", st["kpi_num"]),
        Paragraph(f"{prog}%", st["kpi_num"]),
        Paragraph(str(n_hall), st["kpi_num"]),
        Paragraph(str(n_risg), st["kpi_num"]),
    ],[
        Paragraph("Madurez global", st["kpi_label"]),
        Paragraph("Completitud", st["kpi_label"]),
        Paragraph("Hallazgos abiertos", st["kpi_label"]),
        Paragraph("Riesgos activos", st["kpi_label"]),
    ]]
    kpi_t = Table(kpi_data, colWidths=[4*cm]*4)
    kpi_t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), st["C_LIGHT"]),
        ("BOX",          (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("LINEAFTER",    (0, 0), (2, -1),  0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",   (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10),
    ]))
    story.append(kpi_t)
    story.append(Spacer(1, 14))

    # ── 2. Madurez por dominio ───────────────────────────────────────────────
    story.append(Paragraph("2. Madurez por Dominio / Categoría", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))
    story.append(_tabla_dominios(stats, st))
    story.append(Spacer(1, 14))

    # ── 3. Hallazgos críticos ────────────────────────────────────────────────
    criticos = [h for h in hallazgos if h.get("severidad") in ("critica", "alta") and h.get("estado") == "abierto"][:8]
    story.append(Paragraph("3. Hallazgos Críticos y Altos", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    if criticos:
        hall_data = [["Control", "Título", "Severidad", "Estado"]]
        for h in criticos:
            sev = h.get("severidad","").title()
            hall_data.append([h.get("control_id","—"), h.get("titulo","")[:60], sev, h.get("estado","").title()])

        ht = Table(hall_data, colWidths=[2.5*cm, 9.5*cm, 2.5*cm, 2.5*cm])
        ht.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  st["C_DARK"]),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  st["C_WHITE"]),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#fff7ed"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("ALIGN",         (2, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (1, -1),  5),
        ]))
        story.append(ht)
    else:
        story.append(Paragraph("No hay hallazgos críticos o altos abiertos.", st["normal"]))

    story.append(Spacer(1, 14))

    # ── 4. Top 5 Riesgos ────────────────────────────────────────────────────
    top_riesgos = sorted(riesgos, key=lambda r: r.get("probabilidad",1)*r.get("impacto",1), reverse=True)[:5]
    story.append(Paragraph("4. Top Riesgos por Exposición", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    if top_riesgos:
        risk_data = [["Descripción", "Prob.", "Imp.", "Exp.", "Tratamiento"]]
        for r in top_riesgos:
            exp = r.get("probabilidad",1) * r.get("impacto",1)
            risk_data.append([
                r.get("descripcion","")[:60],
                str(r.get("probabilidad","—")),
                str(r.get("impacto","—")),
                str(exp),
                r.get("tratamiento","—").title(),
            ])
        rt = Table(risk_data, colWidths=[9.5*cm, 1.5*cm, 1.5*cm, 1.5*cm, 3*cm])
        rt.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  st["C_DARK"]),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  st["C_WHITE"]),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [st["C_LIGHT"], colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(rt)
    else:
        story.append(Paragraph("No hay riesgos registrados.", st["normal"]))

    _pie(story, fw_id, st)
    doc.build(story)
    return out


# ── Informe Detallado ────────────────────────────────────────────────────────

def generar_detallado(evaluacion: dict, stats: dict, controles: list,
                      fw_id: str, hallazgos: list, riesgos: list) -> Path:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak,
    )

    out = REPORTS_DIR / f"detallado_{evaluacion['id']}_{fw_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    st  = _build_styles()
    story = []

    # Portada
    _portada(story, evaluacion, "detallado", fw_id, st)
    story.append(PageBreak())

    # ── 1. Resumen ejecutivo ─────────────────────────────────────────────────
    story.append(Paragraph("1. Resumen Ejecutivo", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    mg    = stats["madurez_global"]
    nivel = MADUREZ_LABELS.get(round(mg), "N/D")
    story.append(Paragraph(
        f"La organización alcanzó una <b>madurez global de {mg}/5 — {nivel}</b> "
        f"sobre los controles de {_fw_label(fw_id)}. "
        f"Se evaluaron <b>{stats['respondidos']} de {stats['total']} controles</b> "
        f"({stats['progreso_pct']}% de completitud). "
        f"Los dominios con menor madurez requieren atención prioritaria.",
        st["normal"]
    ))
    story.append(Spacer(1, 8))
    story.append(_tabla_dominios(stats, st))
    story.append(Spacer(1, 12))

    # ── 2. Detalle por dominio ───────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("2. Evaluación por Dominio / Categoría", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    # Construir lookup de controles por ID
    ctrl_map = {c["id"]: c for c in controles}

    for dom, d in stats["dominios"].items():
        story.append(Paragraph(f"{dom} — Madurez promedio: {d['promedio_madurez']}/5", st["h2"]))

        # Controles de este dominio con respuestas
        dom_controles = [c for c in controles if c.get("dominio") == dom or c.get("id","").startswith(dom)]
        dom_respondidos = [c for c in dom_controles if c.get("madurez") is not None and c.get("aplica", 1)]

        if dom_respondidos:
            ctrl_data = [["ID Control", "Nombre", "Madurez", "Nivel", "Comentario"]]
            for c in sorted(dom_respondidos, key=lambda x: x.get("madurez", 0)):
                m = c.get("madurez", 0)
                ctrl_data.append([
                    c.get("id",""),
                    c.get("nombre","")[:45],
                    str(m),
                    MADUREZ_LABELS.get(m,"N/D"),
                    (c.get("comentario") or "")[:40],
                ])
            ct = Table(ctrl_data, colWidths=[2.5*cm, 6.5*cm, 1.5*cm, 2.5*cm, 4.5*cm])
            ct.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0),  st["C_MED"]),
                ("TEXTCOLOR",     (0, 0), (-1, 0),  st["C_WHITE"]),
                ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 7.5),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [st["C_LIGHT"], colors.white]),
                ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
                ("ALIGN",         (2, 0), (3, -1),  "CENTER"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(ct)
        else:
            story.append(Paragraph("Sin controles evaluados en este dominio.", st["small"]))
        story.append(Spacer(1, 8))

    # ── 3. Registro de brechas ───────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("3. Registro de Brechas (Controles con Madurez ≤ 2)", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    todas_brechas = []
    for dom, d in stats["dominios"].items():
        for b in d["brechas"]:
            b = dict(b)
            b["dominio"] = dom
            todas_brechas.append(b)
    todas_brechas.sort(key=lambda x: x["madurez"])

    if todas_brechas:
        brecha_data = [["#", "Control", "Nombre", "Dom.", "Madurez", "Nivel", "Prioridad"]]
        for i, b in enumerate(todas_brechas, 1):
            prioridad = "CRÍTICA" if b["madurez"] <= 1 else ("ALTA" if b["madurez"] == 2 else "MEDIA")
            brecha_data.append([
                str(i),
                b.get("id",""),
                b.get("nombre","")[:35],
                b.get("dominio",""),
                str(b["madurez"]),
                MADUREZ_LABELS.get(b["madurez"],"N/D"),
                prioridad,
            ])
        bt = Table(brecha_data, colWidths=[0.7*cm, 2.3*cm, 5.5*cm, 1.5*cm, 1.5*cm, 2*cm, 2*cm])
        bt.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  st["C_DARK"]),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  st["C_WHITE"]),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#fff7ed"), colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("ALIGN",         (0, 0), (0, -1),  "CENTER"),
            ("ALIGN",         (4, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(bt)
    else:
        story.append(Paragraph("No se detectaron brechas. Todos los controles evaluados tienen madurez ≥ 3.", st["normal"]))

    # ── 4. Hallazgos ────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("4. Registro de Hallazgos", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    if hallazgos:
        for h in hallazgos:
            story.append(Paragraph(f"• [{h.get('control_id','?')}] {h.get('titulo','')}", st["h3"]))
            story.append(Paragraph(
                f"<b>Tipo:</b> {h.get('tipo','').replace('_',' ').title()} | "
                f"<b>Severidad:</b> {h.get('severidad','').title()} | "
                f"<b>Estado:</b> {h.get('estado','').title()}",
                st["small"]
            ))
            if h.get("descripcion"):
                story.append(Paragraph(h["descripcion"][:300], st["small"]))
            if h.get("plan_accion"):
                story.append(Paragraph(f"<b>Plan:</b> {h['plan_accion'][:200]}", st["small"]))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No hay hallazgos registrados en esta evaluación.", st["normal"]))

    # ── 5. Registro de Riesgos ───────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("5. Registro de Riesgos", st["h1"]))
    story.append(HRFlowable(width="100%", thickness=1, color=st["C_BLUE"], spaceAfter=8))

    if riesgos:
        risk_data = [["#", "Descripción", "Prob.", "Imp.", "Exp.", "Tratamiento", "Estado"]]
        for i, r in enumerate(sorted(riesgos, key=lambda x: x.get("probabilidad",1)*x.get("impacto",1), reverse=True), 1):
            exp = r.get("probabilidad",1) * r.get("impacto",1)
            risk_data.append([
                str(i),
                r.get("descripcion","")[:55],
                str(r.get("probabilidad","—")),
                str(r.get("impacto","—")),
                str(exp),
                r.get("tratamiento","—").title(),
                r.get("estado","—").title(),
            ])
        rt = Table(risk_data, colWidths=[0.7*cm, 7.5*cm, 1.3*cm, 1.3*cm, 1.3*cm, 2.5*cm, 2*cm])
        rt.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, 0),  st["C_DARK"]),
            ("TEXTCOLOR",     (0, 0), (-1, 0),  st["C_WHITE"]),
            ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0, 0), (-1, -1), 7.5),
            ("ROWBACKGROUNDS",(0, 1), (-1, -1), [st["C_LIGHT"], colors.white]),
            ("GRID",          (0, 0), (-1, -1), 0.3, colors.HexColor("#cbd5e1")),
            ("ALIGN",         (0, 0), (0, -1),  "CENTER"),
            ("ALIGN",         (2, 0), (5, -1),  "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(rt)
    else:
        story.append(Paragraph("No hay riesgos registrados en esta evaluación.", st["normal"]))

    _pie(story, fw_id, st)
    doc.build(story)
    return out


# ── Punto de entrada principal ───────────────────────────────────────────────

def generar_informe(evaluacion: dict, stats: dict, controles: list,
                    fw_id: str, tipo: str,
                    hallazgos: list = None, riesgos: list = None) -> Path:
    """
    Genera el informe solicitado.
    tipo: "ejecutivo" | "detallado"
    """
    hallazgos = hallazgos or []
    riesgos   = riesgos   or []

    try:
        if tipo == "detallado":
            return generar_detallado(evaluacion, stats, controles, fw_id, hallazgos, riesgos)
        else:
            return generar_ejecutivo(evaluacion, stats, controles, fw_id, hallazgos, riesgos)
    except ImportError:
        # Fallback texto plano si no hay reportlab
        out = REPORTS_DIR / f"{tipo}_{evaluacion['id']}_{fw_id}.txt"
        lines = [
            f"{_fw_label(fw_id)} — {tipo.title()}",
            f"Empresa: {evaluacion['empresa']}",
            f"Evaluación: {evaluacion['nombre']}",
            f"Fecha: {datetime.now().strftime('%d/%m/%Y')}",
            f"Madurez global: {stats['madurez_global']}/5",
            "",
        ]
        for dom, d in stats["dominios"].items():
            lines.append(f"\n{dom}: {d['promedio_madurez']}/5 — {len(d['brechas'])} brechas")
        out.write_text("\n".join(lines), encoding="utf-8")
        return out


# Backward compat alias
def generar_pdf(evaluacion, stats, controles):
    fw_id = "ISO27001"
    try:
        fws = evaluacion.get("frameworks", '["ISO27001"]')
        import json
        fw_list = json.loads(fws) if isinstance(fws, str) else fws
        if fw_list:
            fw_id = fw_list[0]
    except Exception:
        pass
    return generar_informe(evaluacion, stats, controles, fw_id, "ejecutivo")
