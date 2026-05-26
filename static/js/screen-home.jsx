/* global React, Icon, Modal, Badge, Maturity, Progress, KPI, Spinner,
          fmtDate, sevTone, sevLabel, stateTone, stateLabel, useApi, API */

const { useState: useStateH, useEffect: useEffectH } = React;

// ── Login Screen ──────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
  const [user,    setUser]    = useStateH("admin");
  const [pass,    setPass]    = useStateH("");
  const [showP,   setShowP]   = useStateH(false);
  const [err,     setErr]     = useStateH("");
  const [loading, setLoading] = useStateH(false);

  const submit = async (e) => {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      const r = await API.login(user, pass);
      if (r.error) { setErr(r.error); }
      else { onLogin(r); }
    } catch { setErr("Error de conexión. Intentá nuevamente."); }
    finally  { setLoading(false); }
  };

  return (
    <div className="login-page">
      <aside className="login-aside">
        <div className="login-brand">
          <div className="login-brand-mark"><Icon.ShieldCheck size={20}/></div>
          <div>
            <div className="login-brand-name">NormaLab</div>
            <div className="login-brand-sub">GRC · Proof of Concept</div>
          </div>
        </div>

        <div className="login-msg">
          <h1>Compliance GRC,<br/>sin complejidad innecesaria.</h1>
          <p>Gap analysis multi-framework: ISO 27001, NIST CSF 2.0, SOC 2, CIS Controls v8 y más. Centralizá controles, riesgos, evidencia y planes de remediación en un solo lugar.</p>
        </div>

        <div className="login-feats">
          {[
            { ic: "ClipboardCheck", text: "530+ controles en 7 frameworks y normativas" },
            { ic: "Cpu",            text: "Análisis de evidencias asistido por IA" },
            { ic: "History",        text: "Log inmutable para auditoría externa" },
          ].map(f => {
            const FI = Icon[f.ic];
            return (
              <div key={f.ic} className="login-feat">
                <span className="login-feat-ic"><FI size={14}/></span>
                <span>{f.text}</span>
              </div>
            );
          })}
        </div>
      </aside>

      <main className="login-main">
        <div className="login-card">
          <h2>Iniciar sesión</h2>
          <div className="hint">Ingresá con tu cuenta corporativa.</div>

          <form className="login-form" onSubmit={submit}>
            {err && (
              <div style={{ background:"var(--danger-soft)", border:"1px solid var(--danger-border)", borderRadius:8, padding:"10px 14px", fontSize:13, color:"var(--danger)" }}>
                {err}
              </div>
            )}
            <div className="field">
              <label>Usuario</label>
              <input className="input" value={user} onChange={e => setUser(e.target.value)} autoFocus autoComplete="username"/>
            </div>
            <div className="field">
              <label>Contraseña</label>
              <div style={{ position:"relative" }}>
                <input
                  className="input"
                  type={showP ? "text" : "password"}
                  value={pass}
                  onChange={e => setPass(e.target.value)}
                  style={{ paddingRight: 38 }}
                  autoComplete="current-password"
                />
                <button type="button" onClick={() => setShowP(!showP)}
                  style={{ position:"absolute", right:4, top:4, bottom:4, padding:"0 8px", border:"none", background:"transparent", color:"var(--text-muted)", cursor:"pointer" }}>
                  {showP ? <Icon.EyeOff size={14}/> : <Icon.Eye size={14}/>}
                </button>
              </div>
            </div>
            <button className="btn btn-primary" type="submit" style={{ marginTop:6 }} disabled={loading}>
              {loading ? <Icon.Loader size={14}/> : <><Icon.ArrowRight size={14}/> Iniciar sesión</>}
            </button>
          </form>

          <div className="login-extra">
            <a href="#forgot">¿Olvidaste tu contraseña?</a>
            <a href="#register">Crear cuenta</a>
          </div>
        </div>
      </main>
    </div>
  );
}

