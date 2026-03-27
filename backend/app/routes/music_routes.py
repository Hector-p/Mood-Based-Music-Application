from flask import Blueprint, request, jsonify, current_app
from app.utils.spotify import SpotifyService
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, FavoriteTrack, ListeningHistory
from app import db
from datetime import datetime

music_bp = Blueprint("music", __name__)


# -------------------------------------------------
# INTERNAL: GET PROPER SPOTIFY SERVICE FOR A USER
# -------------------------------------------------
def _get_service_for_user():
    """
    Returns a SpotifyService instance.
    If user is logged in & has personal Spotify tokens → use them.
    Otherwise → use app-level token.
    """

    user_id = None
    try:
        user_id = get_jwt_identity()
    except Exception:
        user_id = None

    # Logged-in user with Spotify connection
    if user_id:
        user = User.query.get(user_id)
        if user and user.spotify_access:
            return SpotifyService(
                current_app.config.get("SPOTIFY_CLIENT_ID"),
                current_app.config.get("SPOTIFY_CLIENT_SECRET"),
                current_app.config.get("SPOTIFY_REDIRECT_URI"),
                user_token=user.spotify_access,
                refresh_token=user.spotify_refresh,
                token_expires_at=user.spotify_expires_at
            )

    # Fallback app-only Spotify token
    svc = SpotifyService(
        current_app.config.get("SPOTIFY_CLIENT_ID"),
        current_app.config.get("SPOTIFY_CLIENT_SECRET"),
        current_app.config.get("SPOTIFY_REDIRECT_URI")
    )
    svc.get_app_token()
    return svc


# -------------------------------------------------
# HELPER: Normalize Spotify track objects for React
# -------------------------------------------------
def format_track(item):
    """Ensures consistent track structure for frontend."""

    if not isinstance(item, dict):
        return None

    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "preview_url": item.get("preview_url"),
        "artists": [a["name"] for a in item.get("artists", [])],
        "album": item.get("album", {}),
        "external_url": item.get("external_urls", {}).get("spotify")
        if isinstance(item.get("external_urls"), dict)
        else None
    }


# -------------------------------------------------
# SEARCH
# -------------------------------------------------
@music_bp.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "happy")
    limit = int(request.args.get("limit", 20))

    svc = _get_service_for_user()
    res = svc.search_tracks(q, limit=limit)

    items = res.get("tracks", {}).get("items", [])
    tracks = [format_track(item) for item in items if format_track(item)]

    return jsonify({"tracks": tracks})


