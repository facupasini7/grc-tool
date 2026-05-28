/* global React, Icon, Badge, Modal, Spinner, useApi,
          fmtDate, sevTone, sevLabel, stateTone, stateLabel, API */

const { useState: useStateHa, useEffect: useEffectHa } = React;

/* Helpers locales (autocontenidos para no depender de otros scripts) */
const ROLE_SHORT_HA = { admin:"Adm", analista:"Analista GRC", auditado:"Auditado", auditor_externo:"Auditor", ia:"IA Local" };
const ROLE_COLOR_HA = { admin:"var(--accent)", analista:"#10b981", auditado:"#f59e0b", auditor_externo:"#6366f1", ia:"#a855f7" };
const initialsHa = (n) => (n || "?").split(" ").map(w => w[0]).join("").slice(0,2).toUpperCase();
const fmtDateTimeHa = (s) => {
  if (!s) return "";
  const d = new Date(s.includes("T") || s.includes(" ") ? s.replace(" ", "T") + (s.includes("Z") ? "" : "Z") : s);
  if (isNaN(d)) return s;
  return d.toLocaleString("es-AR", { day:"2-digit", month:"short", year:"numeric", hour:"2-digit", minute:"2-digit" });
};
const fileToB64Ha = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload  = () => resolve(String(reader.result).split(",")[1]);
  reader.onerror = reject;
  reader.readAsDataURL(file);
});

/* ── Modelo de estados (workflow auditor ⇄ auditado) ──────────────────── */
const HALLAZGO_STATES = ["incompleto","pendiente","implementado","normalizado","cerrado_no_aplica"];

/* Próximo estado según el rol del usuario. Devuelve null si no puede avanzar. */
function nextStateForRole(h, user) {
  const rol = user?.rol;
  const esStaff = rol === "admin" || rol === "analista";
  if (esStaff) {
    const NATURAL = { incompleto:"pendiente", implementado:"normalizado", normalizado:"cerrado_no_aplica" };
    return NATURAL[h.estado] || null;
  }
  if (rol === "auditado") {
    if (h.estado === "pendiente" && h.responsable_id === user?.id) return "implementado";
  }
  return null;
}

function HallazgosScreen({ evalId, onBack, user }) {
  const [filtSev,   setFiltSev]   = useStateHa("all");
  const [filtState, setFiltState] = useStateHa("all");
  const [editing,   setEditing]   = useStateHa(null);
  const { data, loading, reload } = useApi(() => API.hallazgos(evalId), [evalId]);

  const hallazgos = data?.hallazgos || data || [];
  const esAuditado = user?.rol === "auditado";

  const filtered = hallazgos.filter(h => {
    if (filtSev   !== "all" && h.severidad !== filtSev)   return false;
    if (filtState !== "all" && h.estado    !== filtState) return false;
    return true;
  });

  const sevs   = ["critica","alta","media","baja"];
  const states = HALLAZGO_STATES;

  const countSev   = (s) => hallazgos.filter(h => h.severidad === s).length;
  const countState = (s) => hallazgos.filter(h => h.estado    === s).length;

  const advanceState = async (h) => {
    const next = nextStateForRole(h, user);
    if (!next) return;
    try {
      await API.avanzarEstado(h.id, next);
      reload();
    } catch { alert("Error al actualizar estado"); }
  };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Hallazgos</div>
          <div className="page-sub">No conformidades, observaciones y oportunidades de mejora identificadas en las evaluaciones.</div>
        </div>
        <div className="page-actions">
          {onBack && <button className="btn btn-ghost btn-sm" onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>}
        </div>
      </div>

      {/* Summary chips */}
      <div style={{ display:"flex", gap:8, marginBottom:16, flexWrap:"wrap" }}>
        {sevs.map(s => {
          const n = countSev(s);
          return n > 0 && (
            <button key={s} className={`filter-chip ${filtSev===s?"active":""}`} onClick={() => setFiltSev(filtSev===s?"all":s)}>
              <span className="badge-dot" style={{ width:6,height:6,borderRadius:"50%",background:`var(--${s==="critica"?"danger":s==="alta"?"warning":s==="media"?"info":"success"})`,display:"inline-block",marginRight:2 }}></span>
              {sevLabel(s)} <span className="mono" style={{ opacity:.6 }}>{n}</span>
            </button>
          );
        })}
        <div style={{ width:1, background:"var(--border)", margin:"0 4px" }}/>
        {states.map(s => {
          const n = countState(s);
          return n > 0 && (
            <button key={s} className={`filter-chip ${filtState===s?"active":""}`} onClick={() => setFiltState(filtState===s?"all":s)}>
              {stateLabel(s)} <span className="mono" style={{ opacity:.6 }}>{n}</span>
            </button>
          );
        })}
      </div>

      {loading ? <Spinner/> : filtered.length === 0 ? (
        <div className="empty">
          <div className="empty-icon"><Icon.CheckCircle size={22}/></div>
          <div className="empty-title">Sin hallazgos</div>
          <div className="empty-text">No hay hallazgos que coincidan con los filtros seleccionados.</div>
        </div>
      ) : (
        <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
          {filtered.map(h => (
            <HallazgoCard key={h.id} h={h} user={user} onEdit={() => setEditing(h)} onAdvance={() => advanceState(h)}/>
          ))}
        </div>
      )}

      {editing && <HallazgoEditModal h={editing} onClose={() => { setEditing(null); reload(); }}/>}
    </div>
  );
}

