"""
Módulo de autenticación para la GRC Tool.
Provee: hash de contraseñas (PBKDF2), sesiones, audit log y setup inicial.
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta

from database import get_conn

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
            """SELECT u.id, u.username, u.nombre, u.rol
               FROM sesiones s JOIN usuarios u ON s.usuario_id = u.id
               WHERE s.token = ?
                 AND s.expira_en > datetime('now')
                 AND u.activo = 1""",
            (token,),
        ).fetchone()
    return dict(row) if row else None


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


# ── Setup inicial ─────────────────────────────────────────────────────────────

def init_default_users() -> None:
    """Crea el usuario admin por defecto si no existe ningún usuario."""
    with get_conn() as conn:
        exists = conn.execute("SELECT id FROM usuarios LIMIT 1").fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO usuarios (username, password_hash, nombre, rol) VALUES (?,?,?,?)",
                ("admin", hash_password("Admin1234!"), "Administrador", "admin"),
            )
