/* ── Módulo de Evidencias con análisis IA ────────────────────────── */

const VEREDICTO_CONFIG = {
  cumple:     { icon: "✅", label: "Cumple",            cls: "v-cumple"  },
  parcial:    { icon: "⚠️", label: "Cumple parcialmente", cls: "v-parcial" },
  no_cumple:  { icon: "❌", label: "No cumple",          cls: "v-nocumple"},
  pendiente:  { icon: "⏳", label: "Pendiente",          cls: "v-pendiente"},
};

// ── Inyectar panel de evidencia en una control-card ──────────────────
async function cargarEvidenciasControl(ctrlId) {
  if (!evalActual) return;
  const rows = await fetch(
    `${API}/api/evaluaciones/${evalActual.id}/evidencias?control_id=${encodeURIComponent(ctrlId)}`
  ).then(r => r.json());

  const safeId = ctrlId.replace(/\./g, "_");
  const panel = document.getElementById(`ev-panel-${safeId}`);
  if (!panel) return;

  // Update count badge
  const countBadge = document.getElementById(`ev-count-${safeId}`);
  if (countBadge) countBadge.textContent = rows.length;

  if (!rows.length) {
    panel.innerHTML = `<div class="ev-empty">Sin evidencias cargadas.</div>`;
    return;
  }

  panel.innerHTML = rows.map(ev => {
    const cfg = VEREDICTO_CONFIG[ev.veredicto] || VEREDICTO_CONFIG.pendiente;
    let analisis = null;
    if (ev.analisis_ia) {
      try { analisis = JSON.parse(ev.analisis_ia); } catch(_) {}
    }
    return `
    <div class="ev-item" id="ev-${ev.id}">
      <div class="ev-header">
        <span class="ev-filename">📎 ${ev.filename}</span>
        <span class="ev-veredicto ${cfg.cls}">${cfg.icon} ${cfg.label}</span>
        <div class="ev-btns">
          ${puedeEscribir()
            ? (ev.veredicto === "pendiente" || !ev.analisis_ia
                ? `<button class="btn btn-sm btn-ai" onclick="analizarEvidencia(${ev.id}, '${ctrlId}')">🤖 Analizar</button>`
                : `<button class="btn btn-sm btn-outline" onclick="analizarEvidencia(${ev.id}, '${ctrlId}')">🔄 Re-analizar</button>`)
            : ""}
          ${esAdmin() ? `<button class="btn btn-sm btn-danger" onclick="eliminarEvidencia(${ev.id}, '${ctrlId}')">🗑</button>` : ""}
        </div>
      </div>
      ${analisis ? renderAnalisis(ev.id, analisis, ctrlId) : ""}
    </div>`;
  }).join("");
}

function renderAnalisis(evId, analisis, ctrlId) {
  const cfg = VEREDICTO_CONFIG[analisis.veredicto] || VEREDICTO_CONFIG.pendiente;
  const sug = analisis.hallazgo_sugerido;
  return `
  <div class="analisis-box ${cfg.cls}">
    <div class="analisis-resumen">${cfg.icon} <b>${analisis.resumen || ""}</b></div>
    ${analisis.fortalezas?.length ? `
      <div class="analisis-section">
        <span class="analisis-lbl">✅ Fortalezas</span>
        <ul>${analisis.fortalezas.map(f => `<li>${f}</li>`).join("")}</ul>
      </div>` : ""}
    ${analisis.brechas?.length ? `
      <div class="analisis-section">
        <span class="analisis-lbl">⚠️ Brechas</span>
        <ul>${analisis.brechas.map(b => `<li>${b}</li>`).join("")}</ul>
      </div>` : ""}
    ${analisis.recomendacion ? `
      <div class="analisis-section">
        <span class="analisis-lbl">💡 Recomendación</span>
        <p>${analisis.recomendacion}</p>
      </div>` : ""}
    ${sug?.aplica ? `
      <div class="hallazgo-sugerido">
        <span class="hs-label">⚠️ Hallazgo sugerido por IA</span>
        <div class="hs-titulo">${sug.titulo || ""}</div>
        ${puedeEscribir() ? `<button class="btn btn-warning btn-sm" onclick='crearHallazgoDesdeIA("${ctrlId}", ${evId}, ${JSON.stringify(sug).replace(/'/g, "&#39;")})'>
          + Crear hallazgo
        </button>` : ""}
      </div>` : ""}
  </div>`;
}

// ── Analizar evidencia con IA ─────────────────────────────────────────
async function analizarEvidencia(evId, ctrlId) {
  const btn = document.querySelector(`#ev-${evId} .btn-ai, #ev-${evId} .btn-outline`);
  if (btn) { btn.textContent = "🤖 Analizando..."; btn.disabled = true; }

  const resultado = await fetch(`${API}/api/evidencias/${evId}/analizar`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: "{}",
  }).then(r => r.json()).catch(() => ({ error: "Error de conexión" }));

  if (resultado.error && !resultado.veredicto) {
    alert(`Error: ${resultado.error}`);
    if (btn) { btn.textContent = "🤖 Analizar"; btn.disabled = false; }
    return;
  }
  await cargarEvidenciasControl(ctrlId);
}

