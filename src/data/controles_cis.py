"""
CIS Controls v8 — Center for Internet Security
18 Controles con Safeguards (Salvaguardas) organizados por Implementation Group (IG)
IG1 = Higiene básica (56 safeguards)  — todas las organizaciones
IG2 = Fundacional (+ 74 safeguards)   — organizaciones con equipos de TI dedicados
IG3 = Organizacional (+ 23 safeguards)— organizaciones con equipo de seguridad maduro
"""

DOMINIOS_CIS = {
    "IG1": "IG1 — Higiene Cibernética Básica",
    "IG2": "IG2 — Controles Fundacionales",
    "IG3": "IG3 — Controles Organizacionales",
}

CONTROLES_CIS_GRUPOS = {
    "CIS-01": "Control 1: Inventario y Control de Activos de Empresa",
    "CIS-02": "Control 2: Inventario y Control de Activos de Software",
    "CIS-03": "Control 3: Protección de Datos",
    "CIS-04": "Control 4: Configuración Segura de Activos y Software",
    "CIS-05": "Control 5: Gestión de Cuentas",
    "CIS-06": "Control 6: Gestión del Control de Acceso",
    "CIS-07": "Control 7: Gestión Continua de Vulnerabilidades",
    "CIS-08": "Control 8: Gestión de Logs de Auditoría",
    "CIS-09": "Control 9: Protecciones de Correo Electrónico y Navegador Web",
    "CIS-10": "Control 10: Defensas contra Malware",
    "CIS-11": "Control 11: Recuperación de Datos",
    "CIS-12": "Control 12: Gestión de Infraestructura de Red",
    "CIS-13": "Control 13: Monitoreo y Defensa de Red",
    "CIS-14": "Control 14: Concientización y Capacitación en Habilidades de Seguridad",
    "CIS-15": "Control 15: Gestión de Proveedores de Servicios",
    "CIS-16": "Control 16: Seguridad del Software de Aplicación",
    "CIS-17": "Control 17: Gestión de Respuesta a Incidentes",
    "CIS-18": "Control 18: Pruebas de Penetración",
}

