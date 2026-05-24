"""
Tests unitarios para calcular_stats().

ANÁLISIS DE RIESGO:
  - División por cero cuando aplica=0 en todos los controles
  - Madurez global ignorando controles con aplica=0
  - progreso_pct cuando total=0
  - Brechas: solo controles con madurez < 3 (no los no respondidos con madurez=0?)
"""
import pytest


def insertar(conn, eval_id, ctrl_id, madurez, aplica=1, comentario=""):
    conn.execute(
        "INSERT OR REPLACE INTO respuestas "
        "(evaluacion_id, control_id, madurez, aplica, comentario) VALUES (?,?,?,?,?)",
        (eval_id, ctrl_id, madurez, aplica, comentario),
    )


class TestStatsEvaluacionVacia:

    def test_progreso_pct_es_cero(self, tmp_db, eval_basico):
        from app import calcular_stats
        stats = calcular_stats(eval_basico)
        assert stats["progreso_pct"] == 0.0

    def test_madurez_global_es_cero(self, tmp_db, eval_basico):
        from app import calcular_stats
        stats = calcular_stats(eval_basico)
        assert stats["madurez_global"] == 0

    def test_no_crash_con_cero_aplicables(self, tmp_db, conn, eval_basico):
        """Si todos los controles tienen aplica=0, no debe dividir por cero."""
        from data.controles_iso27001 import CONTROLES
        from app import calcular_stats
        for ctrl in CONTROLES:
            insertar(conn, eval_basico, ctrl["id"], 0, aplica=0)
        stats = calcular_stats(eval_basico)
        assert stats["progreso_pct"] == 0
        assert stats["madurez_global"] == 0


class TestStatsConRespuestas:

    def test_madurez_global_excluye_no_aplica(self, tmp_db, conn, eval_basico):
        """Controles con aplica=0 no deben influir en la madurez global."""
        from data.controles_iso27001 import CONTROLES
        from app import calcular_stats

        # 1 control con madurez=4, aplica=1
        insertar(conn, eval_basico, CONTROLES[0]["id"], 4, aplica=1)
        # 1 control con madurez=1, aplica=0 → no debe contar
        insertar(conn, eval_basico, CONTROLES[1]["id"], 1, aplica=0)

        stats = calcular_stats(eval_basico)
        assert stats["madurez_global"] == 4.0

    def test_respondidos_cuenta_correctamente(self, tmp_db, conn, eval_basico):
        from data.controles_iso27001 import CONTROLES
        from app import calcular_stats

        controles_a_responder = CONTROLES[:5]
        for ctrl in controles_a_responder:
            insertar(conn, eval_basico, ctrl["id"], 3)

        stats = calcular_stats(eval_basico)
        assert stats["respondidos"] == 5

    def test_brechas_incluyen_madurez_baja(self, tmp_db, conn, eval_basico):
        """Controles con madurez < 3 deben aparecer en brechas del dominio."""
        from data.controles_iso27001 import CONTROLES, DOMINIOS
        from app import calcular_stats

        primer_dominio = list(DOMINIOS.keys())[0]
        ctrl_dominio = [c for c in CONTROLES if c["dominio"] == primer_dominio][0]
        insertar(conn, eval_basico, ctrl_dominio["id"], 1)

        stats = calcular_stats(eval_basico)
        brechas = stats["dominios"][primer_dominio]["brechas"]
        ids_brechas = [b["id"] for b in brechas]
        assert ctrl_dominio["id"] in ids_brechas

    def test_progreso_pct_calculo_correcto(self, tmp_db, conn, eval_basico):
        from data.controles_iso27001 import CONTROLES
        from app import calcular_stats

        total = len(CONTROLES)
        respondidos = 10
        for ctrl in CONTROLES[:respondidos]:
            insertar(conn, eval_basico, ctrl["id"], 3)

        stats = calcular_stats(eval_basico)
        expected_pct = round(respondidos / total * 100, 1)
        assert stats["progreso_pct"] == expected_pct


class TestStatsDominios:

    def test_todos_los_dominios_presentes(self, tmp_db, eval_basico):
        from data.controles_iso27001 import DOMINIOS
        from app import calcular_stats
        stats = calcular_stats(eval_basico)
        for dom_id in DOMINIOS:
            assert dom_id in stats["dominios"], f"Dominio {dom_id} falta en stats"

    def test_promedio_dominio_correcto(self, tmp_db, conn, eval_basico):
        from data.controles_iso27001 import CONTROLES, DOMINIOS
        from app import calcular_stats

        primer_dominio = list(DOMINIOS.keys())[0]
        ctrls = [c for c in CONTROLES if c["dominio"] == primer_dominio][:3]
        scores = [2, 4, 3]
        for ctrl, score in zip(ctrls, scores):
            insertar(conn, eval_basico, ctrl["id"], score)

        stats = calcular_stats(eval_basico)
        prom = stats["dominios"][primer_dominio]["promedio_madurez"]
        expected = round(sum(scores) / len(scores), 2)
        assert prom == expected
