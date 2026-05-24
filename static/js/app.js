/* ── GRC Tool — frontend ─────────────────────────────────────────── */

const API = "";
let evalActual  = null;
let controles   = [];
let dominios    = {};
let respuestas  = {};
let dominioActivo = null;
let chartRadar  = null;
let chartBar    = null;

// Copia de los controles ISO 27001 para restaurar al cambiar evaluación
let _iso27001Controles = [];
let _iso27001Dominios  = {};
let usuarioActual = null;

const MADUREZ_LABELS = ["Inexistente","Inicial","Repetible","Definido","Gestionado","Optimizado"];

// ── Helpers de rol ────────────────────────────────────────────────
const ROL_LABELS = {
  admin:          "Administrador",
  analista:       "Analista",
  auditor:        "Analista",        // alias legacy
  auditor_externo:"Auditor Externo",
};
const ROL_CSS = {
  admin:          "role-admin",
  analista:       "role-analista",
  auditor:        "role-analista",
  auditor_externo:"role-externo",
};

function puedeEscribir() {
  return ["admin", "analista", "auditor"].includes(usuarioActual?.rol);
}
function esAdmin() {
  return usuarioActual?.rol === "admin";
}
function esAuditorExterno() {
  return usuarioActual?.rol === "auditor_externo";
}

// ── Navegación ────────────────────────────────────────────────────
document.querySelectorAll(".nav-item").forEach(a => {
  a.addEventListener("click", e => {
    e.preventDefault();
    showView(a.dataset.view);
  });
});

