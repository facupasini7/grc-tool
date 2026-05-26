/* global React, Icon, Badge, Modal, Spinner, Empty, useApi, fmtDate, API */
const { useState: useStateDL, useEffect: useEffectDL, useCallback: useCallbackDL } = React;

function diasRestantes(fecha) {
  if (!fecha) return null;
  const diff = Math.ceil((new Date(fecha) - new Date()) / 86400000);
  return diff;
}

function urgencyTone(dias) {
  if (dias === null) return "neutral";
  if (dias < 0)  return "neutral";
  if (dias <= 2) return "danger";
  if (dias <= 7) return "warning";
  return "success";
}

function urgencyLabel(dias) {
  if (dias === null) return "—";
  if (dias < 0)  return "Vencido";
  if (dias === 0) return "Hoy";
  if (dias === 1) return "Mañana";
  return `${dias}d`;
}

/* ── Modal nuevo deadline ─────────────────────────────────────── */
function DeadlineModal({ open, onClose, evalId, participantes }) {
  const [ctrl,    setCtrl]   = useStateDL("");
  const [userId,  setUserId] = useStateDL("");
  const [fecha,   setFecha]  = useStateDL("");
  const [dias,    setDias]   = useStateDL(3);
  const [saving,  setSaving] = useStateDL(false);

  useEffectDL(() => {
    if (open) { setCtrl(""); setUserId(""); setFecha(""); setDias(3); }
  }, [open]);

  const submit = async () => {
    if (!ctrl.trim() || !userId || !fecha) {
      alert("Completá todos los campos requeridos."); return;
    }
    setSaving(true);
    try {
      await API.crearDeadline(evalId, {
        control_id: ctrl.trim(), asignado_a: +userId,
        fecha_limite: fecha, recordatorio_dias: +dias,
      });
      onClose(true);
    } catch (e) { alert("Error al guardar: " + e.message); }
    finally { setSaving(false); }
  };

  return (
    <Modal open={open} onClose={() => onClose(false)}
      title="Nuevo deadline de evidencia"
      sub="Asigná un vencimiento a un auditado para subir evidencia de un control"
      footer={<>
        <button className="btn btn-secondary" onClick={() => onClose(false)}>Cancelar</button>
        <button className="btn btn-primary" onClick={submit} disabled={saving}>
          {saving ? <Icon.Loader size={13}/> : <><Icon.Check size={13}/> Guardar</>}
        </button>
      </>}
    >
      <div className="field">
        <label>Control ISO 27001 *</label>
        <input className="input" value={ctrl} onChange={e => setCtrl(e.target.value)}
          placeholder="Ej: A.5.1, A.9.4.2…"/>
      </div>
      <div className="field">
        <label>Auditado responsable *</label>
        <select className="select" value={userId} onChange={e => setUserId(e.target.value)}>
          <option value="">Seleccioná un usuario</option>
          {(participantes||[]).filter(p => p.rol === "auditado" || p.rol === "analista")
            .map(p => (
              <option key={p.id} value={p.id}>{p.nombre} ({p.rol})</option>
          ))}
        </select>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
        <div className="field">
          <label>Fecha límite *</label>
          <input className="input" type="date" value={fecha} onChange={e => setFecha(e.target.value)}
            min={new Date().toISOString().slice(0,10)}/>
        </div>
        <div className="field">
          <label>Recordar con anticipación</label>
          <select className="select" value={dias} onChange={e => setDias(e.target.value)}>
            {[1,2,3,5,7,14].map(d => <option key={d} value={d}>{d} día{d>1?"s":""} antes</option>)}
          </select>
        </div>
      </div>
      <div style={{ background:"var(--surface-2)", borderRadius:8, padding:"12px 14px",
        fontSize:12.5, color:"var(--text-secondary)", display:"flex", gap:8, alignItems:"flex-start" }}>
        <Icon.Mail size={14} style={{ color:"var(--accent)", flexShrink:0, marginTop:1 }}/>
        <span>
          El sistema enviará un email de recordatorio al auditado cuando falten
          {" "}<strong>{dias} día{+dias>1?"s":""}</strong> para el vencimiento (si está configurado el SMTP).
        </span>
      </div>
    </Modal>
  );
}

