import requests

class ZohoAPIClient:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret


    def get_access_token(self, refresh_token):
        url = 'https://accounts.zoho.com/oauth/v2/token'
        data = {
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token'
        }
        response = requests.post(url, data=data)
        return response.json()['access_token']
    

    def is_token_valid(self, access_token):
        url = 'https://recruit.zoho.com/recruit/v2/Candidates'
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True
        return False
    
    def get(self, access_token, url):
        headers = {'Authorization': f'Zoho-oauthtoken {access_token}'}
        response = requests.get(url, headers=headers)
        return response