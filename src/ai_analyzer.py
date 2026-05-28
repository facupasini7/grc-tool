"""
Análisis de evidencias con Ollama — llama3.2-vision:11b
Soporta: texto plano, PDF, DOCX, imágenes (PNG/JPG/WEBP)
"""
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_TEXT   = "llama3.2-vision:11b"
MODEL_VISION = "llama3.2-vision:11b"   # mismo modelo, soporta ambos

FALLBACK_MODELS = ["llama3.1:8b", "qwen2.5:7b", "qwen2.5:3b"]


# ── Extracción de texto ───────────────────────────────────────────────────────

def extraer_texto(filepath: str, filetype: str) -> tuple[str, bool]:
    """Devuelve (texto_extraido, es_imagen)."""
    path = Path(filepath)
    ext = path.suffix.lower()

    if ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"):
        return None, True   # imagen → va directo al modelo vision

    if ext == ".pdf":
        return _extraer_pdf(path), False

    if ext in (".docx", ".doc"):
        return _extraer_docx(path), False

    # texto plano, csv, json, xml, etc.
    try:
        return path.read_text(encoding="utf-8", errors="ignore"), False
    except Exception:
        return "", False


def _extraer_pdf(path: Path) -> str:
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            partes = []
            for p in pdf.pages[:20]:           # límite 20 páginas
                t = p.extract_text()
                if t:
                    partes.append(t)
        return "\n".join(partes)
    except ImportError:
        pass
    try:
        import PyPDF2
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join(
                p.extract_text() or "" for p in reader.pages[:20]
            )
    except ImportError:
        return "[PDF: instalá pdfplumber para extraer texto]"


def _extraer_docx(path: Path) -> str:
    try:
        import docx
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except ImportError:
        return "[DOCX: instalá python-docx para extraer texto]"


# ── Guía experta por framework ────────────────────────────────────────────────
# Conocimiento destilado de los estándares para que el analizador local (Ollama)
# evalúe la evidencia con el criterio propio de cada marco normativo.
# Equivalente práctico a los "GRC skills": inyecta el contexto del framework en el
# system prompt según el control que se está analizando.

FRAMEWORK_GUIDANCE = {
    "ISO27001": (
        "Marco: ISO/IEC 27001:2022 (SGSI). Los controles del Anexo A se agrupan en 4 temas: "
        "Organizacionales (5.x), Personas (6.x), Físicos (7.x) y Tecnológicos (8.x). "
        "Evaluá si la evidencia demuestra: (a) una política/procedimiento documentado y aprobado, "
        "(b) implementación operativa real, y (c) revisión/mejora continua. "
        "Buscá trazabilidad con el ciclo PDCA, dueños de control asignados, fechas de revisión y "
        "registros que prueben ejecución (no solo intención). Una política sin evidencia de operación = madurez ≤ 2."
    ),
    "NIST_CSF": (
        "Marco: NIST CSF 2.0. Funciones: GOVERN (GV), IDENTIFY (ID), PROTECT (PR), DETECT (DE), "
        "RESPOND (RS), RECOVER (RC). Evaluá contra Tiers de implementación (1 Parcial → 4 Adaptativo) y "
        "el perfil objetivo. Priorizá evidencia de gobernanza (roles, apetito de riesgo), gestión de activos, "
        "monitoreo continuo y capacidad de respuesta/recuperación probada (ejercicios, lecciones aprendidas)."
    ),
    "PCI": (
        "Marco: PCI DSS v4.0.1. 12 requisitos sobre el Cardholder Data Environment (CDE). "
        "Verificá: segmentación de red y alcance del CDE, cifrado de PAN en tránsito y reposo, "
        "gestión de accesos con mínimo privilegio y MFA, registro y monitoreo (req. 10), y pruebas de seguridad (req. 11). "
        "PCI exige cumplimiento binario por requisito: evidencia parcial o sin periodicidad definida = no_cumple o parcial."
    ),
    "BCRA": (
        "Marco: BCRA Com. 'A' 7777/7783 (Argentina) — requisitos mínimos para la gestión de riesgos de TI y "
        "seguridad de la información en entidades financieras y servicios financieros digitales. "
        "Evaluá: gobierno de TI/SI y responsabilidades del directorio, gestión de riesgos de TI, ciberseguridad, "
        "continuidad operativa, gestión de incidentes con reporte al BCRA, y control de terceros/proveedores críticos. "
        "Esperá evidencia formal, aprobada por nivel gerencial y con periodicidad de revisión definida."
    ),
    "SOC2": (
        "Marco: SOC 2 (AICPA) — Trust Services Criteria: Security (común), Availability, Processing Integrity, "
        "Confidentiality y Privacy. La evidencia debe demostrar que el control opera de forma efectiva durante un "
        "período (Type II), no solo en un punto en el tiempo (Type I). Buscá controles comunes (CC1–CC9): "
        "ambiente de control, evaluación de riesgos, monitoreo, actividades de control lógico y físico, y cambios."
    ),
    "CIS": (
        "Marco: CIS Controls v8 — 18 controles priorizados en Grupos de Implementación (IG1/IG2/IG3). "
        "Enfocate en salvaguardas concretas y medibles: inventario de activos y software, gestión de "
        "configuración segura, gestión de vulnerabilidades, control de accesos y privilegios administrativos, "
        "registros de auditoría y respuesta a incidentes. Preferí evidencia automatizada y verificable sobre la declarativa."
    ),
}


