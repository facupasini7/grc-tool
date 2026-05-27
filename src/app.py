"""
GRC Tool — servidor principal
"""
import json
import os
import re
import base64
import socketserver
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from database import get_conn, init_db, seed_roles_y_permisos
from data.controles_iso27001 import CONTROLES as CONTROLES_ISO, DOMINIOS as DOMINIOS_ISO
from data.controles_bcra import CONTROLES_BCRA, DOMINIOS_BCRA, DOMINIOS_A7777, DOMINIOS_A7783
from data.controles_pci import CONTROLES_PCI, DOMINIOS_PCI
from data.controles_nist_csf import CONTROLES_NIST, DOMINIOS_NIST
from data.controles_soc2 import CONTROLES_SOC2, DOMINIOS_SOC2
from data.controles_cis import CONTROLES_CIS, DOMINIOS_CIS
from report import generar_pdf, generar_informe
from ai_analyzer import analizar_evidencia

# Backwards compat aliases
CONTROLES = CONTROLES_ISO
DOMINIOS  = DOMINIOS_ISO

CONTROLES_A7777 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7777"]
CONTROLES_A7783 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7783"]

# ── Framework registry ────────────────────────────────────────────────────────
FRAMEWORK_REGISTRY = {
    "ISO27001": {
        "id":       "ISO27001",
        "label":    "ISO 27001:2022",
        "controles": CONTROLES_ISO,
        "dominios":  DOMINIOS_ISO,
        "n":        len(CONTROLES_ISO),
    },
    "NIST_CSF": {
        "id":       "NIST_CSF",
        "label":    "NIST CSF 2.0",
        "controles": CONTROLES_NIST,
        "dominios":  DOMINIOS_NIST,
        "n":        len(CONTROLES_NIST),
    },
    "SOC2": {
        "id":       "SOC2",
        "label":    "SOC 2 (TSC)",
        "controles": CONTROLES_SOC2,
        "dominios":  DOMINIOS_SOC2,
        "n":        len(CONTROLES_SOC2),
    },
    "CIS": {
        "id":       "CIS",
        "label":    "CIS Controls v8",
        "controles": CONTROLES_CIS,
        "dominios":  DOMINIOS_CIS,
        "n":        len(CONTROLES_CIS),
    },
    # Legacy cobertura-only frameworks (no direct eval support)
    "A7777": {"id":"A7777","label":"BCRA A 7777","controles":CONTROLES_A7777,"dominios":DOMINIOS_A7777,"n":len(CONTROLES_A7777)},
    "A7783": {"id":"A7783","label":"BCRA A 7783","controles":CONTROLES_A7783,"dominios":DOMINIOS_A7783,"n":len(CONTROLES_A7783)},
    "BCRA":  {"id":"BCRA", "label":"BCRA",        "controles":CONTROLES_BCRA, "dominios":DOMINIOS_BCRA, "n":len(CONTROLES_BCRA)},
    "PCI":   {"id":"PCI",  "label":"PCI DSS v4.0","controles":CONTROLES_PCI,  "dominios":DOMINIOS_PCI,  "n":len(CONTROLES_PCI)},
}

def _rol_key_from_nombre(nombre: str) -> str:
    """Mapea nombre de rol en tabla roles → key en usuarios.rol."""
    return {
        "Administrador":  "admin",
        "Analista GRC":   "analista",
        "Auditor Externo":"auditor_externo",
        "Auditado":       "auditado",
    }.get(nombre, nombre.lower().replace(" ", "_"))


def get_primary_framework(eval_row) -> str:
    """Return the first selectable framework ID for an evaluation."""
    try:
        fws = json.loads(eval_row["frameworks"] or '["ISO27001"]')
        if fws:
            return fws[0]
    except Exception:
        pass
    return "ISO27001"


def seed_controles_db():
    """Populate controles_fw table from Python data files (only inserts missing rows)."""
    with get_conn() as conn:
        for fw_id, fw in FRAMEWORK_REGISTRY.items():
            ctrl_list = fw.get("controles", [])
            for i, c in enumerate(ctrl_list):
                try:
                    conn.execute(
                        """INSERT OR IGNORE INTO controles_fw
                           (id, framework, nombre, descripcion, dominio, categoria, orden, activo, es_custom)
                           VALUES (?,?,?,?,?,?,?,1,0)""",
                        (
                            c["id"], fw_id,
                            c.get("nombre") or c.get("name", ""),
                            c.get("descripcion", ""),
                            c.get("dominio", ""),
                            c.get("categoria", c.get("dominio", "")),
                            i,
                        ),
                    )
                except Exception:
                    pass


