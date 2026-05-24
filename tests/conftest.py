"""
Fixtures compartidas para toda la suite de tests.
Usa una DB SQLite en memoria para aislar cada test.
"""
import json
import sqlite3
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# ── Asegurar que src/ está en el path ───────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))


# ── DB en memoria ────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """Base de datos SQLite temporal, aislada por test."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("database.DB_PATH", db_file)
    from database import init_db
    init_db()
    return db_file


@pytest.fixture
def conn(tmp_db):
    """Conexión directa a la DB temporal.

    isolation_level = None → modo autocommit: cada statement se commitea
    inmediatamente y es visible para otras conexiones (ej. calcular_cobertura
    abre su propia conexión). Sin esto, los INSERTs quedan en una transacción
    implícita abierta hasta que el fixture cierra, y las funciones bajo prueba
    leen una DB vacía.
    """
    from database import get_conn
    c = get_conn()
    c.isolation_level = None   # autocommit
    yield c
    c.close()


# ── Evaluación de prueba ─────────────────────────────────────────────────────

@pytest.fixture
def eval_basico(conn):
    """Inserta una evaluación mínima y retorna su id."""
    cur = conn.execute(
        "INSERT INTO evaluaciones (nombre, empresa, alcance, frameworks) "
        "VALUES (?,?,?,?)",
        ("Eval Test", "ACME", "cloud", json.dumps(["ISO27001", "A7777"])),
    )
    return cur.lastrowid


@pytest.fixture
def eval_con_respuestas(conn, eval_basico):
    """Evaluación con respuestas precargadas para todos los dominios ISO."""
    from data.controles_iso27001 import CONTROLES
    for ctrl in CONTROLES[:10]:   # primeros 10 controles con madurez variada
        madurez = (CONTROLES.index(ctrl) % 5) + 1
        conn.execute(
            "INSERT INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
            "VALUES (?,?,?,1)",
            (eval_basico, ctrl["id"], madurez),
        )
    # Un control marcado como no aplica
    if CONTROLES:
        conn.execute(
            "INSERT OR REPLACE INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
            "VALUES (?,?,0,0)",
            (eval_basico, CONTROLES[-1]["id"]),
        )
    return eval_basico
