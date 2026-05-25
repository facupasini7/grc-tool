/* ── Gestión de Usuarios (solo admin) ─────────────────────────────── */

const ROL_DISPLAY = {
  admin:          { label: "Administrador",  css: "role-admin"    },
  analista:       { label: "Analista",        css: "role-analista" },
  auditor:        { label: "Analista",        css: "role-analista" },  // alias legacy
  auditor_externo:{ label: "Auditor Externo", css: "role-externo"  },
  auditado:       { label: "Auditado",        css: "role-auditado" },
};

// ── Cargar y renderizar lista ────────────────────────────────────────
async function cargarUsuarios() {
  const resp = await fetch(`${API}/api/usuarios`);
  if (!resp.ok) return;
  const usuarios = await resp.json();

  const pendientes = usuarios.filter(u => !u.aprobado);
  const activos    = usuarios.filter(u => u.aprobado);

  const cont = document.getElementById("tabla-usuarios");
  if (!cont) return;

  // Banner de pendientes
  if (pendientes.length) {
    cont.innerHTML = `
      <div class="pending-banner">
        <span>⏳ ${pendientes.length} solicitud${pendientes.length > 1 ? "es" : ""} de registro pendiente${pendientes.length > 1 ? "s" : ""} de aprobación</span>
        <button class="btn btn-sm btn-primary" onclick="togglePendientes()">Ver pendientes</button>
      </div>
      <div id="tabla-pendientes" class="hidden"></div>`;
    renderPendientes(pendientes);
  } else {
    cont.innerHTML = "";
  }

  renderUsuarios(activos);
}

function togglePendientes() {
  const el = document.getElementById("tabla-pendientes");
  el?.classList.toggle("hidden");
}

function renderPendientes(usuarios) {
  const cont = document.getElementById("tabla-pendientes");
  if (!cont) return;
  cont.innerHTML = `
    <table class="usuarios-table" style="margin-bottom:20px">
      <thead><tr><th>Nombre</th><th>Usuario</th><th>Email</th><th>Solicitado</th><th>Acción</th></tr></thead>
      <tbody>${usuarios.map(u => `
        <tr>
          <td>${esc(u.nombre || "—")}</td>
          <td style="font-family:monospace;font-size:12px">${esc(u.username)}</td>
          <td style="font-size:12px">${esc(u.email || "—")}</td>
          <td style="font-size:12px;color:var(--text-muted)">${u.creado_en?.slice(0,16) || "—"}</td>
          <td>
            <div style="display:flex;gap:6px">
              <button class="btn btn-success btn-sm" onclick="aprobarUsuario(${u.id})">✅ Aprobar</button>
              <button class="btn btn-danger btn-sm" onclick="eliminarUsuario(${u.id}, '${esc(u.nombre || u.username)}')">🗑 Rechazar</button>
            </div>
          </td>
        </tr>`).join("")}
      </tbody>
    </table>`;
}

