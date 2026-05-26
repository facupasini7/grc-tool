/* global React, ReactDOM, Sidebar, Topbar, TweaksPanel,
          LoginScreen, HomeScreen, EvaluacionesScreen, NewEvalModal,
          EvaluacionScreen, HallazgosScreen, ResultadosScreen,
          CoberturaScreen, RemediacionScreen, AuditoriaScreen,
          UsuariosScreen, SeguridadScreen, SettingsScreen,
          RiesgosScreen, SoAScreen, DeadlinesScreen, Spinner, API */

const { useState, useEffect, useCallback } = React;

/* ─── Main App ───────────────────────────────────────────────────── */
function App() {
  const [user,       setUser]       = useState(null);
  const [authCheck,  setAuthCheck]  = useState(true);
  const [screen,     setScreen]     = useState("home");
  const [evalId,     setEvalId]     = useState(null);
  const [evalNombre, setEvalNombre] = useState("");
  const [newEvalOpen,setNewEvalOpen]= useState(false);
  const [tweaksOpen, setTweaksOpen] = useState(false);

  /* 401 global handler */
  useEffect(() => {
    window._onUnauth = () => { setUser(null); setScreen("home"); };
    return () => { delete window._onUnauth; };
  }, []);

  /* Session check on mount */
  useEffect(() => {
    API.me()
      .then(u  => setUser(u))
      .catch(() => setUser(null))
      .finally(()=> setAuthCheck(false));
  }, []);

  /* ── Navigation ── */
  const go = useCallback((s, id, nombre) => {
    setScreen(s);
    if (id !== undefined) setEvalId(id);
    if (nombre !== undefined) setEvalNombre(nombre || "");
  }, []);

  const handleLogin = useCallback((u) => {
    setUser(u);
    setScreen(u.debe_cambiar_password ? "settings" : "home");
  }, []);

  const handleLogout = useCallback(async () => {
    try { await API.logout(); } catch {}
    setUser(null);
    setScreen("home");
    setEvalId(null);
  }, []);

  /* ── Loading ── */
  if (authCheck) return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:"100vh" }}>
      <Spinner/>
    </div>
  );

  /* ── Login ── */
  if (!user) return <LoginScreen onLogin={handleLogin}/>;

  /* ── Nav items ── */
  const isAdmin    = user.rol === "admin";
  const isAnalista = user.rol === "analista";
  const isAuditado = user.rol === "auditado";

  const NAV = [
    { id:"home",        label:"Inicio",          icon:"Home"          },
    { id:"evaluaciones",label:"Evaluaciones",     icon:"ClipboardCheck"},
    ...(!isAuditado ? [
      { id:"hallazgos",   label:"Hallazgos",      icon:"AlertTriangle" },
      { id:"riesgos",     label:"Riesgos",        icon:"AlertOctagon"  },
      { id:"remediacion", label:"Remediación",    icon:"Kanban"        },
      { id:"resultados",  label:"Resultados",     icon:"PieChart"      },
      { id:"cobertura",   label:"Cobertura",      icon:"Layers"        },
    ] : []),
    ...(isAdmin ? [
      { id:"seguridad",   label:"Seguridad",       icon:"ShieldCheck"   },
    ] : []),
  ];

  /* ── Screen router ── */
  const renderScreen = () => {
    switch (screen) {
      case "home":
        return (
          <HomeScreen
            userName={user.nombre || user.username}
            userRol={user.rol}
            onOpenEval={(id, nombre) => go("evaluacion", id, nombre)}
            onNewEval={() => setNewEvalOpen(true)}
            onNav={(s) => go(s)}
          />
        );
      case "evaluaciones":
        return (
          <EvaluacionesScreen
            onOpenEval={(id, nombre) => go("evaluacion", id, nombre)}
            onNewEval={() => setNewEvalOpen(true)}
          />
        );
      case "evaluacion":
        return (
          <EvaluacionScreen
            evalId={evalId}
            user={user}
            onBack={() => go("evaluaciones")}
            onNav={(s, id, nombre) => go(s, id ?? evalId, nombre ?? evalNombre)}
          />
        );
      case "hallazgos":
        return (
          <HallazgosScreen
            evalId={evalId}
            onBack={evalId ? () => go("evaluacion", evalId) : null}
          />
        );
      case "riesgos":
        return (
          <RiesgosScreen
            evalId={evalId}
            onBack={evalId ? () => go("evaluacion", evalId) : null}
          />
        );
      case "soa":
        return (
          <SoAScreen
            evalId={evalId}
            evalNombre={evalNombre}
            onBack={() => go("evaluacion", evalId)}
          />
        );
      case "deadlines":
        return (
          <DeadlinesScreen
            evalId={evalId}
            onBack={() => go("evaluacion", evalId)}
          />
        );
      case "resultados":
        return (
          <ResultadosScreen
            evalId={evalId}
            onBack={() => go(evalId ? "evaluacion" : "home", evalId)}
          />
        );
      case "cobertura":
        return (
          <CoberturaScreen
            evalId={evalId}
            onBack={evalId ? () => go("evaluacion", evalId) : null}
          />
        );
      case "remediacion":
        return (
          <RemediacionScreen
            evalId={evalId}
            onBack={evalId ? () => go("evaluacion", evalId) : null}
          />
        );
      case "seguridad":
        return <SeguridadScreen user={user}/>;
      case "settings":
        return <SettingsScreen user={user} onLogout={handleLogout}/>;
      default:
        return (
          <HomeScreen
            userName={user.nombre || user.username}
            userRol={user.rol}
            onOpenEval={(id, nombre) => go("evaluacion", id, nombre)}
            onNewEval={() => setNewEvalOpen(true)}
            onNav={(s) => go(s)}
          />
        );
    }
  };

  return (
    <div className="app">
      <Sidebar
        nav={NAV}
        active={screen}
        user={user}
        onNav={(id) => go(id)}
        onSettings={() => go("settings")}
      />

      <div className="app-main">
        <Topbar
          user={user}
          onSettings={() => go("settings")}
          onLogout={handleLogout}
          onTweaks={typeof TweaksPanel !== "undefined" ? () => setTweaksOpen(true) : null}
        />
        {renderScreen()}
      </div>

      {newEvalOpen && (
        <NewEvalModal
          open={true}
          onClose={() => setNewEvalOpen(false)}
          onCreate={(id) => { setNewEvalOpen(false); go("evaluacion", id); }}
        />
      )}

      {typeof TweaksPanel !== "undefined" && tweaksOpen && (
        <TweaksPanel open={tweaksOpen} onClose={() => setTweaksOpen(false)}/>
      )}
    </div>
  );
}

/* ─── Bootstrap ─────────────────────────────────────────────────── */
ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
