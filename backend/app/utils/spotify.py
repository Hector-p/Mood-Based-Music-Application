import requests
import base64
import time
from typing import Optional

class SpotifyService:
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    API_BASE = 'https://api.spotify.com/v1'
    

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, user_token: Optional[str]=None, refresh_token: Optional[str]=None, token_expires_at: Optional[float]=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.access_token = user_token
        self.refresh_token = refresh_token
        self.expires_at = token_expires_at or 0

    def _headers(self):
        return {'Authorization': f'Bearer {self.access_token}'} if self.access_token else {}

    def get_authorize_url(self, state: str = None, scope: str = None):
        if scope is None:
            scope = ('user-read-private user-read-email user-read-playback-state user-modify-playback-state '
                     'playlist-read-private playlist-modify-private playlist-modify-public streaming')
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope
        }
        qs = '&'.join([f"{k}={requests.utils.quote(v)}" for k, v in params.items()])
        return f"{self.AUTH_URL}?{qs}"

    def get_app_token(self):
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64 = base64.b64encode(auth_str.encode()).decode()
        headers = {'Authorization': f'Basic {b64}'}
        data = {'grant_type': 'client_credentials'}
        resp = requests.post(self.TOKEN_URL, headers=headers, data=data)
        resp.raise_for_status()
        json_data = resp.json()
        self.access_token = json_data['access_token']
        self.expires_at = time.time() + json_data.get('expires_in', 3600)
        return self.access_token

    def get_user_token(self, code: str):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        resp = requests.post(self.TOKEN_URL, data=data)
        resp.raise_for_status()
        json_data = resp.json()
        self.access_token = json_data['access_token']
        self.refresh_token = json_data.get('refresh_token')
        self.expires_at = time.time() + json_data.get('expires_in', 3600)
        return json_data

    def refresh_user_token(self):
        if not self.refresh_token:
            raise Exception('No refresh token available')
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        resp = requests.post(self.TOKEN_URL, data=data)
        resp.raise_for_status()
        json_data = resp.json()
        self.access_token = json_data['access_token']
        self.expires_at = time.time() + json_data.get('expires_in', 3600)
        return json_data

    def _ensure_token(self):
        if not self.access_token or time.time() > (self.expires_at - 60):
            # try to use app token if no user token
            self.get_app_token()

    def search_tracks(self, query: str, limit: int = 20):
        self._ensure_token()
        url = f"{self.API_BASE}/search"
        params = {'q': query, 'type': 'track', 'limit': limit}
        resp = requests.get(url, headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    def search_tracks_by_mood(self, mood: str, limit: int = 20):
        """
        Search tracks based on mood with optimized queries
        """
        self._ensure_token()
        
        # Map moods to search queries
        mood_map = {
            'happy': 'happy upbeat cheerful pop dance',
            'sad': 'sad melancholy emotional acoustic ballad',
            'calm': 'calm peaceful relaxing chill ambient',
            'angry': 'rock metal intense aggressive powerful'
        }
        
        query = mood_map.get(mood.lower(), mood)
        return self.search_tracks(query, limit=limit)

    def get_mood_recommendations(self, mood: str, limit: int = 25):
        """
        Get track recommendations based on mood - FIXED VERSION
        Uses search instead of recommendations API for better reliability
        """
        self._ensure_token()
        
        # Map moods to better search queries
        mood_queries = {
            'happy': 'happy upbeat energetic pop dance feel good party',
            'sad': 'sad emotional melancholy acoustic slow ballad heartbreak',
            'calm': 'calm peaceful relaxing chill ambient zen meditation spa',
            'angry': 'rock metal aggressive intense powerful hardcore angry'
        }
        
        query = mood_queries.get(mood.lower(), 'popular music')
        
        # Use search API instead (more reliable than recommendations)
        url = f"{self.API_BASE}/search"
        params = {
            'q': query,
            'type': 'track',
            'limit': limit
        }
        
        resp = requests.get(url, headers=self._headers(), params=params)
        resp.raise_for_status()
        
        result = resp.json()
        
        # Return in same format as recommendations API
        return {
            'tracks': result.get('tracks', {}).get('items', [])
        }

    def get_recommendations(self, seed_tracks: list, limit: int = 20):
        self._ensure_token()
        url = f"{self.API_BASE}/recommendations"
        params = {'seed_tracks': ','.join(seed_tracks[:5]), 'limit': limit}
        resp = requests.get(url, headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    def get_audio_features(self, track_id: str):
        self._ensure_token()
        url = f"{self.API_BASE}/audio-features/{track_id}"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_user_profile(self):
        self._ensure_token()
        url = f"{self.API_BASE}/me"
        resp = requests.get(url, headers=self._headers())
        resp.raise_for_status()
        return resp.json()