def get_controles_db(fw_id: str) -> list:
    """Return active controls for a framework from the DB."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM controles_fw WHERE framework=? AND activo=1 ORDER BY orden, id",
            (fw_id,),
        ).fetchall()
    return [dict(r) for r in rows]

BASE_DIR     = Path(__file__).parent.parent
STATIC_DIR   = BASE_DIR / "static"
UPLOADS_DIR  = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB

EXTENSIONES_VALIDAS = {
    ".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp",
}


# ── Helpers de dominio ────────────────────────────────────────────────────────

def controles_por_dominio():
    agrupados = {}
    for d in DOMINIOS:
        agrupados[d] = [c for c in CONTROLES if c["dominio"] == d]
    return agrupados


def get_control(ctrl_id: str):
    return next((c for c in CONTROLES if c["id"] == ctrl_id), None)


def calcular_stats(evaluacion_id):
    with get_conn() as conn:
        filas = conn.execute(
            "SELECT control_id, madurez, aplica FROM respuestas WHERE evaluacion_id = ?",
            (evaluacion_id,),
        ).fetchall()

    respuestas = {r["control_id"]: dict(r) for r in filas}
    stats = {"dominios": {}, "total": 0, "respondidos": 0, "madurez_global": 0}

    for dominio, controles in controles_por_dominio().items():
        aplicables  = [c for c in controles if respuestas.get(c["id"], {}).get("aplica", 1)]
        respondidos = [c for c in aplicables if c["id"] in respuestas and respuestas[c["id"]]["madurez"] > 0]
        madureces   = [respuestas[c["id"]]["madurez"] for c in respondidos]
        promedio    = round(sum(madureces) / len(madureces), 2) if madureces else 0

        stats["dominios"][dominio] = {
            "nombre": DOMINIOS[dominio],
            "total": len(aplicables),
            "respondidos": len(respondidos),
            "promedio_madurez": promedio,
            "brechas": [
                {
                    "id": c["id"],
                    "nombre": c["nombre"],
                    "madurez": respuestas[c["id"]]["madurez"] if c["id"] in respuestas else 0,
                }
                for c in aplicables
                if c["id"] not in respuestas or respuestas[c["id"]]["madurez"] < 3
            ],
        }
        stats["total"]      += len(aplicables)
        stats["respondidos"] += len(respondidos)

    todas = [
        respuestas[r]["madurez"]
        for r in respuestas
        if respuestas[r]["aplica"] and respuestas[r]["madurez"] > 0
    ]
    stats["madurez_global"] = round(sum(todas) / len(todas), 2) if todas else 0
    stats["progreso_pct"]   = round(stats["respondidos"] / stats["total"] * 100, 1) if stats["total"] else 0
    return stats


def calcular_cobertura(evaluacion_id: int, framework: str):
    """Calcula cobertura estimada de A7777, A7783, BCRA o PCI basada en madurez ISO 27001."""
    fw_map = {
        "A7777": (CONTROLES_A7777, DOMINIOS_A7777),
        "A7783": (CONTROLES_A7783, DOMINIOS_A7783),
        "BCRA":  (CONTROLES_BCRA,  DOMINIOS_BCRA),
        "PCI":   (CONTROLES_PCI,   DOMINIOS_PCI),
    }
    controles_fw, dominios_fw = fw_map[framework]

    with get_conn() as conn:
        filas = conn.execute(
            "SELECT control_id, madurez, aplica FROM respuestas WHERE evaluacion_id = ?",
            (evaluacion_id,),
        ).fetchall()
    madureces_iso = {r["control_id"]: dict(r) for r in filas}

    dominios_result  = {}
    controles_result = []

    for ctrl in controles_fw:
        mapped = ctrl.get("iso_mapping", [])
        scores = [
            madureces_iso[iso]["madurez"]
            for iso in mapped
            if iso in madureces_iso
            and madureces_iso[iso].get("aplica", 1)
            and madureces_iso[iso]["madurez"] > 0
        ]
        madurez_est   = round(sum(scores) / len(scores), 2) if scores else 0
        cubierto      = len(scores)
        total_mapped  = len(mapped)

        controles_result.append({
            "id":                     ctrl["id"],
            "nombre":                 ctrl["nombre"],
            "dominio":                ctrl["dominio"],
            "referencia":             ctrl.get("referencia", ""),
            "iso_mapping":            mapped,
            "madurez_estimada":       madurez_est,
            "controles_iso_cubiertos": cubierto,
            "controles_iso_total":    total_mapped,
            "evidencia_requerida":    ctrl.get("evidencia_requerida", []),
        })

        dom = ctrl["dominio"]
        if dom not in dominios_result:
            dominios_result[dom] = {
                "nombre": dominios_fw[dom],
                "total": 0, "con_cobertura": 0, "madurez_sum": 0.0,
            }
        dominios_result[dom]["total"] += 1
        if madurez_est > 0:
            dominios_result[dom]["con_cobertura"] += 1
            dominios_result[dom]["madurez_sum"]   += madurez_est

    for dom in dominios_result:
        n = dominios_result[dom]["con_cobertura"]
        dominios_result[dom]["madurez_promedio"] = (
            round(dominios_result[dom]["madurez_sum"] / n, 2) if n else 0
        )
        del dominios_result[dom]["madurez_sum"]

    return {"framework": framework, "dominios": dominios_result, "controles": controles_result}


# ── Handler HTTP ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # silenciar logs HTTP en consola

    # ── Helpers de respuesta ──────────────────────────────────────────────────

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_json_with_cookie(self, data, cookie: str, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, content_type):
        try:
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── Auth helpers ──────────────────────────────────────────────────────────

    def _get_user(self):
        from auth import get_user_from_token, parse_session_token
        token = parse_session_token(self.headers.get("Cookie", ""))
        return get_user_from_token(token)

    def _require_auth(self):
        """
        Retorna el usuario autenticado o None.
        Si GRC_AUTH=0 (modo test/dev), retorna un usuario admin ficticio.
        """
        if os.environ.get("GRC_AUTH", "1") == "0":
            return {"id": None, "username": "dev", "nombre": "Dev", "rol": "admin", "debe_cambiar_password": 0}
        user = self._get_user()
        if not user:
            if self.path.startswith("/api/"):
                self.send_json({"error": "No autenticado"}, 401)
            else:
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
            return None
        return user

    def _require_admin(self, user):
        if user.get("rol") != "admin":
            self.send_json({"error": "Se requiere rol Administrador."}, 403)
            return False
        return True

    def _require_perm(self, user, permiso: str) -> bool:
        """Chequea permiso granular. Admin siempre tiene acceso total."""
        if user.get("rol") == "admin":
            return True
        perms = user.get("permisos") or []
        if permiso not in perms:
            self.send_json({"error": f"Permiso requerido: {permiso}"}, 403)
            return False
        return True

    def _require_write(self, user):
        """admin y analista pueden escribir; auditor_externo solo lectura."""
        if user.get("rol") in ("admin", "analista", "auditor"):
            return True
        self.send_json({"error": "Tu rol es de solo lectura. No podés realizar esta operación."}, 403)
        return False

    def _require_audit_access(self, user):
        """Audit log: visible para admin y auditor_externo."""
        if user.get("rol") in ("admin", "auditor_externo"):
            return True
        self.send_json({"error": "Sin acceso al log de auditoría."}, 403)
        return False

    def _require_evidence_upload(self, user):
        """Subir evidencia: admin, analista/auditor y auditado."""
        if user.get("rol") in ("admin", "analista", "auditor", "auditado"):
            return True
        self.send_json({"error": "Tu rol no permite subir evidencia."}, 403)
        return False

    def _block_auditado(self, user):
        """Bloquea al auditado de endpoints de resultados/hallazgos (confidenciales)."""
        if user.get("rol") == "auditado":
            self.send_json({"error": "Sin acceso a esta sección."}, 403)
            return True
        return False

    def _ip(self):
        return self.client_address[0]

    # ── Login / Logout ────────────────────────────────────────────────────────

    def _handle_register(self, body):
        from auth import hash_password
        username = body.get("username", "").strip()
        password = body.get("password", "")
        nombre   = body.get("nombre", "").strip()
        email    = body.get("email", "").strip()
        if not username or not password or not nombre:
            self.send_json({"error": "Nombre, usuario y contraseña son requeridos."}, 400)
            return
        if len(password) < 8:
            self.send_json({"error": "La contraseña debe tener al menos 8 caracteres."}, 400)
            return
        try:
            with get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO usuarios (username, password_hash, nombre, email, rol, aprobado) "
                    "VALUES (?,?,?,?,?,?)",
                    (username, hash_password(password), nombre, email, "auditado", 0),
                )
            self.send_json({"ok": True, "id": cur.lastrowid})
        except Exception as e:
            self.send_json({"error": f"El usuario '{username}' ya existe."}, 409)

    def _handle_forgot_password(self, body):
        from auth import create_reset_token, send_reset_email
        identifier = body.get("email_or_username", "").strip()
        if not identifier:
            self.send_json({"error": "Ingresá tu email o usuario."}, 400)
            return
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id, email, username FROM usuarios "
                "WHERE (email=? OR username=?) AND activo=1",
                (identifier, identifier),
            ).fetchone()
        # Siempre responder ok para no revelar si existe el usuario
        if row:
            row = dict(row)
            token = create_reset_token(row["id"])
            base_url = f"http://{self.headers.get('Host', 'localhost:8090')}"
            email_sent = send_reset_email(row["email"], token, base_url) if row["email"] else False
            reset_url  = f"{base_url}/reset-password?token={token}"
            # Si no hay SMTP, devolvemos el link para que el admin lo comparta
            self.send_json({"ok": True, "email_sent": email_sent,
                            "reset_url": reset_url if not email_sent else None})
        else:
            self.send_json({"ok": True, "email_sent": False, "reset_url": None})

    def _handle_reset_password(self, body):
        from auth import validate_reset_token, consume_reset_token, hash_password
        token  = body.get("token", "").strip()
        new_pw = body.get("password", "")
        if not token:
            self.send_json({"error": "Token inválido."}, 400)
            return
        if len(new_pw) < 8:
            self.send_json({"error": "La contraseña debe tener al menos 8 caracteres."}, 400)
            return
        uid = validate_reset_token(token)
        if not uid:
            self.send_json({"error": "El link expiró o ya fue utilizado."}, 400)
            return
        consume_reset_token(token)
        with get_conn() as conn:
            conn.execute(
                "UPDATE usuarios SET password_hash=?, debe_cambiar_password=0 WHERE id=?",
                (hash_password(new_pw), uid),
            )
        self.send_json({"ok": True})

    def _handle_login(self, body):
        from auth import verify_password, create_session, log_action
        username = body.get("username", "").strip()
        password = body.get("password", "")

        with get_conn() as conn:
            row = conn.execute(
                "SELECT id, password_hash, nombre, rol, activo, aprobado, debe_cambiar_password "
                "FROM usuarios WHERE username=?",
                (username,),
            ).fetchone()

        if row and verify_password(password, row["password_hash"]):
            row = dict(row)
            if not row["activo"]:
                self.send_json({"error": "Cuenta desactivada. Contactá al administrador."}, 401)
                return
            if not row["aprobado"]:
                self.send_json({"error": "Tu cuenta está pendiente de aprobación por el administrador."}, 401)
                return
            token = create_session(row["id"])
            log_action(row["id"], username, "login", ip=self._ip())
            with get_conn() as conn:
                conn.execute(
                    "UPDATE usuarios SET ultimo_login=datetime('now') WHERE id=?", (row["id"],)
                )
            cookie = f"grc_session={token}; HttpOnly; SameSite=Lax; Path=/; Max-Age=28800"
            self.send_json_with_cookie(
                {"ok": True, "nombre": row["nombre"], "rol": row["rol"],
                 "debe_cambiar_password": row["debe_cambiar_password"]}, cookie
            )
        else:
            log_action(None, username, "login_fallido", ip=self._ip())
            self.send_json({"error": "Usuario o contraseña incorrectos"}, 401)

    def _handle_logout(self):
        from auth import delete_session, log_action, parse_session_token
        token = parse_session_token(self.headers.get("Cookie", ""))
        user  = self._get_user()
        if user:
            log_action(user["id"], user["username"], "logout", ip=self._ip())
        delete_session(token)
        clear = "grc_session=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0"
        self.send_json_with_cookie({"ok": True}, clear)

    # ── GET ───────────────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        qs     = parse_qs(parsed.query)

        # ── Rutas siempre públicas — todas sirven la SPA ──
        if path in ("/login", "/register", "/forgot-password",
                    "/reset-password", "/change-password"):
            # Redirect legacy HTML routes to the React SPA
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return
        if path in ("/", "/index.html"):
            self.send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            rel   = path[len("/static/"):]
            ext   = Path(rel).suffix
            tipos = {
                ".css":  "text/css",
                ".js":   "application/javascript",
                ".jsx":  "application/javascript",
                ".svg":  "image/svg+xml",
                ".woff2":"font/woff2",
                ".woff": "font/woff",
            }
            self.send_file(STATIC_DIR / rel, tipos.get(ext, "application/octet-stream"))
            return

        # ── Requiere autenticación ──
        user = self._require_auth()
        if not user:
            return

        if path == "/api/me":
            self.send_json({
                "id": user["id"], "username": user["username"],
                "nombre": user["nombre"], "rol": user["rol"],
                "debe_cambiar_password": user.get("debe_cambiar_password", 0),
            })

        elif path == "/api/audit-log":
            if not self._require_audit_access(user):
                return
            limit       = int(qs.get("limit",       ["500"])[0])
            offset      = int(qs.get("offset",      ["0"])[0])
            accion      = qs.get("accion",      [None])[0]
            usuario     = qs.get("usuario",     [None])[0]
            fecha_desde = qs.get("fecha_desde", [None])[0]
            fecha_hasta = qs.get("fecha_hasta", [None])[0]

            where, params = [], []
            if accion:
                where.append("accion LIKE ?"); params.append(accion + "%")
            if usuario:
                where.append("(usuario_nombre LIKE ? OR usuario_id = ?)"); params += ["%" + usuario + "%", usuario]
            if fecha_desde:
                where.append("timestamp >= ?"); params.append(fecha_desde)
            if fecha_hasta:
                # include the full day
                where.append("timestamp < date(?, '+1 day')"); params.append(fecha_hasta)

            sql = "SELECT al.*, u.nombre AS usuario_nombre FROM audit_log al LEFT JOIN usuarios u ON al.usuario_id = u.id"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY al.timestamp DESC LIMIT ? OFFSET ?"
            params += [limit, offset]

            with get_conn() as conn:
                rows = conn.execute(sql, params).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == "/api/usuarios":
            if not self._require_admin(user):
                return
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT id, username, nombre, rol, activo, creado_en, ultimo_login "
                    "FROM usuarios ORDER BY creado_en"
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == "/api/participantes":
            # Lista liviana de usuarios para asignar a evaluaciones — admin y analista
            if user.get("rol") not in ("admin", "analista"):
                self.send_json({"error": "Sin acceso."}, 403)
                return
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT id, username, nombre, rol FROM usuarios "
                    "WHERE activo = 1 AND aprobado = 1 ORDER BY nombre"
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == "/api/evaluaciones":
            with get_conn() as conn:
                if user.get("rol") == "auditado" and user.get("id"):
                    rows = conn.execute(
                        """SELECT e.* FROM evaluaciones e
                           JOIN evaluacion_usuarios eu ON eu.evaluacion_id = e.id
                           WHERE eu.usuario_id = ?
                           ORDER BY e.actualizada DESC, e.id DESC""",
                        (user["id"],),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM evaluaciones ORDER BY actualizada DESC, id DESC"
                    ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and "/controles" in path:
            # GET /api/evaluaciones/{id}/controles[?framework=ISO27001]
            # Returns controls for the primary (or specified) framework merged with responses
            eid = int(path.split("/")[3])
            fw_override = qs.get("framework", [None])[0]
            with get_conn() as conn:
                ev = conn.execute("SELECT * FROM evaluaciones WHERE id=?", (eid,)).fetchone()
                if not ev:
                    self.send_json({"error": "no encontrada"}, 404); return
                resps = conn.execute(
                    "SELECT * FROM respuestas WHERE evaluacion_id=?", (eid,)
                ).fetchall()
            fw_id = fw_override or get_primary_framework(ev)
            fw    = FRAMEWORK_REGISTRY.get(fw_id, FRAMEWORK_REGISTRY["ISO27001"])
            ctrl_list = get_controles_db(fw_id)
            dominios_map = fw["dominios"]
            resp_map = {r["control_id"]: dict(r) for r in resps}
            result = []
            for c in ctrl_list:
                r = resp_map.get(c["id"], {})
                dom = c.get("dominio", "")
                result.append({
                    "id":             c["id"],
                    "nombre":         c.get("nombre", ""),
                    "dominio":        dom,
                    "dominio_nombre": dominios_map.get(dom, dom),
                    "descripcion":    c.get("descripcion", ""),
                    "categoria":      c.get("categoria", dom),
                    "madurez":        r.get("madurez", 0) or 0,
                    "comentario":     r.get("comentario", "") or "",
                    "aplica":         r.get("aplica", 1) if r else 1,
                    "excepcion_justificacion": r.get("excepcion_justificacion", ""),
                    "excepcion_aprobada":      r.get("excepcion_aprobada", 0),
                    "excepcion_hasta":         r.get("excepcion_hasta", ""),
                    # IA suggestion fields
                    "ia_madurez_sugerida":        r.get("ia_madurez_sugerida") if r else None,
                    "ia_comentario":              r.get("ia_comentario", "") if r else "",
                    "ia_pendiente_confirmacion":  r.get("ia_pendiente_confirmacion", 0) if r else 0,
                })
            self.send_json({"controles": result, "framework": fw_id, "framework_label": fw["label"]})

        elif path.startswith("/api/evaluaciones/") and "/stats" in path:
            if self._block_auditado(user): return
            eid = int(path.split("/")[3])
            self.send_json(calcular_stats(eid))

        elif path.startswith("/api/evaluaciones/") and path.count("/") == 3 and path.split("/")[3].isdigit():
            # GET /api/evaluaciones/{id}
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                ev = conn.execute("SELECT * FROM evaluaciones WHERE id=?", (eid,)).fetchone()
            if not ev:
                self.send_json({"error": "no encontrada"}, 404); return
            self.send_json(dict(ev))

        elif path.startswith("/api/evaluaciones/") and "/respuestas" in path:
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM respuestas WHERE evaluacion_id = ?", (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and "/evidencias" in path:
            parts   = path.split("/")
            eid     = int(parts[3])
            ctrl_id = qs.get("control_id", [None])[0]
            with get_conn() as conn:
                if ctrl_id:
                    rows = conn.execute(
                        "SELECT * FROM evidencias WHERE evaluacion_id=? AND control_id=? ORDER BY subida_en DESC",
                        (eid, ctrl_id),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM evidencias WHERE evaluacion_id=? ORDER BY subida_en DESC", (eid,)
                    ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and "/hallazgos" in path:
            if self._block_auditado(user): return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM hallazgos WHERE evaluacion_id=? ORDER BY creado_en DESC", (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and path.endswith("/asignados"):
            if user.get("rol") not in ("admin", "analista"):
                self.send_json({"error": "Sin acceso."}, 403); return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    """SELECT u.id, u.username, u.nombre, u.rol, u.email
                       FROM evaluacion_usuarios eu JOIN usuarios u ON eu.usuario_id = u.id
                       WHERE eu.evaluacion_id = ?""", (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == "/api/controles":
            self.send_json(CONTROLES_ISO)

        elif path == "/api/dominios":
            self.send_json(DOMINIOS_ISO)

        elif path == "/api/frameworks":
            # Returns the catalogue of all selectable frameworks
            catalogue = [
                # ── Frameworks / normas con evaluación directa ──
                {"id":"ISO27001", "label":"ISO 27001:2022",  "icon":"ShieldCheck", "n":len(CONTROLES_ISO),  "tipo":"framework",   "descripcion":"Gestión de seguridad de la información (ISMS)"},
                {"id":"NIST_CSF", "label":"NIST CSF 2.0",    "icon":"Shield",       "n":len(CONTROLES_NIST), "tipo":"framework",   "descripcion":"Marco de ciberseguridad del NIST — 6 funciones (Govern, Identify, Protect, Detect, Respond, Recover)"},
                {"id":"SOC2",     "label":"SOC 2 (TSC)",      "icon":"Lock",         "n":len(CONTROLES_SOC2), "tipo":"framework",   "descripcion":"Trust Services Criteria del AICPA — Seguridad, Disponibilidad, Integridad, Confidencialidad, Privacidad"},
                {"id":"CIS",      "label":"CIS Controls v8",  "icon":"CheckSquare",  "n":len(CONTROLES_CIS),  "tipo":"framework",   "descripcion":"Centro para la Seguridad en Internet — 18 controles, IG1/IG2/IG3"},
                {"id":"PCI",      "label":"PCI DSS v4.0",     "icon":"CreditCard",   "n":len(CONTROLES_PCI),  "tipo":"framework",   "descripcion":"Estándar de seguridad para la industria de tarjetas de pago"},
                # ── Normativa regulatoria obligatoria (sin evaluación directa) ──
                {"id":"A7777",    "label":"Com. A 7777",      "icon":"Building",     "n":len(CONTROLES_A7777),"tipo":"regulacion",  "descripcion":"Gestión de riesgos de TI — Normativa obligatoria Banco Central de la Rep. Argentina"},
                {"id":"A7783",    "label":"Com. A 7783",      "icon":"Building",     "n":len(CONTROLES_A7783),"tipo":"regulacion",  "descripcion":"Gestión de incidentes de TI — Normativa obligatoria Banco Central de la Rep. Argentina"},
            ]
            self.send_json(catalogue)

        elif path == "/api/frameworks/bcra/controles":
            self.send_json(CONTROLES_BCRA)
        elif path == "/api/frameworks/bcra/dominios":
            self.send_json(DOMINIOS_BCRA)
        elif path == "/api/frameworks/a7777/controles":
            self.send_json(CONTROLES_A7777)
        elif path == "/api/frameworks/a7777/dominios":
            self.send_json(DOMINIOS_A7777)
        elif path == "/api/frameworks/a7783/controles":
            self.send_json(CONTROLES_A7783)
        elif path == "/api/frameworks/a7783/dominios":
            self.send_json(DOMINIOS_A7783)
        elif path == "/api/frameworks/pci/controles":
            self.send_json(CONTROLES_PCI)
        elif path == "/api/frameworks/pci/dominios":
            self.send_json(DOMINIOS_PCI)
        elif path == "/api/frameworks/nist_csf/controles":
            self.send_json(CONTROLES_NIST)
        elif path == "/api/frameworks/nist_csf/dominios":
            self.send_json(DOMINIOS_NIST)
        elif path == "/api/frameworks/soc2/controles":
            self.send_json(CONTROLES_SOC2)
        elif path == "/api/frameworks/soc2/dominios":
            self.send_json(DOMINIOS_SOC2)
        elif path == "/api/frameworks/cis/controles":
            self.send_json(CONTROLES_CIS)
        elif path == "/api/frameworks/cis/dominios":
            self.send_json(DOMINIOS_CIS)

        # ── Admin: ABM de controles por framework ──────────────────────────────
        elif path.startswith("/api/admin/frameworks/") and path.endswith("/controles"):
            if not self._require_admin(user): return
            fw_id = path.split("/")[4].upper()
            q        = qs.get("q", [""])[0].lower()
            page     = int(qs.get("page", ["1"])[0])
            per_page = int(qs.get("per_page", ["50"])[0])
            offset   = (page - 1) * per_page
            with get_conn() as conn:
                base_q = "FROM controles_fw WHERE framework=?"
                params = [fw_id]
                if q:
                    base_q += " AND (lower(id) LIKE ? OR lower(nombre) LIKE ? OR lower(dominio) LIKE ?)"
                    params += [f"%{q}%", f"%{q}%", f"%{q}%"]
                total = conn.execute(f"SELECT COUNT(*) {base_q}", params).fetchone()[0]
                rows  = conn.execute(
                    f"SELECT * {base_q} ORDER BY activo DESC, orden, id LIMIT ? OFFSET ?",
                    params + [per_page, offset],
                ).fetchall()
            fw_meta = FRAMEWORK_REGISTRY.get(fw_id, {})
            dominios_map = fw_meta.get("dominios", {})
            result = []
            for r in rows:
                d = dict(r)
                d["dominio_nombre"] = dominios_map.get(d["dominio"], d["dominio"])
                result.append(d)
            self.send_json({"controles": result, "total": total, "page": page, "per_page": per_page})

        elif path.startswith("/api/evaluaciones/") and "/cobertura/" in path:
            if self._block_auditado(user): return
            parts = path.split("/")
            eid   = int(parts[3])
            fw    = parts[5].upper()
            if fw not in ("A7777", "A7783", "BCRA", "PCI"):
                self.send_json({"error": "framework no soportado"}, 400)
                return
            self.send_json(calcular_cobertura(eid, fw))

        elif path.startswith("/api/report/"):
            if not self._require_perm(user, "reportes.generar"): return
            parts = path.split("/")   # ['', 'api', 'report', '{eid}']
            eid   = int(parts[3])
            tipo  = qs.get("tipo",      ["ejecutivo"])[0]   # ejecutivo | detallado
            fw_id = qs.get("framework", ["ISO27001"])[0]
            with get_conn() as conn:
                ev = conn.execute("SELECT * FROM evaluaciones WHERE id=?", (eid,)).fetchone()
                hallazgos_rows = conn.execute(
                    "SELECT * FROM hallazgos WHERE evaluacion_id=? AND framework=? ORDER BY severidad DESC",
                    (eid, fw_id)
                ).fetchall()
                riesgos_rows = conn.execute(
                    "SELECT r.*, u.nombre AS propietario_nombre FROM riesgos r "
                    "LEFT JOIN usuarios u ON r.propietario_id = u.id "
                    "WHERE r.evaluacion_id=? ORDER BY (r.probabilidad*r.impacto) DESC",
                    (eid,)
                ).fetchall()
            if not ev:
                self.send_json({"error": "no encontrada"}, 404)
                return
            stats     = calcular_stats(eid)
            controles = get_controles_db(fw_id)
            # Enriquecer controles con respuestas
            with get_conn() as conn:
                resp_rows = conn.execute(
                    "SELECT * FROM respuestas WHERE evaluacion_id=?", (eid,)
                ).fetchall()
            resp_map = {r["control_id"]: dict(r) for r in resp_rows}
            for c in controles:
                r = resp_map.get(c["id"], {})
                c["madurez"]    = r.get("madurez")
                c["comentario"] = r.get("comentario","")
                c["aplica"]     = r.get("aplica", 1)

            hallazgos = [dict(h) for h in hallazgos_rows]
            riesgos   = [dict(r) for r in riesgos_rows]

            pdf_path = generar_informe(dict(ev), stats, controles, fw_id, tipo, hallazgos, riesgos)
            data     = pdf_path.read_bytes()
            fname    = f"{tipo}-{fw_id}-{eid}.pdf"
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)

        # ── Riesgos ──
        elif path.startswith("/api/evaluaciones/") and "/riesgos" in path and path.count("/") == 4:
            if self._block_auditado(user): return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    """SELECT r.*, u.nombre AS propietario_nombre
                       FROM riesgos r
                       LEFT JOIN usuarios u ON r.propietario_id = u.id
                       WHERE r.evaluacion_id = ?
                       ORDER BY (r.probabilidad * r.impacto) DESC, r.creado_en DESC""",
                    (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/riesgos/") and path.count("/") == 3:
            if self._block_auditado(user): return
            rid = int(path.split("/")[3])
            with get_conn() as conn:
                row = conn.execute(
                    "SELECT r.*, u.nombre AS propietario_nombre FROM riesgos r "
                    "LEFT JOIN usuarios u ON r.propietario_id = u.id WHERE r.id=?", (rid,)
                ).fetchone()
            if not row: self.send_json({"error": "no encontrado"}, 404); return
            self.send_json(dict(row))

        # ── Tareas de un hallazgo ──
        elif path.startswith("/api/hallazgos/") and "/tareas" in path:
            if self._block_auditado(user): return
            hid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    """SELECT t.*, u.nombre AS asignado_nombre, u.email AS asignado_email
                       FROM tareas t LEFT JOIN usuarios u ON t.asignado_a = u.id
                       WHERE t.hallazgo_id = ? ORDER BY t.creado_en DESC""",
                    (hid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        # ── Deadlines de evidencia ──
        elif path.startswith("/api/evaluaciones/") and "/deadlines" in path:
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    """SELECT d.*, u.nombre AS asignado_nombre, u.email AS asignado_email
                       FROM deadlines_evidencia d
                       LEFT JOIN usuarios u ON d.asignado_a = u.id
                       WHERE d.evaluacion_id = ?
                       ORDER BY d.fecha_limite ASC""",
                    (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        # ── Historial de madurez ──
        elif path.startswith("/api/evaluaciones/") and "/historial-madurez" in path:
            if self._block_auditado(user): return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM historial_madurez WHERE evaluacion_id=? ORDER BY registrado_en ASC",
                    (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        # ── Comparar evaluaciones ──
        elif path.startswith("/api/evaluaciones/") and "/comparar" in path:
            if self._block_auditado(user): return
            eid1 = int(path.split("/")[3])
            eid2 = int(qs.get("con", [0])[0]) if qs.get("con") else None
            if not eid2:
                self.send_json({"error": "Parámetro 'con' requerido"}, 400); return
            with get_conn() as conn:
                r1 = conn.execute("SELECT control_id, madurez FROM respuestas WHERE evaluacion_id=?", (eid1,)).fetchall()
                r2 = conn.execute("SELECT control_id, madurez FROM respuestas WHERE evaluacion_id=?", (eid2,)).fetchall()
                ev1 = conn.execute("SELECT nombre FROM evaluaciones WHERE id=?", (eid1,)).fetchone()
                ev2 = conn.execute("SELECT nombre FROM evaluaciones WHERE id=?", (eid2,)).fetchone()
            m1 = {r["control_id"]: r["madurez"] for r in r1}
            m2 = {r["control_id"]: r["madurez"] for r in r2}
            todos = set(m1) | set(m2)
            delta = []
            for cid in todos:
                v1, v2 = m1.get(cid, 0), m2.get(cid, 0)
                if v1 != v2:
                    ctrl = get_control(cid)
                    delta.append({
                        "control_id": cid,
                        "nombre": ctrl["nombre"] if ctrl else cid,
                        "dominio": ctrl["dominio"] if ctrl else "",
                        "eval1": v1, "eval2": v2, "delta": v2 - v1,
                    })
            delta.sort(key=lambda x: abs(x["delta"]), reverse=True)
            self.send_json({
                "eval1": {"id": eid1, "nombre": ev1["nombre"] if ev1 else str(eid1)},
                "eval2": {"id": eid2, "nombre": ev2["nombre"] if ev2 else str(eid2)},
                "delta": delta,
                "resumen": {
                    "mejoraron": len([d for d in delta if d["delta"] > 0]),
                    "empeoraron": len([d for d in delta if d["delta"] < 0]),
                    "sin_cambio": len(todos) - len(delta),
                }
            })

        # ── Catálogo de permisos ──
        elif path == "/api/admin/permisos":
            if not self._require_admin(user): return
            with get_conn() as conn:
                rows = conn.execute("SELECT * FROM permisos ORDER BY categoria, id").fetchall()
            self.send_json([dict(r) for r in rows])

        # ── Roles: lista ──
        elif path == "/api/admin/roles":
            if not self._require_admin(user): return
            with get_conn() as conn:
                roles = conn.execute("SELECT * FROM roles ORDER BY es_sistema DESC, nombre").fetchall()
                result = []
                for r in roles:
                    rd = dict(r)
                    rd["n_usuarios"] = conn.execute(
                        "SELECT COUNT(*) FROM usuarios WHERE rol=?",
                        (_rol_key_from_nombre(rd["nombre"]),)
                    ).fetchone()[0]
                    perms = conn.execute(
                        "SELECT permiso_id FROM rol_permisos WHERE rol_id=?", (rd["id"],)
                    ).fetchall()
                    rd["permisos"] = [p["permiso_id"] for p in perms]
                    result.append(rd)
            self.send_json(result)

        # ── Rol: detalle ──
        elif path.startswith("/api/admin/roles/") and path.count("/") == 4:
            if not self._require_admin(user): return
            rid = int(path.split("/")[4])
            with get_conn() as conn:
                rol = conn.execute("SELECT * FROM roles WHERE id=?", (rid,)).fetchone()
                if not rol:
                    self.send_json({"error": "Rol no encontrado"}, 404); return
                perms = conn.execute(
                    "SELECT permiso_id FROM rol_permisos WHERE rol_id=?", (rid,)
                ).fetchall()
                rd = dict(rol)
                rd["permisos"] = [p["permiso_id"] for p in perms]
            self.send_json(rd)

        # ── Config sistema ──
        elif path == "/api/admin/config":
            if not self._require_admin(user): return
            with get_conn() as conn:
                rows = conn.execute("SELECT clave, valor FROM config_sistema").fetchall()
            self.send_json({r["clave"]: r["valor"] for r in rows})

        # ── Forzar chequeo de recordatorios ──
        elif path == "/api/admin/reminders/check":
            if not self._require_admin(user): return
            from reminders import check_and_send_reminders
            base_url = f"http://{self.headers.get('Host', 'localhost:8090')}"
            result = check_and_send_reminders(base_url)
            self.send_json(result)

        # ── Hallazgos globales (sin filtro de eval) ──
        elif path == "/api/hallazgos":
            if self._block_auditado(user): return
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM hallazgos ORDER BY creado_en DESC LIMIT 200"
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        else:
            self.send_response(404)
            self.end_headers()

    # ── POST ──────────────────────────────────────────────────────────────────

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw    = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw)
        except Exception:
            body = {}
        parsed = urlparse(self.path)
        path   = parsed.path

        # ── Rutas públicas ──
        if path == "/api/login":
            self._handle_login(body)
            return
        if path == "/api/logout":
            self._handle_logout()
            return
        if path == "/api/register":
            self._handle_register(body)
            return
        if path == "/api/forgot-password":
            self._handle_forgot_password(body)
            return
        if path == "/api/reset-password":
            self._handle_reset_password(body)
            return

        # ── Requiere autenticación ──
        user = self._require_auth()
        if not user:
            return

        from auth import log_action

        # ── Cambiar contraseña propia ──
        if path == "/api/change-password":
            from auth import hash_password as hp, verify_password as vp
            new_pw = body.get("password", "")
            if len(new_pw) < 8:
                self.send_json({"error": "La contraseña debe tener al menos 8 caracteres."}, 400)
                return
            with get_conn() as conn:
                conn.execute(
                    "UPDATE usuarios SET password_hash=?, debe_cambiar_password=0 WHERE id=?",
                    (hp(new_pw), user["id"]),
                )
            log_action(user["id"], user["username"], "cambiar_password", ip=self._ip())
            self.send_json({"ok": True})
            return

        # ── Asignar usuario a evaluación (admin) ──
        if path.startswith("/api/evaluaciones/") and path.endswith("/asignados"):
            if not self._require_admin(user): return
            eid = int(path.split("/")[3])
            uid = body.get("usuario_id")
            if not uid:
                self.send_json({"error": "usuario_id requerido"}, 400)
                return
            try:
                with get_conn() as conn:
                    conn.execute(
                        "INSERT OR IGNORE INTO evaluacion_usuarios (evaluacion_id, usuario_id) VALUES (?,?)",
                        (eid, uid),
                    )
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"error": str(e)}, 400)
            return

        # ── Aprobar usuario pendiente (admin) ──
        if path.startswith("/api/usuarios/") and path.endswith("/aprobar"):
            if not self._require_admin(user): return
            uid = int(path.split("/")[3])
            with get_conn() as conn:
                conn.execute("UPDATE usuarios SET aprobado=1 WHERE id=?", (uid,))
            log_action(user["id"], user["username"], "aprobar_usuario", "usuario", uid, ip=self._ip())
            self.send_json({"ok": True})
            return

        # ── Generar link de reset (admin) ──
        if path.startswith("/api/usuarios/") and path.endswith("/reset-link"):
            if not self._require_admin(user): return
            uid = int(path.split("/")[3])
            from auth import create_reset_token, send_reset_email
            with get_conn() as conn:
                row = conn.execute("SELECT email, username FROM usuarios WHERE id=?", (uid,)).fetchone()
            if not row:
                self.send_json({"error": "Usuario no encontrado"}, 404)
                return
            token = create_reset_token(uid)
            base_url = f"http://{self.headers.get('Host', 'localhost:8090')}"
            reset_url = f"{base_url}/reset-password?token={token}"
            email_sent = send_reset_email(dict(row)["email"], token, base_url) if dict(row)["email"] else False
            log_action(user["id"], user["username"], "reset_password_link", "usuario", uid, ip=self._ip())
            self.send_json({"ok": True, "reset_url": reset_url, "email_sent": email_sent})
            return

        # ── Crear usuario (solo admin) ──
        if path == "/api/usuarios":
            if not self._require_admin(user):
                return
            from auth import hash_password
            username = body.get("username", "").strip()
            password = body.get("password", "")
            nombre   = body.get("nombre", "").strip()
            email    = body.get("email", "").strip()
            if not username or not password:
                self.send_json({"error": "username y password son requeridos"}, 400)
                return
            if len(password) < 8:
                self.send_json({"error": "La contraseña debe tener al menos 8 caracteres."}, 400)
                return
            rol_nuevo = body.get("rol", "analista")
            if rol_nuevo not in ("admin", "analista", "auditor_externo", "auditado"):
                rol_nuevo = "analista"
            try:
                with get_conn() as conn:
                    cur = conn.execute(
                        """INSERT INTO usuarios
                           (username, password_hash, nombre, email, rol, aprobado, activo, debe_cambiar_password)
                           VALUES (?,?,?,?,?,1,1,1)""",
                        (username, hash_password(password), nombre, email, rol_nuevo),
                    )
                log_action(user["id"], user["username"], "crear_usuario",
                           "usuario", cur.lastrowid, f"username={username} rol={rol_nuevo}", self._ip())
                self.send_json({"id": cur.lastrowid})
            except Exception as e:
                self.send_json({"error": f"No se pudo crear: {e}"}, 400)

        # ── Crear evaluación ──
        elif path == "/api/evaluaciones":
            if not self._require_write(user):
                return
            fws = body.get("frameworks", ["ISO27001"])
            if not fws or not isinstance(fws, list):
                self.send_json({"error": "Seleccioná al menos un framework."}, 400); return
            # Validate all requested frameworks exist
            fws = [f for f in fws if f in FRAMEWORK_REGISTRY]
            if not fws:
                self.send_json({"error": "Ningún framework válido seleccionado."}, 400); return
            with get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO evaluaciones (nombre, empresa, alcance, frameworks) VALUES (?,?,?,?)",
                    (body.get("nombre", "Sin nombre"), body.get("empresa", ""),
                     body.get("alcance", ""), json.dumps(fws, ensure_ascii=False)),
                )
                eid = cur.lastrowid
            log_action(user["id"], user["username"], "crear_evaluacion",
                       "evaluacion", eid, body.get("nombre", ""), self._ip())
            self.send_json({"id": eid})

        # ── Guardar respuesta de control ──
        elif path.startswith("/api/evaluaciones/") and "/respuestas" in path:
            if not self._require_write(user):
                return
            eid      = int(path.split("/")[3])
            ctrl_id  = body["control_id"]
            madurez  = int(body.get("madurez", 0))
            comentario = body.get("comentario", "")
            aplica   = int(body.get("aplica", 1))
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO respuestas (evaluacion_id, control_id, madurez, comentario, aplica)
                       VALUES (?,?,?,?,?)
                       ON CONFLICT(evaluacion_id, control_id)
                       DO UPDATE SET madurez=excluded.madurez,
                                     comentario=excluded.comentario,
                                     aplica=excluded.aplica""",
                    (eid, ctrl_id, madurez, comentario, aplica),
                )
                conn.execute("UPDATE evaluaciones SET actualizada=datetime('now') WHERE id=?", (eid,))
            self.send_json({"ok": True})

        # ── Subir evidencia (base64 JSON) ──
        elif path.startswith("/api/evaluaciones/") and "/evidencias" in path and "analizar" not in path and "confirmar" not in path:
            if not self._require_evidence_upload(user):
                return
            eid       = int(path.split("/")[3])
            ctrl_id   = body.get("control_id", "")
            filename  = body.get("filename", "archivo")
            data_b64  = body.get("data", "")
            framework = body.get("framework", "ISO27001")

            # Sanitise filename — keep only safe characters
            safe_filename = re.sub(r'[^\w.\-]', '_', Path(filename).name)
            ext = Path(safe_filename).suffix.lower()
            if ext not in EXTENSIONES_VALIDAS:
                self.send_json({"error": f"Extensión no soportada: {ext}"}, 400)
                return

            # Decode & validate size
            try:
                file_bytes = base64.b64decode(data_b64)
            except Exception as e:
                self.send_json({"error": f"Datos de archivo inválidos: {e}"}, 400)
                return
            if len(file_bytes) > MAX_UPLOAD_BYTES:
                self.send_json({"error": "El archivo supera el límite de 20 MB."}, 400)
                return

            safe_name = f"{uuid.uuid4().hex}{ext}"
            filepath  = UPLOADS_DIR / safe_name
            try:
                filepath.write_bytes(file_bytes)
            except Exception as e:
                self.send_json({"error": f"No se pudo guardar: {e}"}, 500)
                return

            with get_conn() as conn:
                cur = conn.execute(
                    """INSERT INTO evidencias (evaluacion_id, control_id, framework, filename, filepath, filetype)
                       VALUES (?,?,?,?,?,?)""",
                    (eid, ctrl_id, framework, safe_filename, str(filepath), ext),
                )
                ev_id = cur.lastrowid
            log_action(user["id"], user["username"], "subir_evidencia",
                       "evidencia", ev_id, f"{ctrl_id} — {safe_filename}", self._ip())

            # ── Auto-análisis IA en background ──────────────────────────────
            import threading as _threading
            def _bg_analyze(eid=eid, ctrl_id=ctrl_id, ev_id=ev_id,
                             filepath=str(filepath), ext=ext, framework=framework):
                try:
                    with get_conn() as conn:
                        ctrl_row = conn.execute(
                            "SELECT * FROM controles_fw WHERE id=? AND framework=?",
                            (ctrl_id, framework),
                        ).fetchone()
                    if not ctrl_row:
                        return
                    ctrl_row = dict(ctrl_row)
                    resultado = analizar_evidencia(
                        filepath=filepath,
                        filetype=ext,
                        control_id=ctrl_row["id"],
                        control_nombre=ctrl_row["nombre"],
                        control_descripcion=ctrl_row.get("descripcion", ""),
                    )
                    veredicto    = resultado.get("veredicto", "pendiente")
                    analisis_str = json.dumps(resultado, ensure_ascii=False)
                    # Validate suggested maturity — must be int 0-5
                    raw_mad = resultado.get("madurez_sugerida")
                    try:
                        madurez_ia = max(0, min(5, int(raw_mad))) if raw_mad is not None else None
                    except (TypeError, ValueError):
                        madurez_ia = None
                    comentario_ia = resultado.get("resumen", "")
                    with get_conn() as conn:
                        conn.execute(
                            "UPDATE evidencias SET analisis_ia=?, veredicto=? WHERE id=?",
                            (analisis_str, veredicto, ev_id),
                        )
                        if madurez_ia is not None:
                            conn.execute(
                                """INSERT INTO respuestas
                                   (evaluacion_id, control_id, madurez, comentario, aplica,
                                    ia_madurez_sugerida, ia_comentario, ia_pendiente_confirmacion)
                                   VALUES (?,?,0,'',1,?,?,1)
                                   ON CONFLICT(evaluacion_id, control_id) DO UPDATE SET
                                       ia_madurez_sugerida=excluded.ia_madurez_sugerida,
                                       ia_comentario=excluded.ia_comentario,
                                       ia_pendiente_confirmacion=1""",
                                (eid, ctrl_id, madurez_ia, comentario_ia),
                            )
                except Exception:
                    pass
            _threading.Thread(target=_bg_analyze, daemon=True).start()
            # ────────────────────────────────────────────────────────────────

            self.send_json({"id": ev_id, "filename": safe_filename})

        # ── Confirmar / rechazar sugerencia de IA ──
        elif path.startswith("/api/evaluaciones/") and "/controles/" in path and path.endswith("/confirmar-ia"):
            # POST /api/evaluaciones/{eid}/controles/{ctrl_id}/confirmar-ia
            if not self._require_perm(user, "eval.responder"):
                return
            parts   = path.split("/")
            eid     = int(parts[3])
            ctrl_id = "/".join(parts[5:-1])  # supports IDs with dots/slashes
            confirmar = body.get("confirmar", True)
            with get_conn() as conn:
                if confirmar:
                    row = conn.execute(
                        "SELECT ia_madurez_sugerida, ia_comentario FROM respuestas "
                        "WHERE evaluacion_id=? AND control_id=?",
                        (eid, ctrl_id),
                    ).fetchone()
                    if row and row["ia_madurez_sugerida"] is not None:
                        conn.execute(
                            """UPDATE respuestas
                               SET madurez=?, comentario=?, ia_pendiente_confirmacion=0
                               WHERE evaluacion_id=? AND control_id=?""",
                            (row["ia_madurez_sugerida"], row["ia_comentario"] or "", eid, ctrl_id),
                        )
                    else:
                        conn.execute(
                            "UPDATE respuestas SET ia_pendiente_confirmacion=0 "
                            "WHERE evaluacion_id=? AND control_id=?",
                            (eid, ctrl_id),
                        )
                else:
                    conn.execute(
                        "UPDATE respuestas SET ia_pendiente_confirmacion=0 "
                        "WHERE evaluacion_id=? AND control_id=?",
                        (eid, ctrl_id),
                    )
            log_action(user["id"], user["username"],
                       "confirmar_ia" if confirmar else "rechazar_ia",
                       "respuesta", ctrl_id, f"eval={eid}", self._ip())
            self.send_json({"ok": True})

        # ── Analizar evidencia con IA ──
        elif "/evidencias/" in path and path.endswith("/analizar"):
            if not self._require_write(user):
                return
            parts = path.split("/")
            ev_id = int(parts[5])
            with get_conn() as conn:
                ev = conn.execute("SELECT * FROM evidencias WHERE id=?", (ev_id,)).fetchone()
            if not ev:
                self.send_json({"error": "evidencia no encontrada"}, 404)
                return
            ev   = dict(ev)
            ctrl = get_control(ev["control_id"])
            if not ctrl:
                self.send_json({"error": "control no encontrado"}, 404)
                return

            resultado = analizar_evidencia(
                filepath=ev["filepath"], filetype=ev["filetype"],
                control_id=ctrl["id"], control_nombre=ctrl["nombre"],
                control_descripcion=ctrl["descripcion"],
            )
            analisis_str = json.dumps(resultado, ensure_ascii=False)
            with get_conn() as conn:
                conn.execute(
                    "UPDATE evidencias SET analisis_ia=?, veredicto=? WHERE id=?",
                    (analisis_str, resultado.get("veredicto", "pendiente"), ev_id),
                )
            log_action(user["id"], user["username"], "analizar_ia",
                       "evidencia", ev_id, f"{ctrl['id']} — {resultado.get('veredicto','?')}", self._ip())
            self.send_json(resultado)

        # ── Crear hallazgo ──
        elif path.startswith("/api/evaluaciones/") and "/hallazgos" in path:
            if not self._require_write(user):
                return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                cur = conn.execute(
                    """INSERT INTO hallazgos
                       (evaluacion_id, control_id, framework, evidencia_id, tipo, severidad,
                        titulo, descripcion, responsable_nombre, responsable_email,
                        fecha_limite, plan_accion, estado)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        eid, body.get("control_id", ""), body.get("framework", "ISO27001"),
                        body.get("evidencia_id"),  body.get("tipo", "no_conformidad"),
                        body.get("severidad", "media"), body.get("titulo", ""),
                        body.get("descripcion", ""), body.get("responsable_nombre", ""),
                        body.get("responsable_email", ""), body.get("fecha_limite", ""),
                        body.get("plan_accion", ""), body.get("estado", "abierto"),
                    ),
                )
                hid = cur.lastrowid
            log_action(user["id"], user["username"], "crear_hallazgo",
                       "hallazgo", hid, body.get("titulo", ""), self._ip())
            self.send_json({"id": hid})

        # ── Riesgos — crear / actualizar ──
        elif path.startswith("/api/evaluaciones/") and "/riesgos" in path and path.count("/") == 4:
            if not self._require_write(user): return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                cur = conn.execute(
                    """INSERT INTO riesgos
                       (evaluacion_id, control_id, descripcion, probabilidad, impacto,
                        tratamiento, propietario_id, riesgo_residual, estado, notas)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (eid, body.get("control_id",""), body.get("descripcion","Sin descripción"),
                     int(body.get("probabilidad", 3)), int(body.get("impacto", 3)),
                     body.get("tratamiento","mitigar"), body.get("propietario_id"),
                     int(body.get("probabilidad",3)) * int(body.get("impacto",3)),
                     body.get("estado","abierto"), body.get("notas","")),
                )
                rid = cur.lastrowid
            log_action(user["id"], user["username"], "crear_riesgo", "riesgo", rid,
                       body.get("descripcion","")[:80], self._ip())
            self.send_json({"id": rid})

        elif path.startswith("/api/riesgos/") and path.count("/") == 3:
            if not self._require_write(user): return
            rid = int(path.split("/")[3])
            campos = ["descripcion","probabilidad","impacto","tratamiento",
                      "propietario_id","riesgo_residual","estado","notas","control_id"]
            sets = ", ".join(f"{c}=?" for c in campos if c in body)
            vals = [body[c] for c in campos if c in body]
            if sets:
                # Recalcular riesgo_residual si cambian prob/impacto
                prob = body.get("probabilidad")
                imp  = body.get("impacto")
                if prob and imp and "riesgo_residual" not in body:
                    sets += ", riesgo_residual=?"; vals.append(int(prob)*int(imp))
                vals.append(rid)
                with get_conn() as conn:
                    conn.execute(f"UPDATE riesgos SET {sets}, actualizado_en=datetime('now') WHERE id=?", vals)
            self.send_json({"ok": True})

        # ── Tareas ──
        elif path.startswith("/api/hallazgos/") and "/tareas" in path and path.count("/") == 4:
            if not self._require_write(user): return
            hid = int(path.split("/")[3])
            with get_conn() as conn:
                cur = conn.execute(
                    """INSERT INTO tareas (hallazgo_id, titulo, descripcion, asignado_a, fecha_limite, estado, progreso)
                       VALUES (?,?,?,?,?,?,?)""",
                    (hid, body.get("titulo","Tarea"), body.get("descripcion",""),
                     body.get("asignado_a"), body.get("fecha_limite",""),
                     body.get("estado","pendiente"), int(body.get("progreso",0))),
                )
                tid = cur.lastrowid
            log_action(user["id"], user["username"], "crear_tarea", "tarea", tid,
                       body.get("titulo","")[:80], self._ip())
            self.send_json({"id": tid})

        elif path.startswith("/api/tareas/") and path.count("/") == 3:
            if not self._require_write(user): return
            tid = int(path.split("/")[3])
            campos = ["titulo","descripcion","asignado_a","fecha_limite","estado","progreso"]
            sets = ", ".join(f"{c}=?" for c in campos if c in body)
            vals = [body[c] for c in campos if c in body]
            if sets:
                vals.append(tid)
                with get_conn() as conn:
                    conn.execute(f"UPDATE tareas SET {sets}, actualizado_en=datetime('now') WHERE id=?", vals)
            self.send_json({"ok": True})

        # ── Deadlines de evidencia ──
        elif path.startswith("/api/evaluaciones/") and "/deadlines" in path and path.count("/") == 4:
            if not self._require_write(user): return
            eid = int(path.split("/")[3])
            ctrl_id    = body.get("control_id","")
            asignado_a = body.get("asignado_a")
            fecha      = body.get("fecha_limite","")
            dias_rec   = int(body.get("recordatorio_dias", 3))
            if not ctrl_id or not asignado_a or not fecha:
                self.send_json({"error": "control_id, asignado_a y fecha_limite son requeridos"}, 400); return
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO deadlines_evidencia
                       (evaluacion_id, control_id, asignado_a, fecha_limite, recordatorio_dias)
                       VALUES (?,?,?,?,?)
                       ON CONFLICT(evaluacion_id, control_id, asignado_a)
                       DO UPDATE SET fecha_limite=excluded.fecha_limite,
                                     recordatorio_dias=excluded.recordatorio_dias,
                                     notificado=0""",
                    (eid, ctrl_id, asignado_a, fecha, dias_rec)
                )
                # Notificar inmediatamente si el email está configurado
                u_row = conn.execute("SELECT nombre, email FROM usuarios WHERE id=?", (asignado_a,)).fetchone()
                ev_row = conn.execute("SELECT nombre FROM evaluaciones WHERE id=?", (eid,)).fetchone()
            log_action(user["id"], user["username"], "crear_deadline", "deadline", 0,
                       f"ctrl={ctrl_id} asignado={asignado_a} fecha={fecha}", self._ip())
            self.send_json({"ok": True})

        # ── Aprobar/verificar hallazgo ──
        elif path.startswith("/api/hallazgos/") and "/aprobar" in path:
            hid    = int(path.split("/")[3])
            accion = body.get("accion", "aprobar")  # aprobar | verificar | rechazar
            if accion == "verificar" and user.get("rol") not in ("admin", "auditor_externo"):
                self.send_json({"error": "Solo auditores externos pueden verificar hallazgos."}, 403); return
            if accion in ("aprobar","rechazar") and user.get("rol") not in ("admin","analista"):
                self.send_json({"error": "Solo admin o analista pueden aprobar/rechazar."}, 403); return
            mapa = {"aprobar": "resuelto", "verificar": "verificado", "rechazar": "abierto"}
            nuevo_estado = mapa.get(accion, "resuelto")
            with get_conn() as conn:
                if accion == "verificar":
                    conn.execute(
                        "UPDATE hallazgos SET estado=?, verificado_por=?, fecha_aprobacion=datetime('now') WHERE id=?",
                        (nuevo_estado, user["id"], hid)
                    )
                else:
                    conn.execute(
                        "UPDATE hallazgos SET estado=?, aprobado_por=?, fecha_aprobacion=datetime('now') WHERE id=?",
                        (nuevo_estado, user["id"], hid)
                    )
            log_action(user["id"], user["username"], f"hallazgo_{accion}", "hallazgo", hid,
                       body.get("comentario",""), self._ip())
            self.send_json({"ok": True, "estado": nuevo_estado})

        # ── Guardar excepción de control (no aplica + justificación) ──
        elif path.startswith("/api/evaluaciones/") and "/excepcion" in path:
            if not self._require_write(user): return
            eid = int(path.split("/")[3])
            ctrl_id   = body.get("control_id","")
            justif    = body.get("justificacion","")
            aprobada  = int(body.get("aprobada", 0))
            hasta     = body.get("excepcion_hasta","")
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO respuestas (evaluacion_id, control_id, aplica, excepcion_justificacion,
                       excepcion_aprobada, excepcion_hasta)
                       VALUES (?,?,0,?,?,?)
                       ON CONFLICT(evaluacion_id, control_id)
                       DO UPDATE SET aplica=0, excepcion_justificacion=excluded.excepcion_justificacion,
                                     excepcion_aprobada=excluded.excepcion_aprobada,
                                     excepcion_hasta=excluded.excepcion_hasta""",
                    (eid, ctrl_id, justif, aprobada, hasta)
                )
            log_action(user["id"], user["username"], "excepcion_control", "control", ctrl_id,
                       f"eval={eid} justif={justif[:50]}", self._ip())
            self.send_json({"ok": True})

        # ── Registrar snapshot de madurez ──
        elif path.startswith("/api/evaluaciones/") and "/snapshot-madurez" in path:
            if not self._require_write(user): return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                resps = conn.execute(
                    "SELECT control_id, madurez FROM respuestas WHERE evaluacion_id=? AND madurez > 0",
                    (eid,)
                ).fetchall()
                for r in resps:
                    conn.execute(
                        "INSERT INTO historial_madurez (evaluacion_id, control_id, madurez) VALUES (?,?,?)",
                        (eid, r["control_id"], r["madurez"])
                    )
            self.send_json({"ok": True, "snapshots": len(resps)})

        # ── Config sistema (admin) ──
        elif path == "/api/admin/config":
            if not self._require_admin(user): return
            for clave, valor in body.items():
                if clave.startswith("smtp_") or clave in ("base_url","app_name"):
                    with get_conn() as conn:
                        conn.execute(
                            "INSERT OR REPLACE INTO config_sistema (clave, valor) VALUES (?,?)",
                            (clave, str(valor))
                        )
                    # También actualiza variables de entorno en memoria
                    env_key = f"GRC_{clave.upper()}"
                    os.environ[env_key] = str(valor)
            self.send_json({"ok": True})

        # ── Forzar envío de recordatorios ──
        elif path == "/api/admin/reminders/send":
            if not self._require_admin(user): return
            from reminders import check_and_send_reminders
            base_url = f"http://{self.headers.get('Host', 'localhost:8090')}"
            result = check_and_send_reminders(base_url)
            self.send_json(result)

        # ── Test de conexión SMTP ──
        elif path == "/api/admin/config/test-smtp":
            if not self._require_admin(user): return
            from reminders import send_email, smtp_configured
            if not smtp_configured():
                self.send_json({"error": "SMTP no configurado. Guardá primero el host SMTP."}, 400)
                return
            # Determine destination: body.to, user email, or smtp_user
            to_addr = (body.get("to") or "").strip()
            if not to_addr:
                with get_conn() as conn:
                    row = conn.execute(
                        "SELECT email FROM usuarios WHERE id=?", (user["id"],)
                    ).fetchone()
                    to_addr = (row["email"] if row else "") or os.environ.get("GRC_SMTP_USER", "")
            if not to_addr:
                self.send_json({"error": "No hay dirección destino. Configurá tu email de usuario o smtp_user."}, 400)
                return
            ok = send_email(
                to=to_addr,
                subject="[NormaLab GRC] Prueba de conexión SMTP ✓",
                html="<div style='font-family:system-ui,sans-serif;padding:24px'>"
                     "<h2 style='color:#4f46e5'>NormaLab GRC</h2>"
                     "<p>¡La configuración SMTP funciona correctamente!</p>"
                     "<p style='color:#888;font-size:12px'>Este es un email de prueba generado desde el panel de configuración.</p>"
                     "</div>",
                plain="NormaLab GRC — La configuración SMTP funciona correctamente.",
            )
            if ok:
                self.send_json({"ok": True, "to": to_addr})
            else:
                self.send_json({"error": "Error al enviar. Verificá host, puerto, usuario y contraseña SMTP."}, 500)

        # ── Roles: crear ──────────────────────────────────────────────────────
        elif path == "/api/admin/roles":
            if not self._require_admin(user): return
            nombre = body.get("nombre", "").strip()
            if not nombre:
                self.send_json({"error": "El nombre del rol es requerido."}, 400); return
            with get_conn() as conn:
                if conn.execute("SELECT 1 FROM roles WHERE nombre=?", (nombre,)).fetchone():
                    self.send_json({"error": "Ya existe un rol con ese nombre."}, 409); return
                cur = conn.execute(
                    "INSERT INTO roles (nombre, descripcion, color, es_sistema) VALUES (?,?,?,0)",
                    (nombre, body.get("descripcion",""), body.get("color","#6366f1")),
                )
                rid = cur.lastrowid
                permisos = body.get("permisos", [])
                for pid in permisos:
                    conn.execute("INSERT OR IGNORE INTO rol_permisos (rol_id, permiso_id) VALUES (?,?)", (rid, pid))
            from auth import log_action
            log_action(user["id"], user["username"], "crear_rol", "roles", rid, nombre, self._ip())
            self.send_json({"ok": True, "id": rid})

        # ── Admin: crear control en framework ──────────────────────────────────
        elif path.startswith("/api/admin/frameworks/") and path.endswith("/controles"):
            if not self._require_admin(user): return
            fw_id = path.split("/")[4].upper()
            if fw_id not in FRAMEWORK_REGISTRY:
                self.send_json({"error": "Framework no encontrado"}, 404); return
            ctrl_id  = body.get("id", "").strip()
            nombre   = body.get("nombre", "").strip()
            if not ctrl_id or not nombre:
                self.send_json({"error": "ID y nombre son requeridos."}, 400); return
            with get_conn() as conn:
                existing = conn.execute(
                    "SELECT 1 FROM controles_fw WHERE id=? AND framework=?", (ctrl_id, fw_id)
                ).fetchone()
                if existing:
                    self.send_json({"error": "Ya existe un control con ese ID en este framework."}, 409); return
                max_orden = conn.execute(
                    "SELECT COALESCE(MAX(orden),0) FROM controles_fw WHERE framework=?", (fw_id,)
                ).fetchone()[0]
                conn.execute(
                    """INSERT INTO controles_fw (id, framework, nombre, descripcion, dominio, categoria, orden, activo, es_custom)
                       VALUES (?,?,?,?,?,?,?,1,1)""",
                    (ctrl_id, fw_id, nombre,
                     body.get("descripcion", ""), body.get("dominio", ""),
                     body.get("categoria", body.get("dominio", "")),
                     max_orden + 1),
                )
            from auth import log_action
            log_action(user["id"], user["username"], "crear_control", "controles_fw",
                       f"{fw_id}:{ctrl_id}", nombre, self._ip())
            self.send_json({"ok": True, "id": ctrl_id})

        else:
            self.send_response(404)
            self.end_headers()

    # ── PUT ───────────────────────────────────────────────────────────────────

    def do_PUT(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = json.loads(self.rfile.read(length)) if length else {}
        path   = urlparse(self.path).path

        user = self._require_auth()
        if not user:
            return

        if "/hallazgos/" in path:
            if not self._require_write(user):
                return
            hid    = int(path.split("/")[-1])
            campos = ["tipo", "severidad", "titulo", "descripcion",
                      "responsable_nombre", "responsable_email",
                      "fecha_limite", "plan_accion", "estado"]
            sets = ", ".join(f"{c}=?" for c in campos if c in body)
            vals = [body[c] for c in campos if c in body]
            if sets:
                vals.append(hid)
                with get_conn() as conn:
                    conn.execute(
                        f"UPDATE hallazgos SET {sets}, actualizado_en=datetime('now') WHERE id=?", vals
                    )
                if "estado" in body:
                    from auth import log_action
                    log_action(user["id"], user["username"], "cambiar_estado_hallazgo",
                               "hallazgo", hid, f"nuevo estado: {body['estado']}", self._ip())
            self.send_json({"ok": True})

        elif "/usuarios/" in path and path.endswith("/password"):
            # Cambiar contraseña: admin puede cambiar cualquiera, el usuario puede cambiar la suya
            uid = int(path.split("/")[3])
            if user["id"] != uid and not self._require_admin(user):
                return
            from auth import hash_password
            new_pw = body.get("password", "")
            if len(new_pw) < 8:
                self.send_json({"error": "La contraseña debe tener al menos 8 caracteres."}, 400)
                return
            with get_conn() as conn:
                conn.execute("UPDATE usuarios SET password_hash=? WHERE id=?",
                             (hash_password(new_pw), uid))
            self.send_json({"ok": True})

        elif "/usuarios/" in path:
            uid = int(path.split("/")[-1])
            if not self._require_admin(user):
                return
            campos = ["nombre", "email", "rol", "activo"]
            # Validar rol si viene en el body
            if "rol" in body and body["rol"] not in ("admin", "analista", "auditor_externo", "auditado"):
                self.send_json({"error": "Rol inválido."}, 400)
                return
            sets   = ", ".join(f"{c}=?" for c in campos if c in body)
            vals   = [body[c] for c in campos if c in body]
            if sets:
                vals.append(uid)
                with get_conn() as conn:
                    conn.execute(f"UPDATE usuarios SET {sets} WHERE id=?", vals)
            # Cambiar contraseña si se incluye en el body
            if "password" in body and body["password"]:
                new_pw = body["password"]
                if len(new_pw) < 8:
                    self.send_json({"error": "La contraseña debe tener al menos 8 caracteres."}, 400)
                    return
                from auth import hash_password
                with get_conn() as conn:
                    conn.execute(
                        "UPDATE usuarios SET password_hash=?, debe_cambiar_password=0 WHERE id=?",
                        (hash_password(new_pw), uid),
                    )
            self.send_json({"ok": True})

        # ── Roles: actualizar (nombre/desc/color) o asignar permisos ─────────
        elif path.startswith("/api/admin/roles/"):
            if not self._require_admin(user): return
            parts = path.split("/")
            rid = int(parts[4])
            with get_conn() as conn:
                rol = conn.execute("SELECT * FROM roles WHERE id=?", (rid,)).fetchone()
                if not rol: self.send_json({"error": "Rol no encontrado"}, 404); return
                if len(parts) == 6 and parts[5] == "permisos":
                    nuevos = body.get("permisos", [])
                    conn.execute("DELETE FROM rol_permisos WHERE rol_id=?", (rid,))
                    for pid in nuevos:
                        conn.execute("INSERT OR IGNORE INTO rol_permisos (rol_id, permiso_id) VALUES (?,?)", (rid, pid))
                else:
                    if rol["es_sistema"] and "nombre" in body:
                        self.send_json({"error": "No se puede cambiar el nombre de roles del sistema."}, 400); return
                    for campo in ["nombre", "descripcion", "color"]:
                        if campo in body:
                            conn.execute(f"UPDATE roles SET {campo}=? WHERE id=?", (body[campo], rid))
            self.send_json({"ok": True})

        # ── Admin: actualizar control de framework ─────────────────────────────
        elif path.startswith("/api/admin/frameworks/") and "/controles/" in path:
            if not self._require_admin(user): return
            parts  = path.split("/")
            fw_id  = parts[4].upper()
            ctrl_id = "/".join(parts[6:])  # support IDs with slashes (e.g. NIST)
            if not ctrl_id:
                self.send_json({"error": "ID de control requerido."}, 400); return
            allowed = ["nombre", "descripcion", "dominio", "categoria", "activo", "orden"]
            sets  = ", ".join(f"{k}=?" for k in allowed if k in body)
            vals  = [body[k] for k in allowed if k in body]
            if sets:
                vals += [fw_id, ctrl_id]
                with get_conn() as conn:
                    conn.execute(
                        f"UPDATE controles_fw SET {sets}, actualizado_en=datetime('now') "
                        "WHERE framework=? AND id=?", vals
                    )
            from auth import log_action
            log_action(user["id"], user["username"], "editar_control", "controles_fw",
                       f"{fw_id}:{ctrl_id}", "", self._ip())
            self.send_json({"ok": True})

        else:
            self.send_response(404)
            self.end_headers()

    # ── DELETE ────────────────────────────────────────────────────────────────

    def do_DELETE(self):
        path = urlparse(self.path).path

        user = self._require_auth()
        if not user:
            return

        from auth import log_action

        if "/hallazgos/" in path:
            if not self._require_admin(user):
                return
            hid = int(path.split("/")[-1])
            with get_conn() as conn:
                conn.execute("DELETE FROM hallazgos WHERE id=?", (hid,))
            log_action(user["id"], user["username"], "eliminar_hallazgo",
                       "hallazgo", hid, ip=self._ip())
            self.send_json({"ok": True})

        elif "/evidencias/" in path:
            if not self._require_admin(user):
                return
            ev_id = int(path.split("/")[-1])
            with get_conn() as conn:
                ev = conn.execute("SELECT filepath FROM evidencias WHERE id=?", (ev_id,)).fetchone()
                if ev:
                    try:
                        Path(ev["filepath"]).unlink(missing_ok=True)
                    except Exception:
                        pass
                conn.execute("DELETE FROM evidencias WHERE id=?", (ev_id,))
            self.send_json({"ok": True})

        elif path.startswith("/api/evaluaciones/"):
            if not self._require_admin(user):
                return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                ev = conn.execute("SELECT nombre FROM evaluaciones WHERE id=?", (eid,)).fetchone()
                nombre = ev["nombre"] if ev else str(eid)
                conn.execute("DELETE FROM evaluaciones WHERE id=?", (eid,))
            log_action(user["id"], user["username"], "eliminar_evaluacion",
                       "evaluacion", eid, nombre, self._ip())
            self.send_json({"ok": True})

        elif "/asignados/" in path:
            # DELETE /api/evaluaciones/:eid/asignados/:uid
            if not self._require_admin(user): return
            parts = path.split("/")
            eid = int(parts[3])
            uid = int(parts[5])
            with get_conn() as conn:
                conn.execute(
                    "DELETE FROM evaluacion_usuarios WHERE evaluacion_id=? AND usuario_id=?",
                    (eid, uid),
                )
            self.send_json({"ok": True})

        elif "/riesgos/" in path:
            if not self._require_write(user): return
            rid = int(path.split("/")[-1])
            with get_conn() as conn:
                conn.execute("DELETE FROM riesgos WHERE id=?", (rid,))
            log_action(user["id"], user["username"], "eliminar_riesgo", "riesgo", rid, ip=self._ip())
            self.send_json({"ok": True})

        elif "/tareas/" in path:
            if not self._require_write(user): return
            tid = int(path.split("/")[-1])
            with get_conn() as conn:
                conn.execute("DELETE FROM tareas WHERE id=?", (tid,))
            self.send_json({"ok": True})

        elif "/deadlines/" in path:
            if not self._require_write(user): return
            did = int(path.split("/")[-1])
            with get_conn() as conn:
                conn.execute("DELETE FROM deadlines_evidencia WHERE id=?", (did,))
            self.send_json({"ok": True})

        elif "/usuarios/" in path:
            uid = int(path.split("/")[-1])
            if not self._require_admin(user):
                return
            if uid == user["id"]:
                self.send_json({"error": "No podés eliminar tu propia cuenta."}, 400)
                return
            with get_conn() as conn:
                conn.execute("DELETE FROM usuarios WHERE id=?", (uid,))
            self.send_json({"ok": True})

        # ── Roles: eliminar ────────────────────────────────────────────────────
        elif path.startswith("/api/admin/roles/"):
            if not self._require_admin(user): return
            rid = int(path.split("/")[4])
            with get_conn() as conn:
                rol = conn.execute("SELECT * FROM roles WHERE id=?", (rid,)).fetchone()
                if not rol: self.send_json({"error": "Rol no encontrado"}, 404); return
                if rol["es_sistema"]:
                    self.send_json({"error": "No se pueden eliminar roles del sistema."}, 400); return
                n_usuarios = conn.execute(
                    "SELECT COUNT(*) FROM usuarios WHERE rol=?",
                    (_rol_key_from_nombre(rol["nombre"]),)
                ).fetchone()[0]
                if n_usuarios > 0:
                    self.send_json({"error": f"El rol tiene {n_usuarios} usuario(s) asignado(s). Reasignalos antes de eliminar."}, 400); return
                conn.execute("DELETE FROM roles WHERE id=?", (rid,))
            from auth import log_action
            log_action(user["id"], user["username"], "eliminar_rol", "roles", rid, rol["nombre"], self._ip())
            self.send_json({"ok": True})

        # ── Admin: eliminar control de framework ───────────────────────────────
        elif path.startswith("/api/admin/frameworks/") and "/controles/" in path:
            if not self._require_admin(user): return
            parts   = path.split("/")
            fw_id   = parts[4].upper()
            ctrl_id = "/".join(parts[6:])
            qs_del  = parse_qs(urlparse(self.path).query)
            hard    = qs_del.get("hard", ["0"])[0] == "1"
            with get_conn() as conn:
                row = conn.execute(
                    "SELECT es_custom FROM controles_fw WHERE framework=? AND id=?", (fw_id, ctrl_id)
                ).fetchone()
                if not row:
                    self.send_json({"error": "Control no encontrado."}, 404); return
                if hard and row["es_custom"]:
                    conn.execute("DELETE FROM controles_fw WHERE framework=? AND id=?", (fw_id, ctrl_id))
                else:
                    # Soft-delete (toggle activo)
                    new_activo = 0 if row else 1
                    conn.execute(
                        "UPDATE controles_fw SET activo=?, actualizado_en=datetime('now') WHERE framework=? AND id=?",
                        (new_activo, fw_id, ctrl_id),
                    )
            from auth import log_action
            log_action(user["id"], user["username"], "eliminar_control", "controles_fw",
                       f"{fw_id}:{ctrl_id}", "", self._ip())
            self.send_json({"ok": True})

        else:
            self.send_response(404)
            self.end_headers()


class ThreadingServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    init_db()
    seed_roles_y_permisos()
    seed_controles_db()
    from auth import init_default_users
    init_default_users()
    from reminders import start_reminder_thread
    base_url = os.environ.get("GRC_BASE_URL", "http://localhost:8090")
    start_reminder_thread(base_url=base_url, interval_seconds=3600)
    port = 8090
    print(f"GRC Tool — http://localhost:{port}")
    print(f"Usuario por defecto: admin / Admin1234!")
    ThreadingServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
