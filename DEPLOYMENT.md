# Deployment Guide

Architecture:

- **Frontend** (React/Vite) → **Vercel** (static site)
- **Backend** (Flask) → **Render** (long-running web service; Railway works the same way)
- **Gmail tokens** → **MongoDB Atlas**

The backend auto-detects its environment: if `MONGODB_URI` is set it stores
tokens in MongoDB; otherwise it falls back to local files for development. No
code changes are needed to switch between local and production.

---

## 1. MongoDB Atlas (token storage)

1. Create a free cluster at https://www.mongodb.com/atlas.
2. Create a database user (username + password).
3. Network Access → allow `0.0.0.0/0` (or Render's outbound IPs).
4. Copy the connection string, e.g.
   `mongodb+srv://<user>:<pass>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority`.
   This becomes `MONGODB_URI`. The app uses database `venmo`, collection
   `gmail_tokens` (created automatically).

## 2. Google Cloud OAuth

In the existing OAuth client (Google Cloud Console → APIs & Services →
Credentials):

1. **Authorized redirect URIs** — add the production callback:
   `https://<your-backend>.onrender.com/auth/callback/google`
   (keep `http://localhost:8000/auth/callback/google` for local dev).
2. **OAuth consent screen** — the app now requests only
   `gmail.readonly`. Keep the app in **Testing** mode and add each user under
   **Test users** (up to 100). No Google verification is required in this mode.
   - Going fully public later requires Google's restricted-scope verification
     + annual CASA security assessment.
3. Consider rotating the client secret (Console → Credentials) since the old
   one was present in an on-disk token file. Update `GOOGLE_CLIENT_SECRET`
   everywhere if you do.

## 3. Backend on Render

1. New → Web Service → connect the repo, set **Root Directory** to `backend`.
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn server:app --bind 0.0.0.0:$PORT`
   (also defined in `backend/Procfile`).
4. Environment variables:

   | Key | Value |
   | --- | --- |
   | `GOOGLE_CLIENT_ID` | from Google Cloud |
   | `GOOGLE_CLIENT_SECRET` | from Google Cloud |
   | `FLASK_SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `FRONTEND_URL` | `https://<your-app>.vercel.app` |
   | `GOOGLE_REDIRECT_URI` | `https://<your-backend>.onrender.com/auth/callback/google` |
   | `MONGODB_URI` | from Atlas |
   | `MONGODB_DB` | `venmo` |
   | `FLASK_DEBUG` | `false` |

   Setting `FRONTEND_URL` to an `https://` URL automatically enables
   cross-site session cookies (`SameSite=None; Secure`), required because the
   frontend and backend are on different domains.

## 4. Frontend on Vercel

1. New Project → import the repo, set **Root Directory** to `frontend`.
   Framework preset: Vite (build `npm run build`, output `dist`).
2. Environment variable:

   | Key | Value |
   | --- | --- |
   | `VITE_API_URL` | `https://<your-backend>.onrender.com` |

3. `frontend/vercel.json` already handles SPA routing (rewrites to
   `index.html`) so React Router deep links work.

## 5. Wire-up order

1. Deploy backend → note its URL.
2. Deploy frontend with `VITE_API_URL` = backend URL → note its URL.
3. Set backend `FRONTEND_URL` = frontend URL and `GOOGLE_REDIRECT_URI` =
   backend callback; redeploy backend.
4. Add the production redirect URI + test users in Google Cloud.
5. Open the Vercel URL and sign in.

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

With no `MONGODB_URI` set, tokens are written to `backend/tokens/` and the app
behaves exactly as before.

## Known tech debt

- `simplegmail` / `oauth2client` are deprecated. Migrating to
  `google-api-python-client` + `google-auth` would remove the temp-file dance
  in `token_store.materialize_token_file` and improve token refresh handling.
- `/getVenmoData` rescans ~6 months of Gmail on every load. Cache results in
  MongoDB to cut latency and Gmail API quota usage.
