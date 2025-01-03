import os
import google.auth.transport.requests
import google.oauth2.id_token
from flask import Flask, request, jsonify

app = Flask(__name__)
prev_token_used = ''

@app.route("/token/")
def token_for_askys():
    global prev_token_used
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Missing or invalid bearer token'}), 401
    token = auth_header.split(' ')[1]
    if token == prev_token_used or len(token) < 30 or not token[1].isdigit():
        return jsonify({'error': 'Invalid bearer token'}), 401
    prev_token_used = token
    try:
        auth_req = google.auth.transport.requests.Request()
        target_audience = 'https://askys-discover-572467571658.asia-south1.run.app'
        
        creds = google.oauth2.id_token.fetch_id_token_credentials(
            target_audience, 
            request=auth_req
        )
        creds.refresh(auth_req)
        return jsonify({'v': '0.1', 'token': creds.token})
    except google.auth.exceptions.RefreshError:
        return jsonify({
            'error': 'Failed to refresh credentials'
        }), 500
    except google.auth.exceptions.GoogleAuthError as e:
        return jsonify({
            'error': f'Authentication error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Unexpected error: {str(e)}'
        }), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
