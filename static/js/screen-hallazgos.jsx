/* global React, Icon, Badge, Modal, Spinner, useApi,
          fmtDate, sevTone, sevLabel, stateTone, stateLabel, API */

const { useState: useStateHa, useEffect: useEffectHa } = React;

function HallazgosScreen({ evalId, onBack }) {
  const [filtSev,   setFiltSev]   = useStateHa("all");
  const [filtState, setFiltState] = useStateHa("all");
  const [editing,   setEditing]   = useStateHa(null);
  const { data, loading, reload } = useApi(() => API.hallazgos(evalId), [evalId]);

  const hallazgos = data?.hallazgos || data || [];

  const filtered = hallazgos.filter(h => {
    if (filtSev   !== "all" && h.severidad !== filtSev)   return false;
    if (filtState !== "all" && h.estado    !== filtState) return false;
    return true;
  });

  const sevs   = ["critica","alta","media","baja"];
  const states = ["abierto","en_proceso","resuelto","verificado"];

  const countSev   = (s) => hallazgos.filter(h => h.severidad === s).length;
  const countState = (s) => hallazgos.filter(h => h.estado    === s).length;

  const advanceState = async (h) => {
    const order = ["abierto","en_proceso","resuelto","verificado"];
    const idx   = order.indexOf(h.estado);
    if (idx >= order.length - 1) return;
    const next = order[idx + 1];
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
            <HallazgoCard key={h.id} h={h} onEdit={() => setEditing(h)} onAdvance={() => advanceState(h)}/>
          ))}
        </div>
      )}

      {editing && <HallazgoEditModal h={editing} onClose={() => { setEditing(null); reload(); }}/>}
    </div>
  );
}

function HallazgoCard({ h, onEdit, onAdvance }) {
  const overdue = h.fecha_limite && new Date(h.fecha_limite) < new Date() && h.estado !== "verificado" && h.estado !== "resuelto";
  const canAdvance = h.estado !== "verificado";
  const stateOrder = ["abierto","en_proceso","resuelto","verificado"];
  const nextState = stateOrder[stateOrder.indexOf(h.estado) + 1];

  return (
    <div className="card" style={{ borderLeft:`4px solid var(--${h.severidad==="critica"?"danger":h.severidad==="alta"?"warning":h.severidad==="media"?"info":"success"})`, borderRadius:"0 var(--radius-lg) var(--radius-lg) 0" }}>
      <div style={{ padding:"16px 20px" }}>
        <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap:12, marginBottom:10 }}>
          <div style={{ display:"flex", gap:6, flexWrap:"wrap", alignItems:"center" }}>
            <Badge tone={sevTone(h.severidad)} dot>{sevLabel(h.severidad)}</Badge>
            <Badge tone={stateTone(h.estado)}>{stateLabel(h.estado)}</Badge>
            <span className="tag-mono">{h.control_id || h.ctrl}</span>
            {h.framework && <span className="tag-mono">{h.framework}</span>}
          </div>
          <div style={{ display:"flex", gap:6, flexShrink:0 }}>
            {canAdvance && (
              <button className="btn btn-sm btn-secondary" onClick={onAdvance} title={`Marcar como ${stateLabel(nextState)}`}>
                <Icon.ArrowRight size={12}/> {stateLabel(nextState)}
              </button>
            )}
            <button className="btn btn-sm btn-ghost" onClick={onEdit}><Icon.Edit size={12}/> Editar</button>
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
      </div>
    </div>
  );
}

function HallazgoEditModal({ h, onClose }) {
  const [titulo,      setTitulo]      = useStateHa(h.titulo || "");
  const [desc,        setDesc]        = useStateHa(h.descripcion || "");
  const [sev,         setSev]         = useStateHa(h.severidad || "media");
  const [estado,      setEstado]      = useStateHa(h.estado || "abierto");
  const [responsable, setResponsable] = useStateHa(h.responsable_nombre || "");
  const [email,       setEmail]       = useStateHa(h.responsable_email || "");
  const [fecha,       setFecha]       = useStateHa(h.fecha_limite || "");
  const [plan,        setPlan]        = useStateHa(h.plan_accion || "");
  const [loading,     setLoading]     = useStateHa(false);

  const submit = async () => {
    setLoading(true);
    try {
      await API.actualizarHallazgo(h.id, { titulo, descripcion: desc, severidad: sev, estado, responsable_nombre: responsable, responsable_email: email, fecha_limite: fecha, plan_accion: plan });
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
            {["abierto","en_proceso","resuelto","verificado"].map(s => <option key={s} value={s}>{stateLabel(s)}</option>)}
          </select>
        </div>
        <div className="field"><label>Fecha límite</label><input className="input" type="date" value={fecha} onChange={e=>setFecha(e.target.value)}/></div>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="field"><label>Responsable</label><input className="input" value={responsable} onChange={e=>setResponsable(e.target.value)}/></div>
        <div className="field"><label>Email responsable</label><input className="input" type="email" value={email} onChange={e=>setEmail(e.target.value)}/></div>
      </div>
      <div className="field"><label>Plan de acción</label><textarea className="textarea" rows={3} value={plan} onChange={e=>setPlan(e.target.value)}/></div>
    </Modal>
  );
}

Object.assign(window, { HallazgosScreen });
