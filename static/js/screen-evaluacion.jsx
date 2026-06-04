/* global React, Icon, Badge, Maturity, MaturitySelector, Modal, Spinner, useApi,
          fmtDate, sevTone, sevLabel, stateTone, stateLabel, API, InformeModal */

const { useState: useStateE, useEffect: useEffectE, useCallback: useCallbackE } = React;

// Helper: read File as base64 (strips data-URL prefix)
function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload  = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
  });
}

function EvaluacionScreen({ evalId, onBack, onNav, user }) {
  const { data: ev,       loading: le } = useApi(() => API.evaluacion(evalId),        [evalId]);
  const { data: ctrlData, loading: lc, reload: reloadCtrls } = useApi(() => API.controles(evalId), [evalId]);

  const [dominioActivo, setDominioActivo] = useStateE(null);
  const [respuestas,    setRespuestas]    = useStateE({});
  const [saving,        setSaving]        = useStateE({});
  const [newHallazgo,   setNewHallazgo]   = useStateE(null); // ctrl for new finding modal
  const [informeOpen,   setInformeOpen]   = useStateE(false);
  const [asignarOpen,   setAsignarOpen]   = useStateE(false);

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
      r[c.id] = {
        madurez:  c.madurez ?? 0,
        comentario: c.comentario ?? "",
        aplica:   c.aplica ?? 1,
        ia_madurez_sugerida:       c.ia_madurez_sugerida ?? null,
        ia_comentario:             c.ia_comentario ?? "",
        ia_pendiente_confirmacion: c.ia_pendiente_confirmacion ?? 0,
        verificado:                c.verificado ?? 0,
        verificado_por:            c.verificado_por ?? null,
        verificado_en:             c.verificado_en ?? null,
      };
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
      // Si madurez/aplica cambiaron en un control verificado, el backend
      // invalida la verificación automáticamente. Reflejarlo en local.
      const prev = respuestas[ctrl.id] || {};
      const invalidaVerificacion = prev.verificado === 1 &&
        (prev.madurez !== payload.madurez || prev.aplica !== payload.aplica);
      setRespuestas(s => ({
        ...s,
        [ctrl.id]: {
          ...s[ctrl.id],
          ...payload,
          ...(invalidaVerificacion ? { verificado: 0, verificado_por: null, verificado_en: null } : {}),
        },
      }));
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
            <button className="btn btn-ghost btn-sm" onClick={() => setAsignarOpen(true)}><Icon.Users size={13}/> Asignar usuarios</button>
          </>}
          <button className="btn btn-secondary" onClick={() => onNav("resultados")}><Icon.PieChart size={13}/> Resultados</button>
          <button className="btn btn-secondary" onClick={() => onNav("hallazgos")}><Icon.AlertTriangle size={13}/> Hallazgos</button>
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
            resp={respuestas[ctrl.id] || { madurez: ctrl.madurez ?? 0, comentario: ctrl.comentario ?? "", aplica: ctrl.aplica ?? 1, ia_madurez_sugerida: ctrl.ia_madurez_sugerida, ia_comentario: ctrl.ia_comentario ?? "", ia_pendiente_confirmacion: ctrl.ia_pendiente_confirmacion ?? 0, verificado: ctrl.verificado ?? 0, verificado_por: ctrl.verificado_por ?? null, verificado_en: ctrl.verificado_en ?? null }}
            saving={saving[ctrl.id]}
            evalId={evalId}
            user={user}
            onSave={(m, c, a) => guardar(ctrl, m, c, a)}
            onNewHallazgo={() => setNewHallazgo(ctrl)}
            onReloadCtrls={reloadCtrls}
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

      {asignarOpen && (
        <AsignarUsuariosModal evalId={evalId} onClose={() => setAsignarOpen(false)}/>
      )}
    </div>
  );
}

