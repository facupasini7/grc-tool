"""
Tests de la capa de base de datos.

ANÁLISIS DE RIESGO:
  - Migración duplicada: llamar init_db() dos veces no debe crashear
  - Columna frameworks: DB vieja sin la columna → debe migrarse
  - FK CASCADE: borrar evaluación elimina respuestas/evidencias/hallazgos
  - Unique constraint en respuestas (evaluacion_id, control_id): upsert correcto
"""
import json
import sqlite3
import pytest


class TestInitDB:

    def test_init_idempotente(self, tmp_db):
        """Llamar init_db() dos veces no debe lanzar errores."""
        from database import init_db
        init_db()  # segunda llamada
        init_db()  # tercera

    def test_crea_tablas_evaluaciones(self, conn):
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        names = {r[0] for r in tables}
        assert "evaluaciones" in names
        assert "respuestas" in names
        assert "evidencias" in names
        assert "hallazgos" in names

    def test_columna_frameworks_existe(self, conn):
        cols = conn.execute("PRAGMA table_info(evaluaciones)").fetchall()
        col_names = {c[1] for c in cols}
        assert "frameworks" in col_names, (
            "La columna 'frameworks' no existe — migración fallida"
        )

    def test_migracion_db_sin_frameworks(self, tmp_path, monkeypatch):
        """
        Simula una DB antigua creada SIN la columna frameworks.
        init_db() debe agregarla sin crashear.
        """
        import database as db_module
        db_file = tmp_path / "old.db"
        monkeypatch.setattr(db_module, "DB_PATH", db_file)

        # Crear DB vieja manualmente sin la columna frameworks
        conn = sqlite3.connect(db_file)
        conn.execute("""
            CREATE TABLE evaluaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                empresa TEXT NOT NULL,
                alcance TEXT,
                creada_en TEXT DEFAULT (datetime('now')),
                actualizada TEXT DEFAULT (datetime('now')),
                completada INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()

        # init_db() debe hacer la migración
        db_module.init_db()

        # Verificar que la columna fue agregada
        with db_module.get_conn() as c:
            cols = c.execute("PRAGMA table_info(evaluaciones)").fetchall()
            col_names = {r[1] for r in cols}
        assert "frameworks" in col_names


class TestConstraints:

    def test_upsert_respuesta_actualiza_madurez(self, conn, eval_basico):
        """INSERT OR REPLACE debe actualizar la madurez del control existente."""
        conn.execute(
            "INSERT INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
            "VALUES (?,?,?,1)", (eval_basico, "A.5.1", 2)
        )
        conn.execute(
            "INSERT OR REPLACE INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
            "VALUES (?,?,?,1)", (eval_basico, "A.5.1", 4)
        )
        row = conn.execute(
            "SELECT madurez FROM respuestas WHERE evaluacion_id=? AND control_id=?",
            (eval_basico, "A.5.1")
        ).fetchone()
        assert row[0] == 4

    def test_no_duplicados_respuesta(self, conn, eval_basico):
        """No pueden existir dos respuestas para el mismo (evaluacion_id, control_id)."""
        conn.execute(
            "INSERT INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
            "VALUES (?,?,?,1)", (eval_basico, "A.5.1", 2)
        )
        with pytest.raises(sqlite3.IntegrityError):
            # INSERT sin OR REPLACE debe violar el UNIQUE
            conn.execute(
                "INSERT INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
                "VALUES (?,?,?,1)", (eval_basico, "A.5.1", 3)
            )

    def test_fk_cascade_borra_respuestas(self, conn, eval_basico):
        """Al borrar una evaluación, sus respuestas deben eliminarse en cascada."""
        conn.execute(
            "INSERT INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
            "VALUES (?,?,?,1)", (eval_basico, "A.5.1", 3)
        )
        conn.execute("DELETE FROM evaluaciones WHERE id=?", (eval_basico,))
        rows = conn.execute(
            "SELECT * FROM respuestas WHERE evaluacion_id=?", (eval_basico,)
        ).fetchall()
        assert rows == [], "Respuestas huérfanas después de borrar la evaluación"

    def test_fk_cascade_borra_hallazgos(self, conn, eval_basico):
        conn.execute(
            "INSERT INTO hallazgos (evaluacion_id, control_id, titulo, descripcion) "
            "VALUES (?,?,?,?)", (eval_basico, "A.5.1", "Hallazgo test", "Desc")
        )
        conn.execute("DELETE FROM evaluaciones WHERE id=?", (eval_basico,))
        rows = conn.execute(
            "SELECT * FROM hallazgos WHERE evaluacion_id=?", (eval_basico,)
        ).fetchall()
        assert rows == []

    def test_frameworks_default_es_iso27001(self, conn):
        """Si se inserta sin especificar frameworks, el default debe ser ["ISO27001"]."""
        conn.execute(
            "INSERT INTO evaluaciones (nombre, empresa) VALUES (?,?)",
            ("Sin fw", "Corp")
        )
        row = conn.execute(
            "SELECT frameworks FROM evaluaciones WHERE nombre='Sin fw'"
        ).fetchone()
        stored = json.loads(row[0])
        assert stored == ["ISO27001"]
