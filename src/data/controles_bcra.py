"""
BCRA Comunicación "A" 7777 (01/06/2023) — Texto ordenado de las normas sobre
"Requisitos mínimos para la gestión y control de los riesgos de tecnología y
seguridad de la información" (RUNOR 1-1798).

BCRA Comunicación "A" 7783 (02/06/2023) — "Requisitos mínimos para la gestión
y control de los riesgos de tecnología y seguridad de la información asociados
a los servicios financieros digitales" (RUNOR 1-1799).

Controles organizados por sección y subsección según los textos ordenados
originales del BCRA. Cada control incluye el campo 'evidencia_requerida' con
los documentos y artefactos que el auditado debe presentar para demostrar
cumplimiento.
"""

# ── Dominios por norma ───────────────────────────────────────────────────────

DOMINIOS_A7777 = {
    "S2":  "A7777 — Sec. 2: Gobierno de tecnología y seguridad de la información",
    "S3":  "A7777 — Sec. 3: Gestión de riesgos de TI y SI",
    "S4":  "A7777 — Sec. 4: Gestión de tecnología de la información",
    "S5":  "A7777 — Sec. 5: Gestión de seguridad de la información",
    "S6":  "A7777 — Sec. 6: Gestión de la continuidad del negocio",
    "S7":  "A7777 — Sec. 7: Infraestructura tecnológica y procesamiento",
    "S8":  "A7777 — Sec. 8: Gestión de ciberincidentes",
    "S9":  "A7777 — Sec. 9: Desarrollo, adquisición y mantenimiento de software",
    "S10": "A7777 — Sec. 10: Gestión de la relación con terceras partes",
}

DOMINIOS_A7783 = {
    "S11": "A7783 — Servicios financieros digitales",
}

DOMINIOS_BCRA = {**DOMINIOS_A7777, **DOMINIOS_A7783}

# ── Controles ────────────────────────────────────────────────────────────────

