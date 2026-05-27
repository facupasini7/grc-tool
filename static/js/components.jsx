/* global React, Icon */
/* Shared UI components */

const { useState, useEffect, useRef, useCallback, useMemo } = React;

// ── Badge with semantic tone ──────────────────────────────────────
function Badge({ tone = "neutral", dot = false, mono = false, children, style }) {
  const cls = mono ? "tag-mono" : `badge b-${tone}`;
  return (
    <span className={cls} style={style}>
      {dot && !mono && <span className="badge-dot"></span>}
      {children}
    </span>
  );
}

// ── Maturity (0–5) dots ───────────────────────────────────────────
function Maturity({ value, showVal = true }) {
  const v = Math.max(0, Math.min(5, value ?? 0));
  return (
    <span className="maturity" title={`Madurez ${v}/5`}>
      {[1, 2, 3, 4, 5].map((i) => (
        <span key={i} className={`dot ${i <= v ? `on-${v}` : ""}`}></span>
      ))}
      {showVal && <span className="maturity-val">{v.toFixed(1)}</span>}
    </span>
  );
}

// ── Maturity selector (clickable 0–5) ─────────────────────────────
function MaturitySelector({ value, onChange, disabled }) {
  return (
    <div className="mat-row">
      {[0, 1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          className={`mat-btn ${value === n ? `sel-${n}` : ""}`}
          onClick={() => !disabled && onChange(n)}
          title={`Nivel ${n}`}
          disabled={disabled}
        >
          {n}
        </button>
      ))}
    </div>
  );
}

// ── Progress bar ──────────────────────────────────────────────────
function Progress({ value, color }) {
  return (
    <div className="progress">
      <div
        className="progress-fill"
        style={{ width: `${Math.max(0, Math.min(100, value))}%`, background: color || undefined }}
      ></div>
    </div>
  );
}

// ── KPI card ──────────────────────────────────────────────────────
function KPI({ label, value, unit, icon, delta, deltaDir }) {
  const I = icon ? Icon[icon] : null;
  return (
    <div className="kpi">
      <div className="kpi-label">{I && <I className="ic" />}{label}</div>
      <div className="kpi-val">
        {value}
        {unit && <span className="unit">{unit}</span>}
      </div>
      {delta != null && (
        <div className={`kpi-delta ${deltaDir || ""}`}>
          {deltaDir === "up" ? <Icon.ArrowUp size={12}/> : deltaDir === "down" ? <Icon.ArrowDown size={12}/> : null}
          {delta}
        </div>
      )}
    </div>
  );
}

// ── Modal ─────────────────────────────────────────────────────────
function Modal({ open, onClose, title, sub, size, children, footer }) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e) => { if (e.key === "Escape") onClose(); };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className={`modal ${size === "lg" ? "modal-lg" : ""}`} onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <div className="modal-title">{title}</div>
            {sub && <div className="modal-sub">{sub}</div>}
          </div>
          <button className="btn btn-ghost btn-icon" onClick={onClose} aria-label="Cerrar">
            <Icon.X size={16}/>
          </button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}

// ── Sidebar ───────────────────────────────────────────────────────
// Props: nav=[{id,label,icon}], active, user, onNav(id), onSettings()
function Sidebar({ nav = [], active, user, onNav, onSettings }) {
  const initials = (name) =>
    (name || "U").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();

  return (
    <aside className="sidebar">
      <div className="sb-brand">
        <div className="sb-brand-mark"><Icon.ShieldCheck size={16}/></div>
        <div>
          <div className="sb-brand-name">NormaLab</div>
          <div className="sb-brand-sub">GRC · Proof of Concept</div>
        </div>
      </div>

      <div className="sb-nav">
        {nav.map(({ id, label, icon }) => {
          const IconC = Icon[icon] || Icon.Circle;
          return (
            <div
              key={id}
              className={`sb-item ${active === id ? "active" : ""}`}
              onClick={() => onNav && onNav(id)}
            >
              <IconC size={15} className="sb-icon"/>
              <span>{label}</span>
            </div>
          );
        })}
      </div>

      <div className="sb-footer">
        <div className="sb-user" onClick={() => onSettings && onSettings()}>
          <div className="sb-avatar">{initials(user?.nombre || user?.name)}</div>
          <div style={{ minWidth: 0, flex: 1 }}>
            <div className="sb-user-name">{user?.nombre || user?.name}</div>
            <div className="sb-user-role">{roleLabel(user?.rol || user?.role)}</div>
          </div>
          <Icon.Settings size={13} style={{ color: "var(--sb-text-muted)", flexShrink: 0 }}/>
        </div>
      </div>
    </aside>
  );
}