/* ── Modal: asociar usuarios (auditados) a la evaluación ─────────── */
function AsignarUsuariosModal({ evalId, onClose }) {
  const [usuarios, setUsuarios]   = useStateE([]);
  const [sel,      setSel]        = useStateE(new Set());
  const [loading,  setLoading]    = useStateE(true);
  const [saving,   setSaving]     = useStateE(false);

  useEffectE(() => {
    let alive = true;
    Promise.all([API.participantes().catch(() => []), API.asignados(evalId).catch(() => [])])
      .then(([todos, asignados]) => {
        if (!alive) return;
        setUsuarios(Array.isArray(todos) ? todos : []);
        setSel(new Set((Array.isArray(asignados) ? asignados : []).map(u => u.id)));
        setLoading(false);
      });
    return () => { alive = false; };
  }, [evalId]);

  const toggle = (id) => setSel(s => {
    const n = new Set(s);
    n.has(id) ? n.delete(id) : n.add(id);
    return n;
  });

  const guardar = async () => {
    setSaving(true);
    try {
      const prev = new Set((await API.asignados(evalId).catch(() => [])).map(u => u.id));
      const ahora = sel;
      const aAgregar = [...ahora].filter(id => !prev.has(id));
      const aQuitar  = [...prev].filter(id => !ahora.has(id));
      for (const id of aAgregar) await API.asignarUsuarioEval(evalId, id);
      for (const id of aQuitar)  await API.desasignarUsuarioEval(evalId, id);
      onClose();
    } catch { alert("Error al guardar las asignaciones."); }
    finally { setSaving(false); }
  };

  // Resaltar auditados (son los que típicamente se asignan a una evaluación)
  const orden = (u) => (u.rol === "auditado" ? 0 : 1);
  const lista = [...usuarios].sort((a, b) => orden(a) - orden(b));

  return (
    <Modal open={true} onClose={onClose}
      title="Asignar usuarios a la evaluación"
      sub="Asociá los usuarios (auditados) que podrán acceder y responder esta evaluación"
      footer={<>
        <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={guardar} disabled={saving || loading}>
          {saving ? <Icon.Loader size={13}/> : <Icon.Check size={13}/>} Guardar
        </button>
      </>}>
      {loading ? <Spinner/> : usuarios.length === 0 ? (
        <div style={{ fontSize:13, color:"var(--text-muted)" }}>No hay usuarios disponibles.</div>
      ) : (
        <div style={{ display:"flex", flexDirection:"column", gap:6, maxHeight:380, overflowY:"auto" }}>
          {lista.map(u => {
            const checked = sel.has(u.id);
            return (
              <label key={u.id} style={{
                display:"flex", alignItems:"center", gap:10, padding:"9px 11px", borderRadius:8,
                cursor:"pointer", background: checked ? "var(--accent-bg)" : "var(--surface-2)",
                border:`1px solid ${checked ? "var(--accent)" : "var(--border)"}`,
              }}>
                <input type="checkbox" checked={checked} onChange={() => toggle(u.id)}
                       style={{ accentColor:"var(--accent)" }}/>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontSize:13, fontWeight:600 }}>{u.nombre || u.username}</div>
                  <div style={{ fontSize:11.5, color:"var(--text-muted)" }} className="mono">@{u.username}</div>
                </div>
                <Badge tone={u.rol === "auditado" ? "warning" : "neutral"}>{ROLE_SHORT[u.rol] || u.rol}</Badge>
              </label>
            );
          })}
        </div>
      )}
    </Modal>
  );
}