// ── Home / Dashboard ──────────────────────────────────────────────
function HomeScreen({ onOpenEval, onNewEval, onNav, userName }) {
  const { data: evals,    loading: le } = useApi(() => API.evaluaciones(), []);
  const { data: findings, loading: lf } = useApi(() => API.hallazgos(null), []);
  const { data: auditLog, loading: la } = useApi(() => API.auditLog({ limit: 6 }), []);

  if (le || lf || la) return <Spinner/>;

  const evList = evals || [];
  const fList  = findings?.hallazgos || findings || [];
  const aList  = auditLog?.log || auditLog || [];

  const sevOrder = { critica: 0, alta: 1, media: 2, baja: 3 };
  const today = new Date();

  const attention = [...fList]
    .filter(h => h.estado === "abierto" || h.estado === "en_proceso")
    .sort((a, b) => (sevOrder[a.severidad] ?? 4) - (sevOrder[b.severidad] ?? 4) || new Date(a.fecha_limite) - new Date(b.fecha_limite))
    .slice(0, 5);

  const in30 = new Date(); in30.setDate(today.getDate() + 30);
  const upcoming = [...fList]
    .filter(h => h.estado !== "verificado" && h.estado !== "resuelto" && h.fecha_limite && new Date(h.fecha_limite) <= in30)
    .sort((a, b) => new Date(a.fecha_limite) - new Date(b.fecha_limite))
    .slice(0, 4);

  const critCount  = fList.filter(h => h.severidad === "critica").length;
  const inProgress = evList.filter(e => !e.completada).length;
  const allFind    = fList.filter(h => h.estado === "abierto" || h.estado === "en_proceso").length;
  const avgMat     = evList.length
    ? (evList.reduce((s, e) => s + (e.madurez_promedio || 0), 0) / evList.length).toFixed(1)
    : "0.0";

  const firstName = (userName || "").split(" ")[0] || "usuario";
  const h = today.getHours();
  const greeting = h < 12 ? "Buenos días" : h < 19 ? "Buenas tardes" : "Buenas noches";

  return (
    <div className="page">
      {/* Hero */}
      <div style={{ background:"linear-gradient(135deg,#0f172a 0%,#1e1b4b 100%)", borderRadius:14, padding:"28px 32px", marginBottom:24, color:"#e2e8f0", position:"relative", overflow:"hidden" }}>
        <div style={{ position:"absolute", right:-80, top:-60, width:320, height:320, background:"radial-gradient(circle,rgba(99,102,241,.35),transparent 60%)", pointerEvents:"none" }}/>
        <div style={{ position:"relative", display:"flex", justifyContent:"space-between", alignItems:"flex-end", gap:24 }}>
          <div style={{ maxWidth:560 }}>
            <div style={{ fontSize:11.5, color:"#a5b4fc", textTransform:"uppercase", letterSpacing:".08em", fontWeight:600, marginBottom:8 }}>
              {greeting}, {firstName}
            </div>
            <div style={{ fontSize:24, fontWeight:700, color:"#fff", letterSpacing:"-.02em", marginBottom:8, lineHeight:1.2 }}>
              Tenés <span style={{ color:"#fca5a5" }}>{critCount} hallazgos críticos</span> y <span style={{ color:"#fcd34d" }}>{inProgress} evaluaciones en curso</span>.
            </div>
            <div style={{ fontSize:13.5, color:"#94a3b8", lineHeight:1.55 }}>
              Madurez promedio de tu portfolio: <strong style={{ color:"#cbd5e1" }}>{avgMat}/5</strong>. Revisá los hallazgos prioritarios y avanzá con el plan de remediación.
            </div>
            <div style={{ display:"flex", gap:8, marginTop:18 }}>
              <button className="btn btn-primary" onClick={onNewEval}><Icon.Plus size={14}/> Nueva evaluación</button>
              <button className="btn" onClick={() => onNav("hallazgos")} style={{ background:"rgba(255,255,255,.08)", color:"#fff", border:"1px solid rgba(255,255,255,.12)" }}>
                <Icon.AlertTriangle size={14}/> Ver hallazgos
              </button>
            </div>
          </div>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(2,1fr)", gap:8, flexShrink:0 }}>
            <MiniStat n={inProgress} label="Eval. activas"/>
            <MiniStat n={avgMat}     label="Madurez prom." suffix="/5"/>
            <MiniStat n={allFind}    label="Hallazgos abiertos" tone="warn"/>
            <MiniStat n={evList.length} label="Evaluaciones"/>
          </div>
        </div>
      </div>

      {/* Attention + upcoming */}
      <div style={{ display:"grid", gridTemplateColumns:"1.4fr 1fr", gap:20, marginBottom:24 }}>
        <div className="card">
          <div className="card-head">
            <div><div className="card-title">Requiere tu atención</div><div className="card-sub">Hallazgos críticos y altos abiertos.</div></div>
            <button className="btn btn-ghost btn-sm" onClick={() => onNav("hallazgos")}>Ver todos <Icon.ArrowRight size={12}/></button>
          </div>
          {attention.length === 0 ? (
            <div style={{ padding:32, textAlign:"center", color:"var(--text-muted)", fontSize:13 }}>✓ Sin hallazgos abiertos prioritarios</div>
          ) : attention.map((h, i) => {
            const overdue = h.fecha_limite && new Date(h.fecha_limite) < today;
            return (
              <div key={h.id} style={{ display:"grid", gridTemplateColumns:"auto 1fr auto auto", gap:14, alignItems:"center", padding:"14px 18px", borderBottom: i === attention.length-1 ? "none" : "1px solid var(--border-subtle)", cursor:"pointer" }}>
                <Badge tone={sevTone(h.severidad)} dot>{sevLabel(h.severidad)}</Badge>
                <div style={{ minWidth:0 }}>
                  <div style={{ fontSize:13.5, fontWeight:600, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{h.titulo}</div>
                  <div style={{ fontSize:11.5, color:"var(--text-muted)", marginTop:2 }}><span className="mono">{h.control_id}</span></div>
                </div>
                <div style={{ fontSize:11.5, color: overdue ? "var(--danger)" : "var(--text-muted)", fontWeight: overdue ? 700 : 500, textAlign:"right", whiteSpace:"nowrap" }}>
                  {h.fecha_limite ? <><Icon.Calendar size={11} style={{ display:"inline", verticalAlign:"-1px", marginRight:3 }}/>{fmtDate(h.fecha_limite)}</> : "—"}
                </div>
                <Badge tone={stateTone(h.estado)}>{stateLabel(h.estado)}</Badge>
              </div>
            );
          })}
        </div>

        <div className="card">
          <div className="card-head"><div><div className="card-title">Próximos vencimientos</div><div className="card-sub">Próximos 30 días.</div></div></div>
          <div style={{ padding:"6px 8px 10px" }}>
            {upcoming.length === 0 ? (
              <div style={{ padding:24, textAlign:"center", color:"var(--text-muted)", fontSize:13 }}>Sin vencimientos próximos</div>
            ) : upcoming.map(h => {
              const due = new Date(h.fecha_limite);
              const days = Math.ceil((due - today) / (1000*60*60*24));
              const overdue = days < 0;
              return (
                <div key={h.id} style={{ display:"flex", gap:12, padding:"10px", alignItems:"center", borderRadius:8 }}>
                  <div style={{ width:44, textAlign:"center", flexShrink:0, background: overdue ? "var(--danger-soft)" : "var(--accent-soft)", color: overdue ? "var(--danger)" : "var(--accent)", borderRadius:7, padding:"5px 6px" }}>
                    <div style={{ fontSize:16, fontWeight:700, lineHeight:1 }}>{due.getDate()}</div>
                    <div style={{ fontSize:9, textTransform:"uppercase", letterSpacing:".06em", fontWeight:700, marginTop:2 }}>{due.toLocaleDateString("es-AR",{month:"short"}).replace(".","")}</div>
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontSize:12.5, fontWeight:600, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{h.titulo}</div>
                    <div style={{ fontSize:11, color: overdue ? "var(--danger)" : "var(--text-muted)", marginTop:1, fontWeight: overdue ? 600 : 400 }}>
                      {overdue ? `Vencido hace ${-days}d` : days === 0 ? "Vence hoy" : `En ${days} día${days!==1?"s":""}`}
                    </div>
                  </div>
                  <Badge tone={sevTone(h.severidad)}>{sevLabel(h.severidad)}</Badge>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Evaluaciones list + audit */}
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:20 }}>
        <div className="card">
          <div className="card-head">
            <div><div className="card-title">Evaluaciones activas</div><div className="card-sub">Estado de tu portfolio.</div></div>
            <button className="btn btn-ghost btn-sm" onClick={() => onNav("evaluaciones")}>Ver todas <Icon.ArrowRight size={12}/></button>
          </div>
          <div>
            {evList.slice(0,5).map((ev, i) => (
              <div key={ev.id} onClick={() => onOpenEval(ev.id)}
                style={{ display:"flex", gap:12, padding:"13px 18px", alignItems:"center", borderBottom: i < Math.min(evList.length,5)-1 ? "1px solid var(--border-subtle)" : "none", cursor:"pointer" }}>
                <div style={{ width:36, height:36, borderRadius:9, background:"var(--accent-soft)", color:"var(--accent)", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
                  <Icon.ClipboardCheck size={16}/>
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontSize:13.5, fontWeight:600, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{ev.nombre}</div>
                  <div style={{ fontSize:11.5, color:"var(--text-muted)", marginTop:2 }}>{ev.empresa} · {fmtDate(ev.actualizada)}</div>
                </div>
                <Badge tone={ev.completada ? "success" : "warning"} dot>{ev.completada ? "Completa" : "En curso"}</Badge>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-head">
            <div><div className="card-title">Actividad reciente</div><div className="card-sub">Últimas acciones en tu workspace.</div></div>
            <button className="btn btn-ghost btn-sm" onClick={() => onNav("auditoria")}>Log completo <Icon.ArrowRight size={12}/></button>
          </div>
          <div style={{ padding:"6px 0" }}>
            {aList.slice(0,6).map((l, i) => <ActivityRow key={i} log={l}/>)}
          </div>
        </div>
      </div>
    </div>
  );
}

function MiniStat({ n, label, suffix, tone }) {
  return (
    <div style={{ background:"rgba(255,255,255,.05)", border:"1px solid rgba(255,255,255,.08)", borderRadius:10, padding:"10px 14px", minWidth:110 }}>
      <div style={{ fontSize:20, fontWeight:700, color: tone==="warn" ? "#fca5a5" : "#fff", lineHeight:1, fontVariantNumeric:"tabular-nums" }}>
        {n}{suffix && <span style={{ fontSize:12, color:"#94a3b8", fontWeight:500 }}>{suffix}</span>}
      </div>
      <div style={{ fontSize:10.5, color:"#94a3b8", textTransform:"uppercase", letterSpacing:".05em", fontWeight:600, marginTop:4 }}>{label}</div>
    </div>
  );
}

function ActivityRow({ log }) {
  const actionLabels = {
    login:"Login", login_fallido:"Login fallido", logout:"Logout",
    crear:"Creó", eliminar:"Eliminó", subir:"Subió evidencia",
    analizar:"Análisis IA", cambiar:"Cambió estado",
  };
  const action = log.accion || log.action || "";
  const label  = Object.entries(actionLabels).find(([k]) => action.startsWith(k))?.[1] || action;
  const user   = log.usuario_nombre || log.user || "—";
  const detail = log.detalle || log.details || "";
  const ts     = (log.timestamp || log.ts || "").replace(" ","T");
  const date   = new Date(ts);
  const now    = new Date();
  const mins   = Math.max(0, Math.floor((now - date) / 60000));
  const rel    = mins < 60 ? `hace ${mins}min` : mins < 1440 ? `hace ${Math.floor(mins/60)}h` : `hace ${Math.floor(mins/1440)}d`;

  return (
    <div style={{ display:"flex", gap:10, padding:"9px 18px", alignItems:"flex-start" }}>
      <div style={{ width:26, height:26, borderRadius:"50%", background:"var(--surface-2)", border:"1px solid var(--border)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:9.5, fontWeight:700, color:"var(--text-secondary)", flexShrink:0 }}>
        {user.slice(0,2).toUpperCase()}
      </div>
      <div style={{ flex:1, minWidth:0 }}>
        <div style={{ fontSize:12.5 }}><span style={{ fontWeight:600 }} className="mono">{user}</span>{" · "}<span style={{ color:"var(--text-secondary)" }}>{label}</span></div>
        <div style={{ fontSize:11.5, color:"var(--text-muted)", marginTop:1, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{detail}</div>
      </div>
      <span style={{ fontSize:11, color:"var(--text-faint)", flexShrink:0 }}>{rel}</span>
    </div>
  );
}

// ── Evaluaciones list ─────────────────────────────────────────────
function EvaluacionesScreen({ onOpenEval, onNewEval }) {
  const [filter, setFilter] = useStateH("all");
  const { data, loading, reload } = useApi(() => API.evaluaciones(), []);

  const evList = data || [];
  const filtered = evList.filter(e => {
    if (filter === "all")       return true;
    if (filter === "active")    return !e.completada;
    if (filter === "completed") return e.completada;
    return true;
  });

  const del = async (id, ev) => {
    ev.stopPropagation();
    if (!confirm("¿Eliminar esta evaluación? Esta acción no se puede deshacer.")) return;
    try { await API.eliminarEvaluacion(id); reload(); }
    catch { alert("Error al eliminar"); }
  };

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <div className="page-title">Evaluaciones</div>
          <div className="page-sub">Gap analysis activos y completados en tu organización.</div>
        </div>
        <button className="btn btn-primary" onClick={onNewEval}><Icon.Plus size={14}/> Nueva evaluación</button>
      </div>

      <div className="filter-bar">
        {[["all","Todas"],["active","En curso"],["completed","Completadas"]].map(([v,l]) => (
          <button key={v} className={`filter-chip ${filter===v?"active":""}`} onClick={() => setFilter(v)}>{l}</button>
        ))}
        <span style={{ marginLeft:"auto", fontSize:12, color:"var(--text-muted)" }}>{filtered.length} evaluaciones</span>
      </div>

      {loading ? <Spinner/> : filtered.length === 0 ? (
        <div className="empty">
          <div className="empty-icon"><Icon.ClipboardCheck size={22}/></div>
          <div className="empty-title">Sin evaluaciones</div>
          <div className="empty-text">Creá tu primera evaluación para comenzar el gap analysis.</div>
          <div style={{ marginTop:16 }}><button className="btn btn-primary" onClick={onNewEval}><Icon.Plus size={14}/> Nueva evaluación</button></div>
        </div>
      ) : (
        <div className="card tbl-card">
          <table className="tbl">
            <thead><tr>
              <th>Evaluación</th>
              <th style={{ width:180 }}>Empresa</th>
              <th style={{ width:140 }}>Frameworks</th>
              <th style={{ width:120 }}>Estado</th>
              <th style={{ width:160 }}>Actualización</th>
              <th style={{ width:80 }}></th>
            </tr></thead>
            <tbody>
              {filtered.map(ev => (
                <tr key={ev.id} className="clickable" onClick={() => onOpenEval(ev.id)}>
                  <td>
                    <div style={{ display:"flex", alignItems:"center", gap:10 }}>
                      <div style={{ width:34, height:34, borderRadius:8, background:"var(--accent-soft)", color:"var(--accent)", display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}><Icon.ClipboardCheck size={15}/></div>
                      <div>
                        <div style={{ fontWeight:600, fontSize:13.5 }}>{ev.nombre}</div>
                        {ev.alcance && <div style={{ fontSize:11.5, color:"var(--text-muted)", marginTop:1 }}>{ev.alcance.slice(0,60)}{ev.alcance.length>60?"…":""}</div>}
                      </div>
                    </div>
                  </td>
                  <td style={{ fontSize:13, color:"var(--text-secondary)" }}>{ev.empresa}</td>
                  <td>
                    <div style={{ display:"flex", flexWrap:"wrap", gap:4 }}>
                      {(typeof ev.frameworks==="string" ? JSON.parse(ev.frameworks) : ev.frameworks || ["ISO27001"]).map(fw => (
                        <span key={fw} className="tag-mono">{fw}</span>
                      ))}
                    </div>
                  </td>
                  <td><Badge tone={ev.completada?"success":"warning"} dot>{ev.completada?"Completa":"En curso"}</Badge></td>
                  <td><span style={{ fontSize:12, color:"var(--text-muted)" }}>{fmtDate(ev.actualizada)}</span></td>
                  <td onClick={e => e.stopPropagation()}>
                    <button className="btn btn-ghost btn-icon" onClick={e => del(ev.id, e)} title="Eliminar"><Icon.Trash size={14}/></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// ── Nueva evaluación modal ────────────────────────────────────────
function NewEvalModal({ open, onClose, onCreate }) {
  const [nombre,  setNombre]  = useStateH("");
  const [empresa, setEmpresa] = useStateH("");
  const [alcance, setAlcance] = useStateH("");
  const [fws,     setFws]     = useStateH([]);
  const [loading, setLoading] = useStateH(false);

  const { data: _catData } = useApi(() => API.frameworksCatalogo(), []);
  const catalogue = Array.isArray(_catData) ? _catData : [];

  // Separate primary frameworks (direct eval support) from reference/cobertura only
  const PRIMARY_FW_IDS = ["ISO27001","NIST_CSF","SOC2","CIS"];
  const primaryFws  = catalogue.filter(fw => PRIMARY_FW_IDS.includes(fw.id));
  const extraFws    = catalogue.filter(fw => fw.tipo === "framework" && !PRIMARY_FW_IDS.includes(fw.id));
  const regulFws    = catalogue.filter(fw => fw.tipo === "regulacion");

  const toggle = (id) => {
    setFws(prev => prev.includes(id) ? prev.filter(f => f !== id) : [...prev, id]);
  };

  const canSubmit = nombre.trim() && empresa.trim() && fws.length > 0 && !loading;

  const submit = async () => {
    if (!canSubmit) return;
    setLoading(true);
    try {
      const r = await API.crearEvaluacion({ nombre: nombre.trim(), empresa: empresa.trim(), alcance: alcance.trim(), frameworks: fws });
      if (!r.error) {
        setNombre(""); setEmpresa(""); setAlcance(""); setFws([]);
        onClose(); onCreate(r.id);
      } else { alert(r.error); }
    } catch (e) { alert("Error al crear evaluación: " + e.message); }
    finally { setLoading(false); }
  };

  const FwCard = ({ fw }) => {
    const sel = fws.includes(fw.id);
    const FI  = Icon[fw.icon] || Icon.Shield;
    const isPrimary = PRIMARY_FW_IDS.includes(fw.id);
    return (
      <div onClick={() => toggle(fw.id)}
        style={{
          display:"flex", alignItems:"flex-start", gap:10,
          padding:"10px 12px",
          border:`2px solid ${sel ? "var(--accent)" : "var(--border)"}`,
          borderRadius:9, cursor:"pointer",
          background: sel ? "var(--accent-soft)" : "var(--surface-2)",
          transition:"all .12s",
          opacity: catalogue.length === 0 ? 0.5 : 1,
        }}>
        <FI size={15} style={{ color: sel ? "var(--accent)" : "var(--text-muted)", flexShrink:0, marginTop:2 }}/>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontSize:12.5, fontWeight:700, color: sel ? "var(--accent)" : "var(--text-primary)" }}>{fw.label}</div>
          <div style={{ fontSize:10.5, color:"var(--text-faint)", marginTop:1, whiteSpace:"nowrap", overflow:"hidden", textOverflow:"ellipsis" }}>
            {fw.n} controles{isPrimary ? "" : " · cobertura"}
          </div>
        </div>
        {sel && <Icon.CheckCircle size={13} style={{ color:"var(--accent)", flexShrink:0, marginTop:2 }}/>}
      </div>
    );
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Nueva evaluación"
      sub="Configurá el alcance y los frameworks a auditar."
      footer={<>
        <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
        <button className="btn btn-primary" onClick={submit} disabled={!canSubmit}>
          {loading ? <Icon.Loader size={13}/> : <><Icon.Plus size={13}/> Crear evaluación</>}
        </button>
      </>}
    >
      <div className="field"><label>Nombre de la evaluación</label><input className="input" value={nombre} onChange={e=>setNombre(e.target.value)} placeholder="Ej: NIST CSF 2.0 — Gap Analysis 2026"/></div>
      <div className="field"><label>Empresa / organización</label><input className="input" value={empresa} onChange={e=>setEmpresa(e.target.value)} placeholder="Ej: Acme S.A."/></div>
      <div className="field"><label>Alcance (opcional)</label><textarea className="textarea" rows={2} value={alcance} onChange={e=>setAlcance(e.target.value)} placeholder="Describe el alcance de la evaluación…"/></div>

      <div className="field">
        <label>Frameworks con evaluación directa</label>
        <div style={{ fontSize:11, color:"var(--text-muted)", marginBottom:6 }}>
          Seleccioná al menos uno. El primero elegido será el framework principal de la evaluación.
        </div>
        <div style={{ display:"grid", gridTemplateColumns:"repeat(2,1fr)", gap:8 }}>
          {primaryFws.map(fw => <FwCard key={fw.id} fw={fw}/>)}
        </div>
      </div>

      {extraFws.length > 0 && (
        <div className="field">
          <label>Otros frameworks</label>
          <div style={{ fontSize:11, color:"var(--text-muted)", marginBottom:6 }}>
            Cobertura adicional — sin evaluación directa de controles.
          </div>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:8 }}>
            {extraFws.map(fw => <FwCard key={fw.id} fw={fw}/>)}
          </div>
        </div>
      )}

      {regulFws.length > 0 && (
        <div className="field">
          <label>Normativa regulatoria obligatoria</label>
          <div style={{ fontSize:11, color:"var(--text-muted)", marginBottom:6 }}>
            Comunicaciones del Banco Central de la Rep. Argentina — se incluyen en el análisis de cobertura.
          </div>
          <div style={{ display:"grid", gridTemplateColumns:"repeat(3,1fr)", gap:8 }}>
            {regulFws.map(fw => <FwCard key={fw.id} fw={fw}/>)}
          </div>
        </div>
      )}

      {fws.length === 0 && (
        <div style={{ display:"flex", alignItems:"center", gap:6, padding:"9px 12px",
          background:"var(--warning-soft)", border:"1px solid var(--warning-border)",
          borderRadius:8, fontSize:12, color:"var(--warning)" }}>
          <Icon.AlertTriangle size={13}/>
          Seleccioná al menos un framework para continuar.
        </div>
      )}
    </Modal>
  );
}

Object.assign(window, { LoginScreen, HomeScreen, EvaluacionesScreen, NewEvalModal });
