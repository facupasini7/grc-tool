"""
Servicio de recordatorios por email para deadlines de evidencias.
Corre en un hilo de fondo — se dispara cada hora y envía notificaciones
a los auditados cuyo deadline está dentro de `recordatorio_dias` días.
"""
import os
import smtplib
import threading
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from database import get_conn


# ── SMTP helper ───────────────────────────────────────────────────────────────

def _smtp_cfg():
    return {
        "host":      os.environ.get("GRC_SMTP_HOST", ""),
        "port":      int(os.environ.get("GRC_SMTP_PORT", "587")),
        "user":      os.environ.get("GRC_SMTP_USER", ""),
        "password":  os.environ.get("GRC_SMTP_PASS", ""),
        "from_addr": os.environ.get("GRC_SMTP_FROM", os.environ.get("GRC_SMTP_USER", "")),
    }


def smtp_configured() -> bool:
    return bool(_smtp_cfg()["host"])


def send_email(to: str, subject: str, html: str, plain: str) -> bool:
    cfg = _smtp_cfg()
    if not cfg["host"] or not to:
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = cfg["from_addr"]
    msg["To"]      = to
    msg.attach(MIMEText(plain, "plain", "utf-8"))
    msg.attach(MIMEText(html,  "html",  "utf-8"))
    try:
        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            if cfg["user"]:
                smtp.login(cfg["user"], cfg["password"])
            smtp.sendmail(cfg["from_addr"], [to], msg.as_string())
        return True
    except Exception as e:
        print(f"[reminders] Error SMTP: {e}")
        return False


# ── Templates ─────────────────────────────────────────────────────────────────

def _reminder_html(nombre: str, control_nombre: str, evaluacion: str,
                   fecha_limite: str, dias: int, base_url: str) -> str:
    urgency = "🔴 URGENTE:" if dias <= 1 else ("🟡" if dias <= 3 else "🟢")
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"/></head>
<body style="font-family:system-ui,sans-serif;background:#f5f5f5;margin:0;padding:32px">
  <div style="max-width:560px;margin:0 auto;background:#fff;border-radius:12px;
               box-shadow:0 2px 8px rgba(0,0,0,.08);overflow:hidden">
    <div style="background:#0b1220;padding:24px 32px;display:flex;align-items:center;gap:12px">
      <span style="color:#7c6ef2;font-size:22px">🛡</span>
      <span style="color:#fff;font-weight:700;font-size:18px">Sentry GRC</span>
    </div>
    <div style="padding:32px">
      <p style="margin:0 0 8px;color:#666;font-size:14px">Recordatorio de vencimiento</p>
      <h2 style="margin:0 0 24px;font-size:22px;color:#111">
        {urgency} Evidencia requerida
      </h2>
      <p style="color:#444;line-height:1.6">
        Hola <strong>{nombre}</strong>,<br><br>
        Tenés pendiente la subida de evidencia para el siguiente control:
      </p>
      <div style="background:#f8f8ff;border:1px solid #e0deff;border-radius:8px;
                   padding:16px 20px;margin:20px 0">
        <div style="font-size:12px;color:#888;font-weight:600;
                     text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">
          Control
        </div>
        <div style="font-size:15px;font-weight:600;color:#222">{control_nombre}</div>
        <div style="font-size:12px;color:#888;margin-top:8px">
          Evaluación: <strong>{evaluacion}</strong>
        </div>
      </div>
      <table style="width:100%;border-collapse:collapse;margin:20px 0">
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #eee;
                      color:#666;font-size:13px">Fecha límite</td>
          <td style="padding:10px 0;border-bottom:1px solid #eee;
                      text-align:right;font-weight:600;color:#111">{fecha_limite}</td>
        </tr>
        <tr>
          <td style="padding:10px 0;color:#666;font-size:13px">Días restantes</td>
          <td style="padding:10px 0;text-align:right;font-weight:700;
                      color:{'#dc2626' if dias <= 1 else ('#d97706' if dias <= 3 else '#16a34a')}">
            {dias} {'día' if dias == 1 else 'días'}
          </td>
        </tr>
      </table>
      <a href="{base_url}" style="display:inline-block;background:#7c6ef2;color:#fff;
                                    padding:12px 24px;border-radius:8px;text-decoration:none;
                                    font-weight:600;font-size:14px;margin-top:8px">
        Ir a Sentry GRC →
      </a>
      <p style="color:#aaa;font-size:12px;margin-top:24px">
        Este es un recordatorio automático generado por Sentry GRC. No respondas este email.
      </p>
    </div>
  </div>
