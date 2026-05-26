"""
SOC 2 Trust Services Criteria (TSC) — AICPA 2022
Basado en los Criterios de Servicios de Confianza (TSC) del AICPA.
Categorías: CC (Criteria Comunes / Seguridad), A (Disponibilidad),
            PI (Integridad del Procesamiento), C (Confidencialidad), P (Privacidad)
"""

DOMINIOS_SOC2 = {
    "CC": "Criterios Comunes (Seguridad)",
    "A":  "Disponibilidad (Availability)",
    "PI": "Integridad del Procesamiento",
    "C":  "Confidencialidad",
    "P":  "Privacidad",
}

CATEGORIAS_SOC2 = {
    "CC1": "Control Environment",
    "CC2": "Communication and Information",
    "CC3": "Risk Assessment",
    "CC4": "Monitoring Activities",
    "CC5": "Control Activities",
    "CC6": "Logical and Physical Access Controls",
    "CC7": "System Operations",
    "CC8": "Change Management",
    "CC9": "Risk Mitigation",
    "A1":  "Additional Criteria — Availability",
    "PI1": "Additional Criteria — Processing Integrity",
    "C1":  "Additional Criteria — Confidentiality",
    "P1":  "Additional Criteria — Privacy (Notice)",
    "P2":  "Additional Criteria — Privacy (Choice & Consent)",
    "P3":  "Additional Criteria — Privacy (Collection)",
    "P4":  "Additional Criteria — Privacy (Use, Retention & Disposal)",
    "P5":  "Additional Criteria — Privacy (Access)",
    "P6":  "Additional Criteria — Privacy (Disclosure)",
    "P7":  "Additional Criteria — Privacy (Quality)",
    "P8":  "Additional Criteria — Privacy (Monitoring)",
}

