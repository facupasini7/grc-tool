# NormaLab GRC — Open Source Cybersecurity Compliance Tool

A lightweight, self-hosted **GRC (Governance, Risk & Compliance)** platform for performing cybersecurity gap analyses across multiple international frameworks. Built with Python and React — no external dependencies beyond a few pip packages.

> **Language:** The UI is in Spanish. Internationalization contributions are welcome.

---

## Features

| Module | Description |
|---|---|
| **Multi-framework gap analysis** | Evaluate controls across ISO 27001, NIST CSF, SOC 2, CIS Controls, ISO 27701, BCRA, PCI DSS |
| **Maturity scoring** | 0–5 maturity levels per control with comments and exception management |
| **Findings & non-conformities** | Create, assign, approve and track findings to closure |
| **Risk register** | Full risk register with probability × impact matrix and treatment plans |
| **Remediation board** | Kanban-style task tracking for remediation plans |
| **Evidence management** | Upload files per control with optional AI-powered analysis |
| **Statement of Applicability (SoA)** | Generate SoA per framework |
| **PDF report export** | Executive summary (2–3 pages) and detailed full report |
| **Deadlines & reminders** | Assign evidence deadlines with email reminders |
| **Security & RBAC** | Role-based access control with 4 system roles + custom roles with granular permissions |
| **Audit log** | Immutable action log, exportable to CSV/Excel |
| **Multi-user** | Registration, approval workflow, forced password change on first login |
| **Dark mode + themes** | Light/dark mode, accent color, density tweaks |

---

## Supported Frameworks

| ID | Framework |
|---|---|
| `ISO27001` | ISO/IEC 27001:2022 — 93 controls |
| `NIST_CSF` | NIST Cybersecurity Framework 2.0 — 124 controls |
| `SOC2` | SOC 2 Type II — 57 controls |
| `CIS` | CIS Controls v8 — 151 controls |
| `A7777` | BCRA Com. A 7777 — Requisitos mínimos para la gestión y control de los riesgos de TI y SI (46 controles) |
| `A7783` | BCRA Com. A 7783 — Requisitos mínimos para la gestión y control de los riesgos de TI y SI asociados a los servicios financieros digitales (9 controles) |
| `BCRA` | BCRA Com. A 7777 + A 7783 — 55 controles |
| `PCI` | PCI DSS v4.0 — 61 controls |

---

## Architecture

```
normalab-grc/
├── src/
│   ├── app.py            # HTTP server + all API endpoints (pure Python, no Flask)
│   ├── auth.py           # Password hashing (PBKDF2), sessions, audit log, reset tokens
│   ├── database.py       # SQLite schema, migrations, role/permission seeding
│   ├── report.py         # PDF report generator (reportlab)
│   ├── ai_analyzer.py    # Local evidence analysis via Ollama (text + vision)
│   ├── reminders.py      # Email deadline reminders
│   └── data/
│       ├── controles_iso27001.py
│       ├── controles_nist_csf.py
│       ├── controles_soc2.py
│       ├── controles_cis.py
│       ├── controles_bcra.py
│       └── controles_pci.py
├── static/
│   ├── css/style.css     # Design system (CSS variables, components)
│   └── js/
│       ├── api.js        # Fetch wrapper for all API calls
│       ├── app.jsx       # Root React app + routing
│       ├── components.jsx# Shared UI components (Modal, Badge, KPI, useApi…)
│       ├── icons.jsx     # Lucide icon set
│       ├── screen-*.jsx  # One file per screen/module
│       └── tweaks-panel.jsx
├── data/                 # SQLite database (auto-created, gitignored)
├── uploads/              # Uploaded evidence files (auto-created, gitignored)
├── reports/              # Generated PDFs (auto-created, gitignored)
├── requirements.txt
└── run.py                # Entry point
```

**Stack:**
- **Backend:** Python 3.10+ standard library (`http.server`, `sqlite3`, `hashlib`, `smtplib`) — zero framework
- **Frontend:** React 18 + Babel Standalone (in-browser JSX transpilation) — zero build step
- **Database:** SQLite (file-based, no server needed)
- **PDF:** ReportLab
- **Charts:** Chart.js (bundled)

---

## Requirements

- Python **3.10+**
- pip packages (see `requirements.txt`):

```
reportlab>=4.0     # PDF report generation
pdfplumber>=0.10   # text extraction from PDF evidence
python-docx>=1.1   # text extraction from DOCX evidence
```