// ── Topbar ────────────────────────────────────────────────────────
// Props: user, onSettings(), onLogout(), onTweaks()
function Topbar({ user, onSettings, onLogout, onTweaks }) {
  const [dark, setDark] = useState(
    document.documentElement.getAttribute("data-theme") === "dark"
  );

  const toggleTheme = () => {
    const next = dark ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    setDark(!dark);
  };

  return (
    <div className="topbar">
      <div className="crumb">
        <Icon.ShieldCheck size={13} style={{ color: "var(--accent)", marginRight: 4 }}/>
        <span style={{ fontWeight: 600 }}>NormaLab</span>
      </div>

      <div className="tb-search">
        <Icon.Search size={14}/>
        <input placeholder="Buscar controles, hallazgos…" readOnly/>
        <span className="kbd">⌘K</span>
      </div>

      <button className="tb-iconbtn" title={dark ? "Modo claro" : "Modo oscuro"} onClick={toggleTheme}>
        {dark ? <Icon.Sun size={15}/> : <Icon.Moon size={15}/>}
      </button>
      {onTweaks && (
        <button className="tb-iconbtn" title="Panel de tweaks" onClick={onTweaks}>
          <Icon.Sliders size={15}/>
        </button>
      )}
      {onLogout && (
        <button className="tb-iconbtn" title="Cerrar sesión" onClick={onLogout}>
          <Icon.LogOut size={15}/>
        </button>
      )}
    </div>
  );
}

// ── Empty state ───────────────────────────────────────────────────
function Empty({ icon, title, text, action }) {
  const I = icon ? Icon[icon] : Icon.Inbox;
  return (
    <div className="empty">
      <div className="empty-icon"><I size={22}/></div>
      <div className="empty-title">{title}</div>
      {text && <div className="empty-text">{text}</div>}
      {action && <div style={{ marginTop: 16 }}>{action}</div>}
    </div>
  );
}

// ── Spinner ───────────────────────────────────────────────────────
function Spinner() {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 48, color: "var(--text-muted)" }}>
      <Icon.Loader size={20} style={{ animation: "spin 1s linear infinite" }}/>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}

// ── useApi hook (fetch + loading + error) ─────────────────────────
function useApi(fetcher, deps = []) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try { setData(await fetcher()); }
    catch(e) { setError(e.message); }
    finally  { setLoading(false); }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => { load(); }, [load]);
  return { data, loading, error, reload: load };
}

// ── Formatters ────────────────────────────────────────────────────
const fmtDate = (s) => {
  if (!s) return "—";
  const d = new Date(s);
  if (isNaN(d)) return s;
  return d.toLocaleDateString("es-AR", { day: "2-digit", month: "short", year: "numeric" });
};

const sevTone   = (sev) => ({ critica: "danger",  alta: "warning", media: "info", baja: "success" }[sev] || "neutral");
const sevLabel  = (sev) => ({ critica: "Crítica", alta: "Alta",    media: "Media",baja: "Baja"    }[sev] || sev);
const stateTone = (st)  => ({ abierto:"danger", en_proceso:"warning", resuelto:"success", verificado:"info" }[st] || "neutral");
const stateLabel = (st) => ({ abierto:"Abierto", en_proceso:"En proceso", resuelto:"Resuelto", verificado:"Verificado" }[st] || st);
const roleLabel = (r)   => ({ admin:"Administrador", analista:"Analista GRC", auditado:"Auditado", auditor_externo:"Auditor Externo" }[r] || r);

// ── Export ────────────────────────────────────────────────────────
Object.assign(window, {
  Badge, Maturity, MaturitySelector, Progress, KPI, Modal,
  Sidebar, Topbar, Empty, Spinner, useApi,
  fmtDate, sevTone, sevLabel, stateTone, stateLabel, roleLabel,
});
