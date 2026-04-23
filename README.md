# EquiDex

> Fix harmful bias before AI systems impact real people.

EquiDex is an open source AI bias auditing platform that wraps any AI decision system as middleware, silently logs every decision, calculates discrimination statistics in real time, and generates compliance reports on demand.

Most auditing tools investigate bias after the fact — once a year, after thousands of people have already been harmed. EquiDex catches it before it scales.

Built for the GDG PromptWars 2026 National Hackathon.

---
**Status:** Fully functional · Backend + Frontend complete

## The Problem

Companies use AI to filter job applications, approve loans, and make medical decisions. These systems often discriminate silently — rejecting Mohammed Hassan and accepting James Smith with identical qualifications, purely based on name or ethnicity. Nobody notices because it happens automatically, at scale, with no paper trail.

**EquiDex makes the invisible visible.**

---

## What It Does

```
Company's AI makes decisions
↓
EquiDex middleware watches silently
↓
Every decision logged to database
↓
FastAPI calculates acceptance rates
grouped by ethnicity, age, name origin
↓
Dashboard shows discrimination statistics
with professional interactive charts
↓
Gemini AI interprets findings on demand
↓
Formal compliance report generated
```

---

## Demo Results

In our hiring AI demo, EquiDex detected:

| Group | Acceptance Rate |
|---|---|
| Caucasian | 100% |
| East Asian | 100% |
| Hispanic | 25% |
| South Asian | 21.9% |
| African American | 21.9% |
| Middle Eastern | 20.8% |

**Caucasian candidates are accepted 4.8× more often than Middle Eastern candidates with identical qualifications.**

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Python 3.13 |
| Database | SQLite (dev) / Firebase Firestore (prod) |
| AI | Gemini 2.5 Flash |
| Frontend | Vanilla JS + Chart.js 4.x |
| Config | `fairprobe.config.yaml` |
| Frontend Hosting | Firebase Hosting / Vercel |
| Backend Hosting | Google Cloud Run |

---

## Dashboard Features

The EquiDex dashboard provides **6 professional interactive charts**:

| Chart | Type | Purpose |
|---|---|---|
| Overall Acceptance Rate | Doughnut with center % | Quick glance at accept/reject ratio |
| Acceptance Rate by Group | Horizontal Bar | Color-coded by severity per demographic group |
| Applications Received | Vertical Bar | Volume distribution with distinct palette |
| Accepted vs Rejected | Stacked Bar | Breakdown showing where rejections cluster |
| Acceptance Rate Over Time | Area Line | Trend monitoring across audit dates |
| Bias Disparity by Dimension | Polar Area | Severity-coded disparity across all dimensions |

All charts update dynamically when switching between dimension tabs (name origin, age group, ethnicity).

---

## Project Structure

