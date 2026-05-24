/* ── Módulo de Cobertura Multi-framework ────────────────────────────── */

let coberturaActual = null;
let fwActual = "A7777";

const FW_INFO = {
  A7777: { nombre: "BCRA A 7777",  icono: "🏦", color: "#3b82f6" },
  A7783: { nombre: "BCRA A 7783",  icono: "🏦", color: "#0891b2" },
  PCI:   { nombre: "PCI DSS v4.0", icono: "💳", color: "#8b5cf6" },
};

// ── Botón desde evaluación ──────────────────────────────────────────────
document.getElementById("btn-ver-cobertura").addEventListener("click", () => {
  if (!evalActual) return;
  document.getElementById("cobertura-empresa").textContent = evalActual.empresa;
  document.getElementById("cobertura-sin-eval").classList.add("hidden");
  document.getElementById("cobertura-contenido").classList.remove("hidden");
  showView("cobertura");
  renderFrameworkButtons();
  // Seleccionar el primer framework disponible (no ISO27001)
  const disponibles = fwsDisponibles();
  const primero = disponibles[0] || "A7777";
  fwActual = primero;
  cargarCobertura(fwActual);
});

function fwsDisponibles() {
  const fws = evalActual?._frameworks || ["ISO27001", "A7777", "A7783", "PCI"];
  return Object.keys(FW_INFO).filter(fw => fws.includes(fw));
}

function renderFrameworkButtons() {
  const disponibles = fwsDisponibles();
  const sel = document.querySelector(".fw-selector");
  if (!sel) return;

  if (disponibles.length === 0) {
    sel.innerHTML = `<span style="color:var(--text-secondary);font-size:13px;">
      Esta evaluación no incluye frameworks adicionales.</span>`;
    return;
  }

  sel.innerHTML = disponibles.map(fw => {
    const info = FW_INFO[fw];
    return `<button class="btn btn-fw${fw === fwActual ? " active" : ""}"
      data-fw="${fw}" onclick="seleccionarFramework('${fw}')">
      ${info.icono} ${info.nombre}
    </button>`;
  }).join("");
}

document.getElementById("btn-back-eval-cob").addEventListener("click", () => showView("evaluacion"));

// ── Activar desde nav sin evaluación ──────────────────────────────────
document.querySelector('[data-view="cobertura"]').addEventListener("click", () => {
  if (!evalActual) {
    document.getElementById("cobertura-sin-eval").classList.remove("hidden");
    document.getElementById("cobertura-contenido").classList.add("hidden");
  }
});

// ── Cargar datos de cobertura ──────────────────────────────────────────
async function cargarCobertura(fw) {
  if (!evalActual) return;
  fwActual = fw;

  const data = await fetch(`${API}/api/evaluaciones/${evalActual.id}/cobertura/${fw.toLowerCase()}`)
    .then(r => r.json())
    .catch(() => null);

  if (!data) return;
  coberturaActual = data;
  renderCobertura(data);
}

function seleccionarFramework(fw) {
  fwActual = fw;
  document.querySelectorAll(".btn-fw").forEach(b => b.classList.toggle("active", b.dataset.fw === fw));
  cargarCobertura(fw);
}

// ── Render principal ────────────────────────────────────────────────────
function renderCobertura(data) {
  renderResumen(data);
  renderDominios(data);
}

function madurezColor(m) {
  if (m >= 4) return "#22c55e";
  if (m >= 3) return "#84cc16";
  if (m >= 2) return "#f59e0b";
  if (m >  0) return "#ef4444";
  return "#94a3b8";
}

function madurezBarra(m, max = 5) {
  const pct = Math.round((m / max) * 100);
  const color = madurezColor(m);
  return `<div class="cob-bar-wrap">
    <div class="cob-bar" style="width:${pct}%;background:${color}"></div>
    <span class="cob-bar-val">${m > 0 ? m.toFixed(1) : "—"}</span>
  </div>`;
}

function renderResumen(data) {
  const totalCtrl = data.controles.length;
  const conCobertura = data.controles.filter(c => c.madurez_estimada > 0).length;
  const pctCobertura = totalCtrl ? Math.round((conCobertura / totalCtrl) * 100) : 0;

  const madAll = data.controles.filter(c => c.madurez_estimada > 0).map(c => c.madurez_estimada);
  const madGlobal = madAll.length ? (madAll.reduce((a, b) => a + b, 0) / madAll.length).toFixed(2) : "—";

  const criticos = data.controles.filter(c => c.madurez_estimada > 0 && c.madurez_estimada < 2).length;
  const fw = FW_INFO[data.framework] || { nombre: data.framework, icono: "📋" };

  document.getElementById("cobertura-resumen").innerHTML = `
    <div class="cob-resumen-header">
      <span class="fw-badge">${fw.icono} ${fw.nombre}</span>
      <span class="cob-subtitle">Cobertura estimada basada en madurez ISO 27001:2022</span>
    </div>
    <div class="cob-stats-row">
      <div class="cob-stat">
        <div class="cob-stat-val">${pctCobertura}%</div>
        <div class="cob-stat-lbl">Controles con cobertura</div>
      </div>
      <div class="cob-stat">
        <div class="cob-stat-val">${madGlobal}</div>
        <div class="cob-stat-lbl">Madurez promedio /5</div>
      </div>
      <div class="cob-stat">
        <div class="cob-stat-val">${conCobertura}/${totalCtrl}</div>
        <div class="cob-stat-lbl">Controles evaluados</div>
      </div>
      <div class="cob-stat cob-stat-warn">
        <div class="cob-stat-val">${criticos}</div>
        <div class="cob-stat-lbl">Brechas críticas (&lt;2)</div>
      </div>
    </div>`;
}

