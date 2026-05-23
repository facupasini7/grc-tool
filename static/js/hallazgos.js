/* ── Módulo de Hallazgos de Auditoría ─────────────────────────────── */

const TIPO_LABELS = {
  no_conformidad: "No Conformidad",
  observacion: "Observación",
  oportunidad: "Oportunidad",
};
const SEV_ICONS = { critica: "🔴", alta: "🟠", media: "🟡", baja: "🟢" };
const ESTADO_LABELS = {
  abierto: "Abierto",
  en_proceso: "En proceso",
  resuelto: "Resuelto",
  verificado: "Verificado",
};
const ESTADO_CLASS = {
  abierto: "estado-abierto",
  en_proceso: "estado-proceso",
  resuelto: "estado-resuelto",
  verificado: "estado-verificado",
};

// ── Cargar y renderizar hallazgos ────────────────────────────────────
async function cargarHallazgos(eid) {
  const todos = await fetch(`${API}/api/evaluaciones/${eid}/hallazgos`).then(r => r.json());

  const filtroEstado = document.getElementById("filtro-estado").value;
  const filtroSev    = document.getElementById("filtro-severidad").value;
  const hallazgos = todos.filter(h =>
    (!filtroEstado || h.estado === filtroEstado) &&
    (!filtroSev    || h.severidad === filtroSev)
  );

  // Counters
  const cnts = { abierto: 0, en_proceso: 0, resuelto: 0, verificado: 0 };
  todos.forEach(h => { if (cnts[h.estado] !== undefined) cnts[h.estado]++; });
  document.getElementById("hallazgos-counters").innerHTML = Object.entries(cnts).map(([e, n]) =>
    `<span class="counter-chip ${ESTADO_CLASS[e]}">${ESTADO_LABELS[e]}: <b>${n}</b></span>`
  ).join("");

  const cont = document.getElementById("lista-hallazgos");
  if (!hallazgos.length) {
    cont.innerHTML = `<div class="empty-state"><div class="empty-icon">${todos.length ? "🔍" : "✅"}</div>
      <div>${todos.length ? "Ningún hallazgo coincide con los filtros." : "No hay hallazgos registrados para esta evaluación."}</div></div>`;
    return;
  }

  cont.innerHTML = hallazgos.map(h => `
    <div class="hallazgo-card sev-${h.severidad}" data-hid="${h.id}">
      <div class="hallazgo-header">
        <div class="hallazgo-meta">
          <span class="badge-tipo">${TIPO_LABELS[h.tipo] || h.tipo}</span>
          <span class="badge-sev sev-${h.severidad}">${SEV_ICONS[h.severidad]} ${h.severidad.charAt(0).toUpperCase() + h.severidad.slice(1)}</span>
          <span class="badge-ctrl">${h.control_id}</span>
        </div>
        <div class="hallazgo-actions">
          <span class="estado-tag ${ESTADO_CLASS[h.estado]}">${ESTADO_LABELS[h.estado]}</span>
          <button class="btn-icon" onclick="editarHallazgo(${h.id})" title="Editar">✏️</button>
          <button class="btn-icon danger" onclick="eliminarHallazgo(${h.id})" title="Eliminar">🗑</button>
        </div>
      </div>
      <div class="hallazgo-titulo">${h.titulo}</div>
      <div class="hallazgo-desc">${h.descripcion}</div>
      ${h.responsable_nombre ? `
        <div class="hallazgo-footer">
          <span class="footer-item">👤 <b>${h.responsable_nombre}</b>${h.responsable_email ? ` &lt;${h.responsable_email}&gt;` : ""}</span>
          ${h.fecha_limite ? `<span class="footer-item">📅 Fecha límite: <b>${h.fecha_limite}</b></span>` : ""}
        </div>` : ""}
      ${h.plan_accion ? `
        <div class="plan-accion">
          <span class="plan-label">Plan de acción</span>
          <div class="plan-text">${h.plan_accion}</div>
        </div>` : ""}
      <div class="estado-row">
        ${Object.entries(ESTADO_LABELS).map(([val, lbl]) => `
          <button class="btn-estado ${h.estado === val ? "active-estado" : ""}"
            onclick="cambiarEstado(${h.id}, '${val}')">${lbl}</button>
        `).join("")}
      </div>
    </div>
  `).join("");
}

// ── Filtros ──────────────────────────────────────────────────────────
document.getElementById("filtro-estado").addEventListener("change", () => {
  if (evalActual) cargarHallazgos(evalActual.id);
});
document.getElementById("filtro-severidad").addEventListener("change", () => {
  if (evalActual) cargarHallazgos(evalActual.id);
});

// ── Ver hallazgos ─────────────────────────────────────────────────────
document.getElementById("btn-ver-hallazgos").addEventListener("click", () => {
  if (!evalActual) return;
  document.getElementById("hallazgos-empresa").textContent = evalActual.empresa;
  cargarHallazgos(evalActual.id);
  showView("hallazgos");
});
document.getElementById("btn-back-eval-h").addEventListener("click", () => showView("evaluacion"));

