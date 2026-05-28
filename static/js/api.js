/* ─── API client — connects to the Python backend ─────────────────── */
window.API = (() => {
  const json = (r) => {
    if (r.status === 401) { window._onUnauth && window._onUnauth(); throw new Error("401"); }
    if (!r.ok) throw new Error(r.status);
    return r.json();
  };
  const get  = (url)       => fetch(url,               { credentials: "include" }).then(json);
  const post = (url, body) => fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), credentials: "include" }).then(json);
  const put  = (url, body) => fetch(url, { method: "PUT",  headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), credentials: "include" }).then(json);
  const del  = (url)       => fetch(url, { method: "DELETE", credentials: "include" }).then(json);

  return {
    /* Auth */
    me()             { return get("/api/me"); },
    login(u, p)      {
      return fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: u, password: p }),
        credentials: "include",
      }).then(r => r.json());
    },
    register(d)      { return post("/api/register", d); },
    logout()         { return post("/api/logout", {}); },
    changePass(o, n) { return post("/api/change-password", { old_password: o, new_password: n }); },

    /* Frameworks catalogue */
    frameworksCatalogo()   { return get("/api/frameworks"); },

    /* Evaluaciones */
    evaluaciones()         { return get("/api/evaluaciones"); },
    evaluacion(id)         { return get(`/api/evaluaciones/${id}`); },
    crearEvaluacion(data)  { return post("/api/evaluaciones", data); },
    eliminarEvaluacion(id) { return del(`/api/evaluaciones/${id}`); },

    /* Controles + respuestas */
    controles(evalId)           { return get(`/api/evaluaciones/${evalId}/controles`); },
    guardarRespuesta(evalId, d) { return post(`/api/evaluaciones/${evalId}/respuestas`, d); },
    guardarExcepcion(evalId, d) { return post(`/api/evaluaciones/${evalId}/excepcion`, d); },

    /* Historial + comparación */
    historialMadurez(evalId)        { return get(`/api/evaluaciones/${evalId}/historial-madurez`); },
    snapshotMadurez(evalId)         { return post(`/api/evaluaciones/${evalId}/snapshot-madurez`, {}); },
    compararEvaluaciones(id1, id2)  { return get(`/api/evaluaciones/${id1}/comparar?con=${id2}`); },

    /* Hallazgos */
    hallazgos(evalId)          { return get(evalId ? `/api/evaluaciones/${evalId}/hallazgos` : "/api/hallazgos"); },
    crearHallazgo(evalId, d)   { return post(`/api/evaluaciones/${evalId}/hallazgos`, d); },
    actualizarHallazgo(id, d)  { return put(`/api/hallazgos/${id}`, d); },
    aprobarHallazgo(id, d)     { return post(`/api/hallazgos/${id}/aprobar`, d); },

    /* Colaboración por hallazgo — comentarios + evidencias */
    hallazgoComentarios(id)         { return get(`/api/hallazgos/${id}/comentarios`); },
    agregarHallazgoComentario(id, texto) { return post(`/api/hallazgos/${id}/comentarios`, { texto }); },
    hallazgoEvidencias(id)          { return get(`/api/hallazgos/${id}/evidencias`); },
    subirHallazgoEvidencia(id, d)   { return post(`/api/hallazgos/${id}/evidencias`, d); },
    eliminarHallazgoEvidencia(id)   { return del(`/api/hallazgo-evidencias/${id}`); },

    /* Tareas de remediación */
    tareas(hallazgoId)         { return get(`/api/hallazgos/${hallazgoId}/tareas`); },
    crearTarea(hallazgoId, d)  { return post(`/api/hallazgos/${hallazgoId}/tareas`, d); },
    actualizarTarea(id, d)     { return post(`/api/tareas/${id}`, d); },
    eliminarTarea(id)          { return del(`/api/tareas/${id}`); },

    /* Riesgos */
    riesgos(evalId)         { return get(`/api/evaluaciones/${evalId}/riesgos`); },
    crearRiesgo(evalId, d)  { return post(`/api/evaluaciones/${evalId}/riesgos`, d); },
    actualizarRiesgo(id, d) { return post(`/api/riesgos/${id}`, d); },
    eliminarRiesgo(id)      { return del(`/api/riesgos/${id}`); },

    /* Deadlines de evidencia */
    deadlines(evalId)             { return get(`/api/evaluaciones/${evalId}/deadlines`); },
    crearDeadline(evalId, d)      { return post(`/api/evaluaciones/${evalId}/deadlines`, d); },
    eliminarDeadline(id)          { return del(`/api/deadlines/${id}`); },

    /* Comentarios de discusión por control */
    comentariosControl(evalId, ctrlId) { return get(`/api/evaluaciones/${evalId}/controles/${encodeURIComponent(ctrlId)}/comentarios`); },
    agregarComentario(evalId, ctrlId, texto) { return post(`/api/evaluaciones/${evalId}/controles/${encodeURIComponent(ctrlId)}/comentarios`, { texto }); },

    /* Evidencias */
    evidencias(evalId, ctrlId)        { return get(`/api/evaluaciones/${evalId}/evidencias${ctrlId ? "?control_id=" + ctrlId : ""}`); },
    subirEvidencia(evalId, ctrlId, d) { return post(`/api/evaluaciones/${evalId}/evidencias`, { ...d, control_id: ctrlId }); },
    eliminarEvidencia(evalId, evId)   { return del(`/api/evaluaciones/${evalId}/evidencias/${evId}`); },
    /* IA — confirmar / rechazar sugerencia */
    confirmarIa(evalId, ctrlId, confirmar) {
      return post(`/api/evaluaciones/${evalId}/controles/${encodeURIComponent(ctrlId)}/confirmar-ia`, { confirmar });
    },

    /* Verificar control (analista/admin) */
    verificarControl(evalId, ctrlId) {
      return post(`/api/evaluaciones/${evalId}/controles/${encodeURIComponent(ctrlId)}/verificar`, {});
    },

    /* Cobertura */
    cobertura(evalId) { return get(`/api/evaluaciones/${evalId}/cobertura`); },

    /* Remediación */
    remediacion(evalId)         { return get(`/api/evaluaciones/${evalId}/hallazgos`); },
    avanzarEstado(id, estado)   { return post(`/api/hallazgos/${id}/estado`, { estado }); },

    /* Audit log */
    auditLog(params) {
      const q = params ? "?" + new URLSearchParams(params).toString() : "";
      return get(`/api/audit-log${q}`);
    },

    /* Usuarios */
    usuarios()               { return get("/api/usuarios"); },
    crearUsuario(d)          { return post("/api/usuarios", d); },
    actualizarUsuario(id, d) { return put(`/api/usuarios/${id}`, d); },

    /* Participantes */
    participantes()                     { return get("/api/participantes"); },
    asignados(evalId)                   { return get(`/api/evaluaciones/${evalId}/asignados`); },
    asignarParticipantes(evalId, ids)   { return post(`/api/evaluaciones/${evalId}/asignados`, { usuario_ids: ids }); },

    /* Admin — config + reminders */
    configSistema()       { return get("/api/admin/config"); },
    guardarConfig(d)      { return post("/api/admin/config", d); },
    enviarRecordatorios() { return post("/api/admin/reminders/send", {}); },
    testSmtp(to)          { return post("/api/admin/config/test-smtp", to ? { to } : {}); },

    /* Admin — ABM controles por framework */
    adminControles(fw, params) {
      const q = params ? "?" + new URLSearchParams(params).toString() : "";
      return get(`/api/admin/frameworks/${fw}/controles${q}`);
    },
    adminCrearControl(fw, d)       { return post(`/api/admin/frameworks/${fw}/controles`, d); },
    adminEditarControl(fw, id, d)  { return put(`/api/admin/frameworks/${fw}/controles/${encodeURIComponent(id)}`, d); },
    adminEliminarControl(fw, id)   { return del(`/api/admin/frameworks/${fw}/controles/${encodeURIComponent(id)}`); },

    /* Informes PDF */
    descargarInforme(evalId, tipo, framework) {
      const q = new URLSearchParams({ tipo, framework }).toString();
      // Returns a URL for direct browser download (window.open)
      return `/api/report/${evalId}?${q}`;
    },

    /* Admin — Roles y Permisos */
    permisoCatalogo()              { return get("/api/admin/permisos"); },
    roles()                        { return get("/api/admin/roles"); },
    rolDetalle(id)                 { return get(`/api/admin/roles/${id}`); },
    crearRol(d)                    { return post("/api/admin/roles", d); },
    actualizarRol(id, d)           { return put(`/api/admin/roles/${id}`, d); },
    asignarPermisos(id, permisos)  { return put(`/api/admin/roles/${id}/permisos`, { permisos }); },
    eliminarRol(id)                { return del(`/api/admin/roles/${id}`); },
  };
})();
