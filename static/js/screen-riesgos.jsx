/* global React, Icon, Badge, Modal, Spinner, Empty, useApi, fmtDate, API */
const { useState: useStateR, useCallback: useCallbackR, useEffect: useEffectR } = React;

const PROB_LABEL  = { 1:"Muy baja", 2:"Baja", 3:"Media", 4:"Alta", 5:"Muy alta" };
const TRAT_LABEL  = { mitigar:"Mitigar", aceptar:"Aceptar", transferir:"Transferir", evitar:"Evitar" };
const TRAT_TONE   = { mitigar:"warning", aceptar:"neutral", transferir:"info", evitar:"danger" };
const RIESGO_TONE = (score) => score >= 15 ? "danger" : score >= 9 ? "warning" : score >= 4 ? "info" : "success";
const RIESGO_LABEL= (score) => score >= 15 ? "Crítico" : score >= 9 ? "Alto" : score >= 4 ? "Medio" : "Bajo";

/* ── Heat map 5×5 ─────────────────────────────────────────────── */
function HeatMap({ riesgos }) {
  const cells = {};
  riesgos.forEach(r => {
    const k = `${r.probabilidad}-${r.impacto}`;
    cells[k] = (cells[k] || []);
    cells[k].push(r);
  });

  const bg = (p, i) => {
    const s = p * i;
    if (s >= 15) return "rgba(220,38,38,.18)";
    if (s >= 9)  return "rgba(234,179,8,.18)";
    if (s >= 4)  return "rgba(59,130,246,.14)";
    return "rgba(22,163,74,.12)";
  };
  const border = (p, i) => {
    const s = p * i;
    if (s >= 15) return "rgba(220,38,38,.45)";
    if (s >= 9)  return "rgba(234,179,8,.45)";
    if (s >= 4)  return "rgba(59,130,246,.35)";
    return "rgba(22,163,74,.3)";
  };

  return (
    <div className="card" style={{ padding:20 }}>
      <div style={{ fontWeight:700, fontSize:14, marginBottom:16 }}>Mapa de calor de riesgos</div>
      <div style={{ display:"flex", alignItems:"flex-end", gap:8 }}>
        {/* Eje Y */}
        <div style={{ display:"flex", flexDirection:"column-reverse", gap:4, width:70 }}>
          {[1,2,3,4,5].map(p => (
            <div key={p} style={{ height:52, display:"flex", alignItems:"center",
              fontSize:10.5, color:"var(--text-muted)", fontWeight:500, justifyContent:"flex-end",
              paddingRight:8 }}>
              {PROB_LABEL[p]}
            </div>
          ))}
          <div style={{ height:20, fontSize:10, color:"var(--text-faint)", textAlign:"right", paddingRight:8 }}>
            Prob.
          </div>
        </div>
        <div>
          {/* Grilla */}
          <div style={{ display:"flex", flexDirection:"column-reverse", gap:4 }}>
            {[1,2,3,4,5].map(p => (
              <div key={p} style={{ display:"flex", gap:4 }}>
                {[1,2,3,4,5].map(i => {
                  const list = cells[`${p}-${i}`] || [];
                  return (
                    <div key={i} style={{
                      width:52, height:52, borderRadius:8,
                      background: bg(p,i), border:`1px solid ${border(p,i)}`,
                      display:"flex", alignItems:"center", justifyContent:"center",
                      fontSize:13, fontWeight:700,
                      color: list.length ? "var(--text-primary)" : "var(--text-faint)",
                    }}
                    title={list.map(r => r.descripcion).join("\n") || "Sin riesgos"}>
                      {list.length || ""}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
          {/* Eje X */}
          <div style={{ display:"flex", gap:4, marginTop:6 }}>
            {[1,2,3,4,5].map(i => (
              <div key={i} style={{ width:52, textAlign:"center", fontSize:10.5,
                color:"var(--text-muted)", fontWeight:500 }}>
                {PROB_LABEL[i].split(" ")[1] || PROB_LABEL[i]}
              </div>
            ))}
          </div>
          <div style={{ textAlign:"center", fontSize:10, color:"var(--text-faint)", marginTop:2 }}>
            Impacto
          </div>
        </div>
        {/* Leyenda */}
        <div style={{ display:"flex", flexDirection:"column", gap:6, marginLeft:12, justifyContent:"center" }}>
          {[
            { label:"Crítico ≥15", bg:"rgba(220,38,38,.18)", border:"rgba(220,38,38,.45)" },
            { label:"Alto ≥9",     bg:"rgba(234,179,8,.18)",  border:"rgba(234,179,8,.45)" },
            { label:"Medio ≥4",    bg:"rgba(59,130,246,.14)", border:"rgba(59,130,246,.35)" },
            { label:"Bajo <4",     bg:"rgba(22,163,74,.12)",  border:"rgba(22,163,74,.3)" },
          ].map(({ label, bg: b, border: bo }) => (
            <div key={label} style={{ display:"flex", alignItems:"center", gap:6 }}>
              <div style={{ width:14, height:14, borderRadius:3,
                background:b, border:`1px solid ${bo}`, flexShrink:0 }}/>
              <span style={{ fontSize:11, color:"var(--text-muted)" }}>{label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Modal crear/editar riesgo ────────────────────────────────── */
function RiesgoModal({ open, onClose, evalId, editing, participantes, evaluaciones }) {
  const [form, setForm] = useStateR({
    descripcion:"", probabilidad:3, impacto:3,
    tratamiento:"mitigar", propietario_id:"", notas:"", control_id:"",
    evaluacion_id:"",
  });
  const [saving, setSaving] = useStateR(false);
  const [controles, setControles] = useStateR([]);
  const [cargandoCtrl, setCargandoCtrl] = useStateR(false);

  useEffectR(() => {
    if (editing) setForm({
      descripcion:   editing.descripcion   || "",
      probabilidad:  editing.probabilidad  || 3,
      impacto:       editing.impacto       || 3,
      tratamiento:   editing.tratamiento   || "mitigar",
      propietario_id:editing.propietario_id|| "",
      notas:         editing.notas         || "",
      control_id:    editing.control_id    || "",
      evaluacion_id: editing.evaluacion_id || evalId || "",
    });
    else setForm({ descripcion:"", probabilidad:3, impacto:3,
      tratamiento:"mitigar", propietario_id:"", notas:"", control_id:"",
      evaluacion_id: evalId || "" });
  }, [editing, open, evalId]);

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));
  const score = form.probabilidad * form.impacto;

  /* Cargar los controles de la evaluación elegida para el desplegable */
  useEffectR(() => {
    if (!open || !form.evaluacion_id) { setControles([]); return; }
    let alive = true;
    setCargandoCtrl(true);
    API.controles(form.evaluacion_id)
      .then(cs => {
        const arr = Array.isArray(cs) ? cs : (Array.isArray(cs?.controles) ? cs.controles : []);
        if (alive) setControles(arr);
      })
      .catch(() => { if (alive) setControles([]); })
      .finally(() => { if (alive) setCargandoCtrl(false); });
    return () => { alive = false; };
  }, [open, form.evaluacion_id]);

  const submit = async () => {
    if (!form.descripcion.trim()) return;
    if (!form.evaluacion_id) { alert("Seleccioná la evaluación a la que pertenece el riesgo."); return; }
    setSaving(true);
    try {
      const d = { ...form, probabilidad: +form.probabilidad, impacto: +form.impacto,
                  propietario_id: form.propietario_id || null,
                  evaluacion_id: +form.evaluacion_id };
      if (editing) await API.actualizarRiesgo(editing.id, d);
      else         await API.crearRiesgo(form.evaluacion_id, d);
      onClose(true);
    } catch { alert("Error al guardar."); }
    finally { setSaving(false); }
  };

  const fwLabel = (ev) => {
    try { const fws = JSON.parse(ev.frameworks || "[]"); return fws.length ? fws.join(" · ") : ""; }
    catch { return ""; }
  };

  return (
    <Modal open={open} onClose={() => onClose(false)} size="lg"
      title={editing ? "Editar riesgo" : "Nuevo riesgo"}
      sub="Registrá el riesgo, su probabilidad, impacto y plan de tratamiento"
      footer={<>
        <button className="btn btn-secondary" onClick={() => onClose(false)}>Cancelar</button>
        <button className="btn btn-primary" onClick={submit} disabled={saving}>
          {saving ? <Icon.Loader size={13}/> : "Guardar"}
        </button>
      </>}
    >
      <div className="field">
        <label>Evaluación *</label>
        <select className="select" value={form.evaluacion_id}
          onChange={e => { set("evaluacion_id", e.target.value); set("control_id", ""); }}>
          <option value="">— Seleccioná una evaluación —</option>
          {(evaluaciones || []).map(ev => (
            <option key={ev.id} value={ev.id}>
              {ev.nombre}{fwLabel(ev) ? ` — ${fwLabel(ev)}` : ""}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>Descripción del riesgo *</label>
        <textarea className="input" rows={3} value={form.descripcion}
          onChange={e => set("descripcion", e.target.value)}
          placeholder="Ej: Acceso no autorizado a datos sensibles de clientes por falta de MFA"/>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12 }}>
        <div className="field">
          <label>Probabilidad (1-5)</label>
          <select className="select" value={form.probabilidad} onChange={e => set("probabilidad", +e.target.value)}>
            {[1,2,3,4,5].map(n => <option key={n} value={n}>{n} — {PROB_LABEL[n]}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Impacto (1-5)</label>
          <select className="select" value={form.impacto} onChange={e => set("impacto", +e.target.value)}>
            {[1,2,3,4,5].map(n => <option key={n} value={n}>{n} — {PROB_LABEL[n]}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Score de riesgo</label>
          <div style={{ height:38, display:"flex", alignItems:"center", gap:8 }}>
            <span style={{ fontSize:22, fontWeight:800, color:
              score>=15?"var(--danger)":score>=9?"var(--warning)":score>=4?"var(--accent)":"var(--success)" }}>
              {score}
            </span>
            <Badge tone={RIESGO_TONE(score)}>{RIESGO_LABEL(score)}</Badge>
          </div>
        </div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="field">
          <label>Tratamiento</label>
          <select className="select" value={form.tratamiento} onChange={e => set("tratamiento", e.target.value)}>
            {Object.entries(TRAT_LABEL).map(([k,v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Propietario del riesgo</label>
          <select className="select" value={form.propietario_id} onChange={e => set("propietario_id", e.target.value)}>
            <option value="">Sin asignar</option>
            {(participantes||[]).map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
          </select>
        </div>
      </div>

      <div className="field">
        <label>Control relacionado</label>
        <select className="select" value={form.control_id}
          onChange={e => set("control_id", e.target.value)}
          disabled={!form.evaluacion_id || cargandoCtrl}>
          <option value="">
            {!form.evaluacion_id ? "Elegí primero una evaluación"
              : cargandoCtrl ? "Cargando controles…" : "— Sin control específico —"}
          </option>
          {controles.map(c => (
            <option key={c.id} value={c.id}>
              {c.id}{c.nombre ? ` — ${c.nombre}` : ""}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>Notas / Plan de mitigación</label>
        <textarea className="input" rows={3} value={form.notas}
          onChange={e => set("notas", e.target.value)}
          placeholder="Describí las acciones de mitigación planificadas…"/>
      </div>
    </Modal>
  );
}

/* ── Pantalla principal ───────────────────────────────────────── */
function RiesgosScreen({ evalId, onBack }) {
  const [modal,   setModal]   = useStateR(false);
  const [editing, setEditing] = useStateR(null);
  const [filter,  setFilter]  = useStateR("todos");

  const { data: _riesgosData, loading, reload } = useApi(
    () => evalId ? API.riesgos(evalId) : Promise.resolve([]), [evalId]
  );
  const { data: _partData } = useApi(() => API.participantes(), []);
  const { data: _evalData } = useApi(() => API.evaluaciones(), []);

  const riesgos      = Array.isArray(_riesgosData) ? _riesgosData : [];
  const participantes = Array.isArray(_partData)   ? _partData   : [];
  const evaluaciones  = Array.isArray(_evalData)   ? _evalData   : [];

  const open  = (r = null) => { setEditing(r); setModal(true); };
  const close = (saved)    => { setModal(false); if (saved) reload(); };

  const eliminar = async (id) => {
    if (!confirm("¿Eliminar este riesgo?")) return;
    await API.eliminarRiesgo(id);
    reload();
  };

  /* ── No eval selected ── */
  if (!evalId) return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Registro de Riesgos</div>
          <div className="page-sub">Identificá, evaluá y gestioná los riesgos del SGSI.</div>
        </div>
      </div>
      <Empty icon="ShieldCheck" title="Seleccioná una evaluación"
        text="Para ver el registro de riesgos, primero abrí una evaluación desde la pantalla de Evaluaciones."/>
    </div>
  );

  const lista = riesgos.filter(r => {
    if (filter === "todos")    return true;
    if (filter === "critico")  return r.probabilidad * r.impacto >= 15;
    if (filter === "alto")     return r.probabilidad * r.impacto >= 9 && r.probabilidad * r.impacto < 15;
    if (filter === "abierto")  return r.estado === "abierto";
    return true;
  });

  const resumen = {
    total:    riesgos.length,
    critico:  riesgos.filter(r => r.probabilidad*r.impacto >= 15).length,
    alto:     riesgos.filter(r => r.probabilidad*r.impacto >= 9 && r.probabilidad*r.impacto < 15).length,
    abiertos: riesgos.filter(r => r.estado === "abierto").length,
  };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          {onBack && <button className="btn btn-ghost btn-sm" style={{ marginBottom:8 }} onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>}
          <div className="page-title">Registro de Riesgos</div>
          <div className="page-sub">Identificá, evaluá y gestioná los riesgos del SGSI.</div>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost btn-sm" onClick={reload}><Icon.Refresh size={13}/></button>
          <button className="btn btn-primary" onClick={() => open()}><Icon.Plus size={14}/> Nuevo riesgo</button>
        </div>
      </div>

      {/* KPIs */}
      <div className="kpi-grid" style={{ marginBottom:20 }}>
        <div className="kpi"><div className="kpi-label">Total riesgos</div><div className="kpi-val">{resumen.total}</div></div>
        <div className="kpi"><div className="kpi-label" style={{ color:"var(--danger)" }}>Críticos</div><div className="kpi-val" style={{ color:"var(--danger)" }}>{resumen.critico}</div></div>
        <div className="kpi"><div className="kpi-label" style={{ color:"var(--warning)" }}>Altos</div><div className="kpi-val" style={{ color:"var(--warning)" }}>{resumen.alto}</div></div>
        <div className="kpi"><div className="kpi-label">Abiertos</div><div className="kpi-val">{resumen.abiertos}</div></div>
      </div>

      {riesgos.length > 0 && <HeatMap riesgos={riesgos}/>}

      {/* Filtros */}
      <div className="filter-bar" style={{ marginTop:16 }}>
        {["todos","critico","alto","abierto"].map(f => (
          <button key={f} className={`filter-chip${filter===f?" active":""}`} onClick={() => setFilter(f)}>
            {f==="todos"?"Todos":f==="critico"?"Críticos":f==="alto"?"Altos":"Abiertos"}
            <span className="mono" style={{ opacity:.6, marginLeft:4 }}>
              {f==="todos"?resumen.total:f==="critico"?resumen.critico:f==="alto"?resumen.alto:resumen.abiertos}
            </span>
          </button>
        ))}
        <div style={{ flex:1 }}/>
        <span style={{ fontSize:12, color:"var(--text-muted)" }}>{lista.length} riesgos</span>
      </div>

      {loading ? <Spinner/> : lista.length === 0 ? (
        <Empty icon="ShieldCheck" title="Sin riesgos registrados"
          text="Registrá los riesgos identificados durante el gap analysis."
          action={<button className="btn btn-primary" onClick={() => open()}><Icon.Plus size={13}/> Nuevo riesgo</button>}/>
      ) : (
        <div className="card tbl-card" style={{ marginTop:12 }}>
          <table className="tbl">
            <thead><tr>
              <th style={{ width:70 }}>Score</th>
              <th style={{ width:100 }}>Nivel</th>
              <th>Descripción</th>
              <th style={{ width:110 }}>Tratamiento</th>
              <th style={{ width:140 }}>Propietario</th>
              <th style={{ width:110 }}>Estado</th>
              <th style={{ width:70 }}></th>
            </tr></thead>
            <tbody>
              {lista.map(r => {
                const score = r.probabilidad * r.impacto;
                return (
                  <tr key={r.id} className="clickable" onClick={() => open(r)}>
                    <td>
                      <span style={{ fontWeight:800, fontSize:18,
                        color:score>=15?"var(--danger)":score>=9?"var(--warning)":score>=4?"var(--accent)":"var(--success)" }}>
                        {score}
                      </span>
                      <div style={{ fontSize:10.5, color:"var(--text-muted)" }}>
                        P{r.probabilidad}×I{r.impacto}
                      </div>
                    </td>
                    <td><Badge tone={RIESGO_TONE(score)}>{RIESGO_LABEL(score)}</Badge></td>
                    <td>
                      <div style={{ fontWeight:500, fontSize:13 }}>{r.descripcion}</div>
                      {r.control_id && <div style={{ fontSize:11.5, color:"var(--text-muted)", marginTop:2 }}
                        className="mono">{r.control_id}</div>}
                      {r.notas && <div style={{ fontSize:11.5, color:"var(--text-secondary)", marginTop:4,
                        display:"-webkit-box", WebkitLineClamp:2, WebkitBoxOrient:"vertical", overflow:"hidden" }}>
                        {r.notas}
                      </div>}
                    </td>
                    <td><Badge tone={TRAT_TONE[r.tratamiento]}>{TRAT_LABEL[r.tratamiento]}</Badge></td>
                    <td style={{ fontSize:13 }}>{r.propietario_nombre || <span style={{ color:"var(--text-faint)" }}>—</span>}</td>
                    <td>
                      <Badge tone={r.estado==="cerrado"?"success":r.estado==="aceptado"?"neutral":"warning"}>
                        {r.estado==="abierto"?"Abierto":r.estado==="en_tratamiento"?"En trat.":
                          r.estado==="aceptado"?"Aceptado":"Cerrado"}
                      </Badge>
                    </td>
                    <td onClick={e => e.stopPropagation()}>
                      <button className="btn btn-ghost btn-icon" style={{ color:"var(--danger)" }}
                        onClick={() => eliminar(r.id)}>
                        <Icon.Trash size={13}/>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <RiesgoModal open={modal} onClose={close} evalId={evalId}
        editing={editing} participantes={participantes} evaluaciones={evaluaciones}/>
    </div>
  );
}

Object.assign(window, { RiesgosScreen });