- **(Optional)** [Ollama](https://ollama.com) for local AI evidence analysis — see [AI Evidence Analysis](#ai-evidence-analysis-local--private) for models and minimum hardware.

> The core app (Python + SQLite + in-browser React) is extremely light and runs on almost anything. The optional local AI is the only resource-intensive part.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/facupasini7/grc-tool.git
cd grc-tool
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
python run.py
```

The server starts on **http://localhost:8090** by default and binds to all interfaces (`0.0.0.0`).

To use a different port or bind address:

```bash
python run.py --port 9000          # via CLI flag
GRC_PORT=9000 python run.py        # via env var
GRC_HOST=127.0.0.1 python run.py   # restrict to localhost only
```

### 5. First login

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `Admin1234!` |

> **You will be forced to change the password on first login.** Do not skip this step before deploying.

---

## Configuration

### Environment variables

All configuration is done via environment variables (no config file needed):

| Variable | Description | Default |
|---|---|---|
| `GRC_PORT` | HTTP server port | `8090` |
| `GRC_HOST` | Bind address (`0.0.0.0` = all interfaces) | `0.0.0.0` |
| `GRC_SMTP_HOST` | SMTP server hostname | _(email disabled)_ |
| `GRC_SMTP_PORT` | SMTP port | `587` |
| `GRC_SMTP_USER` | SMTP username / email address | |
| `GRC_SMTP_PASS` | SMTP password or App Password | |
| `GRC_SMTP_FROM` | Sender address (defaults to USER) | |
| `GRC_BASE_URL` | Public URL for password reset links | `http://localhost:8090` |

> AI evidence analysis is configured by installing **Ollama** locally — there are no API keys or env vars for it. See [AI Evidence Analysis](#ai-evidence-analysis-local--private).

### Email setup (Gmail recommended)

1. Enable **2-Step Verification** on your Google account
2. Go to **Google Account → Security → App Passwords**
3. Create an App Password for "Mail"
4. Set environment variables:

```bash
export GRC_SMTP_HOST=smtp.gmail.com
export GRC_SMTP_PORT=587
export GRC_SMTP_USER=your@gmail.com
export GRC_SMTP_PASS=xxxx-xxxx-xxxx-xxxx   # App Password
```

---

## AI Evidence Analysis (local & private)

Evidence analysis is **optional** and runs entirely on a **local [Ollama](https://ollama.com) instance** — no data ever leaves your machine, no API keys, no cloud provider. If Ollama is not installed or not running, the rest of the app works normally and analyses are simply reported as *pending*.

### How it works

When evidence is uploaded to a control, `src/ai_analyzer.py` routes it by type:

| Evidence type | Processing | Model used |
|---|---|---|
| PDF, DOCX, TXT, CSV, JSON, XML | Text extracted (pdfplumber / python-docx) | **text model** |
| PNG, JPG, JPEG, WEBP, GIF, BMP | Image sent directly (base64) | **vision model** |

The best installed model is selected automatically by order of preference. A **framework-aware system prompt** injects expert guidance for the relevant standard (ISO 27001, NIST CSF, PCI DSS, BCRA, SOC 2, CIS), so the verdict, maturity score and suggested finding follow each framework's criteria. The model returns structured JSON: `veredicto`, `madurez_sugerida` (0–5), `fortalezas`, `brechas`, `recomendacion` and an optional `hallazgo_sugerido`.

### Models used (defaults)

| Capability | Default model | Automatic fallbacks |
|---|---|---|
| Text documents | `llama3.1:8b` | `qwen2.5:14b` → `qwen2.5:7b` → `qwen2.5:3b` |
| Images / screenshots | `minicpm-v` | `llama3.2-vision:11b` |

```bash
# 1. Install Ollama: https://ollama.com
# 2. Pull the models
ollama pull llama3.1:8b    # text/document analysis
ollama pull minicpm-v      # image / screenshot analysis (vision)
```

For higher-quality reasoning on documents, `ollama pull qwen2.5:14b` — the analyzer prefers it automatically when present.

### Minimum hardware

Only the AI analysis is resource-intensive; everything else runs on minimal hardware.

| Component | Core app (no AI) | With local AI (reference setup) |
|---|---|---|
| CPU | any x64 | any modern x64 |
| RAM | ~1 GB | **16 GB** |
| GPU | none | NVIDIA **4 GB VRAM** (e.g. GTX 1050 Ti) — optional |
| Disk | ~50 MB | + ~6–10 GB for the models |

Validated reference machine: **16 GB RAM + NVIDIA GTX 1050 Ti (4 GB VRAM)**. On that GPU the first image analysis takes ~50–60 s (the vision model loads partly into system RAM); subsequent analyses are faster while the model stays resident (`keep_alive`). A GPU is **not required** — without one, text analysis still works on CPU (slower) and the vision model can be skipped.

---

## Running as a service

### Linux (systemd)

Create `/etc/systemd/system/normalab-grc.service`:

```ini
[Unit]
Description=NormaLab GRC Tool
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/grc-tool
ExecStart=/opt/grc-tool/venv/bin/python run.py
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

### Windows (run at startup)

Add `run.py` to Task Scheduler or create a `.bat` file:

```bat
@echo off
cd C:\grc-tool
venv\Scripts\python.exe run.py
```

### Docker (community)

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

## Roles & Permissions

| Role | Description |
|---|---|
| **Administrador** | Full access — users, roles, config, all modules |
| **Analista GRC** | Manage evaluations, findings, risks, reports |
| **Auditor Externo** | Read-only access + audit log |
| **Auditado** | Upload evidence and respond to assigned controls; sees only their own assigned findings (comment, attach evidence, mark as *Implementado*) |

Custom roles with granular permissions can be created from **Security → Roles & Permissions**.

---

## Data & Privacy

- All data is stored locally in a **SQLite file** (`data/evaluaciones.db`)
- No telemetry, no external services (unless you configure OpenAI or SMTP)
- Evidence files are stored locally in `uploads/`
- Generated PDFs in `reports/`

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you would like to change.

### Adding a new framework

1. Create `src/data/controles_<framework_id>.py` following the existing structure
2. Register it in the `FRAMEWORK_REGISTRY` dict in `src/app.py`
3. Add the framework label in `src/report.py` (`FRAMEWORK_LABELS`)
4. Run `seed_controles_db()` (called automatically on startup)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Screenshots

> _Coming soon — contributions welcome!_

---

<div align="center">
  <sub>Built with Python + React · No build step · Runs anywhere Python runs</sub>
</div>
