import requests
from typing import Optional, List, Dict
import time

class DeezerService:
    """
    Deezer API Service - No authentication required for basic searches!
    Provides 30-second preview URLs for tracks.
    """
    API_BASE = 'https://api.deezer.com'
    
    def __init__(self):
        """Initialize Deezer service - no credentials needed!"""
        print("🔧 DeezerService initialized")
    
    def search_tracks(self, query: str, limit: int = 25) -> Dict:
        """
        Search for tracks on Deezer
        
        Args:
            query: Search query string
            limit: Maximum number of results (default 25)
            
        Returns:
            Dictionary with tracks array
        """
        url = f"{self.API_BASE}/search"
        params = {
            'q': query,
            'limit': limit
        }
        
        print(f"🔍 DEEZER search_tracks: query='{query}', limit={limit}")
        
        try:
            # Add headers to mimic a real browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            
            # Debug the actual URL being called
            print(f"🔍 DEEZER Actual URL called: {resp.url}")
            print(f"🔍 DEEZER Response status: {resp.status_code}")
            
            resp.raise_for_status()
            data = resp.json()
            
            # Debug the response structure
            print(f"🔍 DEEZER Response keys: {data.keys()}")
            
            raw_tracks = data.get('data', [])
            print(f"🔍 Deezer API returned {len(raw_tracks)} raw tracks")
            
            # Check for API errors
            if 'error' in data:
                print(f"❌ Deezer API Error: {data['error']}")
                return {'tracks': []}
            
            # Debug: print first track if available
            if raw_tracks:
                print(f"🔍 First track example: {raw_tracks[0].get('title')} by {raw_tracks[0].get('artist', {}).get('name')}")
                print(f"🔍 Has preview? {bool(raw_tracks[0].get('preview'))}")
            else:
                print(f"⚠️ DEEZER: No tracks in 'data' field. Full response: {data}")
            
            # Transform to our standard format
            tracks = []
            for track in raw_tracks:
                # Only include tracks with preview URLs
                if track.get('preview'):
                    tracks.append({
                        'id': f"deezer_{track['id']}",
                        'name': track.get('title', 'Unknown Title'),
                        'preview_url': track.get('preview'),  # 30-second preview
                        'artists': [{'name': track.get('artist', {}).get('name', 'Unknown Artist')}],
                        'album': {
                            'name': track.get('album', {}).get('title', 'Unknown Album'),
                            'images': [{'url': track.get('album', {}).get('cover_xl', '')}]
                        },
                        'duration_ms': track.get('duration', 0) * 1000,  # Convert to ms
                        'source': 'deezer'
                    })
            
            print(f"✅ Deezer processed {len(tracks)} tracks with valid previews")
            return {'tracks': tracks}
            
        except requests.exceptions.Timeout:
            print(f"❌ Deezer API Timeout after 10 seconds")
            return {'tracks': []}
        except requests.exceptions.RequestException as e:
            print(f"❌ Deezer API Error: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"❌ Response status: {e.response.status_code}")
                print(f"❌ Response body: {e.response.text[:500]}")
            import traceback
            traceback.print_exc()
            return {'tracks': []}
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return {'tracks': []}
    
    def search_tracks_by_mood(self, mood: str, limit: int = 25) -> Dict:
        """
        Search tracks based on mood
        
        Args:
            mood: Mood string (happy, sad, calm, angry, etc.)
            limit: Maximum number of results
            
        Returns:
            Dictionary with tracks array
        """
        print(f"🔍 DEEZER search_tracks_by_mood: Called with mood='{mood}', limit={limit}")
        
        # Simplified mood queries - shorter and more effective
        mood_queries = {
            'happy': 'happy pop dance',
            'sad': 'sad emotional',
            'calm': 'calm chill',
            'angry': 'rock metal',
            'energetic': 'energetic workout',
            'romantic': 'romantic love',
            'focused': 'focus instrumental'
        }
        
        query = mood_queries.get(mood.lower(), mood)
        print(f"🔍 DEEZER search_tracks_by_mood: Mapped to query='{query}'")
        
        result = self.search_tracks(query, limit)
        print(f"🔍 DEEZER search_tracks_by_mood: Returning {len(result.get('tracks', []))} tracks")
        
        return result
    
    def get_mood_recommendations(self, mood: str, limit: int = 25) -> Dict:
        """
        Get track recommendations based on mood (alias for search_tracks_by_mood)
        Maintains compatibility with Spotify interface
        """
        print(f"🔍 DEEZER get_mood_recommendations: Called with mood='{mood}', limit={limit}")
        return self.search_tracks_by_mood(mood, limit)
    
    def test_connection(self) -> bool:
        """
        Test if Deezer API is accessible
        
        Returns:
            True if API is responding, False otherwise
        """
        try:
            resp = requests.get(f"{self.API_BASE}/chart", timeout=5)
            resp.raise_for_status()
            print("✅ Deezer API connection successful")
            return True
        except Exception as e:
            print(f"❌ Deezer API connection failed: {e}")
            return False


# Quick test function
if __name__ == "__main__":
    print("Testing Deezer Service...")
    service = DeezerService()
    
    # Test connection
    service.test_connection()
    
    # Test search
    print("\n--- Testing search ---")
    result = service.search_tracks("happy", limit=5)
    print(f"Found {len(result['tracks'])} tracks")
    
    if result['tracks']:
        print(f"First track: {result['tracks'][0]['name']} by {result['tracks'][0]['artists'][0]['name']}")
        print(f"Preview URL: {result['tracks'][0]['preview_url']}")