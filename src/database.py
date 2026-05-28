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
        # v2 — riesgos, SoA, deadlines, tareas, historial
        "ALTER TABLE hallazgos ADD COLUMN aprobado_por INTEGER REFERENCES usuarios(id)",
        "ALTER TABLE hallazgos ADD COLUMN fecha_aprobacion TEXT",
        "ALTER TABLE hallazgos ADD COLUMN verificado_por INTEGER REFERENCES usuarios(id)",
        "ALTER TABLE respuestas ADD COLUMN excepcion_justificacion TEXT DEFAULT ''",
        "ALTER TABLE respuestas ADD COLUMN excepcion_aprobada INTEGER DEFAULT 0",
        "ALTER TABLE respuestas ADD COLUMN excepcion_hasta TEXT DEFAULT ''",
        # v3 — IA suggestions per control
        "ALTER TABLE respuestas ADD COLUMN ia_madurez_sugerida INTEGER",
        "ALTER TABLE respuestas ADD COLUMN ia_comentario TEXT DEFAULT ''",
        "ALTER TABLE respuestas ADD COLUMN ia_pendiente_confirmacion INTEGER DEFAULT 0",
        # v4 — verificación formal del analista GRC
        "ALTER TABLE respuestas ADD COLUMN verificado INTEGER DEFAULT 0",
        "ALTER TABLE respuestas ADD COLUMN verificado_por INTEGER REFERENCES usuarios(id) ON DELETE SET NULL",
        "ALTER TABLE respuestas ADD COLUMN verificado_en TEXT",
        # v5 — responsable formal del hallazgo (relación con usuarios)
        "ALTER TABLE hallazgos ADD COLUMN responsable_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL",
    ]
    new_tables = """
        CREATE TABLE IF NOT EXISTS riesgos (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluacion_id   INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
            control_id      TEXT DEFAULT '',
            descripcion     TEXT NOT NULL,
            probabilidad    INTEGER DEFAULT 3,
            impacto         INTEGER DEFAULT 3,
            tratamiento     TEXT DEFAULT 'mitigar',
            propietario_id  INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            riesgo_residual INTEGER DEFAULT 9,
            estado          TEXT DEFAULT 'abierto',
            notas           TEXT DEFAULT '',
            creado_en       TEXT DEFAULT (datetime('now')),
            actualizado_en  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tareas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            hallazgo_id   INTEGER NOT NULL REFERENCES hallazgos(id) ON DELETE CASCADE,
            titulo        TEXT NOT NULL,
            descripcion   TEXT DEFAULT '',
            asignado_a    INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            fecha_limite  TEXT DEFAULT '',
            estado        TEXT DEFAULT 'pendiente',
            progreso      INTEGER DEFAULT 0,
            creado_en     TEXT DEFAULT (datetime('now')),
            actualizado_en TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS deadlines_evidencia (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluacion_id     INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
            control_id        TEXT NOT NULL,
            asignado_a        INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            fecha_limite      TEXT NOT NULL,
            recordatorio_dias INTEGER DEFAULT 3,
            notificado        INTEGER DEFAULT 0,
            creado_en         TEXT DEFAULT (datetime('now')),
            UNIQUE(evaluacion_id, control_id, asignado_a)
        );

        CREATE TABLE IF NOT EXISTS historial_madurez (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluacion_id INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
            control_id    TEXT NOT NULL,
            madurez       REAL DEFAULT 0,
            registrado_en TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS config_sistema (
            clave TEXT PRIMARY KEY,
            valor TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS controles_fw (
            id             TEXT NOT NULL,
            framework      TEXT NOT NULL,
            nombre         TEXT NOT NULL,
            descripcion    TEXT DEFAULT '',
            dominio        TEXT DEFAULT '',
            categoria      TEXT DEFAULT '',
            orden          INTEGER DEFAULT 0,
            activo         INTEGER DEFAULT 1,
            es_custom      INTEGER DEFAULT 0,
            creado_en      TEXT DEFAULT (datetime('now')),
            actualizado_en TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (id, framework)
        );

        CREATE TABLE IF NOT EXISTS comentarios (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            evaluacion_id   INTEGER NOT NULL REFERENCES evaluaciones(id) ON DELETE CASCADE,
            control_id      TEXT NOT NULL,
            usuario_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            usuario_nombre  TEXT NOT NULL DEFAULT 'Usuario',
            usuario_rol     TEXT DEFAULT '',
            texto           TEXT NOT NULL,
            creado_en       TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS hallazgo_comentarios (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            hallazgo_id     INTEGER NOT NULL REFERENCES hallazgos(id) ON DELETE CASCADE,
            usuario_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            usuario_nombre  TEXT NOT NULL DEFAULT 'Usuario',
            usuario_rol     TEXT DEFAULT '',
            texto           TEXT NOT NULL,
            creado_en       TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS hallazgo_evidencias (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            hallazgo_id     INTEGER NOT NULL REFERENCES hallazgos(id) ON DELETE CASCADE,
            usuario_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            usuario_nombre  TEXT NOT NULL DEFAULT 'Usuario',
            usuario_rol     TEXT DEFAULT '',
            filename        TEXT NOT NULL,
            filepath        TEXT NOT NULL,
            filetype        TEXT DEFAULT '',
            subida_en       TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS roles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL UNIQUE,
            descripcion TEXT DEFAULT '',
            color       TEXT DEFAULT '#6366f1',
            es_sistema  INTEGER DEFAULT 0,
            creado_en   TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS permisos (
            id          TEXT PRIMARY KEY,
            label       TEXT NOT NULL,
            descripcion TEXT DEFAULT '',
            categoria   TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS rol_permisos (
            rol_id     INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            permiso_id TEXT    NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
            PRIMARY KEY (rol_id, permiso_id)
        );
    """
    with get_conn() as conn:
        for sql in migrations:
            try:
                conn.execute(sql)
            except Exception:
                pass  # columna ya existe
        conn.executescript(new_tables)

        # Si el admin aún tiene la contraseña por defecto y no tiene el flag,
        # activarlo para que se le pida el cambio en el próximo login.
        row = conn.execute(
            "SELECT password_hash FROM usuarios WHERE username = 'admin' AND debe_cambiar_password = 0"
        ).fetchone()
        if row and _check_is_default_password(row["password_hash"]):
            conn.execute(
                "UPDATE usuarios SET debe_cambiar_password = 1 WHERE username = 'admin'"
            )


