/* global React, Icon, Badge, Spinner, useApi, fmtDate, API */
const { useState: useStateSoa, useCallback: useCallbackSoa, useMemo: useMemoSoa } = React;

/* ── Helpers ──────────────────────────────────────────────────── */
function soaTone(aplica, aprobada) {
  if (!aplica) return aprobada ? "neutral" : "warning";
  return "success";
}
function soaLabel(aplica, aprobada) {
  if (!aplica) return aprobada ? "Excluido" : "No aplica (sin aprobar)";
  return "Aplica";
}

/* ── Exportar SoA a CSV ───────────────────────────────────────── */
function exportSoA(controles, respMap, evalNombre) {
  const cols = [
    "ID Control","Nombre","Dominio","Aplica","Justificación excepción",
    "Excepción aprobada","Válida hasta","Madurez"
  ];
  const escape = v => `"${String(v ?? "").replace(/"/g,'""')}"`;
  const header = cols.map(escape).join(",");
  const rows = controles.map(c => {
    const r = respMap[c.id] || {};
    return [
      c.id, c.nombre, c.dominio_nombre||c.dominio,
      r.aplica !== 0 ? "Sí" : "No",
      r.excepcion_justificacion || "",
      r.excepcion_aprobada ? "Sí" : "",
      r.excepcion_hasta || "",
      r.madurez || 0,
    ].map(escape).join(",");
  });
  const csv  = "﻿" + header + "\n" + rows.join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const a    = document.createElement("a");
  a.href     = URL.createObjectURL(blob);
  a.download = `SoA-${evalNombre}-${new Date().toISOString().slice(0,10)}.csv`;
  a.click();
}