/* ── Pantalla principal ───────────────────────────────────────── */
function DeadlinesScreen({ evalId, onBack }) {
  const [modal, setModal] = useStateDL(false);

  const { data: _dlData, loading, reload } = useApi(
    () => evalId ? API.deadlines(evalId) : Promise.resolve([]), [evalId]
  );
  const { data: _partData } = useApi(() => API.participantes(), []);

  const deadlines    = Array.isArray(_dlData)   ? _dlData   : [];
  const participantes = Array.isArray(_partData) ? _partData : [];

  const eliminar = async (id) => {
    if (!confirm("¿Eliminar este deadline?")) return;
    await API.eliminarDeadline(id);
    reload();
  };

  const vencidos   = deadlines.filter(d => diasRestantes(d.fecha_limite) < 0);
  const hoy        = deadlines.filter(d => diasRestantes(d.fecha_limite) === 0);
  const proximosSemana = deadlines.filter(d => { const r = diasRestantes(d.fecha_limite); return r >= 1 && r <= 7; });
  const restantes  = deadlines.filter(d => diasRestantes(d.fecha_limite) > 7);

  const groups = [
    { label:"Vencidos", items:vencidos,        tone:"danger"  },
    { label:"Vence hoy", items:hoy,            tone:"danger"  },
    { label:"Esta semana", items:proximosSemana,tone:"warning" },
    { label:"Próximos", items:restantes,        tone:"success" },
  ].filter(g => g.items.length > 0);

  return (
    <div className="page">
      <div className="page-head">
        <div>
          {onBack && <button className="btn btn-ghost btn-sm" style={{ marginBottom:8 }} onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>}
          <div className="page-title">Deadlines de Evidencia</div>
          <div className="page-sub">
            Gestioná los vencimientos para subida de evidencias por parte de auditados.
          </div>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost btn-sm" onClick={reload}><Icon.Refresh size={13}/></button>
          <button className="btn btn-primary" onClick={() => setModal(true)}>
            <Icon.Plus size={14}/> Nuevo deadline
          </button>
        </div>
      </div>

      {/* Alerta si hay vencidos */}
      {vencidos.length > 0 && (
        <div style={{ background:"var(--danger-soft)", border:"1px solid var(--danger-border)",
          borderRadius:10, padding:"12px 16px", display:"flex", gap:10,
          alignItems:"center", marginBottom:16 }}>
          <Icon.AlertOctagon size={16} style={{ color:"var(--danger)", flexShrink:0 }}/>
          <span style={{ fontSize:13 }}>
            <strong>{vencidos.length} deadline{vencidos.length>1?"s":""} vencido{vencidos.length>1?"s":""}.</strong>
            {" "}Revisá el estado de la evidencia correspondiente.
          </span>
        </div>
      )}

      {loading ? <Spinner/> : deadlines.length === 0 ? (
        <Empty icon="Calendar" title="Sin deadlines configurados"
          text="Asigná fechas límite a los auditados para que suban evidencias de los controles."
          action={<button className="btn btn-primary" onClick={() => setModal(true)}><Icon.Plus size={13}/> Nuevo deadline</button>}/>
      ) : (
        groups.map(group => (
          <div key={group.label} style={{ marginBottom:24 }}>
            <div style={{ fontWeight:700, fontSize:13, color:"var(--text-secondary)",
              textTransform:"uppercase", letterSpacing:".06em", marginBottom:10 }}>
              <Badge tone={group.tone} dot>{group.label}</Badge>
            </div>
            <div className="card tbl-card">
              <table className="tbl">
                <thead><tr>
                  <th style={{ width:100 }}>Control</th>
                  <th style={{ width:180 }}>Auditado</th>
                  <th style={{ width:130 }}>Fecha límite</th>
                  <th style={{ width:90 }}>Restante</th>
                  <th style={{ width:90 }}>Recordatorio</th>
                  <th style={{ width:80 }}>Notif. env.</th>
                  <th style={{ width:50 }}></th>
                </tr></thead>
                <tbody>
                  {group.items.map(d => {
                    const dias = diasRestantes(d.fecha_limite);
                    return (
                      <tr key={d.id}>
                        <td><span className="mono" style={{ fontSize:12 }}>{d.control_id}</span></td>
                        <td>
                          <div style={{ display:"flex", alignItems:"center", gap:7 }}>
                            <div style={{ width:24, height:24, borderRadius:"50%",
                              background:"var(--accent-soft)", color:"var(--accent)",
                              display:"flex", alignItems:"center", justifyContent:"center",
                              fontSize:10, fontWeight:700, flexShrink:0 }}>
                              {(d.asignado_nombre||"?").slice(0,2).toUpperCase()}
                            </div>
                            <div>
                              <div style={{ fontSize:13, fontWeight:500 }}>{d.asignado_nombre}</div>
                              {d.asignado_email && <div style={{ fontSize:11, color:"var(--text-muted)" }}>{d.asignado_email}</div>}
                            </div>
                          </div>
                        </td>
                        <td><span className="mono" style={{ fontSize:12 }}>{fmtDate(d.fecha_limite)}</span></td>
                        <td>
                          <Badge tone={urgencyTone(dias)}>{urgencyLabel(dias)}</Badge>
                        </td>
                        <td style={{ fontSize:12.5, color:"var(--text-secondary)" }}>
                          {d.recordatorio_dias}d antes
                        </td>
                        <td>
                          {d.notificado > 0
                            ? <Badge tone="success">{d.notificado}</Badge>
                            : <span style={{ color:"var(--text-faint)", fontSize:12 }}>—</span>}
                        </td>
                        <td>
                          <button className="btn btn-ghost btn-icon" style={{ color:"var(--danger)" }}
                            onClick={() => eliminar(d.id)}>
                            <Icon.Trash size={13}/>
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))
      )}

      <DeadlineModal open={modal} onClose={(saved) => { setModal(false); if (saved) reload(); }}
        evalId={evalId} participantes={participantes}/>
    </div>
  );
}

Object.assign(window, { DeadlinesScreen });
