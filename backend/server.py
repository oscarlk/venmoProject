from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from read_emails import get_venmo_data
import os
import json
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
import secrets

# NOW we can use os and debug
print("=" * 50)
print("DEBUG: Environment Variables")
print(f"GOOGLE_CLIENT_ID: {os.environ.get('GOOGLE_CLIENT_ID')}")
print(f"GOOGLE_CLIENT_SECRET: {os.environ.get('GOOGLE_CLIENT_SECRET')}")
print(f"FLASK_SECRET_KEY: {os.environ.get('FLASK_SECRET_KEY')}")
print("=" * 50)

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-change-this')

print(f"Flask app secret key: '{app.secret_key}'")
print(f"Secret key length: {len(app.secret_key)}")
print("=" * 50)

CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = 'http://localhost:8000/auth/callback/google'

def create_gmail_token_file(user_id, tokens):
    """Create Gmail token file in the format simplegmail expects"""
    token_structure = {
        "access_token": tokens['access_token'],
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
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
            "scope": "https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.settings.basic",
            "token_type": "Bearer",
            "refresh_token": tokens.get('refresh_token'),
            "refresh_token_expires_in": 527109
        },
        "scopes": [
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/gmail.settings.basic"
        ],
        "token_info_uri": "https://oauth2.googleapis.com/tokeninfo",
        "invalid": False,
        "_class": "OAuth2Credentials",
        "_module": "oauth2client.client"
    }
    
    # Create tokens directory
    tokens_dir = 'tokens'
    os.makedirs(tokens_dir, exist_ok=True)
    
    # Write token file
    token_file_path = os.path.join(tokens_dir, f'gmail_token_{user_id}.json')
    with open(token_file_path, 'w') as f:
        json.dump(token_structure, f, indent=2)
    
    return token_file_path

@app.route('/auth/signin/google')
def google_signin():
    """Initiate Google OAuth flow"""
    print("=" * 50)
    print("Starting OAuth flow...")
    
    # IMPORTANT: Clear ALL existing session data first
    session.clear()
    print("Cleared all existing session data")
    
    # Generate fresh state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state
    
    print(f"Generated fresh state: {state}")
    print(f"Session after setting state: {dict(session)}")
    print("=" * 50)
    
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scope': 'openid email profile https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.settings.basic',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urlencode(params)
    print(f"Redirecting to: {auth_url}")
    return redirect(auth_url)

@app.route('/auth/callback/google')
def google_callback():
    """Handle Google OAuth callback"""
    print("=" * 50)
    print("OAuth callback received")
    print(f"Request args: {dict(request.args)}")
    print(f"Session contents: {dict(session)}")
    print("=" * 50)
    
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        print(f"OAuth error: {error}")
        return f'''
        <script>
            window.opener.postMessage({{type: 'error', message: 'OAuth error: {error}'}}, 'http://localhost:5173');
            window.close();
        </script>
        ''', 400
    
    # Debug session state
    session_state = session.get('oauth_state')
    print(f"Received state: {state}")
    print(f"Session state: {session_state}")
    
    # Verify state parameter
    if not state:
        print("No state parameter received")
        return '''
        <script>
            window.opener.postMessage({type: 'error', message: 'No state parameter received'}, 'http://localhost:5173');
            window.close();
        </script>
        ''', 400
    
    if not session_state:
        print("ERROR: No state found in session")
        return '''
        <script>
            window.opener.postMessage({type: 'error', message: 'Session expired. Please try again.'}, 'http://localhost:5173');
            window.close();
        </script>
        ''', 400
    
    if state != session_state:
        print(f"State mismatch! Received: {state}, Expected: {session_state}")
        # Clear session on mismatch
        session.clear()
        return '''
        <script>
            window.opener.postMessage({type: 'error', message: 'Session expired. Please try signing in again.'}, 'http://localhost:5173');
            window.close();
        </script>
        ''', 400
    
    if not code:
        print("No authorization code received")
        return '''
        <script>
            window.opener.postMessage({type: 'error', message: 'No authorization code received'}, 'http://localhost:5173');
            window.close();
        </script>
        ''', 400
    
    try:
        print("State verification passed! Exchanging code for tokens...")
        
        # Clear the OAuth state since we're using it now
        session.pop('oauth_state', None)
        
        # Exchange code for tokens
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': GOOGLE_REDIRECT_URI
        }
        
        token_response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        tokens = token_response.json()
        
        print(f"Token response status: {token_response.status_code}")
        if 'error' in tokens:
            print(f"Token exchange error: {tokens}")
            raise Exception(f"Token exchange failed: {tokens['error']}")
        
        print("✅ Token exchange successful!")
        
        # Get user info
        headers = {'Authorization': f"Bearer {tokens['access_token']}"}
        user_response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers)
        user_info = user_response.json()
        
        print(f"✅ User info received for: {user_info.get('email')}")
        
        # Create user session
        user_id = user_info['email'].replace('@', '_').replace('.', '_')
        session['user'] = {
            'id': user_id,
            'email': user_info['email'],
            'name': user_info['name'],
            'picture': user_info.get('picture')
        }
        
        # Create Gmail token file
        token_file_path = create_gmail_token_file(user_id, tokens)
        session['gmail_token_file'] = token_file_path
        
        print(f"✅ User {user_info['email']} authenticated successfully")
        print(f"Final session: {dict(session)}")
        
        # Success - close popup and notify parent
        return '''
        <script>
            window.opener.postMessage({type: 'success'}, 'http://localhost:5173');
            window.close();
        </script>
        '''
        
    except Exception as e:
        print(f"❌ Auth callback error: {str(e)}")
        import traceback
        traceback.print_exc()
        session.clear()  # Clear session on error
        return f'''
        <script>
            window.opener.postMessage({{type: 'error', message: 'Authentication failed: {str(e)}'}}, 'http://localhost:5173');
            window.close();
        </script>
        ''', 500

@app.route('/auth/session')
def get_session():
    """Get current user session"""
    if 'user' in session:
        return jsonify({'user': session['user']})
    else:
        return jsonify({'error': 'Not authenticated'}), 401

@app.route('/auth/signout', methods=['GET', 'POST'])
def signout():
    """Sign out user"""
    session.clear()
    if request.method == 'GET':
        return "Session cleared successfully. You can now try signing in again."
    else:
        return jsonify({'success': True})

@app.route('/getVenmoData')
def get_venmo_data_route():
    """Get Venmo data for authenticated user"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        token_file = session.get('gmail_token_file')
        if not token_file or not os.path.exists(token_file):
            return jsonify({'error': 'Gmail token file not found'}), 404
        
        # Call your existing function with the user-specific token file
        obj = get_venmo_data(token_file=token_file)
        return jsonify(obj)
    
    except Exception as e:
        print(f"Error processing Venmo data request: {str(e)}")
        return jsonify({'error': f'Failed to process request: {str(e)}'}), 500

@app.route('/')
def home():
    return "Venmo Analytics Backend - Ready to serve!"

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(port=8000, debug=True)