function ControlRow({ ctrl, resp, saving, evalId, user, onSave, onNewHallazgo, onReloadCtrls }) {
  const [open,         setOpen]         = useStateE(false);
  const [aplica,       setAplica]       = useStateE(resp.aplica !== 0);
  const [confirmingIa, setConfirmingIa] = useStateE(false);
  const [verifying,    setVerifying]    = useStateE(false);

  useEffectE(() => { setAplica(resp.aplica !== 0); }, [resp.aplica]);

  // El comentario "oficial" de la respuesta se preserva tal cual está en DB
  // (la observación/discusión ahora vive 100% en DiscusionThread).
  const comentarioPersist = resp.comentario || "";

  const m          = resp.madurez ?? 0;
  const isBad      = aplica && m < 3;
  const hasIaSug   = resp.ia_pendiente_confirmacion === 1 && resp.ia_madurez_sugerida != null;
  const verificado = resp.verificado === 1;
  const canVerify  = user && (user.rol === "admin" || user.rol === "analista");

  const status = !aplica
    ? <Badge tone="neutral">No aplica</Badge>
    : m === 0
      ? <Badge tone="neutral">Sin evaluar</Badge>
      : isBad
        ? <Badge tone="danger" dot>Brecha</Badge>
        : <Badge tone="success" dot>Cumple</Badge>;

  const handleConfirmIa = async (confirmar) => {
    setConfirmingIa(true);
    try {
      await API.confirmarIa(evalId, ctrl.id, confirmar);
      if (onReloadCtrls) onReloadCtrls();
    } catch { alert("Error al procesar la sugerencia de IA."); }
    finally { setConfirmingIa(false); }
  };

  const handleVerificar = async (e) => {
    e.stopPropagation();
    setVerifying(true);
    try {
      await API.verificarControl(evalId, ctrl.id);
      if (onReloadCtrls) onReloadCtrls();
    } catch { alert("Error al verificar el control."); }
    finally { setVerifying(false); }
  };

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
          {hasIaSug && <Badge tone="accent" dot>IA pendiente</Badge>}
          {!hasIaSug && status}
          {verificado && (
            <span title={`Verificado${resp.verificado_en ? " el " + fmtDateTime(resp.verificado_en) : ""}`}
                  style={{ display:"inline-flex", alignItems:"center", gap:3, fontSize:11, fontWeight:600,
                           color:"#10b981", background:"rgba(16,185,129,.12)", border:"1px solid rgba(16,185,129,.3)",
                           padding:"2px 7px", borderRadius:10 }}>
              <Icon.ShieldCheck size={11}/> Verificado
            </span>
          )}
          <Icon.ChevronDown size={14} style={{ color:"var(--text-faint)", transform: open ? "rotate(180deg)" : "none", transition:"transform .15s" }}/>
        </div>
      </div>

      {open && (
        <div className="ctrl-expand">

          {/* ── IA Suggestion Banner ── */}
          {hasIaSug && (
            <div style={{
              background:"linear-gradient(135deg,rgba(99,102,241,.08),rgba(139,92,246,.08))",
              border:"1px solid rgba(99,102,241,.3)", borderRadius:10, padding:"14px 16px",
              marginBottom:14
            }}>
              <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:8 }}>
                <Icon.Cpu size={14} style={{ color:"var(--accent)", flexShrink:0 }}/>
                <span style={{ fontWeight:700, fontSize:13, color:"var(--accent)" }}>Sugerencia de IA</span>
                <Badge tone="accent">Madurez {resp.ia_madurez_sugerida}/5</Badge>
              </div>
              {resp.ia_comentario && (
                <p style={{ fontSize:12.5, color:"var(--text-secondary)", margin:"0 0 12px", lineHeight:1.55 }}>
                  {resp.ia_comentario}
                </p>
              )}
              <div style={{ display:"flex", gap:8 }}>
                <button className="btn btn-primary btn-sm" onClick={() => handleConfirmIa(true)} disabled={confirmingIa}>
                  {confirmingIa ? <Icon.Loader size={12}/> : <><Icon.Check size={12}/> Confirmar resultado</>}
                </button>
                <button className="btn btn-secondary btn-sm" onClick={() => handleConfirmIa(false)} disabled={confirmingIa}>
                  <Icon.X size={12}/> Evaluar manualmente
                </button>
              </div>
            </div>
          )}

          <div style={{ display:"flex", alignItems:"center", gap:16, flexWrap:"wrap" }}>
            <label style={{ display:"flex", alignItems:"center", gap:6, fontSize:12.5, color:"var(--text-secondary)", cursor:"pointer", userSelect:"none" }}>
              <input type="checkbox" checked={aplica} onChange={e => { setAplica(e.target.checked); onSave(m, comentarioPersist, e.target.checked ? 1 : 0); }} style={{ accentColor:"var(--accent)" }}/>
              Aplica
            </label>
            <MaturitySelector value={m} disabled={!aplica} onChange={v => onSave(v, comentarioPersist, aplica ? 1 : 0)}/>
            {saving && <Icon.Loader size={13} style={{ color:"var(--accent)", animation:"spin 1s linear infinite" }}/>}
          </div>

          <div style={{ display:"flex", gap:8, alignItems:"center", flexWrap:"wrap" }}>
            {isBad && (
              <button className="btn btn-sm btn-secondary" onClick={e => { e.stopPropagation(); onNewHallazgo(); }}>
                <Icon.Plus size={12}/> Registrar hallazgo
              </button>
            )}
            {canVerify && !verificado && (
              <button className="btn btn-sm" onClick={handleVerificar} disabled={verifying}
                style={{ background:"#10b981", color:"#fff", border:"none" }}>
                {verifying ? <Icon.Loader size={12}/> : <><Icon.ShieldCheck size={12}/> Verificar</>}
              </button>
            )}
            {verificado && (
              <span style={{ fontSize:11.5, color:"#10b981", display:"inline-flex", alignItems:"center", gap:4 }}>
                <Icon.ShieldCheck size={12}/>
                Verificado{resp.verificado_en ? ` el ${fmtDateTime(resp.verificado_en)}` : ""}
              </span>
            )}
            <EvidenciasInline evalId={evalId} ctrlId={ctrl.id}/>
          </div>

          {/* ── Discusión ── */}
          <DiscusionThread evalId={evalId} ctrlId={ctrl.id}/>
        </div>
      )}
    </div>
  );
}

