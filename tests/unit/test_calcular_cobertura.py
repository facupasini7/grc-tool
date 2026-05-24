"""
Tests unitarios para calcular_cobertura().

ANÁLISIS DE RIESGO:
  - Evaluación sin respuestas → cobertura 0 para todos los controles
  - Control con iso_mapping vacío → madurez_estimada = 0, no dividir por 0
  - Control cuyo iso_mapping apunta a controles NO respondidos → madurez = 0
  - Framework inválido → KeyError no manejado
  - Respuestas con aplica=0 deben excluirse del cálculo
  - Madurez promedio por dominio: solo considera controles con madurez > 0
"""
import json
import pytest


# ── Helpers ──────────────────────────────────────────────────────────────────

def insertar_respuesta(conn, eval_id, ctrl_id, madurez, aplica=1):
    conn.execute(
        "INSERT OR REPLACE INTO respuestas (evaluacion_id, control_id, madurez, aplica) "
        "VALUES (?,?,?,?)",
        (eval_id, ctrl_id, madurez, aplica),
    )


# ── Tests ────────────────────────────────────────────────────────────────────

class TestCoberturaEvaluacionVacia:
    """Evaluación sin ninguna respuesta ISO."""

    def test_todos_los_controles_tienen_madurez_cero(self, tmp_db, eval_basico):
        from app import calcular_cobertura
        result = calcular_cobertura(eval_basico, "A7777")
        for c in result["controles"]:
            assert c["madurez_estimada"] == 0, (
                f"Control {c['id']} debería tener madurez 0 sin respuestas"
            )

    def test_controles_iso_cubiertos_es_cero(self, tmp_db, eval_basico):
        from app import calcular_cobertura
        result = calcular_cobertura(eval_basico, "A7777")
        for c in result["controles"]:
            assert c["controles_iso_cubiertos"] == 0

    def test_madurez_promedio_dominio_es_cero(self, tmp_db, eval_basico):
        from app import calcular_cobertura
        result = calcular_cobertura(eval_basico, "A7777")
        for dom in result["dominios"].values():
            assert dom["madurez_promedio"] == 0

    def test_no_division_por_cero_en_dominio_sin_cobertura(self, tmp_db, eval_basico):
        """Jamás debe producirse ZeroDivisionError."""
        from app import calcular_cobertura
        # No debe lanzar excepción
        result = calcular_cobertura(eval_basico, "A7777")
        assert result is not None


class TestCoberturaConRespuestas:
    """Evaluación con respuestas parciales."""

    def test_madurez_estimada_es_promedio_de_iso_mapping(self, tmp_db, conn, eval_basico):
        """
        Si A7777-2.1.1 mapea a [A.5.1, A.5.2, A.5.4] y los tres tienen
        madurez 3, 4, 5 → el promedio debe ser 4.0.
        """
        from app import calcular_cobertura
        from data.controles_bcra import CONTROLES_BCRA

        ctrl = next(c for c in CONTROLES_BCRA if c["id"] == "A7777-2.1.1")
        iso_ids = ctrl["iso_mapping"]   # ["A.5.1", "A.5.2", "A.5.4"]

        scores = [3, 4, 5]
        for iso_id, score in zip(iso_ids, scores):
            insertar_respuesta(conn, eval_basico, iso_id, score)

        result = calcular_cobertura(eval_basico, "A7777")
        ctrl_result = next(c for c in result["controles"] if c["id"] == "A7777-2.1.1")

        expected = round(sum(scores) / len(scores), 2)
        assert ctrl_result["madurez_estimada"] == expected, (
            f"Esperaba {expected}, obtuve {ctrl_result['madurez_estimada']}"
        )

    def test_controles_con_aplica_false_no_cuentan(self, tmp_db, conn, eval_basico):
        """Respuestas con aplica=0 no deben sumar al promedio."""
        from app import calcular_cobertura
        from data.controles_bcra import CONTROLES_BCRA

        ctrl = next(c for c in CONTROLES_BCRA if c["id"] == "A7777-2.1.1")
        iso_ids = ctrl["iso_mapping"]

        # Primer ISO: aplica=0, madurez=5 (no debe contar)
        insertar_respuesta(conn, eval_basico, iso_ids[0], 5, aplica=0)
        # Segundo ISO: aplica=1, madurez=2
        insertar_respuesta(conn, eval_basico, iso_ids[1], 2, aplica=1)

        result = calcular_cobertura(eval_basico, "A7777")
        ctrl_result = next(c for c in result["controles"] if c["id"] == "A7777-2.1.1")

        # Solo debe promediar el control con madurez=2
        assert ctrl_result["madurez_estimada"] == 2.0
        assert ctrl_result["controles_iso_cubiertos"] == 1

    def test_dominio_madurez_promedio_solo_controles_cubiertos(self, tmp_db, conn, eval_basico):
        """
        El promedio de dominio solo divide entre controles con madurez > 0,
        no entre todos los controles del dominio.
        """
        from app import calcular_cobertura
        from data.controles_bcra import CONTROLES_BCRA

        # Responder solo el primer ISO del primer control de S2
        ctrl_s2 = [c for c in CONTROLES_BCRA if c["dominio"] == "S2"][0]
        insertar_respuesta(conn, eval_basico, ctrl_s2["iso_mapping"][0], 4)

        result = calcular_cobertura(eval_basico, "A7777")
        dom_s2 = result["dominios"]["S2"]

        assert dom_s2["con_cobertura"] >= 1
        # El promedio debe ser > 0 (no arrastrar los 0 de controles sin cubrir)
        assert dom_s2["madurez_promedio"] > 0

    def test_evidencia_requerida_incluida_en_respuesta(self, tmp_db, eval_basico):
        """El campo evidencia_requerida debe venir en cada control."""
        from app import calcular_cobertura
        result = calcular_cobertura(eval_basico, "A7777")
        for c in result["controles"]:
            assert "evidencia_requerida" in c, (
                f"Control {c['id']} no tiene evidencia_requerida"
            )
            assert isinstance(c["evidencia_requerida"], list)