function HallazgoCard({ h, user, onEdit, onAdvance }) {
  const [showColab, setShowColab] = useStateHa(false);
  const esAuditado = user?.rol === "auditado";
  const cerrado = h.estado === "normalizado" || h.estado === "cerrado_no_aplica";
  const overdue = h.fecha_limite && new Date(h.fecha_limite) < new Date() && !cerrado;
  const nextState = nextStateForRole(h, user);

  return (
    <div className="card" style={{ borderLeft:`4px solid var(--${h.severidad==="critica"?"danger":h.severidad==="alta"?"warning":h.severidad==="media"?"info":"success"})`, borderRadius:"0 var(--radius-lg) var(--radius-lg) 0" }}>
      <div style={{ padding:"16px 20px" }}>
        <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap:12, marginBottom:10 }}>
          <div style={{ display:"flex", gap:6, flexWrap:"wrap", alignItems:"center" }}>
            <Badge tone={sevTone(h.severidad)} dot>{sevLabel(h.severidad)}</Badge>
            <Badge tone={stateTone(h.estado)}>{stateLabel(h.estado)}</Badge>
            <span className="tag-mono">{h.control_id || h.ctrl}</span>
            {h.framework && <span className="tag-mono">{h.framework}</span>}
            {h.evaluacion_nombre && (
              <span style={{ display:"flex", alignItems:"center", gap:4, fontSize:11.5, color:"var(--text-muted)" }}>
                <Icon.ClipboardCheck size={11}/> {h.evaluacion_nombre}
              </span>
            )}
          </div>
          <div style={{ display:"flex", gap:6, flexShrink:0 }}>
            {nextState && (
              <button className="btn btn-sm btn-secondary" onClick={onAdvance} title={`Marcar como ${stateLabel(nextState)}`}>
                <Icon.ArrowRight size={12}/> {stateLabel(nextState)}
              </button>
            )}
            <button className={`btn btn-sm ${showColab ? "btn-secondary" : "btn-ghost"}`} onClick={() => setShowColab(v => !v)} title="Comentarios y evidencias">
              <Icon.MessageSquare size={12}/> Colaboración
            </button>
            {!esAuditado && (
              <button className="btn btn-sm btn-ghost" onClick={onEdit}><Icon.Edit size={12}/> Editar</button>
            )}
          </div>
        </div>

        <div style={{ fontWeight:700, fontSize:14.5, marginBottom:6 }}>{h.titulo}</div>
        <div style={{ fontSize:13, color:"var(--text-secondary)", lineHeight:1.55, marginBottom:12 }}>{h.descripcion}</div>

        <div style={{ display:"flex", gap:16, fontSize:12, color:"var(--text-muted)", flexWrap:"wrap" }}>
          {h.responsable_nombre && (
            <span style={{ display:"flex", alignItems:"center", gap:4 }}>
              <Icon.User size={11}/> {h.responsable_nombre}
            </span>
          )}
          {h.fecha_limite && (
            <span style={{ display:"flex", alignItems:"center", gap:4, color: overdue ? "var(--danger)" : "var(--text-muted)", fontWeight: overdue ? 700 : 400 }}>
              <Icon.Calendar size={11}/> {fmtDate(h.fecha_limite)} {overdue && "· VENCIDO"}
            </span>
          )}
          <span style={{ display:"flex", alignItems:"center", gap:4 }}>
            <Icon.Clock size={11}/> {fmtDate(h.creado_en || h.created)}
          </span>
        </div>

        {h.plan_accion && (
          <div style={{ marginTop:12, background:"var(--surface-2)", borderRadius:8, padding:"10px 14px", border:"1px solid var(--border)" }}>
            <div style={{ fontSize:10.5, fontWeight:700, color:"var(--text-muted)", textTransform:"uppercase", letterSpacing:".06em", marginBottom:4 }}>Plan de acción</div>
            <div style={{ fontSize:12.5, color:"var(--text-secondary)", lineHeight:1.5, whiteSpace:"pre-wrap" }}>{h.plan_accion}</div>
          </div>
        )}

        {showColab && <HallazgoColaboracion hallazgoId={h.id}/>}
      </div>
    </div>
  );
}