// ── Abrir modal nuevo/editar ──────────────────────────────────────────
function abrirModalHallazgo({ id, evalId, ctrlId, evId, tipo, severidad, titulo, descripcion,
  respNombre, respEmail, fecha, plan, estado, framework } = {}) {
  document.getElementById("h-id").value = id || "";
  document.getElementById("h-eval-id").value = evalId || evalActual?.id || "";
  document.getElementById("h-ctrl-id").value = ctrlId || "";
  document.getElementById("h-ev-id").value = evId || "";
  document.getElementById("h-control").value = ctrlId || "";
  document.getElementById("h-framework").value = framework || "ISO27001";
  document.getElementById("h-tipo").value = tipo || "no_conformidad";
  document.getElementById("h-severidad").value = severidad || "media";
  document.getElementById("h-estado").value = estado || "abierto";
  document.getElementById("h-titulo").value = titulo || "";
  document.getElementById("h-descripcion").value = descripcion || "";
  document.getElementById("h-resp-nombre").value = respNombre || "";
  document.getElementById("h-resp-email").value = respEmail || "";
  document.getElementById("h-fecha").value = fecha || "";
  document.getElementById("h-plan").value = plan || "";
  document.getElementById("modal-hallazgo-titulo").textContent = id ? "Editar Hallazgo" : "Nuevo Hallazgo";
  document.getElementById("modal-hallazgo").classList.remove("hidden");
}

document.getElementById("btn-cancel-hallazgo").addEventListener("click", () => {
  document.getElementById("modal-hallazgo").classList.add("hidden");
});

// ── Guardar hallazgo ──────────────────────────────────────────────────
document.getElementById("btn-save-hallazgo").addEventListener("click", async () => {
  const id = document.getElementById("h-id").value;
  const payload = {
    control_id:         document.getElementById("h-ctrl-id").value,
    framework:          document.getElementById("h-framework").value,
    evidencia_id:       document.getElementById("h-ev-id").value || null,
    tipo:               document.getElementById("h-tipo").value,
    severidad:          document.getElementById("h-severidad").value,
    titulo:             document.getElementById("h-titulo").value.trim(),
    descripcion:        document.getElementById("h-descripcion").value.trim(),
    responsable_nombre: document.getElementById("h-resp-nombre").value.trim(),
    responsable_email:  document.getElementById("h-resp-email").value.trim(),
    fecha_limite:       document.getElementById("h-fecha").value,
    plan_accion:        document.getElementById("h-plan").value.trim(),
    estado:             document.getElementById("h-estado").value,
  };
  if (!payload.titulo) { alert("El título es requerido."); return; }

  const eid = document.getElementById("h-eval-id").value;
  if (id) {
    await fetch(`${API}/api/hallazgos/${id}`, {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } else {
    await fetch(`${API}/api/evaluaciones/${eid}/hallazgos`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }
  document.getElementById("modal-hallazgo").classList.add("hidden");
  cargarHallazgos(parseInt(eid));
});

// ── Editar ────────────────────────────────────────────────────────────
async function editarHallazgo(hid) {
  const hallazgos = await fetch(`${API}/api/evaluaciones/${evalActual.id}/hallazgos`).then(r => r.json());
  const h = hallazgos.find(x => x.id === hid);
  if (!h) return;
  abrirModalHallazgo({
    id: h.id, evalId: h.evaluacion_id, ctrlId: h.control_id, evId: h.evidencia_id,
    tipo: h.tipo, severidad: h.severidad, titulo: h.titulo, descripcion: h.descripcion,
    respNombre: h.responsable_nombre, respEmail: h.responsable_email,
    fecha: h.fecha_limite, plan: h.plan_accion, estado: h.estado, framework: h.framework,
  });
}

// ── Cambiar estado rápido ─────────────────────────────────────────────
async function cambiarEstado(hid, nuevoEstado) {
  await fetch(`${API}/api/hallazgos/${hid}`, {
    method: "PUT", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ estado: nuevoEstado }),
  });
  cargarHallazgos(evalActual.id);
}

// ── Eliminar ──────────────────────────────────────────────────────────
async function eliminarHallazgo(hid) {
  if (!confirm("¿Eliminar este hallazgo? Esta acción no se puede deshacer.")) return;
  await fetch(`${API}/api/hallazgos/${hid}`, { method: "DELETE" });
  cargarHallazgos(evalActual.id);
}

// ── Crear hallazgo desde análisis IA (llamado por evidencias.js) ───────
function crearHallazgoDesdeIA(ctrlId, evId, sugerido) {
  abrirModalHallazgo({
    ctrlId, evId,
    tipo:        sugerido.tipo || "no_conformidad",
    severidad:   sugerido.severidad || "media",
    titulo:      sugerido.titulo || "",
    descripcion: sugerido.descripcion || "",
  });
}
