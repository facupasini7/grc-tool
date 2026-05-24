/* ── Audit Log ────────────────────────────────────────────────────── */

const AUDIT_ACCION_CSS = {
  login:                  "audit-login",
  login_fallido:          "audit-login_fallido",
  logout:                 "audit-logout",
  crear_evaluacion:       "audit-crear",
  eliminar_evaluacion:    "audit-eliminar",
  crear_hallazgo:         "audit-crear",
  eliminar_hallazgo:      "audit-eliminar",
  crear_usuario:          "audit-crear",
  subir_evidencia:        "audit-subir",
  analizar_ia:            "audit-analizar",
  cambiar_estado_hallazgo:"audit-cambiar",
};

const AUDIT_ACCION_LABEL = {
  login:                  "Login",
  login_fallido:          "Login fallido",
  logout:                 "Logout",
  crear_evaluacion:       "Crear evaluación",
  eliminar_evaluacion:    "Eliminar evaluación",
  crear_hallazgo:         "Crear hallazgo",
  eliminar_hallazgo:      "Eliminar hallazgo",
  crear_usuario:          "Crear usuario",
  subir_evidencia:        "Subir evidencia",
  analizar_ia:            "Analizar IA",
  cambiar_estado_hallazgo:"Cambiar estado",
};

let _auditRows = [];

async function cargarAuditLog() {
  const cont = document.getElementById("audit-log-tabla");
  cont.innerHTML = `<div class="empty-state" style="padding:24px">Cargando…</div>`;
  try {
    _auditRows = await fetch(`${API}/api/audit-log?limit=500`).then(r => {
      if (r.status === 403) throw new Error("forbidden");
      return r.json();
    });
    renderAuditLog(_auditRows);
    document.getElementById("audit-counter").textContent = `${_auditRows.length} registros`;
  } catch (err) {
    if (err.message === "forbidden") {
      cont.innerHTML = `<div class="empty-state">⛔ Tu rol no tiene acceso al log de auditoría.</div>`;
    } else {
      cont.innerHTML = `<div class="empty-state">Error al cargar el log.</div>`;
    }
  }
}

function renderAuditLog(rows) {
  const filtro = document.getElementById("audit-filtro-accion")?.value || "";
  const data   = filtro ? rows.filter(r => r.accion === filtro) : rows;

  document.getElementById("audit-counter").textContent = `${data.length} registros`;

  const cont = document.getElementById("audit-log-tabla");
  if (!data.length) {
    cont.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🕵️</div>
        <div>Sin registros de auditoría aún.</div>
      </div>`;
    return;
  }

  cont.innerHTML = `
    <table class="audit-table">
      <thead>
        <tr>
          <th>Fecha / Hora</th>
          <th>Usuario</th>
          <th>Rol</th>
          <th>Acción</th>
          <th>Entidad</th>
          <th>Detalle</th>
          <th>IP</th>
        </tr>
      </thead>
      <tbody>
        ${data.map(r => {
          const css   = AUDIT_ACCION_CSS[r.accion] || "audit-default";
          const label = AUDIT_ACCION_LABEL[r.accion] || r.accion;
          const ts    = r.timestamp ? r.timestamp.replace("T", " ").slice(0, 19) : "—";
          const entidad = r.entidad ? `${r.entidad}${r.entidad_id ? " #" + r.entidad_id : ""}` : "—";
          return `
            <tr>
              <td style="white-space:nowrap;font-family:monospace;font-size:11px">${esc(ts)}</td>
              <td style="font-weight:600">${esc(r.usuario_nombre || "—")}</td>
              <td style="color:var(--text-muted);font-size:11px">—</td>
              <td><span class="audit-accion ${css}">${esc(label)}</span></td>
              <td style="color:var(--text-muted);font-size:11px">${esc(entidad)}</td>
              <td style="max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${esc(r.detalle || '')}">${esc(r.detalle || "—")}</td>
              <td style="color:var(--text-muted);font-size:11px;font-family:monospace">${esc(r.ip || "—")}</td>
            </tr>`;
        }).join("")}
      </tbody>
    </table>`;
}

// Filtro por acción
document.addEventListener("DOMContentLoaded", () => {
  const sel = document.getElementById("audit-filtro-accion");
  if (sel) sel.addEventListener("change", () => renderAuditLog(_auditRows));

  document.getElementById("btn-refresh-audit")
    ?.addEventListener("click", cargarAuditLog);
});

// Cargar cuando se navega a auditoría
document.querySelectorAll(".nav-item").forEach(a => {
  if (a.dataset.view === "auditoria") {
    a.addEventListener("click", cargarAuditLog);
  }
});

function esc(str) {
  return String(str || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
