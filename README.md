# NormaLab GRC — Herramienta de cumplimiento de ciberseguridad de código abierto

Una plataforma de **GRC (Gobierno, Riesgo y Cumplimiento)** liviana y autoalojada para realizar análisis de brechas de ciberseguridad sobre múltiples marcos internacionales. Construida con Python y React — sin dependencias externas más allá de unos pocos paquetes de pip.

> **Idioma:** La interfaz está en español. Las contribuciones de internacionalización son bienvenidas.

---

## Funcionalidades

| Módulo | Descripción |
|---|---|
| **Análisis de brechas multi-marco** | Evaluá controles sobre ISO 27001, NIST CSF, SOC 2, CIS Controls, ISO 27701, BCRA, PCI DSS |
| **Puntuación de madurez** | Niveles de madurez 0–5 por control, con comentarios y gestión de excepciones |
| **Hallazgos y no conformidades** | Crear, asignar, aprobar y seguir hallazgos hasta su cierre |
| **Registro de riesgos** | Registro de riesgos completo con matriz de probabilidad × impacto y planes de tratamiento |
| **Tablero de remediación** | Seguimiento de tareas estilo Kanban para los planes de remediación |
| **Gestión de evidencias** | Subí archivos por control con análisis opcional asistido por IA |
| **Declaración de Aplicabilidad (SoA)** | Generá la SoA por marco |
| **Exportación de informes en PDF** | Resumen ejecutivo (2–3 páginas) e informe completo detallado |
| **Plazos y recordatorios** | Asigná fechas límite de evidencia con recordatorios por email |
| **Seguridad y RBAC** | Control de acceso basado en roles, con 4 roles de sistema + roles personalizados con permisos granulares |
| **Registro de auditoría** | Bitácora de acciones inmutable, exportable a CSV/Excel |
| **Multiusuario** | Registro, flujo de aprobación y cambio de contraseña forzado en el primer inicio de sesión |
| **Modo oscuro + temas** | Modo claro/oscuro, color de acento, ajustes de densidad |

---

## Marcos soportados

| ID | Marco |
|---|---|
| `ISO27001` | ISO/IEC 27001:2022 — 93 controles |
| `NIST_CSF` | NIST Cybersecurity Framework 2.0 — 124 controles |
| `SOC2` | SOC 2 Type II — 57 controles |
| `CIS` | CIS Controls v8 — 151 controles |
| `A7777` | BCRA Com. A 7777 — Requisitos mínimos para la gestión y control de los riesgos de TI y SI (46 controles) |
| `A7783` | BCRA Com. A 7783 — Requisitos mínimos para la gestión y control de los riesgos de TI y SI asociados a los servicios financieros digitales (9 controles) |
| `BCRA` | BCRA Com. A 7777 + A 7783 — 55 controles |
| `PCI` | PCI DSS v4.0 — 61 controles |

---

## Arquitectura

```
normalab-grc/
├── src/
│   ├── app.py            # Servidor HTTP + todos los endpoints de la API (Python puro, sin Flask)
│   ├── auth.py           # Hashing de contraseñas (PBKDF2), sesiones, registro de auditoría, tokens de reseteo
│   ├── database.py       # Esquema SQLite, migraciones, carga inicial de roles/permisos
│   ├── report.py         # Generador de informes en PDF (reportlab)
│   ├── ai_analyzer.py    # Análisis local de evidencias vía Ollama (texto + visión)
│   ├── reminders.py      # Recordatorios de plazos por email
│   └── data/
│       ├── controles_iso27001.py
│       ├── controles_nist_csf.py
│       ├── controles_soc2.py
│       ├── controles_cis.py
│       ├── controles_bcra.py
│       └── controles_pci.py
├── static/
│   ├── css/style.css     # Sistema de diseño (variables CSS, componentes)
│   └── js/
│       ├── api.js        # Wrapper de fetch para todas las llamadas a la API
│       ├── app.jsx       # App raíz de React + ruteo
│       ├── components.jsx# Componentes de UI compartidos (Modal, Badge, KPI, useApi…)
│       ├── icons.jsx     # Set de íconos Lucide
│       ├── screen-*.jsx  # Un archivo por pantalla/módulo
│       └── tweaks-panel.jsx
├── data/                 # Base de datos SQLite (se crea automáticamente, ignorada por git)
├── uploads/              # Archivos de evidencia subidos (se crea automáticamente, ignorada por git)
├── reports/              # PDFs generados (se crea automáticamente, ignorada por git)
├── requirements.txt
└── run.py                # Punto de entrada
```

**Stack:**
- **Backend:** Biblioteca estándar de Python 3.10+ (`http.server`, `sqlite3`, `hashlib`, `smtplib`) — sin framework
- **Frontend:** React 18 + Babel Standalone (transpilación de JSX en el navegador) — sin paso de build
- **Base de datos:** SQLite (basada en archivo, no necesita servidor)
- **PDF:** ReportLab
- **Gráficos:** Chart.js (incluido)

