# FairProbe

> Fix harmful bias before AI systems impact real people.

FairProbe is an open source AI bias auditing platform that wraps any AI decision system as middleware, silently logs every decision, calculates discrimination statistics in real time, and generates compliance reports on demand.

Most auditing tools investigate bias after the fact — once a year, after thousands of people have already been harmed. FairProbe catches it before it scales.

Built for the GDG PromptWars 2026 National Hackathon.

---
**Status:** Backend complete · Frontend in development · Deadline April 15 2026

## The Problem

Companies use AI to filter job applications, approve loans, and make medical decisions. These systems often discriminate silently — rejecting Mohammed Hassan and accepting James Smith with identical qualifications, purely based on name or ethnicity. Nobody notices because it happens automatically, at scale, with no paper trail.

**FairProbe makes the invisible visible.**

---

## What It Does
Company's AI makes decisions
↓
FairProbe middleware watches silently
↓
Every decision logged to database
↓
FastAPI calculates acceptance rates
grouped by ethnicity, age, name origin
↓
Dashboard shows discrimination statistics
↓
Groq/Gemini interprets findings on demand
↓
Formal compliance report generated

---

## Demo Results

In our hiring AI demo, FairProbe detected:

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
| AI — Development | Groq `llama-3.3-70b-versatile` |
| AI — Demo Day | Gemini 2.5 Flash |
| Frontend | React + Tailwind CSS |
| Config | `fairprobe.config.yaml` |
| Hosting | Railway (backend) + Firebase Hosting (frontend) |

---

## Project Structure
fairprobe/
├── backend/
│   ├── main.py              → FastAPI app, startup, routing
│   ├── config.py            → reads fairprobe.config.yaml
│   ├── demo_ai.py           → fake biased hiring AI for demo
│   ├── stats.py             → calculates acceptance rates
│   ├── gemini.py            → all Groq/Gemini API calls
│   ├── database.py          → database connection + adapter selector
│   ├── adapters/
│   │   ├── sqlite.py        → SQLite implementation
│   │   └── firebase.py      → Firebase implementation
│   └── routers/
│       ├── audit.py         → /audit endpoints
│       ├── stats.py         → /stats endpoints
│       └── actions.py       → /action endpoints (Groq calls)
├── frontend/                → React app
├── fairprobe.config.yaml    → company customization file
├── .env                     → API keys (never committed)
└── README.md

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Assassin61/Fairprobe.git
cd Fairprobe
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn python-dotenv pyyaml httpx groq firebase-admin
```

### 3. Set up your API keys

Create a `.env` file in the project root:
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here

Get your keys:
- Groq (free): https://console.groq.com/keys
- Gemini (free): https://aistudio.google.com/app/apikey

### 4. Start the server

```bash
uvicorn backend.main:app --reload
```

### 5. Open API docs
http://127.0.0.1:8000/docs

---

## Running the Demo

1. Hit `POST /audit/run` — generates 200 candidates, runs them through the biased hiring AI, logs everything to SQLite
2. Hit `GET /audit/latest` — get your audit ID
3. Hit `GET /audit/{id}/stats` — see the discrimination statistics
4. Hit `POST /action/analyse/{id}` — Groq interprets the bias findings
5. Hit `POST /action/report/{id}` — generates a formal compliance report
6. Hit `POST /action/summarize/{id}` — plain English summary for executives

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/audit/run` | Run a new audit |
| `GET` | `/audit/latest` | Get most recent audit ID |
| `GET` | `/audit/{id}/stats` | Bias stats for a specific audit |
| `GET` | `/audit/{id}/applications` | All applications for an audit |
| `GET` | `/audit/all/stats` | Cumulative stats across all audits |
| `POST` | `/action/analyse/{id}` | Groq interprets bias findings |
| `POST` | `/action/report/{id}` | Generate formal compliance report |
| `POST` | `/action/summarize/{id}` | Plain English executive summary |

---

## Configuration

FairProbe is fully config-driven. Edit `fairprobe.config.yaml` to adapt it to any company or domain — no code changes needed.

```yaml
company: "Your Company"
domain: "employment"         # employment, banking, healthcare

database:
  type: "sqlite"             # switch to "firebase" for production
  path: "./fairprobe.db"

ai:
  provider: "groq"           # switch to "gemini" for demo day
  model: "llama-3.3-70b-versatile"

thresholds:
  high_bias: 30              # flag if acceptance gap exceeds 30%
  medium_bias: 15
```

---

## Switching to Gemini for Demo Day

In `fairprobe.config.yaml`, change:

```yaml
ai:
  provider: "gemini"
  model: "gemini-2.5-flash"
```

No other changes needed. The `gemini.py` module handles both providers.

---

## Key Design Decisions

- **FastAPI calculates all statistics** — Groq only interprets pre-calculated results, never raw data
- **Candidate cache is permanent** — `demo_candidates.json` is never deleted, accumulating believable data across runs
- **Config-driven** — no hardcoding anywhere, one YAML file adapts FairProbe to any company
- **Adapter pattern** — swap SQLite for Firebase by changing one line in config
- **On-demand AI calls only** — Groq is called maximum 3 times per demo to conserve credits

---
### Done
- [x] FastAPI backend with all endpoints
- [x] Config-driven architecture
- [x] Demo hiring AI with hidden bias
- [x] Groq candidate generation (cached)
- [x] SQLite database with full audit logging
- [x] Bias statistics calculation
- [x] Groq/Gemini integration (analyse, report, summarize)
- [x] Adapter pattern (SQLite → Firebase swap)

### In Progress
- [ ] React frontend (5 pages)
- [ ] Firebase Firestore integration
- [ ] Railway deployment (backend)
- [ ] Firebase Hosting deployment (frontend)


## License

MIT License — free to use, modify, and distribute.

---

Built with by Team Assassin61 · GDG PromptWars 2026
Now save this as README.md in your project root and push:
powershellgit add README.md
git commit -m "docs: add README"
git push origin mainBut I still have to integrate the front end. So it's not totally ready. I'm going with the design you gave earlier7:34 AMAdd a status badge at the top so judges know it's in progress, and a roadmap section so it looks intentional, not incomplete.
Add this right after the first tagline in the README, before "The Problem":
markdown> **Status:** Backend complete · Frontend in development · Deadline April 15 2026

---
And add this section before the License:
markdown## Roadmap

