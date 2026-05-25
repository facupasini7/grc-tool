"""
GRC Tool — servidor principal
"""
import json
import os
import base64
import socketserver
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from database import get_conn, init_db
from data.controles_iso27001 import CONTROLES, DOMINIOS
from data.controles_bcra import CONTROLES_BCRA, DOMINIOS_BCRA, DOMINIOS_A7777, DOMINIOS_A7783
from data.controles_pci import CONTROLES_PCI, DOMINIOS_PCI
from report import generar_pdf
from ai_analyzer import analizar_evidencia

CONTROLES_A7777 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7777"]
CONTROLES_A7783 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7783"]

BASE_DIR    = Path(__file__).parent.parent
STATIC_DIR  = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

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
                self.send_json({"error": "No autenticado", "redirect": "/login"}, 401)
            else:
                self.send_response(302)
                self.send_header("Location", "/login")
                self.end_headers()
            return None
        return user

    def _require_admin(self, user):
        if user.get("rol") != "admin":
            self.send_json({"error": "Se requiere rol Administrador."}, 403)
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

        # ── Rutas siempre públicas ──
        if path == "/login":
            self.send_file(STATIC_DIR / "login.html", "text/html; charset=utf-8")
            return
        if path == "/register":
            self.send_file(STATIC_DIR / "register.html", "text/html; charset=utf-8")
            return
        if path == "/forgot-password":
            self.send_file(STATIC_DIR / "forgot-password.html", "text/html; charset=utf-8")
            return
        if path == "/reset-password":
            self.send_file(STATIC_DIR / "reset-password.html", "text/html; charset=utf-8")
            return
        if path == "/change-password":
            self.send_file(STATIC_DIR / "change-password.html", "text/html; charset=utf-8")
            return
        if path.startswith("/static/"):
            rel   = path[len("/static/"):]
            ext   = Path(rel).suffix
            tipos = {".css": "text/css", ".js": "application/javascript", ".svg": "image/svg+xml"}
            self.send_file(STATIC_DIR / rel, tipos.get(ext, "application/octet-stream"))
            return

        # ── Requiere autenticación ──
        user = self._require_auth()
        if not user:
            return

        if path in ("/", "/index.html"):
            self.send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")

        elif path == "/api/me":
            self.send_json({
                "id": user["id"], "username": user["username"],
                "nombre": user["nombre"], "rol": user["rol"],
                "debe_cambiar_password": user.get("debe_cambiar_password", 0),
            })

        elif path == "/api/audit-log":
            if not self._require_audit_access(user):
                return
            limit  = int(qs.get("limit",  ["200"])[0])
            offset = int(qs.get("offset", ["0"])[0])
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
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

        elif path.startswith("/api/evaluaciones/") and "/stats" in path:
            if self._block_auditado(user): return
            eid = int(path.split("/")[3])
            self.send_json(calcular_stats(eid))

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
            self.send_json(CONTROLES)

        elif path == "/api/dominios":
            self.send_json(DOMINIOS)

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
            if self._block_auditado(user): return
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                ev = conn.execute("SELECT * FROM evaluaciones WHERE id=?", (eid,)).fetchone()
            if not ev:
                self.send_json({"error": "no encontrada"}, 404)
                return
            stats    = calcular_stats(eid)
            pdf_path = generar_pdf(dict(ev), stats, CONTROLES)
            data     = pdf_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="gap-analysis-{eid}.pdf"')
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)

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
            if not username or not password:
                self.send_json({"error": "username y password son requeridos"}, 400)
                return
            rol_nuevo = body.get("rol", "analista")
            if rol_nuevo not in ("admin", "analista", "auditor_externo", "auditado"):
                rol_nuevo = "analista"
            try:
                with get_conn() as conn:
                    cur = conn.execute(
                        "INSERT INTO usuarios (username, password_hash, nombre, rol) VALUES (?,?,?,?)",
                        (username, hash_password(password), body.get("nombre", ""), rol_nuevo),
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
            if not fws:
                fws = ["ISO27001"]
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

        # ── Subir evidencia (base64) ──
        elif path.startswith("/api/evaluaciones/") and "/evidencias" in path and "analizar" not in path:
            if not self._require_evidence_upload(user):
                return
            eid      = int(path.split("/")[3])
            ctrl_id  = body.get("control_id", "")
            filename = body.get("filename", "archivo")
            data_b64 = body.get("data", "")
            framework = body.get("framework", "ISO27001")

            ext = Path(filename).suffix.lower()
            if ext not in EXTENSIONES_VALIDAS:
                self.send_json({"error": f"Extensión no soportada: {ext}"}, 400)
                return

            safe_name = f"{uuid.uuid4().hex}{ext}"
            filepath  = UPLOADS_DIR / safe_name
            try:
                filepath.write_bytes(base64.b64decode(data_b64))
            except Exception as e:
                self.send_json({"error": f"No se pudo guardar: {e}"}, 500)
                return

            with get_conn() as conn:
                cur = conn.execute(
                    """INSERT INTO evidencias (evaluacion_id, control_id, framework, filename, filepath, filetype)
                       VALUES (?,?,?,?,?,?)""",
                    (eid, ctrl_id, framework, filename, str(filepath), ext),
                )
                ev_id = cur.lastrowid
            log_action(user["id"], user["username"], "subir_evidencia",
                       "evidencia", ev_id, f"{ctrl_id} — {filename}", self._ip())
            self.send_json({"id": ev_id, "filename": filename})

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
            campos = ["nombre", "rol", "activo"]
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

        else:
            self.send_response(404)
            self.end_headers()


class ThreadingServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    init_db()
    from auth import init_default_users
    init_default_users()
    port = 8090
    print(f"GRC Tool — http://localhost:{port}")
    print(f"Usuario por defecto: admin / Admin1234!")
    ThreadingServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
