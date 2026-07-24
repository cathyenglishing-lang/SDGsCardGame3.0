# Repository Guidelines

## Project Shape
- FastAPI backend lives in `backend/`; the main app and routes are in `backend/main.py`.
- Static frontend source lives in `frontend/`. Update source files there first.
- `dist/` is generated output from the frontend build script and is used for Vercel static hosting.
- Local SQLite data is stored under `sql/`. Treat `sql/app.db` as local application data.
- Deployment notes are in `DEPLOYMENT.md`; Redis rate-limit notes are in `dev/redis-rate-limit.md`.

## Run And Build
- Local API: `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`
- Frontend build: `npm run build`
- The build script is `scripts/build-frontend.mjs`; it copies `frontend/` to `dist/` and `dist/static/`, then writes config files using `API_BASE_URL` or `VITE_API_BASE_URL`.
- If `python`, `node`, or `npm` are not on PATH in the Codex desktop shell, use the bundled runtimes reported by `codex_app.load_workspace_dependencies`.

## Verification
- Python syntax check: `python -m py_compile backend/main.py backend/rate_limit.py scripts/test_rate_limits.py`
- Redis rate-limit self-test: `python scripts/test_rate_limits.py`
- Frontend build check: `npm run build`

## Backend Notes
- `backend/main.py` initializes the database at import time via `init_db()`.
- Without `DATABASE_URL`, the app uses SQLite at `sql/app.db`; with `DATABASE_URL`, it uses PostgreSQL through `psycopg`.
- API groups include `/auth`, `/content`, `/game`, `/teacher`, and `/health`.
- Rate limiting is implemented in `backend/rate_limit.py` and is enabled only when `REDIS_URL` is configured.
- Email verification uses Resend via `RESEND_API_KEY` and `RESEND_FROM`.
- Initial admin creation is controlled by `INITIAL_ADMIN_NAME`, `INITIAL_ADMIN_EMAIL`, and `INITIAL_ADMIN_PASSWORD`.

## Frontend Notes
- Frontend API calls are centralized in `frontend/js/api.js`.
- Runtime API base URL comes from `window.CARDLEARN_API_BASE_URL`, set by `frontend/config.js` locally and generated config files in `dist/`.
- HTML pages are under `frontend/pages/`; assets are under `frontend/assets/`.

## Working Rules
- Do not commit or expose real values from `.env`; use `.env.example` for documented configuration.
- Preserve existing user data in `sql/` unless a task explicitly asks for migration or reset work.
- Prefer editing source files in `frontend/` over generated files in `dist/`; rebuild `dist/` when generated output is needed.
- Keep changes scoped: this project is mostly single-file backend logic plus static frontend pages, so avoid broad refactors unless they are part of the task.