function renderUsuarios(usuarios) {
  const existing = document.getElementById("tabla-usuarios-list");
  const cont = existing || document.getElementById("tabla-usuarios");
  if (!cont) return;

  // Si ya existe el contenedor principal con pendientes, renderizar en un sub-div
  let target = document.getElementById("tabla-usuarios-list");
  if (!target) {
    const div = document.createElement("div");
    div.id = "tabla-usuarios-list";
    document.getElementById("tabla-usuarios").appendChild(div);
    target = div;
  }

  if (!usuarios.length) {
    target.innerHTML = `<div class="empty-state"><div class="empty-icon">👥</div><div>No hay usuarios aprobados.</div></div>`;
    return;
  }

  target.innerHTML = `
    <table class="usuarios-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Nombre</th>
          <th>Usuario</th>
          <th>Rol</th>
          <th>Estado</th>
          <th>Último acceso</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        ${usuarios.map(u => {
          const cfg = ROL_DISPLAY[u.rol] || { label: u.rol, css: "role-default" };
          const ultimo = u.ultimo_login
            ? u.ultimo_login.replace("T", " ").slice(0, 16)
            : "Nunca";
          const esMiCuenta = usuarioActual && usuarioActual.id === u.id;
          return `
          <tr>
            <td style="color:var(--text-muted);font-size:12px">${u.id}</td>
            <td style="font-weight:600">${esc(u.nombre || "—")}</td>
            <td style="font-family:monospace;font-size:12px">${esc(u.username)}</td>
            <td><span class="role-badge ${cfg.css}">${cfg.label}</span></td>
            <td>${u.activo
              ? `<span class="user-activo">● Activo</span>`
              : `<span class="user-inactivo">● Inactivo</span>`}
            </td>
            <td style="font-size:12px;color:var(--text-muted);font-family:monospace">${ultimo}</td>
            <td>
              <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button class="btn btn-outline btn-sm" onclick="abrirEditarUsuario(${u.id})">✏️ Editar</button>
                <button class="btn btn-outline btn-sm" onclick="generarResetLink(${u.id}, '${esc(u.nombre || u.username)}')">🔑 Reset pass</button>
                <button class="btn btn-outline btn-sm" onclick="abrirAsignacion(${u.id}, '${esc(u.nombre || u.username)}')">📋 Evaluaciones</button>
                ${!esMiCuenta ? `
                  <button class="btn btn-sm ${u.activo ? "btn-warning" : "btn-success"}"
                    onclick="toggleActivo(${u.id}, ${u.activo ? 0 : 1})">
                    ${u.activo ? "⏸ Desactivar" : "▶ Activar"}
                  </button>
                  <button class="btn btn-danger btn-sm" onclick="eliminarUsuario(${u.id}, '${esc(u.nombre || u.username)}')">🗑</button>
                ` : `<span style="font-size:11px;color:var(--text-muted)">(tu cuenta)</span>`}
              </div>
            </td>
          </tr>`;
        }).join("")}
      </tbody>
    </table>`;
}

// ── Abrir modal nuevo usuario ────────────────────────────────────────
document.getElementById("btn-nuevo-usuario")?.addEventListener("click", () => {
  document.getElementById("modal-usuario-titulo").textContent = "Nuevo usuario";
  document.getElementById("u-id").value       = "";
  document.getElementById("u-nombre").value   = "";
  document.getElementById("u-username").value = "";
  document.getElementById("u-password").value = "";
  document.getElementById("u-rol").value      = "analista";
  document.getElementById("u-username").disabled = false;
  document.getElementById("u-password").placeholder = "Mínimo 8 caracteres";
  document.getElementById("modal-usuario").classList.remove("hidden");
});

// ── Abrir modal editar usuario ───────────────────────────────────────
async function abrirEditarUsuario(uid) {
  const resp = await fetch(`${API}/api/usuarios`);
  const usuarios = await resp.json();
  const u = usuarios.find(x => x.id === uid);
  if (!u) return;

  document.getElementById("modal-usuario-titulo").textContent = "Editar usuario";
  document.getElementById("u-id").value       = u.id;
  document.getElementById("u-nombre").value   = u.nombre || "";
  document.getElementById("u-username").value = u.username;
  document.getElementById("u-password").value = "";
  document.getElementById("u-rol").value      = u.rol;
  document.getElementById("u-username").disabled = true; // no se puede cambiar el username
  document.getElementById("u-password").placeholder = "Dejá vacío para no cambiar";
  document.getElementById("modal-usuario").classList.remove("hidden");
}

// ── Aprobar usuario pendiente ────────────────────────────────────────
async function aprobarUsuario(uid) {
  const r = await fetch(`${API}/api/usuarios/${uid}/aprobar`, { method: "POST",
    headers: { "Content-Type": "application/json" }, body: "{}" }).then(res => res.json());
  if (r.ok) cargarUsuarios();
  else alert(`Error: ${r.error}`);
}