CONTROLES_BCRA = [

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 2 — Gobierno de tecnología y seguridad de la información
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-2.1.1",
        "norma": "A7777",
        "nombre": "Directorio — Responsabilidades de gobierno de TI y SI",
        "descripcion": (
            "El Directorio o autoridad equivalente deberá: establecer y mantener componentes de gobierno "
            "respecto de la autoridad y responsabilidades para lograr la misión y objetivos del negocio; "
            "aprobar y supervisar estructuras organizacionales y políticas de alto nivel relativas al gobierno "
            "de TI y SI; monitorear continuamente el desempeño del gobierno de TI y SI; impulsar y supervisar "
            "proyectos estratégicos de TI y SI; asegurar recursos adecuados; aprobar y supervisar el marco de "
            "gestión de riesgos y el apetito de riesgo de TI; fomentar una cultura de gestión de riesgos; "
            "promover el marco de gestión de seguridad de la información; aprobar el marco de gestión de "
            "continuidad del negocio y los mecanismos de ciberresiliencia; aprobar políticas para gestionar "
            "la relación con terceras partes y para informar ciberincidentes significativos a organismos gubernamentales."
        ),
        "dominio": "S2",
        "referencia": "Com. A 7777 — Sección 2.1.1",
        "iso_mapping": ["A.5.1", "A.5.2", "A.5.4"],
        "evidencia_requerida": [
            "Actas de reuniones del Directorio con tratamiento de temas de TI y SI",
            "Política de gobierno de TI y SI aprobada formalmente por el Directorio",
            "Estructura organizacional de TI y SI aprobada (organigrama firmado)",
            "Marco de apetito de riesgo de TI aprobado por el Directorio",
            "Informes de desempeño de TI y SI presentados al Directorio",
            "Registro de proyectos estratégicos de TI supervisados por el Directorio",
        ],
    },
    {
        "id": "A7777-2.1.2",
        "norma": "A7777",
        "nombre": "Alta Gerencia — Responsabilidades de gestión de TI y SI",
        "descripcion": (
            "La Alta Gerencia deberá: diseñar estrategias y planes de TI y definir el presupuesto necesario; "
            "conocer y gestionar los riesgos de TI y SI con planes de mitigación; diseñar estrategias, planes y "
            "medidas de seguridad de la información; definir y asegurar la implementación de políticas de alto "
            "nivel; definir roles y responsabilidades para procesos de TI y SI; establecer un marco de gestión "
            "de SI para la identificación, prevención, detección, respuesta y recuperación ante ciberincidentes; "
            "implementar prácticas de control interno y gestión de riesgos; delinear el marco de gestión de "
            "continuidad del negocio; definir un esquema de control y monitoreo de procesos, servicios y/o "
            "actividades delegadas en terceras partes; asegurar la incorporación del principio de seguridad "
            "desde el diseño; aprobar protocolos de comunicación ante situaciones de crisis."
        ),
        "dominio": "S2",
        "referencia": "Com. A 7777 — Sección 2.1.2",
        "iso_mapping": ["A.5.2", "A.5.3", "A.5.4"],
        "evidencia_requerida": [
            "Plan estratégico de TI aprobado por la Alta Gerencia",
            "Presupuesto de TI y SI aprobado y documentado",
            "Matriz de roles y responsabilidades de TI y SI con asignaciones formales",
            "Políticas de alto nivel de TI y SI aprobadas (con firma de la Alta Gerencia)",
            "Planes de mitigación de riesgos de TI aprobados",
            "Protocolo de comunicación ante crisis (aprobado y vigente)",
        ],
    },
    {
        "id": "A7777-2.1.4",
        "norma": "A7777",
        "nombre": "Comité de gobierno de TI y seguridad de la información",
        "descripcion": (
            "Las entidades deberán definir al menos un comité de gobierno de TI y SI, integrado por un miembro "
            "del Directorio, miembros de la Alta Gerencia y los responsables de las áreas de TI y SI. Sus "
            "responsabilidades incluirán: vigilar y evaluar el marco de gestión de TI y SI; supervisar planes "
            "de TI y SI; supervisar la efectividad del marco de gestión de continuidad del negocio y resiliencia "
            "tecnológica; supervisar acciones correctivas ante observaciones de auditoría; monitorear los "
            "resultados del marco de gestión de riesgos; supervisar la gestión integral de ciberincidentes; "
            "mantener informado al Directorio. Deberá reunirse periódicamente y elaborar actas formales."
        ),
        "dominio": "S2",
        "referencia": "Com. A 7777 — Sección 2.1.4",
        "iso_mapping": ["A.5.2", "A.5.4"],
        "evidencia_requerida": [
            "Acta de constitución formal del Comité de TI y SI (con integrantes designados)",
            "Reglamento o carta del Comité (funciones, periodicidad, quórum)",
            "Actas de las últimas reuniones del Comité (mínimo 4 por año)",
            "Registro de seguimiento de acciones correctivas acordadas en el Comité",
            "Informes presentados al Directorio por el Comité",
        ],
    },
    {
        "id": "A7777-2.2",
        "norma": "A7777",
        "nombre": "Segregación de funciones de TI y seguridad de la información",
        "descripcion": (
            "Las entidades deberán establecer formalmente una delimitación de roles y responsabilidades que "
            "mitigue los riesgos de superposición de funciones y falta de controles por oposición de intereses, "
            "extensible a las terceras partes. Las funciones de gobierno y gestión de TI y SI no podrán acumularse "
            "con: Recursos Humanos, Relaciones Institucionales, Administración Contable, Gestión Financiera, "
            "Gestión Comercial, Marketing, Gestión de Riesgo Integral y Auditoría Interna. En casos excepcionales "
            "donde no pueda segregarse alguna función, el Directorio deberá asumir formalmente el riesgo y "
            "evidenciar la existencia de controles compensatorios realizados por sectores independientes."
        ),
        "dominio": "S2",
        "referencia": "Com. A 7777 — Sección 2.2",
        "iso_mapping": ["A.5.3", "A.6.1"],
        "evidencia_requerida": [
            "Matriz de segregación de funciones de TI y SI (actualizada)",
            "Descripciones formales de puestos con delimitación de funciones incompatibles",
            "Evidencia de controles compensatorios (si hay excepciones aprobadas por el Directorio)",
            "Resolución del Directorio asumiendo el riesgo ante funciones no segregadas (si aplica)",
        ],
    },
    {
        "id": "A7777-2.3",
        "norma": "A7777",
        "nombre": "Marco normativo de TI y seguridad de la información",
        "descripcion": (
            "Las entidades deberán establecer un marco normativo formalizado que incluya políticas, normas y "
            "procedimientos para la gestión efectiva, supervisión y control de los procesos de gestión de riesgos, "
            "tecnología, seguridad de la información, continuidad del negocio, gestión de ciberincidentes y "
            "gestión de terceras partes. Deberán implementar mecanismos para su publicación y comunicación "
            "formal a todos los involucrados (entidad y terceras partes), y establecer un proceso para su "
            "estandarización y actualización periódica."
        ),
        "dominio": "S2",
        "referencia": "Com. A 7777 — Sección 2.3",
        "iso_mapping": ["A.5.1", "A.5.31", "A.5.36"],
        "evidencia_requerida": [
            "Índice del marco normativo vigente (políticas, normas y procedimientos)",
            "Políticas aprobadas con fecha de aprobación, versión y responsable",
            "Evidencia de comunicación formal del marco normativo a empleados y terceros",
            "Proceso o calendario de revisión periódica de políticas (y registros de revisiones)",
            "Repositorio centralizado o intranet donde se publican las normas",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 3 — Gestión de riesgos de tecnología y seguridad de la información
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-3",
        "norma": "A7777",
        "nombre": "Marco de gestión de riesgos de TI y seguridad de la información",
        "descripcion": (
            "Las entidades deberán establecer un área o función de gestión de riesgos de TI y SI, independiente "
            "de las áreas que originan los riesgos y de la auditoría interna. El marco de gestión deberá: "
            "determinar la tolerancia al riesgo; establecer políticas y metodología de gestión de riesgos; "
            "establecer procedimientos de identificación y evaluación de riesgos (incluyendo terceras partes); "
            "formalizar y someter a aprobación los riesgos residuales; realizar monitoreo continuo de exposición "
            "a riesgos; establecer indicadores vinculados a la gestión de riesgos. Deberán considerarse "
            "especialmente: escenarios de resiliencia tecnológica, obsolescencia tecnológica, relación con "
            "terceras partes, uso de IA/ML, tecnología nueva o emergente, software no autorizado, DLT y "
            "escenarios de ciberincidentes relacionados con datos personales."
        ),
        "dominio": "S3",
        "referencia": "Com. A 7777 — Sección 3",
        "iso_mapping": ["A.5.7", "A.5.8", "A.6.1"],
        "evidencia_requerida": [
            "Estructura organizacional del área de Gestión de Riesgos de TI y SI (independiente)",
            "Política y metodología de gestión de riesgos de TI y SI aprobada",
            "Registro de riesgos de TI y SI actualizado (con valoración, propietario y estado)",
            "Declaración formal de tolerancia/apetito al riesgo aprobada",
            "Informes periódicos de exposición al riesgo presentados a la Alta Gerencia",
            "Indicadores clave de riesgo (KRIs) definidos y monitoreados",
            "Análisis de riesgos de escenarios específicos (IA/ML, obsolescencia, terceros, DLT)",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 4 — Gestión de tecnología de la información
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-4.1",
        "norma": "A7777",
        "nombre": "Estrategia de tecnología de la información",
        "descripcion": (
            "Las entidades deberán establecer una estrategia de TI acorde a sus operaciones, procesos y "
            "estructura, que permita la alineación entre los resultados de la gestión de TI y los requerimientos "
            "del negocio y de seguridad. Deberán: establecer objetivos estratégicos y metas vinculados con la "
            "estrategia de TI; definir planes de acción para lograr los objetivos; revisar los planes regularmente; "
            "establecer procesos para seguimiento y medición de la eficacia de la estrategia de TI."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.1",
        "iso_mapping": ["A.5.1", "A.5.8"],
        "evidencia_requerida": [
            "Plan estratégico de TI documentado y aprobado (vigente)",
            "Objetivos estratégicos de TI con métricas y metas medibles",
            "Planes de acción con responsables y cronogramas",
            "Informes de seguimiento del plan estratégico (revisiones periódicas)",
            "Evidencia de alineación entre la estrategia de TI y los objetivos del negocio",
        ],
    },
    {
        "id": "A7777-4.2",
        "norma": "A7777",
        "nombre": "Arquitectura empresarial",
        "descripcion": (
            "Las entidades deberán establecer un modelo de arquitectura empresarial que coordine la estrategia "
            "de datos, la arquitectura de tecnología y aplicaciones con los procesos del negocio. Deberá incluir "
            "principios, estándares y prácticas para: apoyar al Directorio y Alta Gerencia en decisiones de "
            "inversión en TI; favorecer la evaluación de medidas de seguridad, resiliencia operacional y gestión "
            "de datos; gestionar la complejidad del entorno; favorecer la interoperabilidad e integración con "
            "servicios propios o de terceros; comparar la arquitectura existente con los objetivos a largo plazo."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.2",
        "iso_mapping": ["A.5.8", "A.8.20"],
        "evidencia_requerida": [
            "Documento de arquitectura empresarial aprobado",
            "Diagramas de arquitectura tecnológica y de aplicaciones (actualizados)",
            "Principios y estándares de arquitectura documentados",
            "Mapa de integración e interoperabilidad con sistemas propios y de terceros",
            "Análisis de brecha (AS-IS vs. TO-BE) de arquitectura",
        ],
    },
    {
        "id": "A7777-4.3",
        "norma": "A7777",
        "nombre": "Presupuesto, inversiones y gestión de portafolio de TI",
        "descripcion": (
            "Las entidades deberán establecer prácticas efectivas para la elaboración de presupuestos de TI y "
            "evaluación continua de inversiones. Se deberán establecer canales de comunicación formales para "
            "notificar desvíos en su ejecución. Las áreas de TI y negocio deberán definir e implementar un "
            "proceso de gestión de portafolio que permita capturar, evaluar, priorizar, programar y ejecutar "
            "los requerimientos del negocio, contribuyendo a la planificación estratégica de TI y rindiendo "
            "cuentas sobre la utilización del presupuesto."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.3",
        "iso_mapping": ["A.5.8"],
        "evidencia_requerida": [
            "Presupuesto de TI aprobado para el ejercicio vigente",
            "Registro del portafolio de proyectos e iniciativas de TI",
            "Reportes de ejecución presupuestaria con análisis de desvíos",
            "Proceso documentado de priorización y aprobación de inversiones en TI",
            "Comunicaciones formales de desvíos presupuestarios a la Alta Gerencia",
        ],
    },
    {
        "id": "A7777-4.3.1",
        "norma": "A7777",
        "nombre": "Gestión de proyectos de TI",
        "descripcion": (
            "Las entidades deberán establecer un marco para la gestión de proyectos que abarque todo su ciclo "
            "de vida. Deberán definir estándares que incluyan: asignación de roles y responsabilidades; "
            "metodologías de gestión de proyectos; evaluación de riesgos del ciclo de vida; criterios de "
            "seguimiento y comunicación de desvíos; documentación y reportes de gestión. Deberán notificar "
            "a la Gerencia de Auditoría Externa de Sistemas los proyectos que involucren nuevos servicios "
            "financieros digitales o cambios en servicios existentes que traten datos de clientes, contables "
            "y/o transaccionales."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.3.1",
        "iso_mapping": ["A.5.8", "A.8.32"],
        "evidencia_requerida": [
            "Marco de gestión de proyectos documentado (metodología adoptada)",
            "Actas de inicio y cierre de proyectos significativos",
            "Informes de estado de proyectos con seguimiento de desvíos",
            "Análisis de riesgos de proyectos relevantes",
            "Registros de notificación a la Gerencia de Auditoría Externa de Sistemas (cuando aplica)",
        ],
    },
    {
        "id": "A7777-4.4",
        "norma": "A7777",
        "nombre": "Gestión de datos",
        "descripcion": (
            "Las entidades deberán definir un proceso con responsabilidades, políticas y procedimientos para la "
            "gestión de datos que abarque todas las etapas de su ciclo de vida. Deberá establecer criterios para: "
            "identificar datos estructurados y no estructurados; controlar el uso de los datos; asegurar la "
            "calidad del dato durante todo el ciclo de vida; definir necesidades de conservación, almacenamiento "
            "y copias de respaldo según la clasificación; disponer la eliminación segura de datos al final de su "
            "ciclo de vida; supervisar el cumplimiento de políticas. Clasificación de datos: deberán definir "
            "políticas considerando la participación del propietario, criterios de integridad, disponibilidad, "
            "confidencialidad y valor para el negocio."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.4",
        "iso_mapping": ["A.5.9", "A.5.10", "A.5.12", "A.5.13", "A.8.10"],
        "evidencia_requerida": [
            "Política de gestión de datos aprobada (ciclo de vida completo)",
            "Inventario de datos clasificados (estructurados y no estructurados)",
            "Política de clasificación de datos con criterios de integridad, disponibilidad y confidencialidad",
            "Procedimientos de eliminación segura de datos y registros de su aplicación",
            "Procedimientos de backup conforme a la clasificación de datos",
            "Evidencia de supervisión del cumplimiento de políticas de datos",
        ],
    },
    {
        "id": "A7777-4.5",
        "norma": "A7777",
        "nombre": "Gestión de activos de información",
        "descripcion": (
            "Las entidades deberán definir un proceso con responsabilidades, políticas y procedimientos para la "
            "gestión de activos de información (propios y delegados en terceras partes). Deberán mantener un "
            "inventario detallado y actualizado que incluya: identificación de propietarios; ubicación, "
            "configuración, interconexiones internas y externas, e interdependencias; clasificación del activo. "
            "La clasificación de activos deberá mantenerse actualizada durante todo el ciclo de vida y revisarse "
            "ante cambios en procesos, propietarios u otras modificaciones organizativas."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.5",
        "iso_mapping": ["A.5.9", "A.5.10", "A.5.11"],
        "evidencia_requerida": [
            "Inventario de activos de información actualizado (con propietario asignado)",
            "Política de clasificación de activos de información",
            "Evidencia de revisiones periódicas del inventario de activos",
            "Registro de activos delegados en terceras partes (con ubicación e interdependencias)",
            "Procedimiento de alta/baja/modificación de activos en el inventario",
        ],
    },
    {
        "id": "A7777-4.6",
        "norma": "A7777",
        "nombre": "Inteligencia artificial o aprendizaje automático",
        "descripcion": (
            "Las entidades deberán identificar y documentar el objetivo del uso de IA o aprendizaje automático "
            "en proyectos o procesos. Deberán establecer roles y responsabilidades para la identificación de "
            "modelos, algoritmos y conjuntos de datos utilizados. Los análisis de riesgos deberán considerar: "
            "los modelos adoptados y sus posibles discrepancias con la realidad; los datos de entrenamiento; "
            "la privacidad y afectación de usuarios; el nivel de madurez de estándares de pruebas de software. "
            "Además, deberán implementar procesos para: evitar sesgos o discriminación; documentar "
            "transparencia y explicabilidad; ejecutar revisiones periódicas de resultados respecto de la "
            "tolerancia al riesgo; comunicar al cliente el uso de este tipo de tecnología."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.6",
        "iso_mapping": ["A.5.7", "A.5.8"],
        "evidencia_requerida": [
            "Registro de modelos de IA/ML en uso (con objetivo, datos de entrenamiento y propietario)",
            "Análisis de riesgos de modelos de IA/ML (sesgos, privacidad, discrepancias)",
            "Documentación de transparencia y explicabilidad de cada modelo",
            "Evidencia de revisiones periódicas de resultados vs. tolerancia al riesgo",
            "Comunicación a clientes sobre el uso de IA/ML en los servicios (si aplica)",
        ],
    },
    {
        "id": "A7777-4.7",
        "norma": "A7777",
        "nombre": "Control y reportes de gestión de TI",
        "descripcion": (
            "Las entidades deberán definir un proceso de control sobre la gestión de áreas de TI, mediante "
            "procedimientos, herramientas y métricas que permitan el seguimiento y evaluación de tareas y "
            "cumplimiento de objetivos. Las métricas deberán incluir indicadores o umbrales para controlar "
            "desvíos y establecer planes de acciones correctivas. Los reportes de gestión deberán considerar "
            "al menos: el monitoreo de capacidad en comunicaciones, procesamiento, virtualización y hardware; "
            "rendimiento de sistemas (disponibilidad, tiempos de respuesta); gestión de cambios; cumplimiento "
            "de SLAs incluyendo terceros; avances y riesgos de proyectos; supervisión de planes de acción ante "
            "incumplimientos; gestión de infraestructura tecnológica."
        ),
        "dominio": "S4",
        "referencia": "Com. A 7777 — Sección 4.7",
        "iso_mapping": ["A.5.36", "A.8.6", "A.8.16"],
        "evidencia_requerida": [
            "Dashboard o reportes periódicos de gestión de TI (disponibilidad, capacidad, cambios)",
            "Indicadores clave de desempeño (KPIs) de TI con umbrales definidos",
            "Reportes de cumplimiento de SLAs (propios y de terceros)",
            "Informes de avance y riesgo de proyectos de TI presentados a la Alta Gerencia",
            "Planes de acción ante incumplimientos e indicadores fuera de umbral",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 5 — Gestión de seguridad de la información
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-5.1",
        "norma": "A7777",
        "nombre": "Marco de gestión de seguridad de la información",
        "descripcion": (
            "Las entidades deberán establecer un marco de gestión de la seguridad de la información que "
            "contemple: los objetivos estratégicos del negocio y de tecnología, la gestión del dato, la "
            "clasificación de datos, los activos de información y los riesgos; la protección de activos "
            "de información para asegurar la prestación de servicios y contener el impacto de eventos de "
            "seguridad; la identificación y detección de eventos que podrían dar lugar a un ciberincidente, "
            "y el diseño e implementación de medidas de respuesta planificada y oportuna; el diseño de "
            "medidas destinadas a brindar seguridad de la información en los procesos y servicios en la "
            "recuperación ante ciberincidentes."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.1",
        "iso_mapping": ["A.5.1", "A.5.2"],
        "evidencia_requerida": [
            "Marco de gestión de SI documentado y aprobado formalmente",
            "Política de seguridad de la información vigente (con fecha de aprobación y revisión)",
            "Mapa de procesos de SI que cubra protección, detección, respuesta y recuperación",
        ],
    },
    {
        "id": "A7777-5.2",
        "norma": "A7777",
        "nombre": "Estrategia de seguridad de la información",
        "descripcion": (
            "Las entidades deberán definir una estrategia de seguridad de la información alineada con la "
            "estrategia del negocio. Deberá ser consistente con la estrategia de TI, la arquitectura empresarial "
            "y los resultados de la gestión de riesgos. Deberá considerar: amenazas y vulnerabilidades asociadas "
            "a cada entorno tecnológico; recursos humanos y tecnológicos propios; requerimientos de organismos "
            "de regulación y control; dependencias de terceras partes. En la elaboración deberán: establecer "
            "objetivos estratégicos y metas; crear planes de acción; considerar la gestión de amenazas y "
            "vulnerabilidades y la clasificación de datos y activos; definir objetivos y lineamientos para la "
            "detección de eventos y amenazas; considerar la gestión de ciberincidentes."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.2",
        "iso_mapping": ["A.5.1", "A.5.7", "A.5.8"],
        "evidencia_requerida": [
            "Estrategia de seguridad de la información documentada y aprobada",
            "Objetivos estratégicos de SI con métricas e indicadores de cumplimiento",
            "Plan de acción de SI con responsables y cronogramas",
            "Evidencia de alineación con la estrategia de TI y los resultados de gestión de riesgos",
            "Análisis de amenazas y vulnerabilidades del entorno tecnológico",
        ],
    },
    {
        "id": "A7777-5.3",
        "norma": "A7777",
        "nombre": "Normas y procedimientos de seguridad de la información",
        "descripcion": (
            "Las entidades deberán establecer normas y procedimientos para gestionar, controlar y documentar "
            "las actividades de los procesos para la gestión de la seguridad de la información. Deberán "
            "incluirse como mínimo: control de accesos; contraseñas; gestión de vulnerabilidades; detección y "
            "monitoreo; criterios para compartir información de amenazas y vulnerabilidades; dispositivos de "
            "la entidad asignados a usuarios; dispositivos propios del usuario; modelado de amenazas; desarrollo "
            "seguro; detección y regularización de software no autorizado; estándares de informática forense. "
            "Además, deberán establecer estándares de seguridad sobre: implementación de configuraciones "
            "seguras (hardening); adopción, revisión e implementación de algoritmos de criptografía."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.3",
        "iso_mapping": ["A.5.1", "A.5.17", "A.8.7", "A.8.8", "A.8.9", "A.8.24"],
        "evidencia_requerida": [
            "Política de control de accesos vigente",
            "Política de gestión de contraseñas y autenticación",
            "Política de gestión de vulnerabilidades",
            "Procedimiento de detección y monitoreo de eventos de seguridad",
            "Estándar de hardening (configuraciones seguras por tipo de activo)",
            "Política de criptografía (algoritmos aprobados y vigentes)",
            "Política de uso de dispositivos de la entidad y BYOD",
            "Procedimiento de detección y regularización de software no autorizado",
            "Estándares de informática forense",
        ],
    },
    {
        "id": "A7777-5.5",
        "norma": "A7777",
        "nombre": "Programas de capacitación y concientización en SI",
        "descripcion": (
            "Las entidades deberán establecer programas de capacitación y concientización en seguridad de la "
            "información, medibles y verificables, que alcancen a toda la organización, terceros, clientes y "
            "usuarios de servicios financieros. Los programas deberán incluir: contenidos mínimos, plazos y "
            "público alcanzado; vinculación con los planes de SI; incorporación de lecciones aprendidas en "
            "ciberincidentes previos y de pruebas y ejercicios; información actualizada de seguridad para "
            "clientes. Los planes de capacitación para usuarios internos y de terceros deberán considerar: "
            "riesgos en el uso de dispositivos propios; riesgos en el uso de dispositivos asignados por la "
            "entidad; aspectos de desarrollo seguro; riesgos de software no autorizado; riesgos de shadow IT."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.5",
        "iso_mapping": ["A.6.3"],
        "evidencia_requerida": [
            "Programa anual de capacitación y concientización aprobado",
            "Registros de asistencia/completitud de capacitaciones realizadas",
            "Indicadores de cumplimiento del programa (% de cobertura de la organización)",
            "Evidencia de incorporación de lecciones aprendidas de ciberincidentes",
            "Material de concientización dirigido a clientes/usuarios de servicios financieros",
            "Resultados de evaluaciones o pruebas de phishing simulado (si aplica)",
        ],
    },
    {
        "id": "A7777-5.7.1",
        "norma": "A7777",
        "nombre": "Seguridad física y medioambiental",
        "descripcion": (
            "Las entidades deberán diseñar e implementar controles para evitar puntos únicos de falla y mitigar "
            "riesgos vinculados con la seguridad física de las áreas de procesamiento, transmisión y "
            "almacenamiento de información. Deberán establecer procedimientos para: mantenimiento preventivo y "
            "pruebas periódicas de dispositivos de control ambiental y equipos de energía redundantes; "
            "destrucción de activos acorde a su clasificación; autorización y registro del retiro y traslado "
            "de activos; monitoreo permanente de medidas de protección. Las medidas deberán incluir como "
            "mínimo: sistemas de suministro eléctrico redundante; control de temperatura y humedad; materiales "
            "ignífugos; alarmas y sistemas de detección y extinción de incendios; sistemas de video y grabación; "
            "sistemas de control de accesos físicos con segregación de permisos y registro de ingresos."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.7.1",
        "iso_mapping": ["A.7.1", "A.7.2", "A.7.3", "A.7.4", "A.7.5", "A.7.6"],
        "evidencia_requerida": [
            "Plano de áreas de procesamiento con controles físicos implementados",
            "Inventario de sistemas de seguridad física (UPS, climatización, CCTV, control de acceso, extinción)",
            "Registros de mantenimiento preventivo de sistemas de seguridad física",
            "Registros de accesos físicos al centro de procesamiento de datos",
            "Procedimiento de autorización y registro de retiro/traslado de activos",
            "Evidencia de pruebas periódicas de sistemas de energía redundante y extinción de incendios",
        ],
    },
    {
        "id": "A7777-5.7.2",
        "norma": "A7777",
        "nombre": "Control de accesos y gestión de privilegios",
        "descripcion": (
            "Las entidades deberán definir un proceso de gestión que permita solicitar, aprobar, asignar, "
            "modificar, monitorear y revocar los derechos de acceso a los activos de información. El proceso "
            "deberá: alcanzar a todos los activos incluyendo el acceso físico a los centros de procesamiento; "
            "asegurar la aplicación de segregación de funciones y mínimos privilegios; establecer criterios "
            "de asignación acorde con roles, funciones y responsabilidades; asegurar la adecuación oportuna "
            "ante cambios de puestos o desvinculaciones; definir revisiones periódicas de niveles de acceso. "
            "Para cuentas privilegiadas y de servicio deberán: mantener un inventario; restringir accesos de "
            "administración; implementar controles sobre cuentas por defecto; promover la implementación de "
            "autenticación multifactor para cuentas privilegiadas; utilizar herramientas PAM para la "
            "administración de derechos de acceso privilegiados."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.7.2",
        "iso_mapping": ["A.5.15", "A.5.16", "A.5.17", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.5"],
        "evidencia_requerida": [
            "Política de control de accesos y gestión de privilegios vigente",
            "Inventario de cuentas privilegiadas y de servicio (actualizado)",
            "Matriz de roles y permisos (RBAC/ABAC) con aprobaciones formales",
            "Evidencia de revisiones periódicas de accesos (certificación de accesos)",
            "Procedimiento de revocación de accesos ante desvinculación o cambio de rol",
            "Evidencia de implementación de MFA para cuentas privilegiadas",
            "Evidencia de herramienta PAM implementada (si aplica)",
            "Registros de solicitudes y aprobaciones de acceso",
        ],
    },
    {
        "id": "A7777-5.7.2.2",
        "norma": "A7777",
        "nombre": "Métodos de autenticación",
        "descripcion": (
            "Para la selección e implementación de métodos de autenticación y sus factores, las entidades "
            "deberán considerar los resultados de los análisis de riesgos y el cumplimiento de las políticas "
            "de control de acceso. Deberán considerarse: los factores de autenticación, la validación y el "
            "canal utilizado. Se deberán establecer medidas de protección que aseguren la integridad y "
            "confidencialidad de los factores de autenticación durante todo su ciclo de vida. Controles mínimos: "
            "secreto memorizado (contraseñas) con longitud mínima, reglas de composición, revocación de "
            "contraseñas con más de un año de antigüedad, limitación de intentos fallidos; autenticación "
            "fuera de banda con canal cifrado; dispositivos criptográficos con almacenamiento seguro de claves; "
            "OTP con algoritmos seguros y tiempo de vida definido; datos biométricos con factor de autenticación "
            "adicional."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Secciones 5.7.2.2 y 5.7.2.3",
        "iso_mapping": ["A.5.17", "A.8.5"],
        "evidencia_requerida": [
            "Estándar de métodos de autenticación vigente (con reglas mínimas por tipo de factor)",
            "Configuración de políticas de contraseñas en sistemas (longitud mínima, complejidad, vigencia)",
            "Evidencia de limitación de intentos fallidos de autenticación",
            "Documentación de autenticación fuera de banda (canal cifrado) donde aplica",
            "Inventario de dispositivos criptográficos (tokens, smartcards) en uso",
        ],
    },
    {
        "id": "A7777-5.7.2.4",
        "norma": "A7777",
        "nombre": "Requisitos generales para la autenticación multifactor",
        "descripcion": (
            "Las entidades deberán evaluar la utilización de autenticación multifactor para el acceso a los "
            "activos de información de acuerdo con su clasificación y la gestión de amenazas y vulnerabilidades. "
            "En la implementación de autenticación multifactor se deberá utilizar al menos dos factores de "
            "distinta categoría o un autenticador multifactor. Se considerará autenticador multifactor al "
            "software o hardware de generación de OTP o dispositivos criptográficos, cuando el acceso al "
            "generador requiera un factor de autenticación del tipo secreto memorizado o datos biométricos, "
            "el secreto memorizado tenga al menos 6 caracteres, y se limiten los intentos fallidos de acceso."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.7.2.4",
        "iso_mapping": ["A.8.5"],
        "evidencia_requerida": [
            "Evaluación de riesgos que justifica la aplicación de MFA por tipo de acceso",
            "Política de MFA aprobada (con alcance y requisitos mínimos)",
            "Evidencia de implementación de MFA para accesos a activos críticos",
            "Configuración del generador OTP (algoritmo, tiempo de vida, longitud mínima de 6 dígitos)",
            "Registro de excepciones al MFA con controles compensatorios documentados",
        ],
    },
    {
        "id": "A7777-5.7.4",
        "norma": "A7777",
        "nombre": "Controles sobre la información (cifrado y DLP)",
        "descripcion": (
            "Las entidades deberán implementar medidas para detectar y evitar el acceso, modificación, copia "
            "o transmisión no autorizada de información. Los controles deberán: cifrar la información en "
            "tránsito, almacenada en sistemas y en dispositivos de usuarios, en concordancia con su "
            "clasificación; segmentar el procesamiento, transmisión y almacenamiento de la información; "
            "establecer medidas para limitar los derechos de acceso a datos en entornos productivos; "
            "establecer medidas de enmascaramiento y protección en entornos no productivos; aplicar medidas "
            "de borrado seguro antes de descarte o reutilización; implementar mecanismos de protección ante "
            "código malicioso. Además, deberán implementar controles para identificar la transferencia o "
            "procesamiento no autorizados de información confidencial o crítica."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.7.4",
        "iso_mapping": ["A.8.7", "A.8.10", "A.8.11", "A.8.12", "A.8.24"],
        "evidencia_requerida": [
            "Política de cifrado de datos (en tránsito y en reposo, con algoritmos aprobados)",
            "Inventario de datos cifrados (sistemas, bases de datos, dispositivos de usuario)",
            "Evidencia de implementación de controles DLP (reportes o configuración)",
            "Procedimiento de borrado seguro de dispositivos y registros de su aplicación",
            "Evidencia de enmascaramiento de datos en entornos no productivos",
            "Reportes de antivirus/EDR y evidencia de protección contra código malicioso",
        ],
    },
    {
        "id": "A7777-5.8.1",
        "norma": "A7777",
        "nombre": "Detección, monitoreo y análisis de eventos de seguridad",
        "descripcion": (
            "Las entidades deberán establecer un proceso para el registro y análisis de información vinculada "
            "con eventos de seguridad de sistemas, redes e infraestructura tecnológica. El proceso deberá: "
            "recolectar, procesar, controlar y conservar registros de eventos y actividades de usuarios; "
            "definir medidas de mejora continua; establecer y revisar perfiles de comportamiento de usuarios "
            "y sistemas; correlacionar distintos eventos de los registros de actividad para identificar patrones "
            "sospechosos o inusuales. Como parte de este proceso deberán definir: métricas de monitoreo "
            "alineadas a la estrategia; evaluaciones continuas de riesgos y controles; umbrales para "
            "categorización y tratamiento de alertas; alertas para uso de accesos privilegiados; controles "
            "para la protección de registros de actividad; medidas para la conservación de registros de "
            "eventos y auditoría."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.8.1",
        "iso_mapping": ["A.8.15", "A.8.16", "A.8.17"],
        "evidencia_requerida": [
            "Política de monitoreo y registro de eventos de seguridad",
            "Inventario de fuentes de logs recolectadas (sistemas, redes, aplicaciones)",
            "Evidencia de implementación de SIEM o plataforma de correlación de eventos",
            "Definición de umbrales y alertas configuradas (incluyendo accesos privilegiados)",
            "Perfiles de comportamiento (UEBA) definidos y revisados periódicamente",
            "Registros conservados con evidencia de protección de integridad de logs",
            "Métricas de monitoreo reportadas periódicamente a la gerencia",
        ],
    },
    {
        "id": "A7777-5.8.2",
        "norma": "A7777",
        "nombre": "Gestión de amenazas y vulnerabilidades",
        "descripcion": (
            "Las entidades deberán establecer un proceso para recolectar, procesar, analizar e interpretar "
            "información referida a amenazas mediante métodos proactivos y reactivos. Además, deberán "
            "implementar acciones para la detección y eliminación de perfiles no autorizados en redes sociales "
            "y plataformas de comercio electrónico. El proceso de gestión de vulnerabilidades deberá: establecer "
            "puntos de contacto para la notificación de vulnerabilidades; realizar análisis y evaluación del "
            "impacto de vulnerabilidades publicadas o reportadas; establecer un plan y cronograma de mitigación "
            "por criticidad; definir medidas alternativas de mitigación cuando no existan actualizaciones "
            "disponibles; brindar información oportuna al proceso de gestión de actualizaciones de seguridad."
        ),
        "dominio": "S5",
        "referencia": "Com. A 7777 — Sección 5.8.2",
        "iso_mapping": ["A.5.7", "A.8.7", "A.8.8"],
        "evidencia_requerida": [
            "Proceso de gestión de vulnerabilidades documentado (política y procedimiento)",
            "Suscripción a fuentes de inteligencia de amenazas (feeds CTI, alertas CERT)",
            "Registro de vulnerabilidades identificadas con estado y cronograma de remediación",
            "Informes de escaneo de vulnerabilidades (con frecuencia definida)",
            "Evidencia de pruebas de penetración periódicas y planes de remediación",
            "Registro de perfiles no autorizados en redes sociales detectados y eliminados",
            "Criterios de priorización de vulnerabilidades por criticidad (CVSS u otro estándar)",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 6 — Gestión de la continuidad del negocio
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-6.1",
        "norma": "A7777",
        "nombre": "Marco de gestión de la continuidad del negocio",
        "descripcion": (
            "Las entidades deberán establecer un marco de gestión de la continuidad del negocio que considere: "
            "las disposiciones vigentes sobre lineamientos de gestión de riesgos, agregación de datos y "
            "lineamientos de respuesta y recuperación ante ciberincidentes (RRCI); los principios de resiliencia "
            "operacional; los resultados de la gestión integral de riesgos; los objetivos estratégicos del "
            "negocio; la gestión de TI y SI y el modelo de arquitectura empresarial. El marco deberá establecer "
            "como mínimo: criterios para el análisis de impacto y definición de estrategias de continuidad; "
            "lineamientos para la elaboración de planes de recuperación; medidas de mejora continua; un programa "
            "de ejercicios y testeo alineado con los de gestión de ciberincidentes; planes de capacitación."
        ),
        "dominio": "S6",
        "referencia": "Com. A 7777 — Sección 6.1",
        "iso_mapping": ["A.5.29", "A.5.30"],
        "evidencia_requerida": [
            "Política de gestión de continuidad del negocio aprobada formalmente",
            "Marco de continuidad documentado (alineado con RRCI del BCRA)",
            "Programa anual de ejercicios de continuidad aprobado",
            "Planes de capacitación en continuidad del negocio",
            "Evidencia de alineación del marco con la gestión de riesgos y arquitectura empresarial",
        ],
    },
    {
        "id": "A7777-6.2",
        "norma": "A7777",
        "nombre": "Ciberresiliencia en la continuidad del negocio",
        "descripcion": (
            "Las entidades deberán establecer medidas proactivas en el diseño de operaciones y procesos para "
            "mitigar el riesgo de eventos disruptivos y mantener la confidencialidad, integridad y disponibilidad. "
            "Se deberán aplicar medidas que fortalezcan las capacidades de recuperación ante eventos disruptivos "
            "respecto de: instalaciones, arquitectura tecnológica e infraestructura; ciberataques; estrategias "
            "de resguardos de datos y mecanismos de replicación; disponibilidad de personal esencial; servicios "
            "de terceras partes, interconexiones y dependencias; suministros de energía y abastecimiento; "
            "gestión de cambios de emergencia."
        ),
        "dominio": "S6",
        "referencia": "Com. A 7777 — Sección 6.2",
        "iso_mapping": ["A.5.29", "A.5.30", "A.8.13", "A.8.14"],
        "evidencia_requerida": [
            "Estrategia de ciberresiliencia documentada",
            "Plan de recuperación ante ciberataques específicos",
            "Estrategia y procedimiento de backups con replicación fuera de línea",
            "Mapa de dependencias críticas (terceros, interconexiones, suministros)",
            "Plan de disponibilidad de personal esencial ante eventos disruptivos",
            "Procedimiento de gestión de cambios de emergencia",
        ],
    },
    {
        "id": "A7777-6.3",
        "norma": "A7777",
        "nombre": "Análisis de impacto del negocio (BIA) y evaluación de riesgos",
        "descripcion": (
            "Las entidades deberán implementar un proceso para la elaboración de análisis de impacto del "
            "negocio (BIA) que involucre a todas las áreas y permita definir las necesidades y prioridades "
            "de recuperación. El proceso deberá incluir: definición de criterios de evaluación de impacto; "
            "identificación de actividades que soportan la prestación de productos y servicios; identificación "
            "de interdependencias de procesos; identificación de dependencias respecto de terceras partes; "
            "evaluación de posibles incidentes disruptivos; objetivos de recuperación en relación al tiempo y "
            "pérdida de datos (RTO/RPO); comunicación de resultados a la Alta Gerencia. Además, deberán "
            "realizar evaluaciones periódicas de riesgos de escenarios disruptivos y analizar riesgos asociados "
            "a ubicación geográfica y susceptibilidad a amenazas de todas las instalaciones."
        ),
        "dominio": "S6",
        "referencia": "Com. A 7777 — Sección 6.3",
        "iso_mapping": ["A.5.29", "A.5.30"],
        "evidencia_requerida": [
            "Análisis de Impacto del Negocio (BIA) actualizado (con participación de todas las áreas)",
            "Definición de RTO y RPO por proceso/servicio crítico",
            "Identificación de interdependencias de procesos y dependencias de terceras partes",
            "Evaluación de riesgos de escenarios disruptivos (por geografía, tipo de amenaza)",
            "Informe de resultados del BIA presentado a la Alta Gerencia",
        ],
    },
    {
        "id": "A7777-6.4",
        "norma": "A7777",
        "nombre": "Estrategias y planes de continuidad del negocio (BCP)",
        "descripcion": (
            "Las entidades deberán desarrollar estrategias de continuidad del negocio para cumplir con los "
            "objetivos de resiliencia y recuperación definidos. Los planes de continuidad deberán incluir como "
            "mínimo: procedimientos para la declaración de crisis y criterios de activación de planes; "
            "asignación de responsabilidades para la ejecución de planes; procedimientos detallados de "
            "recuperación e identificación de infraestructura y sistemas críticos con prioridad de recuperación; "
            "procedimientos para traslado de actividades esenciales a ubicaciones alternativas; establecimiento "
            "de canales de atención alternativos para clientes; medidas que aseguren la integridad y "
            "confidencialidad de información crítica durante los procesos de recuperación."
        ),
        "dominio": "S6",
        "referencia": "Com. A 7777 — Sección 6.4",
        "iso_mapping": ["A.5.29", "A.5.30", "A.8.13", "A.8.14"],
        "evidencia_requerida": [
            "Planes de Continuidad del Negocio (BCP) aprobados y vigentes por proceso/servicio crítico",
            "Procedimientos de declaración de crisis y criterios de activación de planes",
            "Plan de recuperación de TI (DRP) con infraestructura y sistemas críticos priorizados",
            "Acuerdos de uso de sitios/infraestructura alternativos (DRS)",
            "Procedimientos de canales de atención alternativos para clientes durante una crisis",
        ],
    },
    {
        "id": "A7777-6.6",
        "norma": "A7777",
        "nombre": "Ejercicios y pruebas de los planes de continuidad del negocio",
        "descripcion": (
            "Las entidades deberán desarrollar un plan de ejercicios y pruebas para verificar que las "
            "estrategias de continuidad y los planes establecidos respaldan adecuadamente los objetivos "
            "de continuidad del negocio. El plan deberá contener un cronograma anual formalizado que contemple "
            "al menos uno de los escenarios de más alta criticidad. Deberán participar como mínimo: el "
            "responsable de continuidad del negocio, las áreas de TI y SI, las áreas usuarias, las terceras "
            "partes vinculadas y las áreas de auditoría interna. Los resultados deberán permitir la evaluación "
            "de: eficacia de las estrategias de continuidad; desempeño de los participantes; aspectos técnicos, "
            "logísticos y administrativos; funcionamiento de la infraestructura de recuperación; deficiencias "
            "y oportunidades de mejora. Deberá mantenerse un registro detallado de resultados y planes de acción."
        ),
        "dominio": "S6",
        "referencia": "Com. A 7777 — Sección 6.6",
        "iso_mapping": ["A.5.29", "A.5.30"],
        "evidencia_requerida": [
            "Cronograma anual de ejercicios de continuidad (aprobado)",
            "Informes de resultados de ejercicios realizados (con participantes y hallazgos)",
            "Planes de acción ante deficiencias identificadas en los ejercicios",
            "Evidencia de participación de áreas usuarias, TI, SI, terceras partes y auditoría interna",
            "Evidencia de actualización de planes a partir de lecciones aprendidas",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 7 — Infraestructura tecnológica y procesamiento
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-7.1",
        "norma": "A7777",
        "nombre": "Gestión de la infraestructura tecnológica",
        "descripcion": (
            "Las entidades deberán definir estructuras, procesos y procedimientos para las actividades de "
            "gestión de actualizaciones y configuraciones, implementación de cambios, monitoreo de la "
            "infraestructura, operación de sistemas y gestión de comunicaciones. Los procesos deberán asegurar: "
            "la alineación de la infraestructura y operaciones con la arquitectura empresarial y los objetivos "
            "de resiliencia; la preservación de la confidencialidad, integridad y disponibilidad; la "
            "implementación de medidas para evitar puntos únicos de falla; la aplicación de mecanismos que "
            "aseguren la trazabilidad de las actividades de gestión. Además, deberán establecer procesos para "
            "la gestión planificada y centralizada del registro y respuesta de la demanda de servicios de TI."
        ),
        "dominio": "S7",
        "referencia": "Com. A 7777 — Sección 7.1",
        "iso_mapping": ["A.8.6", "A.8.9"],
        "evidencia_requerida": [
            "Política y procedimientos de gestión de infraestructura tecnológica",
            "Diagrama de infraestructura actualizado (con redundancias documentadas)",
            "Evidencia de medidas implementadas para evitar puntos únicos de falla",
            "Registros del sistema de gestión de servicios de TI (mesa de ayuda/ITSM)",
            "Métricas de disponibilidad de infraestructura reportadas periódicamente",
        ],
    },
    {
        "id": "A7777-7.2",
        "norma": "A7777",
        "nombre": "Gestión de cambios en producción",
        "descripcion": (
            "Las entidades deberán establecer un proceso para registrar, evaluar, planificar, revisar, aprobar "
            "y comunicar los cambios en activos de información antes de la implementación en entornos productivos. "
            "Los procedimientos deberán incluir: definición de roles y responsabilidades que mitigue riesgos de "
            "inadecuada segregación de funciones; controles por oposición de intereses; separación de entornos "
            "en las distintas etapas del ciclo de vida (desarrollo, testing, producción); definición de criterios "
            "de aprobación y mecanismos de escalamiento; análisis de impacto de los cambios; procedimientos "
            "para la administración de servicios específicos (APIs, virtualización, etc.); medidas que permitan "
            "revertir cambios ante la detección de fallas; mecanismos de trazabilidad."
        ),
        "dominio": "S7",
        "referencia": "Com. A 7777 — Sección 7.2",
        "iso_mapping": ["A.8.31", "A.8.32"],
        "evidencia_requerida": [
            "Política de gestión de cambios aprobada (con criterios de categorización y aprobación)",
            "Registro de solicitudes de cambio (RFC) con aprobaciones y análisis de impacto",
            "Evidencia de separación de entornos (desarrollo / testing / producción)",
            "Actas de CAB (Change Advisory Board) o equivalente",
            "Procedimientos de rollback documentados y probados",
            "Registros de cambios implementados con evidencia de trazabilidad",
        ],
    },
    {
        "id": "A7777-7.3",
        "norma": "A7777",
        "nombre": "Actualización de infraestructura y gestión de configuraciones",
        "descripcion": (
            "Las entidades deberán establecer un proceso de gestión de actualizaciones de infraestructura "
            "tecnológica que les permita: desarrollar un plan de actualización de activos considerando "
            "vulnerabilidades por obsolescencia; establecer un proceso de registro de cambios alineado con la "
            "gestión de activos de información; evaluar riesgos del uso de activos obsoletos e implementar "
            "medidas de mitigación. Además, deberán implementar un proceso de gestión de configuraciones que "
            "permita: establecer y actualizar estándares de configuración para hardware y software; mantener "
            "información precisa y actualizada de configuraciones; revisar y verificar configuraciones "
            "regularmente; establecer mecanismos para verificar la integridad de software y detectar cambios "
            "no autorizados. El proceso de actualizaciones de seguridad deberá ser probado antes de su "
            "implementación en producción."
        ),
        "dominio": "S7",
        "referencia": "Com. A 7777 — Sección 7.3",
        "iso_mapping": ["A.8.8", "A.8.9"],
        "evidencia_requerida": [
            "Plan de actualización de infraestructura (con activos obsoletos identificados)",
            "Estándares de configuración (hardening) por tipo de activo/plataforma",
            "Base de datos de configuraciones (CMDB) actualizada",
            "Reportes de cumplimiento de configuraciones (vs. baseline/estándar)",
            "Registro de actualizaciones de seguridad aplicadas (con evidencia de prueba previa)",
            "Evaluación de riesgos por uso de activos con soporte finalizado (EOL)",
        ],
    },
    {
        "id": "A7777-7.4",
        "norma": "A7777",
        "nombre": "Gestión de las comunicaciones de red",
        "descripcion": (
            "Las entidades deberán establecer un proceso para la gestión de las comunicaciones que permita: "
            "definición de roles y responsabilidades con adecuada segregación de funciones; mantener "
            "documentación detallada y actualizada del diseño de red, interfaces, conexiones y elementos de "
            "seguridad; asegurar la generación y conservación de registros de actividades de dispositivos de "
            "red; establecer medidas para el monitoreo de redes en tiempo real y análisis del tráfico; definir "
            "métricas para la detección de anomalías y evaluación del nivel de calidad y disponibilidad de "
            "los servicios de red; realizar revisiones periódicas de la infraestructura de comunicaciones "
            "para identificar posibles debilidades."
        ),
        "dominio": "S7",
        "referencia": "Com. A 7777 — Sección 7.4",
        "iso_mapping": ["A.8.20", "A.8.21", "A.8.22"],
        "evidencia_requerida": [
            "Diagrama de topología de red actualizado (con segmentación y elementos de seguridad)",
            "Documentación de interfaces, conexiones externas y zonas de red",
            "Logs de actividad de dispositivos de red (conservados con período definido)",
            "Evidencia de monitoreo de red en tiempo real (herramienta de NMS/NPM)",
            "Métricas de disponibilidad y calidad de servicios de red",
            "Informes de revisiones periódicas de la infraestructura de comunicaciones",
        ],
    },
    {
        "id": "A7777-7.6",
        "norma": "A7777",
        "nombre": "Gestión de copias de respaldo de datos",
        "descripcion": (
            "Las entidades deberán definir una estrategia para la realización de copias de respaldo que garantice "
            "la disponibilidad e integridad de los datos y sistemas de información. El proceso deberá incluir: "
            "procedimientos para la realización, prueba y restauración de copias (alcance, frecuencia, tipos de "
            "medios, períodos de retención y cantidad de copias); controles en la realización y conservación de "
            "copias que mitiguen riesgos de modificación o eliminación durante el período de retención; "
            "controles de acceso, mecanismos de protección y cifrado para las copias de respaldo; medidas de "
            "protección contra la replicación de malware y la corrupción de datos; conservación de copias fuera "
            "de línea acorde a la clasificación de datos. En función de requisitos legales y regulatorios, "
            "deberán realizarse al menos dos copias de la información de clientes, contable financiera y "
            "transaccional."
        ),
        "dominio": "S7",
        "referencia": "Com. A 7777 — Sección 7.6",
        "iso_mapping": ["A.8.13"],
        "evidencia_requerida": [
            "Política de backup aprobada (alcance, frecuencia, retención, tipos de medios)",
            "Registros de backups realizados (con estado de éxito/falla)",
            "Evidencia de pruebas de restauración exitosas (periódicas, al menos anual)",
            "Evidencia de al menos 2 copias de información de clientes, contable y transaccional",
            "Evidencia de copias fuera de línea (offline/air-gap) para datos críticos",
            "Controles de acceso y cifrado de los medios de backup",
        ],
    },
    {
        "id": "A7777-7.7",
        "norma": "A7777",
        "nombre": "Monitoreo de la infraestructura tecnológica y procesamiento",
        "descripcion": (
            "Las entidades deberán implementar procesos de monitoreo de la infraestructura tecnológica y del "
            "procesamiento de las operaciones para prevenir, detectar y responder oportunamente ante eventos "
            "no deseados. Se deberán establecer indicadores de desempeño que incluyan al menos: utilización "
            "de recursos y disponibilidad de servicios propios y de terceros; tiempo de respuesta o tiempo "
            "medio de conexión por servicio; fallos de los sistemas; eficiencia del procesamiento de "
            "transacciones; métricas de gestión de cambios y actualizaciones. Los resultados del monitoreo "
            "deberán ser considerados para la mejora continua y la planificación de actualizaciones, y "
            "reportados periódicamente a la Alta Gerencia."
        ),
        "dominio": "S7",
        "referencia": "Com. A 7777 — Sección 7.7",
        "iso_mapping": ["A.8.6", "A.8.16"],
        "evidencia_requerida": [
            "Dashboard de monitoreo de infraestructura (disponibilidad, utilización de recursos)",
            "KPIs de desempeño de infraestructura con umbrales definidos",
            "Alertas configuradas ante fallos de sistemas o superación de umbrales",
            "Reportes periódicos de desempeño presentados a la Alta Gerencia",
            "Planes de mejora o actualización derivados de resultados del monitoreo",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 8 — Gestión de ciberincidentes
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-8.1",
        "norma": "A7777",
        "nombre": "Preparación de la respuesta ante ciberincidentes",
        "descripcion": (
            "Las entidades deberán establecer normas y procedimientos para gestionar, controlar y documentar "
            "las actividades de la gestión de ciberincidentes; contener el impacto y restablecer capacidades "
            "y servicios; y prevenir nuevos incidentes e investigar causas. Los procedimientos deberán "
            "contener como mínimo: los circuitos y flujos de actividades ante ciberincidentes y criterios de "
            "priorización y escalamiento; una taxonomía de ciberincidentes; descripción de responsabilidades "
            "de las áreas participantes (aspectos legales, comunicación interna y externa, investigación de "
            "causa raíz); criterios de priorización basados en la criticidad o impacto; alineación con la "
            "política de continuidad del negocio; criterios para el análisis e investigación forense y "
            "conservación de evidencia; circuitos de comunicación internos y externos."
        ),
        "dominio": "S8",
        "referencia": "Com. A 7777 — Sección 8.1",
        "iso_mapping": ["A.5.24", "A.5.25", "A.5.26", "A.5.27"],
        "evidencia_requerida": [
            "Política y procedimientos de gestión de ciberincidentes aprobados",
            "Taxonomía de ciberincidentes documentada (con criterios de priorización)",
            "Flujogramas de respuesta ante ciberincidentes (con roles y escalamiento)",
            "Plan de comunicación ante crisis (interno y externo, incluyendo clientes y BCRA)",
            "Criterios y procedimientos de análisis forense y conservación de evidencia",
            "Alineación documentada con la política de continuidad del negocio",
        ],
    },
    {
        "id": "A7777-8.1.1",
        "norma": "A7777",
        "nombre": "Registro y repositorio de ciberincidentes",
        "descripcion": (
            "Las entidades deberán establecer y mantener un registro completo de sus ciberincidentes que "
            "permita la identificación, trazabilidad y evidencia de las acciones tomadas hasta su cierre. "
            "Deberán establecer un repositorio para el registro del ciberincidente y las evidencias que "
            "asegure su integridad, trazabilidad, disponibilidad y confidencialidad. Deberán realizar un "
            "registro del seguimiento de las actividades hasta la identificación de la causa raíz para "
            "asegurar su resolución y evitar su recurrencia. Se deberá analizar la información registrada "
            "para detectar la correlación entre incidentes y prevenir nuevos ciberincidentes. Cuando los "
            "ciberincidentes se relacionen con reclamos de clientes o posibles fraudes, se deberán vincular "
            "los respectivos registros para un seguimiento conjunto."
        ),
        "dominio": "S8",
        "referencia": "Com. A 7777 — Sección 8.1.1",
        "iso_mapping": ["A.5.26", "A.5.27", "A.5.28"],
        "evidencia_requerida": [
            "Repositorio/sistema de registro de ciberincidentes (con evidencia de integridad)",
            "Registro de los últimos 12 meses de ciberincidentes (con trazabilidad hasta causa raíz)",
            "Evidencia de análisis de causa raíz documentado para incidentes significativos",
            "Evidencia de correlación entre incidentes y reclamos de clientes/fraudes (si aplica)",
            "Métricas de ciberincidentes (cantidad, tiempo de detección, tiempo de resolución)",
        ],
    },
    {
        "id": "A7777-8.1.3",
        "norma": "A7777",
        "nombre": "Comunicación y notificación de ciberincidentes al BCRA",
        "descripcion": (
            "Los procedimientos de comunicación y notificación deberán permitir la comunicación eficaz de los "
            "ciberincidentes para que la respuesta sea oportuna y planificada. Las entidades deberán definir: "
            "roles para la atención ante distintos incidentes o escenarios; mecanismos para la comunicación "
            "con terceras partes, para la gestión y el reporte de ciberincidentes a las autoridades (BCRA); "
            "un punto de contacto para reportar ciberincidentes para empleados, terceras partes y público en "
            "general, a fin de mitigar el impacto de manera oportuna."
        ),
        "dominio": "S8",
        "referencia": "Com. A 7777 — Sección 8.1.3",
        "iso_mapping": ["A.5.26", "A.5.27"],
        "evidencia_requerida": [
            "Procedimiento de notificación al BCRA ante ciberincidentes significativos",
            "Canal/punto de contacto público para reporte de incidentes (empleados, terceros, clientes)",
            "Registros de notificaciones al BCRA realizadas (si hubiera ciberincidentes reportables)",
            "Evidencia de acuse de recibo o seguimiento ante reportes realizados al BCRA",
            "Directorio de contactos de respuesta ante incidentes (interno y externo)",
        ],
    },
    {
        "id": "A7777-8.2",
        "norma": "A7777",
        "nombre": "Ejercicios y pruebas de la respuesta ante ciberincidentes",
        "descripcion": (
            "Las entidades deberán establecer un plan de pruebas de las actividades previstas para la respuesta "
            "ante ciberincidentes que incluya al menos la periodicidad, los objetivos y el alcance de los "
            "ejercicios. Las pruebas deberán contemplar distintos escenarios de ciberincidentes, validando la "
            "eficacia de los procedimientos de respuesta, la coordinación entre las áreas participantes y la "
            "efectividad de los planes de comunicación. Los resultados deberán documentarse y utilizarse para "
            "la mejora continua del marco de gestión de ciberincidentes."
        ),
        "dominio": "S8",
        "referencia": "Com. A 7777 — Sección 8.2",
        "iso_mapping": ["A.5.26", "A.5.29"],
        "evidencia_requerida": [
            "Plan anual de ejercicios de respuesta ante ciberincidentes (aprobado)",
            "Informes de ejercicios y simulacros realizados (con escenarios y resultados)",
            "Planes de mejora continua derivados de los ejercicios",
            "Evidencia de validación de la coordinación inter-áreas durante los ejercicios",
            "Evidencia de actualización de procedimientos a partir de lecciones aprendidas",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 9 — Desarrollo, adquisición y mantenimiento de software
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-9.1",
        "norma": "A7777",
        "nombre": "Requisitos de seguridad para sistemas y aplicaciones",
        "descripcion": (
            "Las entidades deberán establecer un proceso para identificar, definir, documentar y gestionar "
            "los requisitos de seguridad de los sistemas y aplicaciones, tanto para los desarrollados "
            "internamente como para los adquiridos a terceros. Los requisitos de seguridad deberán ser "
            "incorporados desde las etapas iniciales del ciclo de vida del software (seguridad desde el "
            "diseño) y deberán contemplar los resultados de la gestión de riesgos, la clasificación de "
            "datos e información y los activos de información involucrados."
        ),
        "dominio": "S9",
        "referencia": "Com. A 7777 — Sección 9.1",
        "iso_mapping": ["A.8.25", "A.8.26", "A.8.27"],
        "evidencia_requerida": [
            "Política de requisitos de seguridad en el ciclo de vida del software",
            "Plantillas o listas de verificación de requisitos de seguridad por tipo de proyecto",
            "Documentación de requisitos de seguridad en proyectos de desarrollo recientes",
            "Evidencia de modelado de amenazas (threat modeling) aplicado desde el diseño",
            "Proceso de evaluación de seguridad en adquisición de software de terceros",
        ],
    },
    {
        "id": "A7777-9.2",
        "norma": "A7777",
        "nombre": "Gestión del ciclo de vida de software seguro (SSDLC)",
        "descripcion": (
            "Las entidades deberán establecer un proceso de gestión del ciclo de vida del software que "
            "incorpore controles de seguridad en todas las etapas: planificación, diseño, desarrollo, prueba, "
            "implementación y mantenimiento. Deberán establecer prácticas de desarrollo seguro que incluyan: "
            "codificación segura (según OWASP u otros estándares); revisión de código fuente; análisis de "
            "vulnerabilidades (SAST/DAST); pruebas de seguridad antes de la implementación en producción; "
            "gestión de dependencias y componentes de terceros. Las pruebas de seguridad deberán ser realizadas "
            "antes de cualquier nueva implementación o cambio significativo en los sistemas. Se deberán "
            "establecer estándares de informática forense aplicables a los sistemas de información."
        ),
        "dominio": "S9",
        "referencia": "Com. A 7777 — Sección 9.2",
        "iso_mapping": ["A.8.25", "A.8.26", "A.8.27", "A.8.28", "A.8.29", "A.8.30"],
        "evidencia_requerida": [
            "Política o estándar de desarrollo seguro (SSDLC) documentado",
            "Guías de codificación segura adoptadas (OWASP u otro estándar)",
            "Informes de análisis SAST/DAST de aplicaciones críticas",
            "Informes de pruebas de penetración de aplicaciones (pre-producción o periódicas)",
            "Proceso de gestión de dependencias y componentes de terceros (SCA)",
            "Evidencia de revisiones de código de seguridad",
            "Estándares de informática forense aplicables a sistemas",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # SECCIÓN 10 — Gestión de la relación con terceras partes
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7777-10.1",
        "norma": "A7777",
        "nombre": "Marco de gestión de la relación con terceras partes",
        "descripcion": (
            "Las entidades deberán establecer un marco de gestión de la relación con terceras partes que "
            "contemple: la identificación y evaluación de los riesgos asociados a la delegación de procesos, "
            "servicios y/o actividades en terceras partes; la definición de roles y responsabilidades para "
            "la gestión de la relación; la integración de los riesgos de terceras partes en el marco de "
            "gestión de riesgos de TI y SI; los requisitos de seguridad de la información que deben cumplir "
            "las terceras partes; los mecanismos de control y monitoreo de las actividades delegadas."
        ),
        "dominio": "S10",
        "referencia": "Com. A 7777 — Sección 10.1",
        "iso_mapping": ["A.5.19", "A.5.20", "A.5.21"],
        "evidencia_requerida": [
            "Política de gestión de terceras partes aprobada",
            "Registro de terceras partes críticas (con clasificación por nivel de riesgo)",
            "Evaluaciones de riesgo realizadas por cada tercero crítico",
            "Requisitos mínimos de seguridad definidos para terceras partes",
            "Roles y responsabilidades documentados para la gestión de la relación con terceros",
        ],
    },
    {
        "id": "A7777-10.2",
        "norma": "A7777",
        "nombre": "Formalización de la relación con terceras partes",
        "descripcion": (
            "Las entidades deberán formalizar la relación con las terceras partes mediante contratos o acuerdos "
            "que contemplen como mínimo: los servicios, procesos y/o actividades delegados; los requisitos "
            "de seguridad de la información que deben cumplir las terceras partes (incluyendo los sub-proveedores); "
            "los niveles de servicio acordados (SLAs) y las consecuencias ante su incumplimiento; el derecho "
            "a auditar a las terceras partes; los requisitos de notificación de ciberincidentes que afecten "
            "a la entidad; los planes de continuidad del negocio de las terceras partes; las condiciones de "
            "terminación del acuerdo y los planes de salida (exit plans)."
        ),
        "dominio": "S10",
        "referencia": "Com. A 7777 — Sección 10.2",
        "iso_mapping": ["A.5.19", "A.5.20", "A.5.22"],
        "evidencia_requerida": [
            "Contratos con terceras partes críticas que incluyan cláusulas de seguridad de la información",
            "SLAs formalizados con consecuencias ante incumplimiento",
            "Cláusulas de derecho a auditoría incluidas en contratos",
            "Requisitos de notificación de ciberincidentes en contratos",
            "Planes de salida (exit plans) documentados para servicios críticos",
            "Evidencia de que contratos cubren a sub-proveedores (supply chain)",
        ],
    },
    {
        "id": "A7777-10.3",
        "norma": "A7777",
        "nombre": "Control y monitoreo de terceras partes",
        "descripcion": (
            "Las entidades deberán definir e implementar un esquema de control y monitoreo continuo de los "
            "procesos, servicios y/o actividades delegadas en las terceras partes. Deberán establecer "
            "mecanismos que permitan: verificar periódicamente el cumplimiento de los requisitos de seguridad "
            "acordados; monitorear los niveles de servicio (SLAs); evaluar los riesgos derivados de cambios "
            "en la prestación de los servicios por parte de las terceras partes; gestionar las deficiencias "
            "o incumplimientos identificados; establecer planes de contingencia ante la interrupción de los "
            "servicios de las terceras partes críticas."
        ),
        "dominio": "S10",
        "referencia": "Com. A 7777 — Sección 10.3",
        "iso_mapping": ["A.5.22", "A.5.23"],
        "evidencia_requerida": [
            "Registros de monitoreo de SLAs de terceras partes (con indicadores y resultados)",
            "Informes de revisiones periódicas de cumplimiento de requisitos de seguridad de terceros",
            "Registro de incumplimientos y gestión de deficiencias identificadas en terceros",
            "Planes de contingencia ante interrupción de servicios de terceros críticos",
            "Evidencia de evaluación de riesgos ante cambios en la prestación de terceros",
        ],
    },
    {
        "id": "A7777-10.4",
        "norma": "A7777",
        "nombre": "Informes de auditoría de terceras partes",
        "descripcion": (
            "Las entidades deberán asegurar que las terceras partes que prestan servicios críticos proporcionen "
            "informes de auditoría interna y/o externa que permitan verificar el cumplimiento de los requisitos "
            "de seguridad acordados. Deberán definir la periodicidad y el alcance de dichos informes en función "
            "de la criticidad y el riesgo asociado al servicio prestado. Los resultados de las auditorías "
            "deberán ser analizados y utilizados para la mejora continua del marco de gestión de la relación "
            "con terceras partes y para la actualización de los análisis de riesgos correspondientes."
        ),
        "dominio": "S10",
        "referencia": "Com. A 7777 — Sección 10.4",
        "iso_mapping": ["A.5.20", "A.5.35", "A.5.36"],
        "evidencia_requerida": [
            "Informes de auditoría de terceras partes críticas (internos y/o externos: SOC 2, ISO 27001, PCI DSS)",
            "Evidencia de análisis de los resultados de auditorías de terceros",
            "Planes de mejora basados en hallazgos de auditorías de terceros",
            "Periodicidad y alcance de informes de auditoría definidos por nivel de criticidad",
            "Registro de seguimiento de planes de remediación de terceros",
        ],
    },

    # ══════════════════════════════════════════════════════════════════════
    # COM. A 7783 — Servicios financieros digitales
    # ══════════════════════════════════════════════════════════════════════

    {
        "id": "A7783-2",
        "norma": "A7783",
        "nombre": "Gestión de riesgos de servicios financieros digitales",
        "descripcion": (
            "Los sujetos alcanzados deberán aplicar principios y prácticas para identificar, analizar y "
            "mitigar los riesgos vinculados con la provisión de servicios financieros por medios digitales. "
            "Los análisis de riesgos deberán considerar como mínimo: riesgos operacionales (especialmente "
            "fraudes internos y a clientes, y los vinculados con TI y SI); riesgos propios de los medios por "
            "los cuales se proveen los servicios financieros digitales; riesgos vinculados a la apertura de "
            "cuenta no presencial, factores de autenticación y autorización de instrucciones en servicios "
            "digitales; el impacto en los riesgos integrales de la organización; escenarios que afecten "
            "la resiliencia operacional."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 2",
        "iso_mapping": ["A.5.7", "A.5.8"],
        "evidencia_requerida": [
            "Análisis de riesgos de servicios financieros digitales (actualizado)",
            "Identificación documentada de riesgos de fraude interno y a clientes",
            "Evaluación de riesgos de apertura de cuentas no presenciales",
            "Análisis de riesgos por canal digital (home banking, app móvil, billetera, ATM)",
            "Integración de riesgos digitales en el registro de riesgos integral",
        ],
    },
    {
        "id": "A7783-3.1",
        "norma": "A7783",
        "nombre": "Pautas para transacciones financieras digitales y acciones críticas",
        "descripcion": (
            "Los sujetos alcanzados deberán tener identificados y documentados los servicios digitales y la "
            "funcionalidad de cada uno. Deberán diseñar e implementar controles para las transacciones acordes "
            "a los resultados de la gestión de riesgos. El cliente deberá estar identificado y autenticado "
            "para efectuar cualquier tipo de transacción. Deberán aplicar técnicas de autenticación multifactor "
            "acorde a los niveles de riesgo. Para acciones críticas deberán aplicar MFA o identificación "
            "digital del cliente en: creación/habilitación/rehabilitación de factores de autenticación; "
            "suscripción a nuevos productos o servicios; cambios de puntos de contacto o parámetros "
            "operacionales; agenda de cuentas de terceros para transferencias; confirmación de transacciones "
            "que se desvíen de patrones predeterminados en sistemas de monitoreo transaccional."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 3.1",
        "iso_mapping": ["A.8.5", "A.5.17"],
        "evidencia_requerida": [
            "Inventario de servicios financieros digitales con funcionalidades documentadas",
            "Política de autenticación para transacciones digitales (con niveles de riesgo)",
            "Evidencia de MFA implementado para acciones críticas (con capturas o registros técnicos)",
            "Procedimiento de devolución inmediata ante desconocimiento de operación en atención telefónica",
            "Controles de transacciones implementados derivados del análisis de riesgos",
        ],
    },
    {
        "id": "A7783-3.2",
        "norma": "A7783",
        "nombre": "Seguridad de dispositivos y aplicaciones provistas por la organización",
        "descripcion": (
            "Los sujetos alcanzados deberán diseñar e implementar medidas de seguridad para los dispositivos "
            "y aplicaciones provistas a los clientes para brindar los servicios financieros digitales (home "
            "banking, banca móvil, billetera digital, cajeros automáticos, kioscos digitales). Los controles "
            "deberán incluir: cifrado de datos intercambiados durante toda la interacción con el cliente; "
            "medidas para detectar y finalizar la sesión de cliente no autorizada; inhabilitación del servicio "
            "ante fallas que comprometan su seguridad; en la redirección a sitios de terceros, los factores "
            "de autenticación del cliente no deben compartirse. Para aplicaciones en entornos controlados "
            "por el cliente: limitar exposición de datos personales en la instalación; impedir el acceso "
            "desde dispositivos que no satisfagan criterios de admisibilidad; aplicar medidas contra riesgos "
            "de configuraciones del sistema operativo de dispositivos móviles. Para dispositivos físicos "
            "(ATMs, kioscos): protección contra skimming, anti-tamper, detectores de objetos adosados, "
            "control dual en apertura."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 3.2",
        "iso_mapping": ["A.8.5", "A.8.9", "A.8.26"],
        "evidencia_requerida": [
            "Especificaciones de seguridad de la app móvil/home banking/billetera (cifrado, sesión, MDM)",
            "Informes de pruebas de seguridad de aplicaciones (DAST/pentesting de app móvil y web)",
            "Evidencia de controles anti-jailbreak/root en la app móvil",
            "Documentación de medidas anti-skimming y anti-tamper en ATMs/kioscos",
            "Registros de revisión/mantenimiento de dispositivos físicos (ATMs) ante manipulación",
            "Evidencia de que datos de autenticación no se comparten en redirecciones a terceros",
        ],
    },
    {
        "id": "A7783-3.3",
        "norma": "A7783",
        "nombre": "Identificación digital de clientes (onboarding no presencial)",
        "descripcion": (
            "Cuando los sujetos alcanzados admitan la identificación de personas en forma digital y no "
            "presencial, deberán diseñar procesos para corroborar la correspondencia unívoca de los datos "
            "con los de la persona que se pretende identificar. Durante el proceso de identificación deberán "
            "aplicar controles para determinar como mínimo: validación de la presencia real de la persona "
            "con prueba de vida; validación de los puntos de contacto declarados y del dispositivo móvil "
            "asociado al cliente; validación de elementos biométricos y la documentación presentada con "
            "organismos públicos. Se deberán utilizar técnicas complementarias para verificar la identidad. "
            "En caso de que el proceso de alta no se concrete: no comunicar al cliente los motivos de los "
            "errores; eliminar los datos recolectados mediante borrado seguro; los datos conservados con "
            "fines estadísticos deberán ser anonimizados."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 3.3",
        "iso_mapping": ["A.5.16", "A.8.5"],
        "evidencia_requerida": [
            "Documentación del proceso de onboarding digital (KYC digital) con controles por etapa",
            "Evidencia de implementación de prueba de vida (liveness detection) en el proceso de alta",
            "Evidencia de validación con organismos públicos (RENAPER u otro)",
            "Procedimiento de borrado seguro de datos ante alta no concretada",
            "Proceso de anonimización de datos estadísticos de altas no concretadas",
            "Evidencia de validación del dispositivo móvil asociado al cliente",
        ],
    },
    {
        "id": "A7783-3.4",
        "norma": "A7783",
        "nombre": "Control de accesos y factores de autenticación en servicios digitales",
        "descripcion": (
            "Los valores de los identificadores de acceso no podrán incluir datos personales o públicos del "
            "cliente. Las medidas mínimas para la protección de factores de autenticación durante todo su "
            "ciclo de vida: no podrán ser conocidos por el personal de la organización o de terceras partes; "
            "podrán almacenarse únicamente para su verificación con medidas adicionales de confidencialidad; "
            "deberán implementar técnicas criptográficas para su protección. Secreto memorizado: longitud "
            "mínima de 8 caracteres con letras mayúsculas, minúsculas, números y caracteres especiales; "
            "limitación de intentos fallidos. OTP: tiempo de vigencia no mayor a 120 segundos, longitud "
            "mínima de 6 dígitos. Tarjetas: autenticación dinámica, mecanismos que impidan duplicación o "
            "alteración, cifrado de datos en el chip; PIN mínimo de 4 dígitos, autenticación en línea. "
            "Los factores de autenticación no entregados al cliente deberán destruirse o desvincularse en "
            "no más de 30 días hábiles."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 3.4",
        "iso_mapping": ["A.5.17", "A.8.5"],
        "evidencia_requerida": [
            "Configuración de política de contraseñas: mínimo 8 caracteres (mayúscula, minúscula, número, especial)",
            "Evidencia de limitación de intentos fallidos de autenticación en canales digitales",
            "Configuración de OTP: vigencia ≤ 120 segundos, longitud ≥ 6 dígitos",
            "Evidencia de almacenamiento cifrado de factores de autenticación (no recuperables en texto plano)",
            "Procedimiento de destrucción/desvinculación de factores no entregados en ≤ 30 días hábiles",
            "Evidencia de que identificadores de acceso no contienen datos personales del cliente",
        ],
    },
    {
        "id": "A7783-3.5",
        "norma": "A7783",
        "nombre": "Capacitación y concientización en servicios financieros digitales",
        "descripcion": (
            "Los sujetos alcanzados deberán elaborar planes de capacitación y concientización específicos "
            "para los servicios financieros digitales que incluyan al menos: información sobre los puntos "
            "de contacto dispuestos por la organización y pautas para verificar si son genuinos; información "
            "sobre vías de contacto para notificar situaciones que podrían comprometer su seguridad, "
            "incluyendo las cuentas oficiales de redes sociales; información sobre aspectos configurables "
            "o parametrizables en el servicio financiero digital; recomendaciones específicas sobre el uso "
            "seguro de dispositivos propios del cliente; información sobre técnicas de ingeniería social "
            "y medidas de protección; recomendaciones sobre el uso de dispositivos o aplicaciones provistas "
            "por la organización; procedimientos ante el desconocimiento de una operación."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 3.5",
        "iso_mapping": ["A.6.3"],
        "evidencia_requerida": [
            "Plan de concientización en seguridad digital para clientes (aprobado y vigente)",
            "Material publicado sobre puntos de contacto genuinos de la organización",
            "Campañas de concientización sobre ingeniería social e intentos de fraude (evidencia de difusión)",
            "Información disponible en la app/web sobre configuración de parámetros de seguridad",
            "Procedimiento ante desconocimiento de operación publicado y accesible al cliente",
            "Registros de acciones de concientización (email, notificaciones push, web, redes sociales)",
        ],
    },
    {
        "id": "A7783-3.6",
        "norma": "A7783",
        "nombre": "Vías de comunicación con clientes (canales 24x7)",
        "descripcion": (
            "Los sujetos alcanzados deberán proveer vías de comunicación disponibles las 24 horas a sus "
            "clientes para la recepción, atención de consultas y denuncias, notificación de ciberincidentes "
            "y/o situaciones sospechosas. La organización deberá entregar al cliente un comprobante para "
            "el seguimiento de la comunicación. Además, deberán implementar mecanismos de comunicación "
            "alternativa con sus clientes para notificar alarmas o alertas surgidas del monitoreo "
            "transaccional, utilizando puntos de contacto del cliente previamente validados. Deberán "
            "notificar sobre: alta, baja, vinculación o rehabilitación de factores de autenticación; "
            "modificación de datos personales o parámetros para transaccionar; información transaccional "
            "relevante."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 3.6",
        "iso_mapping": ["A.5.26", "A.6.3"],
        "evidencia_requerida": [
            "Evidencia de canales de atención 24x7 disponibles para clientes (call center, chat, app)",
            "Comprobante/número de seguimiento emitido al cliente ante cada comunicación",
            "Evidencia de notificaciones automatizadas a clientes ante eventos de seguridad (alta/baja de factores, cambio de datos)",
            "Registros de alertas de monitoreo transaccional comunicadas a clientes",
            "Mecanismo de comunicación alternativa (SMS, email, push) con puntos de contacto validados",
        ],
    },
    {
        "id": "A7783-4.1",
        "norma": "A7783",
        "nombre": "Detección y análisis de eventos en servicios digitales",
        "descripcion": (
            "Los sujetos alcanzados deberán implementar mecanismos de detección y análisis de eventos "
            "para los servicios financieros digitales, incluyendo: recolección y análisis de logs de "
            "accesos, autenticaciones y transacciones; correlación de eventos para la detección de "
            "patrones de actividad sospechosa o inusual; alertas ante comportamientos que se desvíen "
            "de los perfiles de comportamiento establecidos; detección de intentos de acceso no "
            "autorizados y ataques a los factores de autenticación."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 4.1",
        "iso_mapping": ["A.8.15", "A.8.16"],
        "evidencia_requerida": [
            "Evidencia de recolección de logs de accesos, autenticaciones y transacciones digitales",
            "Reglas de correlación configuradas para detección de actividad sospechosa",
            "Alertas configuradas ante desvíos de perfiles de comportamiento de clientes",
            "Registros de detección de intentos de acceso no autorizados en canales digitales",
            "Métricas de eventos de seguridad en servicios digitales (reportadas periódicamente)",
        ],
    },
    {
        "id": "A7783-4.2",
        "norma": "A7783",
        "nombre": "Monitoreo de la actividad y transacción del cliente",
        "descripcion": (
            "Los sujetos alcanzados deberán establecer y mantener sistemas de monitoreo de la actividad "
            "y transaccional del cliente que permitan: detectar transacciones inusuales o sospechosas; "
            "identificar patrones de fraude conocidos y nuevos vectores de ataque; disparar los procesos "
            "de autenticación multifactor cuando se superen los umbrales establecidos; generar alertas "
            "para el cliente ante eventos que pudieran comprometer la seguridad de sus cuentas. Los "
            "sistemas de monitoreo transaccional deberán ser actualizados en función de los resultados "
            "de la gestión de ciberincidentes y las nuevas técnicas de ataque identificadas."
        ),
        "dominio": "S11",
        "referencia": "Com. A 7783 — Sección 4.2",
        "iso_mapping": ["A.8.16", "A.5.7"],
        "evidencia_requerida": [
            "Sistema de monitoreo transaccional implementado (documentación técnica y funcional)",
            "Reglas de detección de fraude configuradas (con umbrales y criterios de disparo de MFA)",
            "Registros de alertas generadas por monitoreo transaccional y su atención",
            "Evidencia de actualización de reglas basada en resultados de gestión de ciberincidentes",
            "Reportes de efectividad del sistema de monitoreo transaccional (tasa de detección, falsos positivos)",
        ],
    },
]
