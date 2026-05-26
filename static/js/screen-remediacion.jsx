/* global React, Icon, Badge, Spinner, useApi, fmtDate, sevTone, sevLabel, stateLabel, API */

const { useState: useStateRem } = React;

function RemediacionScreen({ evalId, onBack }) {
  const { data, loading, reload } = useApi(() => API.hallazgos(evalId), [evalId]);

  const hallazgos = data?.hallazgos || data || [];

  const COLS = [
    { key:"abierto",    label:"Abierto",    dot:"#f87171" },
    { key:"en_proceso", label:"En proceso", dot:"#fbbf24" },
    { key:"resuelto",   label:"Resuelto",   dot:"#4ade80" },
    { key:"verificado", label:"Verificado", dot:"#818cf8" },
  ];

  const advance = async (h) => {
    const order = ["abierto","en_proceso","resuelto","verificado"];
    const next  = order[order.indexOf(h.estado) + 1];
    if (!next) return;
    try { await API.avanzarEstado(h.id, next); reload(); }
    catch { alert("Error al actualizar estado"); }
  };

  const openCount    = hallazgos.filter(h => h.estado === "abierto").length;
  const critCount    = hallazgos.filter(h => h.severidad === "critica").length;
  const overdueCount = hallazgos.filter(h => h.fecha_limite && new Date(h.fecha_limite) < new Date() && h.estado !== "verificado").length;
  const doneCount    = hallazgos.filter(h => h.estado === "verificado" || h.estado === "resuelto").length;

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
          { label:"Resueltos",           n:doneCount,    tone:"success" },
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
                    const overdue = h.fecha_limite && new Date(h.fecha_limite) < new Date() && h.estado !== "verificado";
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
                        {col.key !== "verificado" && (
                          <div style={{ display:"flex", justifyContent:"flex-end" }}>
                            <button className="btn btn-xs btn-secondary" onClick={() => advance(h)}>
                              <Icon.ArrowRight size={10}/> {stateLabel(["abierto","en_proceso","resuelto","verificado"][["abierto","en_proceso","resuelto"].indexOf(col.key)+1])}
                            </button>
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