// ── Generar link de reset de contraseña ─────────────────────────────
async function generarResetLink(uid, nombre) {
  const r = await fetch(`${API}/api/usuarios/${uid}/reset-link`, { method: "POST",
    headers: { "Content-Type": "application/json" }, body: "{}" }).then(res => res.json());
  if (!r.ok) { alert(`Error: ${r.error}`); return; }
  if (r.email_sent) {
    alert(`✅ Email de recuperación enviado a ${nombre}.`);
  } else {
    const link = r.reset_url || "";
    // Mostrar modal con el link para copiar
    const modal = document.createElement("div");
    modal.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:9999";
    modal.innerHTML = `
      <div style="background:#fff;border-radius:12px;padding:28px;max-width:480px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,.3)">
        <h3 style="margin:0 0 8px;font-size:16px">🔑 Link de reset para ${esc(nombre)}</h3>
        <p style="font-size:13px;color:#64748b;margin:0 0 14px">
          No hay SMTP configurado. Enviá este link al usuario (válido 2 horas):
        </p>
        <input id="modal-reset-link" type="text" value="${esc(link)}" readonly
          style="width:100%;padding:8px;font-size:11px;font-family:monospace;border:1px solid #e2e8f0;border-radius:6px;background:#f8f9fa;margin-bottom:12px" />
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <button onclick="navigator.clipboard?.writeText('${link}');this.textContent='✅ Copiado'"
            class="btn btn-outline btn-sm">📋 Copiar</button>
          <button onclick="this.closest('[style*=fixed]').remove()" class="btn btn-secondary btn-sm">Cerrar</button>
        </div>
      </div>`;
    document.body.appendChild(modal);
    modal.querySelector("#modal-reset-link").select();
  }
}

// ── Asignar evaluaciones al usuario ─────────────────────────────────
async function abrirAsignacion(uid, nombre) {
  // Traer evaluaciones disponibles y las ya asignadas al usuario
  const [evals, asignadas] = await Promise.all([
    fetch(`${API}/api/evaluaciones`).then(r => r.json()),
    // Para saber qué evaluaciones tiene: iterar y ver asignados
    fetch(`${API}/api/usuarios`).then(r => r.json()).then(() => []),  // placeholder
  ]);

  // Buscar en cada eval si este usuario está asignado
  const asignadasIds = new Set();
  await Promise.all(evals.map(async ev => {
    const asigs = await fetch(`${API}/api/evaluaciones/${ev.id}/asignados`).then(r => r.json()).catch(() => []);
    if (asigs.some(u => u.id === uid)) asignadasIds.add(ev.id);
  }));

  const modal = document.createElement("div");
  modal.style.cssText = "position:fixed;inset:0;background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:9999;overflow-y:auto;padding:20px";
  modal.innerHTML = `
    <div style="background:#fff;border-radius:12px;padding:28px;max-width:520px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,.3)">
      <h3 style="margin:0 0 6px;font-size:16px">📋 Evaluaciones asignadas a ${esc(nombre)}</h3>
      <p style="font-size:13px;color:#64748b;margin:0 0 16px">Marcá las evaluaciones a las que este usuario puede acceder.</p>
      ${!evals.length ? `<div style="color:#64748b;font-size:13px">No hay evaluaciones creadas aún.</div>` :
        evals.map(ev => `
          <label style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #e2e8f0;cursor:pointer">
            <input type="checkbox" data-eid="${ev.id}" ${asignadasIds.has(ev.id) ? "checked" : ""}
              style="width:16px;height:16px;cursor:pointer" />
            <div>
              <div style="font-weight:600;font-size:13px">${esc(ev.nombre)}</div>
              <div style="font-size:11px;color:#64748b">${esc(ev.empresa)}</div>
            </div>
          </label>`).join("")}
      <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:20px">
        <button onclick="this.closest('[style*=fixed]').remove()" class="btn btn-secondary btn-sm">Cancelar</button>
        <button onclick="guardarAsignaciones(${uid}, this)" class="btn btn-primary btn-sm">Guardar</button>
      </div>
    </div>`;
  document.body.appendChild(modal);

  // Guardar estado inicial para comparar cambios
  modal._asignadasIds = asignadasIds;
  modal._uid = uid;
}