/* ── Colaboración por hallazgo: evidencias + hilo de comentarios ──────── */
function HallazgoColaboracion({ hallazgoId }) {
  return (
    <div style={{ marginTop:14, borderTop:"1px solid var(--border)", paddingTop:14, display:"flex", flexDirection:"column", gap:16 }}>
      <HallazgoEvidencias hallazgoId={hallazgoId}/>
      <HallazgoThread hallazgoId={hallazgoId}/>
    </div>
  );
}

function HallazgoEvidencias({ hallazgoId }) {
  const { data, loading, reload } = useApi(() => API.hallazgoEvidencias(hallazgoId), [hallazgoId]);
  const evidencias = Array.isArray(data) ? data : [];
  const [subiendo, setSubiendo] = useStateHa(false);

  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 20 * 1024 * 1024) { alert("El archivo supera el límite de 20 MB."); e.target.value = ""; return; }
    setSubiendo(true);
    try {
      const b64 = await fileToB64Ha(file);
      await API.subirHallazgoEvidencia(hallazgoId, { filename: file.name, data: b64 });
      reload();
    } catch (err) {
      alert(err?.message?.includes("soportada") ? "Extensión no soportada." : "Error al subir el archivo.");
    } finally { setSubiendo(false); e.target.value = ""; }
  };

  const eliminar = async (id) => {
    if (!confirm("¿Eliminar esta evidencia?")) return;
    try { await API.eliminarHallazgoEvidencia(id); reload(); }
    catch { alert("No se pudo eliminar la evidencia."); }
  };

  return (
    <div>
      <div style={{ fontSize:10.5, fontWeight:700, color:"var(--text-muted)", textTransform:"uppercase", letterSpacing:".06em", marginBottom:8, display:"flex", alignItems:"center", gap:6 }}>
        <Icon.Paperclip size={12}/> Evidencias {evidencias.length > 0 && `(${evidencias.length})`}
      </div>
      <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
        {loading ? <Spinner/> :
          evidencias.length === 0 ? <div style={{ fontSize:12, color:"var(--text-faint)" }}>Sin evidencias adjuntas.</div> :
          evidencias.map(ev => {
            const color = ROLE_COLOR_HA[ev.usuario_rol] || "var(--text-muted)";
            return (
              <div key={ev.id} style={{ display:"flex", alignItems:"center", gap:10, background:"var(--surface-2)", border:"1px solid var(--border)", borderRadius:7, padding:"7px 12px" }}>
                <Icon.FileText size={14} style={{ color:"var(--text-muted)", flexShrink:0 }}/>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontSize:12.5, color:"var(--text-primary)", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{ev.filename}</div>
                  <div style={{ fontSize:11, color:"var(--text-faint)" }}>
                    <span style={{ color, fontWeight:600 }}>{ev.usuario_nombre}</span>
                    {ev.usuario_rol && <span style={{ color }}> · {ROLE_SHORT_HA[ev.usuario_rol] || ev.usuario_rol}</span>}
                    {" · "}{fmtDateTimeHa(ev.subida_en)}
                  </div>
                </div>
                <button className="btn btn-sm btn-ghost" onClick={() => eliminar(ev.id)} title="Eliminar"><Icon.Trash size={12}/></button>
              </div>
            );
          })}
        <label style={{ display:"inline-flex", alignItems:"center", gap:6, padding:"6px 10px", border:"1.5px dashed var(--border)", borderRadius:7, fontSize:12, color:"var(--text-muted)", cursor:"pointer", alignSelf:"flex-start" }}>
          {subiendo ? <Icon.Loader size={13}/> : <Icon.Upload size={13}/>} Adjuntar evidencia
          <input type="file" style={{ display:"none" }} onChange={upload} disabled={subiendo}/>
        </label>
      </div>
    </div>
  );
}

