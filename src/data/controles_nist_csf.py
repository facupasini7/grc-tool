"""
NIST Cybersecurity Framework 2.0 (CSF 2.0) — Publicado febrero 2024
6 Funciones · 22 Categorías · 106 Subcategorías
"""

DOMINIOS_NIST = {
    "GV": "Gobernar (Govern)",
    "ID": "Identificar (Identify)",
    "PR": "Proteger (Protect)",
    "DE": "Detectar (Detect)",
    "RS": "Responder (Respond)",
    "RC": "Recuperar (Recover)",
}

CATEGORIAS_NIST = {
    "GV.OC": "Contexto Organizacional",
    "GV.RM": "Estrategia de Gestión de Riesgos",
    "GV.RR": "Roles, Responsabilidades y Autoridades",
    "GV.PO": "Política",
    "GV.OV": "Supervisión",
    "GV.SC": "Gestión de Riesgos en la Cadena de Suministro",
    "ID.AM": "Gestión de Activos",
    "ID.RA": "Evaluación de Riesgos",
    "ID.IM": "Mejora Continua",
    "PR.AA": "Identidad, Autenticación y Control de Acceso",
    "PR.AT": "Concientización y Capacitación",
    "PR.DS": "Seguridad de Datos",
    "PR.PS": "Seguridad de Plataformas",
    "PR.IR": "Resiliencia de la Infraestructura Tecnológica",
    "DE.CM": "Monitoreo Continuo",
    "DE.AE": "Análisis de Eventos Adversos",
    "RS.MA": "Gestión de Incidentes",
    "RS.AN": "Análisis de Incidentes",
    "RS.CO": "Reporte y Comunicación",
    "RS.MI": "Mitigación de Incidentes",
    "RC.RP": "Ejecución del Plan de Recuperación",
    "RC.CO": "Comunicación de Recuperación",
}