# -------------------------------------------------
# RECOMMEND (MOOD-BASED) - FIXED VERSION
# -------------------------------------------------
@music_bp.route("/recommend", methods=["GET"])
def recommend():
    """Get mood-based music recommendations using Spotify's recommendation API"""
    mood = request.args.get("mood", "happy")
    limit = int(request.args.get("limit", 25))
    
    print(f"🎵 Getting recommendations for mood: {mood}, limit: {limit}")

    try:
        svc = _get_service_for_user()
        
        # Use get_mood_recommendations for better results
        res = svc.get_mood_recommendations(mood, limit=limit)
        
        print(f"📦 Spotify API response type: {type(res)}")
        
        # Extract tracks from recommendations response
        if isinstance(res, dict):
            items = res.get("tracks", [])
        elif isinstance(res, list):
            items = res
        else:
            items = []
        
        print(f"🎼 Found {len(items)} tracks")
        
        tracks = [format_track(item) for item in items if format_track(item)]
        
        print(f"✅ Returning {len(tracks)} formatted tracks")
        
        return jsonify({"tracks": tracks}), 200
        
    except Exception as e:
        print(f"❌ Error in recommend endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Fallback to search if recommendations fail
        try:
            print(f"⚠️ Falling back to search_tracks_by_mood")
            svc = _get_service_for_user()
            res = svc.search_tracks_by_mood(mood, limit=limit)
            
            items = res.get("tracks", {}).get("items", [])
            tracks = [format_track(item) for item in items if format_track(item)]
            
            return jsonify({"tracks": tracks}), 200
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {str(fallback_error)}")
            return jsonify({"error": str(e), "tracks": []}), 500


# -------------------------------------------------
# MOOD RECOMMENDATIONS (POST) - Alternative endpoint
# -------------------------------------------------
@music_bp.route('/mood-recommendations', methods=['POST'])
def mood_recommendations():
    """
    Get music recommendations based on detected mood
    Expects: { "mood": "happy/sad/angry/calm", "limit": 25 }
    """
    try:
        data = request.get_json()
        mood = data.get('mood', 'calm')
        limit = data.get('limit', 25)
        
        print(f"🎵 POST mood-recommendations: {mood}")
        
        # Get Spotify service
        svc = _get_service_for_user()
        
        # Get mood-based recommendations
        result = svc.get_mood_recommendations(mood, limit)
        
        # Format tracks
        tracks = []
        for track in result.get('tracks', []):
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'album': {
                    'name': track['album']['name'],
                    'cover_small': track['album']['images'][-1]['url'] if track['album']['images'] else None,
                    'cover_medium': track['album']['images'][1]['url'] if len(track['album']['images']) > 1 else None,
                    'cover_large': track['album']['images'][0]['url'] if track['album']['images'] else None,
                },
                'preview_url': track.get('preview_url'),
                'external_url': track['external_urls']['spotify'],
                'duration_ms': track['duration_ms']
            })
        
        return jsonify({
            'mood': mood,
            'tracks': tracks,
            'total': len(tracks)
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting mood recommendations: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# -------------------------------------------------
# FAVORITES — GET
# -------------------------------------------------
@music_bp.route("/favorites", methods=["GET"])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    favorites = FavoriteTrack.query.filter_by(user_id=user_id).order_by(FavoriteTrack.added_at.desc()).all()

    tracks = []
    for fav in favorites:
        tracks.append({
            "id": fav.spotify_track_id,
            "name": fav.track_name,
            "artists": [fav.artist_name],
            "album": {"name": fav.album_name},
            "preview_url": fav.preview_url,
            "is_favorite": True
        })

    return jsonify({"tracks": tracks})


# -------------------------------------------------
# FAVORITES — ADD
# -------------------------------------------------
@music_bp.route("/favorites", methods=["POST"])
@jwt_required()
def add_favorite():
    user_id = get_jwt_identity()
    data = request.get_json()

    track_id = data.get("track_id")
    if not track_id:
        return jsonify({"msg": "Track ID is required"}), 400

    existing = FavoriteTrack.query.filter_by(user_id=user_id, spotify_track_id=track_id).first()
    if existing:
        return jsonify({"msg": "Track is already in favorites"}), 409

    favorite = FavoriteTrack(
        user_id=user_id,
        spotify_track_id=track_id,
        track_name=data.get("track_name"),
        artist_name=data.get("artist_name"),
        album_name=data.get("album_name"),
        preview_url=data.get("preview_url")
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({"msg": "Added to favorites", "track_id": track_id}), 201


# -------------------------------------------------
# FAVORITES — DELETE
# -------------------------------------------------
@music_bp.route("/favorites/<track_id>", methods=["DELETE"])
@jwt_required()
def remove_favorite(track_id):
    user_id = get_jwt_identity()

    favorite = FavoriteTrack.query.filter_by(user_id=user_id, spotify_track_id=track_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"msg": "Removed from favorites"}), 200


# -------------------------------------------------
# HISTORY — ADD
# -------------------------------------------------
@music_bp.route("/history", methods=["POST"])
@jwt_required()
def add_to_history():
    user_id = get_jwt_identity()
    data = request.get_json()

    track_id = data.get("track_id")
    if not track_id:
        return jsonify({"msg": "Track ID is required"}), 400

    history = ListeningHistory(
        user_id=user_id,
        spotify_track_id=track_id,
        track_name=data.get("track_name")
    )

    db.session.add(history)
    db.session.commit()

    return jsonify({"msg": "Added to history"}), 201


# -------------------------------------------------
# HISTORY — GET
# -------------------------------------------------
@music_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    limit = int(request.args.get("limit", 50))

    history = ListeningHistory.query.filter_by(user_id=user_id) \
        .order_by(ListeningHistory.played_at.desc()) \
        .limit(limit).all()

    tracks = [{
        "id": item.spotify_track_id,
        "name": item.track_name,
        "played_at": item.played_at.isoformat()
    } for item in history]

    return jsonify({"history": tracks})