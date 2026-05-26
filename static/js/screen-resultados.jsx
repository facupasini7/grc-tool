/* global React, Icon, Badge, Maturity, Spinner, useApi, fmtDate, sevTone, sevLabel, API */

const { useState: useStateR } = React;

function ResultadosScreen({ evalId, onBack }) {
  const { data: ev,      loading: le } = useApi(() => API.evaluacion(evalId),  [evalId]);
  const { data: ctrls,   loading: lc } = useApi(() => API.controles(evalId),   [evalId]);
  const { data: findData,loading: lf } = useApi(() => API.hallazgos(evalId),   [evalId]);

  if (le || lc || lf) return <Spinner/>;

  const controles  = ctrls?.controles || ctrls || [];
  const hallazgos  = findData?.hallazgos || findData || [];

  if (!controles.length) return (
    <div className="page">
      <div className="page-head"><div><div className="page-title">Resultados</div></div><button className="btn btn-ghost btn-sm" onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button></div>
      <div className="empty"><div className="empty-icon"><Icon.PieChart size={22}/></div><div className="empty-title">Sin datos</div><div className="empty-text">Evaluá controles primero para ver los resultados.</div></div>
    </div>
  );

  // Build domain stats
  const domains = {};
  controles.forEach(c => {
    if (!domains[c.dominio]) domains[c.dominio] = { id: c.dominio, name: c.dominio_nombre || c.dominio, ctrls: [], total: 0, answered: 0, sumMat: 0 };
    domains[c.dominio].ctrls.push(c);
    domains[c.dominio].total++;
    if (c.madurez > 0) { domains[c.dominio].answered++; domains[c.dominio].sumMat += c.madurez; }
  });
  const domList = Object.values(domains);

  const totalCtrls  = controles.length;
  const answered    = controles.filter(c => c.madurez > 0).length;
  const avgMat      = answered ? (controles.reduce((s,c) => s + (c.madurez||0), 0) / answered).toFixed(1) : "0.0";
  const gaps        = controles.filter(c => c.madurez > 0 && c.madurez < 3).length;
  const openFind    = hallazgos.filter(h => h.estado === "abierto").length;
  const pct         = totalCtrls > 0 ? Math.round(answered / totalCtrls * 100) : 0;

  // Color for maturity bar
  const matColor = (v) => v >= 4 ? "var(--success)" : v >= 2.5 ? "var(--warning)" : "var(--danger)";

  // Brecha table: controls with madurez 1-2
  const brechas = controles.filter(c => c.madurez > 0 && c.madurez < 3).sort((a,b) => a.madurez - b.madurez);

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Resultados</div>
          <div className="page-sub">{ev?.nombre} · Análisis de madurez y brechas</div>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>
      </div>

      {/* KPIs */}
      <div className="kpi-grid" style={{ marginBottom:24 }}>
        <div className="kpi"><div className="kpi-label"><Icon.Target className="ic"/>Progreso</div><div className="kpi-val">{pct}<span className="unit">%</span></div><div style={{ fontSize:12, color:"var(--text-muted)" }}>{answered} / {totalCtrls} controles</div></div>
        <div className="kpi"><div className="kpi-label"><Icon.TrendingUp className="ic"/>Madurez prom.</div><div className="kpi-val">{avgMat}<span className="unit">/5</span></div></div>
        <div className="kpi"><div className="kpi-label"><Icon.AlertTriangle className="ic" style={{ color:"var(--danger)" }}/>Brechas</div><div className="kpi-val" style={{ color:"var(--danger)" }}>{gaps}</div><div style={{ fontSize:12, color:"var(--text-muted)" }}>controles bajo nivel 3</div></div>
        <div className="kpi"><div className="kpi-label"><Icon.AlertOctagon className="ic"/>Hallazgos abiertos</div><div className="kpi-val">{openFind}</div></div>
      </div>

      {/* Domain radar (SVG bar chart) */}
      <div style={{ display:"grid", gridTemplateColumns:"1.4fr 1fr", gap:20, marginBottom:24 }}>
        <div className="card">
          <div className="card-head"><div className="card-title">Madurez por dominio</div></div>
          <div style={{ padding:20 }}>
            {domList.map(d => {
              const avg = d.answered ? (d.sumMat / d.answered) : 0;
              const pctBar = (avg / 5) * 100;
              return (
                <div key={d.id} style={{ marginBottom:14 }}>
                  <div style={{ display:"flex", justifyContent:"space-between", marginBottom:5 }}>
                    <div>
                      <span style={{ fontSize:12.5, fontWeight:600 }}>{d.id}</span>
                      <span style={{ fontSize:11.5, color:"var(--text-muted)", marginLeft:6 }}>{d.name}</span>
                    </div>
                    <span className="mono" style={{ fontSize:13, fontWeight:700, color: matColor(avg) }}>{avg.toFixed(1)}</span>
                  </div>
                  <div className="progress">
                    <div className="progress-fill" style={{ width:`${pctBar}%`, background: matColor(avg) }}></div>
                  </div>
                  <div style={{ display:"flex", justifyContent:"space-between", marginTop:3, fontSize:11, color:"var(--text-muted)" }}>
                    <span>{d.answered}/{d.total} evaluados</span>
                    <span>{Math.round(pctBar)}% cobertura</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Distribution chart */}
        <div className="card">
          <div className="card-head"><div className="card-title">Distribución de madurez</div></div>
          <div style={{ padding:20 }}>
            {[0,1,2,3,4,5].map(n => {
              const count = controles.filter(c => (c.madurez||0) === n).length;
              const barW  = totalCtrls > 0 ? (count / totalCtrls) * 100 : 0;
              const colors = ["var(--danger)","var(--m1)","var(--m2)","var(--m3)","var(--m4)","var(--m5)"];
              const labels = ["Inexistente","Inicial","Repetible","Definido","Gestionado","Optimizado"];
              return (
                <div key={n} style={{ display:"grid", gridTemplateColumns:"60px 1fr 40px", gap:10, alignItems:"center", marginBottom:10 }}>
                  <div style={{ fontSize:11.5, fontWeight:600, color:"var(--text-secondary)" }}>{labels[n]}</div>
                  <div className="progress">
                    <div className="progress-fill" style={{ width:`${barW}%`, background: count > 0 ? colors[n] : "transparent" }}></div>
                  </div>
                  <span className="mono" style={{ fontSize:12, fontWeight:700, color:"var(--text-secondary)", textAlign:"right" }}>{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Brechas table */}
      {brechas.length > 0 && (
        <div>
          <div className="section-title" style={{ marginBottom:12 }}>Controles con brecha (madurez &lt; 3)</div>
          <div className="card tbl-card">
            <table className="tbl">
              <thead><tr>
                <th style={{ width:120 }}>Control</th>
                <th>Nombre</th>
                <th style={{ width:140 }}>Madurez</th>
                <th style={{ width:120 }}>Dominio</th>
              </tr></thead>
              <tbody>
                {brechas.map(c => (
                  <tr key={c.id}>
                    <td><span className="tag-mono">{c.id}</span></td>
                    <td style={{ fontSize:13 }}>{c.nombre || c.name}</td>
                    <td>
                      <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                        <div className="progress" style={{ flex:1, maxWidth:80 }}>
                          <div className="progress-fill" style={{ width:`${(c.madurez/5)*100}%`, background:matColor(c.madurez) }}></div>
                        </div>
                        <span className="mono" style={{ fontSize:13, fontWeight:700, color:matColor(c.madurez) }}>{c.madurez.toFixed(1)}</span>
                      </div>
                    </td>
                    <td><Badge tone="neutral">{c.dominio}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { ResultadosScreen });
