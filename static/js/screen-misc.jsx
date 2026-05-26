/* global React, Icon, Badge, Modal, KPI, Spinner, Empty, useApi,
          fmtDate, roleLabel, API */

const { useState: useStateMisc, useEffect: useEffectMisc, useRef: useRefMisc, useCallback: useCallbackMisc } = React;

// ── Auditoría ─────────────────────────────────────────────────────
const ACTION_META = {
  login:         { label:"Login",            tone:"info"    },
  login_fallido: { label:"Login fallido",    tone:"danger"  },
  logout:        { label:"Logout",           tone:"neutral" },
  crear:         { label:"Crear",            tone:"success" },
  eliminar:      { label:"Eliminar",         tone:"danger"  },
  subir:         { label:"Subir evidencia",  tone:"info"    },
  analizar:      { label:"Análisis IA",      tone:"accent"  },
  cambiar:       { label:"Cambio de estado", tone:"warning" },
};

function getActionMeta(accion) {
  const key = Object.keys(ACTION_META).find(k => (accion || "").startsWith(k));
  return ACTION_META[key] || { label: accion || "—", tone: "neutral" };
}

/* ── Exportar CSV / Excel ─────────────────────────── */
function exportLogs(rows, fmt) {
  const cols = [
    { key: "timestamp",      label: "Fecha y hora"  },
    { key: "usuario_nombre", label: "Usuario"       },
    { key: "accion",         label: "Acción"        },
    { key: "entidad_id",     label: "Entidad"       },
    { key: "detalle",        label: "Detalle"       },
    { key: "ip",             label: "IP"            },
  ];
  const escape = (v) => {
    const s = String(v == null ? "" : v).replace(/"/g, '""');
    return `"${s}"`;
  };
  const header = cols.map(c => escape(c.label)).join(",");
  const body   = rows.map(r => cols.map(c => escape(r[c.key] ?? "")).join(",")).join("\n");
  const csv    = header + "\n" + body;

  const ext  = fmt === "excel" ? "xls" : "csv";
  const mime = fmt === "excel" ? "application/vnd.ms-excel" : "text/csv";
  const bom  = "﻿"; // UTF-8 BOM so Excel opens it correctly
  const blob = new Blob([bom + csv], { type: mime + ";charset=utf-8" });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement("a");
  a.href     = url;
  a.download = `audit-log-${new Date().toISOString().slice(0,10)}.${ext}`;
  a.click();
  URL.revokeObjectURL(url);
}

/* ── Panel de filtros colapsable ──────────────────── */
function FilterPanel({ filters, onChange, onApply, onClear, logTotal }) {
  const [open, setOpen] = useStateMisc(false);

  const activeCount = [
    filters.accion && filters.accion !== "all",
    filters.usuario,
    filters.fecha_desde,
    filters.fecha_hasta,
  ].filter(Boolean).length;

  return (
    <div style={{ marginBottom: 12 }}>
      {/* ── Barra superior ── */}
      <div style={{ display:"flex", alignItems:"center", gap:8 }}>
        <button
          className={`btn btn-ghost btn-sm${open ? " active" : ""}`}
          style={{ gap:6, position:"relative" }}
          onClick={() => setOpen(o => !o)}
        >
          <Icon.Filter size={13}/>
          Filtros
          {activeCount > 0 && (
            <span style={{
              position:"absolute", top:-4, right:-4,
              width:16, height:16, borderRadius:"50%",
              background:"var(--accent)", color:"#fff",
              fontSize:9, fontWeight:700,
              display:"flex", alignItems:"center", justifyContent:"center",
            }}>{activeCount}</span>
          )}
          <Icon.ChevronDown size={12} style={{ marginLeft:2, transform: open ? "rotate(180deg)" : "none", transition:"transform .18s" }}/>
        </button>

        <div style={{ flex:1 }}/>
        <span style={{ fontSize:12, color:"var(--text-muted)" }}>{logTotal} eventos</span>

        {/* ── Exportar ── */}
        <ExportMenu onExport={(fmt) => onApply(fmt)}/>
      </div>

      {/* ── Panel expandible ── */}
      {open && (
        <div className="card" style={{ marginTop:8, padding:"16px 18px", display:"flex", flexDirection:"column", gap:14 }}>

          {/* Acción */}
          <div>
            <div style={{ fontSize:11, fontWeight:600, color:"var(--text-muted)", textTransform:"uppercase", letterSpacing:".05em", marginBottom:8 }}>Acción</div>
            <div style={{ display:"flex", flexWrap:"wrap", gap:6 }}>
              <button
                className={`filter-chip${filters.accion === "all" || !filters.accion ? " active" : ""}`}
                onClick={() => onChange("accion", "all")}
              >Todas</button>
              {Object.entries(ACTION_META).map(([key, meta]) => (
                <button
                  key={key}
                  className={`filter-chip${filters.accion === key ? " active" : ""}`}
                  onClick={() => onChange("accion", filters.accion === key ? "all" : key)}
                >
                  {meta.label}
                </button>
              ))}
            </div>
          </div>

          {/* Fecha + Usuario */}
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12 }}>
            <div className="field" style={{ marginBottom:0 }}>
              <label>Fecha desde</label>
              <input
                className="input"
                type="date"
                value={filters.fecha_desde || ""}
                onChange={e => onChange("fecha_desde", e.target.value)}
              />
            </div>
            <div className="field" style={{ marginBottom:0 }}>
              <label>Fecha hasta</label>
              <input
                className="input"
                type="date"
                value={filters.fecha_hasta || ""}
                onChange={e => onChange("fecha_hasta", e.target.value)}
              />
            </div>
            <div className="field" style={{ marginBottom:0 }}>
              <label>Usuario</label>
              <input
                className="input"
                type="text"
                placeholder="Nombre o username…"
                value={filters.usuario || ""}
                onChange={e => onChange("usuario", e.target.value)}
              />
            </div>
          </div>

          {/* Acciones del panel */}
          <div style={{ display:"flex", justifyContent:"flex-end", gap:8, paddingTop:4 }}>
            {activeCount > 0 && (
              <button className="btn btn-ghost btn-sm" onClick={onClear}>
                <Icon.X size={13}/> Limpiar filtros
              </button>
            )}
            <button className="btn btn-primary btn-sm" onClick={() => { onApply(); setOpen(false); }}>
              <Icon.Check size={13}/> Aplicar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Menú de exportación ──────────────────────────── */
function ExportMenu({ onExport }) {
  const [open, setOpen] = useStateMisc(false);
  const ref = useRefMisc(null);

  useEffectMisc(() => {
    if (!open) return;
    const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);

  return (
    <div ref={ref} style={{ position:"relative" }}>
      <button className="btn btn-ghost btn-sm" style={{ gap:6 }} onClick={() => setOpen(o => !o)}>
        <Icon.Download size={13}/> Exportar
        <Icon.ChevronDown size={12} style={{ transform: open ? "rotate(180deg)" : "none", transition:"transform .18s" }}/>
      </button>
      {open && (
        <div style={{
          position:"absolute", right:0, top:"calc(100% + 6px)", zIndex:200,
          background:"var(--surface-1)", border:"1px solid var(--border)",
          borderRadius:10, boxShadow:"0 8px 24px rgba(0,0,0,.12)",
          minWidth:160, padding:6, display:"flex", flexDirection:"column", gap:2,
        }}>
          {[
            { fmt:"csv",   icon:"FileText", label:"CSV (.csv)"       },
            { fmt:"excel", icon:"FileCheck",label:"Excel (.xls)"     },
          ].map(({ fmt, icon, label }) => (
            <button
              key={fmt}
              style={{
                display:"flex", alignItems:"center", gap:9,
                padding:"8px 12px", borderRadius:7, border:"none",
                background:"transparent", cursor:"pointer",
                fontSize:13, color:"var(--text-primary)", textAlign:"left",
                width:"100%",
              }}
              onMouseEnter={e => e.currentTarget.style.background = "var(--surface-2)"}
              onMouseLeave={e => e.currentTarget.style.background = "transparent"}
              onClick={() => { onExport(fmt); setOpen(false); }}
            >
              {React.createElement(Icon[icon] || Icon.FileText, { size:14, style:{ color:"var(--text-muted)", flexShrink:0 } })}
              {label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

/* ── Pantalla principal ───────────────────────────── */
function AuditoriaScreen() {
  const [filters, setFilters] = useStateMisc({
    accion: "all", usuario: "", fecha_desde: "", fecha_hasta: "",
  });
  // applied = what was sent to the server last time
  const [applied, setApplied] = useStateMisc({ accion: "all", usuario: "", fecha_desde: "", fecha_hasta: "" });
  const { data, loading, reload, error } = useApi(
    () => {
      const params = {};
      if (applied.accion && applied.accion !== "all") params.accion = applied.accion;
      if (applied.usuario)     params.usuario     = applied.usuario;
      if (applied.fecha_desde) params.fecha_desde = applied.fecha_desde;
      if (applied.fecha_hasta) params.fecha_hasta = applied.fecha_hasta;
      return API.auditLog(Object.keys(params).length ? params : null);
    },
    [applied]
  );

  const log = Array.isArray(data) ? data : (data?.log || []);

  const handleChange = useCallbackMisc((key, val) => {
    setFilters(prev => ({ ...prev, [key]: val }));
  }, []);

  const handleApply = useCallbackMisc((exportFmt) => {
    if (exportFmt === "csv" || exportFmt === "excel") {
      exportLogs(log, exportFmt);
      return;
    }
    setApplied({ ...filters });
  }, [filters, log]);

  const handleClear = useCallbackMisc(() => {
    const empty = { accion: "all", usuario: "", fecha_desde: "", fecha_hasta: "" };
    setFilters(empty);
    setApplied(empty);
  }, []);

  const activeCount = [
    applied.accion && applied.accion !== "all",
    applied.usuario,
    applied.fecha_desde,
    applied.fecha_hasta,
  ].filter(Boolean).length;

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Log de auditoría</div>
          <div className="page-sub">Registro inmutable de todas las acciones del sistema.</div>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost btn-sm" onClick={reload}>
            <Icon.Refresh size={14}/> Actualizar
          </button>
        </div>
      </div>

      <FilterPanel
        filters={filters}
        onChange={handleChange}
        onApply={handleApply}
        onClear={handleClear}
        logTotal={log.length}
      />

      {/* Chips de filtros activos */}
      {activeCount > 0 && (
        <div style={{ display:"flex", gap:6, flexWrap:"wrap", marginBottom:10 }}>
          {applied.accion && applied.accion !== "all" && (
            <span className="tag-mono" style={{ display:"flex", alignItems:"center", gap:5 }}>
              {ACTION_META[applied.accion]?.label || applied.accion}
              <Icon.X size={10} style={{ cursor:"pointer" }} onClick={() => { const f = {...filters, accion:"all"}; setFilters(f); setApplied(f); }}/>
            </span>
          )}
          {applied.usuario && (
            <span className="tag-mono" style={{ display:"flex", alignItems:"center", gap:5 }}>
              Usuario: {applied.usuario}
              <Icon.X size={10} style={{ cursor:"pointer" }} onClick={() => { const f = {...filters, usuario:""}; setFilters(f); setApplied(f); }}/>
            </span>
          )}
          {applied.fecha_desde && (
            <span className="tag-mono" style={{ display:"flex", alignItems:"center", gap:5 }}>
              Desde: {applied.fecha_desde}
              <Icon.X size={10} style={{ cursor:"pointer" }} onClick={() => { const f = {...filters, fecha_desde:""}; setFilters(f); setApplied(f); }}/>
            </span>
          )}
          {applied.fecha_hasta && (
            <span className="tag-mono" style={{ display:"flex", alignItems:"center", gap:5 }}>
              Hasta: {applied.fecha_hasta}
              <Icon.X size={10} style={{ cursor:"pointer" }} onClick={() => { const f = {...filters, fecha_hasta:""}; setFilters(f); setApplied(f); }}/>
            </span>
          )}
        </div>
      )}

      {loading ? <Spinner/> : error ? (
        <div className="card" style={{ padding:24, color:"var(--danger)", fontSize:13 }}>
          Error al cargar el log. <button className="btn btn-ghost btn-sm" onClick={reload}>Reintentar</button>
        </div>
      ) : (
        <div className="card tbl-card">
          <table className="tbl">
            <thead><tr>
              <th style={{ width:170 }}>Fecha y hora</th>
              <th style={{ width:150 }}>Usuario</th>
              <th style={{ width:160 }}>Acción</th>
              <th style={{ width:140 }}>Entidad</th>
              <th>Detalle</th>
              <th style={{ width:130 }}>IP</th>
            </tr></thead>
            <tbody>
              {log.map((l, i) => {
                const meta = getActionMeta(l.accion || l.action || "");
                const usr  = l.usuario_nombre || l.user || "—";
                return (
                  <tr key={i}>
                    <td>
                      <span className="mono" style={{ fontSize:11.5, color:"var(--text-secondary)" }}>
                        {l.timestamp || l.ts}
                      </span>
                    </td>
                    <td>
                      <div style={{ display:"flex", alignItems:"center", gap:7 }}>
                        <div style={{
                          width:22, height:22, borderRadius:"50%",
                          background:"var(--accent-soft)", color:"var(--accent)",
                          display:"flex", alignItems:"center", justifyContent:"center",
                          fontSize:9.5, fontWeight:700, flexShrink:0,
                        }}>
                          {usr.slice(0,2).toUpperCase()}
                        </div>
                        <span className="mono" style={{ fontSize:12, fontWeight:500 }}>{usr}</span>
                      </div>
                    </td>
                    <td><Badge tone={meta.tone}>{meta.label}</Badge></td>
                    <td>
                      <span className="mono" style={{ fontSize:11.5, color:"var(--text-secondary)" }}>
                        {l.entidad_id || l.target || "—"}
                      </span>
                    </td>
                    <td style={{ fontSize:12.5, color:"var(--text-secondary)" }}>
                      {l.detalle || l.details || ""}
                    </td>
                    <td>
                      <span className="mono" style={{ fontSize:11.5, color:"var(--text-faint)" }}>
                        {l.ip || "—"}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {log.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ textAlign:"center", padding:40, color:"var(--text-muted)", fontSize:13 }}>
                    <div style={{ marginBottom:8 }}><Icon.Inbox size={22} style={{ opacity:.35 }}/></div>
                    Sin eventos para los filtros seleccionados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Usuarios ──────────────────────────────────────────────────────
function UsuariosScreen() {
  const [modal,   setModal]   = useStateMisc(false);
  const [editing, setEditing] = useStateMisc(null);
  const { data, loading, reload } = useApi(() => API.usuarios(), []);

  const usuarios = data?.usuarios || data || [];
  const active   = usuarios.filter(u => u.activo);

  const roleTone = { admin:"danger", analista:"accent", auditor_externo:"success", auditado:"warning" };

  const open = (u) => { setEditing(u); setModal(true); };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Usuarios</div>
          <div className="page-sub">Administrá cuentas, roles y accesos al sistema.</div>
        </div>
        <div className="page-actions">
          <button className="btn btn-primary" onClick={() => open(null)}><Icon.Plus size={14}/> Nuevo usuario</button>
        </div>
      </div>

      <div className="kpi-grid" style={{ marginBottom:24 }}>
        <KPI label="Usuarios activos"       icon="Users"  value={active.length}/>
        <KPI label="Administradores"        icon="Key"    value={usuarios.filter(u=>u.rol==="admin").length}/>
        <KPI label="Auditores externos"     icon="Eye"    value={usuarios.filter(u=>u.rol==="auditor_externo").length}/>
        <KPI label="Pendientes aprobación"  icon="Clock"  value={usuarios.filter(u=>!u.aprobado).length}/>
      </div>

      {loading ? <Spinner/> : (
        <div className="card tbl-card">
          <table className="tbl">
            <thead><tr>
              <th>Usuario</th>
              <th style={{ width:200 }}>Email</th>
              <th style={{ width:150 }}>Rol</th>
              <th style={{ width:110 }}>Estado</th>
              <th style={{ width:180 }}>Último acceso</th>
              <th style={{ width:80 }}></th>
            </tr></thead>
            <tbody>
              {usuarios.map(u => {
                const initials = (u.nombre||u.username||"U").split(" ").map(w=>w[0]).join("").slice(0,2);
                return (
                  <tr key={u.id} className="clickable" onClick={() => open(u)}>
                    <td>
                      <div style={{ display:"flex", alignItems:"center", gap:10 }}>
                        <div style={{ width:30, height:30, borderRadius:"50%", background: u.activo ? "var(--accent)" : "var(--surface-3)", color:"#fff", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:700 }}>
                          {initials.toUpperCase()}
                        </div>
                        <div>
                          <div style={{ fontSize:13, fontWeight:600 }}>{u.nombre || u.username}</div>
                          <div style={{ fontSize:11.5, color:"var(--text-muted)" }} className="mono">@{u.username}</div>
                        </div>
                      </div>
                    </td>
                    <td style={{ fontSize:12.5, color:"var(--text-secondary)" }}>{u.email || "—"}</td>
                    <td><Badge tone={roleTone[u.rol]||"neutral"}>{roleLabel(u.rol)}</Badge></td>
                    <td>{u.activo ? <Badge tone="success" dot>Activo</Badge> : <Badge tone="neutral" dot>Inactivo</Badge>}</td>
                    <td><span className="mono" style={{ fontSize:11.5, color:"var(--text-muted)" }}>{u.ultimo_login ? fmtDate(u.ultimo_login) : "—"}</span></td>
                    <td onClick={e=>e.stopPropagation()}>
                      <button className="btn btn-ghost btn-icon"><Icon.MoreH size={14}/></button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <UsuarioModal open={modal} onClose={() => { setModal(false); reload(); }} editing={editing}/>
    </div>
  );
}

function UsuarioModal({ open, onClose, editing }) {
  const [nombre,   setNombre]   = useStateMisc(editing?.nombre || "");
  const [email,    setEmail]    = useStateMisc(editing?.email  || "");
  const [rol,      setRol]      = useStateMisc(editing?.rol    || "auditor_externo");
  const [pass,     setPass]     = useStateMisc("");
  const [activo,   setActivo]   = useStateMisc(editing?.activo !== 0);
  const [loading,  setLoading]  = useStateMisc(false);

  // Sync fields when editing changes
  useEffectMisc(() => {
    setNombre(editing?.nombre || ""); setEmail(editing?.email || "");
    setRol(editing?.rol || "auditor_externo"); setActivo(editing?.activo !== 0); setPass("");
  }, [editing]);

  const submit = async () => {
    setLoading(true);
    try {
      if (editing) {
        await API.actualizarUsuario(editing.id, { nombre, email, rol, activo: activo ? 1 : 0, ...(pass ? { password: pass } : {}) });
      } else {
        if (!nombre || !pass) return;
        await API.crearUsuario({ username: nombre.toLowerCase().replace(/\s+/g,"_"), nombre, email, rol, password: pass });
      }
      onClose();
    } catch { alert("Error al guardar usuario"); }
    finally { setLoading(false); }
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={editing ? "Editar usuario" : "Nuevo usuario"}
      sub={editing ? `Modificá los datos de ${editing.nombre}` : "Creá una cuenta nueva con su rol."}
      footer={<>
        <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={submit} disabled={loading}>{loading ? <Icon.Loader size={13}/> : "Guardar"}</button>
      </>}
    >
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="field"><label>Nombre completo</label><input className="input" value={nombre} onChange={e=>setNombre(e.target.value)} placeholder="María García"/></div>
        <div className="field"><label>Email</label><input className="input" type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="maria@empresa.com"/></div>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="field">
          <label>Rol</label>
          <select className="select" value={rol} onChange={e=>setRol(e.target.value)}>
            {["admin","analista","auditor_externo","auditado"].map(r => <option key={r} value={r}>{roleLabel(r)}</option>)}
          </select>
        </div>
        <div className="field"><label>{editing ? "Nueva contraseña (opcional)" : "Contraseña"}</label><input className="input" type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder={editing ? "Dejar vacío para no cambiar" : "Mínimo 8 caracteres"}/></div>
      </div>
      {editing && (
        <label style={{ display:"flex", alignItems:"center", gap:8, fontSize:13.5, cursor:"pointer" }}>
          <input type="checkbox" checked={activo} onChange={e=>setActivo(e.target.checked)} style={{ accentColor:"var(--accent)" }}/>
          Usuario activo
        </label>
      )}
    </Modal>
  );
}

// ── Settings ──────────────────────────────────────────────────────
function SettingsScreen({ user, onLogout }) {
  const [tab,       setTab]       = useStateMisc("perfil");
  const [oldPass,   setOldPass]   = useStateMisc("");
  const [newPass,   setNewPass]   = useStateMisc("");
  const [confirm,   setConfirm]   = useStateMisc("");
  const [msg,       setMsg]       = useStateMisc("");
  const [loading,   setLoading]   = useStateMisc(false);

  const changePass = async () => {
    if (newPass !== confirm) { setMsg("Las contraseñas no coinciden."); return; }
    if (newPass.length < 8)  { setMsg("Mínimo 8 caracteres."); return; }
    setLoading(true); setMsg("");
    try {
      const r = await API.changePass(oldPass, newPass);
      if (r.error) setMsg(r.error);
      else { setMsg("✓ Contraseña cambiada exitosamente."); setOldPass(""); setNewPass(""); setConfirm(""); }
    } catch { setMsg("Error al cambiar contraseña."); }
    finally { setLoading(false); }
  };

  return (
    <div className="page">
      <div className="page-head">
        <div><div className="page-title">Configuración</div><div className="page-sub">Ajustá tu perfil y preferencias de la cuenta.</div></div>
      </div>

      <div className="tabs" style={{ marginBottom:24 }}>
        {[["perfil","Perfil"],["seguridad","Seguridad"],["sistema","Sistema"]].map(([v,l]) => (
          <button key={v} className={`tab ${tab===v?"active":""}`} onClick={() => setTab(v)}>{l}</button>
        ))}
      </div>

      {tab === "perfil" && (
        <div className="card" style={{ padding:24, maxWidth:520 }}>
          <div style={{ display:"flex", alignItems:"center", gap:16, marginBottom:24, paddingBottom:20, borderBottom:"1px solid var(--border)" }}>
            <div style={{ width:56, height:56, borderRadius:"50%", background:"var(--accent)", color:"#fff", display:"flex", alignItems:"center", justifyContent:"center", fontSize:20, fontWeight:700 }}>
              {(user?.name || "U").split(" ").map(w=>w[0]).join("").slice(0,2)}
            </div>
            <div>
              <div style={{ fontSize:18, fontWeight:700 }}>{user?.name}</div>
              <div style={{ fontSize:13, color:"var(--text-muted)", marginTop:2 }}>{user?.role}</div>
            </div>
          </div>
          <div className="field"><label>Nombre completo</label><input className="input" defaultValue={user?.name || ""}/></div>
          <div className="field" style={{ marginTop:12 }}><label>Email</label><input className="input" type="email" defaultValue=""/></div>
          <button className="btn btn-primary" style={{ marginTop:20 }}>Guardar cambios</button>
        </div>
      )}

      {tab === "seguridad" && (
        <div className="card" style={{ padding:24, maxWidth:440 }}>
          <div style={{ fontWeight:700, fontSize:15, marginBottom:18 }}>Cambiar contraseña</div>
          {msg && <div style={{ padding:"10px 14px", borderRadius:8, marginBottom:14, fontSize:13, background: msg.startsWith("✓") ? "var(--success-soft)" : "var(--danger-soft)", color: msg.startsWith("✓") ? "var(--success)" : "var(--danger)", border:`1px solid ${msg.startsWith("✓") ? "var(--success-border)" : "var(--danger-border)"}` }}>{msg}</div>}
          <div className="field"><label>Contraseña actual</label><input className="input" type="password" value={oldPass} onChange={e=>setOldPass(e.target.value)}/></div>
          <div className="field" style={{ marginTop:12 }}><label>Nueva contraseña</label><input className="input" type="password" value={newPass} onChange={e=>setNewPass(e.target.value)} placeholder="Mínimo 8 caracteres"/></div>
          <div className="field" style={{ marginTop:12 }}><label>Confirmar nueva contraseña</label><input className="input" type="password" value={confirm} onChange={e=>setConfirm(e.target.value)}/></div>
          <button className="btn btn-primary" style={{ marginTop:20 }} onClick={changePass} disabled={loading}>{loading ? <Icon.Loader size={13}/> : "Cambiar contraseña"}</button>
        </div>
      )}

      {tab === "sistema" && (
        <FrameworksCard onLogout={onLogout} user={user}/>
      )}
    </div>
  );
}

/* ── FrameworksCard ───────────────────────────────────────────── */
function FrameworksCard({ onLogout, user }) {
  const { data: _catData } = useApi(() => API.frameworksCatalogo(), []);
  const catalogue = Array.isArray(_catData) ? _catData : [];
  const [manageFw, setManageFw] = useStateMisc(null); // {id, label} of fw being managed
  const isAdmin = user?.rol === "admin";

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:20, maxWidth:660 }}>
      <div className="card" style={{ padding:24 }}>
        <div style={{ fontWeight:700, fontSize:15, marginBottom:14 }}>Frameworks disponibles</div>
        {catalogue.length === 0 ? <Spinner/> : catalogue.map((fw, i) => {
          const FI = Icon[fw.icon] || Icon.Shield;
          return (
            <div key={fw.id} style={{ display:"flex", alignItems:"center", gap:12,
              padding:"12px 0", borderBottom: i < catalogue.length-1 ? "1px solid var(--border)" : "none" }}>
              <FI size={18} style={{ color:"var(--accent)", flexShrink:0 }}/>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontSize:13.5, fontWeight:600 }}>{fw.label}</div>
                <div style={{ fontSize:11.5, color:"var(--text-muted)" }}>
                  {fw.n} controles · <span style={{ color:"var(--text-faint)" }}>{fw.descripcion}</span>
                </div>
              </div>
              <span style={{ fontSize:11, color:"var(--success)", fontWeight:600,
                background:"var(--success-soft)", padding:"2px 8px", borderRadius:5, flexShrink:0 }}>Activo</span>
              {isAdmin && (
                <button className="btn btn-ghost btn-sm" style={{ flexShrink:0, marginLeft:4 }}
                  onClick={() => setManageFw(fw)}
                  title="Gestionar controles">
                  <Icon.Settings size={13}/> Gestionar
                </button>
              )}
            </div>
          );
        })}
        <div style={{ marginTop:20 }}>
          <button className="btn btn-danger" onClick={onLogout}><Icon.LogOut size={13}/> Cerrar sesión</button>
        </div>
      </div>
      <EmailConfigCard/>

      {manageFw && (
        <ControlesAdminModal fw={manageFw} onClose={() => setManageFw(null)}/>
      )}
    </div>
  );
}

/* ── ControlesAdminModal ──────────────────────────────────────── */
function ControlesAdminModal({ fw, onClose }) {
  const [q,       setQ]       = useStateMisc("");
  const [page,    setPage]    = useStateMisc(1);
  const [total,   setTotal]   = useStateMisc(0);
  const [items,   setItems]   = useStateMisc([]);
  const [loading, setLoading] = useStateMisc(true);
  const [editing, setEditing] = useStateMisc(null);  // control row being edited
  const [adding,  setAdding]  = useStateMisc(false);
  const PER_PAGE = 50;

  const load = useCallbackMisc(async () => {
    setLoading(true);
    try {
      const r = await API.adminControles(fw.id, { q, page, per_page: PER_PAGE });
      setItems(r.controles || []);
      setTotal(r.total || 0);
    } catch(e) { console.error(e); }
    finally { setLoading(false); }
  }, [fw.id, q, page]);

  useEffectMisc(() => { load(); }, [load]);

  const toggleActivo = async (ctrl) => {
    await API.adminEditarControl(fw.id, ctrl.id, { activo: ctrl.activo ? 0 : 1 });
    load();
  };

  const pages = Math.max(1, Math.ceil(total / PER_PAGE));

  return (
    <Modal open onClose={onClose} size="lg"
      title={`Controles — ${fw.label}`}
      sub={`${total} controles en total`}
      footer={
        <div style={{ display:"flex", justifyContent:"space-between", width:"100%", alignItems:"center" }}>
          <button className="btn btn-secondary" onClick={onClose}>Cerrar</button>
          <button className="btn btn-primary" onClick={() => setAdding(true)}>
            <Icon.Plus size={13}/> Agregar control
          </button>
        </div>
      }
    >
      {/* Search bar */}
      <div style={{ display:"flex", gap:8, marginBottom:14 }}>
        <div style={{ position:"relative", flex:1 }}>
          <Icon.Search size={13} style={{ position:"absolute", left:9, top:"50%", transform:"translateY(-50%)", color:"var(--text-muted)" }}/>
          <input className="input" style={{ paddingLeft:30, fontSize:13 }}
            placeholder="Buscar por ID, nombre o dominio…"
            value={q} onChange={e => { setQ(e.target.value); setPage(1); }}/>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={load} title="Recargar"><Icon.RefreshCw size={13}/></button>
      </div>

      {/* Table */}
      {loading ? <Spinner/> : items.length === 0 ? (
        <Empty icon="Inbox" title="Sin resultados" text="Probá otro término de búsqueda."/>
      ) : (
        <div style={{ overflowX:"auto" }}>
          <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12.5 }}>
            <thead>
              <tr style={{ background:"var(--surface-2)", textAlign:"left" }}>
                {["ID","Nombre","Dominio","Estado","Tipo","Acciones"].map(h => (
                  <th key={h} style={{ padding:"7px 10px", fontWeight:600, color:"var(--text-secondary)",
                    borderBottom:"1px solid var(--border)", whiteSpace:"nowrap" }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {items.map((c, i) => (
                <tr key={c.id} style={{
                  background: i%2===0 ? "transparent" : "var(--surface)",
                  opacity: c.activo ? 1 : 0.45,
                }}>
                  <td style={{ padding:"7px 10px", fontFamily:"var(--font-mono)", fontSize:11.5,
                    whiteSpace:"nowrap", color:"var(--accent)", fontWeight:600 }}>{c.id}</td>
                  <td style={{ padding:"7px 10px", maxWidth:280 }}>
                    <div style={{ fontWeight:500 }}>{c.nombre}</div>
                    {c.descripcion && <div style={{ fontSize:11, color:"var(--text-muted)",
                      overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap", maxWidth:260 }}>
                      {c.descripcion}
                    </div>}
                  </td>
                  <td style={{ padding:"7px 10px", whiteSpace:"nowrap", fontSize:11.5 }}>
                    {c.dominio_nombre || c.dominio || "—"}
                  </td>
                  <td style={{ padding:"7px 10px" }}>
                    <span style={{ fontSize:11, fontWeight:600, padding:"2px 7px", borderRadius:4,
                      color: c.activo ? "var(--success)" : "var(--text-muted)",
                      background: c.activo ? "var(--success-soft)" : "var(--surface-2)" }}>
                      {c.activo ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td style={{ padding:"7px 10px" }}>
                    <span style={{ fontSize:11, color: c.es_custom ? "var(--warning)" : "var(--text-faint)" }}>
                      {c.es_custom ? "Personalizado" : "Base"}
                    </span>
                  </td>
                  <td style={{ padding:"7px 10px", whiteSpace:"nowrap" }}>
                    <div style={{ display:"flex", gap:4 }}>
                      <button className="btn btn-ghost btn-icon" title="Editar"
                        onClick={() => setEditing({...c})}>
                        <Icon.Edit size={13}/>
                      </button>
                      <button className="btn btn-ghost btn-icon"
                        title={c.activo ? "Desactivar" : "Activar"}
                        onClick={() => toggleActivo(c)}>
                        {c.activo ? <Icon.EyeOff size={13}/> : <Icon.Eye size={13}/>}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {pages > 1 && (
        <div style={{ display:"flex", justifyContent:"center", gap:6, marginTop:14 }}>
          <button className="btn btn-ghost btn-sm" disabled={page<=1} onClick={() => setPage(p=>p-1)}>
            <Icon.ChevronLeft size={13}/>
          </button>
          <span style={{ fontSize:13, color:"var(--text-muted)", alignSelf:"center" }}>
            {page} / {pages}
          </span>
          <button className="btn btn-ghost btn-sm" disabled={page>=pages} onClick={() => setPage(p=>p+1)}>
            <Icon.ChevronRight size={13}/>
          </button>
        </div>
      )}

      {/* Edit modal */}
      {editing && (
        <ControlEditModal fw={fw} ctrl={editing} onClose={() => setEditing(null)} onSaved={() => { setEditing(null); load(); }}/>
      )}

      {/* Add modal */}
      {adding && (
        <ControlEditModal fw={fw} ctrl={null} onClose={() => setAdding(false)} onSaved={() => { setAdding(false); load(); }}/>
      )}
    </Modal>
  );
}

/* ── ControlEditModal ─────────────────────────────────────────── */
function ControlEditModal({ fw, ctrl, onClose, onSaved }) {
  const isNew = !ctrl;
  const [form,   setForm]   = useStateMisc(ctrl ? {...ctrl} : { id:"", nombre:"", descripcion:"", dominio:"", categoria:"" });
  const [saving, setSaving] = useStateMisc(false);
  const [err,    setErr]    = useStateMisc("");

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }));

  const save = async () => {
    setErr(""); setSaving(true);
    try {
      if (isNew) {
        await API.adminCrearControl(fw.id, form);
      } else {
        await API.adminEditarControl(fw.id, ctrl.id, {
          nombre:      form.nombre,
          descripcion: form.descripcion,
          dominio:     form.dominio,
          categoria:   form.categoria,
        });
      }
      onSaved();
    } catch(e) {
      setErr(e.message === "409" ? "Ya existe un control con ese ID." : "Error al guardar.");
    } finally { setSaving(false); }
  };

  return (
    <Modal open onClose={onClose}
      title={isNew ? "Agregar control" : `Editar ${ctrl.id}`}
      sub={fw.label}
      footer={
        <>
          <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
          <button className="btn btn-primary" onClick={save} disabled={saving || !form.nombre.trim()}>
            {saving ? <Icon.Loader size={13}/> : <Icon.Check size={13}/>}
            {isNew ? " Agregar" : " Guardar cambios"}
          </button>
        </>
      }
    >
      {err && <div style={{ color:"var(--danger)", fontSize:13, marginBottom:12 }}>{err}</div>}
      <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
        {isNew && (
          <div className="field">
            <label style={{ fontSize:12.5, fontWeight:600 }}>ID del control <span style={{color:"var(--danger)"}}>*</span></label>
            <input className="input" value={form.id} onChange={e => set("id", e.target.value)}
              placeholder="Ej: A.5.1.3 — debe ser único en este framework"
              style={{ fontFamily:"var(--font-mono)", fontSize:13 }}/>
          </div>
        )}
        <div className="field">
          <label style={{ fontSize:12.5, fontWeight:600 }}>Nombre <span style={{color:"var(--danger)"}}>*</span></label>
          <input className="input" value={form.nombre} onChange={e => set("nombre", e.target.value)}
            placeholder="Nombre del control o requisito"/>
        </div>
        <div className="field">
          <label style={{ fontSize:12.5, fontWeight:600 }}>Descripción</label>
          <textarea className="input" rows={3} value={form.descripcion}
            onChange={e => set("descripcion", e.target.value)}
            placeholder="Descripción o guía de implementación del control"
            style={{ resize:"vertical" }}/>
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
          <div className="field">
            <label style={{ fontSize:12.5, fontWeight:600 }}>Dominio</label>
            <input className="input" value={form.dominio} onChange={e => set("dominio", e.target.value)}
              placeholder="Ej: Organizacional"/>
          </div>
          <div className="field">
            <label style={{ fontSize:12.5, fontWeight:600 }}>Categoría</label>
            <input className="input" value={form.categoria} onChange={e => set("categoria", e.target.value)}
              placeholder="Categoría o subcategoría"/>
          </div>
        </div>
      </div>
    </Modal>
  );
}

/* ── EmailConfigCard ──────────────────────────────────────────── */
function EmailConfigCard() {
  const [cfg,     setCfg]     = useStateMisc({ smtp_host:"", smtp_port:"587", smtp_user:"", smtp_pass:"", smtp_from:"", base_url:"" });
  const [loading, setLoading] = useStateMisc(false);
  const [msg,     setMsg]     = useStateMisc("");
  const [testing, setTesting] = useStateMisc(false);

  useEffectMisc(() => {
    API.configSistema().then(d => {
      setCfg(prev => ({ ...prev, ...d }));
    }).catch(() => {});
  }, []);

  const set = (k, v) => setCfg(prev => ({ ...prev, [k]: v }));

  const save = async () => {
    setLoading(true); setMsg("");
    try {
      await API.guardarConfig(cfg);
      setMsg("✓ Configuración guardada.");
    } catch { setMsg("Error al guardar."); }
    finally { setLoading(false); }
  };

  const test = async () => {
    setTesting(true); setMsg("");
    try {
      const r = await API.enviarRecordatorios();
      setMsg(`✓ Chequeo ejecutado — enviados: ${r.sent}, errores: ${r.errors}`);
    } catch { setMsg("Error al ejecutar chequeo."); }
    finally { setTesting(false); }
  };

  return (
    <div className="card" style={{ padding:24 }}>
      <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:4 }}>
        <Icon.Mail size={16} style={{ color:"var(--accent)" }}/>
        <div style={{ fontWeight:700, fontSize:15 }}>Configuración de Email (SMTP)</div>
      </div>
      <div style={{ fontSize:12.5, color:"var(--text-muted)", marginBottom:18 }}>
        Requerido para enviar recordatorios automáticos de deadlines a los auditados.
      </div>

      {msg && (
        <div style={{ padding:"10px 14px", borderRadius:8, marginBottom:14, fontSize:13,
          background: msg.startsWith("✓") ? "var(--success-soft)" : "var(--danger-soft)",
          color: msg.startsWith("✓") ? "var(--success)" : "var(--danger)",
          border:`1px solid ${msg.startsWith("✓") ? "var(--success-border)" : "var(--danger-border)"}` }}>
          {msg}
        </div>
      )}

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="field">
          <label>SMTP Host</label>
          <input className="input" value={cfg.smtp_host} onChange={e => set("smtp_host", e.target.value)}
            placeholder="smtp.gmail.com"/>
        </div>
        <div className="field">
          <label>Puerto</label>
          <input className="input" value={cfg.smtp_port} onChange={e => set("smtp_port", e.target.value)}
            placeholder="587"/>
        </div>
        <div className="field">
          <label>Usuario SMTP</label>
          <input className="input" value={cfg.smtp_user} onChange={e => set("smtp_user", e.target.value)}
            placeholder="noreply@empresa.com"/>
        </div>
        <div className="field">
          <label>Contraseña / App Password</label>
          <input className="input" type="password" value={cfg.smtp_pass}
            onChange={e => set("smtp_pass", e.target.value)}
            placeholder="••••••••"/>
        </div>
        <div className="field">
          <label>Email remitente (From)</label>
          <input className="input" value={cfg.smtp_from} onChange={e => set("smtp_from", e.target.value)}
            placeholder="NormaLab &lt;noreply@empresa.com&gt;"/>
        </div>
        <div className="field">
          <label>URL base de la app</label>
          <input className="input" value={cfg.base_url} onChange={e => set("base_url", e.target.value)}
            placeholder="http://grc.empresa.com:8090"/>
        </div>
      </div>

      <div style={{ display:"flex", gap:8, marginTop:20 }}>
        <button className="btn btn-primary" onClick={save} disabled={loading}>
          {loading ? <Icon.Loader size={13}/> : <><Icon.Check size={13}/> Guardar configuración</>}
        </button>
        <button className="btn btn-ghost btn-sm" onClick={test} disabled={testing}>
          {testing ? <Icon.Loader size={13}/> : <><Icon.Mail size={13}/> Probar recordatorios</>}
        </button>
      </div>
    </div>
  );
}

// ── Modal de exportación de informes ──────────────────────────────────────

const REPORT_FRAMEWORKS = [
  { id:"ISO27001", label:"ISO/IEC 27001:2022"          },
  { id:"NIST_CSF",  label:"NIST CSF 2.0"               },
  { id:"SOC2",      label:"SOC 2 Type II"               },
  { id:"CIS",       label:"CIS Controls v8"             },
  { id:"A7777",     label:"ISO/IEC 27701:2019"          },
  { id:"BCRA",      label:"BCRA Com. A 7724"            },
  { id:"PCI",       label:"PCI DSS v4.0"                },
];

function InformeModal({ evalId, frameworks, onClose }) {
  const [tipo,     setTipo]     = useStateMisc("ejecutivo");
  const [fw,       setFw]       = useStateMisc(frameworks?.[0] || "ISO27001");
  const [loading,  setLoading]  = useStateMisc(false);

  // Filter to only frameworks used in this evaluation
  const fwOptions = frameworks?.length
    ? REPORT_FRAMEWORKS.filter(f => frameworks.includes(f.id))
    : REPORT_FRAMEWORKS;

  const handleDownload = () => {
    setLoading(true);
    const url = API.descargarInforme(evalId, tipo, fw);
    const a   = document.createElement("a");
    a.href    = url;
    a.target  = "_blank";
    a.rel     = "noopener";
    a.click();
    setTimeout(() => { setLoading(false); onClose(); }, 1200);
  };

  const tipoInfo = {
    ejecutivo: { icon:"FileText", title:"Informe Ejecutivo",
      desc:"Resumen de 2-3 páginas con KPIs, madurez por dominio, hallazgos críticos y top riesgos." },
    detallado: { icon:"FileText", title:"Informe Detallado",
      desc:"Documento completo con evaluación control por control, registro de brechas, hallazgos y riesgos." },
  };

  return (
    <Modal open={true} title="Exportar informe PDF" onClose={onClose} width={540}>
      {/* Tipo de informe */}
      <div style={{ display:"flex", flexDirection:"column", gap:8, marginBottom:20 }}>
        <label style={{ fontSize:12, fontWeight:600, color:"var(--text-secondary)" }}>Tipo de informe</label>
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
          {["ejecutivo","detallado"].map(t => {
            const info = tipoInfo[t];
            const Ic   = Icon[info.icon] || Icon.FileText;
            const sel  = tipo === t;
            return (
              <button
                key={t}
                type="button"
                onClick={() => setTipo(t)}
                style={{
                  display:"flex", flexDirection:"column", alignItems:"flex-start",
                  gap:6, padding:"14px 14px", borderRadius:10, border:"none", cursor:"pointer",
                  textAlign:"left",
                  background: sel ? "var(--accent-bg)" : "var(--surface-2)",
                  outline: sel ? "2px solid var(--accent)" : "1px solid var(--border)",
                  transition:"all .15s"
                }}
              >
                <div style={{ display:"flex", alignItems:"center", gap:6 }}>
                  <Ic size={15} style={{ color: sel ? "var(--accent)" : "var(--text-secondary)" }}/>
                  <span style={{ fontSize:13, fontWeight:700, color:"var(--text-primary)" }}>{info.title}</span>
                </div>
                <span style={{ fontSize:11, color:"var(--text-secondary)", lineHeight:1.4 }}>{info.desc}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Framework */}
      {fwOptions.length > 1 && (
        <div style={{ display:"flex", flexDirection:"column", gap:6, marginBottom:20 }}>
          <label style={{ fontSize:12, fontWeight:600, color:"var(--text-secondary)" }}>Framework / Norma</label>
          <select className="input" value={fw} onChange={e => setFw(e.target.value)}>
            {fwOptions.map(f => <option key={f.id} value={f.id}>{f.label}</option>)}
          </select>
        </div>
      )}

      {/* Info box */}
      <div style={{
        background:"var(--surface-2)", border:"1px solid var(--border)",
        borderRadius:8, padding:"10px 12px", marginBottom:20,
        display:"flex", gap:8, alignItems:"flex-start"
      }}>
        <Icon.Info size={14} style={{ color:"var(--accent)", flexShrink:0, marginTop:1 }}/>
        <p style={{ margin:0, fontSize:12, color:"var(--text-secondary)" }}>
          El PDF se generará con los datos actuales de la evaluación y se descargará automáticamente.
          Los informes quedan guardados en la carpeta <code>reports/</code> del servidor.
        </p>
      </div>

      <div style={{ display:"flex", justifyContent:"flex-end", gap:8 }}>
        <button className="btn btn-ghost" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={handleDownload} disabled={loading}>
          {loading
            ? <><Icon.Loader size={14}/> Generando…</>
            : <><Icon.Download size={14}/> Descargar PDF</>
          }
        </button>
      </div>
    </Modal>
  );
}

Object.assign(window, { AuditoriaScreen, UsuariosScreen, SettingsScreen, EmailConfigCard, InformeModal });
