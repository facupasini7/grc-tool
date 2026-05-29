"""
Módulo de autenticación para la GRC Tool.
Provee: hash de contraseñas (PBKDF2), sesiones, audit log, reset tokens y setup inicial.
"""
import hashlib
import hmac
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from database import get_conn

# ── Política de seguridad (config_sistema) ─────────────────────────────────────

# Valores por defecto. Solo se persisten en config_sistema las claves que el admin
# modifica; el resto se completa con estos defaults.
SEG_DEFAULTS = {
    "seg_pwd_min_len":      8,   # longitud mínima de contraseña
    "seg_pwd_mayus":        1,   # exigir al menos una mayúscula
    "seg_pwd_minus":        0,   # exigir al menos una minúscula
    "seg_pwd_numero":       1,   # exigir al menos un dígito
    "seg_pwd_simbolo":      0,   # exigir al menos un símbolo
    "seg_max_intentos":     5,   # intentos fallidos antes de bloquear (0 = sin bloqueo)
    "seg_bloqueo_min":      15,  # minutos de bloqueo de cuenta
    "seg_inactividad_min":  0,   # cierre de sesión por inactividad en minutos (0 = desactivado)
    "seg_pwd_expira_dias":  0,   # vencimiento de contraseña en días (0 = nunca)
}

_SEG_KEYS = set(SEG_DEFAULTS)


def get_seg_config(conn=None) -> dict:
    """Devuelve la política de seguridad efectiva (defaults + overrides en DB)."""
    cfg = dict(SEG_DEFAULTS)
    own = conn is None
    if own:
        conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT clave, valor FROM config_sistema WHERE clave LIKE 'seg_%'"
        ).fetchall()
        for r in rows:
            if r["clave"] in _SEG_KEYS:
                try:
                    cfg[r["clave"]] = int(r["valor"])
                except (TypeError, ValueError):
                    pass
    except Exception:
        pass
    finally:
        if own:
            conn.close()
    return cfg


def save_seg_config(valores: dict) -> dict:
    """Persiste solo las claves válidas de política de seguridad. Retorna la config efectiva."""
    with get_conn() as conn:
        for clave, valor in (valores or {}).items():
            if clave in _SEG_KEYS:
                try:
                    v = int(valor)
                except (TypeError, ValueError):
                    continue
                conn.execute(
                    "INSERT OR REPLACE INTO config_sistema (clave, valor) VALUES (?,?)",
                    (clave, str(v)),
                )
    return get_seg_config()


def validate_password_policy(password: str, conn=None) -> str | None:
    """Valida la contraseña contra la política activa.
    Retorna None si es válida, o un mensaje de error en español."""
    cfg = get_seg_config(conn)
    pw = password or ""
    if len(pw) < cfg["seg_pwd_min_len"]:
        return f"La contraseña debe tener al menos {cfg['seg_pwd_min_len']} caracteres."
    if cfg["seg_pwd_mayus"] and not any(c.isupper() for c in pw):
        return "La contraseña debe incluir al menos una letra mayúscula."
    if cfg["seg_pwd_minus"] and not any(c.islower() for c in pw):
        return "La contraseña debe incluir al menos una letra minúscula."
    if cfg["seg_pwd_numero"] and not any(c.isdigit() for c in pw):
        return "La contraseña debe incluir al menos un número."
    if cfg["seg_pwd_simbolo"] and not any(not c.isalnum() for c in pw):
        return "La contraseña debe incluir al menos un símbolo."
    return None


# ── Bloqueo de cuenta por intentos fallidos ────────────────────────────────────

def account_locked_until(conn, username: str) -> str | None:
    """Si la cuenta está bloqueada, retorna la marca de tiempo de desbloqueo; si no, None."""
    row = conn.execute(
        "SELECT bloqueado_hasta FROM usuarios "
        "WHERE username=? AND bloqueado_hasta IS NOT NULL "
        "AND bloqueado_hasta > datetime('now')",
        (username,),
    ).fetchone()
    return row["bloqueado_hasta"] if row else None