def _guia_framework(framework: str) -> str:
    """Devuelve la guía experta del marco normativo correspondiente."""
    if not framework:
        return FRAMEWORK_GUIDANCE["ISO27001"]
    fw = framework.upper().replace("-", "_").replace(" ", "_")
    # Coincidencia directa o por prefijo/contención (p. ej. A7777, PCI_DSS, NIST_CSF_2)
    if fw in FRAMEWORK_GUIDANCE:
        return FRAMEWORK_GUIDANCE[fw]
    if fw.startswith("A77") or "BCRA" in fw:
        return FRAMEWORK_GUIDANCE["BCRA"]
    if "NIST" in fw:
        return FRAMEWORK_GUIDANCE["NIST_CSF"]
    if "PCI" in fw:
        return FRAMEWORK_GUIDANCE["PCI"]
    if "SOC" in fw:
        return FRAMEWORK_GUIDANCE["SOC2"]
    if "CIS" in fw:
        return FRAMEWORK_GUIDANCE["CIS"]
    if "ISO" in fw or "27001" in fw:
        return FRAMEWORK_GUIDANCE["ISO27001"]
    return FRAMEWORK_GUIDANCE["ISO27001"]


# ── Prompt de auditoría ───────────────────────────────────────────────────────

PROMPT_TEXTO = """Eres un auditor senior de seguridad de la información certificado (CISA, ISO 27001 Lead Auditor).

GUÍA DEL MARCO NORMATIVO APLICABLE:
{guia_marco}

Tu tarea es analizar si la evidencia proporcionada demuestra cumplimiento del siguiente control de seguridad, aplicando el criterio del marco indicado arriba.

CONTROL: {control_id} — {control_nombre}
DESCRIPCIÓN: {control_descripcion}

EVIDENCIA PRESENTADA:
{evidencia}

Escala de madurez para "madurez_sugerida":
0 = Sin evidencia / No evaluable
1 = Inicial (ad-hoc, sin procedimientos formales)
2 = Básico (documentado pero no implementado consistentemente)
3 = Definido (implementado y documentado formalmente)
4 = Gestionado (monitorizado con métricas y mejora continua)
5 = Optimizado (proceso maduro, mejora continua y best practices)

Responde EXACTAMENTE en este formato JSON (sin texto adicional, solo el JSON):
{{
  "veredicto": "cumple" | "parcial" | "no_cumple",
  "madurez_sugerida": 0,
  "resumen": "Una oración que resume el veredicto",
  "fortalezas": ["punto positivo 1", "punto positivo 2"],
  "brechas": ["brecha 1", "brecha 2"],
  "recomendacion": "Qué debería mejorar o completar",
  "hallazgo_sugerido": {{
    "aplica": true | false,
    "tipo": "no_conformidad" | "observacion" | "oportunidad",
    "severidad": "critica" | "alta" | "media" | "baja",
    "titulo": "Título corto del hallazgo",
    "descripcion": "Descripción detallada del hallazgo para el informe de auditoría"
  }}
}}"""