</body>
</html>"""


def _reminder_plain(nombre: str, control_nombre: str, evaluacion: str,
                    fecha_limite: str, dias: int, base_url: str) -> str:
    return (
        f"Hola {nombre},\n\n"
        f"Recordatorio: tenés pendiente la subida de evidencia para el control:\n"
        f"  {control_nombre}\n"
        f"  Evaluación: {evaluacion}\n"
        f"  Fecha límite: {fecha_limite}\n"
        f"  Días restantes: {dias}\n\n"
        f"Accedé a Sentry GRC para subir la evidencia:\n{base_url}\n\n"
        f"Este es un recordatorio automático. No respondas este email."
    )


# ── Lógica de chequeo ─────────────────────────────────────────────────────────

def check_and_send_reminders(base_url: str = "http://localhost:8090") -> dict:
    """
    Revisa la tabla deadlines_evidencia y envía recordatorios para los que:
    - Su fecha_limite está dentro de los próximos `recordatorio_dias` días
    - No fueron notificados aún (notificado = 0) O su ultima notificación fue hace >24h

    Retorna un dict con contadores: {checked, sent, errors}
    """
    if not smtp_configured():
        return {"checked": 0, "sent": 0, "errors": 0, "reason": "smtp_not_configured"}

    now   = datetime.now()
    stats = {"checked": 0, "sent": 0, "errors": 0}

    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                d.id, d.evaluacion_id, d.control_id,
                d.fecha_limite, d.recordatorio_dias, d.notificado,
                u.nombre AS usuario_nombre, u.email AS usuario_email,
                e.nombre AS evaluacion_nombre
            FROM deadlines_evidencia d
            JOIN usuarios u ON d.asignado_a = u.id
            JOIN evaluaciones e ON d.evaluacion_id = e.id
            WHERE u.activo = 1
              AND u.email != ''
              AND d.fecha_limite >= date('now')
        """).fetchall()

    for row in rows:
        row = dict(row)
        stats["checked"] += 1
        try:
            deadline = datetime.strptime(row["fecha_limite"], "%Y-%m-%d")
            dias_restantes = (deadline - now).days + 1  # inclusive

            if dias_restantes > row["recordatorio_dias"]:
                continue  # aún no es momento de recordar

            if dias_restantes < 0:
                continue  # ya venció

            # Buscar el nombre del control
            from data.controles_iso27001 import CONTROLES
            ctrl = next((c for c in CONTROLES if c["id"] == row["control_id"]), None)
            ctrl_nombre = ctrl["nombre"] if ctrl else row["control_id"]

            html  = _reminder_html(
                row["usuario_nombre"], ctrl_nombre, row["evaluacion_nombre"],
                row["fecha_limite"], dias_restantes, base_url
            )
            plain = _reminder_plain(
                row["usuario_nombre"], ctrl_nombre, row["evaluacion_nombre"],
                row["fecha_limite"], dias_restantes, base_url
            )
            subject = (
                f"[Sentry GRC] Recordatorio: {dias_restantes}d para subir evidencia — {ctrl_nombre[:40]}"
            )
            ok = send_email(row["usuario_email"], subject, html, plain)

            if ok:
                stats["sent"] += 1
                with get_conn() as conn:
                    conn.execute(
                        "UPDATE deadlines_evidencia SET notificado = notificado + 1 WHERE id = ?",
                        (row["id"],),
                    )
            else:
                stats["errors"] += 1

        except Exception as ex:
            print(f"[reminders] Error procesando deadline {row['id']}: {ex}")
            stats["errors"] += 1

    return stats


# ── Hilo de fondo ─────────────────────────────────────────────────────────────

_reminder_thread: threading.Thread | None = None
_stop_event = threading.Event()


def start_reminder_thread(base_url: str = "http://localhost:8090",
                          interval_seconds: int = 3600) -> None:
    """Inicia el hilo de recordatorios (solo una vez)."""
    global _reminder_thread
    if _reminder_thread and _reminder_thread.is_alive():
        return

    _stop_event.clear()

    def loop():
        print(f"[reminders] Hilo iniciado — intervalo {interval_seconds}s")
        while not _stop_event.is_set():
            try:
                result = check_and_send_reminders(base_url)
                if result.get("sent"):
                    print(f"[reminders] Enviados: {result['sent']}")
            except Exception as e:
                print(f"[reminders] Error en ciclo: {e}")
            _stop_event.wait(interval_seconds)

    _reminder_thread = threading.Thread(target=loop, daemon=True, name="reminder-worker")
    _reminder_thread.start()


def stop_reminder_thread() -> None:
    _stop_event.set()
