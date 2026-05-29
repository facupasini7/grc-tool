/* global React, Icon, Badge, Modal, Spinner, Empty, useApi, fmtDate, API,
          UsuariosScreen, AuditoriaScreen */

const { useState: useStateSeg, useEffect: useEffectSeg, useCallback: useCallbackSeg } = React;

/* ── Helpers ─────────────────────────────────────────────────────── */
const ROLE_COLORS = ["#6366f1","#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899","#14b8a6"];

function ColorPicker({ value, onChange }) {
  return (
    <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
      {ROLE_COLORS.map(c => (
        <button
          key={c}
          type="button"
          onClick={() => onChange(c)}
          style={{
            width:28, height:28, borderRadius:6,
            background:c, border: value === c ? "3px solid var(--text-primary)" : "2px solid transparent",
            cursor:"pointer", flexShrink:0
          }}
        />
      ))}
      {/* custom hex */}
      <input
        type="color"
        value={value || "#6366f1"}
        onChange={e => onChange(e.target.value)}
        style={{ width:28, height:28, borderRadius:6, border:"none", cursor:"pointer", padding:0 }}
        title="Color personalizado"
      />
    </div>
  );
}

/* ── Catálogo de permisos agrupado ───────────────────────────────── */
function PermisosMatrix({ permisos, selected, onChange, readOnly }) {
  /* agrupar por categoría */
  const grupos = permisos.reduce((acc, p) => {
    (acc[p.categoria] = acc[p.categoria] || []).push(p);
    return acc;
  }, {});

  const toggle = (pid) => {
    if (readOnly) return;
    const next = selected.includes(pid)
      ? selected.filter(x => x !== pid)
      : [...selected, pid];
    onChange(next);
  };

  const toggleAll = (ids) => {
    if (readOnly) return;
    const allIn = ids.every(id => selected.includes(id));
    const next  = allIn
      ? selected.filter(x => !ids.includes(x))
      : [...new Set([...selected, ...ids])];
    onChange(next);
  };

  return (
    <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
      {Object.entries(grupos).map(([cat, items]) => {
        const ids   = items.map(p => p.id);
        const allIn = ids.every(id => selected.includes(id));
        return (
          <div key={cat}>
            {/* Categoría header */}
            <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
              <span style={{ fontSize:11, fontWeight:700, textTransform:"uppercase", letterSpacing:1, color:"var(--text-secondary)" }}>
                {cat}
              </span>
              {!readOnly && (
                <button
                  type="button"
                  className="btn btn-ghost btn-xs"
                  onClick={() => toggleAll(ids)}
                  style={{ fontSize:10, padding:"2px 6px" }}
                >
                  {allIn ? "Quitar todos" : "Seleccionar todos"}
                </button>
              )}
            </div>
            {/* Permisos */}
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:6 }}>
              {items.map(p => {
                const checked = selected.includes(p.id);
                return (
                  <label
                    key={p.id}
                    style={{
                      display:"flex", alignItems:"flex-start", gap:8, padding:"8px 10px",
                      borderRadius:8, cursor: readOnly ? "default" : "pointer",
                      background: checked ? "var(--accent-bg)" : "var(--surface-2)",
                      border:`1px solid ${checked ? "var(--accent)" : "var(--border)"}`,
                      transition:"all .15s"
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => toggle(p.id)}
                      disabled={readOnly}
                      style={{ marginTop:2, accentColor:"var(--accent)" }}
                    />
                    <div>
                      <div style={{ fontSize:13, fontWeight:600, color:"var(--text-primary)" }}>{p.label}</div>
                      <div style={{ fontSize:11, color:"var(--text-secondary)", marginTop:1 }}>{p.descripcion}</div>
                    </div>
                  </label>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ── Modal de creación / edición de rol ──────────────────────────── */
function RolModal({ rol, permisos, onClose, onSaved }) {
  const isNew  = !rol;
  const isSystem = rol?.es_sistema;

  const [nombre,    setNombre]    = useStateSeg(rol?.nombre    || "");
  const [desc,      setDesc]      = useStateSeg(rol?.descripcion || "");
  const [color,     setColor]     = useStateSeg(rol?.color     || "#6366f1");
  const [selected,  setSelected]  = useStateSeg(rol?.permisos  || []);
  const [saving,    setSaving]    = useStateSeg(false);
  const [error,     setError]     = useStateSeg("");
  const [tab,       setTab]       = useStateSeg("info");   // "info" | "permisos"

  const handleSave = async () => {
    if (!nombre.trim()) { setError("El nombre es obligatorio"); return; }
    setSaving(true); setError("");
    try {
      let savedId = rol?.id;
      if (isNew) {
        const r = await API.crearRol({ nombre: nombre.trim(), descripcion: desc.trim(), color });
        savedId = r.id;
      } else if (!isSystem) {
        await API.actualizarRol(rol.id, { nombre: nombre.trim(), descripcion: desc.trim(), color });
      }
      // Asignar permisos (siempre, incluso para roles sistema)
      await API.asignarPermisos(savedId, selected);
      onSaved();
    } catch (e) {
      setError(e.message || "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const permisoCount = selected.length;

  return (
    <Modal
      open={true}
      title={isNew ? "Nuevo rol" : `Editar: ${rol.nombre}`}
      onClose={onClose}
      width={720}
    >
      {/* Tabs */}
      <div style={{ display:"flex", gap:4, marginBottom:20, borderBottom:"1px solid var(--border)", paddingBottom:12 }}>
        {[["info","Información"], ["permisos",`Permisos (${permisoCount})`]].map(([id,lbl]) => (
          <button
            key={id}
            className={`btn btn-sm ${tab===id ? "btn-primary" : "btn-ghost"}`}
            onClick={() => setTab(id)}
          >{lbl}</button>
        ))}
      </div>

      {tab === "info" && (
        <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
          {/* Preview chip */}
          <div style={{ display:"flex", alignItems:"center", gap:12 }}>
            <span style={{
              display:"inline-flex", alignItems:"center", gap:6, padding:"4px 12px",
              borderRadius:20, fontWeight:700, fontSize:13,
              background: color + "22", color, border:`1px solid ${color}44`
            }}>
              <span style={{ width:8, height:8, borderRadius:"50%", background:color }}/>
              {nombre || "Nombre del rol"}
            </span>
            {isSystem && <Badge tone="accent">Sistema</Badge>}
          </div>

          <div style={{ display:"flex", flexDirection:"column", gap:4 }}>
            <label style={{ fontSize:12, fontWeight:600, color:"var(--text-secondary)" }}>Nombre *</label>
            <input
              className="input"
              value={nombre}
              onChange={e => setNombre(e.target.value)}
              disabled={isSystem}
              placeholder="ej. Seguridad de la Información"
            />
            {isSystem && (
              <span style={{ fontSize:11, color:"var(--text-secondary)" }}>
                Los roles del sistema no pueden renombrarse.
              </span>
            )}
          </div>

          <div style={{ display:"flex", flexDirection:"column", gap:4 }}>
            <label style={{ fontSize:12, fontWeight:600, color:"var(--text-secondary)" }}>Descripción</label>
            <textarea
              className="input"
              value={desc}
              onChange={e => setDesc(e.target.value)}
              disabled={isSystem}
              rows={2}
              placeholder="Breve descripción del propósito de este rol..."
              style={{ resize:"vertical" }}
            />
          </div>

          <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
            <label style={{ fontSize:12, fontWeight:600, color:"var(--text-secondary)" }}>Color</label>
            <ColorPicker value={color} onChange={setColor} />
          </div>
        </div>
      )}

      {tab === "permisos" && (
        <div style={{ maxHeight:420, overflowY:"auto", paddingRight:4 }}>
          <PermisosMatrix
            permisos={permisos}
            selected={selected}
            onChange={setSelected}
            readOnly={false}
          />
        </div>
      )}

      {error && (
        <div style={{ marginTop:12, padding:"8px 12px", borderRadius:8, background:"var(--danger-bg)", color:"var(--danger)", fontSize:13 }}>
          {error}
        </div>
      )}

      <div style={{ display:"flex", justifyContent:"flex-end", gap:8, marginTop:20 }}>
        <button className="btn btn-ghost" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? <Spinner size={14}/> : <Icon.Check size={14}/>}
          {saving ? "Guardando…" : "Guardar"}
        </button>
      </div>
    </Modal>
  );
}

/* ── Tarjeta de rol ──────────────────────────────────────────────── */
function RolCard({ rol, onEdit, onDelete }) {
  const isSystem = rol.es_sistema;
  const color    = rol.color || "#6366f1";

  return (
    <div style={{
      background:"var(--surface-1)",
      border:"1px solid var(--border)",
      borderLeft:`4px solid ${color}`,
      borderRadius:10, padding:"14px 16px",
      display:"flex", flexDirection:"column", gap:8
    }}>
      <div style={{ display:"flex", alignItems:"center", gap:8 }}>
        <span style={{
          fontWeight:700, fontSize:14, color:"var(--text-primary)", flex:1
        }}>
          {rol.nombre}
        </span>
        {isSystem
          ? <Badge tone="accent">Sistema</Badge>
          : <Badge tone="neutral">Custom</Badge>
        }
      </div>

      {rol.descripcion && (
        <p style={{ fontSize:12, color:"var(--text-secondary)", margin:0 }}>
          {rol.descripcion}
        </p>
      )}

      <div style={{ display:"flex", alignItems:"center", gap:12, fontSize:12, color:"var(--text-secondary)" }}>
        <span><Icon.Key size={12}/> {rol.permisos?.length ?? 0} permisos</span>
        <span><Icon.Users size={12}/> {rol.n_usuarios ?? 0} usuarios</span>
      </div>

      <div style={{ display:"flex", gap:6, marginTop:4 }}>
        <button className="btn btn-ghost btn-sm" onClick={() => onEdit(rol)} style={{ flex:1 }}>
          <Icon.Edit size={12}/> Editar
        </button>
        {!isSystem && (
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => onDelete(rol)}
            style={{ color:"var(--danger)" }}
            disabled={rol.n_usuarios > 0}
            title={rol.n_usuarios > 0 ? "Hay usuarios con este rol" : "Eliminar rol"}
          >
            <Icon.Trash size={12}/>
          </button>
        )}
      </div>
    </div>
  );
}

/* ── Pestaña: Roles y Permisos ───────────────────────────────────── */
function RolesTab() {
  const { data: roles,    loading: loadingRoles,   reload: reloadRoles }   = useApi(() => API.roles());
  const { data: permisos, loading: loadingPermisos }                        = useApi(() => API.permisoCatalogo());

  const [modalRol,  setModalRol]  = useStateSeg(null);   // null = cerrado, {} = nuevo, rol = editar
  const [showModal, setShowModal] = useStateSeg(false);
  const [delConfirm,setDelConfirm]= useStateSeg(null);
  const [deleting,  setDeleting]  = useStateSeg(false);
  const [search,    setSearch]    = useStateSeg("");

  const openNew  = () => { setModalRol(null); setShowModal(true); };
  const openEdit = (rol) => { setModalRol(rol); setShowModal(true); };
  const closeModal = () => { setShowModal(false); setModalRol(null); };

  const handleSaved = () => { closeModal(); reloadRoles(); };

  const handleDelete = async (rol) => {
    setDeleting(true);
    try {
      await API.eliminarRol(rol.id);
      reloadRoles();
    } catch (e) {
      alert(e.message || "Error al eliminar");
    } finally {
      setDeleting(false);
      setDelConfirm(null);
    }
  };

  const rolesFiltered = (roles || []).filter(r =>
    !search || r.nombre.toLowerCase().includes(search.toLowerCase())
  );

  /* cargar permisos del rol a editar */
  const rolConPermisos = (rol) => {
    if (!rol) return null;
    const found = (roles || []).find(r => r.id === rol.id);
    return found || rol;
  };

  if (loadingRoles || loadingPermisos) return (
    <div style={{ display:"flex", justifyContent:"center", padding:48 }}><Spinner/></div>
  );

  return (
    <div>
      {/* Header */}
      <div style={{ display:"flex", alignItems:"center", gap:12, marginBottom:20, flexWrap:"wrap" }}>
        <input
          className="input"
          placeholder="Buscar rol…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex:1, minWidth:160 }}
        />
        <button className="btn btn-primary btn-sm" onClick={openNew}>
          <Icon.Plus size={14}/> Nuevo rol
        </button>
      </div>

      {/* Info card */}
      <div style={{
        background:"var(--accent-bg)", border:"1px solid var(--accent)33",
        borderRadius:10, padding:"10px 14px", marginBottom:20,
        display:"flex", gap:10, alignItems:"flex-start"
      }}>
        <Icon.Info size={15} style={{ color:"var(--accent)", flexShrink:0, marginTop:1 }}/>
        <p style={{ margin:0, fontSize:13, color:"var(--text-secondary)" }}>
          Los <strong>roles del sistema</strong> no pueden eliminarse ni renombrarse, pero sí pueden
          tener sus permisos ajustados. Los <strong>roles custom</strong> se eliminan solo si no tienen
          usuarios asignados.
        </p>
      </div>

      {rolesFiltered.length === 0 ? (
        <Empty icon="Shield" title="No hay roles" subtitle="Crea un rol personalizado para comenzar"/>
      ) : (
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(280px, 1fr))", gap:14 }}>
          {rolesFiltered.map(rol => (
            <RolCard
              key={rol.id}
              rol={rol}
              onEdit={openEdit}
              onDelete={(r) => setDelConfirm(r)}
            />
          ))}
        </div>
      )}

      {/* Modal editar / crear */}
      {showModal && (
        <RolModal
          rol={rolConPermisos(modalRol)}
          permisos={permisos || []}
          onClose={closeModal}
          onSaved={handleSaved}
        />
      )}

      {/* Confirm delete */}
      {delConfirm && (
        <Modal
          open={true}
          title="Eliminar rol"
          onClose={() => setDelConfirm(null)}
          width={420}
        >
          <p style={{ fontSize:14, color:"var(--text-secondary)" }}>
            ¿Eliminar el rol <strong>{delConfirm.nombre}</strong>? Esta acción no se puede deshacer.
          </p>
          <div style={{ display:"flex", justifyContent:"flex-end", gap:8, marginTop:16 }}>
            <button className="btn btn-ghost" onClick={() => setDelConfirm(null)}>Cancelar</button>
            <button
              className="btn btn-danger"
              onClick={() => handleDelete(delConfirm)}
              disabled={deleting}
            >
              {deleting ? <Spinner size={14}/> : <Icon.Trash size={14}/>}
              Eliminar
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

/* ── Pestaña: Políticas de acceso ────────────────────────────────── */
function ToggleRow({ label, hint, checked, onChange }) {
  return (
    <label style={{
      display:"flex", alignItems:"center", gap:12, padding:"10px 12px",
      borderRadius:8, cursor:"pointer", background:"var(--surface-2)",
      border:"1px solid var(--border)"
    }}>
      <input type="checkbox" checked={!!checked} onChange={e => onChange(e.target.checked ? 1 : 0)}
             style={{ accentColor:"var(--accent)", width:16, height:16 }}/>
      <div style={{ flex:1 }}>
        <div style={{ fontSize:13, fontWeight:600, color:"var(--text-primary)" }}>{label}</div>
        {hint && <div style={{ fontSize:11, color:"var(--text-secondary)", marginTop:1 }}>{hint}</div>}
      </div>
    </label>
  );
}

function NumberRow({ label, hint, value, onChange, min = 0, max = 999, suffix }) {
  return (
    <div style={{
      display:"flex", alignItems:"center", gap:12, padding:"10px 12px",
      borderRadius:8, background:"var(--surface-2)", border:"1px solid var(--border)"
    }}>
      <div style={{ flex:1 }}>
        <div style={{ fontSize:13, fontWeight:600, color:"var(--text-primary)" }}>{label}</div>
        {hint && <div style={{ fontSize:11, color:"var(--text-secondary)", marginTop:1 }}>{hint}</div>}
      </div>
      <input
        type="number" className="input" value={value} min={min} max={max}
        onChange={e => onChange(Math.max(min, Math.min(max, parseInt(e.target.value || "0", 10))))}
        style={{ width:90, textAlign:"center" }}
      />
      {suffix && <span style={{ fontSize:12, color:"var(--text-secondary)", width:54 }}>{suffix}</span>}
    </div>
  );
}

function PoliticasTab() {
  const { data, loading, reload } = useApi(() => API.configSeguridad());
  const [cfg,    setCfg]    = useStateSeg(null);
  const [saving, setSaving] = useStateSeg(false);
  const [msg,    setMsg]    = useStateSeg("");

  useEffectSeg(() => { if (data) setCfg({ ...data }); }, [data]);

  const set = (k) => (v) => setCfg(c => ({ ...c, [k]: v }));

  const handleSave = async () => {
    setSaving(true); setMsg("");
    try {
      const r = await API.guardarConfigSeguridad(cfg);
      if (r.config) setCfg({ ...r.config });
      setMsg("ok");
      reload();
      setTimeout(() => setMsg(""), 2500);
    } catch (e) {
      setMsg("err");
    } finally {
      setSaving(false);
    }
  };

  if (loading || !cfg) return (
    <div style={{ display:"flex", justifyContent:"center", padding:48 }}><Spinner/></div>
  );

  const Section = ({ icon, title, children }) => {
    const Ic = Icon[icon];
    return (
      <div style={{ marginBottom:24 }}>
        <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
          {Ic && <Ic size={15} style={{ color:"var(--accent)" }}/>}
          <span style={{ fontSize:12, fontWeight:700, textTransform:"uppercase", letterSpacing:1, color:"var(--text-secondary)" }}>{title}</span>
        </div>
        <div style={{ display:"flex", flexDirection:"column", gap:8 }}>{children}</div>
      </div>
    );
  };

  return (
    <div style={{ maxWidth:680 }}>
      <Section icon="Key" title="Requisitos de contraseña">
        <NumberRow label="Longitud mínima" hint="Caracteres requeridos en toda contraseña nueva."
                   value={cfg.seg_pwd_min_len} onChange={set("seg_pwd_min_len")} min={4} max={128} suffix="caract." />
        <ToggleRow label="Exigir mayúscula"  hint="Al menos una letra A–Z." checked={cfg.seg_pwd_mayus}   onChange={set("seg_pwd_mayus")} />
        <ToggleRow label="Exigir minúscula"  hint="Al menos una letra a–z." checked={cfg.seg_pwd_minus}   onChange={set("seg_pwd_minus")} />
        <ToggleRow label="Exigir número"     hint="Al menos un dígito 0–9." checked={cfg.seg_pwd_numero}  onChange={set("seg_pwd_numero")} />
        <ToggleRow label="Exigir símbolo"    hint="Al menos un carácter especial." checked={cfg.seg_pwd_simbolo} onChange={set("seg_pwd_simbolo")} />
        <NumberRow label="Vencimiento de contraseña" hint="Fuerza el cambio tras N días. 0 = nunca vence."
                   value={cfg.seg_pwd_expira_dias} onChange={set("seg_pwd_expira_dias")} min={0} max={3650} suffix="días" />
      </Section>

      <Section icon="Lock" title="Bloqueo de cuenta">
        <NumberRow label="Intentos antes de bloquear" hint="Logins fallidos consecutivos permitidos. 0 = sin bloqueo."
                   value={cfg.seg_max_intentos} onChange={set("seg_max_intentos")} min={0} max={20} suffix="intentos" />
        <NumberRow label="Duración del bloqueo" hint="Tiempo que la cuenta queda bloqueada."
                   value={cfg.seg_bloqueo_min} onChange={set("seg_bloqueo_min")} min={1} max={1440} suffix="min" />
      </Section>

      <Section icon="Clock" title="Sesión">
        <NumberRow label="Cierre por inactividad" hint="Cierra la sesión tras N minutos sin actividad. 0 = desactivado."
                   value={cfg.seg_inactividad_min} onChange={set("seg_inactividad_min")} min={0} max={1440} suffix="min" />
      </Section>

      <div style={{ display:"flex", alignItems:"center", gap:12, marginTop:8 }}>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? <Spinner size={14}/> : <Icon.Check size={14}/>}
          {saving ? "Guardando…" : "Guardar políticas"}
        </button>
        {msg === "ok"  && <span style={{ fontSize:13, color:"var(--success)" }}><Icon.Check size={13}/> Políticas guardadas</span>}
        {msg === "err" && <span style={{ fontSize:13, color:"var(--danger)" }}>Error al guardar</span>}
      </div>
    </div>
  );
}

/* ── Pantalla principal: Seguridad ───────────────────────────────── */
function SeguridadScreen({ user }) {
  const [tab, setTab] = useStateSeg("usuarios");

  const tabs = [
    { id:"usuarios",  label:"Usuarios",         icon:"Users"       },
    { id:"roles",     label:"Roles y Permisos", icon:"ShieldCheck" },
    { id:"politicas", label:"Políticas de acceso", icon:"Lock"     },
    { id:"auditoria", label:"Auditoría",         icon:"History"     },
  ];

  return (
    <div className="screen">
      {/* Page header */}
      <div className="screen-header" style={{ marginBottom:20 }}>
        <div>
          <h1 className="screen-title" style={{ display:"flex", alignItems:"center", gap:10 }}>
            <Icon.ShieldCheck size={22} style={{ color:"var(--accent)" }}/>
            Seguridad
          </h1>
          <p className="screen-subtitle">
            Gestión de usuarios, roles y permisos, y registro de auditoría.
          </p>
        </div>
      </div>

      {/* Tab bar */}
      <div style={{
        display:"flex", gap:4, marginBottom:24,
        borderBottom:"1px solid var(--border)", paddingBottom:0
      }}>
        {tabs.map(t => {
          const Ic = Icon[t.icon];
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              style={{
                display:"flex", alignItems:"center", gap:6, padding:"8px 14px",
                border:"none", background:"transparent", cursor:"pointer",
                fontSize:13, fontWeight: tab === t.id ? 700 : 500,
                color: tab === t.id ? "var(--accent)" : "var(--text-secondary)",
                borderBottom: tab === t.id ? "2px solid var(--accent)" : "2px solid transparent",
                marginBottom:"-1px", borderRadius:0, transition:"color .15s"
              }}
            >
              {Ic && <Ic size={14}/>}
              {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      {tab === "usuarios"  && <UsuariosScreen/>}
      {tab === "roles"     && <RolesTab/>}
      {tab === "politicas" && <PoliticasTab/>}
      {tab === "auditoria" && <AuditoriaScreen/>}
    </div>
  );
}
