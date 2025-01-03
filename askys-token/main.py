import google.auth.transport.requests
import google.oauth2.id_token
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/token/")
def token_for_askys():
    auth_req = google.auth.transport.requests.Request()
    target_audience = 'https://askys-discover-572467571658.asia-south1.run.app'
    
    creds = google.oauth2.id_token.fetch_id_token_credentials(
        target_audience, 
        request=auth_req
    )
    creds.refresh(auth_req)
    return jsonify({'token': creds.token})