// ── Eliminar evidencia ────────────────────────────────────────────────
async function eliminarEvidencia(evId, ctrlId) {
  if (!confirm("¿Eliminar esta evidencia?")) return;
  await fetch(`${API}/api/evidencias/${evId}`, { method: "DELETE" });
  cargarEvidenciasControl(ctrlId);
}

// ── Upload desde control-card ─────────────────────────────────────────
function setupUploadZone(ctrlId) {
  const safeId = ctrlId.replace(/\./g, "_");
  const zone = document.getElementById(`upload-zone-${safeId}`);
  const input = document.getElementById(`upload-input-${safeId}`);
  if (!zone || !input) return;

  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("drag-over"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", e => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    if (files.length) subirArchivo(files[0], ctrlId);
  });
  zone.addEventListener("click", () => input.click());
  input.addEventListener("change", () => {
    if (input.files.length) subirArchivo(input.files[0], ctrlId);
  });
}

async function subirArchivo(file, ctrlId) {
  const safeId = ctrlId.replace(/\./g, "_");
  const zone = document.getElementById(`upload-zone-${safeId}`);
  if (zone) zone.innerHTML = `<span class="uploading">⏳ Subiendo ${file.name}...</span>`;

  const reader = new FileReader();
  reader.onload = async (e) => {
    const b64 = e.target.result.split(",")[1];
    const resp = await fetch(`${API}/api/evaluaciones/${evalActual.id}/evidencias`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ control_id: ctrlId, filename: file.name, data: b64, framework: "ISO27001" }),
    }).then(r => r.json()).catch(() => ({ error: "Error de conexión" }));

    if (resp.error) {
      alert(resp.error);
    }
    // Restaurar zona de upload y recargar lista
    if (zone) {
      zone.innerHTML = `
        <div class="upload-zone-icon">📎</div>
        <span class="upload-hint">Arrastrá archivos aquí o hacé clic · PDF, DOCX, TXT, PNG, JPG</span>`;
    }
    await cargarEvidenciasControl(ctrlId);
  };
  reader.readAsDataURL(file);
}

// ── Patch renderControles para inyectar panel de evidencia ────────────
const _origRenderControles = window.renderControles;
window.renderControles = function renderControles(dominioId) {
  _origRenderControles(dominioId);
  // Después de que el DOM se actualiza, agregar paneles de evidencia
  const controlesDominio = controles.filter(c => c.dominio === dominioId);
  controlesDominio.forEach(c => {
    const safeId = c.id.replace(/\./g, "_");
    const card = document.getElementById(`card-${c.id}`);
    if (!card) return;

    // Inyectar zona de evidencia al final de la card
    const evDiv = document.createElement("div");
    evDiv.className = "evidencia-section";
    evDiv.innerHTML = `
      <div class="ev-toggle" onclick="toggleEvidencia('${c.id}')">
        <span>📎</span>
        <span class="ev-toggle-label">Evidencia</span>
        <span class="ev-toggle-count" id="ev-count-${safeId}">0</span>
        <span class="ev-toggle-arrow" id="ev-arrow-${safeId}">▸</span>
      </div>
      <div id="ev-body-${safeId}" class="ev-body hidden">
        ${puedeSubirEvidencia() ? `
        <div class="upload-zone" id="upload-zone-${safeId}">
          <div class="upload-zone-icon">📎</div>
          <span class="upload-hint">Arrastrá archivos aquí o hacé clic · PDF, DOCX, TXT, PNG, JPG</span>
          <input type="file" id="upload-input-${safeId}" class="upload-input" accept=".pdf,.docx,.doc,.txt,.md,.csv,.json,.xml,.png,.jpg,.jpeg,.webp,.gif,.bmp" />
        </div>` : ""}
        <div id="ev-panel-${safeId}" class="ev-panel"></div>
      </div>`;
    card.appendChild(evDiv);
    if (puedeSubirEvidencia()) setupUploadZone(c.id);
  });
}

function toggleEvidencia(ctrlId) {
  const safeId = ctrlId.replace(/\./g, "_");
  const body  = document.getElementById(`ev-body-${safeId}`);
  const arrow = document.getElementById(`ev-arrow-${safeId}`);
  if (!body) return;
  const isOpen = !body.classList.contains("hidden");
  body.classList.toggle("hidden", isOpen);
  if (arrow) {
    arrow.textContent = isOpen ? "▸" : "▾";
    arrow.classList.toggle("open", !isOpen);
  }
  if (!isOpen) cargarEvidenciasControl(ctrlId);
}
