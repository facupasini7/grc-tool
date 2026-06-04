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
        # v7 — política de contraseñas y bloqueo de cuenta
        "ALTER TABLE usuarios ADD COLUMN intentos_fallidos INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN bloqueado_hasta TEXT",
        "ALTER TABLE usuarios ADD COLUMN password_cambiada_en TEXT",
        "ALTER TABLE sesiones ADD COLUMN ultima_actividad TEXT",
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

        -- ── TPRM: gestión de riesgos de terceros ──
        CREATE TABLE IF NOT EXISTS proveedores (
            id                    INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre                TEXT NOT NULL,
            tipo_servicio         TEXT DEFAULT '',
            criticidad            TEXT DEFAULT 'media',         -- baja/media/alta/critica
            datos_maneja          TEXT DEFAULT '',              -- tipos de datos que procesa
            contacto_nombre       TEXT DEFAULT '',
            contacto_email        TEXT DEFAULT '',
            estado                TEXT DEFAULT 'en_evaluacion', -- activo/en_evaluacion/inactivo
            riesgo_inherente      TEXT DEFAULT '',              -- bajo/medio/alto/critico
            riesgo_inherente_just TEXT DEFAULT '',              -- justificación (IA o manual)
            notas                 TEXT DEFAULT '',
            creado_en             TEXT DEFAULT (datetime('now')),
            actualizado_en        TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tprm_preguntas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT DEFAULT '',
            texto     TEXT NOT NULL,
            peso      INTEGER DEFAULT 1,
            orden     INTEGER DEFAULT 0,
            activa    INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS tprm_respuestas (
            proveedor_id   INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
            pregunta_id    INTEGER NOT NULL REFERENCES tprm_preguntas(id) ON DELETE CASCADE,
            respuesta      TEXT DEFAULT 'na',   -- cumple/parcial/no_cumple/na
            comentario     TEXT DEFAULT '',
            actualizado_en TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (proveedor_id, pregunta_id)
        );

        -- Evidencias adjuntas por pregunta del cuestionario de un proveedor.
        CREATE TABLE IF NOT EXISTS tprm_respuesta_evidencias (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id    INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
            pregunta_id     INTEGER NOT NULL REFERENCES tprm_preguntas(id) ON DELETE CASCADE,
            usuario_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            usuario_nombre  TEXT NOT NULL DEFAULT 'Usuario',
            filename        TEXT NOT NULL,
            filepath        TEXT NOT NULL,
            filetype        TEXT DEFAULT '',
            subida_en       TEXT DEFAULT (datetime('now'))
        );

        -- Hilo de comentarios/actividad por proveedor (incluye análisis de IA).
        CREATE TABLE IF NOT EXISTS proveedor_comentarios (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id    INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE CASCADE,
            usuario_id      INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
            usuario_nombre  TEXT NOT NULL DEFAULT 'Usuario',
            usuario_rol     TEXT DEFAULT '',     -- rol del autor; 'ia' para análisis del asistente
            texto           TEXT NOT NULL,
            creado_en       TEXT DEFAULT (datetime('now'))
        );
    """
    with get_conn() as conn:
        for sql in migrations:
            try:
                conn.execute(sql)
            except Exception:
                pass  # columna ya existe
        conn.executescript(new_tables)

        # v6 — Migración de datos: estados de hallazgo del modelo viejo
        # (abierto/en_proceso/resuelto/verificado) al nuevo modelo de 5 estados.
        # Idempotente: si no quedan estados viejos, no hace nada.
        _ESTADO_LEGADO = {
            "abierto":    "pendiente",
            "en_proceso": "implementado",
            "resuelto":   "normalizado",
            "verificado": "normalizado",
        }
        for viejo, nuevo in _ESTADO_LEGADO.items():
            try:
                conn.execute(
                    "UPDATE hallazgos SET estado=? WHERE estado=?", (nuevo, viejo)
                )
            except Exception:
                pass

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
    # Terceros (TPRM)
    ("tprm.ver",            "Ver terceros",                  "Consultar proveedores y sus evaluaciones de riesgo",          "Terceros"),
    ("tprm.gestionar",      "Gestionar terceros",            "Crear/editar proveedores, responder cuestionarios y evaluar", "Terceros"),
    ("tprm.responder",      "Responder cuestionario (proveedor)", "Contestar el cuestionario de seguridad, subir evidencias y comentar", "Terceros"),
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
        "tprm.ver", "tprm.gestionar",
        "remediacion.ver", "remediacion.gestionar",
        "evidencias.ver", "evidencias.subir",
        "reportes.generar",
        "usuarios.ver",
    ],
    "auditor_externo": [
        "eval.ver",
        "hallazgos.ver",
        "riesgos.ver",
        "tprm.ver",
        "remediacion.ver",
        "evidencias.ver",
        "auditoria.ver",
        "reportes.generar",
    ],
    "auditado": [
        "eval.ver", "eval.responder",
        "evidencias.subir", "evidencias.ver",
    ],
    # SegInf IDM (Gestión de identidades): administra toda la sección de Seguridad.
    "seginf_idm": [
        "usuarios.ver", "usuarios.gestionar",
        "roles.gestionar",
        "auditoria.ver",
        "config.seguridad",
    ],
    # Proveedor (tercero externo): solo responde su cuestionario de seguridad.
    "proveedor": [
        "tprm.ver", "tprm.responder",
    ],
}

ROLES_SISTEMA = [
    ("admin",           "Administrador",     "Acceso total al sistema",                                      "#ef4444"),
    ("analista",        "Analista GRC",      "Gestión completa de evaluaciones, hallazgos y riesgos",        "#3b82f6"),
    ("auditor_externo", "Auditor Externo",   "Acceso de solo lectura para revisión independiente",           "#8b5cf6"),
    ("auditado",        "Auditado",          "Carga de evidencias y respuesta a controles asignados",        "#10b981"),
    ("seginf_idm",      "SegInf IDM",        "Gestión de identidades: administra usuarios, roles y seguridad","#0ea5e9"),
    ("proveedor",       "Proveedor",         "Tercero externo: responde el cuestionario de seguridad",       "#f97316"),
]


# ── Cuestionario TPRM por defecto ──────────────────────────────────────────────
# (categoría, texto, peso). Se siembra solo si la tabla está vacía.
TPRM_PREGUNTAS = [
    ("Gobierno y cumplimiento", "¿El proveedor cuenta con certificaciones de seguridad vigentes (ISO 27001, SOC 2, etc.)?", 3),
    ("Gobierno y cumplimiento", "¿Existe un contrato/acuerdo con cláusulas de seguridad y confidencialidad (NDA)?", 2),
    ("Gobierno y cumplimiento", "¿El proveedor cumple con la normativa de protección de datos aplicable?", 3),
    ("Seguridad de la información", "¿El proveedor tiene una política de seguridad de la información documentada?", 2),
    ("Seguridad de la información", "¿Realiza evaluaciones periódicas de vulnerabilidades y/o pentests?", 2),
    ("Seguridad de la información", "¿Cifra los datos sensibles en tránsito y en reposo?", 3),
    ("Gestión de accesos", "¿Aplica control de accesos basado en roles y MFA para sus sistemas?", 2),
    ("Gestión de accesos", "¿Revoca accesos de forma oportuna ante bajas de personal?", 1),
    ("Protección de datos", "¿Existe segregación de los datos de la organización respecto de otros clientes?", 2),
    ("Protección de datos", "¿El proveedor notifica incidentes de seguridad en un plazo definido?", 3),
    ("Continuidad", "¿Cuenta con plan de continuidad del negocio y recuperación ante desastres?", 2),
    ("Continuidad", "¿Mantiene copias de respaldo probadas periódicamente?", 1),
    ("Subcontratación", "¿Gestiona y comunica el uso de subcontratistas (cuarta parte)?", 1),
]


def seed_tprm_preguntas(conn):
    """Siembra el cuestionario de evaluación de terceros si la tabla está vacía."""
    existe = conn.execute("SELECT id FROM tprm_preguntas LIMIT 1").fetchone()
    if existe:
        return
    for orden, (cat, texto, peso) in enumerate(TPRM_PREGUNTAS):
        conn.execute(
            "INSERT INTO tprm_preguntas (categoria, texto, peso, orden) VALUES (?,?,?,?)",
            (cat, texto, peso, orden),
        )


def seed_roles_y_permisos():
    """Inserta el catálogo de permisos y los roles sistema si no existen."""
    with get_conn() as conn:
        seed_tprm_preguntas(conn)
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
