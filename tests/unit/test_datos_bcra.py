"""
Tests de integridad sobre los datos de controles_bcra.py.

ANÁLISIS DE RIESGO:
  - Control con iso_mapping referenciando un control ISO inexistente → cobertura silenciosa incorrecta
  - Control sin evidencia_requerida → UX rota en frontend
  - Dominio de un control no registrado en DOMINIOS_* → KeyError en calcular_cobertura
  - IDs duplicados → datos sobrescritos en el dict de cobertura
  - Norma incorrecta (ni A7777 ni A7783) → controles huérfanos en filtro
"""
import pytest
from data.controles_bcra import (
    CONTROLES_BCRA, DOMINIOS_BCRA, DOMINIOS_A7777, DOMINIOS_A7783,
)
from data.controles_iso27001 import CONTROLES as CONTROLES_ISO


# Pre-computar sets útiles
ISO_IDS = {c["id"] for c in CONTROLES_ISO}
BCRA_NORMAS = {"A7777", "A7783"}


class TestIntegridadEstructural:

    def test_sin_ids_duplicados(self):
        ids = [c["id"] for c in CONTROLES_BCRA]
        duplicados = [i for i in ids if ids.count(i) > 1]
        assert not duplicados, f"IDs duplicados: {set(duplicados)}"

    def test_todos_tienen_campo_norma(self):
        sin_norma = [c["id"] for c in CONTROLES_BCRA if "norma" not in c]
        assert not sin_norma, f"Sin campo 'norma': {sin_norma}"

    def test_norma_es_a7777_o_a7783(self):
        invalidos = [c["id"] for c in CONTROLES_BCRA if c.get("norma") not in BCRA_NORMAS]
        assert not invalidos, f"Norma inválida en: {invalidos}"

    def test_todos_tienen_evidencia_requerida(self):
        sin_ev = [c["id"] for c in CONTROLES_BCRA if not c.get("evidencia_requerida")]
        assert not sin_ev, f"Sin evidencia_requerida: {sin_ev}"

    def test_evidencia_requerida_no_vacia(self):
        vacios = [c["id"] for c in CONTROLES_BCRA if len(c.get("evidencia_requerida", [])) == 0]
        assert not vacios, f"evidencia_requerida vacía en: {vacios}"

    def test_todos_tienen_iso_mapping(self):
        sin_map = [c["id"] for c in CONTROLES_BCRA if "iso_mapping" not in c]
        assert not sin_map, f"Sin iso_mapping: {sin_map}"

    def test_iso_mapping_no_vacio(self):
        """Controles sin ningún ISO mapping no pueden generar cobertura."""
        vacios = [c["id"] for c in CONTROLES_BCRA if not c.get("iso_mapping")]
        assert not vacios, f"iso_mapping vacío en: {vacios}"


class TestConsistenciaConISO27001:

    def test_todos_los_iso_mapping_existen_en_iso27001(self):
        """
        CRÍTICO: Si un control BCRA referencia un ID ISO que no existe,
        nunca tendrá cobertura aunque el auditor lo haya respondido.
        """
        referencias_invalidas = []
        for ctrl in CONTROLES_BCRA:
            for iso_id in ctrl.get("iso_mapping", []):
                if iso_id not in ISO_IDS:
                    referencias_invalidas.append((ctrl["id"], iso_id))
        assert not referencias_invalidas, (
            f"Referencias ISO inválidas (no existen en controles_iso27001): "
            f"{referencias_invalidas[:10]}"
        )


class TestConsistenciaDominios:

    def test_dominio_de_cada_control_existe_en_dominios_bcra(self):
        dominios_invalidos = [
            (c["id"], c["dominio"])
            for c in CONTROLES_BCRA
            if c["dominio"] not in DOMINIOS_BCRA
        ]
        assert not dominios_invalidos, f"Dominios no registrados: {dominios_invalidos}"

    def test_controles_a7777_solo_en_dominios_a7777(self):
        ctrls_7777 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7777"]
        fuera = [(c["id"], c["dominio"]) for c in ctrls_7777 if c["dominio"] not in DOMINIOS_A7777]
        assert not fuera, f"Controles A7777 con dominio A7783: {fuera}"

    def test_controles_a7783_solo_en_dominios_a7783(self):
        ctrls_7783 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7783"]
        fuera = [(c["id"], c["dominio"]) for c in ctrls_7783 if c["dominio"] not in DOMINIOS_A7783]
        assert not fuera, f"Controles A7783 con dominio A7777: {fuera}"

    def test_todos_dominios_a7777_tienen_al_menos_un_control(self):
        ctrls_por_dom = {d: 0 for d in DOMINIOS_A7777}
        for c in CONTROLES_BCRA:
            if c.get("norma") == "A7777" and c["dominio"] in ctrls_por_dom:
                ctrls_por_dom[c["dominio"]] += 1
        vacios = [d for d, n in ctrls_por_dom.items() if n == 0]
        assert not vacios, f"Dominios A7777 sin controles: {vacios}"


class TestSeparacionNormas:

    def test_conteo_controles_a7777(self):
        n = len([c for c in CONTROLES_BCRA if c.get("norma") == "A7777"])
        assert n > 0, "No hay controles A7777"
        assert n == len([c for c in CONTROLES_BCRA if c["id"].startswith("A7777-")])

    def test_conteo_controles_a7783(self):
        n = len([c for c in CONTROLES_BCRA if c.get("norma") == "A7783"])
        assert n > 0, "No hay controles A7783"
        assert n == len([c for c in CONTROLES_BCRA if c["id"].startswith("A7783-")])

    def test_suma_normas_igual_total(self):
        n7777 = len([c for c in CONTROLES_BCRA if c.get("norma") == "A7777"])
        n7783 = len([c for c in CONTROLES_BCRA if c.get("norma") == "A7783"])
        assert n7777 + n7783 == len(CONTROLES_BCRA), (
            "La suma de A7777 + A7783 no coincide con el total de CONTROLES_BCRA"
        )