function renderDominios(data) {
  const cont = document.getElementById("cobertura-dominios");

  // Agrupar controles por dominio
  const porDominio = {};
  data.controles.forEach(c => {
    if (!porDominio[c.dominio]) porDominio[c.dominio] = [];
    porDominio[c.dominio].push(c);
  });

  cont.innerHTML = Object.entries(data.dominios).map(([domId, dom]) => {
    const ctrls = porDominio[domId] || [];
    const madProm = dom.madurez_promedio;

    return `
    <div class="cob-dominio">
      <div class="cob-dominio-header" onclick="toggleDominioCob('${domId}')">
        <div class="cob-dominio-info">
          <span class="cob-dominio-id">${domId}</span>
          <span class="cob-dominio-nombre">${dom.nombre}</span>
          <span class="cob-dominio-sub">${dom.con_cobertura}/${dom.total} controles cubiertos</span>
        </div>
        <div class="cob-dominio-right">
          ${madurezBarra(madProm)}
          <span class="cob-toggle" id="cob-arrow-${domId}">▸</span>
        </div>
      </div>
      <div id="cob-body-${domId}" class="cob-dominio-body hidden">
        <table class="cob-tabla">
          <thead>
            <tr>
              <th>ID</th>
              <th>Control</th>
              <th>Referencia</th>
              <th>Madurez estimada</th>
              <th>ISO cubiertos</th>
              <th>Evidencia requerida</th>
            </tr>
          </thead>
          <tbody>
            ${ctrls.map(c => {
              const evList = (c.evidencia_requerida || []);
              const evHtml = evList.length
                ? `<ul class="ev-req-list">${evList.map(e => `<li>${e}</li>`).join("")}</ul>`
                : `<span class="ev-req-empty">—</span>`;
              return `
            <tr class="${c.madurez_estimada === 0 ? 'cob-row-gap' : c.madurez_estimada < 2 ? 'cob-row-critica' : c.madurez_estimada < 3 ? 'cob-row-baja' : ''}">
              <td><span class="cob-ctrl-id">${c.id}</span></td>
              <td class="cob-ctrl-nombre">${c.nombre}</td>
              <td class="cob-referencia">${c.referencia}</td>
              <td>${madurezBarra(c.madurez_estimada)}</td>
              <td>
                <span class="cob-iso-count">${c.controles_iso_cubiertos}/${c.controles_iso_total}</span>
                <div class="cob-iso-tags">${c.iso_mapping.slice(0, 4).map(iso => `<span class="iso-tag">${iso}</span>`).join("")}${c.iso_mapping.length > 4 ? `<span class="iso-tag">+${c.iso_mapping.length - 4}</span>` : ""}</div>
              </td>
              <td class="ev-req-cell">
                <button class="btn-ev-req" onclick="toggleEvReq('${c.id}', this)" title="Ver documentos requeridos">
                  📋 Ver
                </button>
                <div id="evreq-${c.id}" class="ev-req-dropdown hidden">
                  ${evHtml}
                </div>
              </td>
            </tr>`;
            }).join("")}
          </tbody>
        </table>
      </div>
    </div>`;
  }).join("");
}

function toggleDominioCob(domId) {
  const body  = document.getElementById(`cob-body-${domId}`);
  const arrow = document.getElementById(`cob-arrow-${domId}`);
  if (!body) return;
  const open = body.classList.toggle("hidden");
  arrow.textContent = open ? "▸" : "▾";
}

// Cerrar cualquier dropdown abierto (excepto el que se está abriendo)
function cerrarDropdowns(exceptId) {
  document.querySelectorAll(".ev-req-dropdown:not(.hidden)").forEach(d => {
    if (d.id !== `evreq-${exceptId}`) {
      d.classList.add("hidden");
      const btn = document.querySelector(`[data-ev-btn="${d.id.replace('evreq-','')}"]`);
      if (btn) btn.textContent = "📋 Ver";
    }
  });
}

function toggleEvReq(ctrlId, btn) {
  const panel = document.getElementById(`evreq-${ctrlId}`);
  if (!panel) return;

  const estaAbierto = !panel.classList.contains("hidden");
  cerrarDropdowns(ctrlId);

  if (estaAbierto) {
    panel.classList.add("hidden");
    btn.textContent = "📋 Ver";
    return;
  }

  // Posicionar con position:fixed — inmune a overflow:hidden de ancestros
  const rect = btn.getBoundingClientRect();
  const vw = window.innerWidth;
  const vh = window.innerHeight;

  panel.classList.remove("hidden");          // mostrar para medir
  const pw = panel.offsetWidth;
  const ph = panel.offsetHeight;

  // Horizontal: alinear a la derecha del botón; si se sale, alinear a la izquierda
  let left = rect.right - pw;
  if (left < 8) left = rect.left;
  if (left + pw > vw - 8) left = vw - pw - 8;

  // Vertical: por defecto debajo del botón; si no cabe, encima
  let top = rect.bottom + 6;
  if (top + ph > vh - 8) top = rect.top - ph - 6;

  panel.style.left = `${left}px`;
  panel.style.top  = `${top}px`;
  btn.textContent = "📋 Ocultar";
  btn.dataset.evBtn = ctrlId;
}

// Cerrar dropdowns al hacer scroll o click fuera
document.addEventListener("scroll", () => cerrarDropdowns(null), true);
document.addEventListener("click", e => {
  if (!e.target.closest(".btn-ev-req") && !e.target.closest(".ev-req-dropdown")) {
    cerrarDropdowns(null);
    document.querySelectorAll(".btn-ev-req").forEach(b => {
      if (b.textContent.includes("Ocultar")) b.textContent = "📋 Ver";
    });
  }
});
