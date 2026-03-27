from typing import List, Dict, Optional
from app.utils.spotify import SpotifyService
from app.utils.deezer import DeezerService
from app.utils.jamendo import JamendoService

class MusicService:
    """
    Multi-tier music service with fallback system
    Tries: Spotify → Deezer → Jamendo
    """
    
    def __init__(
        self,
        spotify_client_id: str,
        spotify_client_secret: str,
        spotify_redirect_uri: str,
        jamendo_client_id: Optional[str] = None,
        spotify_user_token: Optional[str] = None,
        spotify_refresh_token: Optional[str] = None,
        spotify_token_expires_at: Optional[float] = None
    ):
        """
        Initialize multi-tier music service
        
        Args:
            spotify_client_id: Spotify client ID
            spotify_client_secret: Spotify client secret
            spotify_redirect_uri: Spotify redirect URI
            jamendo_client_id: Jamendo client ID (optional, but recommended)
            spotify_user_token: User's Spotify access token (optional)
            spotify_refresh_token: User's Spotify refresh token (optional)
            spotify_token_expires_at: Token expiration timestamp (optional)
        """
        # Initialize Spotify service
        self.spotify = SpotifyService(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            redirect_uri=spotify_redirect_uri,
            user_token=spotify_user_token,
            refresh_token=spotify_refresh_token,
            token_expires_at=spotify_token_expires_at
        )
        
        # Initialize Deezer service (no credentials needed!)
        self.deezer = DeezerService()
        
        # Initialize Jamendo service if credentials provided
        self.jamendo = None
        if jamendo_client_id:
            self.jamendo = JamendoService(client_id=jamendo_client_id)
    
    def _filter_tracks_with_preview(self, tracks: List[Dict]) -> List[Dict]:
        """
        Filter tracks to only include those with valid preview URLs
        
        Args:
            tracks: List of track dictionaries
            
        Returns:
            Filtered list with only playable tracks
        """
        return [
            track for track in tracks 
            if track.get('preview_url') and track['preview_url'] not in [None, '', 'null']
        ]
    
    def _standardize_track_format(self, tracks: List[Dict], source: str) -> List[Dict]:
        """
        Ensure all tracks follow the same format regardless of source
        
        Args:
            tracks: List of track dictionaries
            source: Source identifier (spotify, deezer, jamendo)
            
        Returns:
            Standardized track list
        """
        standardized = []
        for track in tracks:
            # Ensure source is set
            if 'source' not in track:
                track['source'] = source
            
            # Ensure all required fields exist
            standardized_track = {
                'id': track.get('id', f"{source}_unknown"),
                'name': track.get('name', 'Unknown Title'),
                'preview_url': track.get('preview_url'),
                'artists': track.get('artists', [{'name': 'Unknown Artist'}]),
                'album': track.get('album', {
                    'name': 'Unknown Album',
                    'images': [{'url': ''}]
                }),
                'duration_ms': track.get('duration_ms', 0),
                'source': track.get('source', source)
            }
            standardized.append(standardized_track)
        
        return standardized
    
    def get_mood_recommendations(self, mood: str, limit: int = 25) -> Dict:
        """
        Get track recommendations with multi-tier fallback
        
        Process:
        1. Try Spotify first (best metadata, but limited previews)
        2. If insufficient tracks, add Deezer (good coverage)
        3. If still insufficient, add Jamendo (full tracks)
        
        Args:
            mood: Mood string (happy, sad, calm, angry, etc.)
            limit: Target number of tracks to return
            
        Returns:
            Dictionary with:
                - tracks: List of track dictionaries
                - sources_used: List of sources that provided tracks
                - total_tracks: Total number of tracks returned
        """
        all_tracks = []
        sources_used = []
        
        # Tier 1: Spotify (primary source)
        print(f"🎵 Fetching from Spotify for mood: {mood}")
        try:
            spotify_result = self.spotify.get_mood_recommendations(mood, limit=50)  # Get extra
            print(f"🔍 Spotify raw result type: {type(spotify_result)}")
            print(f"🔍 Spotify result keys: {spotify_result.keys() if isinstance(spotify_result, dict) else 'Not a dict'}")
            
            spotify_tracks = spotify_result.get('tracks', [])
            print(f"🔍 Spotify returned {len(spotify_tracks)} total tracks")
            
            # Filter tracks with preview URLs
            spotify_playable = self._filter_tracks_with_preview(spotify_tracks)
            print(f"🔍 After filtering: {len(spotify_playable)} tracks with preview URLs")
            
            if spotify_playable:
                # Standardize format
                spotify_playable = self._standardize_track_format(spotify_playable, 'spotify')
                all_tracks.extend(spotify_playable)
                sources_used.append('spotify')
                print(f"✅ Spotify: Found {len(spotify_playable)} playable tracks")
            else:
                print(f"⚠️ Spotify: No tracks with preview URLs")
                
        except Exception as e:
            print(f"❌ Spotify error: {e}")
            import traceback
            traceback.print_exc()
        
        # Tier 2: Deezer (if we need more tracks)
        if len(all_tracks) < limit:
            needed = limit - len(all_tracks)
            print(f"🎵 Need {needed} more tracks, trying Deezer...")
            
            try:
                deezer_result = self.deezer.get_mood_recommendations(mood, limit=needed + 10)
                print(f"🔍 Deezer raw result type: {type(deezer_result)}")
                print(f"🔍 Deezer result keys: {deezer_result.keys() if isinstance(deezer_result, dict) else 'Not a dict'}")
                
                deezer_tracks = deezer_result.get('tracks', [])
                print(f"🔍 Deezer returned {len(deezer_tracks)} tracks")
                
                if deezer_tracks:
                    # Deezer already filters tracks with previews
                    deezer_tracks = self._standardize_track_format(deezer_tracks, 'deezer')
                    all_tracks.extend(deezer_tracks[:needed])
                    sources_used.append('deezer')
                    print(f"✅ Deezer: Added {len(deezer_tracks[:needed])} tracks")
                else:
                    print(f"⚠️ Deezer: No tracks found")
                    
            except Exception as e:
                print(f"❌ Deezer error: {e}")
                import traceback
                traceback.print_exc()
        
        # Tier 3: Jamendo (if we still need more and it's configured)
        if len(all_tracks) < limit and self.jamendo:
            needed = limit - len(all_tracks)
            print(f"🎵 Need {needed} more tracks, trying Jamendo...")
            
            try:
                jamendo_result = self.jamendo.get_mood_recommendations(mood, limit=needed + 10)
                jamendo_tracks = jamendo_result.get('tracks', [])
                
                if jamendo_tracks:
                    jamendo_tracks = self._standardize_track_format(jamendo_tracks, 'jamendo')
                    all_tracks.extend(jamendo_tracks[:needed])
                    sources_used.append('jamendo')
                    print(f"✅ Jamendo: Added {len(jamendo_tracks[:needed])} tracks")
                else:
                    print(f"⚠️ Jamendo: No tracks found")
                    
            except Exception as e:
                print(f"❌ Jamendo error: {e}")
        
        # Limit to requested amount
        final_tracks = all_tracks[:limit]
        
        print(f"🎉 Total tracks returned: {len(final_tracks)} from {sources_used}")
        
        return {
            'tracks': final_tracks,
            'sources_used': sources_used,
            'total_tracks': len(final_tracks),
            'requested': limit
        }
    
    def search_tracks(self, query: str, limit: int = 20) -> Dict:
        """
        Search tracks across all services with fallback
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            Dictionary with tracks and metadata
        """
        all_tracks = []
        sources_used = []
        
        # Try Spotify first
        try:
            spotify_result = self.spotify.search_tracks(query, limit=limit)
            spotify_tracks = spotify_result.get('tracks', {}).get('items', [])
            spotify_playable = self._filter_tracks_with_preview(spotify_tracks)
            
            if spotify_playable:
                spotify_playable = self._standardize_track_format(spotify_playable, 'spotify')
                all_tracks.extend(spotify_playable)
                sources_used.append('spotify')
        except Exception as e:
            print(f"❌ Spotify search error: {e}")
        
        # Add Deezer if needed
        if len(all_tracks) < limit:
            needed = limit - len(all_tracks)
            try:
                deezer_result = self.deezer.search_tracks(query, limit=needed)
                deezer_tracks = deezer_result.get('tracks', [])
                
                if deezer_tracks:
                    deezer_tracks = self._standardize_track_format(deezer_tracks, 'deezer')
                    all_tracks.extend(deezer_tracks[:needed])
                    sources_used.append('deezer')
            except Exception as e:
                print(f"❌ Deezer search error: {e}")
        
        # Add Jamendo if needed and available
        if len(all_tracks) < limit and self.jamendo:
            needed = limit - len(all_tracks)
            try:
                jamendo_result = self.jamendo.search_tracks(query, limit=needed)
                jamendo_tracks = jamendo_result.get('tracks', [])
                
                if jamendo_tracks:
                    jamendo_tracks = self._standardize_track_format(jamendo_tracks, 'jamendo')
                    all_tracks.extend(jamendo_tracks[:needed])
                    sources_used.append('jamendo')
            except Exception as e:
                print(f"❌ Jamendo search error: {e}")
        
        return {
            'tracks': all_tracks[:limit],
            'sources_used': sources_used,
            'total_tracks': len(all_tracks[:limit])
        }