"""Thin Gmail data-access layer built on Google's official libraries.

Replaces the deprecated simplegmail / oauth2client stack. Credentials are
read in-memory from the stored token dict (no on-disk creds file needed),
and message fields are produced in the exact same shapes the parsing code in
read_emails.py expects:

    .subject  -> raw Subject header value
    .snippet  -> html.unescape(message snippet)
    .date     -> str(dateutil.parse(Date header).astimezone())
"""

import html
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dateutil import parser as dateparser

# Gmail allows ~250 quota units/user/second; messages.get costs 5 units, so we
# can do ~50/sec. Batch conservatively and retry anything that gets throttled.
_BATCH_SIZE = 25
_BATCH_PAUSE = 0.5
_MAX_ATTEMPTS = 5
_RETRY_STATUSES = {403, 429, 500, 503}


class Message:
    """Lightweight stand-in for a fetched email (only the fields we parse)."""
    __slots__ = ('subject', 'snippet', 'date')

    def __init__(self, subject, snippet, date):
        self.subject = subject
        self.snippet = snippet
        self.date = date


# --- Auth ------------------------------------------------------------------

def build_service(token):
    """Build a Gmail service + credentials from a stored token dict.

    Returns (service, creds). The credentials auto-refresh the access token
    using the refresh token when needed.
    """
    creds = Credentials(
        token=token.get('access_token'),
        refresh_token=token.get('refresh_token'),
        token_uri=token.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=token.get('client_id'),
        client_secret=token.get('client_secret'),
        scopes=token.get('scopes'),
    )
    service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
    return service, creds


def token_from_creds(creds, base):
    """Merge a (possibly refreshed) credentials object back into a token dict."""
    updated = dict(base)
    updated['access_token'] = creds.token
    if creds.refresh_token:
        updated['refresh_token'] = creds.refresh_token
    if creds.expiry:
        updated['token_expiry'] = creds.expiry.isoformat() + 'Z'
    return updated


# --- Search query builder (subset of simplegmail's construct_query) ---------

def _and(qs):
    return qs[0] if len(qs) == 1 else f'({" ".join(qs)})'


def _or(qs):
    return qs[0] if len(qs) == 1 else '{' + ' '.join(qs) + '}'


_TERM_FNS = {
    'sender': lambda v: f'from:{v}',
    'subject': lambda v: f'subject:{v}',
    'exact_phrase': lambda v: f'"{v}"',
}


def build_query(params):
    """Build a Gmail search string from a params dict.

    Supports the keys this app uses: sender, newer_than, subject, exact_phrase.
    Tuples are AND'd, lists are OR'd — matching simplegmail's semantics.
    """
    terms = []
    for key, val in params.items():
        if key == 'newer_than':
            number, unit = val
            terms.append(f'newer_than:{number}{unit[0]}')
            continue
        fn = _TERM_FNS[key]
        if isinstance(val, tuple):
            terms.append(_and([fn(v) for v in val]))
        elif isinstance(val, list):
            terms.append(_or([fn(v) for v in val]))
        else:
            terms.append(fn(val))
    return _and(terms)


# --- Fetching --------------------------------------------------------------

def _to_message(m):
    snippet = html.unescape(m.get('snippet', ''))
    subject = ''
    date = ''
    for h in m.get('payload', {}).get('headers', []):
        name = h.get('name', '').lower()
        if name == 'subject':
            subject = h.get('value', '')
        elif name == 'date':
            try:
                date = str(dateparser.parse(h.get('value', '')).astimezone())
            except (ValueError, TypeError):
                date = h.get('value', '')
    return Message(subject, snippet, date)


def search_messages(service, query):
    """Return Message objects matching a Gmail search query.

    Only headers + snippet are fetched (format='metadata'), batched for speed
    with retry/backoff so rate-limited (429) requests aren't silently dropped.
    """
    # 1) collect matching message ids (paginated)
    ids = []
    page_token = None
    while True:
        resp = service.users().messages().list(
            userId='me', q=query, pageToken=page_token, maxResults=500,
        ).execute()
        ids.extend(m['id'] for m in resp.get('messages', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break

    # 2) fetch headers + snippet for each id (order doesn't matter — callers
    #    sort by date). Retry throttled requests with exponential backoff.
    responses = {}
    pending = list(ids)
    attempt = 0
    while pending and attempt < _MAX_ATTEMPTS:
        retry = []

        def _collect(request_id, response, exception, _retry=retry):
            if exception is None:
                responses[request_id] = response
            else:
                status = getattr(getattr(exception, 'resp', None), 'status', None)
                if status in _RETRY_STATUSES:
                    _retry.append(request_id)
                # non-retryable errors are dropped

        for i in range(0, len(pending), _BATCH_SIZE):
            batch = service.new_batch_http_request(callback=_collect)
            for mid in pending[i:i + _BATCH_SIZE]:
                batch.add(
                    service.users().messages().get(
                        userId='me', id=mid, format='metadata',
                        metadataHeaders=['Subject', 'Date'],
                    ),
                    request_id=mid,
                )
            batch.execute()
            time.sleep(_BATCH_PAUSE)

        pending = retry
        attempt += 1
        if pending:
            time.sleep(2 ** attempt)  # back off before retrying throttled ids

    return [_to_message(r) for r in responses.values()]
