/* global React, Icon, Badge, Maturity, MaturitySelector, Modal, Spinner, useApi,
          fmtDate, sevTone, sevLabel, stateTone, stateLabel, API, InformeModal */

const { useState: useStateE, useEffect: useEffectE, useCallback: useCallbackE } = React;

function EvaluacionScreen({ evalId, onBack, onNav, user }) {
  const { data: ev,       loading: le } = useApi(() => API.evaluacion(evalId),        [evalId]);
  const { data: ctrlData, loading: lc, reload: reloadCtrls } = useApi(() => API.controles(evalId), [evalId]);

  const [dominioActivo, setDominioActivo] = useStateE(null);
  const [respuestas,    setRespuestas]    = useStateE({});
  const [saving,        setSaving]        = useStateE({});
  const [newHallazgo,   setNewHallazgo]   = useStateE(null); // ctrl for new finding modal
  const [informeOpen,   setInformeOpen]   = useStateE(false);

  // Build domain / control structure from API
  const controles = ctrlData?.controles || ctrlData || [];
  const dominios  = {};
  controles.forEach(c => {
    if (!dominios[c.dominio]) dominios[c.dominio] = c.dominio_nombre || c.dominio;
  });

  // Sync respuestas from API data
  useEffectE(() => {
    if (!controles.length) return;
    const r = {};
    controles.forEach(c => {
      r[c.id] = { madurez: c.madurez ?? 0, comentario: c.comentario ?? "", aplica: c.aplica ?? 1 };
    });
    setRespuestas(r);
    if (!dominioActivo) setDominioActivo(Object.keys(dominios)[0]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [controles.length]);

  const guardar = async (ctrl, madurez, comentario, aplica) => {
    setSaving(s => ({ ...s, [ctrl.id]: true }));
    const payload = { control_id: ctrl.id, madurez, comentario: comentario ?? respuestas[ctrl.id]?.comentario ?? "", aplica: aplica ?? respuestas[ctrl.id]?.aplica ?? 1 };
    try {
      await API.guardarRespuesta(evalId, payload);
      setRespuestas(s => ({ ...s, [ctrl.id]: { ...s[ctrl.id], ...payload } }));
    } catch { /* silently fail */ }
    finally { setSaving(s => ({ ...s, [ctrl.id]: false })); }
  };

  if (le || lc) return <Spinner/>;
  if (!ev) return <div className="page"><div style={{ color:"var(--text-muted)" }}>Evaluación no encontrada.</div></div>;

  const domKeys      = Object.keys(dominios);
  const totalCtrl    = controles.length;
  const respondidos  = controles.filter(c => (respuestas[c.id]?.madurez ?? c.madurez ?? 0) > 0).length;
  const pct          = totalCtrl > 0 ? Math.round(respondidos / totalCtrl * 100) : 0;

  const ctrlsActivos = controles.filter(c => c.dominio === dominioActivo);

  return (
    <div className="page">
      {/* Page header */}
      <div className="page-head">
        <div>
          <div className="page-title">{ev.nombre}</div>
          <div className="page-sub">{ev.empresa}{ev.alcance ? ` · ${ev.alcance}` : ""}</div>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost btn-sm" onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>
          {(!user || user.rol !== "auditado") && <>
            <button className="btn btn-ghost btn-sm" onClick={() => onNav("riesgos")}><Icon.AlertOctagon size={13}/> Riesgos</button>
            <button className="btn btn-ghost btn-sm" onClick={() => onNav("soa")}><Icon.ClipboardCheck size={13}/> SoA</button>
            <button className="btn btn-ghost btn-sm" onClick={() => onNav("deadlines")}><Icon.Calendar size={13}/> Deadlines</button>
          </>}
          <button className="btn btn-secondary" onClick={() => onNav("resultados")}><Icon.PieChart size={13}/> Resultados</button>
          <button className="btn btn-secondary" onClick={() => onNav("hallazgos")}><Icon.AlertTriangle size={13}/> Hallazgos</button>
          <button className="btn btn-secondary" onClick={() => onNav("cobertura")}><Icon.Layers size={13}/> Cobertura</button>
          {(!user || user.rol !== "auditado") && (
            <button className="btn btn-primary btn-sm" onClick={() => setInformeOpen(true)}>
              <Icon.Download size={13}/> Exportar
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="card" style={{ padding:"14px 18px", marginBottom:20, display:"flex", alignItems:"center", gap:16 }}>
        <div style={{ flex:1 }}>
          <div style={{ display:"flex", justifyContent:"space-between", marginBottom:6 }}>
            <span style={{ fontSize:12.5, fontWeight:600, color:"var(--text-secondary)" }}>Progreso</span>
            <span style={{ fontSize:12.5, fontWeight:700, color:"var(--accent)" }} className="mono">{respondidos}/{totalCtrl} controles · {pct}%</span>
          </div>
          <div className="progress"><div className="progress-fill" style={{ width:`${pct}%` }}></div></div>
        </div>
        {ev.completada && <Badge tone="success" dot>Completada</Badge>}
      </div>

      {/* Domain tabs */}
      <div className="tabs">
        {domKeys.map(id => {
          const ctrls   = controles.filter(c => c.dominio === id);
          const resp    = ctrls.filter(c => (respuestas[c.id]?.madurez ?? c.madurez ?? 0) > 0).length;
          return (
            <button key={id} className={`tab ${dominioActivo===id?"active":""}`} onClick={() => setDominioActivo(id)}>
              {id}
              <span className="tab-count">{resp}/{ctrls.length}</span>
            </button>
          );
        })}
      </div>

      {/* Controls list */}
      <div className="card">
        {ctrlsActivos.map(ctrl => (
          <ControlRow
            key={ctrl.id}
            ctrl={ctrl}
            resp={respuestas[ctrl.id] || { madurez: ctrl.madurez ?? 0, comentario: ctrl.comentario ?? "", aplica: ctrl.aplica ?? 1 }}
            saving={saving[ctrl.id]}
            evalId={evalId}
            onSave={(m, c, a) => guardar(ctrl, m, c, a)}
            onNewHallazgo={() => setNewHallazgo(ctrl)}
          />
        ))}
      </div>

      {newHallazgo && (
        <NuevoHallazgoModal
          ctrl={newHallazgo}
          evalId={evalId}
          onClose={() => setNewHallazgo(null)}
        />
      )}

      {informeOpen && (
        <InformeModal
          evalId={evalId}
          frameworks={ev?.frameworks ? (typeof ev.frameworks === "string" ? JSON.parse(ev.frameworks) : ev.frameworks) : ["ISO27001"]}
          onClose={() => setInformeOpen(false)}
        />
      )}
    </div>
  );
}

function ControlRow({ ctrl, resp, saving, evalId, onSave, onNewHallazgo }) {
  const [open,      setOpen]      = useStateE(false);
  const [comentario,setComentario]= useStateE(resp.comentario || "");
  const [aplica,    setAplica]    = useStateE(resp.aplica !== 0);

  // Sync comentario when resp changes from parent
  useEffectE(() => { setComentario(resp.comentario || ""); }, [resp.comentario]);
  useEffectE(() => { setAplica(resp.aplica !== 0); }, [resp.aplica]);

  const m     = resp.madurez ?? 0;
  const isBad = aplica && m > 0 && m < 3;
  const isOk  = aplica && m >= 3;

  const status = !aplica
    ? <Badge tone="neutral">No aplica</Badge>
    : m === 0
      ? <Badge tone="neutral">Sin evaluar</Badge>
      : isBad
        ? <Badge tone="danger" dot>Brecha</Badge>
        : <Badge tone="success" dot>Cumple</Badge>;

  return (
    <div>
      <div className={`ctrl-row ${open ? "is-open" : ""}`} onClick={() => setOpen(!open)} style={{ cursor:"pointer" }}>
        <span className="ctrl-id mono">{ctrl.id}</span>
        <div className="ctrl-info">
          <div className="ctrl-name">{ctrl.nombre || ctrl.name}</div>
          <div className="ctrl-desc">{ctrl.descripcion || ctrl.desc}</div>
        </div>
        <div className="ctrl-mat">
          <Maturity value={m}/>
        </div>
        <div className="ctrl-status">
          {status}
          <Icon.ChevronDown size={14} style={{ color:"var(--text-faint)", transform: open ? "rotate(180deg)" : "none", transition:"transform .15s" }}/>
        </div>
      </div>

      {open && (
        <div className="ctrl-expand">
          <div style={{ display:"flex", alignItems:"center", gap:16, flexWrap:"wrap" }}>
            <label style={{ display:"flex", alignItems:"center", gap:6, fontSize:12.5, color:"var(--text-secondary)", cursor:"pointer", userSelect:"none" }}>
              <input type="checkbox" checked={aplica} onChange={e => { setAplica(e.target.checked); onSave(m, comentario, e.target.checked ? 1 : 0); }} style={{ accentColor:"var(--accent)" }}/>
              Aplica
            </label>
            <MaturitySelector value={m} disabled={!aplica} onChange={v => onSave(v, comentario, aplica ? 1 : 0)}/>
            {saving && <Icon.Loader size={13} style={{ color:"var(--accent)", animation:"spin 1s linear infinite" }}/>}
          </div>

          <textarea
            className="textarea"
            rows={2}
            placeholder="Comentario u observación sobre este control…"
            value={comentario}
            onChange={e => setComentario(e.target.value)}
            onBlur={() => { if (comentario !== (resp.comentario || "")) onSave(m, comentario, aplica ? 1 : 0); }}
          />

          <div style={{ display:"flex", gap:8 }}>
            {isBad && (
              <button className="btn btn-sm btn-secondary" onClick={e => { e.stopPropagation(); onNewHallazgo(); }}>
                <Icon.Plus size={12}/> Registrar hallazgo
              </button>
            )}
            <EvidenciasInline evalId={evalId} ctrlId={ctrl.id}/>
          </div>
        </div>
      )}
    </div>
  );
}

function EvidenciasInline({ evalId, ctrlId }) {
  const [open, setOpen] = useStateE(false);
  const { data, loading, reload } = useApi(() => API.evidencias(evalId, ctrlId), [evalId, ctrlId]);
  const evidencias = data?.evidencias || data || [];

  const upload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append("archivo", file);
    fd.append("control_id", ctrlId);
    try {
      await fetch(`/api/evaluaciones/${evalId}/controles/${ctrlId}/evidencias`, { method:"POST", body: fd, credentials:"include" });
      reload();
    } catch { alert("Error al subir evidencia"); }
    e.target.value = "";
  };

  return (
    <div>
      <button className="btn btn-ghost btn-sm" onClick={() => setOpen(!open)}>
        <Icon.Paperclip size={12}/> Evidencias {evidencias.length > 0 && `(${evidencias.length})`}
        <Icon.ChevronDown size={11} style={{ transform: open ? "rotate(180deg)" : "none", transition:"transform .15s" }}/>
      </button>
      {open && (
        <div style={{ marginTop:8, display:"flex", flexDirection:"column", gap:8 }}>
          {loading ? <Icon.Loader size={14} style={{ animation:"spin 1s linear infinite", color:"var(--accent)" }}/> :
            evidencias.length === 0 ? <div style={{ fontSize:12, color:"var(--text-muted)" }}>Sin evidencias adjuntas.</div> :
            evidencias.map(ev => (
              <div key={ev.id} style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:7, padding:"8px 12px", fontSize:12, display:"flex", alignItems:"center", gap:8 }}>
                <Icon.FileText size={13} style={{ color:"var(--text-muted)", flexShrink:0 }}/>
                <span style={{ flex:1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{ev.filename}</span>
                <Badge tone={ ev.veredicto==="cumple"?"success":ev.veredicto==="no_cumple"?"danger":ev.veredicto==="parcial"?"warning":"neutral" }>
                  {ev.veredicto || "pendiente"}
                </Badge>
              </div>
            ))
          }
          <label style={{ display:"inline-flex", alignItems:"center", gap:6, padding:"6px 10px", border:"1.5px dashed var(--border)", borderRadius:7, fontSize:12, color:"var(--text-muted)", cursor:"pointer" }}>
            <Icon.Upload size={13}/> Subir archivo
            <input type="file" style={{ display:"none" }} onChange={upload}/>
          </label>
        </div>
      )}
    </div>
  );
}

function NuevoHallazgoModal({ ctrl, evalId, onClose }) {
  const [titulo,      setTitulo]      = useStateE(`Brecha en ${ctrl.id}`);
  const [desc,        setDesc]        = useStateE("");
  const [sev,         setSev]         = useStateE("media");
  const [responsable, setResponsable] = useStateE("");
  const [fecha,       setFecha]       = useStateE("");
  const [plan,        setPlan]        = useStateE("");
  const [loading,     setLoading]     = useStateE(false);

  const submit = async () => {
    setLoading(true);
    try {
      await API.crearHallazgo({ evaluacion_id: evalId, control_id: ctrl.id, titulo, descripcion: desc, severidad: sev, responsable_nombre: responsable, fecha_limite: fecha, plan_accion: plan });
      onClose();
    } catch { alert("Error al crear hallazgo"); }
    finally { setLoading(false); }
  };

  return (
    <Modal
      open={true}
      onClose={onClose}
      title="Registrar hallazgo"
      sub={`Control ${ctrl.id} — ${ctrl.nombre || ctrl.name}`}
      footer={<>
        <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={submit} disabled={loading || !titulo.trim()}>{loading ? <Icon.Loader size={13}/> : "Guardar hallazgo"}</button>
      </>}
    >
      <div className="field"><label>Título</label><input className="input" value={titulo} onChange={e=>setTitulo(e.target.value)}/></div>
      <div className="field"><label>Descripción</label><textarea className="textarea" rows={3} value={desc} onChange={e=>setDesc(e.target.value)} placeholder="Describí el hallazgo en detalle…"/></div>
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="field">
          <label>Severidad</label>
          <select className="select" value={sev} onChange={e=>setSev(e.target.value)}>
            {["critica","alta","media","baja"].map(s => <option key={s} value={s}>{sevLabel(s)}</option>)}
          </select>
        </div>
        <div className="field"><label>Fecha límite</label><input className="input" type="date" value={fecha} onChange={e=>setFecha(e.target.value)}/></div>
      </div>
      <div className="field"><label>Responsable</label><input className="input" value={responsable} onChange={e=>setResponsable(e.target.value)} placeholder="Nombre del responsable"/></div>
      <div className="field"><label>Plan de acción</label><textarea className="textarea" rows={2} value={plan} onChange={e=>setPlan(e.target.value)} placeholder="Describí los pasos para remediar…"/></div>
    </Modal>
  );
}

Object.assign(window, { EvaluacionScreen });
