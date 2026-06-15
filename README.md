# Venmo Analytics

A web app that turns your Venmo history into a personal spending dashboard — who you pay, who pays you, how fast people pay you back, and your money in vs. out over time.

**Working demo:** https://drive.google.com/file/d/1H1P5uHx4OyU9GiyUxEJeG8Ze0Bh7LwlK/view?usp=sharing

---

## What it does (the non-technical version)

Venmo emails you a receipt every time money moves — when you pay someone, when someone pays you, when someone requests money. Those receipts pile up in your inbox and you never look at them again.

This app reads those Venmo receipt emails from your Gmail (with your permission, read-only) and turns them into a clean dashboard:

- **Total transactions** — how many payments you've made and received
- **Top people** — who you've paid the most, and who's paid you the most
- **Average payback time** — when you request money, how long until people actually pay you
- **6-month spending trend** — money in, money out, and your net balance per month
- **Full transaction history** — every payment in a searchable table

You sign in with Google (one click), and the app does the rest. It never sees your password, can't send email, and only ever *reads* — nothing is changed in your inbox.

---

## How it's built (architecture)

Three pieces, each independently deployable:

```
┌─────────────────┐        ┌──────────────────┐        ┌──────────────────┐
│   Frontend      │  HTTP  │    Backend       │  reads  │   Your Gmail     │
│  React + Vite   │ ─────► │  Python / Flask  │ ──────► │  (Venmo emails)  │
│   (Vercel)      │ ◄───── │    (Render)      │         └──────────────────┘
└─────────────────┘  JSON  └──────────────────┘
                                    │
                                    │ stores login tokens
                                    ▼
                            ┌──────────────────┐
                            │  MongoDB Atlas   │
                            │  (gmail tokens)  │
                            └──────────────────┘
```

| Layer | Tech | Job |
| --- | --- | --- |
| **Frontend** | React 19, Vite, Material-UI (`@mui/x-charts`) | The dashboard UI and charts. Talks to the backend over HTTP. |
| **Backend** | Python, Flask | Handles Google sign-in, reads Gmail, parses Venmo emails into stats, serves JSON. |
| **Data source** | Gmail API (via `simplegmail`) | The "database" of transactions — every Venmo email is a record. |
| **Token storage** | MongoDB Atlas | Remembers each user's Google login token so they don't re-authorize every visit. |
| **Auth** | Google OAuth 2.0 (`gmail.readonly` scope) | Read-only access to the user's email. |

There is **no traditional transactions database** — Gmail *is* the source of truth. The only thing stored is each user's OAuth token.

---

## How the code flows

### Signing in (OAuth)

1. User clicks **Sign in with Google** in the frontend. This opens a popup to the backend's `/auth/signin/google` ([backend/server.py](backend/server.py)).
2. The backend redirects the popup to Google's consent screen, asking for read-only Gmail access.
3. Google sends the user back to `/auth/callback/google` with a code. The backend swaps that code for an access token + refresh token.
4. The backend saves the token (to MongoDB in production, to a local file in dev) via [backend/token_store.py](backend/token_store.py), creates a session, and closes the popup.
5. The frontend's `AuthContext` ([frontend/src/contexts/AuthContext.jsx](frontend/src/contexts/AuthContext.jsx)) detects success and loads the user.

### Loading the dashboard

1. Once logged in, the dashboard ([frontend/src/pages/Dashboard/Dashboard.jsx](frontend/src/pages/Dashboard/Dashboard.jsx)) calls the backend's `/getVenmoData`.
2. The backend looks up the user's stored token, hands it to `get_venmo_data()` in [backend/read_emails.py](backend/read_emails.py).
3. `read_emails.py` queries Gmail for four kinds of Venmo emails (you paid / someone paid you / requests / completed charge requests) using the search patterns in [backend/constants.py](backend/constants.py), then runs regexes over each email's subject and preview text to pull out the name, amount, and item.
4. It aggregates everything into stats (top payers, monthly totals, average payback time) and returns one JSON object.
5. The frontend renders that JSON as cards, bar/line charts, and a transaction table.

### Where to look for what

| You want to change... | Look in |
| --- | --- |
| The dashboard layout/charts | `frontend/src/pages/Dashboard/Dashboard.jsx` |
| Sign-in / sign-out behavior | `frontend/src/contexts/AuthContext.jsx` |
| Which backend URL the frontend hits | `frontend/src/config.js` |
| OAuth flow, API endpoints | `backend/server.py` |
| How Venmo emails are parsed | `backend/read_emails.py` + `backend/constants.py` |
| Where login tokens are stored | `backend/token_store.py` |

---

## Project files (and why each exists)

Config/infrastructure files that may look unfamiliar:

| File | Why it's here |
| --- | --- |
| `backend/token_store.py` | Saves/loads Google tokens. Uses MongoDB when `MONGODB_URI` is set, otherwise local files — so the same code runs in production and locally. |
| `backend/Procfile` | Tells the host (Render) how to start the app: `gunicorn server:app`. |
| `backend/.env.example` | Documents every environment variable the backend needs (no secrets in it). Copy it to `.env` and fill in. |
| `frontend/config.js` | Single place that defines the backend URL (`VITE_API_URL` in prod, `localhost:8000` in dev). |
| `frontend/vercel.json` | Tells Vercel to route all paths to the app so page refreshes/deep links work (single-page app routing). |
| `frontend/.env.example` | Documents the one frontend env var (`VITE_API_URL`). |
| `DEPLOYMENT.md` | Step-by-step guide to deploy to Vercel + Render + MongoDB Atlas. |

These are committed so that **anyone (or any host) checking out the repo has everything needed to build and deploy.** What is *not* committed (see `.gitignore`): `backend/.env` (real secrets), `backend/tokens/` (local login tokens), `backend/venv/` and `node_modules/` (installed dependencies). Those are either secret or regenerated on install.

---

## Running locally

### Prerequisites
- Python 3.12 (3.14 may have issues with the older `oauth2client` dependency)
- Node.js 18+
- A Google OAuth client ID + secret ([Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials), with `http://localhost:8000/auth/callback/google` listed as an authorized redirect URI.

### Backend

```bash
cd backend
python3.12 -m venv venv
venv/bin/pip install -r requirements.txt
```

Create `backend/.env` (copy from `.env.example`) with at minimum:

```
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
FLASK_SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
```

`MONGODB_URI` is **optional locally** — leave it unset and tokens are stored as files in `backend/tokens/`. Set it only if you want to test the MongoDB path.

Start it:

```bash
venv/bin/python server.py        # runs on http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                       # runs on http://localhost:5173
```

`VITE_API_URL` is optional locally (defaults to `http://localhost:8000`).

### Try it
Open http://localhost:5173, click **Sign in with Google**, authorize, and the dashboard loads your Venmo stats.

> Note: while the Google app is in "Testing" mode, only Gmail accounts added as **test users** in the Google Cloud consent screen can sign in.

---

## Deploying

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for the full walkthrough (Vercel frontend + Render backend + MongoDB Atlas, environment variables, and Google OAuth setup).

---

## Known limitations / future work

- **Email parsing is regex-based** — if Venmo changes its email format, the patterns in `read_emails.py` need updating.
- **No caching** — every dashboard load re-scans ~6 months of Gmail. Caching results in MongoDB would cut latency and API usage.
- **`simplegmail` / `oauth2client` are deprecated** — a future migration to `google-api-python-client` would modernize the auth/token handling.
- **Public access requires Google verification** — reading Gmail uses a *restricted* OAuth scope, so opening it beyond 100 users would require Google's verification + annual security assessment.