---

## Requisitos

- Python **3.10+**
- Paquetes de pip (ver `requirements.txt`):

```
reportlab>=4.0     # generación de informes en PDF
pdfplumber>=0.10   # extracción de texto de evidencias en PDF
python-docx>=1.1   # extracción de texto de evidencias en DOCX
```

- **(Opcional)** [Ollama](https://ollama.com) para el análisis local de evidencias con IA — ver [Análisis de evidencias con IA](#análisis-de-evidencias-con-ia-local-y-privado) para los modelos y el hardware mínimo.

> La app principal (Python + SQLite + React en el navegador) es extremadamente liviana y corre en casi cualquier cosa. La IA local opcional es la única parte que consume muchos recursos.

---

## Instalación

### 1. Cloná el repositorio

```bash
git clone https://github.com/facupasini7/NormaLab.git
cd NormaLab
```

### 2. Creá un entorno virtual (recomendado)

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalá las dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutá el servidor

```bash
python run.py
```

El servidor arranca en **http://localhost:8090** por defecto y escucha en todas las interfaces (`0.0.0.0`).

Para usar otro puerto o dirección de escucha:

```bash
python run.py --port 9000          # vía flag de CLI
GRC_PORT=9000 python run.py        # vía variable de entorno
GRC_HOST=127.0.0.1 python run.py   # restringir solo a localhost
```

### 5. Primer inicio de sesión

| Campo | Valor |
|---|---|
| Usuario | `admin` |
| Contraseña | `Admin1234!` |

> **Se te forzará a cambiar la contraseña en el primer inicio de sesión.** No te saltees este paso antes de poner la herramienta en producción.

---

## Configuración

### Variables de entorno

Toda la configuración se hace mediante variables de entorno (no se necesita archivo de configuración):

| Variable | Descripción | Por defecto |
|---|---|---|
| `GRC_PORT` | Puerto del servidor HTTP | `8090` |
| `GRC_HOST` | Dirección de escucha (`0.0.0.0` = todas las interfaces) | `0.0.0.0` |
| `GRC_SMTP_HOST` | Hostname del servidor SMTP | _(email deshabilitado)_ |
| `GRC_SMTP_PORT` | Puerto SMTP | `587` |
| `GRC_SMTP_USER` | Usuario SMTP / dirección de email | |
| `GRC_SMTP_PASS` | Contraseña SMTP o contraseña de aplicación | |
| `GRC_SMTP_FROM` | Dirección del remitente (por defecto, la de USER) | |
| `GRC_BASE_URL` | URL pública para los enlaces de reseteo de contraseña | `http://localhost:8090` |

> El análisis de evidencias con IA se configura instalando **Ollama** localmente — no hay claves de API ni variables de entorno para eso. Ver [Análisis de evidencias con IA](#análisis-de-evidencias-con-ia-local-y-privado).

### Configuración de email (se recomienda Gmail)

1. Activá la **verificación en 2 pasos** en tu cuenta de Google
2. Andá a **Cuenta de Google → Seguridad → Contraseñas de aplicaciones**
3. Creá una contraseña de aplicación para "Correo"
4. Definí las variables de entorno:

```bash
export GRC_SMTP_HOST=smtp.gmail.com
export GRC_SMTP_PORT=587
export GRC_SMTP_USER=tu@gmail.com
export GRC_SMTP_PASS=xxxx-xxxx-xxxx-xxxx   # Contraseña de aplicación
```

---

## Análisis de evidencias con IA (local y privado)

El análisis de evidencias es **opcional** y corre íntegramente en una **instancia local de [Ollama](https://ollama.com)** — ningún dato sale de tu máquina, sin claves de API, sin proveedor en la nube. Si Ollama no está instalado o no está corriendo, el resto de la app funciona con normalidad y los análisis simplemente se reportan como *pendientes*.

### Cómo funciona

Cuando se sube una evidencia a un control, `src/ai_analyzer.py` la enruta según su tipo:

| Tipo de evidencia | Procesamiento | Modelo usado |
|---|---|---|
| PDF, DOCX, TXT, CSV, JSON, XML | Se extrae el texto (pdfplumber / python-docx) | **modelo de texto** |
| PNG, JPG, JPEG, WEBP, GIF, BMP | La imagen se envía directamente (base64) | **modelo de visión** |

El mejor modelo instalado se selecciona automáticamente por orden de preferencia. Un **system prompt consciente del marco** inyecta orientación experta para el estándar correspondiente (ISO 27001, NIST CSF, PCI DSS, BCRA, SOC 2, CIS), de modo que el veredicto, la puntuación de madurez y el hallazgo sugerido sigan los criterios de cada marco. El modelo devuelve un JSON estructurado: `veredicto`, `madurez_sugerida` (0–5), `fortalezas`, `brechas`, `recomendacion` y un `hallazgo_sugerido` opcional.

### Modelos usados (por defecto)

| Capacidad | Modelo por defecto | Alternativas automáticas |
|---|---|---|
| Documentos de texto | `llama3.1:8b` | `qwen2.5:14b` → `qwen2.5:7b` → `qwen2.5:3b` |
| Imágenes / capturas de pantalla | `minicpm-v` | `llama3.2-vision:11b` |

```bash
# 1. Instalá Ollama: https://ollama.com
# 2. Descargá los modelos
ollama pull llama3.1:8b    # análisis de texto/documentos
ollama pull minicpm-v      # análisis de imágenes / capturas (visión)
```

Para un razonamiento de mayor calidad sobre documentos, `ollama pull qwen2.5:14b` — el analizador lo prefiere automáticamente cuando está presente.

### Hardware mínimo

Solo el análisis con IA consume muchos recursos; todo lo demás corre con hardware mínimo.

| Componente | App principal (sin IA) | Con IA local (configuración de referencia) |
|---|---|---|
| CPU | cualquier x64 | cualquier x64 moderno |
| RAM | ~1 GB | **16 GB** |
| GPU | ninguna | NVIDIA **4 GB de VRAM** (ej. GTX 1050 Ti) — opcional |
| Disco | ~50 MB | + ~6–10 GB para los modelos |

Máquina de referencia validada: **16 GB de RAM + NVIDIA GTX 1050 Ti (4 GB de VRAM)**. En esa GPU, el primer análisis de imagen tarda ~50–60 s (el modelo de visión se carga en parte en la RAM del sistema); los análisis siguientes son más rápidos mientras el modelo permanece residente (`keep_alive`). Una GPU **no es obligatoria** — sin ella, el análisis de texto igual funciona en CPU (más lento) y el modelo de visión se puede omitir.

---

## Ejecutar como servicio

### Linux (systemd)

Creá `/etc/systemd/system/normalab-grc.service`:

```ini
[Unit]
Description=NormaLab GRC Tool
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/normalab
ExecStart=/opt/normalab/venv/bin/python run.py
Restart=on-failure
Environment=GRC_HOST=0.0.0.0
Environment=GRC_PORT=8090
Environment=GRC_SMTP_HOST=smtp.gmail.com
Environment=GRC_SMTP_USER=your@gmail.com
Environment=GRC_SMTP_PASS=your-app-password

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable normalab-grc
sudo systemctl start normalab-grc
```

### Windows (ejecutar al inicio)

Agregá `run.py` al Programador de tareas o creá un archivo `.bat`:

```bat
@echo off
cd C:\NormaLab
venv\Scripts\python.exe run.py
```

### Docker (comunidad)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8090
CMD ["python", "run.py"]
```

```bash
docker build -t normalab-grc .
docker run -p 8090:8090 -v $(pwd)/data:/app/data normalab-grc
```

---

## Roles y permisos

| Rol | Descripción |
|---|---|
| **Administrador** | Acceso total — usuarios, roles, configuración, todos los módulos |
| **Analista GRC** | Gestiona evaluaciones, hallazgos, riesgos e informes |
| **Auditor Externo** | Acceso de solo lectura + registro de auditoría |
| **Auditado** | Sube evidencias y responde a los controles asignados; ve únicamente sus propios hallazgos asignados (comentar, adjuntar evidencia, marcar como *Implementado*) |

Se pueden crear roles personalizados con permisos granulares desde **Seguridad → Roles y permisos**.

---

## Datos y privacidad

- Todos los datos se almacenan localmente en un **archivo SQLite** (`data/evaluaciones.db`)
- Sin telemetría, sin servicios externos (a menos que configures Ollama o SMTP)
- Los archivos de evidencia se almacenan localmente en `uploads/`
- Los PDFs generados, en `reports/`

---

## Cómo contribuir

Los pull requests son bienvenidos. Para cambios importantes, abrí primero un issue para discutir qué te gustaría cambiar.

### Agregar un nuevo marco

1. Creá `src/data/controles_<framework_id>.py` siguiendo la estructura existente
2. Registralo en el diccionario `FRAMEWORK_REGISTRY` en `src/app.py`
3. Agregá la etiqueta del marco en `src/report.py` (`FRAMEWORK_LABELS`)
4. Ejecutá `seed_controles_db()` (se llama automáticamente al iniciar)

---

## Licencia

Licencia MIT — ver [LICENSE](LICENSE) para más detalles.

---

## Capturas de pantalla

> _Próximamente — ¡las contribuciones son bienvenidas!_

---

<div align="center">
  <sub>Construido con Python + React · Sin paso de build · Corre donde corra Python</sub>
</div>
