"""
ISO 27001:2022 Gap Analysis Tool — servidor principal
"""
import json
import base64
import socketserver
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from database import get_conn, init_db
from data.controles_iso27001 import CONTROLES, DOMINIOS
from data.controles_bcra import CONTROLES_BCRA, DOMINIOS_BCRA, DOMINIOS_A7777, DOMINIOS_A7783
from data.controles_pci import CONTROLES_PCI, DOMINIOS_PCI
from report import generar_pdf
from ai_analyzer import analizar_evidencia

CONTROLES_A7777 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7777"]
CONTROLES_A7783 = [c for c in CONTROLES_BCRA if c.get("norma") == "A7783"]

BASE_DIR   = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

EXTENSIONES_VALIDAS = {
    ".pdf", ".docx", ".doc", ".txt", ".md", ".csv", ".json", ".xml",
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def controles_por_dominio():
    agrupados = {}
    for d in DOMINIOS:
        agrupados[d] = [c for c in CONTROLES if c["dominio"] == d]
    return agrupados


def get_control(ctrl_id: str):
    return next((c for c in CONTROLES if c["id"] == ctrl_id), None)


def calcular_stats(evaluacion_id):
    with get_conn() as conn:
        filas = conn.execute(
            "SELECT control_id, madurez, aplica FROM respuestas WHERE evaluacion_id = ?",
            (evaluacion_id,),
        ).fetchall()

    respuestas = {r["control_id"]: dict(r) for r in filas}
    stats = {"dominios": {}, "total": 0, "respondidos": 0, "madurez_global": 0}

    for dominio, controles in controles_por_dominio().items():
        aplicables = [c for c in controles if respuestas.get(c["id"], {}).get("aplica", 1)]
        respondidos = [c for c in aplicables if c["id"] in respuestas and respuestas[c["id"]]["madurez"] > 0]
        madureces = [respuestas[c["id"]]["madurez"] for c in respondidos]
        promedio = round(sum(madureces) / len(madureces), 2) if madureces else 0

        stats["dominios"][dominio] = {
            "nombre": DOMINIOS[dominio],
            "total": len(aplicables),
            "respondidos": len(respondidos),
            "promedio_madurez": promedio,
            "brechas": [
                {
                    "id": c["id"],
                    "nombre": c["nombre"],
                    "madurez": respuestas[c["id"]]["madurez"] if c["id"] in respuestas else 0,
                }
                for c in aplicables
                if c["id"] not in respuestas or respuestas[c["id"]]["madurez"] < 3
            ],
        }
        stats["total"] += len(aplicables)
        stats["respondidos"] += len(respondidos)

    todas_madureces = [
        respuestas[r]["madurez"] for r in respuestas if respuestas[r]["aplica"] and respuestas[r]["madurez"] > 0
    ]
    stats["madurez_global"] = round(sum(todas_madureces) / len(todas_madureces), 2) if todas_madureces else 0
    stats["progreso_pct"] = round(stats["respondidos"] / stats["total"] * 100, 1) if stats["total"] else 0
    return stats


def calcular_cobertura(evaluacion_id: int, framework: str):
    """Calcula cobertura estimada de A7777, A7783, BCRA o PCI DSS basada en madurez ISO 27001."""
    fw_map = {
        "A7777": (CONTROLES_A7777, DOMINIOS_A7777),
        "A7783": (CONTROLES_A7783, DOMINIOS_A7783),
        "BCRA":  (CONTROLES_BCRA,  DOMINIOS_BCRA),
        "PCI":   (CONTROLES_PCI,   DOMINIOS_PCI),
    }
    controles_fw, dominios_fw = fw_map[framework]

    with get_conn() as conn:
        filas = conn.execute(
            "SELECT control_id, madurez, aplica FROM respuestas WHERE evaluacion_id = ?",
            (evaluacion_id,),
        ).fetchall()
    madureces_iso = {r["control_id"]: dict(r) for r in filas}

    dominios_result = {}
    controles_result = []

    for ctrl in controles_fw:
        mapped = ctrl.get("iso_mapping", [])
        scores = [
            madureces_iso[iso]["madurez"]
            for iso in mapped
            if iso in madureces_iso and madureces_iso[iso].get("aplica", 1) and madureces_iso[iso]["madurez"] > 0
        ]
        madurez_est = round(sum(scores) / len(scores), 2) if scores else 0
        cubierto = len(scores)
        total_mapped = len(mapped)

        controles_result.append({
            "id": ctrl["id"],
            "nombre": ctrl["nombre"],
            "dominio": ctrl["dominio"],
            "referencia": ctrl.get("referencia", ""),
            "iso_mapping": mapped,
            "madurez_estimada": madurez_est,
            "controles_iso_cubiertos": cubierto,
            "controles_iso_total": total_mapped,
            "evidencia_requerida": ctrl.get("evidencia_requerida", []),
        })

        dom = ctrl["dominio"]
        if dom not in dominios_result:
            dominios_result[dom] = {
                "nombre": dominios_fw[dom],
                "total": 0,
                "con_cobertura": 0,
                "madurez_sum": 0.0,
            }
        dominios_result[dom]["total"] += 1
        if madurez_est > 0:
            dominios_result[dom]["con_cobertura"] += 1
            dominios_result[dom]["madurez_sum"] += madurez_est

    for dom in dominios_result:
        n = dominios_result[dom]["con_cobertura"]
        dominios_result[dom]["madurez_promedio"] = (
            round(dominios_result[dom]["madurez_sum"] / n, 2) if n else 0
        )
        del dominios_result[dom]["madurez_sum"]

    return {"framework": framework, "dominios": dominios_result, "controles": controles_result}


# ── Handler HTTP ──────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, content_type):
        try:
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── GET ───────────────────────────────────────────────────────────────────

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self.send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")

        elif path.startswith("/static/"):
            rel = path[len("/static/"):]
            ext = Path(rel).suffix
            tipos = {".css": "text/css", ".js": "application/javascript", ".svg": "image/svg+xml"}
            self.send_file(STATIC_DIR / rel, tipos.get(ext, "application/octet-stream"))

        elif path == "/api/evaluaciones":
            with get_conn() as conn:
                rows = conn.execute("SELECT * FROM evaluaciones ORDER BY actualizada DESC").fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and "/stats" in path:
            eid = int(path.split("/")[3])
            self.send_json(calcular_stats(eid))

        elif path.startswith("/api/evaluaciones/") and "/respuestas" in path:
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute("SELECT * FROM respuestas WHERE evaluacion_id = ?", (eid,)).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and "/evidencias" in path:
            parts = path.split("/")
            eid = int(parts[3])
            ctrl_id = qs.get("control_id", [None])[0]
            with get_conn() as conn:
                if ctrl_id:
                    rows = conn.execute(
                        "SELECT * FROM evidencias WHERE evaluacion_id=? AND control_id=? ORDER BY subida_en DESC",
                        (eid, ctrl_id),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        "SELECT * FROM evidencias WHERE evaluacion_id=? ORDER BY subida_en DESC", (eid,)
                    ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and "/hallazgos" in path:
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM hallazgos WHERE evaluacion_id=? ORDER BY creado_en DESC", (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == "/api/controles":
            self.send_json(CONTROLES)

        elif path == "/api/dominios":
            self.send_json(DOMINIOS)

        elif path == "/api/frameworks/bcra/controles":
            self.send_json(CONTROLES_BCRA)

        elif path == "/api/frameworks/bcra/dominios":
            self.send_json(DOMINIOS_BCRA)

        elif path == "/api/frameworks/a7777/controles":
            self.send_json(CONTROLES_A7777)

        elif path == "/api/frameworks/a7777/dominios":
            self.send_json(DOMINIOS_A7777)

        elif path == "/api/frameworks/a7783/controles":
            self.send_json(CONTROLES_A7783)

        elif path == "/api/frameworks/a7783/dominios":
            self.send_json(DOMINIOS_A7783)

        elif path == "/api/frameworks/pci/controles":
            self.send_json(CONTROLES_PCI)

        elif path == "/api/frameworks/pci/dominios":
            self.send_json(DOMINIOS_PCI)

        elif path.startswith("/api/evaluaciones/") and "/cobertura/" in path:
            parts = path.split("/")
            eid = int(parts[3])
            fw = parts[5].upper()
            if fw not in ("A7777", "A7783", "BCRA", "PCI"):
                self.send_json({"error": "framework no soportado"}, 400)
                return
            self.send_json(calcular_cobertura(eid, fw))

        elif path.startswith("/api/report/"):
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                ev = conn.execute("SELECT * FROM evaluaciones WHERE id=?", (eid,)).fetchone()
            if not ev:
                self.send_json({"error": "no encontrada"}, 404)
                return
            stats = calcular_stats(eid)
            pdf_path = generar_pdf(dict(ev), stats, CONTROLES)
            data = pdf_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="gap-analysis-{eid}.pdf"')
            self.send_header("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)

        else:
            self.send_response(404)
            self.end_headers()

    # ── POST ──────────────────────────────────────────────────────────────────

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw)
        except Exception:
            body = {}
        parsed = urlparse(self.path)
        path = parsed.path

        # Crear evaluación
        if path == "/api/evaluaciones":
            import json as _json
            fws = body.get("frameworks", ["ISO27001"])
            if "ISO27001" not in fws:
                fws = ["ISO27001"] + fws
            with get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO evaluaciones (nombre, empresa, alcance, frameworks) VALUES (?,?,?,?)",
                    (body.get("nombre", "Sin nombre"), body.get("empresa", ""),
                     body.get("alcance", ""), _json.dumps(fws, ensure_ascii=False)),
                )
            self.send_json({"id": cur.lastrowid})

        # Guardar respuesta de control
        elif path.startswith("/api/evaluaciones/") and "/respuestas" in path:
            eid = int(path.split("/")[3])
            ctrl_id = body["control_id"]
            madurez = int(body.get("madurez", 0))
            comentario = body.get("comentario", "")
            aplica = int(body.get("aplica", 1))
            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO respuestas (evaluacion_id, control_id, madurez, comentario, aplica)
                       VALUES (?,?,?,?,?)
                       ON CONFLICT(evaluacion_id, control_id)
                       DO UPDATE SET madurez=excluded.madurez,
                                     comentario=excluded.comentario,
                                     aplica=excluded.aplica""",
                    (eid, ctrl_id, madurez, comentario, aplica),
                )
                conn.execute("UPDATE evaluaciones SET actualizada=datetime('now') WHERE id=?", (eid,))
            self.send_json({"ok": True})

        # Subir evidencia (base64)
        elif path.startswith("/api/evaluaciones/") and "/evidencias" in path and "analizar" not in path:
            eid = int(path.split("/")[3])
            ctrl_id = body.get("control_id", "")
            filename = body.get("filename", "archivo")
            data_b64 = body.get("data", "")
            framework = body.get("framework", "ISO27001")

            ext = Path(filename).suffix.lower()
            if ext not in EXTENSIONES_VALIDAS:
                self.send_json({"error": f"Extensión no soportada: {ext}"}, 400)
                return

            # Guardar archivo
            safe_name = f"{uuid.uuid4().hex}{ext}"
            filepath = UPLOADS_DIR / safe_name
            try:
                filepath.write_bytes(base64.b64decode(data_b64))
            except Exception as e:
                self.send_json({"error": f"No se pudo guardar el archivo: {e}"}, 500)
                return

            with get_conn() as conn:
                cur = conn.execute(
                    """INSERT INTO evidencias (evaluacion_id, control_id, framework, filename, filepath, filetype)
                       VALUES (?,?,?,?,?,?)""",
                    (eid, ctrl_id, framework, filename, str(filepath), ext),
                )
                ev_id = cur.lastrowid
            self.send_json({"id": ev_id, "filename": filename})

        # Analizar evidencia con IA
        elif "/evidencias/" in path and path.endswith("/analizar"):
            parts = path.split("/")
            ev_id = int(parts[5])
            with get_conn() as conn:
                ev = conn.execute("SELECT * FROM evidencias WHERE id=?", (ev_id,)).fetchone()
            if not ev:
                self.send_json({"error": "evidencia no encontrada"}, 404)
                return
            ev = dict(ev)
            ctrl = get_control(ev["control_id"])
            if not ctrl:
                self.send_json({"error": "control no encontrado"}, 404)
                return

            resultado = analizar_evidencia(
                filepath=ev["filepath"],
                filetype=ev["filetype"],
                control_id=ctrl["id"],
                control_nombre=ctrl["nombre"],
                control_descripcion=ctrl["descripcion"],
            )

            analisis_str = json.dumps(resultado, ensure_ascii=False)
            with get_conn() as conn:
                conn.execute(
                    "UPDATE evidencias SET analisis_ia=?, veredicto=? WHERE id=?",
                    (analisis_str, resultado.get("veredicto", "pendiente"), ev_id),
                )
            self.send_json(resultado)

        # Crear hallazgo
        elif path.startswith("/api/evaluaciones/") and "/hallazgos" in path:
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                cur = conn.execute(
                    """INSERT INTO hallazgos
                       (evaluacion_id, control_id, framework, evidencia_id, tipo, severidad,
                        titulo, descripcion, responsable_nombre, responsable_email,
                        fecha_limite, plan_accion, estado)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        eid,
                        body.get("control_id", ""),
                        body.get("framework", "ISO27001"),
                        body.get("evidencia_id"),
                        body.get("tipo", "no_conformidad"),
                        body.get("severidad", "media"),
                        body.get("titulo", ""),
                        body.get("descripcion", ""),
                        body.get("responsable_nombre", ""),
                        body.get("responsable_email", ""),
                        body.get("fecha_limite", ""),
                        body.get("plan_accion", ""),
                        body.get("estado", "abierto"),
                    ),
                )
            self.send_json({"id": cur.lastrowid})

        else:
            self.send_response(404)
            self.end_headers()

    # ── PUT ───────────────────────────────────────────────────────────────────

    def do_PUT(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        path = urlparse(self.path).path

        if "/hallazgos/" in path:
            hid = int(path.split("/")[-1])
            campos = ["tipo", "severidad", "titulo", "descripcion",
                      "responsable_nombre", "responsable_email",
                      "fecha_limite", "plan_accion", "estado"]
            sets = ", ".join(f"{c}=?" for c in campos if c in body)
            vals = [body[c] for c in campos if c in body]
            if sets:
                vals.append(hid)
                with get_conn() as conn:
                    conn.execute(
                        f"UPDATE hallazgos SET {sets}, actualizado_en=datetime('now') WHERE id=?", vals
                    )
            self.send_json({"ok": True})
        else:
            self.send_response(404)
            self.end_headers()

    # ── DELETE ────────────────────────────────────────────────────────────────

    def do_DELETE(self):
        path = urlparse(self.path).path

        if "/hallazgos/" in path:
            hid = int(path.split("/")[-1])
            with get_conn() as conn:
                conn.execute("DELETE FROM hallazgos WHERE id=?", (hid,))
            self.send_json({"ok": True})

        elif "/evidencias/" in path:
            ev_id = int(path.split("/")[-1])
            with get_conn() as conn:
                ev = conn.execute("SELECT filepath FROM evidencias WHERE id=?", (ev_id,)).fetchone()
                if ev:
                    try:
                        Path(ev["filepath"]).unlink(missing_ok=True)
                    except Exception:
                        pass
                conn.execute("DELETE FROM evidencias WHERE id=?", (ev_id,))
            self.send_json({"ok": True})

        elif path.startswith("/api/evaluaciones/"):
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                conn.execute("DELETE FROM evaluaciones WHERE id=?", (eid,))
            self.send_json({"ok": True})

        else:
            self.send_response(404)
            self.end_headers()


class ThreadingServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def main():
    init_db()
    port = 8090
    print(f"ISO 27001 Gap Analysis Tool — http://localhost:{port}")
    ThreadingServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
