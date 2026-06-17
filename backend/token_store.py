"""Storage for per-user Gmail OAuth tokens.

simplegmail expects a credentials file on disk (oauth2client format). In
production that doesn't survive a redeploy and is a liability, so when
MONGODB_URI is set we store the token document in MongoDB Atlas and
materialize a short-lived temp file only for the duration of a request.

When MONGODB_URI is not set we fall back to local files under tokens/, so
local development keeps working with no database.
"""

import os
import json
import time
from datetime import datetime, timedelta

USE_MONGO = bool(os.environ.get('MONGODB_URI'))

_TOKENS_DIR = 'tokens'
_collection = None


_db = None


def _get_db():
    """Lazily create the MongoDB database handle (one client per process)."""
    global _db
    if _db is None:
        from pymongo import MongoClient
        client = MongoClient(os.environ['MONGODB_URI'])
        _db = client[os.environ.get('MONGODB_DB', 'venmo')]
    return _db


def _get_collection():
    """Lazily create the gmail_tokens collection handle."""
    global _collection
    if _collection is None:
        _collection = _get_db()['gmail_tokens']
    return _collection


def add_waitlist_email(email):
    """Record a request-access email (MongoDB collection or local file).

    Idempotent on email so duplicate submissions don't pile up.
    """
    if USE_MONGO:
        from datetime import datetime
        _get_db()['waitlist'].update_one(
            {'_id': email},
            {'$setOnInsert': {'created': datetime.utcnow().isoformat() + 'Z'}},
            upsert=True,
        )
    else:
        os.makedirs(_TOKENS_DIR, exist_ok=True)
        path = os.path.join(_TOKENS_DIR, 'waitlist.txt')
        existing = set()
        if os.path.exists(path):
            with open(path) as f:
                existing = {line.strip() for line in f}
        if email not in existing:
            with open(path, 'a') as f:
                f.write(email + '\n')


def build_token_structure(tokens, client_id, client_secret):
    """Build the oauth2client-format credentials dict simplegmail expects.

    `tokens` is the raw token response from Google's token endpoint.
    """
    scope = "https://www.googleapis.com/auth/gmail.readonly"
    return {
        "access_token": tokens['access_token'],
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": tokens.get('refresh_token'),
        "token_expiry": (datetime.now() + timedelta(seconds=tokens.get('expires_in', 3599))).isoformat() + 'Z',
        "token_uri": "https://oauth2.googleapis.com/token",
        "user_agent": None,
        "revoke_uri": "https://oauth2.googleapis.com/revoke",
        "id_token": None,
        "id_token_jwt": None,
        "token_response": {
            "access_token": tokens['access_token'],
            "expires_in": tokens.get('expires_in', 3599),
            "scope": scope,
            "token_type": "Bearer",
            "refresh_token": tokens.get('refresh_token'),
        },
        "scopes": [scope],
        "token_info_uri": "https://oauth2.googleapis.com/tokeninfo",
        "invalid": False,
        "_class": "OAuth2Credentials",
        "_module": "oauth2client.client",
    }


def save_token(user_id, token_structure):
    """Persist a token document for a user (MongoDB or local file)."""
    if USE_MONGO:
        col = _get_collection()
        col.replace_one(
            {'_id': user_id},
            {'_id': user_id, 'token': token_structure},
            upsert=True,
        )
    else:
        os.makedirs(_TOKENS_DIR, exist_ok=True)
        with open(_token_path(user_id), 'w') as f:
            json.dump(token_structure, f, indent=2)


def load_token(user_id):
    """Return the stored token dict for a user, or None if not found."""
    if USE_MONGO:
        doc = _get_collection().find_one({'_id': user_id})
        return doc['token'] if doc else None

    path = _token_path(user_id)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def _token_path(user_id):
    return os.path.join(_TOKENS_DIR, f'gmail_token_{user_id}.json')


def get_cache(user_id):
    """Return the cached Venmo data doc for a user, or None.

    Shape: {'data': {...}, 'fetchedAt': <epoch seconds>}
    """
    if USE_MONGO:
        return _get_db()['venmo_cache'].find_one({'_id': user_id})
    path = os.path.join(_TOKENS_DIR, f'cache_{user_id}.json')
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_cache(user_id, data):
    """Cache parsed Venmo data (full window) for a user with a timestamp."""
    doc = {'_id': user_id, 'data': data, 'fetchedAt': time.time()}
    if USE_MONGO:
        _get_db()['venmo_cache'].replace_one({'_id': user_id}, doc, upsert=True)
    else:
        os.makedirs(_TOKENS_DIR, exist_ok=True)
        with open(os.path.join(_TOKENS_DIR, f'cache_{user_id}.json'), 'w') as f:
            json.dump(doc, f)


_LEADERBOARD_FILE = 'leaderboard.json'


def save_leaderboard_entry(user_id, name, paybacks):
    """Upsert this user's leaderboard entry (per-range payback averages).

    `paybacks` is {range: {'avg': seconds|None, 'count': int}}.
    """
    doc = {'_id': user_id, 'name': name, 'paybacks': paybacks, 'updatedAt': time.time()}
    if USE_MONGO:
        _get_db()['leaderboard'].replace_one({'_id': user_id}, doc, upsert=True)
    else:
        os.makedirs(_TOKENS_DIR, exist_ok=True)
        path = os.path.join(_TOKENS_DIR, _LEADERBOARD_FILE)
        entries = {}
        if os.path.exists(path):
            with open(path) as f:
                entries = json.load(f)
        entries[user_id] = doc
        with open(path, 'w') as f:
            json.dump(entries, f)


def get_leaderboard():
    """Return all leaderboard entry docs."""
    if USE_MONGO:
        return list(_get_db()['leaderboard'].find())
    path = os.path.join(_TOKENS_DIR, _LEADERBOARD_FILE)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(json.load(f).values())