// ── Helpers ───────────────────────────────────────────────────────
const fmtDateTime = (s) => {
  if (!s) return "—";
  const d = new Date(s.endsWith("Z") ? s : s + "Z"); // treat as UTC
  if (isNaN(d)) return s;
  return d.toLocaleString("es-AR", { day:"2-digit", month:"short", year:"numeric", hour:"2-digit", minute:"2-digit" });
};

const ROLE_SHORT = { admin:"Adm", analista:"Analista GRC", auditado:"Auditado", auditor_externo:"Auditor", ia:"IA Local" };
const ROLE_COLOR = { admin:"var(--accent)", analista:"#10b981", auditado:"#f59e0b", auditor_externo:"#6366f1", ia:"#a855f7" };

function initials(nombre) {
  return (nombre || "?").split(" ").map(w => w[0]).join("").slice(0,2).toUpperCase();
}

// ── DiscusionThread ───────────────────────────────────────────────
function DiscusionThread({ evalId, ctrlId }) {
  const { data, loading, reload } = useApi(() => API.comentariosControl(evalId, ctrlId), [evalId, ctrlId]);
  const comentarios = data || [];

  const [texto,    setTexto]    = useStateE("");
  const [enviando, setEnviando] = useStateE(false);
  const [open,     setOpen]     = useStateE(false);

  const totalComentarios = comentarios.length;

  const enviar = async () => {
    if (!texto.trim()) return;
    setEnviando(true);
    try {
      await API.agregarComentario(evalId, ctrlId, texto.trim());
      setTexto("");
      reload();
    } catch(e) { alert("Error al enviar comentario."); }
    finally { setEnviando(false); }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) enviar();
  };

  return (
    <div style={{ borderTop:"1px solid var(--border)", marginTop:6, paddingTop:10 }}>
      {/* Toggle */}
      <button className="btn btn-ghost btn-sm"
        onClick={() => setOpen(!open)}
        style={{ padding:"3px 8px", fontSize:12, color:"var(--text-muted)" }}>
        <Icon.MessageSquare size={12} style={{ marginRight:4 }}/>
        Discusión {totalComentarios > 0 && <span style={{ marginLeft:4, background:"var(--accent)", color:"#fff", borderRadius:9, padding:"1px 6px", fontSize:10.5 }}>{totalComentarios}</span>}
        <Icon.ChevronDown size={11} style={{ marginLeft:4, transform: open?"rotate(180deg)":"none", transition:"transform .15s" }}/>
      </button>

      {open && (
        <div style={{ marginTop:10, display:"flex", flexDirection:"column", gap:0 }}>

          {/* Lista de comentarios */}
          {loading
            ? <div style={{ fontSize:12, color:"var(--text-muted)", padding:"6px 0" }}><Icon.Loader size={13} style={{ animation:"spin 1s linear infinite" }}/> Cargando...</div>
            : comentarios.length === 0
              ? <div style={{ fontSize:12, color:"var(--text-faint)", padding:"4px 0 10px" }}>Sin comentarios aún. Sé el primero.</div>
              : comentarios.map((c, idx) => {
                  const nombre  = c.u_nombre || c.usuario_nombre || "Usuario";
                  const rol     = c.u_rol    || c.usuario_rol    || "";
                  const rolLabel = ROLE_SHORT[rol] || rol;
                  const color   = ROLE_COLOR[rol]  || "var(--text-muted)";
                  const isLast  = idx === comentarios.length - 1;
                  return (
                    <div key={c.id} style={{ display:"flex", gap:10, paddingBottom: isLast ? 10 : 14, position:"relative" }}>
                      {/* Línea de tiempo */}
                      {!isLast && <div style={{ position:"absolute", left:14, top:30, bottom:0, width:2, background:"var(--border)" }}/>}
                      {/* Avatar */}
                      <div style={{ flexShrink:0, width:28, height:28, borderRadius:"50%", background:color, display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:700, color:"#fff", zIndex:1 }}>
                        {rol === "ia" ? <Icon.Cpu size={14}/> : initials(nombre)}
                      </div>
                      {/* Burbuja */}
                      <div style={{ flex:1, minWidth:0 }}>
                        <div style={{ display:"flex", alignItems:"baseline", gap:8, flexWrap:"wrap", marginBottom:4 }}>
                          <span style={{ fontWeight:600, fontSize:12.5, color:"var(--text-primary)" }}>{nombre}</span>
                          {rolLabel && <span style={{ fontSize:10.5, color:color, fontWeight:600 }}>{rolLabel}</span>}
                          <span style={{ fontSize:11, color:"var(--text-faint)" }}>{fmtDateTime(c.creado_en)}</span>
                        </div>
                        <div style={{ background:"var(--surface-2)", border:"1px solid var(--border)", borderRadius:"0 8px 8px 8px", padding:"8px 12px", fontSize:12.5, color:"var(--text-primary)", lineHeight:1.55, whiteSpace:"pre-wrap", wordBreak:"break-word" }}>
                          {c.texto}
                        </div>
                      </div>
                    </div>
                  );
                })
          }

          {/* Input nuevo comentario */}
          <div style={{ display:"flex", flexDirection:"column", gap:6, marginTop:4 }}>
            <textarea
              className="textarea"
              rows={2}
              placeholder="Escribí un comentario… (Ctrl+Enter para enviar)"
              value={texto}
              onChange={e => setTexto(e.target.value)}
              onKeyDown={handleKey}
              style={{ fontSize:13 }}
            />
            <div style={{ display:"flex", justifyContent:"flex-end" }}>
              <button className="btn btn-primary btn-sm"
                onClick={enviar}
                disabled={enviando || !texto.trim()}>
                {enviando
                  ? <Icon.Loader size={12}/>
                  : <><Icon.Send size={12}/> Enviar</>}
              </button>
            </div>
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
    if (file.size > 20 * 1024 * 1024) {
      alert("El archivo supera el límite de 20 MB.");
      e.target.value = "";
      return;
    }
    try {
      const data = await fileToBase64(file);
      await API.subirEvidencia(evalId, ctrlId, { filename: file.name, data });
      reload();
    } catch (err) {
      const msg = err?.message || "Error al subir evidencia";
      alert(msg.includes("IA") ? msg : "Error al subir el archivo. Verificá el formato y tamaño.");
    }
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
            evidencias.map(ev => {
              const vTone = { cumple:"success", no_cumple:"danger", parcial:"warning" }[ev.veredicto] || "neutral";
              const analisis = ev.analisis_ia ? (() => { try { return JSON.parse(ev.analisis_ia); } catch { return null; }})() : null;
              return (
                <div key={ev.id} style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:7, padding:"8px 12px", fontSize:12 }}>
                  <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                    <Icon.FileText size={13} style={{ color:"var(--text-muted)", flexShrink:0 }}/>
                    <span style={{ flex:1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{ev.filename}</span>
                    <a className="btn btn-ghost btn-icon" href={API.evidenciaDownloadUrl(ev.id)}
                       title="Descargar" onClick={e => e.stopPropagation()}>
                      <Icon.Download size={12}/>
                    </a>
                    <Badge tone={vTone}>{ev.veredicto || "pendiente"}</Badge>
                  </div>
                  {analisis?.resumen && (
                    <div style={{ marginTop:5, color:"var(--text-muted)", fontSize:11.5, lineHeight:1.5, paddingLeft:21 }}>
                      <Icon.Cpu size={10} style={{ marginRight:4, color:"var(--accent)" }}/>{analisis.resumen}
                    </div>
                  )}
                </div>
              );
            })}

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
  const [sev,           setSev]           = useStateE("media");
  const [responsableId, setResponsableId] = useStateE("");
  const [fecha,         setFecha]         = useStateE("");
  const [plan,          setPlan]          = useStateE("");
  const [loading,       setLoading]       = useStateE(false);
  const [users,         setUsers]         = useStateE([]);

  useEffectE(() => {
    API.participantes().then(rows => setUsers(Array.isArray(rows) ? rows : [])).catch(() => setUsers([]));
  }, []);

  const submit = async () => {
    setLoading(true);
    try {
      await API.crearHallazgo(evalId, {
        control_id: ctrl.id, titulo, descripcion: desc, severidad: sev,
        responsable_id: responsableId ? Number(responsableId) : null,
        fecha_limite: fecha, plan_accion: plan,
      });
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
      <div className="field">
        <label>Responsable</label>
        <select className="select" value={responsableId} onChange={e=>setResponsableId(e.target.value)}>
          <option value="">— Sin asignar —</option>
          {users.map(u => (
            <option key={u.id} value={String(u.id)}>
              {(u.nombre || u.username)} · {ROLE_SHORT[u.rol] || u.rol}
            </option>
          ))}
        </select>
      </div>
      <div className="field"><label>Plan de acción</label><textarea className="textarea" rows={2} value={plan} onChange={e=>setPlan(e.target.value)} placeholder="Describí los pasos para remediar…"/></div>
    </Modal>
  );
}

Object.assign(window, { EvaluacionScreen });