function HallazgoThread({ hallazgoId }) {
  const { data, loading, reload } = useApi(() => API.hallazgoComentarios(hallazgoId), [hallazgoId]);
  const comentarios = Array.isArray(data) ? data : [];
  const [texto, setTexto]       = useStateHa("");
  const [enviando, setEnviando] = useStateHa(false);

  const enviar = async () => {
    if (!texto.trim()) return;
    setEnviando(true);
    try { await API.agregarHallazgoComentario(hallazgoId, texto.trim()); setTexto(""); reload(); }
    catch { alert("Error al enviar el comentario."); }
    finally { setEnviando(false); }
  };
  const handleKey = (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) enviar(); };

  return (
    <div>
      <div style={{ fontSize:10.5, fontWeight:700, color:"var(--text-muted)", textTransform:"uppercase", letterSpacing:".06em", marginBottom:10, display:"flex", alignItems:"center", gap:6 }}>
        <Icon.MessageSquare size={12}/> Discusión {comentarios.length > 0 && `(${comentarios.length})`}
      </div>
      {loading ? <Spinner/> :
        comentarios.length === 0 ? <div style={{ fontSize:12, color:"var(--text-faint)", marginBottom:10 }}>Sin comentarios aún. Dejá la primera nota.</div> :
        comentarios.map((c, idx) => {
          const rol    = c.usuario_rol || "";
          const color  = ROLE_COLOR_HA[rol] || "var(--text-muted)";
          const isLast = idx === comentarios.length - 1;
          return (
            <div key={c.id} style={{ display:"flex", gap:10, paddingBottom: isLast ? 10 : 14, position:"relative" }}>
              {!isLast && <div style={{ position:"absolute", left:14, top:30, bottom:0, width:2, background:"var(--border)" }}/>}
              <div style={{ flexShrink:0, width:28, height:28, borderRadius:"50%", background:color, display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:700, color:"#fff", zIndex:1 }}>
                {rol === "ia" ? <Icon.Cpu size={14}/> : initialsHa(c.usuario_nombre)}
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ display:"flex", alignItems:"baseline", gap:8, flexWrap:"wrap", marginBottom:4 }}>
                  <span style={{ fontWeight:600, fontSize:12.5, color:"var(--text-primary)" }}>{c.usuario_nombre}</span>
                  {rol && <span style={{ fontSize:10.5, color, fontWeight:600 }}>{ROLE_SHORT_HA[rol] || rol}</span>}
                  <span style={{ fontSize:11, color:"var(--text-faint)" }}>{fmtDateTimeHa(c.creado_en)}</span>
                </div>
                <div style={{ background:"var(--surface-2)", border:"1px solid var(--border)", borderRadius:"0 8px 8px 8px", padding:"8px 12px", fontSize:12.5, color:"var(--text-primary)", lineHeight:1.55, whiteSpace:"pre-wrap", wordBreak:"break-word" }}>
                  {c.texto}
                </div>
              </div>
            </div>
          );
        })}
      <div style={{ display:"flex", flexDirection:"column", gap:6, marginTop:4 }}>
        <textarea className="textarea" rows={2} placeholder="Escribí una nota… (Ctrl+Enter para enviar)" value={texto} onChange={e=>setTexto(e.target.value)} onKeyDown={handleKey} style={{ fontSize:13 }}/>
        <div style={{ display:"flex", justifyContent:"flex-end" }}>
          <button className="btn btn-primary btn-sm" onClick={enviar} disabled={enviando || !texto.trim()}>
            {enviando ? <Icon.Loader size={12}/> : <><Icon.Send size={12}/> Enviar</>}
          </button>
        </div>
      </div>
    </div>
  );
}

