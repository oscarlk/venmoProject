from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from read_emails import get_venmo_data
import token_store
import os
import requests
from urllib.parse import urlencode
import secrets

# --- Configuration (env-driven, with local-dev defaults) -------------------
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.environ.get(
    'GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/callback/google'
)
# Read-only access is all this app needs.
GMAIL_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'
OAUTH_SCOPE = f'openid email profile {GMAIL_SCOPE}'

# When the frontend is served over https it is on a different domain than the
# backend, so the session cookie must be cross-site (SameSite=None; Secure).
_CROSS_SITE = FRONTEND_URL.startswith('https')

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("WARNING: GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not set")

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this')
app.config.update(
    SESSION_COOKIE_SAMESITE='None' if _CROSS_SITE else 'Lax',
    SESSION_COOKIE_SECURE=_CROSS_SITE,
)

CORS(app, supports_credentials=True, origins=[FRONTEND_URL])


def _popup_response(message_type, message='', status=200):
    """Render the popup-closing script that notifies the opener window."""
    payload = '{type: "%s"}' % message_type
    if message:
        payload = '{type: "%s", message: "%s"}' % (message_type, message)
    html = f'''
    <script>
        window.opener.postMessage({payload}, "{FRONTEND_URL}");
        window.close();
    </script>
    '''
    return html, status


@app.route('/auth/signin/google')
def google_signin():
    """Initiate Google OAuth flow"""
    session.clear()

    # Generate fresh state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scope': OAUTH_SCOPE,
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
    }

    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    return redirect(auth_url)


@app.route('/auth/callback/google')
def google_callback():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if error:
        return _popup_response('error', f'OAuth error: {error}', 400)

    # Verify state parameter (CSRF protection)
    session_state = session.get('oauth_state')
    if not state:
        return _popup_response('error', 'No state parameter received', 400)
    if not session_state:
        return _popup_response('error', 'Session expired. Please try again.', 400)
    if state != session_state:
        session.clear()
        return _popup_response('error', 'Session expired. Please try signing in again.', 400)
    if not code:
        return _popup_response('error', 'No authorization code received', 400)

    try:
        # Consume the OAuth state
        session.pop('oauth_state', None)

        # Exchange code for tokens
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI,
        }
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        tokens = token_response.json()
        if 'error' in tokens:
            raise Exception(f"Token exchange failed: {tokens['error']}")

        # Get user info
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
        user_info = user_response.json()

        # Create user session
        user_id = user_info['email'].replace('@', '_').replace('.', '_')
        session['user'] = {
            'id': user_id,
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info.get('picture'),
        }

        # Persist the Gmail token (MongoDB in prod, local file in dev)
        token_structure = token_store.build_token_structure(
            tokens, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
        )
        token_store.save_token(user_id, token_structure)

        print(f"User {user_info['email']} authenticated successfully")
        return _popup_response('success')

    except Exception as e:
        print(f"Auth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        session.clear()
        return _popup_response('error', f'Authentication failed: {str(e)}', 500)


@app.route('/auth/session')
def get_session():
    """Get current user session"""
    if 'user' in session:
        return jsonify({'user': session['user']})
    return jsonify({'error': 'Not authenticated'}), 401


@app.route('/auth/signout', methods=['GET', 'POST'])
def signout():
    """Sign out user"""
    session.clear()
    if request.method == 'GET':
        return "Session cleared successfully. You can now try signing in again."
    return jsonify({'success': True})


@app.route('/getVenmoData')
def get_venmo_data_route():
    """Get Venmo data for authenticated user"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    user_id = session['user']['id']
    token_file, is_temp = token_store.materialize_token_file(user_id)
    if not token_file:
        return jsonify({'error': 'Gmail token not found. Please sign in again.'}), 404

    try:
        obj = get_venmo_data(token_file=token_file)
        # simplegmail may refresh the access token and rewrite the creds file;
        # persist any refresh back to the store.
        token_store.persist_refreshed_token(user_id, token_file)
        return jsonify(obj)
    except Exception as e:
        print(f"Error processing Venmo data request: {str(e)}")
        return jsonify({'error': f'Failed to process request: {str(e)}'}), 500
    finally:
        if is_temp and os.path.exists(token_file):
            os.remove(token_file)


@app.route('/')
def home():
    return "Venmo Analytics Backend - Ready to serve!"


@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
