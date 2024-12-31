import google.auth.transport.requests
import google.oauth2.id_token

import google.auth.transport.requests
import google.oauth2.id_token
import requests


def make_request(service_url: str, method='GET', path='/', json=None, params=None):
    auth_req = google.auth.transport.requests.Request()
    target_audience = service_url
    
    creds = google.oauth2.id_token.fetch_id_token_credentials(
        target_audience, 
        request=auth_req
    )
    creds.refresh(auth_req)

    headers = {
        'Authorization': f'Bearer {creds.token}',
        'Content-Type': 'application/json'
    }
    
    # Ensure the path starts with /
    if not path.startswith('/'):
        path = '/' + path
    url = service_url.rstrip('/') + path
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        params=params
    )
    
    response.raise_for_status()
    return response


if __name__ == '__main__':
    SERVICE_URL = 'https://askys-discover-572467571658.asia-south1.run.app'
    SERVICE_ACCOUNT_PATH = '../gitapower-26-3503b0256243.json'
    
    response = make_request(SERVICE_URL)
    print(response.text)

    # Example GET request
    # response = client(method='GET', path='/api/resource')
    # print(response.json())
    
    # Example POST request
    # data = {'key': 'value'}
    # response = client(method='POST', path='/api/resource', json=data)
    # print(response.json())
