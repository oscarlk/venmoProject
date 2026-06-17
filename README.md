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
- **Spending trend** — money in, money out, and your net balance per month, over a selectable 1-month / 6-month / 1-year range
- **Full transaction history** — every payment in a searchable table
- **Leaderboard** — ranks everyone who uses the app by their average payback time
- **Shareable** — a share button generates a public link (first names only) that anyone can view without an account, with a logo link-preview when posted

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
                                    ▼
                            ┌──────────────────────────────────┐
                            │          MongoDB Atlas            │
                            │   gmail_tokens · venmo_cache      │
                            │     waitlist · leaderboard        │
                            └──────────────────────────────────┘
```

| Layer | Tech | Job |
| --- | --- | --- |
| **Frontend** | React 19, Vite, Material-UI (`@mui/x-charts`) | The dashboard UI and charts. Talks to the backend over HTTP. |
| **Backend** | Python, Flask | Handles Google sign-in, reads Gmail, parses Venmo emails into stats, serves JSON. |
| **Gmail access** | `google-api-python-client` + `google-auth` (see `backend/gmail_client.py`) | Authenticates with the stored token and fetches Venmo emails. |
| **Data source** | Gmail | The source of truth for transactions — every Venmo email is a record. |
| **Storage** | MongoDB Atlas | Three collections (below). |
| **Auth** | Google OAuth 2.0 (`gmail.readonly` scope) | Read-only access to the user's email. |

There is **no traditional transactions database** — Gmail *is* the source of truth. MongoDB stores only supporting data, in four collections:

| Collection | Holds | Why |
| --- | --- | --- |
| `gmail_tokens` | each user's OAuth token (access + refresh token, client id/secret, scopes) | Lets the backend read a user's Gmail without making them sign in again every visit. The long-lived **refresh token** is what keeps access alive after the hourly access token expires. |
| `venmo_cache` | the parsed 1-year transaction set per user, with a timestamp | Caching: one Gmail scan is reused for 30 minutes and sliced into the 1M/6M/1Y views, so loads/range-switches are instant. |
| `leaderboard` | each user's average payback time per range | Powers a cross-user leaderboard that ranks everyone who has signed in by how quickly they pay people back. Refreshed on each dashboard load. |
| `waitlist` | request-access emails submitted on the sign-in page | Collected only — approval is manual (see below). |

**Same-origin proxy:** in production the browser doesn't call Render directly. Vercel proxies `/api/*` to the backend (`frontend/vercel.json`), so everything looks like it comes from the Vercel domain. This keeps the session cookie **first-party** — required for sign-in on iOS Safari, which blocks third-party cookies — and sidesteps CORS. The OAuth callback also runs through `/api`, so the cookie stays first-party across the whole Google round-trip. Locally there's no proxy; the frontend talks to `localhost:8000` directly.

---

## How the code flows

### Signing in (OAuth)

1. User clicks **Sign in with Google** in the frontend. This opens a popup to the backend's `/auth/signin/google` ([backend/server.py](backend/server.py)).
2. The backend redirects the popup to Google's consent screen, asking for read-only Gmail access.
3. Google sends the user back to `/auth/callback/google` with a code. The backend swaps that code for an **access token + refresh token**.
4. The backend saves the token to the `gmail_tokens` collection (MongoDB in prod, a local file in dev) via [backend/token_store.py](backend/token_store.py), creates a session cookie, and closes the popup.
5. The frontend's `AuthContext` ([frontend/src/contexts/AuthContext.jsx](frontend/src/contexts/AuthContext.jsx)) detects success and loads the user.

Two things now persist the login: the **session cookie** ("logged into our app") and the stored **refresh token** ("we can still reach your Gmail"). The refresh token lets the backend mint fresh access tokens automatically, so users don't re-consent every visit.

### Loading the dashboard

1. Once logged in, the dashboard ([frontend/src/pages/Dashboard/Dashboard.jsx](frontend/src/pages/Dashboard/Dashboard.jsx)) calls `/getVenmoData?range=1m|6m|1y`.
2. **Cache check:** if this user's `venmo_cache` entry is < 30 min old, the backend slices it to the requested range and returns immediately (no Gmail call). `?refresh=1` forces a re-scan.
3. **On a miss:** `load_token()` reads the user's token, `gmail_client.build_service()` builds Google credentials in memory, and `read_emails.fetch_transactions()` scans a full year of Gmail. If the access token was refreshed mid-scan, the updated token is written back to `gmail_tokens`. The full result is cached to `venmo_cache`.
4. `read_emails.py` queries Gmail for four kinds of Venmo emails (you paid / someone paid you / requests / completed charge requests) using the patterns in [backend/constants.py](backend/constants.py), runs regexes over each email's subject/snippet to extract name, amount, item, and **matches each request to the earliest payment at or after it** to compute payback time.
5. It aggregates into stats (top payers, monthly totals, average payback time) and returns one JSON object, which the frontend renders as cards, charts, and a table.

### Leaderboard

Each dashboard load also computes the signed-in user's average payback time for all three ranges and upserts it to the `leaderboard` collection (`token_store.save_leaderboard_entry`). The `/leaderboard?range=…` endpoint returns every user's entry sorted by payback time, which the dashboard renders as a ranked card. No extra Gmail scan — it reuses the data already fetched for the dashboard.

### Sharing the leaderboard

The leaderboard card has a **Share** button (`navigator.share` on mobile, copy-link fallback on desktop) that produces a public link like `…/l?range=6m`. That route (`PublicLeaderboard`) is **outside the auth guard** and fetches `GET /public/leaderboard` — a no-login endpoint that returns the ranking with **first names only** (full names never leave the backend). Open Graph tags in `index.html` give it a logo + 👀 link preview (`public/og-image.png`) when posted to iMessage/social. Because the preview image is static, the tags live in the HTML — no serverless OG function needed.

### Requesting access (waitlist)

The sign-in page has a "Request access" form. Submitting an email POSTs to `/waitlist`, which stores it in the `waitlist` collection. It only **collects** — granting access is manual (add the email as a Google test user). See [Managing access](#managing-access-the-waitlist).

### Where to look for what

| You want to change... | Look in |
| --- | --- |
| The dashboard layout / charts / range pills | `frontend/src/pages/Dashboard/Dashboard.jsx` |
| Sign-in page + request-access form | `frontend/src/pages/SignIn/SignIn.jsx` |
| Public share page + leaderboard card | `frontend/src/pages/PublicLeaderboard/` + `frontend/src/components/Leaderboard/LeaderboardCard.jsx` |
| Link-preview tags + share image | `frontend/index.html` + `frontend/public/og-image.png` |
| Sign-in / sign-out behavior | `frontend/src/contexts/AuthContext.jsx` |
| Which backend URL the frontend hits | `frontend/src/config.js` |
| OAuth flow, API endpoints, caching, leaderboard | `backend/server.py` |
| Gmail auth + fetching (Google API) | `backend/gmail_client.py` |
| How Venmo emails are parsed + payback matching | `backend/read_emails.py` + `backend/constants.py` |
| Token / cache / leaderboard / waitlist storage | `backend/token_store.py` |

---

## Project files (and why each exists)

Config/infrastructure files that may look unfamiliar:

| File | Why it's here |
| --- | --- |
| `backend/gmail_client.py` | Gmail data layer on Google's official libraries — builds credentials from the stored token (in memory), builds the search query, and fetches messages with rate-limit retry. |
| `backend/token_store.py` | Saves/loads Google tokens, cached data, and waitlist emails. Uses MongoDB when `MONGODB_URI` is set, otherwise local files — so the same code runs in production and locally. |
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
- Python 3.12+ (3.12 recommended)
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

## Managing access (the waitlist)

The app runs in Google OAuth **Testing** mode, which allows up to 100 manually-approved users. Only Gmail accounts added as **test users** in the Google Cloud consent screen can sign in.

The sign-in page's "Request access" form collects emails into the `waitlist` collection, but **does not grant access**. To approve people:

1. In MongoDB Atlas → `venmo` → `waitlist` → **Browse Collections**, view submitted emails (`{ _id: email, created: timestamp }`).
2. Google Cloud Console → **OAuth consent screen** → **Test users** → **Add users** → paste the emails.
3. (Optional) email them to say they're in.

There's no notification yet — you check the collection periodically. Fully public access (no per-user approval) would require Google's restricted-scope verification + annual security assessment.

## Known limitations / future work

- **Email parsing is regex-based** — if Venmo changes its email format, the patterns in `read_emails.py` need updating.
- **Public access requires Google verification** — reading Gmail uses a *restricted* OAuth scope, so opening it beyond 100 users would require Google's verification + annual security assessment.

### Recently addressed
- **Caching** — a single 1-year Gmail scan is cached per user in MongoDB (`venmo_cache`) for 30 minutes and sliced into the 1M/6M/1Y views, so range switches are instant. Force a re-scan with `?refresh=1`.
- **Gmail access library** — migrated off the deprecated `simplegmail` / `oauth2client` to Google's official `google-api-python-client` + `google-auth` (see `gmail_client.py`). Credentials are held in memory (no on-disk creds file), and rate-limited fetches retry with backoff.
