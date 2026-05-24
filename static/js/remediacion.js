/* ── Plan de Remediación — Kanban ─────────────────────────────────── */

const ESTADO_CONFIG = {
  abierto:   { label: "Abierto",    icon: "🔴", cls: "kanban-col-abierto"   },
  en_proceso: { label: "En proceso", icon: "🟡", cls: "kanban-col-enproceso" },
  cerrado:   { label: "Cerrado",    icon: "✅", cls: "kanban-col-cerrado"   },
};

const SEV_LABEL = { critica: "🔴 Crítica", alta: "🟠 Alta", media: "🟡 Media", baja: "🟢 Baja" };
const TIPO_LABEL = {
  no_conformidad: "No Conformidad",
  observacion: "Observación",
  oportunidad: "Oportunidad",
};

async function cargarRemediacion() {
  if (!evalActual) return;

  document.getElementById("remediacion-empresa").textContent =
    `${evalActual.nombre} — ${evalActual.empresa}`;

  const hallazgos = await fetch(`${API}/api/evaluaciones/${evalActual.id}/hallazgos`)
    .then(r => r.json());

  renderRemStats(hallazgos);
  renderKanban(hallazgos);
  showView("remediacion");
}

function renderRemStats(hallazgos) {
  const total    = hallazgos.length;
  const criticos = hallazgos.filter(h => h.severidad === "critica").length;
  const abiertos = hallazgos.filter(h => h.estado === "abierto").length;
  const cerrados = hallazgos.filter(h => h.estado === "cerrado").length;

  document.getElementById("rem-stats").innerHTML = `
    <div class="rem-stat">
      <div class="rem-stat-val">${total}</div>
      <div class="rem-stat-lbl">Total hallazgos</div>
    </div>
    <div class="rem-stat rem-stat-red">
      <div class="rem-stat-val">${criticos}</div>
      <div class="rem-stat-lbl">Críticos</div>
    </div>
    <div class="rem-stat">
      <div class="rem-stat-val">${abiertos}</div>
      <div class="rem-stat-lbl">Abiertos</div>
    </div>
    <div class="rem-stat">
      <div class="rem-stat-val">${cerrados}</div>
      <div class="rem-stat-lbl">Cerrados</div>
    </div>
  `;
}

function renderKanban(hallazgos) {
  const board = document.getElementById("kanban-board");

  if (!hallazgos.length) {
    board.innerHTML = `
      <div class="rem-empty-state">
        <div style="font-size:40px;margin-bottom:12px">📋</div>
        <div style="font-weight:700;margin-bottom:6px">Sin hallazgos registrados</div>
        <div style="font-size:12px">Los hallazgos creados desde la sección Hallazgos aparecen aquí como plan de remediación.</div>
      </div>`;
    return;
  }

  const estados = ["abierto", "en_proceso", "cerrado"];
  const byEstado = {};
  estados.forEach(e => { byEstado[e] = []; });
  hallazgos.forEach(h => {
    const key = h.estado === "resuelto" || h.estado === "verificado" ? "cerrado" : h.estado;
    if (byEstado[key]) byEstado[key].push(h);
    else byEstado["abierto"].push(h);
  });

  board.innerHTML = estados.map(estado => {
    const cfg   = ESTADO_CONFIG[estado];
    const cards = byEstado[estado];
    return `
      <div class="kanban-col ${cfg.cls}">
        <div class="kanban-col-header">
          <span>${cfg.icon}</span>
          <span class="kanban-col-title">${cfg.label}</span>
          <span class="kanban-col-count">${cards.length}</span>
        </div>
        <div class="kanban-cards" id="kanban-col-${estado}">
          ${cards.length
            ? cards.map(h => renderKanbanCard(h, estado)).join("")
            : `<div class="kanban-empty">
                 <div class="kanban-empty-icon">✓</div>
                 Sin hallazgos en este estado
               </div>`
          }
        </div>
      </div>`;
  }).join("");
}

function renderKanbanCard(h, estadoCol) {
  const hoy     = new Date().toISOString().slice(0, 10);
  const vencida = h.fecha_limite && h.fecha_limite < hoy && estadoCol !== "cerrado";

  const accionBtn = estadoCol === "abierto"
    ? `<button class="btn-kanban btn-kanban-avanzar" onclick="avanzarEstado(${h.id}, 'en_proceso')">→ En proceso</button>`
    : estadoCol === "en_proceso"
    ? `<button class="btn-kanban btn-kanban-avanzar" onclick="avanzarEstado(${h.id}, 'cerrado')">✓ Cerrar</button>`
    : `<button class="btn-kanban btn-kanban-reabrir" onclick="avanzarEstado(${h.id}, 'abierto')">↩ Reabrir</button>`;

  return `
    <div class="kanban-card sev-${h.severidad}" id="kcard-${h.id}">
      <div class="kanban-card-title">${esc(h.titulo || "Sin título")}</div>
      <div class="kanban-card-meta">
        <span class="badge-sev sev-${h.severidad}">${SEV_LABEL[h.severidad] || h.severidad}</span>
        ${h.control_id ? `<span class="badge-ctrl">${esc(h.control_id)}</span>` : ""}
        ${h.tipo ? `<span class="badge-tipo">${TIPO_LABEL[h.tipo] || h.tipo}</span>` : ""}
      </div>
      <div class="kanban-card-footer">
        ${h.responsable_nombre
          ? `<div class="kanban-footer-item">👤 ${esc(h.responsable_nombre)}</div>`
          : ""}
        ${h.fecha_limite
          ? `<div class="kanban-footer-item ${vencida ? "kanban-date-vencida" : ""}">
               📅 ${h.fecha_limite}${vencida ? " ⚠️ Vencida" : ""}
             </div>`
          : ""}
        ${h.plan_accion
          ? `<div class="kanban-footer-item" style="color:var(--text);font-style:italic;font-size:11px">
               "${esc(h.plan_accion.slice(0, 60))}${h.plan_accion.length > 60 ? "…" : ""}"
             </div>`
          : ""}
      </div>
      <div class="kanban-actions">${accionBtn}</div>
    </div>`;
}

async function avanzarEstado(hallazgoId, nuevoEstado) {
  await fetch(`${API}/api/evaluaciones/${evalActual.id}/hallazgos/${hallazgoId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado: nuevoEstado }),
  });
  await cargarRemediacion();  // re-render
}

function esc(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