# ── Catálogo de permisos y roles sistema ──────────────────────────────────────

PERMISOS_CATALOGO = [
    # Evaluaciones
    ("eval.ver",            "Ver evaluaciones",              "Ver y acceder a evaluaciones existentes",                     "Evaluaciones"),
    ("eval.crear",          "Crear evaluaciones",            "Crear nuevas evaluaciones y configurar frameworks",           "Evaluaciones"),
    ("eval.responder",      "Completar controles",           "Responder y actualizar el nivel de madurez de controles",     "Evaluaciones"),
    ("eval.eliminar",       "Eliminar evaluaciones",         "Eliminar evaluaciones y todos sus datos asociados",           "Evaluaciones"),
    # Hallazgos
    ("hallazgos.ver",                "Ver hallazgos",                    "Consultar el registro de hallazgos y no conformidades",                    "Hallazgos"),
    ("hallazgos.gestionar",          "Gestionar hallazgos",              "Crear, editar y cambiar estado de hallazgos",                              "Hallazgos"),
    ("hallazgos.aprobar",            "Aprobar hallazgos",                "Aprobar y verificar resolución de hallazgos",                              "Hallazgos"),
    ("hallazgos.crear_incumplimiento","Crear hallazgo por incumplimiento","Abrir hallazgos cuando evidencia está vencida o rechazada por la IA",     "Hallazgos"),
    # Riesgos
    ("riesgos.ver",         "Ver riesgos",                   "Consultar el registro de riesgos del SGSI",                   "Riesgos"),
    ("riesgos.gestionar",   "Gestionar riesgos",             "Crear, editar y actualizar tratamiento de riesgos",           "Riesgos"),
    # Remediación
    ("remediacion.ver",     "Ver remediación",               "Consultar el plan de remediación y tareas asociadas",         "Remediación"),
    ("remediacion.gestionar","Gestionar remediación",        "Crear y actualizar tareas del plan de remediación",           "Remediación"),
    # Evidencias
    ("evidencias.ver",      "Ver evidencias",                "Consultar evidencias subidas a los controles",                "Evidencias"),
    ("evidencias.subir",    "Subir evidencias",              "Cargar archivos de evidencia para los controles",             "Evidencias"),
    # Reportes
    ("reportes.generar",    "Generar reportes",              "Exportar informes ejecutivos y detallados en PDF",            "Reportes"),
    # Administración
    ("usuarios.ver",        "Ver usuarios",                  "Consultar la lista de usuarios de la plataforma",             "Administración"),
    ("usuarios.gestionar",  "Gestionar usuarios",            "Crear, editar y eliminar cuentas de usuario",                 "Administración"),
    ("roles.gestionar",     "Gestionar roles y permisos",    "Crear roles custom y asignar permisos granulares",            "Administración"),
    ("auditoria.ver",       "Ver auditoría",                 "Acceder al log de auditoría inmutable",                       "Administración"),
    # Configuración
    ("config.sistema",      "Configurar sistema",            "Modificar parámetros generales y SMTP",                       "Configuración"),
    ("config.seguridad",    "Configurar seguridad",          "Gestionar parámetros de seguridad de la plataforma",          "Configuración"),
    ("frameworks.gestionar","Gestionar frameworks",          "Editar, agregar y desactivar controles de cada framework",    "Configuración"),
]

