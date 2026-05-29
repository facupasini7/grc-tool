/* global React, Icon, Badge, Modal, Spinner, Empty, useApi, fmtDate, API */

const { useState: useStateTprm, useEffect: useEffectTprm } = React;

/* ── Catálogos / helpers ─────────────────────────────────────────── */
const TPRM_CRITICIDAD = [
  { v:"baja",    label:"Baja"    },
  { v:"media",   label:"Media"   },
  { v:"alta",    label:"Alta"    },
  { v:"critica", label:"Crítica" },
];
const TPRM_ESTADOS = [
  { v:"en_evaluacion", label:"En evaluación" },
  { v:"activo",        label:"Activo"        },
  { v:"inactivo",      label:"Inactivo"      },
];
const TPRM_RESPUESTAS = [
  { v:"cumple",    label:"Cumple",     color:"#4ade80" },
  { v:"parcial",   label:"Parcial",    color:"#fbbf24" },
  { v:"no_cumple", label:"No cumple",  color:"#f87171" },
  { v:"na",        label:"N/A",        color:"#94a3b8" },
];

const riesgoTone  = (n) => ({ bajo:"success", medio:"info", alto:"warning", critico:"danger" }[n] || "neutral");
const riesgoLabel = (n) => ({ bajo:"Bajo", medio:"Medio", alto:"Alto", critico:"Crítico" }[n] || "—");
const critLabel   = (c) => (TPRM_CRITICIDAD.find(x => x.v === c)?.label || c);
const estadoLabel = (e) => (TPRM_ESTADOS.find(x => x.v === e)?.label || e);

