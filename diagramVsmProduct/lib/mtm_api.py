import requests

class LeanIxMtmApi:
    def __init__(self, hostname, api_token):
        self.hostname = hostname
        self.api_token = api_token
        self.access_token = None
        self.launch_url = None

        self.authenticate()

    def authenticate(self):
        
        url = f"https://{self.hostname}/services/mtm/v1/oauth2/token"
        auth = ("apitoken", self.api_token)
        data = {"grant_type": "client_credentials"}

        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()

        self.access_token = response.json()["access_token"]

        return response.json()["access_token"]
