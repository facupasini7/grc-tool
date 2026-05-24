"""
Tests de integración para los endpoints de evaluaciones.
Levanta el Handler HTTP real contra una DB temporal usando
http.server directamente (sin proceso externo).

ANÁLISIS DE RIESGO:
  - POST sin nombre/empresa → debe rechazar (actualmente no valida en backend)
  - POST con frameworks inválidos → debe guardarse sin crash
  - GET evaluación inexistente → 404 o lista vacía
  - DELETE en cascada → respuestas y evidencias deben borrarse
  - JSON malformado en POST → no debe crashear el servidor
  - Content-Length incorrecto → comportamiento ante truncado
"""
import json
import sys
import threading
from http.server import HTTPServer
from pathlib import Path
from urllib import request as urllib_request
from urllib.error import HTTPError

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))


# ── Server fixture ────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def server(tmp_path, monkeypatch):
    """Levanta una instancia real del servidor en un puerto libre."""
    import database
    db_file = tmp_path / "test_api.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database.init_db()

    from app import Handler, ThreadingServer
    srv = ThreadingServer(("127.0.0.1", 0), Handler)   # puerto 0 = asignado por el SO
    port = srv.server_address[1]
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    yield base
    srv.shutdown()


def get(server, path):
    resp = urllib_request.urlopen(f"{server}{path}")
    return json.loads(resp.read())


