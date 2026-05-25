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
  renderUsuarios(usuarios);
}

function renderUsuarios(usuarios) {
  const cont = document.getElementById("tabla-usuarios");
  if (!cont) return;

  if (!usuarios.length) {
    cont.innerHTML = `<div class="empty-state"><div class="empty-icon">👥</div><div>No hay usuarios registrados.</div></div>`;
    return;
  }

  cont.innerHTML = `
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
                <button class="btn btn-outline btn-sm" onclick="abrirCambiarPassword(${u.id}, '${esc(u.nombre || u.username)}')">🔑 Contraseña</button>
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

// ── Cambiar contraseña ───────────────────────────────────────────────
function abrirCambiarPassword(uid, nombre) {
  const pw = prompt(`Nueva contraseña para ${nombre} (mínimo 8 caracteres):`);
  if (pw === null) return;
  if (pw.length < 8) { alert("La contraseña debe tener al menos 8 caracteres."); return; }
  fetch(`${API}/api/usuarios/${uid}/password`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: pw }),
  }).then(r => r.json()).then(r => {
    if (r.ok) alert("Contraseña actualizada correctamente.");
    else alert(`Error: ${r.error}`);
  });
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
      // Si puso contraseña nueva, la guardamos via endpoint dedicado
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