/* ── Fila expandible ──────────────────────────────────────────── */
function SoARow({ ctrl, resp = {}, evalId, onSaved }) {
  const [open,    setOpen]    = useStateSoa(false);
  const [justif,  setJustif]  = useStateSoa(resp.excepcion_justificacion || "");
  const [hasta,   setHasta]   = useStateSoa(resp.excepcion_hasta || "");
  const [saving,  setSaving]  = useStateSoa(false);

  const aplica   = resp.aplica !== 0;
  const aprobada = !!resp.excepcion_aprobada;

  const toggleAplica = async () => {
    setSaving(true);
    try {
      if (aplica) {
        // Marcar como no aplica — solicita justificación
        setOpen(true);
      } else {
        // Reactivar — guarda aplica=1
        await API.guardarRespuesta(evalId, {
          control_id: ctrl.id, aplica: 1, madurez: resp.madurez || 0,
          comentario: resp.comentario || ""
        });
        onSaved();
      }
    } finally { setSaving(false); }
  };

  const saveExcepcion = async () => {
    if (!justif.trim()) { alert("Ingresá una justificación."); return; }
    setSaving(true);
    try {
      await API.guardarExcepcion(evalId, {
        control_id: ctrl.id, justificacion: justif,
        aprobada: 0, excepcion_hasta: hasta,
      });
      onSaved();
      setOpen(false);
    } finally { setSaving(false); }
  };

  return (
    <>
      <tr className="clickable" onClick={() => setOpen(o => !o)}>
        <td><span className="mono" style={{ fontSize:12 }}>{ctrl.id}</span></td>
        <td style={{ fontWeight:500, fontSize:13 }}>{ctrl.nombre}</td>
        <td style={{ fontSize:12.5, color:"var(--text-secondary)" }}>{ctrl.dominio_nombre || ctrl.dominio}</td>
        <td><Badge tone={soaTone(aplica, aprobada)}>{soaLabel(aplica, aprobada)}</Badge></td>
        <td style={{ fontSize:12.5, color:"var(--text-secondary)" }}>
          {!aplica && resp.excepcion_justificacion
            ? <span style={{ fontStyle:"italic" }}>{resp.excepcion_justificacion.slice(0,60)}…</span>
            : aplica ? <span style={{ color:"var(--text-faint)" }}>—</span>
            : <span style={{ color:"var(--warning)", fontSize:12 }}>Pendiente de justificación</span>}
        </td>
        <td style={{ fontSize:12 }}>{resp.excepcion_hasta ? fmtDate(resp.excepcion_hasta) : "—"}</td>
        <td>
          <button
            className={`btn btn-sm ${aplica ? "btn-ghost" : "btn-primary"}`}
            style={{ fontSize:11 }}
            onClick={e => { e.stopPropagation(); toggleAplica(); }}
            disabled={saving}
          >
            {aplica ? "Excluir" : "Incluir"}
          </button>
        </td>
      </tr>
      {open && !aplica && (
        <tr>
          <td colSpan={7} style={{ padding:0 }}>
            <div style={{ background:"var(--surface-2)", padding:"14px 20px",
              borderBottom:"1px solid var(--border)" }}>
              <div style={{ fontWeight:600, fontSize:13, marginBottom:10 }}>
                Justificación de exclusión — {ctrl.id}
              </div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr auto", gap:12 }}>
                <div className="field" style={{ marginBottom:0 }}>
                  <label>Justificación *</label>
                  <textarea className="input" rows={2} value={justif}
                    onChange={e => setJustif(e.target.value)}
                    placeholder="Explicá por qué este control no aplica a tu organización…"/>
                </div>
                <div className="field" style={{ marginBottom:0 }}>
                  <label>Revisar hasta</label>
                  <input className="input" type="date" value={hasta}
                    onChange={e => setHasta(e.target.value)}/>
                </div>
              </div>
              <div style={{ display:"flex", gap:8, marginTop:12 }}>
                <button className="btn btn-ghost btn-sm" onClick={() => setOpen(false)}>Cancelar</button>
                <button className="btn btn-primary btn-sm" onClick={saveExcepcion} disabled={saving}>
                  {saving ? <Icon.Loader size={12}/> : "Guardar excepción"}
                </button>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

/* ── Pantalla principal ───────────────────────────────────────── */
function SoAScreen({ evalId, evalNombre, onBack }) {
  const [search,    setSearch]    = useStateSoa("");
  const [filterAp,  setFilterAp]  = useStateSoa("todos");

  const { data: ctrlData, loading: ctrlLoading } = useApi(
    () => API.controles(evalId), [evalId]
  );
  const { data: respData, reload } = useApi(
    () => API.controles(evalId), [evalId]
  );

  const controles = ctrlData?.controles || [];

  // Construir mapa de respuestas
  const respMap = useMemoSoa(() => {
    const m = {};
    controles.forEach(c => { m[c.id] = c; });
    return m;
  }, [controles]);

  const stats = useMemoSoa(() => ({
    total:    controles.length,
    aplica:   controles.filter(c => c.aplica !== 0).length,
    excluido: controles.filter(c => c.aplica === 0).length,
    sinJustif:controles.filter(c => c.aplica === 0 && !c.excepcion_justificacion).length,
  }), [controles]);

  const filtrados = useMemoSoa(() => {
    let list = controles;
    if (search) {
      const q = search.toLowerCase();
      list = list.filter(c =>
        c.id.toLowerCase().includes(q) || c.nombre.toLowerCase().includes(q)
      );
    }
    if (filterAp === "aplica")   list = list.filter(c => c.aplica !== 0);
    if (filterAp === "excluido") list = list.filter(c => c.aplica === 0);
    if (filterAp === "sinjustif")list = list.filter(c => c.aplica === 0 && !c.excepcion_justificacion);
    return list;
  }, [controles, search, filterAp]);

  return (
    <div className="page">
      <div className="page-head">
        <div>
          {onBack && <button className="btn btn-ghost btn-sm" style={{ marginBottom:8 }} onClick={onBack}><Icon.ArrowLeft size={13}/> Volver</button>}
          <div className="page-title">Declaración de Aplicabilidad (SoA)</div>
          <div className="page-sub">
            Gestión formal de controles aplicables y justificación de exclusiones — ISO 27001 cl. 6.1.3.
          </div>
        </div>
        <div className="page-actions">
          <button className="btn btn-ghost btn-sm"
            onClick={() => exportSoA(controles, respMap, evalNombre || `eval-${evalId}`)}>
            <Icon.Download size={13}/> Exportar CSV
          </button>
        </div>
      </div>

      {/* KPIs */}
      <div className="kpi-grid" style={{ marginBottom:20 }}>
        <div className="kpi"><div className="kpi-label">Total controles</div><div className="kpi-val">{stats.total}</div></div>
        <div className="kpi"><div className="kpi-label" style={{ color:"var(--success)" }}>Aplican</div>
          <div className="kpi-val" style={{ color:"var(--success)" }}>{stats.aplica}</div></div>
        <div className="kpi"><div className="kpi-label">Excluidos</div><div className="kpi-val">{stats.excluido}</div></div>
        {stats.sinJustif > 0 && (
          <div className="kpi"><div className="kpi-label" style={{ color:"var(--warning)" }}>Sin justificar</div>
            <div className="kpi-val" style={{ color:"var(--warning)" }}>{stats.sinJustif}</div></div>
        )}
      </div>

      {stats.sinJustif > 0 && (
        <div style={{ background:"var(--warning-soft)", border:"1px solid var(--warning-border)",
          borderRadius:10, padding:"12px 16px", display:"flex", alignItems:"center",
          gap:10, marginBottom:16, fontSize:13 }}>
          <Icon.AlertTriangle size={16} style={{ color:"var(--warning)", flexShrink:0 }}/>
          <span><strong>{stats.sinJustif} controles excluidos</strong> sin justificación formal.
            Completalos para cumplir con ISO 27001 cláusula 6.1.3.</span>
        </div>
      )}

      {/* Filtros */}
      <div className="filter-bar">
        {[
          { k:"todos",    l:"Todos",          n:stats.total    },
          { k:"aplica",   l:"Aplican",         n:stats.aplica   },
          { k:"excluido", l:"Excluidos",       n:stats.excluido },
          { k:"sinjustif",l:"Sin justificar",  n:stats.sinJustif},
        ].filter(f => f.n > 0 || f.k === "todos").map(f => (
          <button key={f.k} className={`filter-chip${filterAp===f.k?" active":""}`}
            onClick={() => setFilterAp(f.k)}>
            {f.l} <span className="mono" style={{ opacity:.6 }}>{f.n}</span>
          </button>
        ))}
        <div style={{ flex:1 }}/>
        <div style={{ position:"relative" }}>
          <Icon.Search size={13} style={{ position:"absolute", left:10, top:"50%", transform:"translateY(-50%)",
            color:"var(--text-muted)", pointerEvents:"none" }}/>
          <input style={{ paddingLeft:30, height:32, borderRadius:8, border:"1px solid var(--border)",
            background:"var(--surface-1)", fontSize:13, color:"var(--text-primary)", width:200 }}
            placeholder="Buscar control…" value={search}
            onChange={e => setSearch(e.target.value)}/>
        </div>
      </div>

      {ctrlLoading ? <Spinner/> : (
        <div className="card tbl-card" style={{ marginTop:12 }}>
          <table className="tbl">
            <thead><tr>
              <th style={{ width:90 }}>ID</th>
              <th>Control</th>
              <th style={{ width:160 }}>Dominio</th>
              <th style={{ width:160 }}>Estado SoA</th>
              <th>Justificación</th>
              <th style={{ width:110 }}>Rev. hasta</th>
              <th style={{ width:80 }}></th>
            </tr></thead>
            <tbody>
              {filtrados.map(ctrl => (
                <SoARow key={ctrl.id} ctrl={ctrl} resp={ctrl}
                  evalId={evalId} onSaved={reload}/>
              ))}
              {filtrados.length === 0 && (
                <tr><td colSpan={7} style={{ textAlign:"center", padding:32,
                  color:"var(--text-muted)", fontSize:13 }}>Sin controles</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

Object.assign(window, { SoAScreen });