CONTROLES_SOC2 = [
    # ── CC1 — Control Environment ─────────────────────────────────────────────
    {"id":"CC1.1","nombre":"COSO — Integridad y valores éticos","descripcion":"La entidad demuestra un compromiso con los valores de integridad y ética.","dominio":"CC","categoria":"CC1","tipo":["Gobernanza"]},
    {"id":"CC1.2","nombre":"Independencia y supervisión del directorio","descripcion":"El directorio demuestra independencia de la dirección y ejerce supervisión del desarrollo del sistema de control interno.","dominio":"CC","categoria":"CC1","tipo":["Gobernanza"]},
    {"id":"CC1.3","nombre":"Estructura organizacional y autoridad","descripcion":"La dirección establece, con la supervisión del directorio, estructuras, líneas de reporte y las autoridades adecuadas en la búsqueda de objetivos.","dominio":"CC","categoria":"CC1","tipo":["Gobernanza"]},
    {"id":"CC1.4","nombre":"Compromiso con la competencia","descripcion":"La organización demuestra un compromiso de atraer, desarrollar y retener personas competentes en alineación con los objetivos.","dominio":"CC","categoria":"CC1","tipo":["Gobernanza"]},
    {"id":"CC1.5","nombre":"Responsabilidad y rendición de cuentas","descripcion":"La organización hace responsables a las personas de sus responsabilidades de control interno en la persecución de objetivos.","dominio":"CC","categoria":"CC1","tipo":["Gobernanza"]},

    # ── CC2 — Communication and Information ─────────────────────────────────
    {"id":"CC2.1","nombre":"Información relevante para el control","descripcion":"La entidad obtiene o genera y utiliza información relevante y de calidad para apoyar el funcionamiento del control interno.","dominio":"CC","categoria":"CC2","tipo":["Gobernanza"]},
    {"id":"CC2.2","nombre":"Comunicación interna","descripcion":"La entidad comunica internamente la información necesaria para apoyar el funcionamiento del control interno.","dominio":"CC","categoria":"CC2","tipo":["Gobernanza"]},
    {"id":"CC2.3","nombre":"Comunicación con partes externas","descripcion":"La entidad se comunica con partes externas sobre cuestiones que afectan al funcionamiento del control interno.","dominio":"CC","categoria":"CC2","tipo":["Gobernanza"]},

    # ── CC3 — Risk Assessment ────────────────────────────────────────────────
    {"id":"CC3.1","nombre":"Objetivos de la entidad","descripcion":"La entidad especifica los objetivos con suficiente claridad para permitir la identificación y evaluación de riesgos relacionados con dichos objetivos.","dominio":"CC","categoria":"CC3","tipo":["Preventivo"]},
    {"id":"CC3.2","nombre":"Identificación y análisis de riesgos","descripcion":"La entidad identifica los riesgos para el logro de sus objetivos en toda la entidad y los analiza para determinar cómo deben gestionarse.","dominio":"CC","categoria":"CC3","tipo":["Preventivo"]},
    {"id":"CC3.3","nombre":"Evaluación del riesgo de fraude","descripcion":"La entidad considera el potencial de fraude en la evaluación de los riesgos para el logro de los objetivos.","dominio":"CC","categoria":"CC3","tipo":["Preventivo"]},
    {"id":"CC3.4","nombre":"Cambios significativos","descripcion":"La entidad identifica y evalúa los cambios que podrían afectar significativamente al sistema de control interno.","dominio":"CC","categoria":"CC3","tipo":["Preventivo"]},

    # ── CC4 — Monitoring Activities ──────────────────────────────────────────
    {"id":"CC4.1","nombre":"Evaluaciones continuas e independientes","descripcion":"La entidad selecciona, desarrolla y realiza evaluaciones continuas e independientes para verificar que los componentes del control interno existen y funcionan.","dominio":"CC","categoria":"CC4","tipo":["Detectivo"]},
    {"id":"CC4.2","nombre":"Evaluación y comunicación de deficiencias","descripcion":"La entidad evalúa y comunica las deficiencias del control interno en forma oportuna a las partes responsables.","dominio":"CC","categoria":"CC4","tipo":["Detectivo"]},

    # ── CC5 — Control Activities ─────────────────────────────────────────────
    {"id":"CC5.1","nombre":"Selección y desarrollo de controles","descripcion":"La entidad selecciona y desarrolla actividades de control que contribuyen a la mitigación de los riesgos para el logro de los objetivos.","dominio":"CC","categoria":"CC5","tipo":["Preventivo"]},
    {"id":"CC5.2","nombre":"Controles sobre tecnología","descripcion":"La entidad selecciona y desarrolla actividades de control generales sobre la tecnología para apoyar el logro de los objetivos.","dominio":"CC","categoria":"CC5","tipo":["Preventivo"]},
    {"id":"CC5.3","nombre":"Políticas y procedimientos","descripcion":"La entidad despliega las actividades de control mediante políticas y procedimientos.","dominio":"CC","categoria":"CC5","tipo":["Preventivo"]},

    # ── CC6 — Logical and Physical Access Controls ────────────────────────────
    {"id":"CC6.1","nombre":"Gestión de acceso lógico","descripcion":"La entidad implementa controles de acceso lógico sobre activos de información del sistema para protegerlos contra amenazas externas.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},
    {"id":"CC6.2","nombre":"Registro y autorización de usuarios","descripcion":"Antes del registro, la entidad registra y autoriza a los nuevos usuarios internos y externos y realiza los cambios en el acceso.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},
    {"id":"CC6.3","nombre":"Eliminación de acceso de usuarios","descripcion":"La entidad elimina el acceso de los usuarios cuando ya no es necesario.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},
    {"id":"CC6.4","nombre":"Restricción de acceso físico","descripcion":"La entidad restringe el acceso físico a las instalaciones y recursos de información protegida.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},
    {"id":"CC6.5","nombre":"Eliminación de activos","descripcion":"La entidad elimina los activos de datos cuando ya no son necesarios para cumplir con los requisitos del sistema.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},
    {"id":"CC6.6","nombre":"Amenazas de seguridad de red","descripcion":"La entidad implementa controles para gestionar las amenazas de seguridad de la red.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},
    {"id":"CC6.7","nombre":"Transmisión, movimiento y eliminación de información","descripcion":"La entidad restringe la transmisión, movimiento y eliminación de información a usuarios y sistemas autorizados.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},
    {"id":"CC6.8","nombre":"Detección y prevención de software no autorizado","descripcion":"La entidad implementa controles para prevenir o detectar el uso de software no autorizado.","dominio":"CC","categoria":"CC6","tipo":["Preventivo"]},

    # ── CC7 — System Operations ──────────────────────────────────────────────
    {"id":"CC7.1","nombre":"Detección y monitoreo de vulnerabilidades","descripcion":"Para cumplir con los objetivos, la entidad utiliza software de detección y monitoreo para identificar vulnerabilidades.","dominio":"CC","categoria":"CC7","tipo":["Detectivo"]},
    {"id":"CC7.2","nombre":"Monitoreo de la infraestructura","descripcion":"La entidad monitorea la infraestructura del sistema y el software para detectar componentes que actúen de manera diferente a lo esperado.","dominio":"CC","categoria":"CC7","tipo":["Detectivo"]},
    {"id":"CC7.3","nombre":"Evaluación de eventos de seguridad","descripcion":"La entidad evalúa los eventos de seguridad para determinar si constituyen incidentes de seguridad.","dominio":"CC","categoria":"CC7","tipo":["Detectivo"]},
    {"id":"CC7.4","nombre":"Respuesta a incidentes de seguridad","descripcion":"La entidad responde a los incidentes de seguridad identificados mediante el proceso de respuesta.","dominio":"CC","categoria":"CC7","tipo":["Correctivo"]},
    {"id":"CC7.5","nombre":"Recuperación de incidentes de seguridad","descripcion":"La entidad identifica, desarrolla e implementa actividades para recuperarse de incidentes de seguridad.","dominio":"CC","categoria":"CC7","tipo":["Correctivo"]},

    # ── CC8 — Change Management ──────────────────────────────────────────────
    {"id":"CC8.1","nombre":"Gestión de cambios en infraestructura","descripcion":"La entidad autoriza, diseña, desarrolla o adquiere, configura, documenta, prueba, aprueba e implementa cambios en la infraestructura, datos, software y procedimientos de manera controlada.","dominio":"CC","categoria":"CC8","tipo":["Preventivo"]},

    # ── CC9 — Risk Mitigation ────────────────────────────────────────────────
    {"id":"CC9.1","nombre":"Identificación y mitigación de riesgos del negocio","descripcion":"La entidad identifica, selecciona y desarrolla actividades de mitigación de riesgos para los riesgos derivados de socios de negocio potenciales.","dominio":"CC","categoria":"CC9","tipo":["Preventivo"]},
    {"id":"CC9.2","nombre":"Riesgo de proveedores y socios de negocio","descripcion":"La entidad evalúa y gestiona el riesgo asociado con proveedores y socios de negocio.","dominio":"CC","categoria":"CC9","tipo":["Preventivo"]},

    # ── A1 — Availability ────────────────────────────────────────────────────
    {"id":"A1.1","nombre":"Capacidad y rendimiento del sistema","descripcion":"La entidad mantiene, monitorea y evalúa la capacidad y rendimiento del procesamiento y el almacenamiento actuales para gestionar la disponibilidad.","dominio":"A","categoria":"A1","tipo":["Preventivo"]},
    {"id":"A1.2","nombre":"Recuperación ambiental y de datos","descripcion":"La entidad autoriza, diseña, desarrolla o adquiere, implementa, opera, aprueba, mantiene y monitorea controles ambiental físicos, de infraestructura y recuperación.","dominio":"A","categoria":"A1","tipo":["Correctivo"]},
    {"id":"A1.3","nombre":"Pruebas de recuperación","descripcion":"La entidad prueba los procedimientos de recuperación para garantizar que los sistemas puedan ser restaurados.","dominio":"A","categoria":"A1","tipo":["Correctivo"]},

    # ── PI1 — Processing Integrity ───────────────────────────────────────────
    {"id":"PI1.1","nombre":"Procesamiento completo, válido y preciso","descripcion":"La entidad obtiene o genera, utiliza y comunica datos relevantes y de calidad para apoyar el funcionamiento de los controles de integridad del procesamiento.","dominio":"PI","categoria":"PI1","tipo":["Preventivo"]},
    {"id":"PI1.2","nombre":"Autorización y validación de entradas","descripcion":"Las entradas del sistema se preparan, autorizan, identifican y validadas.","dominio":"PI","categoria":"PI1","tipo":["Preventivo"]},
    {"id":"PI1.3","nombre":"Procesamiento completo, oportuno y preciso","descripcion":"Los datos se procesan de manera completa, válida, precisa y oportuna.","dominio":"PI","categoria":"PI1","tipo":["Preventivo"]},
    {"id":"PI1.4","nombre":"Salidas completas y precisas","descripcion":"Las salidas del sistema se completan, válidas, precisas, oportunas y autorizadas.","dominio":"PI","categoria":"PI1","tipo":["Detectivo"]},
    {"id":"PI1.5","nombre":"Almacenamiento de entradas y salidas","descripcion":"Las entradas y salidas del sistema se almacenan de manera completa, precisa y oportuna.","dominio":"PI","categoria":"PI1","tipo":["Preventivo"]},

    # ── C1 — Confidentiality ─────────────────────────────────────────────────
    {"id":"C1.1","nombre":"Identificación y gestión de datos confidenciales","descripcion":"La entidad identifica y mantiene la confidencialidad de la información designada como confidencial durante todo su ciclo de vida.","dominio":"C","categoria":"C1","tipo":["Preventivo"]},
    {"id":"C1.2","nombre":"Eliminación de datos confidenciales","descripcion":"La entidad elimina la información confidencial para cumplir con los objetivos del sistema.","dominio":"C","categoria":"C1","tipo":["Preventivo"]},

    # ── P — Privacy ──────────────────────────────────────────────────────────
    {"id":"P1.1","nombre":"Aviso de privacidad","descripcion":"La entidad proporciona aviso a los sujetos de datos antes o en el momento de la recopilación de información personal.","dominio":"P","categoria":"P1","tipo":["Gobernanza"]},
    {"id":"P2.1","nombre":"Elección y consentimiento","descripcion":"La entidad comunica opciones disponibles para consentir la recopilación, uso, retención, divulgación y eliminación de información personal.","dominio":"P","categoria":"P2","tipo":["Gobernanza"]},
    {"id":"P3.1","nombre":"Recopilación de información personal","descripcion":"La entidad recopila información personal de acuerdo con sus objetivos de privacidad.","dominio":"P","categoria":"P3","tipo":["Preventivo"]},
    {"id":"P3.2","nombre":"Información personal de terceros","descripcion":"La entidad crea registros de la información personal recopilada en el transcurso de las actividades normales de operación.","dominio":"P","categoria":"P3","tipo":["Preventivo"]},
    {"id":"P4.1","nombre":"Uso de información personal","descripcion":"La entidad limita el uso de la información personal a los propósitos identificados.","dominio":"P","categoria":"P4","tipo":["Preventivo"]},
    {"id":"P4.2","nombre":"Retención de información personal","descripcion":"La entidad retiene la información personal de acuerdo con la política de privacidad.","dominio":"P","categoria":"P4","tipo":["Preventivo"]},
    {"id":"P4.3","nombre":"Eliminación de información personal","descripcion":"La entidad elimina información personal de conformidad con su política de retención y eliminación.","dominio":"P","categoria":"P4","tipo":["Preventivo"]},
    {"id":"P5.1","nombre":"Acceso a información personal","descripcion":"La entidad concede a los sujetos de datos acceso a su información personal cuando así lo solicitan.","dominio":"P","categoria":"P5","tipo":["Gobernanza"]},
    {"id":"P5.2","nombre":"Corrección de información personal","descripcion":"La entidad corrige la información personal inexacta cuando así lo solicitan los sujetos de datos.","dominio":"P","categoria":"P5","tipo":["Gobernanza"]},
    {"id":"P6.1","nombre":"Divulgación a terceros","descripcion":"La entidad divulga información personal a terceros con el consentimiento de los sujetos de datos.","dominio":"P","categoria":"P6","tipo":["Gobernanza"]},
    {"id":"P6.2","nombre":"Acuerdos con terceros","descripcion":"La entidad establece acuerdos de confidencialidad con terceros que tienen acceso a información personal.","dominio":"P","categoria":"P6","tipo":["Gobernanza"]},
    {"id":"P6.3","nombre":"Notificación de transferencia de información personal","descripcion":"La entidad notifica a los sujetos de datos sobre las transferencias de información personal a terceros.","dominio":"P","categoria":"P6","tipo":["Gobernanza"]},
    {"id":"P7.1","nombre":"Calidad y exactitud de la información personal","descripcion":"La entidad recopila y mantiene información personal exacta, actualizada, completa y relevante para los fines identificados.","dominio":"P","categoria":"P7","tipo":["Preventivo"]},
    {"id":"P8.1","nombre":"Monitoreo de cumplimiento de privacidad","descripcion":"La entidad monitorea el cumplimiento de sus objetivos de privacidad e identifica y aborda cualquier no conformidad.","dominio":"P","categoria":"P8","tipo":["Detectivo"]},
]
