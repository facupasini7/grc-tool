"""
ISO 27001:2022 Gap Analysis Tool — servidor principal
"""
import json
import math
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

from database import get_conn, init_db
from data.controles_iso27001 import CONTROLES, DOMINIOS
from report import generar_pdf

BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"


def controles_por_dominio():
    agrupados = {}
    for d in DOMINIOS:
        agrupados[d] = [c for c in CONTROLES if c["dominio"] == d]
    return agrupados


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


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silenciar logs HTTP en consola

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
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
                rows = conn.execute(
                    "SELECT * FROM evaluaciones ORDER BY actualizada DESC"
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path.startswith("/api/evaluaciones/") and "/stats" in path:
            eid = int(path.split("/")[3])
            self.send_json(calcular_stats(eid))

        elif path.startswith("/api/evaluaciones/") and "/respuestas" in path:
            eid = int(path.split("/")[3])
            with get_conn() as conn:
                rows = conn.execute(
                    "SELECT * FROM respuestas WHERE evaluacion_id = ?", (eid,)
                ).fetchall()
            self.send_json([dict(r) for r in rows])

        elif path == "/api/controles":
            self.send_json(CONTROLES)

        elif path == "/api/dominios":
            self.send_json(DOMINIOS)

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

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/evaluaciones":
            with get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO evaluaciones (nombre, empresa, alcance) VALUES (?,?,?)",
                    (body.get("nombre", "Sin nombre"), body.get("empresa", ""), body.get("alcance", "")),
                )
                eid = cur.lastrowid
            self.send_json({"id": eid})

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
                conn.execute(
                    "UPDATE evaluaciones SET actualizada=datetime('now') WHERE id=?", (eid,)
                )
            self.send_json({"ok": True})

        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        path = urlparse(self.path).path
        if path.startswith("/api/evaluaciones/"):
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