CONTROLES_CIS = [
    # ── Control 1: Inventario y Control de Activos de Empresa ─────────────────
    {"id":"CIS-01.1","nombre":"Establecer y mantener inventario de activos de empresa","descripcion":"Establecer y mantener un inventario detallado y preciso de todos los activos de empresa con posibilidad de almacenar, procesar o transmitir datos.","dominio":"IG1","categoria":"CIS-01","ig":1},
    {"id":"CIS-01.2","nombre":"Abordar activos no autorizados","descripcion":"Garantizar que se dispone de un proceso para abordar activos no autorizados encontrados en el inventario de forma regular.","dominio":"IG1","categoria":"CIS-01","ig":1},
    {"id":"CIS-01.3","nombre":"Utilizar una herramienta de descubrimiento de activos","descripcion":"Utilizar una herramienta de descubrimiento de activos de red activa para identificar activos conectados a la infraestructura de la empresa.","dominio":"IG2","categoria":"CIS-01","ig":2},
    {"id":"CIS-01.4","nombre":"Utilizar DHCP logging","descripcion":"Utilizar los logs del protocolo DHCP para mejorar el inventario de activos de empresa y detectar activos desconocidos.","dominio":"IG2","categoria":"CIS-01","ig":2},
    {"id":"CIS-01.5","nombre":"Utilizar un inventario pasivo de activos","descripcion":"Utilizar una herramienta de descubrimiento de activos pasiva para identificar activos conectados a la infraestructura de la empresa.","dominio":"IG3","categoria":"CIS-01","ig":3},

    # ── Control 2: Inventario y Control de Activos de Software ───────────────
    {"id":"CIS-02.1","nombre":"Establecer y mantener inventario de software","descripcion":"Establecer y mantener un inventario de todo el software autorizado utilizado en la empresa.","dominio":"IG1","categoria":"CIS-02","ig":1},
    {"id":"CIS-02.2","nombre":"Garantizar que solo el software autorizado esté instalado","descripcion":"Garantizar que solo el software con soporte activo del proveedor esté autorizado para su uso en la empresa.","dominio":"IG1","categoria":"CIS-02","ig":1},
    {"id":"CIS-02.3","nombre":"Abordar software no autorizado","descripcion":"Garantizar que se dispone de un proceso para abordar el software no autorizado.","dominio":"IG1","categoria":"CIS-02","ig":1},
    {"id":"CIS-02.4","nombre":"Utilizar software de gestión de activos de software automatizado","descripcion":"Utilizar software automatizado de inventario de activos de software para integrar e identificar el software instalado en todos los activos.","dominio":"IG2","categoria":"CIS-02","ig":2},
    {"id":"CIS-02.5","nombre":"Permitir solo bibliotecas de software autorizadas","descripcion":"Usar tecnologías como controles de aplicaciones para garantizar que solo se puedan ejecutar bibliotecas de software autorizadas.","dominio":"IG2","categoria":"CIS-02","ig":2},
    {"id":"CIS-02.6","nombre":"Permitir solo software autorizado","descripcion":"Usar tecnologías como listas de permitidos de aplicaciones para garantizar que solo se pueda ejecutar software autorizado.","dominio":"IG3","categoria":"CIS-02","ig":3},
    {"id":"CIS-02.7","nombre":"Utilizar software de control de versiones","descripcion":"Utilizar software de control de versiones que permita rastrear cambios en el software de la empresa.","dominio":"IG3","categoria":"CIS-02","ig":3},

    # ── Control 3: Protección de Datos ───────────────────────────────────────
    {"id":"CIS-03.1","nombre":"Establecer y mantener proceso de gestión de datos","descripcion":"Establecer y mantener un proceso de gestión de datos que aborde la clasificación de datos, el período de retención de datos y la eliminación.","dominio":"IG1","categoria":"CIS-03","ig":1},
    {"id":"CIS-03.2","nombre":"Establecer y mantener un inventario de datos","descripcion":"Establecer y mantener un inventario de datos de la empresa en base a los datos confidenciales de la empresa.","dominio":"IG1","categoria":"CIS-03","ig":1},
    {"id":"CIS-03.3","nombre":"Configurar listas de control de acceso a datos","descripcion":"Configurar las listas de control de acceso basadas en la necesidad de conocer y el mínimo privilegio para todos los sistemas de archivos.","dominio":"IG1","categoria":"CIS-03","ig":1},
    {"id":"CIS-03.4","nombre":"Aplicar retención de datos","descripcion":"Retener los datos de acuerdo con el proceso de gestión de datos de la empresa.","dominio":"IG1","categoria":"CIS-03","ig":1},
    {"id":"CIS-03.5","nombre":"Eliminar datos de forma segura","descripcion":"Eliminar de forma segura los datos de acuerdo con el proceso de gestión de datos de la empresa.","dominio":"IG1","categoria":"CIS-03","ig":1},
    {"id":"CIS-03.6","nombre":"Cifrar datos en dispositivos de usuario final","descripcion":"Cifrar los datos en los dispositivos de usuario final que contienen datos confidenciales de la empresa.","dominio":"IG2","categoria":"CIS-03","ig":2},
    {"id":"CIS-03.7","nombre":"Establecer y mantener un proceso de gestión de claves","descripcion":"Establecer y mantener un proceso de gestión de claves de cifrado globales.","dominio":"IG2","categoria":"CIS-03","ig":2},
    {"id":"CIS-03.8","nombre":"Establecer y mantener una arquitectura de datos","descripcion":"Establecer y mantener una arquitectura de datos para los activos de la empresa.","dominio":"IG2","categoria":"CIS-03","ig":2},
    {"id":"CIS-03.9","nombre":"Cifrar datos en medios extraíbles","descripcion":"Cifrar datos en medios extraíbles.","dominio":"IG2","categoria":"CIS-03","ig":2},
    {"id":"CIS-03.10","nombre":"Cifrar datos confidenciales en tránsito","descripcion":"Cifrar los datos confidenciales en tránsito.","dominio":"IG2","categoria":"CIS-03","ig":2},
    {"id":"CIS-03.11","nombre":"Cifrar datos confidenciales en reposo","descripcion":"Cifrar datos confidenciales en reposo en servidores, aplicaciones y bases de datos.","dominio":"IG3","categoria":"CIS-03","ig":3},
    {"id":"CIS-03.12","nombre":"Segmentar el procesamiento y almacenamiento de datos","descripcion":"Segmentar el procesamiento y almacenamiento de datos en función de la sensibilidad de los datos.","dominio":"IG3","categoria":"CIS-03","ig":3},

    # ── Control 4: Configuración Segura de Activos y Software ────────────────
    {"id":"CIS-04.1","nombre":"Establecer y mantener proceso de configuración segura","descripcion":"Establecer y mantener un proceso de configuración segura para los activos de empresa.","dominio":"IG1","categoria":"CIS-04","ig":1},
    {"id":"CIS-04.2","nombre":"Establecer y mantener configuración segura del sistema operativo","descripcion":"Establecer y mantener una configuración segura del sistema operativo para todos los sistemas de la empresa.","dominio":"IG1","categoria":"CIS-04","ig":1},
    {"id":"CIS-04.3","nombre":"Configurar el bloqueado de pantalla automático","descripcion":"Configurar el bloqueo automático en los dispositivos de la empresa.","dominio":"IG1","categoria":"CIS-04","ig":1},
    {"id":"CIS-04.4","nombre":"Implementar y gestionar un firewall en los servidores","descripcion":"Implementar y gestionar firewalls en los servidores para filtrar el tráfico no autorizado.","dominio":"IG1","categoria":"CIS-04","ig":1},
    {"id":"CIS-04.5","nombre":"Implementar y gestionar un firewall en los dispositivos de usuario final","descripcion":"Implementar y gestionar firewalls en los dispositivos de usuario final.","dominio":"IG1","categoria":"CIS-04","ig":1},
    {"id":"CIS-04.6","nombre":"Gestión de la configuración de infraestructura de red segura","descripcion":"Gestionar la configuración segura de la infraestructura de red.","dominio":"IG2","categoria":"CIS-04","ig":2},
    {"id":"CIS-04.7","nombre":"Gestionar la configuración de sistemas operativos de red","descripcion":"Gestionar la configuración segura de los sistemas operativos de red en los dispositivos de infraestructura.","dominio":"IG2","categoria":"CIS-04","ig":2},
    {"id":"CIS-04.8","nombre":"Desinstalar o deshabilitar servicios innecesarios","descripcion":"Desinstalar o deshabilitar servicios innecesarios en los activos de empresa para reducir la superficie de ataque.","dominio":"IG2","categoria":"CIS-04","ig":2},
    {"id":"CIS-04.9","nombre":"Configurar dispositivos de usuario final con DNS de confianza","descripcion":"Configurar los dispositivos de usuario final para que utilicen servidores DNS gestionados por la empresa.","dominio":"IG2","categoria":"CIS-04","ig":2},
    {"id":"CIS-04.10","nombre":"Aplicar políticas automáticas de configuración segura en dispositivos de usuario final","descripcion":"Configurar y gestionar una herramienta de gestión de configuración que aplique automáticamente las configuraciones a los dispositivos de usuario final.","dominio":"IG3","categoria":"CIS-04","ig":3},
    {"id":"CIS-04.11","nombre":"Aplicar políticas automáticas de configuración segura en servidores","descripcion":"Configurar y gestionar una herramienta de gestión de configuración que aplique automáticamente las configuraciones a los servidores.","dominio":"IG3","categoria":"CIS-04","ig":3},
    {"id":"CIS-04.12","nombre":"Separar los sistemas de mayor riesgo","descripcion":"Separar los sistemas de mayor riesgo de los demás sistemas de la empresa mediante segmentación de red.","dominio":"IG3","categoria":"CIS-04","ig":3},

    # ── Control 5: Gestión de Cuentas ─────────────────────────────────────────
    {"id":"CIS-05.1","nombre":"Establecer y mantener un inventario de cuentas","descripcion":"Establecer y mantener un inventario de todas las cuentas de usuario de la empresa.","dominio":"IG1","categoria":"CIS-05","ig":1},
    {"id":"CIS-05.2","nombre":"Usar contraseñas únicas","descripcion":"Usar contraseñas únicas para todos los activos de empresa.","dominio":"IG1","categoria":"CIS-05","ig":1},
    {"id":"CIS-05.3","nombre":"Deshabilitar cuentas dormidas","descripcion":"Eliminar o deshabilitar cualquier cuenta que no haya sido utilizada en los últimos 45 días.","dominio":"IG1","categoria":"CIS-05","ig":1},
    {"id":"CIS-05.4","nombre":"Restringir los privilegios de administrador a las cuentas de administrador dedicadas","descripcion":"Restringir los privilegios de administrador a las cuentas de administrador dedicadas en los activos de empresa.","dominio":"IG1","categoria":"CIS-05","ig":1},
    {"id":"CIS-05.5","nombre":"Establecer y mantener un inventario de cuentas de servicio","descripcion":"Establecer y mantener un inventario de cuentas de servicio.","dominio":"IG2","categoria":"CIS-05","ig":2},
    {"id":"CIS-05.6","nombre":"Centralizar la gestión de cuentas","descripcion":"Centralizar la gestión de cuentas a través de un directorio o sistema de autenticación.","dominio":"IG2","categoria":"CIS-05","ig":2},

    # ── Control 6: Gestión del Control de Acceso ──────────────────────────────
    {"id":"CIS-06.1","nombre":"Establecer un proceso de acceso","descripcion":"Establecer y seguir un proceso para conceder acceso a los activos de empresa.","dominio":"IG1","categoria":"CIS-06","ig":1},
    {"id":"CIS-06.2","nombre":"Establecer y mantener un inventario de sistemas de autenticación y autorización","descripcion":"Establecer y mantener un inventario de los sistemas de autenticación y autorización de la empresa.","dominio":"IG2","categoria":"CIS-06","ig":2},
    {"id":"CIS-06.3","nombre":"Requerir MFA para aplicaciones externamente expuestas","descripcion":"Requerir toda la autenticación de aplicaciones externamente expuestas a la empresa para utilizar MFA.","dominio":"IG2","categoria":"CIS-06","ig":2},
    {"id":"CIS-06.4","nombre":"Requerir MFA para acceso remoto de red","descripcion":"Requerir MFA para acceso remoto a la red de la empresa.","dominio":"IG2","categoria":"CIS-06","ig":2},
    {"id":"CIS-06.5","nombre":"Requerir MFA para acceso administrativo","descripcion":"Requerir MFA para todas las cuentas administrativas.","dominio":"IG2","categoria":"CIS-06","ig":2},
    {"id":"CIS-06.6","nombre":"Establecer y mantener un inventario de sistemas de autenticación","descripcion":"Establecer y mantener un inventario de los sistemas de autenticación de la empresa, incluida la autenticación multifactor.","dominio":"IG3","categoria":"CIS-06","ig":3},
    {"id":"CIS-06.7","nombre":"Centralizar el control de acceso","descripcion":"Centralizar el control de acceso para todos los activos de la empresa a través de un directorio u otro sistema de autenticación centralizado.","dominio":"IG3","categoria":"CIS-06","ig":3},
    {"id":"CIS-06.8","nombre":"Definir y mantener un proceso de control de acceso basado en roles","descripcion":"Definir y mantener un proceso de control de acceso basado en roles para todos los activos de la empresa.","dominio":"IG3","categoria":"CIS-06","ig":3},

    # ── Control 7: Gestión Continua de Vulnerabilidades ───────────────────────
    {"id":"CIS-07.1","nombre":"Establecer y mantener un proceso de gestión de vulnerabilidades","descripcion":"Establecer y mantener un proceso de gestión de vulnerabilidades documentado.","dominio":"IG1","categoria":"CIS-07","ig":1},
    {"id":"CIS-07.2","nombre":"Establecer y mantener un sistema de clasificación de vulnerabilidades","descripcion":"Establecer y mantener un sistema de clasificación de riesgos de vulnerabilidades basado en el contexto del negocio.","dominio":"IG1","categoria":"CIS-07","ig":1},
    {"id":"CIS-07.3","nombre":"Realizar escaneos automatizados de gestión de vulnerabilidades","descripcion":"Realizar escaneos automatizados de gestión de vulnerabilidades en los activos de empresa de forma periódica.","dominio":"IG2","categoria":"CIS-07","ig":2},
    {"id":"CIS-07.4","nombre":"Realizar escaneos de vulnerabilidades de aplicaciones","descripcion":"Realizar escaneos de vulnerabilidades de aplicaciones internamente utilizando herramientas de escaneo automatizadas.","dominio":"IG2","categoria":"CIS-07","ig":2},
    {"id":"CIS-07.5","nombre":"Realizar escaneos automatizados de gestión de vulnerabilidades con credenciales","descripcion":"Realizar escaneos de gestión de vulnerabilidades con credenciales para descubrir más vulnerabilidades que sin credenciales.","dominio":"IG2","categoria":"CIS-07","ig":2},
    {"id":"CIS-07.6","nombre":"Remediar detectadas vulnerabilidades","descripcion":"Remediar las vulnerabilidades detectadas en función de la criticidad del sistema.","dominio":"IG2","categoria":"CIS-07","ig":2},
    {"id":"CIS-07.7","nombre":"Remediar vulnerabilidades del sistema operativo detectadas","descripcion":"Remediar las vulnerabilidades del sistema operativo detectadas en los activos de empresa.","dominio":"IG3","categoria":"CIS-07","ig":3},

    # ── Control 8: Gestión de Logs de Auditoría ────────────────────────────────
    {"id":"CIS-08.1","nombre":"Establecer y mantener proceso de gestión de logs de auditoría","descripcion":"Establecer y mantener un proceso de gestión de logs de auditoría para los activos de empresa.","dominio":"IG1","categoria":"CIS-08","ig":1},
    {"id":"CIS-08.2","nombre":"Recopilar logs de auditoría","descripcion":"Recopilar logs de auditoría que deben ser revisados por los sistemas de seguridad.","dominio":"IG1","categoria":"CIS-08","ig":1},
    {"id":"CIS-08.3","nombre":"Asegurarse de que el registro sea adecuado en los activos de empresa","descripcion":"Asegurarse de que los logs sean habilitados en los activos de empresa.","dominio":"IG1","categoria":"CIS-08","ig":1},
    {"id":"CIS-08.4","nombre":"Estandarizar la recopilación de logs de tiempo","descripcion":"Estandarizar la sincronización de tiempo en los activos de empresa.","dominio":"IG2","categoria":"CIS-08","ig":2},
    {"id":"CIS-08.5","nombre":"Recopilar logs de auditoría detallados","descripcion":"Configurar los sistemas de registro detallado para capturar intentos de inicio de sesión, errores del sistema, comandos de privilegiados.","dominio":"IG2","categoria":"CIS-08","ig":2},
    {"id":"CIS-08.6","nombre":"Recopilar logs de DNS","descripcion":"Recopilar los logs de solicitudes DNS en todos los activos de la empresa.","dominio":"IG2","categoria":"CIS-08","ig":2},
    {"id":"CIS-08.7","nombre":"Recopilar logs de proveedor de URL","descripcion":"Recopilar los logs de solicitudes de URL en todos los activos de la empresa.","dominio":"IG2","categoria":"CIS-08","ig":2},
    {"id":"CIS-08.8","nombre":"Recopilar logs de flujo de red","descripcion":"Recopilar logs de flujo de red en todos los activos de empresa.","dominio":"IG3","categoria":"CIS-08","ig":3},
    {"id":"CIS-08.9","nombre":"Centralizar y gestionar los logs de auditoría","descripcion":"Centralizar y gestionar la recopilación de logs de auditoría a través de una plataforma de gestión de logs.","dominio":"IG2","categoria":"CIS-08","ig":2},
    {"id":"CIS-08.10","nombre":"Retener logs de auditoría","descripcion":"Retener los logs de auditoría en todos los activos de empresa durante un mínimo de 90 días.","dominio":"IG2","categoria":"CIS-08","ig":2},
    {"id":"CIS-08.11","nombre":"Conducir revisiones de logs de auditoría","descripcion":"Conducir revisiones de logs de auditoría para detectar anomalías o eventos anormales.","dominio":"IG2","categoria":"CIS-08","ig":2},
    {"id":"CIS-08.12","nombre":"Recopilar registros de proveedores de servicios","descripcion":"Recopilar registros de proveedores de servicios donde se generan o se acceden a datos de la empresa.","dominio":"IG3","categoria":"CIS-08","ig":3},

    # ── Control 9: Protecciones de Correo y Navegador ─────────────────────────
    {"id":"CIS-09.1","nombre":"Garantizar el uso de solo navegadores y clientes de correo completamente compatibles","descripcion":"Garantizar que solo los navegadores y clientes de correo electrónico totalmente compatibles y apoyados por el fabricante sean utilizados.","dominio":"IG1","categoria":"CIS-09","ig":1},
    {"id":"CIS-09.2","nombre":"Usar servicios de filtrado DNS","descripcion":"Usar servicios de filtrado DNS en todos los activos de empresa para bloquear el acceso a sitios web maliciosos.","dominio":"IG1","categoria":"CIS-09","ig":1},
    {"id":"CIS-09.3","nombre":"Mantener y aplicar filtros de URL basados en red","descripcion":"Aplicar y actualizar el filtrado de URL basado en red para limitar que los sistemas se comuniquen con sitios web maliciosos.","dominio":"IG2","categoria":"CIS-09","ig":2},
    {"id":"CIS-09.4","nombre":"Restringir extensiones o complementos de navegadores web innecesarios","descripcion":"Restringir, a través de la configuración del dominio o el control de activos, la capacidad de los usuarios para instalar extensiones o complementos de navegador no autorizados.","dominio":"IG2","categoria":"CIS-09","ig":2},
    {"id":"CIS-09.5","nombre":"Implementar la autenticación basada en DMARC","descripcion":"Para reducir la posibilidad de correos electrónicos falsificados o modificados, implementar DMARC con política de rechazo, SPF y DKIM.","dominio":"IG2","categoria":"CIS-09","ig":2},
    {"id":"CIS-09.6","nombre":"Bloquear tipos de archivos de correo electrónico innecesarios","descripcion":"Bloquear los tipos de archivos de correo electrónico innecesarios que intenten entrar en el gateway de correo de la empresa.","dominio":"IG2","categoria":"CIS-09","ig":2},
    {"id":"CIS-09.7","nombre":"Implementar protección anti-spoofing y autenticación de remitentes de correo","descripcion":"Implementar protecciones anti-suplantación de remitentes de correo electrónico.","dominio":"IG3","categoria":"CIS-09","ig":3},

    # ── Control 10: Defensas contra Malware ──────────────────────────────────
    {"id":"CIS-10.1","nombre":"Implementar software anti-malware","descripcion":"Implementar herramientas anti-malware en todos los activos de empresa.","dominio":"IG1","categoria":"CIS-10","ig":1},
    {"id":"CIS-10.2","nombre":"Configurar actualizaciones automáticas de firmas anti-malware","descripcion":"Configurar las actualizaciones automáticas de firmas anti-malware en todos los activos de empresa.","dominio":"IG1","categoria":"CIS-10","ig":1},
    {"id":"CIS-10.3","nombre":"Deshabilitar ejecución de macro en archivos de Office","descripcion":"Deshabilitar la ejecución de macros en los archivos de Microsoft Office transmitidos por correo electrónico.","dominio":"IG1","categoria":"CIS-10","ig":1},
    {"id":"CIS-10.4","nombre":"Configurar análisis automático de medios extraíbles","descripcion":"Configurar el análisis automático de los medios extraíbles cuando se insertan.","dominio":"IG1","categoria":"CIS-10","ig":1},
    {"id":"CIS-10.5","nombre":"Habilitar características anti-exploit","descripcion":"Habilitar las características anti-exploit en los activos de empresa.","dominio":"IG2","categoria":"CIS-10","ig":2},
    {"id":"CIS-10.6","nombre":"Centralizar el monitoreo de herramientas anti-malware","descripcion":"Centralizar el monitoreo de herramientas anti-malware en todos los activos de empresa.","dominio":"IG2","categoria":"CIS-10","ig":2},
    {"id":"CIS-10.7","nombre":"Usar comportamiento basado en detección de anti-malware","descripcion":"Usar software anti-malware basado en comportamiento.","dominio":"IG3","categoria":"CIS-10","ig":3},

    # ── Control 11: Recuperación de Datos ────────────────────────────────────
    {"id":"CIS-11.1","nombre":"Establecer y mantener proceso de recuperación de datos","descripcion":"Establecer y mantener un proceso de recuperación de datos para los sistemas de empresa.","dominio":"IG1","categoria":"CIS-11","ig":1},
    {"id":"CIS-11.2","nombre":"Realizar copias de seguridad automatizadas","descripcion":"Realizar copias de seguridad automatizadas de los activos de empresa en un ámbito semanal o con mayor frecuencia.","dominio":"IG1","categoria":"CIS-11","ig":1},
    {"id":"CIS-11.3","nombre":"Proteger los datos de recuperación","descripcion":"Proteger los datos de recuperación con controles equivalentes a los del dato original.","dominio":"IG1","categoria":"CIS-11","ig":1},
    {"id":"CIS-11.4","nombre":"Establecer y mantener un procedimiento de recuperación aislado","descripcion":"Establecer y mantener un procedimiento de recuperación aislado para preservar la integridad de los datos de copia de seguridad.","dominio":"IG2","categoria":"CIS-11","ig":2},
    {"id":"CIS-11.5","nombre":"Probar datos de recuperación","descripcion":"Probar los datos de recuperación de los activos de empresa y verificar si la recuperación es exitosa.","dominio":"IG2","categoria":"CIS-11","ig":2},

    # ── Control 12: Gestión de Infraestructura de Red ─────────────────────────
    {"id":"CIS-12.1","nombre":"Garantizar que la infraestructura de red esté actualizada","descripcion":"Garantizar que la infraestructura de red esté actualizada.","dominio":"IG1","categoria":"CIS-12","ig":1},
    {"id":"CIS-12.2","nombre":"Establecer y mantener una arquitectura de red segura","descripcion":"Establecer y mantener una arquitectura de red segura documentada.","dominio":"IG2","categoria":"CIS-12","ig":2},
    {"id":"CIS-12.3","nombre":"Deshabilitar el acceso a la red de comunicación inalámbrica","descripcion":"Deshabilitar la comunicación inalámbrica punto a punto si no es compatible con la empresa.","dominio":"IG2","categoria":"CIS-12","ig":2},
    {"id":"CIS-12.4","nombre":"Establecer y mantener procesos de gestión de puntos de acceso inalámbrico","descripcion":"Establecer y mantener procesos de gestión de puntos de acceso inalámbrico.","dominio":"IG2","categoria":"CIS-12","ig":2},
    {"id":"CIS-12.5","nombre":"Centralizar el control de gestión de red","descripcion":"Centralizar el control de gestión de red.","dominio":"IG2","categoria":"CIS-12","ig":2},
    {"id":"CIS-12.6","nombre":"Usar comunicaciones de red seguras","descripcion":"Usar protocolos de comunicación de red seguros y cifrados.","dominio":"IG2","categoria":"CIS-12","ig":2},
    {"id":"CIS-12.7","nombre":"Garantizar que los dispositivos de red remotos estén conectados de forma segura","descripcion":"Requerir que los dispositivos de red remotos se conecten mediante VPN u otra solución de acceso seguro.","dominio":"IG2","categoria":"CIS-12","ig":2},
    {"id":"CIS-12.8","nombre":"Establecer y mantener infraestructura de red dedicada","descripcion":"Establecer y mantener infraestructura de red dedicada para los sistemas más confidenciales.","dominio":"IG3","categoria":"CIS-12","ig":3},

    # ── Control 13: Monitoreo y Defensa de Red ────────────────────────────────
    {"id":"CIS-13.1","nombre":"Centralizar las alertas de eventos de seguridad","descripcion":"Centralizar las alertas de eventos de seguridad y los logs de todos los activos de la empresa.","dominio":"IG2","categoria":"CIS-13","ig":2},
    {"id":"CIS-13.2","nombre":"Implementar una solución de monitoreo de seguridad basada en host","descripcion":"Implementar una solución de monitoreo de seguridad basada en host en los activos de empresa.","dominio":"IG2","categoria":"CIS-13","ig":2},
    {"id":"CIS-13.3","nombre":"Implementar una solución de filtrado de red","descripcion":"Implementar una solución de filtrado de red para gestionar las conexiones entrantes y salientes de la red.","dominio":"IG2","categoria":"CIS-13","ig":2},
    {"id":"CIS-13.4","nombre":"Realizar el filtrado de captura de paquetes de red","descripcion":"Realizar el filtrado de captura de paquetes de red para detectar actividad anormal de la red.","dominio":"IG3","categoria":"CIS-13","ig":3},
    {"id":"CIS-13.5","nombre":"Gestionar el control de acceso para los activos remotos","descripcion":"Gestionar el control de acceso de los activos que se conectan de forma remota a la red.","dominio":"IG2","categoria":"CIS-13","ig":2},
    {"id":"CIS-13.6","nombre":"Recopilar el tráfico de red y los logs de flujo","descripcion":"Recopilar el tráfico de red y los logs de flujo para detectar actividades anómalas.","dominio":"IG2","categoria":"CIS-13","ig":2},
    {"id":"CIS-13.7","nombre":"Implementar una solución de defensa contra amenazas de red basada en host","descripcion":"Implementar una solución de defensa contra amenazas de red basada en host.","dominio":"IG3","categoria":"CIS-13","ig":3},
    {"id":"CIS-13.8","nombre":"Implementar un IDS/IPS basado en red","descripcion":"Implementar un IDS/IPS basado en red para detectar y/o prevenir intentos de intrusión.","dominio":"IG3","categoria":"CIS-13","ig":3},
    {"id":"CIS-13.9","nombre":"Implementar un control de acceso a la red basado en aplicaciones","descripcion":"Implementar un control de acceso a la red basado en aplicaciones.","dominio":"IG3","categoria":"CIS-13","ig":3},
    {"id":"CIS-13.10","nombre":"Realizar pruebas de detección de intrusiones","descripcion":"Realizar pruebas de penetración e intrusión de red para validar las capacidades de detección.","dominio":"IG3","categoria":"CIS-13","ig":3},
    {"id":"CIS-13.11","nombre":"Afinar las alertas de soluciones de filtrado de red","descripcion":"Afinar las alertas de las soluciones de filtrado de red.","dominio":"IG3","categoria":"CIS-13","ig":3},

    # ── Control 14: Concientización y Capacitación ────────────────────────────
    {"id":"CIS-14.1","nombre":"Establecer y mantener un programa de concientización en seguridad","descripcion":"Establecer y mantener un programa de concientización en seguridad para todos los empleados.","dominio":"IG1","categoria":"CIS-14","ig":1},
    {"id":"CIS-14.2","nombre":"Capacitar a los empleados para reconocer ataques de ingeniería social","descripcion":"Capacitar a los empleados para reconocer los ataques de ingeniería social.","dominio":"IG1","categoria":"CIS-14","ig":1},
    {"id":"CIS-14.3","nombre":"Capacitar a los empleados sobre las mejores prácticas de autenticación","descripcion":"Capacitar a los empleados para implementar las mejores prácticas de autenticación.","dominio":"IG1","categoria":"CIS-14","ig":1},
    {"id":"CIS-14.4","nombre":"Capacitar a los empleados sobre las mejores prácticas de manejo de datos","descripcion":"Capacitar a los empleados sobre las mejores prácticas de manejo de datos para la empresa.","dominio":"IG1","categoria":"CIS-14","ig":1},
    {"id":"CIS-14.5","nombre":"Capacitar a los empleados sobre los peligros de la conexión y uso de medios extraíbles","descripcion":"Capacitar a los empleados sobre los riesgos que representan los dispositivos externos.","dominio":"IG1","categoria":"CIS-14","ig":1},
    {"id":"CIS-14.6","nombre":"Capacitar a los empleados para identificar y reportar incidentes de seguridad","descripcion":"Capacitar a los empleados para identificar y reportar correctamente los incidentes de seguridad.","dominio":"IG1","categoria":"CIS-14","ig":1},
    {"id":"CIS-14.7","nombre":"Capacitar al equipo de seguridad","descripcion":"Brindar a los empleados con roles de seguridad dedicados acceso y capacitación periódica para mantenerse al día con las amenazas.","dominio":"IG2","categoria":"CIS-14","ig":2},
    {"id":"CIS-14.8","nombre":"Capacitar a todos en las responsabilidades de funciones específicas","descripcion":"Capacitar a todos los empleados en habilidades de seguridad específicas de su función.","dominio":"IG3","categoria":"CIS-14","ig":3},
    {"id":"CIS-14.9","nombre":"Realizar simulaciones de phishing","descripcion":"Realizar simulaciones periódicas de phishing para evaluar la concientización del personal.","dominio":"IG2","categoria":"CIS-14","ig":2},

    # ── Control 15: Gestión de Proveedores de Servicios ──────────────────────
    {"id":"CIS-15.1","nombre":"Establecer y mantener un inventario de proveedores de servicios","descripcion":"Establecer y mantener un inventario de proveedores de servicios.","dominio":"IG1","categoria":"CIS-15","ig":1},
    {"id":"CIS-15.2","nombre":"Establecer y mantener una política de gestión de proveedores de servicios","descripcion":"Establecer y mantener una política de gestión de proveedores de servicios.","dominio":"IG2","categoria":"CIS-15","ig":2},
    {"id":"CIS-15.3","nombre":"Clasificar los proveedores de servicios","descripcion":"Clasificar los proveedores de servicios en función de los datos que tienen acceso.","dominio":"IG2","categoria":"CIS-15","ig":2},
    {"id":"CIS-15.4","nombre":"Garantizar que los contratos de proveedor de servicios incluyen requisitos de seguridad","descripcion":"Garantizar que los contratos de proveedor de servicios incluyan requisitos de seguridad.","dominio":"IG2","categoria":"CIS-15","ig":2},
    {"id":"CIS-15.5","nombre":"Evaluar proveedores de servicios","descripcion":"Evaluar periódicamente a los proveedores de servicios en consonancia con el proceso de gestión.","dominio":"IG3","categoria":"CIS-15","ig":3},
    {"id":"CIS-15.6","nombre":"Monitorear proveedores de servicios","descripcion":"Monitorear periódicamente a los proveedores de servicios para confirmar que están cumpliendo con sus requisitos de seguridad.","dominio":"IG3","categoria":"CIS-15","ig":3},
    {"id":"CIS-15.7","nombre":"Revocar de forma segura el acceso de los proveedores de servicios","descripcion":"Revocar el acceso de los proveedores de servicios de forma segura cuando el servicio ya no se utilice.","dominio":"IG3","categoria":"CIS-15","ig":3},

    # ── Control 16: Seguridad del Software de Aplicación ─────────────────────
    {"id":"CIS-16.1","nombre":"Establecer y mantener un proceso de evaluación de la seguridad de aplicaciones","descripcion":"Establecer y mantener un proceso de evaluación de la seguridad de aplicaciones.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.2","nombre":"Establecer y mantener un proceso de gestión del ciclo de vida del software","descripcion":"Establecer y mantener un proceso de gestión del ciclo de vida del software para abordar las vulnerabilidades de seguridad.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.3","nombre":"Realizar análisis estático del código de aplicación","descripcion":"Realizar análisis estático del código de la aplicación para identificar vulnerabilidades de seguridad.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.4","nombre":"Realizar la gestión de amenazas y vulnerabilidades de las aplicaciones web","descripcion":"Realizar revisiones de seguridad de las aplicaciones web externamente expuestas.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.5","nombre":"Usar un firewall de aplicaciones web","descripcion":"Implementar un WAF para bloquear los ataques web comunes en las aplicaciones externamente expuestas.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.6","nombre":"Establecer y mantener un proceso de evaluación de seguridad de terceros","descripcion":"Establecer y mantener un proceso de evaluación de la seguridad de los componentes de terceros de las aplicaciones.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.7","nombre":"Usar componentes de software actualizados y confiables","descripcion":"Usar solo componentes de software actualizados de fuentes confiables.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.8","nombre":"Separar los sistemas de producción y no producción","descripcion":"Mantener los entornos de desarrollo, prueba y producción separados.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.9","nombre":"Capacitar a los desarrolladores en conceptos de seguridad de aplicaciones","descripcion":"Garantizar que todos los desarrolladores de software reciban capacitación en conceptos de seguridad de aplicaciones.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.10","nombre":"Aplicar HTTPS en todos los servicios web","descripcion":"Aplicar HTTPS con certificados válidos en todos los servicios web.","dominio":"IG2","categoria":"CIS-16","ig":2},
    {"id":"CIS-16.11","nombre":"Establecer y mantener procesos de actualización de seguridad de aplicaciones","descripcion":"Establecer y mantener procesos para actualizar de forma oportuna las aplicaciones de software.","dominio":"IG3","categoria":"CIS-16","ig":3},
    {"id":"CIS-16.12","nombre":"Implementar filtros de seguridad de código en el pipeline de CI/CD","descripcion":"Implementar herramientas de seguridad en el pipeline de integración/entrega continua.","dominio":"IG3","categoria":"CIS-16","ig":3},
    {"id":"CIS-16.13","nombre":"Realizar análisis de composición de software","descripcion":"Realizar análisis de composición de software para identificar dependencias de software de riesgo.","dominio":"IG3","categoria":"CIS-16","ig":3},
    {"id":"CIS-16.14","nombre":"Realizar modelado de amenazas","descripcion":"Realizar modelado de amenazas para las aplicaciones web externamente expuestas.","dominio":"IG3","categoria":"CIS-16","ig":3},

    # ── Control 17: Gestión de Respuesta a Incidentes ─────────────────────────
    {"id":"CIS-17.1","nombre":"Establecer un programa de respuesta a incidentes","descripcion":"Establecer un programa de respuesta a incidentes, incluidos formularios de contacto de respuesta y protocolos.","dominio":"IG1","categoria":"CIS-17","ig":1},
    {"id":"CIS-17.2","nombre":"Establecer y mantener información de contacto para reportar incidentes de seguridad","descripcion":"Establecer y mantener información de contacto para reportar incidentes de seguridad.","dominio":"IG1","categoria":"CIS-17","ig":1},
    {"id":"CIS-17.3","nombre":"Establecer y mantener un proceso para reportar incidentes de seguridad internamente","descripcion":"Establecer y mantener un proceso de reporte de incidentes de seguridad internamente.","dominio":"IG1","categoria":"CIS-17","ig":1},
    {"id":"CIS-17.4","nombre":"Establecer y mantener información de contacto para reportar incidentes de seguridad externamente","descripcion":"Establecer y mantener información de contacto para reportar incidentes de seguridad externamente.","dominio":"IG2","categoria":"CIS-17","ig":2},
    {"id":"CIS-17.5","nombre":"Asignar roles de gestión de incidentes de seguridad clave","descripcion":"Asignar roles de gestión de incidentes de seguridad clave a los empleados de la empresa.","dominio":"IG2","categoria":"CIS-17","ig":2},
    {"id":"CIS-17.6","nombre":"Definir mecanismos para comunicar incidentes de seguridad","descripcion":"Determinar cuáles son los mecanismos de comunicación aceptables durante un incidente de seguridad.","dominio":"IG2","categoria":"CIS-17","ig":2},
    {"id":"CIS-17.7","nombre":"Realizar pruebas de respuesta a incidentes","descripcion":"Planificar y realizar ejercicios y simulaciones de respuesta a incidentes de seguridad.","dominio":"IG2","categoria":"CIS-17","ig":2},
    {"id":"CIS-17.8","nombre":"Conducir revisiones post-incidente","descripcion":"Conducir revisiones post-incidente para identificar oportunidades de mejora.","dominio":"IG2","categoria":"CIS-17","ig":2},
    {"id":"CIS-17.9","nombre":"Establecer y mantener procedimientos de gestión de incidentes de seguridad","descripcion":"Establecer y mantener procedimientos de gestión de incidentes de seguridad.","dominio":"IG3","categoria":"CIS-17","ig":3},

    # ── Control 18: Pruebas de Penetración ────────────────────────────────────
    {"id":"CIS-18.1","nombre":"Establecer y mantener un programa de pruebas de penetración","descripcion":"Establecer y mantener un programa de pruebas de penetración para identificar vulnerabilidades y vías de ataque.","dominio":"IG2","categoria":"CIS-18","ig":2},
    {"id":"CIS-18.2","nombre":"Realizar pruebas de penetración externas periódicas","descripcion":"Realizar pruebas de penetración externas periódicas según las necesidades organizacionales.","dominio":"IG2","categoria":"CIS-18","ig":2},
    {"id":"CIS-18.3","nombre":"Remediar las vulnerabilidades del penetration testing","descripcion":"Remediar las vulnerabilidades encontradas durante las pruebas de penetración.","dominio":"IG2","categoria":"CIS-18","ig":2},
    {"id":"CIS-18.4","nombre":"Validar medidas de seguridad","descripcion":"Validar las medidas de seguridad después de cada cambio de configuración importante.","dominio":"IG3","categoria":"CIS-18","ig":3},
    {"id":"CIS-18.5","nombre":"Realizar pruebas de penetración internas periódicas","descripcion":"Realizar pruebas de penetración internas periódicas basadas en objetivos y criterios.","dominio":"IG3","categoria":"CIS-18","ig":3},
]