```
equidex/
├── backend/
│   ├── main.py              → FastAPI app, startup, routing
│   ├── config.py            → reads fairprobe.config.yaml
│   ├── demo_ai.py           → fake biased hiring AI for demo
│   ├── stats.py             → calculates acceptance rates
│   ├── gemini.py            → all Gemini API calls
│   ├── adapters/
│   │   ├── sqlite.py        → SQLite implementation
│   │   └── firebase.py      → Firebase Firestore implementation
│   └── routers/
│       ├── audit.py         → /audit endpoints
│       ├── stats.py         → /stats endpoints
│       ├── actions.py       → /action endpoints (AI calls)
│       └── config_router.py → /config endpoints
├── frontend/
│   ├── index.html           → Dashboard with 6 charts
│   ├── audit.html           → Run demo / upload dataset
│   ├── history.html         → Browse past audits
│   ├── report.html          → AI-generated reports
│   ├── settings.html        → Configuration UI
│   ├── css/style.css        → EquiDex design system
│   └── js/
│       ├── config.js        → API base URL configuration
│       ├── api.js           → API client + shared helpers
│       ├── charts.js        → Chart.js chart definitions
│       ├── dashboard.js     → Dashboard page logic
│       ├── audit.js         → Audit page logic
│       ├── history.js       → History page logic
│       ├── report.js        → Report page logic
│       └── settings.js      → Settings page logic
├── fairprobe.config.yaml    → Company customization file
├── vercel.json              → Vercel deployment config
├── firebase.json            → Firebase Hosting config
├── Dockerfile               → Container for Cloud Run
├── .env                     → API keys (never committed)
├── DEPLOYMENT.md            → Full deployment guide
└── README.md
```

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Assassin61/Fairprobe.git
cd Fairprobe
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your API keys

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_gemini_key_here
```

Get your key: [Google AI Studio](https://aistudio.google.com/app/apikey) (free)

### 4. Start the backend

```bash
uvicorn backend.main:app --reload
```

### 5. Start the frontend

```bash
python -m http.server 3000 --directory frontend
```

### 6. Open the dashboard

Navigate to [http://127.0.0.1:3000](http://127.0.0.1:3000)

---

## Running the Demo

1. Open the dashboard at `http://127.0.0.1:3000`
2. Click **Run / Upload** in the sidebar
3. Click **Run Demo Audit** — generates 500 candidates through a biased hiring AI
4. Return to the **Dashboard** — all 6 charts populate automatically
5. Switch between dimension tabs (name origin, age group, ethnicity)
6. Use the **Latest Audit** action cards:
   - **Analyse Bias** — Gemini interprets the discrimination patterns
   - **Generate Report** — formal compliance report with legal references
   - **Summarize** — plain English executive summary

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/audit/run` | Run a new demo audit |
| `POST` | `/audit/upload` | Upload a custom dataset |
| `GET` | `/audit/latest` | Get most recent audit ID |
| `GET` | `/audit/{id}/stats` | Bias stats for a specific audit |
| `GET` | `/audit/{id}/applications` | All applications for an audit |
| `GET` | `/audit/all/stats` | Cumulative stats across all audits |
| `GET` | `/audit/all/applications` | All applications across all audits |
| `POST` | `/action/analyse/{id}` | Gemini interprets bias findings |
| `POST` | `/action/report/{id}` | Generate formal compliance report |
| `POST` | `/action/summarize/{id}` | Plain English executive summary |

---

## Configuration

EquiDex is fully config-driven. Edit `fairprobe.config.yaml` to adapt it to any company or domain — no code changes needed.

```yaml
company: "Your Company"
domain: "employment"         # employment, banking, healthcare

database:
  type: "sqlite"             # switch to "firebase" for production
  path: "./fairprobe.db"

ai:
  provider: "gemini"
  model: "gemini-2.5-flash"

thresholds:
  high_bias: 30              # flag if acceptance gap exceeds 30%
  medium_bias: 15
```

---

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions covering:
- **Firebase Firestore** — production database
- **Google Cloud Run** — backend API hosting
- **Firebase Hosting** — frontend hosting (primary)
- **Vercel** — frontend hosting (alternative)

Both Firebase Hosting and Vercel provide automatic TLS/HTTPS. Cloud Run also serves over HTTPS by default. No manual certificate configuration needed for production.

---

## Key Design Decisions

- **FastAPI calculates all statistics** — Gemini only interprets pre-calculated results, never raw data
- **Candidate cache is permanent** — `demo_candidates.json` accumulates believable data across runs
- **Config-driven** — no hardcoding anywhere, one YAML file adapts EquiDex to any company
- **Adapter pattern** — swap SQLite for Firebase by changing one line in config
- **On-demand AI calls only** — Gemini is called max 3 times per demo to conserve credits
- **6 professional charts** — doughnut, horizontal bar, vertical bar, stacked bar, line, polar area

---

### Complete ✓
- [x] FastAPI backend with all endpoints
- [x] Config-driven architecture
- [x] Demo hiring AI with hidden bias
- [x] Candidate generation (cached)
- [x] SQLite database with full audit logging
- [x] Bias statistics calculation
- [x] Gemini integration (analyse, report, summarize)
- [x] Adapter pattern (SQLite → Firebase swap)
- [x] Frontend with 5 pages and 6 interactive charts
- [x] Firebase Hosting configuration
- [x] Vercel deployment configuration
- [x] Deployment guide (DEPLOYMENT.md)

## License

MIT License — free to use, modify, and distribute.

---

Built by Team Visionaries · GDG PromptWars 2026
