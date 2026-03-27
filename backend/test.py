from app.utils.deezer import DeezerService

deezer = DeezerService()
result = deezer.search_tracks('happy music', limit=5)
print(f"Tracks found: {len(result['tracks'])}")
print(f"First track: {result['tracks'][0] if result['tracks'] else 'None'}")