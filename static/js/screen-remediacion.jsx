/* global React, Icon, Badge, Spinner, useApi, fmtDate, sevTone, sevLabel, stateLabel, stateTone, API */

const { useState: useStateRem } = React;

/* ── Modelo de estados (espejo de screen-hallazgos.jsx) ──────────────── */
const REM_STATES = ["incompleto", "pendiente", "implementado", "normalizado", "cerrado_no_aplica"];
const REM_DOTS = {
  incompleto:        "#94a3b8",
  pendiente:         "#fbbf24",
  implementado:      "#38bdf8",
  normalizado:       "#4ade80",
  cerrado_no_aplica: "#a78bfa",
};
const REM_DONE = new Set(["normalizado", "cerrado_no_aplica", "resuelto", "verificado"]);
const REM_ABIERTOS = ["incompleto", "pendiente", "implementado"];

/* Próximo estado natural según el rol (idéntico a nextStateForRole de Hallazgos).
   Flujo: incompleto → pendiente → implementado → normalizado (terminal). */
function remNextState(h, user) {
  const rol = user?.rol;
  const esStaff = rol === "admin" || rol === "analista";
  if (esStaff) {
    const NATURAL = { incompleto: "pendiente", implementado: "normalizado" };
    return NATURAL[h.estado] || null;
  }
  if (rol === "auditado") {
    if (h.estado === "pendiente" && h.responsable_id === user?.id) return "implementado";
  }
  return null;
}

/* El staff puede cerrar como "No aplica" desde cualquier estado abierto. */
function remCanNoAplica(h, user) {
  const esStaff = user?.rol === "admin" || user?.rol === "analista";
  return esStaff && REM_ABIERTOS.includes(h.estado);
}

function RemediacionScreen({ evalId, user, onBack }) {
  const { data, loading, reload } = useApi(() => API.hallazgos(evalId), [evalId]);

  const hallazgos = data?.hallazgos || data || [];

  const COLS = REM_STATES.map(key => ({ key, label: stateLabel(key), dot: REM_DOTS[key] }));

  const advance = async (h) => {
    const next = remNextState(h, user);
    if (!next) return;
    try { await API.avanzarEstado(h.id, next); reload(); }
    catch { alert("Error al actualizar estado"); }
  };

  const noAplica = async (h) => {
    if (!confirm("¿Cerrar este hallazgo como «No aplica»?\n\nUsalo cuando el hallazgo ya no aplica (p. ej. el control dejó de aplicar porque la herramienta observada ya no existe).")) return;
    try { await API.avanzarEstado(h.id, "cerrado_no_aplica"); reload(); }
    catch { alert("Error al actualizar estado"); }
  };

  const isOpen       = (h) => !REM_DONE.has(h.estado);
  const openCount    = hallazgos.filter(isOpen).length;
  const critCount    = hallazgos.filter(h => h.severidad === "critica").length;
  const overdueCount = hallazgos.filter(h => h.fecha_limite && new Date(h.fecha_limite) < new Date() && isOpen(h)).length;
  const doneCount    = hallazgos.filter(h => REM_DONE.has(h.estado)).length;

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Plan de Remediación</div>
          <div className="page-sub">Tablero kanban para gestionar el avance de hallazgos y planes de acción.</div>
        </div>
        {onBack && <button className="btn btn-ghost btn-sm" onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>}
      </div>

      {/* Stats bar */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:14, marginBottom:24 }}>
        {[
          { label:"Hallazgos abiertos",  n:openCount,    tone:"danger"  },
          { label:"Críticos",            n:critCount,    tone:"danger"  },
          { label:"Vencidos",            n:overdueCount, tone:"warning" },
          { label:"Cerrados",            n:doneCount,    tone:"success" },
        ].map(s => (
          <div key={s.label} className="card" style={{ padding:"16px 18px", textAlign:"center" }}>
            <div className="mono" style={{ fontSize:26, fontWeight:800, lineHeight:1, marginBottom:4, color:`var(--${s.tone})` }}>{s.n}</div>
            <div style={{ fontSize:11.5, color:"var(--text-muted)" }}>{s.label}</div>
          </div>
        ))}
      </div>

      {loading ? <Spinner/> : (
        <div className="kanban">
          {COLS.map(col => {
            const cards = hallazgos.filter(h => h.estado === col.key);
            return (
              <div key={col.key} className="kanban-col">
                <div className="kanban-head">
                  <span className="dot" style={{ background:col.dot }}/>
                  <span className="kanban-col-title">{col.label}</span>
                  <span className="kanban-col-count">{cards.length}</span>
                </div>
                <div className="kanban-list">
                  {cards.length === 0 ? (
                    <div style={{ padding:"20px 8px", textAlign:"center", fontSize:12, color:"var(--text-muted)" }}>Sin hallazgos</div>
                  ) : cards.map(h => {
                    const overdue = h.fecha_limite && new Date(h.fecha_limite) < new Date() && !REM_DONE.has(h.estado);
                    const next    = remNextState(h, user);
                    return (
                      <div key={h.id} className="kanban-card">
                        <div className="kanban-card-meta">
                          <Badge tone={sevTone(h.severidad)}>{sevLabel(h.severidad)}</Badge>
                          <span className="tag-mono">{h.control_id || h.ctrl}</span>
                        </div>
                        <div className="kanban-card-title">{h.titulo}</div>
                        <div className="kanban-card-foot">
                          {h.responsable_nombre && <span style={{ display:"flex",alignItems:"center",gap:3 }}><Icon.User size={10}/>{h.responsable_nombre}</span>}
                          {h.fecha_limite && (
                            <span style={{ color: overdue?"var(--danger)":"var(--text-muted)", fontWeight: overdue?700:400, display:"flex", alignItems:"center", gap:3 }}>
                              <Icon.Calendar size={10}/>
                              {new Date(h.fecha_limite).toLocaleDateString("es-AR",{day:"2-digit",month:"short"})}
                              {overdue && " · VENCIDO"}
                            </span>
                          )}
                        </div>
                        {(next || remCanNoAplica(h, user)) && (
                          <div style={{ display:"flex", justifyContent:"flex-end", gap:6 }}>
                            {remCanNoAplica(h, user) && (
                              <button className="btn btn-xs btn-ghost" onClick={() => noAplica(h)} title="Cerrar como «No aplica»">
                                <Icon.AlertOctagon size={10}/> No aplica
                              </button>
                            )}
                            {next && (
                              <button className="btn btn-xs btn-secondary" onClick={() => advance(h)}>
                                <Icon.ArrowRight size={10}/> {stateLabel(next)}
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

Object.assign(window, { RemediacionScreen });