/* Anillo de puntaje */
function ScoreRing({ puntaje, nivel, size = 64 }) {
  if (puntaje == null) {
    return (
      <div style={{ width:size, height:size, borderRadius:"50%", border:"3px dashed var(--border)",
                    display:"flex", alignItems:"center", justifyContent:"center", color:"var(--text-muted)", fontSize:11 }}>
        s/d
      </div>
    );
  }
  const col = { bajo:"#4ade80", medio:"#38bdf8", alto:"#fbbf24", critico:"#f87171" }[nivel] || "#94a3b8";
  const deg = Math.round((puntaje / 100) * 360);
  return (
    <div style={{
      width:size, height:size, borderRadius:"50%",
      background:`conic-gradient(${col} ${deg}deg, var(--surface-2) 0deg)`,
      display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0
    }}>
      <div style={{ width:size-12, height:size-12, borderRadius:"50%", background:"var(--surface-1)",
                    display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center" }}>
        <span className="mono" style={{ fontSize:size>56?17:14, fontWeight:800, lineHeight:1, color:col }}>{puntaje}</span>
        <span style={{ fontSize:8, color:"var(--text-muted)" }}>/100</span>
      </div>
    </div>
  );
}

/* ── Modal de detalle / edición de proveedor ─────────────────────── */
function ProveedorModal({ proveedorId, preguntas, canManage, onClose, onChanged }) {
  const isNew = !proveedorId;
  const [tab, setTab] = useStateTprm("perfil");
  const [prov, setProv] = useStateTprm(null);
  const [respuestas, setRespuestas] = useStateTprm({});   // { pregunta_id: {respuesta, comentario} }
  const [loading, setLoading] = useStateTprm(!isNew);
  const [saving, setSaving] = useStateTprm(false);
  const [iaLoading, setIaLoading] = useStateTprm(false);
  const [iaError, setIaError] = useStateTprm("");
  const [error, setError] = useStateTprm("");

  /* Formulario de perfil */
  const [form, setForm] = useStateTprm({
    nombre:"", tipo_servicio:"", criticidad:"media", datos_maneja:"",
    contacto_nombre:"", contacto_email:"", estado:"en_evaluacion", notas:"",
    riesgo_inherente:"", riesgo_inherente_just:"",
  });
  const setF = (k) => (v) => setForm(f => ({ ...f, [k]: v }));

  useEffectTprm(() => {
    if (isNew) return;
    let alive = true;
    setLoading(true);
    API.proveedor(proveedorId).then(p => {
      if (!alive) return;
      setProv(p);
      setForm({
        nombre:p.nombre||"", tipo_servicio:p.tipo_servicio||"", criticidad:p.criticidad||"media",
        datos_maneja:p.datos_maneja||"", contacto_nombre:p.contacto_nombre||"",
        contacto_email:p.contacto_email||"", estado:p.estado||"en_evaluacion", notas:p.notas||"",
        riesgo_inherente:p.riesgo_inherente||"", riesgo_inherente_just:p.riesgo_inherente_just||"",
      });
      setRespuestas(p.respuestas || {});
      setLoading(false);
    }).catch(() => { if (alive) { setError("No se pudo cargar el proveedor"); setLoading(false); } });
    return () => { alive = false; };
  }, [proveedorId]);

  const guardarPerfil = async () => {
    if (!form.nombre.trim()) { setError("El nombre es obligatorio"); setTab("perfil"); return; }
    setSaving(true); setError("");
    try {
      if (isNew) {
        await API.crearProveedor(form);
      } else {
        await API.actualizarProveedor(proveedorId, form);
      }
      onChanged();
      onClose();
    } catch (e) {
      setError(e.message || "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const setResp = (pid, campo, valor) =>
    setRespuestas(r => ({ ...r, [pid]: { ...(r[pid] || {}), [campo]: valor } }));

  const guardarCuestionario = async () => {
    setSaving(true); setError("");
    try {
      const payload = preguntas.map(q => ({
        pregunta_id: q.id,
        respuesta: respuestas[q.id]?.respuesta || "na",
        comentario: respuestas[q.id]?.comentario || "",
      }));
      const r = await API.guardarRespuestasProveedor(proveedorId, payload);
      setProv(p => ({ ...(p || {}), scoring: r.scoring }));
      onChanged();
    } catch (e) {
      setError(e.message || "Error al guardar el cuestionario");
    } finally {
      setSaving(false);
    }
  };

  const sugerirRiesgo = async () => {
    setIaLoading(true); setIaError("");
    try {
      const r = await API.sugerirRiesgoProveedor(proveedorId);
      if (r.error || !r.nivel) {
        setIaError(r.justificacion || r.error || "La IA no devolvió una sugerencia válida.");
      } else {
        setForm(f => ({ ...f, riesgo_inherente:r.nivel, riesgo_inherente_just:r.justificacion || "" }));
        onChanged();
      }
    } catch (e) {
      setIaError("No se pudo contactar al motor de IA. ¿Está corriendo Ollama?");
    } finally {
      setIaLoading(false);
    }
  };

  /* Agrupar preguntas por categoría */
  const grupos = (preguntas || []).reduce((acc, q) => {
    (acc[q.categoria] = acc[q.categoria] || []).push(q); return acc;
  }, {});

  const scoring = prov?.scoring;

  const tabs = isNew
    ? [["perfil","Perfil"]]
    : [["perfil","Perfil"], ["cuestionario",`Cuestionario (${scoring?.respondidas ?? 0}/${scoring?.total ?? 0})`]];

  return (
    <Modal open={true} size="lg" onClose={onClose}
           title={isNew ? "Nuevo proveedor" : (prov?.nombre || "Proveedor")}
           sub={isNew ? "Registrá un tercero para evaluar su riesgo" : "Evaluación de riesgo de tercero">
      {loading ? <Spinner/> : (
        <div>
          {/* Tabs */}
          <div style={{ display:"flex", gap:4, marginBottom:18, borderBottom:"1px solid var(--border)", paddingBottom:10 }}>
            {tabs.map(([id,lbl]) => (
              <button key={id} className={`btn btn-sm ${tab===id ? "btn-primary" : "btn-ghost"}`} onClick={() => setTab(id)}>{lbl}</button>
            ))}
          </div>

          {tab === "perfil" && (
            <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
                <Campo label="Nombre *">
                  <input className="input" value={form.nombre} disabled={!canManage}
                         onChange={e => setF("nombre")(e.target.value)} placeholder="ej. Cloud Hosting S.A."/>
                </Campo>
                <Campo label="Tipo de servicio">
                  <input className="input" value={form.tipo_servicio} disabled={!canManage}
                         onChange={e => setF("tipo_servicio")(e.target.value)} placeholder="ej. Infraestructura cloud"/>
                </Campo>
                <Campo label="Criticidad">
                  <select className="input" value={form.criticidad} disabled={!canManage}
                          onChange={e => setF("criticidad")(e.target.value)}>
                    {TPRM_CRITICIDAD.map(c => <option key={c.v} value={c.v}>{c.label}</option>)}
                  </select>
                </Campo>
                <Campo label="Estado">
                  <select className="input" value={form.estado} disabled={!canManage}
                          onChange={e => setF("estado")(e.target.value)}>
                    {TPRM_ESTADOS.map(s => <option key={s.v} value={s.v}>{s.label}</option>)}
                  </select>
                </Campo>
                <Campo label="Contacto">
                  <input className="input" value={form.contacto_nombre} disabled={!canManage}
                         onChange={e => setF("contacto_nombre")(e.target.value)} placeholder="Nombre del contacto"/>
                </Campo>
                <Campo label="Email de contacto">
                  <input className="input" value={form.contacto_email} disabled={!canManage}
                         onChange={e => setF("contacto_email")(e.target.value)} placeholder="contacto@proveedor.com"/>
                </Campo>
              </div>
              <Campo label="Datos que maneja">
                <input className="input" value={form.datos_maneja} disabled={!canManage}
                       onChange={e => setF("datos_maneja")(e.target.value)}
                       placeholder="ej. datos personales de clientes, información financiera"/>
              </Campo>
              <Campo label="Notas">
                <textarea className="input" rows={2} value={form.notas} disabled={!canManage}
                          onChange={e => setF("notas")(e.target.value)} style={{ resize:"vertical" }}/>
              </Campo>

              {/* Riesgo inherente + IA */}
              <div style={{ background:"var(--surface-2)", border:"1px solid var(--border)", borderRadius:10, padding:14 }}>
                <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:10, marginBottom:8, flexWrap:"wrap" }}>
                  <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                    <span style={{ fontSize:12, fontWeight:700, color:"var(--text-secondary)" }}>Riesgo inherente</span>
                    {form.riesgo_inherente
                      ? <Badge tone={riesgoTone(form.riesgo_inherente)}>{riesgoLabel(form.riesgo_inherente)}</Badge>
                      : <span style={{ fontSize:12, color:"var(--text-muted)" }}>sin evaluar</span>}
                  </div>
                  {canManage && !isNew && (
                    <button className="btn btn-sm btn-secondary" onClick={sugerirRiesgo} disabled={iaLoading}>
                      {iaLoading ? <Spinner size={13}/> : <Icon.Sparkles size={13}/>}
                      {iaLoading ? "Analizando…" : "Sugerir con IA"}
                    </button>
                  )}
                </div>
                {canManage && (
                  <select className="input" value={form.riesgo_inherente} onChange={e => setF("riesgo_inherente")(e.target.value)}
                          style={{ maxWidth:200, marginBottom:8 }}>
                    <option value="">— Sin evaluar —</option>
                    <option value="bajo">Bajo</option>
                    <option value="medio">Medio</option>
                    <option value="alto">Alto</option>
                    <option value="critico">Crítico</option>
                  </select>
                )}
                {form.riesgo_inherente_just && (
                  <p style={{ margin:"4px 0 0", fontSize:12.5, color:"var(--text-secondary)", fontStyle:"italic" }}>
                    {form.riesgo_inherente_just}
                  </p>
                )}
                {iaError && <p style={{ margin:"6px 0 0", fontSize:12, color:"var(--danger)" }}>{iaError}</p>}
                {isNew && (
                  <p style={{ margin:"4px 0 0", fontSize:11.5, color:"var(--text-muted)" }}>
                    Guardá el proveedor para poder pedir la sugerencia de IA.
                  </p>
                )}
              </div>

              {error && <div style={{ padding:"8px 12px", borderRadius:8, background:"var(--danger-bg)", color:"var(--danger)", fontSize:13 }}>{error}</div>}

              {canManage && (
                <div style={{ display:"flex", justifyContent:"flex-end", gap:8 }}>
                  <button className="btn btn-ghost" onClick={onClose}>Cancelar</button>
                  <button className="btn btn-primary" onClick={guardarPerfil} disabled={saving}>
                    {saving ? <Spinner size={14}/> : <Icon.Check size={14}/>}
                    {isNew ? "Crear proveedor" : "Guardar cambios"}
                  </button>
                </div>
              )}
            </div>
          )}

          {tab === "cuestionario" && (
            <div>
              {/* Scoring resumen */}
              <div style={{ display:"flex", alignItems:"center", gap:16, background:"var(--surface-2)",
                            border:"1px solid var(--border)", borderRadius:10, padding:14, marginBottom:18 }}>
                <ScoreRing puntaje={scoring?.puntaje} nivel={scoring?.nivel_residual}/>
                <div>
                  <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                    <span style={{ fontSize:13, fontWeight:700 }}>Riesgo residual</span>
                    {scoring?.nivel_residual
                      ? <Badge tone={riesgoTone(scoring.nivel_residual)}>{riesgoLabel(scoring.nivel_residual)}</Badge>
                      : <span style={{ fontSize:12, color:"var(--text-muted)" }}>sin datos</span>}
                  </div>
                  <div style={{ fontSize:12, color:"var(--text-secondary)", marginTop:2 }}>
                    {scoring?.respondidas ?? 0} de {scoring?.total ?? 0} preguntas respondidas · puntaje ponderado por peso del control
                  </div>
                </div>
              </div>

              {/* Preguntas por categoría */}
              <div style={{ display:"flex", flexDirection:"column", gap:18 }}>
                {Object.entries(grupos).map(([cat, items]) => (
                  <div key={cat}>
                    <div style={{ fontSize:11, fontWeight:700, textTransform:"uppercase", letterSpacing:1,
                                  color:"var(--text-secondary)", marginBottom:8 }}>{cat}</div>
                    <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
                      {items.map(q => {
                        const cur = respuestas[q.id]?.respuesta || "na";
                        return (
                          <div key={q.id} style={{ background:"var(--surface-1)", border:"1px solid var(--border)", borderRadius:8, padding:"10px 12px" }}>
                            <div style={{ fontSize:13, color:"var(--text-primary)", marginBottom:8 }}>{q.texto}</div>
                            <div style={{ display:"flex", gap:6, flexWrap:"wrap" }}>
                              {TPRM_RESPUESTAS.map(opt => {
                                const sel = cur === opt.v;
                                return (
                                  <button key={opt.v} type="button" disabled={!canManage}
                                          onClick={() => setResp(q.id, "respuesta", opt.v)}
                                          style={{
                                            padding:"4px 10px", borderRadius:6, fontSize:12, fontWeight:600,
                                            cursor: canManage ? "pointer" : "default",
                                            background: sel ? opt.color+"22" : "var(--surface-2)",
                                            color: sel ? opt.color : "var(--text-secondary)",
                                            border:`1px solid ${sel ? opt.color : "var(--border)"}`,
                                          }}>
                                    {opt.label}
                                  </button>
                                );
                              })}
                            </div>
                            {canManage && (
                              <input className="input" placeholder="Comentario (opcional)…"
                                     value={respuestas[q.id]?.comentario || ""}
                                     onChange={e => setResp(q.id, "comentario", e.target.value)}
                                     style={{ marginTop:8, fontSize:12.5 }}/>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>

              {error && <div style={{ marginTop:12, padding:"8px 12px", borderRadius:8, background:"var(--danger-bg)", color:"var(--danger)", fontSize:13 }}>{error}</div>}

              {canManage && (
                <div style={{ display:"flex", justifyContent:"flex-end", gap:8, marginTop:16 }}>
                  <button className="btn btn-primary" onClick={guardarCuestionario} disabled={saving}>
                    {saving ? <Spinner size={14}/> : <Icon.Check size={14}/>}
                    Guardar y recalcular
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Modal>
  );
}

function Campo({ label, children }) {
  return (
    <div style={{ display:"flex", flexDirection:"column", gap:4 }}>
      <label style={{ fontSize:12, fontWeight:600, color:"var(--text-secondary)" }}>{label}</label>
      {children}
    </div>
  );
}

/* ── Tarjeta de proveedor ────────────────────────────────────────── */
function ProveedorCard({ p, onOpen, onDelete, canManage }) {
  const sc = p.scoring || {};
  return (
    <div className="card" style={{ padding:16, display:"flex", flexDirection:"column", gap:12, cursor:"pointer" }}
         onClick={() => onOpen(p.id)}>
      <div style={{ display:"flex", gap:12, alignItems:"flex-start" }}>
        <ScoreRing puntaje={sc.puntaje} nivel={sc.nivel_residual} size={52}/>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontSize:14, fontWeight:700, color:"var(--text-primary)", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{p.nombre}</div>
          {p.tipo_servicio && <div style={{ fontSize:12, color:"var(--text-secondary)" }}>{p.tipo_servicio}</div>}
          <div style={{ display:"flex", gap:6, marginTop:6, flexWrap:"wrap" }}>
            <Badge tone="neutral">{critLabel(p.criticidad)}</Badge>
            {p.riesgo_inherente && <Badge tone={riesgoTone(p.riesgo_inherente)} dot>Inh. {riesgoLabel(p.riesgo_inherente)}</Badge>}
          </div>
        </div>
      </div>
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", fontSize:12, color:"var(--text-muted)" }}>
        <span>{estadoLabel(p.estado)}</span>
        <span>{sc.respondidas ?? 0}/{sc.total ?? 0} resp.</span>
      </div>
      {canManage && (
        <div style={{ display:"flex", gap:6 }} onClick={e => e.stopPropagation()}>
          <button className="btn btn-ghost btn-sm" onClick={() => onOpen(p.id)} style={{ flex:1 }}>
            <Icon.Edit size={12}/> Abrir
          </button>
          <button className="btn btn-ghost btn-sm" onClick={() => onDelete(p)} style={{ color:"var(--danger)" }} title="Eliminar">
            <Icon.Trash size={12}/>
          </button>
        </div>
      )}
    </div>
  );
}

/* ── Pantalla principal: Terceros (TPRM) ─────────────────────────── */
function TPRMScreen({ user }) {
  const { data: provs, loading, reload } = useApi(() => API.proveedores());
  const { data: preguntas } = useApi(() => API.tprmPreguntas());

  const [modalId, setModalId] = useStateTprm(undefined);  // undefined=cerrado, null=nuevo, id=editar
  const [delConfirm, setDelConfirm] = useStateTprm(null);
  const [deleting, setDeleting] = useStateTprm(false);
  const [search, setSearch] = useStateTprm("");

  const canManage = user?.rol === "admin" || (user?.permisos || []).includes("tprm.gestionar");

  const lista = (provs || []).filter(p => !search || p.nombre.toLowerCase().includes(search.toLowerCase()));

  /* Stats */
  const total    = (provs || []).length;
  const criticos = (provs || []).filter(p => p.riesgo_inherente === "critico" || p.scoring?.nivel_residual === "critico").length;
  const altos    = (provs || []).filter(p => p.scoring?.nivel_residual === "alto").length;
  const sinEval  = (provs || []).filter(p => (p.scoring?.respondidas ?? 0) === 0).length;

  const handleDelete = async (p) => {
    setDeleting(true);
    try { await API.eliminarProveedor(p.id); reload(); }
    catch (e) { alert(e.message || "Error al eliminar"); }
    finally { setDeleting(false); setDelConfirm(null); }
  };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title" style={{ display:"flex", alignItems:"center", gap:10 }}>
            <Icon.Building size={20} style={{ color:"var(--accent)" }}/>
            Gestión de Terceros (TPRM)
          </div>
          <div className="page-sub">Registro de proveedores, cuestionario de seguridad y evaluación de riesgo asistida por IA.</div>
        </div>
        {canManage && (
          <button className="btn btn-primary btn-sm" onClick={() => setModalId(null)}>
            <Icon.Plus size={14}/> Nuevo proveedor
          </button>
        )}
      </div>

      {/* Stats bar */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:14, marginBottom:24 }}>
        {[
          { label:"Proveedores",      n:total,    tone:"info"    },
          { label:"Riesgo crítico",   n:criticos, tone:"danger"  },
          { label:"Riesgo alto",      n:altos,    tone:"warning" },
          { label:"Sin evaluar",      n:sinEval,  tone:"neutral" },
        ].map(s => (
          <div key={s.label} className="card" style={{ padding:"16px 18px", textAlign:"center" }}>
            <div className="mono" style={{ fontSize:26, fontWeight:800, lineHeight:1, marginBottom:4,
                 color: s.tone==="neutral" ? "var(--text-secondary)" : `var(--${s.tone})` }}>{s.n}</div>
            <div style={{ fontSize:11.5, color:"var(--text-muted)" }}>{s.label}</div>
          </div>
        ))}
      </div>

      <input className="input" placeholder="Buscar proveedor…" value={search}
             onChange={e => setSearch(e.target.value)} style={{ maxWidth:280, marginBottom:18 }}/>

      {loading ? <Spinner/> : lista.length === 0 ? (
        <Empty icon="Building" title="No hay proveedores"
               text={canManage ? "Registrá tu primer tercero para evaluar su riesgo." : "Todavía no se cargaron proveedores."}
               action={canManage ? <button className="btn btn-primary btn-sm" onClick={() => setModalId(null)}><Icon.Plus size={14}/> Nuevo proveedor</button> : null}/>
      ) : (
        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(300px, 1fr))", gap:14 }}>
          {lista.map(p => (
            <ProveedorCard key={p.id} p={p} canManage={canManage}
                           onOpen={(id) => setModalId(id)} onDelete={(pr) => setDelConfirm(pr)}/>
          ))}
        </div>
      )}

      {modalId !== undefined && (
        <ProveedorModal
          proveedorId={modalId}
          preguntas={preguntas || []}
          canManage={canManage}
          onClose={() => setModalId(undefined)}
          onChanged={reload}
        />
      )}

      {delConfirm && (
        <Modal open={true} title="Eliminar proveedor" onClose={() => setDelConfirm(null)}>
          <p style={{ fontSize:14, color:"var(--text-secondary)" }}>
            ¿Eliminar el proveedor <strong>{delConfirm.nombre}</strong> y todas sus respuestas? Esta acción no se puede deshacer.
          </p>
          <div style={{ display:"flex", justifyContent:"flex-end", gap:8, marginTop:16 }}>
            <button className="btn btn-ghost" onClick={() => setDelConfirm(null)}>Cancelar</button>
            <button className="btn btn-danger" onClick={() => handleDelete(delConfirm)} disabled={deleting}>
              {deleting ? <Spinner size={14}/> : <Icon.Trash size={14}/>} Eliminar
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

Object.assign(window, { TPRMScreen });