def register_failed_login(conn, username: str) -> None:
    """Incrementa el contador de intentos fallidos y bloquea la cuenta si supera el límite."""
    cfg = get_seg_config(conn)
    max_intentos = cfg["seg_max_intentos"]
    if max_intentos <= 0:
        return
    row = conn.execute(
        "SELECT id, intentos_fallidos FROM usuarios WHERE username=?", (username,)
    ).fetchone()
    if not row:
        return
    intentos = (row["intentos_fallidos"] or 0) + 1
    if intentos >= max_intentos:
        # Calcular el desbloqueo en UTC vía SQLite para que coincida con
        # la comparación contra datetime('now') de account_locked_until.
        bloqueo = conn.execute(
            "SELECT datetime('now', ?) AS t", (f"+{int(cfg['seg_bloqueo_min'])} minutes",)
        ).fetchone()["t"]
        conn.execute(
            "UPDATE usuarios SET intentos_fallidos=?, bloqueado_hasta=? WHERE id=?",
            (intentos, bloqueo, row["id"]),
        )
    else:
        conn.execute(
            "UPDATE usuarios SET intentos_fallidos=? WHERE id=?", (intentos, row["id"])
        )


def reset_failed_login(conn, usuario_id: int) -> None:
    conn.execute(
        "UPDATE usuarios SET intentos_fallidos=0, bloqueado_hasta=NULL WHERE id=?",
        (usuario_id,),
    )


# ── Contraseñas ───────────────────────────────────────────────────────────────

_ALG   = "sha256"
_ITERS = 260_000


def hash_password(password: str) -> str:
    """Deriva la contraseña con PBKDF2-HMAC-SHA256 + sal aleatoria de 16 bytes."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(_ALG, password.encode(), salt.encode(), _ITERS)
    return f"pbkdf2:{_ALG}:{_ITERS}:{salt}:{dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Comparación timing-safe. Retorna False ante cualquier error de formato."""
    try:
        _, alg, iters, salt, stored_dk = stored.split(":", 4)
        dk = hashlib.pbkdf2_hmac(alg, password.encode(), salt.encode(), int(iters))
        return hmac.compare_digest(dk.hex(), stored_dk)
    except Exception:
        return False


# ── Sesiones ──────────────────────────────────────────────────────────────────

_SESSION_HOURS = 8


