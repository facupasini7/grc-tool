/* global React, Icon, Badge, Maturity, Spinner, useApi, API */

const { useState: useStateCob } = React;

function CoberturaScreen({ evalId, onBack }) {
  const { data: ctrls, loading } = useApi(() => evalId ? API.controles(evalId) : Promise.resolve([]), [evalId]);

  const controles = ctrls?.controles || ctrls || [];

  const FW_INFO = [
    { id:"ISO27001", label:"ISO 27001:2022",         short:"ISO 27001", icon:"ShieldCheck", color:"indigo"  },
    { id:"A7777",    label:"BCRA Comunicación A 7777",short:"BCRA A 7777",icon:"Landmark",   color:"blue"   },
    { id:"A7783",    label:"BCRA Comunicación A 7783",short:"BCRA A 7783",icon:"Landmark",   color:"blue"   },
    { id:"PCI",      label:"PCI DSS v4.0",            short:"PCI DSS",   icon:"CreditCard",  color:"violet" },
  ];

  const DOMAINS = [
    { id:"A.5", name:"Organizacional" },
    { id:"A.6", name:"Personas" },
    { id:"A.7", name:"Físico" },
    { id:"A.8", name:"Tecnológico" },
  ];

  // Compute ISO coverage per domain
  const domStats = DOMAINS.map(d => {
    const dc  = controles.filter(c => c.dominio === d.id);
    const ans = dc.filter(c => c.madurez > 0);
    const avg = ans.length ? (ans.reduce((s,c)=>s+c.madurez,0)/ans.length) : 0;
    return { ...d, total: dc.length, answered: ans.length, avg };
  });

  const matColor = (v) => {
    if (v === 0) return { bg:"var(--surface)", text:"var(--text-faint)" };
    if (v < 2)   return { bg:"#fee2e2",        text:"#991b1b" };
    if (v < 3)   return { bg:"#fed7aa",        text:"#9a3412" };
    if (v < 4)   return { bg:"#fef3c7",        text:"#854d0e" };
    if (v < 5)   return { bg:"#d1fae5",        text:"#065f46" };
    return              { bg:"#a7f3d0",        text:"#064e3b" };
  };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Cobertura multi-framework</div>
          <div className="page-sub">Mapeá el cumplimiento de controles ISO 27001 contra los frameworks regulatorios activos.</div>
        </div>
        {onBack && <button className="btn btn-ghost btn-sm" onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>}
      </div>

      {loading ? <Spinner/> : (
        <>
          {/* Framework cards */}
          <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:16, marginBottom:28 }}>
            {FW_INFO.map(fw => {
              const FI = Icon[fw.icon] || Icon.Shield;
              return (
                <div key={fw.id} className="card" style={{ padding:18 }}>
                  <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:12 }}>
                    <div style={{ width:36, height:36, borderRadius:9, background:"var(--accent-soft)", color:"var(--accent)", display:"flex", alignItems:"center", justifyContent:"center" }}><FI size={16}/></div>
                    <div>
                      <div style={{ fontWeight:700, fontSize:13 }}>{fw.short}</div>
                      <div style={{ fontSize:11, color:"var(--text-muted)" }}>{fw.label}</div>
                    </div>
                  </div>
                  {fw.id === "ISO27001" ? (
                    <div>
                      <div style={{ fontSize:22, fontWeight:700, color:"var(--accent)", marginBottom:4 }}>
                        {controles.filter(c=>c.madurez>0).length}<span style={{ fontSize:13, color:"var(--text-muted)", fontWeight:500 }}>/{controles.length}</span>
                      </div>
                      <div style={{ fontSize:11.5, color:"var(--text-muted)" }}>controles evaluados</div>
                    </div>
                  ) : (
                    <div style={{ fontSize:12, color:"var(--text-muted)", lineHeight:1.4 }}>
                      Activa esta evaluación para ver la cobertura cruzada.
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* ISO 27001 domain heatmap */}
          <div className="section-title" style={{ marginBottom:12 }}>Madurez por dominio — ISO 27001</div>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(4,1fr)", gap:12, marginBottom:28 }}>
            {domStats.map(d => {
              const clr = matColor(d.avg);
              return (
                <div key={d.id} className="card" style={{ padding:16, background: clr.bg, border:`1px solid ${clr.bg==="var(--surface)"?"var(--border)":clr.bg}` }}>
                  <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:10 }}>
                    <div>
                      <span className="tag-mono">{d.id}</span>
                      <div style={{ fontSize:12.5, fontWeight:600, marginTop:6, color: clr.bg==="var(--surface)"?"var(--text)":clr.text }}>{d.name}</div>
                    </div>
                    <div className="mono" style={{ fontSize:20, fontWeight:800, color:clr.text, lineHeight:1 }}>{d.avg.toFixed(1)}</div>
                  </div>
                  <div className="progress" style={{ background:"rgba(0,0,0,.07)" }}>
                    <div className="progress-fill" style={{ width:`${(d.avg/5)*100}%`, background:clr.text }}></div>
                  </div>
                  <div style={{ fontSize:11, color: clr.bg==="var(--surface)"?"var(--text-muted)":clr.text, marginTop:6, opacity:.8 }}>{d.answered}/{d.total} evaluados</div>
                </div>
              );
            })}
          </div>

          {/* Control list grouped by domain */}
          {domStats.map(d => {
            const dc = controles.filter(c => c.dominio === d.id);
            if (!dc.length) return null;
            return (
              <div key={d.id} style={{ marginBottom:20 }}>
                <div className="section-title" style={{ marginBottom:8 }}>{d.id} — {d.name}</div>
                <div className="card tbl-card">
                  <table className="tbl">
                    <thead><tr>
                      <th style={{ width:120 }}>Control</th>
                      <th>Nombre</th>
                      <th style={{ width:160 }}>Madurez</th>
                      <th style={{ width:100 }}>Estado</th>
                    </tr></thead>
                    <tbody>
                      {dc.map(c => {
                        const clr2 = matColor(c.madurez||0);
                        return (
                          <tr key={c.id}>
                            <td><span className="tag-mono">{c.id}</span></td>
                            <td style={{ fontSize:13 }}>{c.nombre || c.name}</td>
                            <td>
                              <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                                <div style={{ flex:1, maxWidth:80 }} className="progress">
                                  <div className="progress-fill" style={{ width:`${((c.madurez||0)/5)*100}%`, background: clr2.text }}></div>
                                </div>
                                <span className="mono" style={{ fontSize:12.5, fontWeight:700, color:clr2.text }}>{(c.madurez||0).toFixed(1)}</span>
                              </div>
                            </td>
                            <td>
                              {c.madurez === 0
                                ? <Badge tone="neutral">Sin evaluar</Badge>
                                : c.madurez < 3
                                  ? <Badge tone="danger" dot>Brecha</Badge>
                                  : <Badge tone="success" dot>Cumple</Badge>}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </>
      )}
    </div>
  );
}

Object.assign(window, { CoberturaScreen });