# Permisos por rol sistema
PERMISOS_POR_ROL = {
    "admin": [p[0] for p in PERMISOS_CATALOGO],  # todos
    "analista": [
        "eval.ver", "eval.crear", "eval.responder",
        "hallazgos.ver", "hallazgos.gestionar", "hallazgos.crear_incumplimiento",
        "riesgos.ver", "riesgos.gestionar",
        "remediacion.ver", "remediacion.gestionar",
        "evidencias.ver", "evidencias.subir",
        "reportes.generar",
        "usuarios.ver",
    ],
    "auditor_externo": [
        "eval.ver",
        "hallazgos.ver",
        "riesgos.ver",
        "remediacion.ver",
        "evidencias.ver",
        "auditoria.ver",
        "reportes.generar",
    ],
    "auditado": [
        "eval.ver", "eval.responder",
        "evidencias.subir", "evidencias.ver",
    ],
}

ROLES_SISTEMA = [
    ("admin",           "Administrador",     "Acceso total al sistema",                                      "#ef4444"),
    ("analista",        "Analista GRC",      "Gestión completa de evaluaciones, hallazgos y riesgos",        "#3b82f6"),
    ("auditor_externo", "Auditor Externo",   "Acceso de solo lectura para revisión independiente",           "#8b5cf6"),
    ("auditado",        "Auditado",          "Carga de evidencias y respuesta a controles asignados",        "#10b981"),
]


def seed_roles_y_permisos():
    """Inserta el catálogo de permisos y los roles sistema si no existen."""
    with get_conn() as conn:
        # Permisos
        for pid, label, desc, cat in PERMISOS_CATALOGO:
            conn.execute(
                "INSERT OR IGNORE INTO permisos (id, label, descripcion, categoria) VALUES (?,?,?,?)",
                (pid, label, desc, cat),
            )
        # Roles sistema
        for rol_key, nombre, desc, color in ROLES_SISTEMA:
            conn.execute(
                "INSERT OR IGNORE INTO roles (nombre, descripcion, color, es_sistema) VALUES (?,?,?,1)",
                (nombre, desc, color),
            )
            rol_row = conn.execute("SELECT id FROM roles WHERE nombre=?", (nombre,)).fetchone()
            if rol_row:
                rid = rol_row["id"]
                for pid in PERMISOS_POR_ROL.get(rol_key, []):
                    conn.execute(
                        "INSERT OR IGNORE INTO rol_permisos (rol_id, permiso_id) VALUES (?,?)",
                        (rid, pid),
                    )