def post(server, path, body):
    data = json.dumps(body).encode()
    req = urllib_request.Request(
        f"{server}{path}", data=data,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    resp = urllib_request.urlopen(req)
    return json.loads(resp.read())


def delete(server, path):
    req = urllib_request.Request(f"{server}{path}", method="DELETE")
    resp = urllib_request.urlopen(req)
    return json.loads(resp.read())


# ── Tests CRUD básico ─────────────────────────────────────────────────────────

class TestCrearEvaluacion:

    def test_crear_con_todos_los_campos_retorna_id(self, server):
        result = post(server, "/api/evaluaciones", {
            "nombre": "Test ISO", "empresa": "ACME SA",
            "alcance": "cloud", "frameworks": ["ISO27001", "A7777"],
        })
        assert "id" in result
        assert isinstance(result["id"], int)

    def test_frameworks_se_guardan_correctamente(self, server):
        post(server, "/api/evaluaciones", {
            "nombre": "Solo BCRA", "empresa": "Banco X",
            "frameworks": ["A7777", "A7783"],
        })
        evs = get(server, "/api/evaluaciones")
        ev = evs[0]
        stored = json.loads(ev["frameworks"])
        assert "A7777" in stored
        assert "A7783" in stored

    def test_crear_sin_frameworks_usa_default(self, server):
        """Sin frameworks en el body → debe usar ["ISO27001"] como default."""
        post(server, "/api/evaluaciones", {"nombre": "Sin FW", "empresa": "Corp"})
        evs = get(server, "/api/evaluaciones")
        stored = json.loads(evs[0]["frameworks"])
        assert stored == ["ISO27001"]

    def test_iso27001_ya_no_es_forzado(self, server):
        """
        CAMBIO DE COMPORTAMIENTO: ISO27001 ahora es opcional.
        Una evaluación solo-BCRA debe almacenarse sin ISO27001.
        """
        post(server, "/api/evaluaciones", {
            "nombre": "Solo BCRA", "empresa": "Banco",
            "frameworks": ["A7777"],
        })
        evs = get(server, "/api/evaluaciones")
        stored = json.loads(evs[0]["frameworks"])
        assert stored == ["A7777"]
        assert "ISO27001" not in stored

    def test_frameworks_lista_vacia_usa_default(self, server):
        """Lista vacía → fallback a ISO27001 para no dejar huérfana la evaluación."""
        post(server, "/api/evaluaciones", {
            "nombre": "Vacio", "empresa": "X", "frameworks": [],
        })
        evs = get(server, "/api/evaluaciones")
        stored = json.loads(evs[0]["frameworks"])
        assert stored == ["ISO27001"]

    def test_crear_multiples_evaluaciones(self, server):
        for i in range(5):
            post(server, "/api/evaluaciones", {"nombre": f"Eval {i}", "empresa": "Corp"})
        evs = get(server, "/api/evaluaciones")
        assert len(evs) == 5

    def test_json_malformado_no_crashea_servidor(self, server):
        """JSON inválido → el servidor debe responder (400/200 con body vacío), no 500."""
        req = urllib_request.Request(
            f"{server}/api/evaluaciones",
            data=b"{ not valid json !!!",
            headers={"Content-Type": "application/json", "Content-Length": "20"},
            method="POST",
        )
        try:
            resp = urllib_request.urlopen(req)
            # Si no lanza, debe retornar algo sensato
            body = json.loads(resp.read())
            assert "id" in body   # se creó con defaults vacíos
        except HTTPError as e:
            # Un 4xx es aceptable
            assert e.code < 500, f"Error del servidor inesperado: {e.code}"


class TestListarEvaluaciones:

    def test_lista_vacia_al_inicio(self, server):
        evs = get(server, "/api/evaluaciones")
        assert evs == []

    def test_lista_retorna_todas(self, server):
        post(server, "/api/evaluaciones", {"nombre": "A", "empresa": "X"})
        post(server, "/api/evaluaciones", {"nombre": "B", "empresa": "Y"})
        evs = get(server, "/api/evaluaciones")
        assert len(evs) == 2

    def test_orden_desc_por_actualizada(self, server):
        """La evaluación más reciente debe aparecer primero."""
        post(server, "/api/evaluaciones", {"nombre": "Primera", "empresa": "X"})
        post(server, "/api/evaluaciones", {"nombre": "Segunda", "empresa": "Y"})
        evs = get(server, "/api/evaluaciones")
        # "Segunda" debe aparecer antes (actualizada más reciente)
        assert evs[0]["nombre"] == "Segunda"


class TestEliminarEvaluacion:

    def test_eliminar_borra_de_la_lista(self, server):
        r = post(server, "/api/evaluaciones", {"nombre": "A borrar", "empresa": "X"})
        eid = r["id"]
        delete(server, f"/api/evaluaciones/{eid}")
        evs = get(server, "/api/evaluaciones")
        assert all(e["id"] != eid for e in evs)

    def test_eliminar_en_cascada_respuestas(self, server):
        """Al eliminar la evaluación, sus respuestas deben desaparecer."""
        r = post(server, "/api/evaluaciones", {"nombre": "Con resp", "empresa": "X"})
        eid = r["id"]
        # Guardar una respuesta
        post(server, f"/api/evaluaciones/{eid}/respuestas", {
            "control_id": "A.5.1", "madurez": 3, "aplica": 1,
        })
        # Verificar que existe
        resp = get(server, f"/api/evaluaciones/{eid}/respuestas")
        assert len(resp) == 1
        # Eliminar evaluación
        delete(server, f"/api/evaluaciones/{eid}")
        # Verificar que la respuesta también se eliminó (FK CASCADE)
        # Con la evaluación borrada, el endpoint retornará 404 o lista vacía
        try:
            resp_post = get(server, f"/api/evaluaciones/{eid}/respuestas")
            assert resp_post == []
        except HTTPError:
            pass  # 404 también es correcto


class TestFrameworksEndpoints:

    @pytest.mark.parametrize("fw,expected_keys", [
        ("bcra",  ["S2", "S3", "S4"]),
        ("a7777", ["S2", "S10"]),
        ("a7783", ["S11"]),
        ("pci",   ["R1", "R12"]),
    ])
    def test_dominios_contienen_claves_esperadas(self, server, fw, expected_keys):
        dominios = get(server, f"/api/frameworks/{fw}/dominios")
        for key in expected_keys:
            assert key in dominios, f"Falta dominio {key} en framework {fw}"

    @pytest.mark.parametrize("fw", ["bcra", "a7777", "a7783", "pci"])
    def test_controles_tienen_campos_obligatorios(self, server, fw):
        controles = get(server, f"/api/frameworks/{fw}/controles")
        assert len(controles) > 0
        campos = ["id", "nombre", "dominio", "iso_mapping", "evidencia_requerida"]
        for c in controles:
            for campo in campos:
                assert campo in c, f"Control {c.get('id')} en {fw} sin campo '{campo}'"

    def test_a7777_no_contiene_controles_a7783(self, server):
        ctrls = get(server, "/api/frameworks/a7777/controles")
        for c in ctrls:
            assert not c["id"].startswith("A7783-"), (
                f"Control A7783 encontrado en endpoint a7777: {c['id']}"
            )

    def test_a7783_no_contiene_controles_a7777(self, server):
        ctrls = get(server, "/api/frameworks/a7783/controles")
        for c in ctrls:
            assert not c["id"].startswith("A7777-"), (
                f"Control A7777 encontrado en endpoint a7783: {c['id']}"
            )


class TestCoberturaEndpoint:

    def test_cobertura_retorna_estructura_correcta(self, server):
        r = post(server, "/api/evaluaciones", {"nombre": "Test", "empresa": "X"})
        eid = r["id"]
        data = get(server, f"/api/evaluaciones/{eid}/cobertura/a7777")
        assert "framework" in data
        assert "controles" in data
        assert "dominios" in data
        assert data["framework"] == "A7777"

    def test_framework_invalido_retorna_400(self, server):
        r = post(server, "/api/evaluaciones", {"nombre": "Test", "empresa": "X"})
        eid = r["id"]
        with pytest.raises(HTTPError) as exc:
            get(server, f"/api/evaluaciones/{eid}/cobertura/nist800")
        assert exc.value.code == 400

    @pytest.mark.parametrize("fw_path", ["a7777", "a7783", "bcra", "pci"])
    def test_todos_frameworks_validos_responden_200(self, server, fw_path):
        r = post(server, "/api/evaluaciones", {"nombre": "T", "empresa": "E"})
        eid = r["id"]
        data = get(server, f"/api/evaluaciones/{eid}/cobertura/{fw_path}")
        assert len(data["controles"]) > 0
