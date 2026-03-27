import requests
from typing import Optional, List, Dict

class JamendoService:
    """
    Jamendo API Service - Free Creative Commons music
    Requires free API key from https://devportal.jamendo.com/
    Provides FULL track playback (not just previews!)
    """
    API_BASE = 'https://api.jamendo.com/v3.0'
    
    def __init__(self, client_id: str):
        """
        Initialize Jamendo service
        
        Args:
            client_id: Jamendo API client ID (get free at https://devportal.jamendo.com/)
        """
        self.client_id = client_id
    
    def search_tracks(self, query: str, limit: int = 25) -> Dict:
        """
        Search for tracks on Jamendo
        
        Args:
            query: Search query string
            limit: Maximum number of results (default 25)
            
        Returns:
            Dictionary with tracks array
        """
        url = f"{self.API_BASE}/tracks/"
        params = {
            'client_id': self.client_id,
            'format': 'json',
            'limit': limit,
            'search': query,
            'audioformat': 'mp32',  # Get MP3 audio files
            'include': 'musicinfo'
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            # Transform to our standard format
            tracks = []
            for track in data.get('results', []):
                # Jamendo provides full tracks, not just previews!
                if track.get('audio'):
                    tracks.append({
                        'id': f"jamendo_{track['id']}",
                        'name': track.get('name', 'Unknown Title'),
                        'preview_url': track.get('audio'),  # Full track URL!
                        'artists': [{'name': track.get('artist_name', 'Unknown Artist')}],
                        'album': {
                            'name': track.get('album_name', 'Unknown Album'),
                            'images': [{'url': track.get('album_image', '')}]
                        },
                        'duration_ms': track.get('duration', 0) * 1000,  # Convert to ms
                        'source': 'jamendo'
                    })
            
            return {'tracks': tracks}
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Jamendo API Error: {e}")
            return {'tracks': []}
    
    def search_tracks_by_tags(self, tags: str, limit: int = 25) -> Dict:
        """
        Search tracks by tags (more accurate than text search)
        
        Args:
            tags: Space-separated tags (e.g., 'happy energetic')
            limit: Maximum number of results
            
        Returns:
            Dictionary with tracks array
        """
        url = f"{self.API_BASE}/tracks/"
        params = {
            'client_id': self.client_id,
            'format': 'json',
            'limit': limit,
            'tags': tags,
            'audioformat': 'mp32',
            'include': 'musicinfo'
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            # Transform to our standard format
            tracks = []
            for track in data.get('results', []):
                if track.get('audio'):
                    tracks.append({
                        'id': f"jamendo_{track['id']}",
                        'name': track.get('name', 'Unknown Title'),
                        'preview_url': track.get('audio'),
                        'artists': [{'name': track.get('artist_name', 'Unknown Artist')}],
                        'album': {
                            'name': track.get('album_name', 'Unknown Album'),
                            'images': [{'url': track.get('album_image', '')}]
                        },
                        'duration_ms': track.get('duration', 0) * 1000,
                        'source': 'jamendo'
                    })
            
            return {'tracks': tracks}
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Jamendo API Error: {e}")
            return {'tracks': []}
    
    def search_tracks_by_mood(self, mood: str, limit: int = 25) -> Dict:
        """
        Search tracks based on mood using Jamendo's tag system
        
        Args:
            mood: Mood string (happy, sad, calm, angry, etc.)
            limit: Maximum number of results
            
        Returns:
            Dictionary with tracks array
        """
        # Map moods to Jamendo tags
        mood_tags = {
            'happy': 'happy energetic',
            'sad': 'melancholic emotional',
            'calm': 'calm peaceful',
            'angry': 'dark energetic',
            'energetic': 'energetic upbeat',
            'romantic': 'romantic emotional',
            'focused': 'calm instrumental'
        }
        
        tags = mood_tags.get(mood.lower(), mood)
        
        # Try tag search first (more accurate)
        result = self.search_tracks_by_tags(tags, limit)
        
        # If no results, fallback to text search
        if not result['tracks']:
            result = self.search_tracks(f'{mood} music', limit)
        
        return result
    
    def get_mood_recommendations(self, mood: str, limit: int = 25) -> Dict:
        """
        Get track recommendations based on mood (alias for search_tracks_by_mood)
        Maintains compatibility with Spotify interface
        """
        return self.search_tracks_by_mood(mood, limit)