PROMPT_IMAGEN = """Eres un auditor senior de seguridad de la información (CISA, ISO 27001 Lead Auditor).

GUÍA DEL MARCO NORMATIVO APLICABLE:
{guia_marco}

Analiza la imagen adjunta como evidencia para el siguiente control de seguridad, aplicando el criterio del marco indicado arriba:

CONTROL: {control_id} — {control_nombre}
DESCRIPCIÓN: {control_descripcion}

¿La imagen demuestra que este control está implementado?

Escala de madurez para "madurez_sugerida":
0 = Sin evidencia / No evaluable
1 = Inicial (ad-hoc)
2 = Básico (documentado pero inconsistente)
3 = Definido (implementado formalmente)
4 = Gestionado (con métricas)
5 = Optimizado (mejora continua)

Responde EXACTAMENTE en este formato JSON (sin texto adicional):
{{
  "veredicto": "cumple" | "parcial" | "no_cumple",
  "madurez_sugerida": 0,
  "resumen": "Una oración que resume el veredicto",
  "fortalezas": ["punto positivo 1"],
  "brechas": ["brecha 1"],
  "recomendacion": "Qué debería mejorar o completar",
  "hallazgo_sugerido": {{
    "aplica": true | false,
    "tipo": "no_conformidad" | "observacion" | "oportunidad",
    "severidad": "critica" | "alta" | "media" | "baja",
    "titulo": "Título corto del hallazgo",
    "descripcion": "Descripción detallada del hallazgo"
  }}
}}"""


# ── Llamada a Ollama ──────────────────────────────────────────────────────────

def _modelo_disponible() -> str:
    """Detecta qué modelo de Ollama está disponible."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read())
        nombres = [m["name"].split(":")[0] for m in data.get("models", [])]
        if "llama3.2-vision" in nombres:
            return MODEL_TEXT
        for m in FALLBACK_MODELS:
            base = m.split(":")[0]
            if base in nombres:
                return m
        # Si hay algo instalado, usar el primero
        if data.get("models"):
            return data["models"][0]["name"]
    except Exception:
        pass
    return MODEL_TEXT  # intento igualmente


def _llamar_ollama(prompt: str, imagen_b64: str = None) -> dict:
    modelo = _modelo_disponible()
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1, "num_predict": 800},
    }
    if imagen_b64:
        payload["images"] = [imagen_b64]

    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read())
        raw = resp.get("response", "{}")
        # Limpiar markdown si el modelo envuelve en ```json
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except urllib.error.URLError:
        return _error_ollama("Ollama no está corriendo. Inicialo con: ollama serve")
    except json.JSONDecodeError as e:
        return _error_ollama(f"El modelo devolvió JSON inválido: {e}")
    except Exception as e:
        return _error_ollama(str(e))


def _error_ollama(msg: str) -> dict:
    return {
        "veredicto": "pendiente",
        "madurez_sugerida": None,
        "resumen": f"Error al conectar con el motor de IA: {msg}",
        "fortalezas": [],
        "brechas": [],
        "recomendacion": "Verificá que Ollama esté corriendo y el modelo descargado.",
        "hallazgo_sugerido": {"aplica": False},
        "error": msg,
    }


# ── API pública ───────────────────────────────────────────────────────────────

def analizar_evidencia(
    filepath: str,
    filetype: str,
    control_id: str,
    control_nombre: str,
    control_descripcion: str,
    framework: str = "ISO27001",
) -> dict:
    """Punto de entrada principal. Devuelve dict con análisis.

    `framework` selecciona la guía experta del marco normativo que se inyecta
    en el system prompt para mejorar la precisión del análisis.
    """
    texto, es_imagen = extraer_texto(filepath, filetype)
    guia = _guia_framework(framework)

    if es_imagen:
        try:
            img_bytes = Path(filepath).read_bytes()
            img_b64 = base64.b64encode(img_bytes).decode()
        except Exception as e:
            return _error_ollama(f"No se pudo leer la imagen: {e}")

        prompt = PROMPT_IMAGEN.format(
            guia_marco=guia,
            control_id=control_id,
            control_nombre=control_nombre,
            control_descripcion=control_descripcion,
        )
        return _llamar_ollama(prompt, img_b64)

    # Texto — truncar si es muy largo (aprox. 6000 tokens)
    if texto and len(texto) > 8000:
        texto = texto[:8000] + "\n\n[... documento truncado por longitud ...]"

    prompt = PROMPT_TEXTO.format(
        guia_marco=guia,
        control_id=control_id,
        control_nombre=control_nombre,
        control_descripcion=control_descripcion,
        evidencia=texto or "(archivo vacío o sin texto extraíble)",
    )
    return _llamar_ollama(prompt)
