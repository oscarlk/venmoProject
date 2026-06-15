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
import tempfile
from datetime import datetime, timedelta

USE_MONGO = bool(os.environ.get('MONGODB_URI'))

_TOKENS_DIR = 'tokens'
_collection = None


def _get_collection():
    """Lazily create the MongoDB collection handle (one client per process)."""
    global _collection
    if _collection is None:
        from pymongo import MongoClient
        client = MongoClient(os.environ['MONGODB_URI'])
        db = client[os.environ.get('MONGODB_DB', 'venmo')]
        _collection = db['gmail_tokens']
    return _collection


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


def materialize_token_file(user_id):
    """Return (path, is_temp) to a creds file simplegmail can read.

    Returns (None, False) if no token is stored for the user. When is_temp is
    True the caller is responsible for deleting the path when done.
    """
    if USE_MONGO:
        col = _get_collection()
        doc = col.find_one({'_id': user_id})
        if not doc:
            return None, False
        tmp = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False)
        json.dump(doc['token'], tmp)
        tmp.close()
        return tmp.name, True

    path = _token_path(user_id)
    if not os.path.exists(path):
        return None, False
    return path, False


def persist_refreshed_token(user_id, path):
    """Read a (possibly refreshed) creds file back and save it to the store.

    simplegmail/oauth2client may refresh the access token and rewrite the creds
    file. When that file is a temp file (MongoDB mode), read it back so the
    refreshed token isn't lost.
    """
    if not USE_MONGO:
        return
    try:
        with open(path) as f:
            token_structure = json.load(f)
        save_token(user_id, token_structure)
    except (OSError, json.JSONDecodeError):
        pass


def _token_path(user_id):
    return os.path.join(_TOKENS_DIR, f'gmail_token_{user_id}.json')
