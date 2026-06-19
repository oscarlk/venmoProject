# Deployment Guide

Architecture:

- **Frontend** (React/Vite) → **Vercel** (static site)
- **Backend** (Flask) → **Render** (long-running web service; Railway works the same way)
- **Storage** → **MongoDB Atlas** (tokens, cache, leaderboard, waitlist)

**Same-origin proxy:** the browser never talks to Render directly. Vercel
proxies `/(api)/*` to the Render backend (see `frontend/vercel.json`), so to the
browser everything is served from the Vercel domain. This makes the session
cookie **first-party**, which is required for sign-in to work on iOS Safari
(it blocks third-party cookies). It also means CORS is a non-issue in
production.

The backend auto-detects its environment: if `MONGODB_URI` is set it uses
MongoDB; otherwise it falls back to local files for development. No code
changes are needed to switch between local and production.

---

## 1. MongoDB Atlas

1. Create a free (M0) cluster at https://www.mongodb.com/atlas.
2. Create a database user (username + password).
3. Network Access → allow `0.0.0.0/0` (or Render's outbound IPs).
4. Copy the connection string, e.g.
   `mongodb+srv://<user>:<pass>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority`.
   This becomes `MONGODB_URI`. The app uses database `venmo`; collections
   (`gmail_tokens`, `venmo_cache`, `leaderboard`, `waitlist`) are created
   automatically.

## 2. Google Cloud OAuth

Use a **Web application** OAuth client (Google Cloud Console → APIs & Services →
Credentials):

1. **Authorized redirect URIs** — because the OAuth callback also goes through
   the Vercel proxy, register the **proxied** callback:
   `https://<your-app>.vercel.app/api/auth/callback/google`
   (keep `http://localhost:8000/auth/callback/google` for local dev).
   - Must match the backend's `GOOGLE_REDIRECT_URI` character-for-character.
   - Changes can take 5 min–a few hours to propagate.
2. The client ID/secret used here go into Render as `GOOGLE_CLIENT_ID` /
   `GOOGLE_CLIENT_SECRET`.
3. **Publishing status** — the app requests `gmail.readonly` (a *restricted*
   scope) and runs in **Production** mode with an unverified-app user cap of
   **100 users** (lifetime, can't be reset). Users self-serve (no test-user
   list) but see an "unverified app" warning. Going beyond 100 / removing the
   warning needs Google's restricted-scope verification + annual CASA
   assessment.

## 3. Backend on Render

1. New → Web Service → connect the repo, set **Root Directory** to `backend`.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn server:app --bind 0.0.0.0:$PORT`
   (also defined in `backend/Procfile`).
4. Environment variables:

   | Key | Value |
   | --- | --- |
   | `GOOGLE_CLIENT_ID` | from Google Cloud (Web client) |
   | `GOOGLE_CLIENT_SECRET` | from Google Cloud (Web client) |
   | `FLASK_SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `FRONTEND_URL` | `https://<your-app>.vercel.app` (no trailing slash) |
   | `GOOGLE_REDIRECT_URI` | `https://<your-app>.vercel.app/api/auth/callback/google` |
   | `MONGODB_URI` | from Atlas |
   | `MONGODB_DB` | `venmo` |
   | `FLASK_DEBUG` | `false` |

   `FRONTEND_URL` being `https://` enables `SameSite=None; Secure` cookies and
   sets the CORS origin. Note `GOOGLE_REDIRECT_URI` points at the **Vercel /api**
   path, not Render directly — that's what keeps the cookie first-party.

## 4. Frontend on Vercel

1. New Project → import the repo, set **Root Directory** to `frontend`.
   Framework preset: Vite (build `npm run build`, output `dist`).
2. Environment variable:

   | Key | Value |
   | --- | --- |
   | `VITE_API_URL` | `/api` |

   This makes the app call same-origin `/(api)/...`, which `vercel.json`
   proxies to Render. (Vite bakes env vars in at build time — redeploy after
   changing it.)
3. `frontend/vercel.json` defines the `/api/*` → Render proxy **and** the SPA
   fallback (rewrite to `index.html`). Update the Render URL there if the
   backend URL changes.

## 5. Wire-up order

1. Deploy backend → note its Render URL.
2. Set the Render URL as the proxy destination in `frontend/vercel.json`.
3. Deploy frontend with `VITE_API_URL=/api` → note its Vercel URL.
4. Set backend `FRONTEND_URL` and `GOOGLE_REDIRECT_URI` (the `/api` callback);
   redeploy backend.
5. Register the `/api` redirect URI in Google Cloud (on the Web client).
6. Open the Vercel URL and sign in (test on iOS Safari to confirm the
   first-party cookie fix).

---

## Local development

Backend:

```bash
cd backend
/opt/homebrew/bin/python3.12 -m venv venv
venv/bin/pip install -r requirements.txt
# .env needs GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FLASK_SECRET_KEY
venv/bin/python server.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Locally `VITE_API_URL` is unset, so the frontend talks to `http://localhost:8000`
directly (no proxy needed). With no `MONGODB_URI` set, tokens/cache/etc. are
written to `backend/tokens/`.

## Known tech debt

- Email parsing is regex-based and breaks if Venmo changes its email format
  (`backend/read_emails.py`).
- The OG link-preview image is static (same preview for every URL). A
  per-leaderboard dynamic image would need a serverless OG endpoint.
