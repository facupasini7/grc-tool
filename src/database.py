import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "evaluaciones.db"
DB_PATH.parent.mkdir(exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                username              TEXT NOT NULL UNIQUE,
                password_hash         TEXT NOT NULL,
                nombre                TEXT DEFAULT '',
                email                 TEXT DEFAULT '',
                rol                   TEXT DEFAULT 'auditor',
                activo                INTEGER DEFAULT 1,
                aprobado              INTEGER DEFAULT 1,
                debe_cambiar_password INTEGER DEFAULT 0,
                creado_en             TEXT DEFAULT (datetime('now')),
                ultimo_login          TEXT
            );

            CREATE TABLE IF NOT EXISTS password_resets (
                token      TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                expira_en  TEXT NOT NULL,
                usado      INTEGER DEFAULT 0,
                creado_en  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS evaluacion_usuarios (
                evaluacion_id INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
                usuario_id    INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                PRIMARY KEY (evaluacion_id, usuario_id)
            );

            CREATE TABLE IF NOT EXISTS sesiones (
                token      TEXT PRIMARY KEY,
                usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                expira_en  TEXT NOT NULL,
                creada_en  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS audit_log (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp      TEXT DEFAULT (datetime('now')),
                usuario_id     INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
                usuario_nombre TEXT DEFAULT '',
                accion         TEXT NOT NULL,
                entidad        TEXT DEFAULT '',
                entidad_id     TEXT DEFAULT '',
                detalle        TEXT DEFAULT '',
                ip             TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS evaluaciones (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT NOT NULL,
                empresa     TEXT NOT NULL,
                alcance     TEXT,
                frameworks  TEXT DEFAULT '["ISO27001"]',
                creada_en   TEXT DEFAULT (datetime('now')),
                actualizada TEXT DEFAULT (datetime('now')),
                completada  INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS respuestas (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluacion_id   INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
                control_id      TEXT NOT NULL,
                madurez         INTEGER DEFAULT 0,
                comentario      TEXT DEFAULT '',
                aplica          INTEGER DEFAULT 1,
                UNIQUE(evaluacion_id, control_id)
            );

            CREATE TABLE IF NOT EXISTS evidencias (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluacion_id   INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
                control_id      TEXT NOT NULL,
                framework       TEXT DEFAULT 'ISO27001',
                filename        TEXT NOT NULL,
                filepath        TEXT NOT NULL,
                filetype        TEXT NOT NULL,
                texto_extraido  TEXT,
                analisis_ia     TEXT,
                veredicto       TEXT DEFAULT 'pendiente',
                subida_en       TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS hallazgos (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluacion_id       INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
                control_id          TEXT NOT NULL,
                framework           TEXT DEFAULT 'ISO27001',
                evidencia_id        INTEGER REFERENCES evidencias(id) ON DELETE SET NULL,
                tipo                TEXT NOT NULL DEFAULT 'no_conformidad',
                severidad           TEXT NOT NULL DEFAULT 'media',
                titulo              TEXT NOT NULL,
                descripcion         TEXT NOT NULL,
                responsable_nombre  TEXT DEFAULT '',
                responsable_email   TEXT DEFAULT '',
                fecha_limite        TEXT DEFAULT '',
                plan_accion         TEXT DEFAULT '',
                estado              TEXT DEFAULT 'abierto',
                creado_en           TEXT DEFAULT (datetime('now')),
                actualizado_en      TEXT DEFAULT (datetime('now'))
            );
        """)
    # Migraciones para DBs existentes (se ignoran si la columna ya existe)
    _migrate()


def _check_is_default_password(stored: str) -> bool:
    """Verifica si el hash corresponde a 'Admin1234!' sin importar auth (evita circular)."""
    import hashlib
    try:
        parts = stored.split(":")
        if len(parts) != 5 or parts[0] != "pbkdf2":
            return False
        _, alg, iters, salt, stored_hex = parts
        dk = hashlib.pbkdf2_hmac(alg, b"Admin1234!", salt.encode(), int(iters))
        return dk.hex() == stored_hex
    except Exception:
        return False


def _migrate():
    migrations = [
        "ALTER TABLE evaluaciones ADD COLUMN frameworks TEXT DEFAULT '[\"ISO27001\"]'",
        "ALTER TABLE usuarios ADD COLUMN email TEXT DEFAULT ''",
        "ALTER TABLE usuarios ADD COLUMN aprobado INTEGER DEFAULT 1",
        "ALTER TABLE usuarios ADD COLUMN debe_cambiar_password INTEGER DEFAULT 0",
    ]
    with get_conn() as conn:
        for sql in migrations:
            try:
                conn.execute(sql)
            except Exception:
                pass  # columna ya existe

        # Si el admin aún tiene la contraseña por defecto y no tiene el flag,
        # activarlo para que se le pida el cambio en el próximo login.
        row = conn.execute(
            "SELECT password_hash FROM usuarios WHERE username = 'admin' AND debe_cambiar_password = 0"
        ).fetchone()
        if row and _check_is_default_password(row["password_hash"]):
            conn.execute(
                "UPDATE usuarios SET debe_cambiar_password = 1 WHERE username = 'admin'"
            )