function showView(name) {
  document.querySelectorAll(".view").forEach(v => v.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(a => a.classList.remove("active"));
  document.getElementById(`view-${name}`).classList.add("active");
  document.querySelector(`[data-view="${name}"]`).classList.add("active");
}

// ── Auth check + Init ─────────────────────────────────────────────
async function init() {
  // Verificar sesión activa
  const meResp = await fetch(`${API}/api/me`);
  if (meResp.status === 401) {
    window.location.href = "/login";
    return;
  }
  usuarioActual = await meResp.json();

  // Mostrar info de usuario en sidebar
  const el = document.getElementById("sidebar-username");
  const rl = document.getElementById("sidebar-role");
  if (el) el.textContent = usuarioActual.nombre || usuarioActual.username;
  if (rl) {
    rl.textContent  = ROL_LABELS[usuarioActual.rol] || usuarioActual.rol;
    rl.className    = `user-display-role ${ROL_CSS[usuarioActual.rol] || "role-default"}`;
  }

  // ── Navegación por rol ──
  // Auditoría: admin + auditor_externo
  const navAudit = document.getElementById("nav-auditoria");
  if (navAudit && !esAdmin() && !esAuditorExterno()) navAudit.style.display = "none";
  // Usuarios: solo admin
  const navUsuarios = document.getElementById("nav-usuarios");
  if (navUsuarios && esAdmin()) navUsuarios.classList.remove("hidden");

  // ── Acciones restringidas por rol ──
  // "Nueva evaluación" solo para quien puede escribir
  const btnNueva = document.getElementById("btn-nueva");
  if (btnNueva && !puedeEscribir()) btnNueva.style.display = "none";

  // Cargar controles ISO 27001 base
  [_iso27001Controles, _iso27001Dominios] = await Promise.all([
    fetch(`${API}/api/controles`).then(r => r.json()),
    fetch(`${API}/api/dominios`).then(r => r.json()),
  ]);
  controles = _iso27001Controles;
  dominios  = _iso27001Dominios;

  await cargarEvaluaciones();
}

async function logout() {
  await fetch(`${API}/api/logout`, { method: "POST" });
  window.location.href = "/login";
}

document.getElementById("btn-logout").addEventListener("click", logout);

// ── Home: lista de evaluaciones ───────────────────────────────────
async function cargarEvaluaciones() {
  const evs = await fetch(`${API}/api/evaluaciones`).then(r => r.json());
  const cont = document.getElementById("lista-evaluaciones");

  if (!evs.length) {
    cont.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📋</div>
        <div>No hay evaluaciones aún.</div>
        <div style="font-size:12px;margin-top:6px;">Creá una nueva para empezar.</div>
      </div>`;
    return;
  }

  const FW_LABELS = { ISO27001: "ISO 27001", A7777: "BCRA A 7777", A7783: "BCRA A 7783", PCI: "PCI DSS" };
  const FW_ICONS  = { ISO27001: "📋", A7777: "🏦", A7783: "🏦", PCI: "💳" };

  cont.innerHTML = `<div class="eval-list">${evs.map(e => {
    const fws = parseFws(e.frameworks);
    const badges = fws.map(fw =>
      `<span class="eval-fw-badge">${FW_ICONS[fw] || "📋"} ${FW_LABELS[fw] || fw}</span>`
    ).join("");
    return `
    <div class="eval-item" data-id="${e.id}">
      <div class="eval-info">
        <div class="eval-nombre">${e.nombre}</div>
        <div class="eval-meta">${e.empresa} · Actualizada: ${fmtDate(e.actualizada)}</div>
        <div class="eval-fw-badges">${badges}</div>
      </div>
      <div class="eval-actions">
        <button class="btn btn-primary btn-sm" onclick="abrirEval(${e.id}, event)">Continuar</button>
        <button class="btn btn-outline btn-sm" onclick="verStats(${e.id}, event)">Resultados</button>
        ${esAdmin() ? `<button class="btn btn-danger btn-sm" onclick="eliminarEval(${e.id}, event)">🗑</button>` : ""}
      </div>
    </div>`;
  }).join("")}</div>`;
}

function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso.replace(" ","T")+"Z");
  return d.toLocaleDateString("es-AR", { day:"2-digit", month:"2-digit", year:"numeric" });
}

function parseFws(raw) {
  try { return JSON.parse(raw || '["ISO27001"]'); }
  catch { return ["ISO27001"]; }
}

// ── Nueva evaluación ──────────────────────────────────────────────
// Framework cards en el modal
document.getElementById("fw-modal-grid").addEventListener("click", e => {
  const card = e.target.closest(".fw-modal-card");
  if (!card || card.classList.contains("locked")) return;
  card.classList.toggle("selected");
});

document.getElementById("btn-nueva").addEventListener("click", () => {
  // Resetear: deseleccionar todas, luego seleccionar ISO27001 por defecto
  document.querySelectorAll(".fw-modal-card").forEach(c => c.classList.remove("selected"));
  document.querySelector('.fw-modal-card[data-fw="ISO27001"]').classList.add("selected");
  document.getElementById("modal-nueva").classList.remove("hidden");
});
document.getElementById("btn-cancelar-modal").addEventListener("click", () => {
  document.getElementById("modal-nueva").classList.add("hidden");
});

document.getElementById("btn-crear").addEventListener("click", async () => {
  const nombre  = document.getElementById("inp-nombre").value.trim();
  const empresa = document.getElementById("inp-empresa").value.trim();
  const alcance = document.getElementById("inp-alcance").value.trim();
  if (!nombre || !empresa) { alert("Nombre y empresa son requeridos."); return; }

  // Recoger frameworks seleccionados (todos los que estén activos)
  const frameworks = [];
  document.querySelectorAll(".fw-modal-card.selected").forEach(c => {
    frameworks.push(c.dataset.fw);
  });
  if (frameworks.length === 0) {
    alert("Seleccioná al menos un framework para la evaluación.");
    return;
  }

  const { id } = await fetch(`${API}/api/evaluaciones`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, empresa, alcance, frameworks }),
  }).then(r => r.json());
  document.getElementById("modal-nueva").classList.add("hidden");
  document.getElementById("inp-nombre").value = "";
  document.getElementById("inp-empresa").value = "";
  document.getElementById("inp-alcance").value = "";
  await cargarEvaluaciones();
  abrirEval(id, null);
});

// ── Abrir evaluación ──────────────────────────────────────────────
async function abrirEval(id, e) {
  if (e) e.stopPropagation();
  const evals = await fetch(`${API}/api/evaluaciones`).then(r => r.json());
  evalActual = evals.find(ev => ev.id === id);
  if (!evalActual) return;

  evalActual._frameworks = parseFws(evalActual.frameworks);

  // ── Fix framework mapping: cargar los controles del framework activo ──
  // Si tiene ISO27001, evaluar siempre con ISO27001 (es la base de cobertura)
  // Si solo tiene normas BCRA/PCI, cargar los controles de esa norma directamente
  if (evalActual._frameworks.includes("ISO27001")) {
    controles = _iso27001Controles;
    dominios  = _iso27001Dominios;
  } else {
    const fw = evalActual._frameworks[0];
    const fwPath = { A7777: "a7777", A7783: "a7783", PCI: "pci" }[fw];
    if (fwPath) {
      [controles, dominios] = await Promise.all([
        fetch(`${API}/api/frameworks/${fwPath}/controles`).then(r => r.json()),
        fetch(`${API}/api/frameworks/${fwPath}/dominios`).then(r => r.json()),
      ]);
    }
  }

  const rows = await fetch(`${API}/api/evaluaciones/${id}/respuestas`).then(r => r.json());
  respuestas = {};
  rows.forEach(r => { respuestas[r.control_id] = r; });

  document.getElementById("eval-titulo").textContent = evalActual.nombre;
  document.getElementById("eval-empresa").textContent = evalActual.empresa;
  dominioActivo = null;
  renderTabs();
  actualizarProgreso();
  showView("evaluacion");
}

// ── Tabs de dominios ──────────────────────────────────────────────
function renderTabs() {
  const bar = document.getElementById("tab-bar");
  bar.innerHTML = Object.entries(dominios).map(([id, nombre]) => {
    const total = controles.filter(c => c.dominio === id).length;
    const resp = controles.filter(c => c.dominio === id && respuestas[c.id]?.madurez > 0).length;
    return `<button class="tab ${dominioActivo === id ? "active" : ""}" data-dom="${id}">
      ${id}<br><span class="tab-count">${nombre.split(" ").at(-1)} · ${resp}/${total}</span>
    </button>`;
  }).join("");

  bar.querySelectorAll(".tab").forEach(t => {
    t.addEventListener("click", () => {
      dominioActivo = t.dataset.dom;
      renderTabs();
      renderControles(dominioActivo);
    });
  });

  if (!dominioActivo) dominioActivo = Object.keys(dominios)[0];
  renderControles(dominioActivo);
}

// ── Controles del dominio ─────────────────────────────────────────
function renderControles(dominioId) {
  const panel = document.getElementById("controles-panel");
  const lista = controles.filter(c => c.dominio === dominioId);

  panel.innerHTML = `<div class="controles-list">${lista.map(c => {
    const resp = respuestas[c.id];
    const madurez = resp?.madurez ?? 0;
    const comentario = resp?.comentario ?? "";
    const aplica = resp?.aplica ?? 1;
    const cardClass = !aplica ? "" : madurez === 0 ? "" : madurez < 3 ? "gap" : "ok";

    const soloLectura = !puedeEscribir();

    return `
    <div class="control-card ${madurez > 0 ? (madurez < 3 ? "gap" : "ok") : ""}" id="card-${c.id}">
      <div class="control-header">
        <span class="control-id">${c.id}</span>
        <div class="control-info">
          <div class="control-nombre">${c.nombre}</div>
          <div class="control-desc">${c.descripcion}</div>
        </div>
      </div>
      <div class="control-body">
        <label class="aplica-toggle">
          <input type="checkbox" ${aplica ? "checked" : ""} data-ctrl="${c.id}" class="chk-aplica" ${soloLectura ? "disabled" : ""} />
          Aplica
        </label>
        <div class="madurez-selector" id="sel-${c.id}">
          ${[0,1,2,3,4,5].map(n => `
            <button class="nivel-btn ${madurez === n ? `sel-${n}` : ""}"
              data-ctrl="${c.id}" data-n="${n}" title="${MADUREZ_LABELS[n]}"
              ${soloLectura ? "disabled style=\"cursor:default;opacity:.7\"" : ""}>${n}</button>
          `).join("")}
        </div>
        <span class="nivel-label" id="lbl-${c.id}">${MADUREZ_LABELS[madurez]}</span>
        ${!soloLectura ? `<button class="btn-comment" data-ctrl="${c.id}">💬 Comentario</button>` : ""}
      </div>
      ${comentario ? `<div class="control-comment visible" id="cmt-${c.id}" style="padding:8px 12px;font-style:italic;font-size:12px;color:var(--text-muted)">${comentario}</div>` :
        (!soloLectura ? `<textarea class="control-comment" id="cmt-${c.id}" placeholder="Agregar comentario o evidencia..."></textarea>` : "")}
    </div>`;
  }).join("")}</div>`;

  if (puedeEscribir()) {
    // Madurez buttons
    panel.querySelectorAll(".nivel-btn").forEach(btn => {
      btn.addEventListener("click", () => guardarRespuesta(btn.dataset.ctrl, parseInt(btn.dataset.n)));
    });

    // Aplica checkbox
    panel.querySelectorAll(".chk-aplica").forEach(chk => {
      chk.addEventListener("change", () => {
        const ctrl = chk.dataset.ctrl;
        const r = respuestas[ctrl] || {};
        guardarRespuesta(ctrl, r.madurez || 0, r.comentario || "", chk.checked ? 1 : 0);
      });
    });

    // Comentario toggle
    panel.querySelectorAll(".btn-comment").forEach(btn => {
      btn.addEventListener("click", () => {
        const ta = document.getElementById(`cmt-${btn.dataset.ctrl}`);
        ta.classList.toggle("visible");
        if (ta.classList.contains("visible")) ta.focus();
      });
    });

    // Comentario blur → guardar
    panel.querySelectorAll("textarea.control-comment").forEach(ta => {
      const ctrlId = ta.id.replace("cmt-", "");
      ta.addEventListener("blur", () => {
        const r = respuestas[ctrlId] || {};
        guardarRespuesta(ctrlId, r.madurez || 0, ta.value, r.aplica ?? 1);
      });
    });
  }
}

// ── Guardar respuesta ─────────────────────────────────────────────
async function guardarRespuesta(ctrlId, madurez, comentario, aplica) {
  if (comentario === undefined) comentario = respuestas[ctrlId]?.comentario || "";
  if (aplica === undefined) aplica = respuestas[ctrlId]?.aplica ?? 1;

  await fetch(`${API}/api/evaluaciones/${evalActual.id}/respuestas`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ control_id: ctrlId, madurez, comentario, aplica }),
  });

  respuestas[ctrlId] = { control_id: ctrlId, madurez, comentario, aplica };

  // Actualizar botones visualmente
  const sel = document.getElementById(`sel-${ctrlId}`);
  if (sel) {
    sel.querySelectorAll(".nivel-btn").forEach(b => {
      b.className = `nivel-btn${parseInt(b.dataset.n) === madurez ? ` sel-${madurez}` : ""}`;
    });
  }
  const lbl = document.getElementById(`lbl-${ctrlId}`);
  if (lbl) lbl.textContent = MADUREZ_LABELS[madurez];

  // Color de la card
  const card = document.getElementById(`card-${ctrlId}`);
  if (card) {
    card.classList.remove("gap","ok");
    if (madurez > 0) card.classList.add(madurez < 3 ? "gap" : "ok");
  }

  actualizarProgreso();
  renderTabs(); // actualizar counters
}

function actualizarProgreso() {
  const aplicables = controles.filter(c => (respuestas[c.id]?.aplica ?? 1));
  const respondidos = aplicables.filter(c => respuestas[c.id]?.madurez > 0);
  const pct = aplicables.length ? Math.round(respondidos.length / aplicables.length * 100) : 0;
  document.getElementById("progreso-pct").textContent = `${pct}%`;
}

// ── Ver stats ─────────────────────────────────────────────────────
async function verStats(id, e) {
  if (e) e.stopPropagation();
  if (!evalActual || evalActual.id !== id) {
    await abrirEval(id, null);
  }
  const stats = await fetch(`${API}/api/evaluaciones/${evalActual.id}/stats`).then(r => r.json());
  renderStats(stats);
}

document.getElementById("btn-ver-stats").addEventListener("click", async () => {
  if (!evalActual) return;
  const stats = await fetch(`${API}/api/evaluaciones/${evalActual.id}/stats`).then(r => r.json());
  renderStats(stats);
});

document.getElementById("btn-back-eval").addEventListener("click", () => showView("evaluacion"));

function renderStats(stats) {
  document.getElementById("stats-titulo").textContent = evalActual.nombre;
  document.getElementById("stats-empresa").textContent = evalActual.empresa;
  document.getElementById("stat-madurez").textContent = stats.madurez_global;
  document.getElementById("stat-respondidos").textContent = `${stats.respondidos}/${stats.total}`;
  document.getElementById("stat-pct").textContent = `${stats.progreso_pct}%`;

  const totalBrechas = Object.values(stats.dominios).reduce((s, d) => s + d.brechas.length, 0);
  document.getElementById("stat-brechas").textContent = totalBrechas;

  showView("stats");
  renderCharts(stats);
  renderTablaBrechas(stats);
}

function renderCharts(stats) {
  const labels = Object.values(stats.dominios).map(d => d.nombre.split(" ").slice(0,2).join(" "));
  const madureces = Object.values(stats.dominios).map(d => d.promedio_madurez);

  // Radar
  if (chartRadar) chartRadar.destroy();
  chartRadar = new Chart(document.getElementById("chart-radar"), {
    type: "radar",
    data: {
      labels,
      datasets: [{
        label: "Madurez promedio",
        data: madureces,
        backgroundColor: "rgba(79,70,229,.15)",
        borderColor: "rgba(79,70,229,.8)",
        pointBackgroundColor: "rgba(79,70,229,1)",
        pointRadius: 4,
        borderWidth: 2,
      }]
    },
    options: {
      animation: false,
      scales: { r: { min: 0, max: 5, ticks: { stepSize: 1, font: { size: 11 } }, pointLabels: { font: { size: 11 } } } },
      plugins: { legend: { display: false } },
      maintainAspectRatio: true,
    }
  });

  // Bar — distribución por nivel de madurez
  const niveles = [0,1,2,3,4,5];
  const counts = niveles.map(n =>
    Object.keys(respuestas).filter(id => respuestas[id].madurez === n && respuestas[id].aplica).length
  );
  const barColors = ["#dc2626","#ea580c","#d97706","#ca8a04","#16a34a","#059669"];

  if (chartBar) chartBar.destroy();
  chartBar = new Chart(document.getElementById("chart-bar"), {
    type: "bar",
    data: {
      labels: MADUREZ_LABELS,
      datasets: [{
        label: "Controles",
        data: counts,
        backgroundColor: barColors,
        borderRadius: 6,
      }]
    },
    options: {
      animation: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
      maintainAspectRatio: true,
    }
  });
}

function renderTablaBrechas(stats) {
  const todas = [];
  Object.entries(stats.dominios).forEach(([dom, d]) => {
    d.brechas.forEach(b => todas.push({ ...b, dominio: dom }));
  });
  todas.sort((a, b) => a.madurez - b.madurez);

  const cont = document.getElementById("tabla-brechas");
  if (!todas.length) {
    cont.innerHTML = `<div class="empty-state"><div class="empty-icon">✅</div><div>¡Sin brechas críticas! Todos los controles evaluados tienen madurez ≥ 3.</div></div>`;
    return;
  }

  cont.innerHTML = `
    <table class="brechas-table">
      <thead><tr>
        <th>#</th><th>Control</th><th>Dominio</th><th>Madurez</th><th>Prioridad</th>
      </tr></thead>
      <tbody>${todas.map((b, i) => {
        const prioridad = b.madurez <= 1 ? "CRÍTICA" : b.madurez === 2 ? "ALTA" : "MEDIA";
        const badgeClass = b.madurez <= 1 ? "badge-critica" : b.madurez === 2 ? "badge-alta" : "badge-media";
        return `<tr>
          <td>${i+1}</td>
          <td><b>${b.id}</b> — ${b.nombre}</td>
          <td>${b.dominio}</td>
          <td><span class="madurez-pip"><span class="pip pip-${b.madurez}"></span>${b.madurez}/5 ${MADUREZ_LABELS[b.madurez]}</span></td>
          <td><span class="badge ${badgeClass}">${prioridad}</span></td>
        </tr>`;
      }).join("")}</tbody>
    </table>`;
}

// ── PDF ───────────────────────────────────────────────────────────
document.getElementById("btn-pdf").addEventListener("click", () => descargarPDF());
document.getElementById("btn-pdf-stats").addEventListener("click", () => descargarPDF());
document.getElementById("btn-ver-remediacion").addEventListener("click", () => {
  if (!evalActual) return;
  cargarRemediacion();
});
document.getElementById("btn-back-eval-rem").addEventListener("click", () => showView("evaluacion"));

function descargarPDF() {
  if (!evalActual) return;
  window.open(`${API}/api/report/${evalActual.id}`, "_blank");
}

// ── Eliminar ──────────────────────────────────────────────────────
async function eliminarEval(id, e) {
  e.stopPropagation();
  if (!confirm("¿Eliminar esta evaluación? Esta acción no se puede deshacer.")) return;
  await fetch(`${API}/api/evaluaciones/${id}`, { method: "DELETE" });
  if (evalActual?.id === id) evalActual = null;
  await cargarEvaluaciones();
}

// ── Start ─────────────────────────────────────────────────────────
init();
