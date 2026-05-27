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
| `NIST_CSF` | NIST Cybersecurity Framework 2.0 — 106 controls |
| `SOC2` | SOC 2 Type II — 57 controls |
| `CIS` | CIS Controls v8 — 153 controls |
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
│   ├── ai_analyzer.py    # Evidence analysis via OpenAI-compatible API
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
- pip packages: `reportlab` (PDF), `openai` (optional — AI evidence analysis)

```
reportlab>=4.0
openai>=1.0       # optional
```

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

The server starts on **http://localhost:8090** by default.

To use a different port:

```bash
python run.py --port 9000
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
| `GRC_HOST` | Bind address | `localhost` |
| `GRC_SMTP_HOST` | SMTP server hostname | _(email disabled)_ |
| `GRC_SMTP_PORT` | SMTP port | `587` |
| `GRC_SMTP_USER` | SMTP username / email address | |
| `GRC_SMTP_PASS` | SMTP password or App Password | |
| `GRC_SMTP_FROM` | Sender address (defaults to USER) | |
| `GRC_OPENAI_KEY` | OpenAI API key for AI evidence analysis | _(AI disabled)_ |
| `GRC_OPENAI_BASE` | Custom OpenAI-compatible base URL | `https://api.openai.com/v1` |
| `GRC_BASE_URL` | Public URL for password reset links | `http://localhost:8090` |

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

### AI evidence analysis (optional)

```bash
export GRC_OPENAI_KEY=sk-...
# Optional: use a local model via LM Studio, Ollama, etc.
export GRC_OPENAI_BASE=http://localhost:1234/v1
```

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
| **Auditado** | Upload evidence and respond to assigned controls only |

Custom roles with granular permissions can be created from **Security → Roles & Permissions**.

---

## Data & Privacy

- All data is stored locally in a **SQLite file** (`data/evaluaciones.db`)
- No telemetry, no external services (unless you configure OpenAI or SMTP)
- Evidence files are stored locally in `data/uploads/`
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
