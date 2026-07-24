# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

CardLearn SDGs (SDGsprogram_5.0) — SDGs Pecha Kucha card-matching English learning platform. Students select an SDG topic and CEFR difficulty, play a card-matching game, then review a script, record audio, and answer cloze questions. Teachers/admins maintain the question bank and view records.

For full architecture detail (data model, API surface, sequence diagrams, page flow), read `SYSTEM_ARCHITECTURE.md` first — it is comprehensive and current. `README.md` (Traditional Chinese) and `AGENTS.md` cover setup/build commands.

## Commands

Local backend:
```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend build (`frontend/` → `dist/` + `dist/static/`, generates `config.js` from `API_BASE_URL`/`VITE_API_BASE_URL`):
```bash
npm run build
```

Verification (there is no automated test suite — these are the only checks):
```bash
python -m py_compile backend/main.py backend/rate_limit.py scripts/test_rate_limits.py
python scripts/test_rate_limits.py   # Redis rate-limit self-test, needs REDIS_URL
npm run build                         # frontend build check
```

Setup:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Architecture

- **Backend**: single-file FastAPI app `backend/main.py` (~2500 lines) — routes, DB init, auth, teacher tools all live here. Rate limiting is factored out into `backend/rate_limit.py` (Redis-backed, only active when `REDIS_URL` + `RATE_LIMIT_ENABLED` are set).
- Backend initializes the DB at **import time**: loads `.env` → configures CORS/JWT/rate-limit/email → picks SQLite (`sql/app.db`, default) or PostgreSQL (when `DATABASE_URL` is set, via `psycopg`) → runs `init_db()` to create/patch tables and seed SDG/difficulty/part rows → mounts static frontend → registers routes → optionally creates an initial admin from `INITIAL_ADMIN_*` env vars.
- API groups: `/auth`, `/content`, `/game`, `/teacher`, `/health`. Auth is JWT bearer; `require_teacher()` gates teacher/admin routes; admin-only checks apply when changing/deleting admin accounts.
- **Frontend**: static HTML/CSS/JS, no framework/bundler. Pages in `frontend/pages/`, all API calls centralized in `frontend/js/api.js`. Runtime API base URL comes from `window.CARDLEARN_API_BASE_URL` (set by `frontend/config.js` locally, generated into `dist/` on build).
- `dist/` is **generated only** — always edit source under `frontend/`, then rebuild. Never hand-edit `dist/`.
- Data model core chain: `SDG_OPTIONS → TBL_SDG_PARTS → TBL_SDG_SUB_TOPICS → TBL_SDG_CARDS` (cards also keyed by `difficulty_code`), plus `USERS → GAME_SESSIONS → GAME_PART_RECORDS`. Current difficulty vocabulary: `A1`, `A2`, `B1`.
- Teacher Excel/JSON import is **upsert-based** (re-uploading updates matching rows, not duplicates); parser uses `openpyxl` when available, else a stdlib `.xlsx` XML fallback.
- Deployment: Railway runs the FastAPI backend; Vercel serves the built `dist/` static frontend, pointed at the Railway backend via `API_BASE_URL`. See `DEPLOYMENT.md`.

## Working rules

- Do not commit or expose real values from `.env`; use `.env.example` for documented configuration.
- Preserve existing data in `sql/app.db` unless a task explicitly asks for migration or reset work.
- Edit `frontend/` source, not `dist/`; rebuild `dist/` when generated output is needed.
- Keep changes scoped — this is mostly single-file backend logic plus static frontend pages; avoid broad refactors unless that's the task.
- Client-side audio recording in `finish.html` is not yet uploaded/stored server-side (`prepareRecordingPayload()` documents the planned future payload only) — don't assume server storage exists for it.