class TestCoberturaFrameworks:
    """Validación de los frameworks soportados."""

    @pytest.mark.parametrize("fw", ["A7777", "A7783", "BCRA", "PCI"])
    def test_frameworks_validos_retornan_datos(self, tmp_db, eval_basico, fw):
        from app import calcular_cobertura
        result = calcular_cobertura(eval_basico, fw)
        assert "controles" in result
        assert "dominios" in result
        assert result["framework"] == fw

    def test_framework_invalido_lanza_key_error(self, tmp_db, eval_basico):
        """
        REGRESIÓN: framework desconocido debe fallar explícitamente,
        no retornar datos vacíos silenciosamente.
        """
        from app import calcular_cobertura
        with pytest.raises(KeyError):
            calcular_cobertura(eval_basico, "NIST_800")

    def test_a7777_y_a7783_son_disjuntos(self, tmp_db, eval_basico):
        """Los controles de A7777 y A7783 no deben solaparse."""
        from app import calcular_cobertura
        ids_7777 = {c["id"] for c in calcular_cobertura(eval_basico, "A7777")["controles"]}
        ids_7783 = {c["id"] for c in calcular_cobertura(eval_basico, "A7783")["controles"]}
        overlap = ids_7777 & ids_7783
        assert not overlap, f"Controles en ambas normas: {overlap}"

    def test_bcra_es_union_de_a7777_y_a7783(self, tmp_db, eval_basico):
        """BCRA combinado debe contener exactamente la unión de A7777 + A7783."""
        from app import calcular_cobertura
        ids_7777 = {c["id"] for c in calcular_cobertura(eval_basico, "A7777")["controles"]}
        ids_7783 = {c["id"] for c in calcular_cobertura(eval_basico, "A7783")["controles"]}
        ids_bcra = {c["id"] for c in calcular_cobertura(eval_basico, "BCRA")["controles"]}
        assert ids_bcra == ids_7777 | ids_7783


class TestCoberturaEdgeCases:
    """Casos de borde y comportamiento ante datos corruptos."""

    def test_madurez_maxima_cinco(self, tmp_db, conn, eval_basico):
        """Madurez 5 en todos los ISO → promedio debe ser exactamente 5."""
        from app import calcular_cobertura
        from data.controles_bcra import CONTROLES_BCRA
        ctrl = CONTROLES_BCRA[0]
        for iso_id in ctrl["iso_mapping"]:
            insertar_respuesta(conn, eval_basico, iso_id, 5)
        result = calcular_cobertura(eval_basico, "A7777")
        c = next(x for x in result["controles"] if x["id"] == ctrl["id"])
        assert c["madurez_estimada"] == 5.0

    def test_control_sin_iso_mapping(self, tmp_db, conn, eval_basico):
        """
        EDGE CASE: si un control tuviese iso_mapping vacío, madurez debe
        ser 0 y controles_iso_cubiertos = 0. No debe explotar.
        """
        from app import calcular_cobertura
        from data.controles_bcra import CONTROLES_BCRA
        # Parchear temporalmente un control para simular mapping vacío
        original = CONTROLES_BCRA[0]["iso_mapping"]
        CONTROLES_BCRA[0]["iso_mapping"] = []
        try:
            result = calcular_cobertura(eval_basico, "A7777")
            c = next(x for x in result["controles"] if x["id"] == CONTROLES_BCRA[0]["id"])
            assert c["madurez_estimada"] == 0
            assert c["controles_iso_cubiertos"] == 0
        finally:
            CONTROLES_BCRA[0]["iso_mapping"] = original

    def test_evaluacion_inexistente_retorna_vacio(self, tmp_db):
        """Evaluación que no existe en DB: no debe crashear, debe retornar listas vacías."""
        from app import calcular_cobertura
        # La función hace SELECT con ese ID; si no hay filas, madureces_iso queda {}
        # y todos los controles tendrán madurez 0 (comportamiento esperado)
        result = calcular_cobertura(99999, "A7777")
        assert len(result["controles"]) > 0   # Los controles BCRA siempre existen
        for c in result["controles"]:
            assert c["madurez_estimada"] == 0