def create_session(usuario_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expira = (datetime.now() + timedelta(hours=_SESSION_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sesiones (token, usuario_id, expira_en) VALUES (?,?,?)",
            (token, usuario_id, expira),
        )
    return token


def get_user_from_token(token: str) -> dict | None:
    if not token:
        return None
    with get_conn() as conn:
        row = conn.execute(
            """SELECT u.id, u.username, u.nombre, u.rol, u.debe_cambiar_password,
                      s.ultima_actividad, s.creada_en
               FROM sesiones s JOIN usuarios u ON s.usuario_id = u.id
               WHERE s.token = ?
                 AND s.expira_en > datetime('now')
                 AND u.activo = 1
                 AND u.aprobado = 1""",
            (token,),
        ).fetchone()
        if not row:
            return None
        user = dict(row)

        # Cierre de sesión por inactividad
        inactividad_min = get_seg_config(conn)["seg_inactividad_min"]
        if inactividad_min > 0:
            ultima = user.get("ultima_actividad") or user.get("creada_en")
            expirada = conn.execute(
                "SELECT ? < datetime('now', ?) AS venc",
                (ultima, f"-{int(inactividad_min)} minutes"),
            ).fetchone()
            if ultima and expirada and expirada["venc"]:
                conn.execute("DELETE FROM sesiones WHERE token=?", (token,))
                return None

        # Registrar actividad (renueva la ventana de inactividad)
        conn.execute(
            "UPDATE sesiones SET ultima_actividad=datetime('now') WHERE token=?", (token,)
        )

        # Cargar permisos del rol (via tabla roles si existe, o sistema por defecto)
        user["permisos"] = _load_permisos(conn, user["rol"])
        user.pop("ultima_actividad", None)
        user.pop("creada_en", None)
    return user


def _load_permisos(conn, rol_nombre: str) -> list:
    """Retorna la lista de permiso IDs para el rol dado."""
    try:
        rows = conn.execute(
            """SELECT rp.permiso_id FROM rol_permisos rp
               JOIN roles r ON rp.rol_id = r.id
               WHERE r.nombre = ?""",
            (_rol_nombre_sistema(rol_nombre),),
        ).fetchall()
        return [r["permiso_id"] for r in rows]
    except Exception:
        return []


def _rol_nombre_sistema(rol_key: str) -> str:
    """Mapea el key interno del rol al nombre en la tabla roles."""
    mapping = {
        "admin": "Administrador",
        "analista": "Analista GRC",
        "auditor_externo": "Auditor Externo",
        "auditado": "Auditado",
    }
    return mapping.get(rol_key, rol_key)


def delete_session(token: str) -> None:
    if token:
        with get_conn() as conn:
            conn.execute("DELETE FROM sesiones WHERE token = ?", (token,))


def parse_session_token(cookie_header: str) -> str:
    """Extrae el valor de grc_session de la cabecera Cookie."""
    for part in (cookie_header or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k.strip() == "grc_session":
            return v.strip()
    return ""


# ── Audit log ─────────────────────────────────────────────────────────────────

def log_action(
    usuario_id,
    usuario_nombre: str,
    accion: str,
    entidad: str = "",
    entidad_id: str = "",
    detalle: str = "",
    ip: str = "",
) -> None:
    """Registra una acción en el audit log. Nunca lanza excepciones."""
    try:
        with get_conn() as conn:
            conn.execute(
                """INSERT INTO audit_log
                   (usuario_id, usuario_nombre, accion, entidad, entidad_id, detalle, ip)
                   VALUES (?,?,?,?,?,?,?)""",
                (usuario_id, usuario_nombre, accion, entidad, str(entidad_id), detalle, ip),
            )
    except Exception:
        pass  # el log nunca debe interrumpir la operación principal


# ── Reset de contraseña ───────────────────────────────────────────────────────

_RESET_HOURS = 2


def create_reset_token(usuario_id: int) -> str:
    """Genera un token de reset válido por 2 h (invalida tokens anteriores)."""
    token = secrets.token_urlsafe(32)
    expira = (datetime.now() + timedelta(hours=_RESET_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute("UPDATE password_resets SET usado=1 WHERE usuario_id=?", (usuario_id,))
        conn.execute(
            "INSERT INTO password_resets (token, usuario_id, expira_en) VALUES (?,?,?)",
            (token, usuario_id, expira),
        )
    return token


def validate_reset_token(token: str) -> int | None:
    """Retorna usuario_id si el token es válido y no fue usado, o None."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT usuario_id FROM password_resets "
            "WHERE token=? AND usado=0 AND expira_en > datetime('now')",
            (token,),
        ).fetchone()
    return row["usuario_id"] if row else None


def consume_reset_token(token: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE password_resets SET usado=1 WHERE token=?", (token,))


def send_reset_email(email: str, token: str, base_url: str) -> bool:
    """
    Envía email de recuperación. Retorna True si se envió.
    Requiere variables de entorno:
      GRC_SMTP_HOST, GRC_SMTP_PORT (def 587), GRC_SMTP_USER, GRC_SMTP_PASS, GRC_SMTP_FROM
    Si no están configuradas, retorna False (el admin debe enviar el link manualmente).
    """
    host = os.environ.get("GRC_SMTP_HOST", "")
    if not host:
        return False
    port     = int(os.environ.get("GRC_SMTP_PORT", "587"))
    user     = os.environ.get("GRC_SMTP_USER", "")
    password = os.environ.get("GRC_SMTP_PASS", "")
    from_addr = os.environ.get("GRC_SMTP_FROM", user)
    reset_url = f"{base_url}/reset-password?token={token}"

    body = (
        f"Hola,\n\n"
        f"Recibimos una solicitud para restablecer tu contraseña en GRC Tool.\n\n"
        f"Hacé clic en el siguiente enlace (válido por {_RESET_HOURS} horas):\n"
        f"{reset_url}\n\n"
        f"Si no solicitaste este cambio, ignorá este correo.\n"
    )
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "GRC Tool — Recuperación de contraseña"
    msg["From"]    = from_addr
    msg["To"]      = email
    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            if user:
                smtp.login(user, password)
            smtp.sendmail(from_addr, [email], msg.as_string())
        return True
    except Exception:
        return False


# ── Setup inicial ─────────────────────────────────────────────────────────────

def init_default_users() -> None:
    """Crea el usuario admin por defecto si no existe ningún usuario.
    El admin debe cambiar la contraseña en el primer login."""
    with get_conn() as conn:
        exists = conn.execute("SELECT id FROM usuarios LIMIT 1").fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO usuarios "
                "(username, password_hash, nombre, rol, debe_cambiar_password) "
                "VALUES (?,?,?,?,?)",
                ("admin", hash_password("Admin1234!"), "Administrador", "admin", 1),
            )