function HallazgoEditModal({ h, onClose }) {
  const [titulo,      setTitulo]      = useStateHa(h.titulo || "");
  const [desc,        setDesc]        = useStateHa(h.descripcion || "");
  const [sev,         setSev]         = useStateHa(h.severidad || "media");
  const [estado,      setEstado]      = useStateHa(h.estado || "incompleto");
  const [responsableId, setResponsableId] = useStateHa(h.responsable_id ? String(h.responsable_id) : "");
  const [fecha,       setFecha]       = useStateHa(h.fecha_limite || "");
  const [plan,        setPlan]        = useStateHa(h.plan_accion || "");
  const [loading,     setLoading]     = useStateHa(false);
  const [users,       setUsers]       = useStateHa([]);

  useEffectHa(() => {
    API.participantes().then(rows => setUsers(Array.isArray(rows) ? rows : [])).catch(() => setUsers([]));
  }, []);

  const selectedUser = users.find(u => String(u.id) === responsableId);

  const submit = async () => {
    setLoading(true);
    try {
      await API.actualizarHallazgo(h.id, {
        titulo, descripcion: desc, severidad: sev, estado,
        responsable_id: responsableId ? Number(responsableId) : null,
        fecha_limite: fecha, plan_accion: plan,
      });
      onClose();
    } catch { alert("Error al guardar"); }
    finally { setLoading(false); }
  };

  return (
    <Modal
      open={true}
      onClose={onClose}
      title="Editar hallazgo"
      sub={`${h.control_id || h.ctrl} — ${h.framework || "ISO27001"}`}
      size="lg"
      footer={<>
        <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={submit} disabled={loading}>{loading ? <Icon.Loader size={13}/> : "Guardar cambios"}</button>
      </>}
    >
      <div className="field"><label>Título</label><input className="input" value={titulo} onChange={e=>setTitulo(e.target.value)}/></div>
      <div className="field"><label>Descripción</label><textarea className="textarea" rows={3} value={desc} onChange={e=>setDesc(e.target.value)}/></div>
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12 }}>
        <div className="field">
          <label>Severidad</label>
          <select className="select" value={sev} onChange={e=>setSev(e.target.value)}>
            {["critica","alta","media","baja"].map(s => <option key={s} value={s}>{sevLabel(s)}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Estado</label>
          <select className="select" value={estado} onChange={e=>setEstado(e.target.value)}>
            {HALLAZGO_STATES.map(s => <option key={s} value={s}>{stateLabel(s)}</option>)}
          </select>
        </div>
        <div className="field"><label>Fecha límite</label><input className="input" type="date" value={fecha} onChange={e=>setFecha(e.target.value)}/></div>
      </div>
      <div className="field">
        <label>Responsable</label>
        <select className="select" value={responsableId} onChange={e=>setResponsableId(e.target.value)}>
          <option value="">— Sin asignar —</option>
          {users.map(u => (
            <option key={u.id} value={String(u.id)}>
              {(u.nombre || u.username)} · {ROLE_SHORT_HA[u.rol] || u.rol}
            </option>
          ))}
        </select>
        {selectedUser?.email && (
          <div style={{ fontSize:11.5, color:"var(--text-muted)", marginTop:4 }}>
            <Icon.User size={10} style={{ marginRight:4 }}/>{selectedUser.email}
          </div>
        )}
      </div>
      <div className="field"><label>Plan de acción</label><textarea className="textarea" rows={3} value={plan} onChange={e=>setPlan(e.target.value)}/></div>
    </Modal>
  );
}

Object.assign(window, { HallazgosScreen });