async function guardarAsignaciones(uid, btn) {
  const modal = btn.closest("[style*=fixed]");
  const checks = modal.querySelectorAll("input[type=checkbox]");
  const prevIds = modal._asignadasIds || new Set();
  const promises = [];

  checks.forEach(chk => {
    const eid = parseInt(chk.dataset.eid);
    if (chk.checked && !prevIds.has(eid)) {
      // Asignar
      promises.push(fetch(`${API}/api/evaluaciones/${eid}/asignados`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario_id: uid }),
      }));
    } else if (!chk.checked && prevIds.has(eid)) {
      // Desasignar
      promises.push(fetch(`${API}/api/evaluaciones/${eid}/asignados/${uid}`, { method: "DELETE" }));
    }
  });

  btn.disabled = true; btn.textContent = "Guardando…";
  await Promise.all(promises);
  modal.remove();
}

// ── Cancelar modal ───────────────────────────────────────────────────
document.getElementById("btn-cancel-usuario")?.addEventListener("click", () => {
  document.getElementById("modal-usuario").classList.add("hidden");
});

// ── Guardar usuario (crear o editar) ────────────────────────────────
document.getElementById("btn-save-usuario")?.addEventListener("click", async () => {
  const uid      = document.getElementById("u-id").value;
  const nombre   = document.getElementById("u-nombre").value.trim();
  const username = document.getElementById("u-username").value.trim();
  const password = document.getElementById("u-password").value;
  const rol      = document.getElementById("u-rol").value;

  if (!nombre) { alert("El nombre es requerido."); return; }

  if (!uid) {
    // Crear
    if (!username) { alert("El usuario (login) es requerido."); return; }
    if (password.length < 8) { alert("La contraseña debe tener al menos 8 caracteres."); return; }
    const r = await fetch(`${API}/api/usuarios`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre, username, password, rol }),
    }).then(res => res.json());
    if (r.error) { alert(`Error: ${r.error}`); return; }
  } else {
    // Editar
    const body = { nombre, rol };
    if (password && password.length >= 8) {
      // Si puso contraseña nueva, la guardamos via el endpoint de change-password
      await fetch(`${API}/api/usuarios/${uid}/password`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
    } else if (password && password.length < 8) {
      alert("La contraseña debe tener al menos 8 caracteres.");
      return;
    }
    const r = await fetch(`${API}/api/usuarios/${uid}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(res => res.json());
    if (r.error) { alert(`Error: ${r.error}`); return; }
  }

  document.getElementById("modal-usuario").classList.add("hidden");
  cargarUsuarios();
});

// ── Activar / desactivar ─────────────────────────────────────────────
async function toggleActivo(uid, nuevoActivo) {
  await fetch(`${API}/api/usuarios/${uid}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ activo: nuevoActivo }),
  });
  cargarUsuarios();
}

// ── Eliminar usuario ─────────────────────────────────────────────────
async function eliminarUsuario(uid, nombre) {
  if (!confirm(`¿Eliminar al usuario "${nombre}"? Esta acción no se puede deshacer.`)) return;
  const r = await fetch(`${API}/api/usuarios/${uid}`, { method: "DELETE" }).then(res => res.json());
  if (r.error) { alert(`Error: ${r.error}`); return; }
  cargarUsuarios();
}

// ── Helper de escape HTML ────────────────────────────────────────────
function esc(str) {
  return String(str || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// ── Cargar cuando se navega a "usuarios" ────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".nav-item").forEach(a => {
    if (a.dataset.view === "usuarios") {
      a.addEventListener("click", cargarUsuarios);
    }
  });
});
