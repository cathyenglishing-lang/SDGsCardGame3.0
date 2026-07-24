# Vercel + Railway + PostgreSQL Deployment

## Railway backend

1. Create a Railway project from this repository.
2. Add a PostgreSQL database service in the same Railway project.
3. Add a Redis service in the same Railway project for API rate limiting.
4. Deploy the backend service from the repository root. The included `railway.json` uses:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

4. Set backend environment variables:

```bash
DATABASE_URL=<Railway PostgreSQL DATABASE_URL>
REDIS_URL=<Railway Redis REDIS_URL>
RATE_LIMIT_ENABLED=true
RATE_LIMIT_FAIL_OPEN=false
SECRET_KEY=<long random string>
FRONTEND_ORIGINS=https://your-vercel-domain.vercel.app
RESEND_API_KEY=<your resend api key>
RESEND_FROM=CardLearn SDGs <your verified resend sender>
INITIAL_ADMIN_NAME=<admin name>
INITIAL_ADMIN_EMAIL=<admin email>
INITIAL_ADMIN_PASSWORD=<strong temporary password>
```

`RATE_LIMIT_FAIL_OPEN=false` keeps the API protected by returning `503` when Redis is configured but unavailable. Set it to `true` only if availability is more important than enforcing traffic limits during a Redis incident.

After the first successful login, rotate the initial admin password flow if you add one later. Do not commit real secrets.

For Resend, create an API key and use a verified sender/domain before testing email delivery:
[Resend Python quickstart](https://resend.com/docs/send-with-python)
[Resend send email API](https://resend.com/docs/api-reference/emails)

## Vercel frontend

1. Create a Vercel project from this repository.
2. Use the included `vercel.json`. The included `pyproject.toml` points Vercel's FastAPI detector at `backend.main:app` so Vercel CLI 54+ does not fail when it sees the backend in this repository.
3. Set the Vercel environment variable:

```bash
API_BASE_URL=https://your-railway-backend-domain.up.railway.app
```

The build command writes this value into `dist/static/config.js`, which is loaded before `static/js/api.js`.

## Local development

Run the API locally with SQLite when `DATABASE_URL` is not set:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Build the static frontend preview output:

```bash
npm run build
```

## Optional SQLite data migration

For a new Railway PostgreSQL database, export the current local SQLite data with:

```bash
set DATABASE_URL=postgresql://...
python scripts/migrate_sqlite_to_postgres.py --replace
```

Use the Railway PostgreSQL public connection string only from your own machine. The app itself should use Railway's internal `DATABASE_URL` reference inside the Railway project.