CONTROLES_NIST = [
    # ── GV — GOBERNAR ────────────────────────────────────────────────────────

    # GV.OC — Contexto Organizacional (5)
    {"id":"GV.OC-01","nombre":"Misión organizacional","descripcion":"La misión de la organización se entiende e informa a las prioridades de ciberseguridad, la gestión de riesgos y los objetivos de resiliencia.","dominio":"GV","categoria":"GV.OC","tipo":["Gobernanza"]},
    {"id":"GV.OC-02","nombre":"Contexto interno y externo","descripcion":"Las vulnerabilidades, amenazas internas y externas, y el contexto legal, regulatorio y contractual que influye en la gestión de riesgos de ciberseguridad se comprenden e informan.","dominio":"GV","categoria":"GV.OC","tipo":["Gobernanza"]},
    {"id":"GV.OC-03","nombre":"Obligaciones legales y regulatorias","descripcion":"Los requisitos legales, regulatorios y contractuales de ciberseguridad se comprenden e informan a la gestión de riesgos.","dominio":"GV","categoria":"GV.OC","tipo":["Gobernanza"]},
    {"id":"GV.OC-04","nombre":"Partes interesadas críticas","descripcion":"Las necesidades y expectativas críticas de las partes interesadas de ciberseguridad se comprenden e informan a la estrategia y objetivos de ciberseguridad.","dominio":"GV","categoria":"GV.OC","tipo":["Gobernanza"]},
    {"id":"GV.OC-05","nombre":"Resultados y dependencias","descripcion":"Los resultados, capacidades y servicios de ciberseguridad de los que depende la organización se comprenden e informan a la gestión de riesgos.","dominio":"GV","categoria":"GV.OC","tipo":["Gobernanza"]},

    # GV.RM — Estrategia de Gestión de Riesgos (7)
    {"id":"GV.RM-01","nombre":"Apetito y tolerancia al riesgo","descripcion":"El apetito y la tolerancia al riesgo de ciberseguridad de la organización se determinan, comunican y aplican.","dominio":"GV","categoria":"GV.RM","tipo":["Gobernanza"]},
    {"id":"GV.RM-02","nombre":"Estrategia de riesgo organizacional","descripcion":"La estrategia de gestión de riesgos de ciberseguridad se establece, comunica y aplica en todos los niveles de la organización.","dominio":"GV","categoria":"GV.RM","tipo":["Gobernanza"]},
    {"id":"GV.RM-03","nombre":"Integración con gestión de riesgos empresarial","descripcion":"La gestión de riesgos de ciberseguridad está integrada con la gestión de riesgos empresarial.","dominio":"GV","categoria":"GV.RM","tipo":["Gobernanza"]},
    {"id":"GV.RM-04","nombre":"Recursos de gestión de riesgos","descripcion":"Se asignan suficientes recursos para una estrategia y plan de gestión de riesgos de ciberseguridad.","dominio":"GV","categoria":"GV.RM","tipo":["Gobernanza"]},
    {"id":"GV.RM-05","nombre":"Riesgos de privacidad","descripcion":"Los riesgos de privacidad se identifican, priorizan y abordan con la supervisión y aprobación apropiadas.","dominio":"GV","categoria":"GV.RM","tipo":["Gobernanza"]},
    {"id":"GV.RM-06","nombre":"Postura de riesgo conocida","descripcion":"Una postura de riesgo de ciberseguridad conocida y aprobada se mantiene para informar las decisiones.","dominio":"GV","categoria":"GV.RM","tipo":["Gobernanza"]},
    {"id":"GV.RM-07","nombre":"Proceso de gestión de riesgos","descripcion":"El proceso estratégico de gestión de riesgos de ciberseguridad se establece.","dominio":"GV","categoria":"GV.RM","tipo":["Gobernanza"]},

    # GV.RR — Roles, Responsabilidades y Autoridades (4)
    {"id":"GV.RR-01","nombre":"Responsabilidad ejecutiva","descripcion":"El liderazgo organizacional es responsable de las decisiones de riesgo de ciberseguridad.","dominio":"GV","categoria":"GV.RR","tipo":["Gobernanza"]},
    {"id":"GV.RR-02","nombre":"Roles y responsabilidades definidos","descripcion":"Los roles, responsabilidades y autoridades de ciberseguridad que reflejan las expectativas de la dirección se establecen, comunican y refuerzan.","dominio":"GV","categoria":"GV.RR","tipo":["Gobernanza"]},
    {"id":"GV.RR-03","nombre":"Separación de funciones","descripcion":"Los adecuados controles de separación de funciones están en su lugar y son administrados por RR.HH.","dominio":"GV","categoria":"GV.RR","tipo":["Preventivo"]},
    {"id":"GV.RR-04","nombre":"Personal de ciberseguridad","descripcion":"Se dispone de personal de ciberseguridad suficiente.","dominio":"GV","categoria":"GV.RR","tipo":["Gobernanza"]},

    # GV.PO — Política (2)
    {"id":"GV.PO-01","nombre":"Política de ciberseguridad","descripcion":"La política de ciberseguridad de la organización se establece, comunica y aplica.","dominio":"GV","categoria":"GV.PO","tipo":["Gobernanza"]},
    {"id":"GV.PO-02","nombre":"Actualización de política","descripcion":"La política de ciberseguridad refleja los requisitos del negocio, la tolerancia al riesgo y se actualiza regularmente.","dominio":"GV","categoria":"GV.PO","tipo":["Gobernanza"]},

    # GV.OV — Supervisión (3)
    {"id":"GV.OV-01","nombre":"Revisión por la dirección","descripcion":"Los resultados de los procesos de gestión de riesgos de ciberseguridad son revisados por los líderes de la organización.","dominio":"GV","categoria":"GV.OV","tipo":["Gobernanza"]},
    {"id":"GV.OV-02","nombre":"Estrategia y objetivos de ciberseguridad","descripcion":"La estrategia y los objetivos de ciberseguridad se revisan y actualizan para reflejar los cambios en el entorno de amenazas.","dominio":"GV","categoria":"GV.OV","tipo":["Gobernanza"]},
    {"id":"GV.OV-03","nombre":"Mejora del proceso de gestión de riesgos","descripcion":"El proceso de gestión de riesgos de ciberseguridad y sus resultados se revisan para informar la mejora continua.","dominio":"GV","categoria":"GV.OV","tipo":["Gobernanza"]},

    # GV.SC — Gestión de Riesgos en la Cadena de Suministro (10)
    {"id":"GV.SC-01","nombre":"Programa de seguridad de cadena de suministro","descripcion":"Se establece un programa de seguridad de la cadena de suministro de ciberseguridad, con políticas, procesos, personal y prácticas.","dominio":"GV","categoria":"GV.SC","tipo":["Gobernanza"]},
    {"id":"GV.SC-02","nombre":"Requisitos de ciberseguridad para proveedores","descripcion":"Los requisitos de ciberseguridad se establecen para todos los proveedores, clientes y socios en la cadena de suministro.","dominio":"GV","categoria":"GV.SC","tipo":["Gobernanza"]},
    {"id":"GV.SC-03","nombre":"Prácticas de gestión de riesgos de terceros","descripcion":"Las prácticas de gestión de riesgos de ciberseguridad de terceros se identifican y priorizan mediante el proceso de gestión de riesgos de la cadena de suministro.","dominio":"GV","categoria":"GV.SC","tipo":["Gobernanza"]},
    {"id":"GV.SC-04","nombre":"Proveedores gestionados","descripcion":"Los proveedores son gestionados para reducir al mínimo el riesgo de ciberseguridad de los productos y servicios que prestan.","dominio":"GV","categoria":"GV.SC","tipo":["Preventivo"]},
    {"id":"GV.SC-05","nombre":"Evaluación de proveedores","descripcion":"Los requisitos para abordar los riesgos de ciberseguridad en la cadena de suministro se incluyen en los contratos de adquisición.","dominio":"GV","categoria":"GV.SC","tipo":["Preventivo"]},
    {"id":"GV.SC-06","nombre":"Diligencia debida de proveedores","descripcion":"Se realiza diligencia debida de ciberseguridad para los proveedores, socios y terceros críticos.","dominio":"GV","categoria":"GV.SC","tipo":["Preventivo"]},
    {"id":"GV.SC-07","nombre":"Planes de respuesta para proveedores","descripcion":"Los planes y procesos de respuesta a incidentes de ciberseguridad se coordinan con los proveedores.","dominio":"GV","categoria":"GV.SC","tipo":["Correctivo"]},
    {"id":"GV.SC-08","nombre":"Seguridad de software de terceros","descripcion":"Los proveedores son evaluados para determinar la seguridad de sus prácticas de desarrollo de software.","dominio":"GV","categoria":"GV.SC","tipo":["Preventivo"]},
    {"id":"GV.SC-09","nombre":"Componentes de hardware y software","descripcion":"La procedencia de los componentes de hardware y software de los sistemas críticos se verifica antes de la adquisición.","dominio":"GV","categoria":"GV.SC","tipo":["Preventivo"]},
    {"id":"GV.SC-10","nombre":"Revisión de acuerdos con proveedores","descripcion":"Los acuerdos con proveedores se revisan regularmente con respecto a los cambios en los requisitos de ciberseguridad.","dominio":"GV","categoria":"GV.SC","tipo":["Gobernanza"]},

    # ── ID — IDENTIFICAR ─────────────────────────────────────────────────────

    # ID.AM — Gestión de Activos (8)
    {"id":"ID.AM-01","nombre":"Inventario de activos físicos","descripcion":"Se mantiene un inventario de activos físicos (hardware, infraestructura) de la organización.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},
    {"id":"ID.AM-02","nombre":"Inventario de activos de software","descripcion":"Se mantiene un inventario de software, aplicaciones, servicios y plataformas de la organización.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},
    {"id":"ID.AM-03","nombre":"Inventario de redes y sistemas","descripcion":"Se mantiene un inventario de las redes y los flujos de datos de la organización.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},
    {"id":"ID.AM-04","nombre":"Inventario de activos externos","descripcion":"Los activos del entorno externo que apoyan la misión de la organización se cataloguen en el inventario de activos.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},
    {"id":"ID.AM-05","nombre":"Inventario de activos de datos","descripcion":"Los activos de datos de la organización, especialmente los datos personales, se identifican.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},
    {"id":"ID.AM-06","nombre":"Activos de personal y terceros","descripcion":"Los activos de ciberseguridad, incluidas las capacidades del personal y de terceros, se inventarían.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},
    {"id":"ID.AM-07","nombre":"Clasificación de activos","descripcion":"Los activos de tecnología, datos y software se clasifican según criticidad e impacto potencial para la organización.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},
    {"id":"ID.AM-08","nombre":"Ciclo de vida de sistemas","descripcion":"Los sistemas se gestionan a lo largo de su ciclo de vida para abordar los riesgos.","dominio":"ID","categoria":"ID.AM","tipo":["Preventivo"]},

    # ID.RA — Evaluación de Riesgos (10)
    {"id":"ID.RA-01","nombre":"Identificación de vulnerabilidades","descripcion":"Las vulnerabilidades de los activos se identifican, validan y registran.","dominio":"ID","categoria":"ID.RA","tipo":["Preventivo"]},
    {"id":"ID.RA-02","nombre":"Fuentes de inteligencia de amenazas","descripcion":"Se recibe, analiza y difunde inteligencia de amenazas cibernéticas de fuentes internas y externas.","dominio":"ID","categoria":"ID.RA","tipo":["Detectivo"]},
    {"id":"ID.RA-03","nombre":"Identificación de amenazas","descripcion":"Las amenazas internas y externas a los activos de la organización se identifican y registran.","dominio":"ID","categoria":"ID.RA","tipo":["Preventivo"]},
    {"id":"ID.RA-04","nombre":"Impacto potencial","descripcion":"Los impactos potenciales de los eventos de ciberseguridad se identifican y registran.","dominio":"ID","categoria":"ID.RA","tipo":["Preventivo"]},
    {"id":"ID.RA-05","nombre":"Probabilidad de ocurrencia","descripcion":"La probabilidad de que ocurran eventos de ciberseguridad se estima e informa.","dominio":"ID","categoria":"ID.RA","tipo":["Preventivo"]},
    {"id":"ID.RA-06","nombre":"Determinación de riesgos","descripcion":"Los riesgos se determinan y priorizan según la probabilidad e impacto estimados de ocurrencia.","dominio":"ID","categoria":"ID.RA","tipo":["Preventivo"]},
    {"id":"ID.RA-07","nombre":"Cambios y nuevos riesgos","descripcion":"Los cambios en la organización, el entorno de amenazas, la tecnología y el panorama de riesgos se identifican e informan.","dominio":"ID","categoria":"ID.RA","tipo":["Preventivo"]},
    {"id":"ID.RA-08","nombre":"Proceso de divulgación de vulnerabilidades","descripcion":"Se establecen procesos para recibir, analizar y responder a las divulgaciones de vulnerabilidades.","dominio":"ID","categoria":"ID.RA","tipo":["Correctivo"]},
    {"id":"ID.RA-09","nombre":"Ciclo de vida de gestión de vulnerabilidades","descripcion":"El ciclo de vida de gestión de vulnerabilidades de los activos críticos incluye identificación, clasificación y remediación.","dominio":"ID","categoria":"ID.RA","tipo":["Correctivo"]},
    {"id":"ID.RA-10","nombre":"Evaluaciones de riesgo de terceros","descripcion":"Las evaluaciones de riesgos de ciberseguridad de los proveedores de la cadena de suministro se realizan periódicamente.","dominio":"ID","categoria":"ID.RA","tipo":["Preventivo"]},

    # ID.IM — Mejora Continua (4)
    {"id":"ID.IM-01","nombre":"Mejoras derivadas de evaluaciones","descripcion":"Las mejoras se identifican de los resultados de las evaluaciones.","dominio":"ID","categoria":"ID.IM","tipo":["Correctivo"]},
    {"id":"ID.IM-02","nombre":"Mejoras derivadas de ejercicios","descripcion":"Las mejoras se identifican de los resultados de las pruebas, ejercicios y simulacros.","dominio":"ID","categoria":"ID.IM","tipo":["Correctivo"]},
    {"id":"ID.IM-03","nombre":"Mejoras derivadas de incidentes","descripcion":"Las mejoras se identifican de los resultados de las actividades de respuesta y recuperación de incidentes.","dominio":"ID","categoria":"ID.IM","tipo":["Correctivo"]},
    {"id":"ID.IM-04","nombre":"Planes de mejora","descripcion":"Los planes de mejora de ciberseguridad se establecen, comunican a las partes interesadas pertinentes y se aplican.","dominio":"ID","categoria":"ID.IM","tipo":["Correctivo"]},

    # ── PR — PROTEGER ────────────────────────────────────────────────────────

    # PR.AA — Identidad, Autenticación y Control de Acceso (6)
    {"id":"PR.AA-01","nombre":"Gestión de identidades","descripcion":"Las identidades y credenciales para usuarios autorizados, servicios y hardware se gestionan por la organización.","dominio":"PR","categoria":"PR.AA","tipo":["Preventivo"]},
    {"id":"PR.AA-02","nombre":"Gestión de accesos privilegiados","descripcion":"Las identidades se gestionan y verifican con autenticación de usuario y mecanismos de control de acceso.","dominio":"PR","categoria":"PR.AA","tipo":["Preventivo"]},
    {"id":"PR.AA-03","nombre":"Autenticación fuerte","descripcion":"Los usuarios, servicios y hardware se autentican.","dominio":"PR","categoria":"PR.AA","tipo":["Preventivo"]},
    {"id":"PR.AA-04","nombre":"Autenticación de identidad","descripcion":"Los accesos se autentican de forma proporcional al riesgo que representen la transacción.","dominio":"PR","categoria":"PR.AA","tipo":["Preventivo"]},
    {"id":"PR.AA-05","nombre":"Control de acceso basado en mínimo privilegio","descripcion":"El acceso a los activos se concede con privilegios mínimos y se revoca cuando ya no es necesario.","dominio":"PR","categoria":"PR.AA","tipo":["Preventivo"]},
    {"id":"PR.AA-06","nombre":"Acceso remoto seguro","descripcion":"El acceso físico a los activos se gestiona, monitoreado y controlado.","dominio":"PR","categoria":"PR.AA","tipo":["Preventivo"]},

    # PR.AT — Concientización y Capacitación (2)
    {"id":"PR.AT-01","nombre":"Concientización del personal","descripcion":"El personal de la organización recibe concientización y capacitación en materia de ciberseguridad para que puedan realizar sus tareas relacionadas con la ciberseguridad.","dominio":"PR","categoria":"PR.AT","tipo":["Preventivo"]},
    {"id":"PR.AT-02","nombre":"Capacitación de roles específicos","descripcion":"El personal con roles y responsabilidades de ciberseguridad específicos recibe la capacitación necesaria para desarrollar las habilidades requeridas.","dominio":"PR","categoria":"PR.AT","tipo":["Preventivo"]},

    # PR.DS — Seguridad de Datos (11)
    {"id":"PR.DS-01","nombre":"Datos en reposo protegidos","descripcion":"Los datos en reposo se protegen.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-02","nombre":"Datos en tránsito protegidos","descripcion":"Los datos en tránsito se protegen.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-03","nombre":"Ciclo de vida de datos","descripcion":"Los activos de datos se gestionan formalmente durante la eliminación, transferencias y disposición.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-04","nombre":"Capacidad de registro","descripcion":"Se mantiene la capacidad adecuada para garantizar la disponibilidad y la integridad de los registros.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-05","nombre":"Protección de copias de datos","descripcion":"Las copias de seguridad de los datos se crean, protegen, mantienen y prueban.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-06","nombre":"Integridad de datos y software","descripcion":"Los mecanismos de verificación de la integridad para hardware, dispositivos, software, firmware y los datos se implementan y utilizan.","dominio":"PR","categoria":"PR.DS","tipo":["Detectivo"]},
    {"id":"PR.DS-07","nombre":"Entorno de desarrollo separado","descripcion":"Los entornos de desarrollo y pruebas están separados del entorno de producción.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-08","nombre":"Integridad del hardware","descripcion":"Los mecanismos de verificación de la integridad del hardware se utilizan para garantizar que los activos no han sido comprometidos.","dominio":"PR","categoria":"PR.DS","tipo":["Detectivo"]},
    {"id":"PR.DS-09","nombre":"Flujos de datos documentados","descripcion":"Los flujos de datos de la organización se documentan para identificar riesgos.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-10","nombre":"Integridad de datos en uso","descripcion":"La integridad de los datos se protege durante su procesamiento.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},
    {"id":"PR.DS-11","nombre":"Clasificación y uso de datos","descripcion":"Se utilizan mecanismos para verificar que los datos se acceden, usan y procesan según las políticas de la organización.","dominio":"PR","categoria":"PR.DS","tipo":["Preventivo"]},

    # PR.PS — Seguridad de Plataformas (6)
    {"id":"PR.PS-01","nombre":"Configuración segura de activos","descripcion":"Las configuraciones de seguridad se establecen, documentan, implementan y gestionan para los activos de hardware y software.","dominio":"PR","categoria":"PR.PS","tipo":["Preventivo"]},
    {"id":"PR.PS-02","nombre":"Gestión del ciclo de vida del software","descripcion":"El software se mantiene, reemplaza y elimina de forma oportuna.","dominio":"PR","categoria":"PR.PS","tipo":["Preventivo"]},
    {"id":"PR.PS-03","nombre":"Gestión del ciclo de vida del hardware","descripcion":"El hardware se mantiene, reemplaza y elimina de forma oportuna.","dominio":"PR","categoria":"PR.PS","tipo":["Preventivo"]},
    {"id":"PR.PS-04","nombre":"Generación de registros","descripcion":"Los registros con el suficiente nivel de detalle se crean o adquieren.","dominio":"PR","categoria":"PR.PS","tipo":["Detectivo"]},
    {"id":"PR.PS-05","nombre":"Instalación de software controlada","descripcion":"La instalación y ejecución de software no autorizado está prevenida.","dominio":"PR","categoria":"PR.PS","tipo":["Preventivo"]},
    {"id":"PR.PS-06","nombre":"Prácticas de codificación segura","descripcion":"Se emplean prácticas de codificación segura y sus resultados se verifican.","dominio":"PR","categoria":"PR.PS","tipo":["Preventivo"]},

    # PR.IR — Resiliencia de la Infraestructura Tecnológica (4)
    {"id":"PR.IR-01","nombre":"Capacidad de redes y entornos","descripcion":"Las redes y entornos se protegen de accesos no autorizados y otros daños potenciales.","dominio":"PR","categoria":"PR.IR","tipo":["Preventivo"]},
    {"id":"PR.IR-02","nombre":"Acceso no autorizado","descripcion":"Se limita el acceso y daño que se puede infligir a la infraestructura tecnológica crítica.","dominio":"PR","categoria":"PR.IR","tipo":["Preventivo"]},
    {"id":"PR.IR-03","nombre":"Mecanismos de recuperación","descripcion":"Los mecanismos de copia de seguridad son implementados y probados.","dominio":"PR","categoria":"PR.IR","tipo":["Correctivo"]},
    {"id":"PR.IR-04","nombre":"Continuidad y resiliencia de TI","descripcion":"La capacidad de resiliencia y la continuidad adecuadas se garantizan para los servicios de TI de la organización.","dominio":"PR","categoria":"PR.IR","tipo":["Preventivo"]},

    # ── DE — DETECTAR ────────────────────────────────────────────────────────

    # DE.CM — Monitoreo Continuo (9)
    {"id":"DE.CM-01","nombre":"Monitoreo de redes","descripcion":"Las redes y los servicios de red se monitorean para detectar eventos de ciberseguridad potenciales.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-02","nombre":"Monitoreo del entorno físico","descripcion":"El entorno físico se monitorea para detectar eventos de ciberseguridad potenciales.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-03","nombre":"Monitoreo de actividad de personal","descripcion":"La actividad del personal se monitorea para detectar eventos de ciberseguridad potenciales.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-04","nombre":"Detección de código malicioso","descripcion":"El código malicioso se detecta.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-05","nombre":"Código no autorizado","descripcion":"El código y el software no autorizados se detectan.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-06","nombre":"Actividad de proveedores de servicios","descripcion":"La actividad de los proveedores de servicios externos se monitorea para detectar posibles incidentes de ciberseguridad.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-07","nombre":"Monitoreo de vulnerabilidades","descripcion":"Se realiza el monitoreo del hardware, software, servicios, configuraciones de red y personal para encontrar vulnerabilidades.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-08","nombre":"Escaneo de vulnerabilidades","descripcion":"Los sistemas de información se escanean para identificar vulnerabilidades.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},
    {"id":"DE.CM-09","nombre":"Monitoreo de hardware y software","descripcion":"El hardware y el software se monitorean para encontrar cambios no autorizados.","dominio":"DE","categoria":"DE.CM","tipo":["Detectivo"]},

    # DE.AE — Análisis de Eventos Adversos (8)
    {"id":"DE.AE-01","nombre":"Actividad de red de base","descripcion":"Se establece y se gestiona una base de la actividad de red y operaciones esperadas de los usuarios.","dominio":"DE","categoria":"DE.AE","tipo":["Detectivo"]},
    {"id":"DE.AE-02","nombre":"Análisis de eventos detectados","descripcion":"Los eventos detectados se analizan para comprender los objetivos y métodos del ataque.","dominio":"DE","categoria":"DE.AE","tipo":["Detectivo"]},
    {"id":"DE.AE-03","nombre":"Correlación de datos de eventos","descripcion":"Los datos de eventos se recopilan y correlacionan de múltiples fuentes y sensores.","dominio":"DE","categoria":"DE.AE","tipo":["Detectivo"]},
    {"id":"DE.AE-04","nombre":"Estimación del impacto de eventos","descripcion":"Se estima el impacto de los eventos adversos.","dominio":"DE","categoria":"DE.AE","tipo":["Detectivo"]},
    {"id":"DE.AE-06","nombre":"Alerta sobre eventos detectados","descripcion":"Las alertas de eventos de ciberseguridad se generan y comunican al personal de gestión y herramientas de respuesta.","dominio":"DE","categoria":"DE.AE","tipo":["Detectivo"]},
    {"id":"DE.AE-07","nombre":"Inteligencia sobre amenazas","descripcion":"La inteligencia de amenazas cibernéticas y la información de otras fuentes se utilizan para mejorar la detección.","dominio":"DE","categoria":"DE.AE","tipo":["Detectivo"]},
    {"id":"DE.AE-08","nombre":"Identificación de incidentes","descripcion":"Los incidentes se identifican.","dominio":"DE","categoria":"DE.AE","tipo":["Detectivo"]},

    # ── RS — RESPONDER ───────────────────────────────────────────────────────

    # RS.MA — Gestión de Incidentes (5)
    {"id":"RS.MA-01","nombre":"Plan de respuesta a incidentes ejecutado","descripcion":"El plan de respuesta a incidentes se ejecuta en coordinación con las partes interesadas relevantes una vez que se declara un incidente.","dominio":"RS","categoria":"RS.MA","tipo":["Correctivo"]},
    {"id":"RS.MA-02","nombre":"Clasificación de incidentes","descripcion":"Los incidentes se clasifican y priorizan.","dominio":"RS","categoria":"RS.MA","tipo":["Correctivo"]},
    {"id":"RS.MA-03","nombre":"Escalación de incidentes","descripcion":"Los incidentes se escalan o elevan según sea necesario.","dominio":"RS","categoria":"RS.MA","tipo":["Correctivo"]},
    {"id":"RS.MA-04","nombre":"Criterios de declaración de incidentes","descripcion":"Los criterios para iniciar una declaración de incidente se establecen.","dominio":"RS","categoria":"RS.MA","tipo":["Correctivo"]},
    {"id":"RS.MA-05","nombre":"Terminación de incidentes","descripcion":"Los criterios para concluir la respuesta a incidentes se establecen y aplican.","dominio":"RS","categoria":"RS.MA","tipo":["Correctivo"]},

    # RS.AN — Análisis de Incidentes (5)
    {"id":"RS.AN-01","nombre":"Investigación de notificaciones","descripcion":"Las notificaciones de los sistemas de detección se investigan.","dominio":"RS","categoria":"RS.AN","tipo":["Correctivo"]},
    {"id":"RS.AN-02","nombre":"Comprensión del impacto del incidente","descripcion":"Se comprende el impacto del incidente.","dominio":"RS","categoria":"RS.AN","tipo":["Correctivo"]},
    {"id":"RS.AN-03","nombre":"Análisis forense","descripcion":"Se realizan análisis forenses.","dominio":"RS","categoria":"RS.AN","tipo":["Correctivo"]},
    {"id":"RS.AN-06","nombre":"Causa raíz de incidentes","descripcion":"Las acciones realizadas durante los incidentes son catalogadas para entender la causa raíz del incidente.","dominio":"RS","categoria":"RS.AN","tipo":["Correctivo"]},
    {"id":"RS.AN-07","nombre":"Identificación de sistemas afectados","descripcion":"Los sistemas, entornos operativos y datos que potencialmente están afectados se identifican.","dominio":"RS","categoria":"RS.AN","tipo":["Correctivo"]},

    # RS.CO — Reporte y Comunicación (4)
    {"id":"RS.CO-02","nombre":"Informes de incidentes a partes internas","descripcion":"Los incidentes se informan conforme a los criterios establecidos.","dominio":"RS","categoria":"RS.CO","tipo":["Correctivo"]},
    {"id":"RS.CO-03","nombre":"Compartición de información sobre incidentes","descripcion":"La información se comparte con las partes interesadas internas y externas designadas.","dominio":"RS","categoria":"RS.CO","tipo":["Correctivo"]},
    {"id":"RS.CO-04","nombre":"Coordinación con partes externas","descripcion":"La coordinación con las partes interesadas externas ocurre consistentemente con los planes de respuesta.","dominio":"RS","categoria":"RS.CO","tipo":["Correctivo"]},
    {"id":"RS.CO-05","nombre":"Información proactiva sobre vulnerabilidades","descripcion":"La información de vulnerabilidades se comparte proactivamente con partes externas designadas.","dominio":"RS","categoria":"RS.CO","tipo":["Correctivo"]},

    # RS.MI — Mitigación de Incidentes (3)
    {"id":"RS.MI-01","nombre":"Contención de incidentes","descripcion":"Los incidentes se contienen.","dominio":"RS","categoria":"RS.MI","tipo":["Correctivo"]},
    {"id":"RS.MI-02","nombre":"Erradicación de incidentes","descripcion":"Los incidentes se erradican.","dominio":"RS","categoria":"RS.MI","tipo":["Correctivo"]},
    {"id":"RS.MI-03","nombre":"Informes de vulnerabilidades nuevas","descripcion":"Las vulnerabilidades recién identificadas se mitigan o se documentan como riesgos aceptados.","dominio":"RS","categoria":"RS.MI","tipo":["Correctivo"]},

    # ── RC — RECUPERAR ───────────────────────────────────────────────────────

    # RC.RP — Ejecución del Plan de Recuperación (6)
    {"id":"RC.RP-01","nombre":"Plan de recuperación ejecutado","descripcion":"El plan de recuperación se ejecuta una vez el incidente está resuelto.","dominio":"RC","categoria":"RC.RP","tipo":["Correctivo"]},
    {"id":"RC.RP-02","nombre":"Tiempo de recuperación y objetivos","descripcion":"Los tiempos de recuperación y puntos de recuperación se consideran al establecer el plan de recuperación.","dominio":"RC","categoria":"RC.RP","tipo":["Correctivo"]},
    {"id":"RC.RP-03","nombre":"Integridad de los sistemas en recuperación","descripcion":"La seguridad de los sistemas en recuperación se verifica antes de continuar con las operaciones normales.","dominio":"RC","categoria":"RC.RP","tipo":["Correctivo"]},
    {"id":"RC.RP-04","nombre":"Tareas de recuperación críticas","descripcion":"Las tareas de recuperación más críticas para la misión se priorizan.","dominio":"RC","categoria":"RC.RP","tipo":["Correctivo"]},
    {"id":"RC.RP-05","nombre":"Integridad de copias de seguridad","descripcion":"La integridad de las copias de seguridad y demás activos de recuperación se verifica antes de su uso.","dominio":"RC","categoria":"RC.RP","tipo":["Correctivo"]},
    {"id":"RC.RP-06","nombre":"Fin del incidente declarado","descripcion":"El fin del incidente se declara en función de los criterios y el plan de recuperación.","dominio":"RC","categoria":"RC.RP","tipo":["Correctivo"]},

    # RC.CO — Comunicación de Recuperación (3)
    {"id":"RC.CO-03","nombre":"Comunicaciones de recuperación","descripcion":"Las actividades de recuperación se comunican a las partes interesadas internas y externas, así como a la dirección ejecutiva.","dominio":"RC","categoria":"RC.CO","tipo":["Correctivo"]},
    {"id":"RC.CO-04","nombre":"Reputación y divulgación pública","descripcion":"El manejo público de la imagen de la organización se gestiona con transparencia tras un incidente.","dominio":"RC","categoria":"RC.CO","tipo":["Correctivo"]},
    {"id":"RC.CO-05","nombre":"Lecciones aprendidas en recuperación","descripcion":"Las lecciones aprendidas durante las actividades de recuperación de incidentes se integran en la planificación futura.","dominio":"RC","categoria":"RC.CO","tipo":["Correctivo"]},
]
