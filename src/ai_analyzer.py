"""
Análisis de evidencias con Ollama (motor de IA local).
Soporta cualquier evidencia: PDF, DOCX, TXT/CSV/JSON/XML e imágenes (PNG/JPG/WEBP/GIF/BMP).

Ruteo por capacidad:
  - Documentos  → se extrae el texto y lo analiza un MODELO DE TEXTO.
  - Imágenes    → se envían en base64 a un MODELO DE VISIÓN (multimodal).

Los modelos se eligen automáticamente entre los instalados, por orden de
preferencia. Si llega una imagen y no hay ningún modelo de visión instalado,
se devuelve un error explícito (en vez de mandarla a un modelo de texto que
no la puede "ver").
"""
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

OLLAMA_BASE = "http://localhost:11434"
OLLAMA_URL  = OLLAMA_BASE + "/api/generate"

# Preferencia de modelos por capacidad (el primero instalado gana).
# Para texto, un modelo de visión también sirve como último recurso.
TEXT_MODELS   = ["qwen2.5:14b", "qwen2.5:7b", "llama3.1:8b", "qwen2.5:3b", "minicpm-v", "llama3.2-vision:11b"]
VISION_MODELS = ["minicpm-v", "llama3.2-vision:11b", "llama3.2-vision", "qwen2.5vl", "llava"]

MODEL_TEXT   = "llama3.1:8b"   # usado solo si no se puede consultar /api/tags


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

def _modelos_instalados() -> list[str]:
    """Lista los modelos instalados en Ollama (nombre completo con tag)."""
    try:
        req = urllib.request.Request(OLLAMA_BASE + "/api/tags")
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def _elegir(preferidos: list[str], instalados: list[str]) -> str | None:
    """Primer modelo preferido que esté instalado, respetando el orden de preferencia.

    Un preferido con tag (p. ej. "qwen2.5:14b") exige coincidencia exacta.
    Un preferido sin tag (p. ej. "minicpm-v") coincide con cualquier tag
    instalado de esa base (minicpm-v:latest, etc.).
    """
    bases = {}
    for n in instalados:
        bases.setdefault(n.split(":")[0], n)
    for p in preferidos:
        if ":" in p:                      # tag explícito → match exacto
            if p in instalados:
                return p
        elif p in bases:                  # sin tag → match por base
            return bases[p]
    return None


def _seleccionar_modelo(necesita_vision: bool) -> str | None:
    """Elige el mejor modelo instalado para el tipo de evidencia.

    Devuelve None solo cuando se necesita visión y no hay ningún modelo
    multimodal instalado (caso que el llamador convierte en error explícito).
    """
    instalados = _modelos_instalados()
    if necesita_vision:
        return _elegir(VISION_MODELS, instalados)
    # Texto: preferidos → cualquier modelo instalado → constante de respaldo
    return _elegir(TEXT_MODELS, instalados) or (instalados[0] if instalados else MODEL_TEXT)


def _llamar_ollama(prompt: str, imagen_b64: str = None) -> dict:
    necesita_vision = imagen_b64 is not None
    modelo = _seleccionar_modelo(necesita_vision)
    if modelo is None:
        return _error_ollama(
            "No hay un modelo de visión instalado para analizar imágenes. "
            "Instalá uno con: ollama pull minicpm-v"
        )
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1, "num_predict": 800},
        # Mantener el modelo residente en memoria entre análisis (evita
        # recargarlo en cada evidencia, costoso en GPUs chicas).
        "keep_alive": "10m",
    }
    if imagen_b64:
        payload["images"] = [imagen_b64]

    # Visión en hardware modesto puede requerir bastante tiempo en el primer
    # análisis (carga del modelo); damos margen amplio (el análisis corre en
    # segundo plano, no bloquea la UI).
    timeout_s = 300 if imagen_b64 else 180

    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        OLLAMA_URL,
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
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


# ── TPRM: sugerencia de riesgo inherente ───────────────────────────────────────

PROMPT_RIESGO_TERCERO = """Sos un analista experto en gestión de riesgos de terceros (TPRM).
Evaluá el RIESGO INHERENTE de incorporar al siguiente proveedor, ANTES de aplicar
controles. El riesgo inherente depende de la criticidad del servicio, la sensibilidad
de los datos que maneja y el tipo de relación.

PERFIL DEL PROVEEDOR
- Nombre: {nombre}
- Tipo de servicio: {tipo_servicio}
- Criticidad declarada: {criticidad}
- Datos que maneja: {datos_maneja}
- Notas adicionales: {notas}

Respondé EXCLUSIVAMENTE con un objeto JSON con esta forma exacta:
{{
  "nivel": "bajo|medio|alto|critico",
  "justificacion": "2-3 frases explicando el nivel asignado",
  "factores": ["factor de riesgo 1", "factor de riesgo 2"]
}}

Criterios de nivel:
- "critico": maneja datos altamente sensibles (financieros, salud, credenciales) y es clave para la operación.
- "alto": maneja datos personales/confidenciales o es relevante para la operación.
- "medio": acceso limitado a datos o impacto operativo moderado.
- "bajo": sin acceso a datos sensibles e impacto operativo menor.
"""

_NIVELES_RIESGO = {"bajo", "medio", "alto", "critico"}


def sugerir_riesgo_inherente(perfil: dict) -> dict:
    """Sugiere el nivel de riesgo inherente de un proveedor a partir de su perfil.

    Retorna: {"nivel": str|None, "justificacion": str, "factores": list, "error": str?}
    """
    prompt = PROMPT_RIESGO_TERCERO.format(
        nombre=perfil.get("nombre", "(sin nombre)"),
        tipo_servicio=perfil.get("tipo_servicio") or "(no especificado)",
        criticidad=perfil.get("criticidad") or "media",
        datos_maneja=perfil.get("datos_maneja") or "(no especificado)",
        notas=perfil.get("notas") or "(sin notas)",
    )
    resp = _llamar_ollama(prompt)
    if resp.get("error"):
        return {"nivel": None, "justificacion": resp.get("resumen", "Error de IA"),
                "factores": [], "error": resp["error"]}
    nivel = str(resp.get("nivel", "")).strip().lower()
    if nivel not in _NIVELES_RIESGO:
        nivel = None
    return {
        "nivel": nivel,
        "justificacion": resp.get("justificacion", ""),
        "factores": resp.get("factores", []) if isinstance(resp.get("factores"), list) else [],
    }
