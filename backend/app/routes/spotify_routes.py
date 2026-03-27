from flask import Blueprint, current_app, redirect, request, jsonify
from app.utils.spotify import SpotifyService
from app.utils.music_service import MusicService
from app import db
from app.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity
import time

spotify_bp = Blueprint('spotify', __name__)


@spotify_bp.route('/login', methods=['GET'])
def spotify_login():
    """Generate Spotify authorization URL."""
    svc = SpotifyService(
        current_app.config['SPOTIFY_CLIENT_ID'],
        current_app.config['SPOTIFY_CLIENT_SECRET'],
        current_app.config['SPOTIFY_REDIRECT_URI']
    )
    auth_url = svc.get_authorize_url()
    return jsonify({'auth_url': auth_url})


@spotify_bp.route('/callback', methods=['GET'])
def spotify_callback():
    """Spotify redirects here after user login."""
    code = request.args.get('code')
    if not code:
        return jsonify({'msg': 'No authorization code provided'}), 400

    svc = SpotifyService(
        current_app.config['SPOTIFY_CLIENT_ID'],
        current_app.config['SPOTIFY_CLIENT_SECRET'],
        current_app.config['SPOTIFY_REDIRECT_URI']
    )

    token_data = svc.get_user_token(code)

    # DO NOT return refresh tokens to the browser!
    return jsonify({
        'access_token': token_data.get('access_token'),
        'refresh_token': token_data.get('refresh_token'),
        'expires_in': token_data.get('expires_in')
    })


@spotify_bp.route('/link', methods=['POST'])
@jwt_required()
def spotify_link():
    """Saves Spotify tokens to the logged-in user's account."""
    data = request.get_json() or {}

    access = data.get('access_token')
    refresh = data.get('refresh_token')
    expires_in = data.get('expires_in')

    if not access:
        return jsonify({'msg': 'Missing access token'}), 400

    uid = get_jwt_identity()
    user = User.query.get(uid)

    user.spotify_access = access
    user.spotify_refresh = refresh
    user.spotify_expires_at = (time.time() + int(expires_in)) if expires_in else None

    db.session.commit()

    return jsonify({'msg': 'Spotify linked successfully'})


@spotify_bp.route('/refresh', methods=['POST'])
@jwt_required()
def spotify_refresh():
    """Refresh Spotify token if expired."""
    uid = get_jwt_identity()
    user = User.query.get(uid)

    if not user.spotify_refresh:
        return jsonify({'msg': 'No refresh token saved'}), 400

    svc = SpotifyService(
        current_app.config['SPOTIFY_CLIENT_ID'],
        current_app.config['SPOTIFY_CLIENT_SECRET'],
        current_app.config['SPOTIFY_REDIRECT_URI'],
        refresh_token=user.spotify_refresh
    )

    new_tokens = svc.refresh_user_token()

    user.spotify_access = new_tokens['access_token']
    user.spotify_expires_at = time.time() + int(new_tokens.get('expires_in', 3600))

    db.session.commit()

    return jsonify({'msg': 'Token refreshed', 'access_token': user.spotify_access})


@spotify_bp.route('/recommendations/<mood>', methods=['GET'])
def get_mood_recommendations(mood):
    """
    Get music recommendations with multi-tier fallback
    Tries: Spotify → Deezer → Jamendo
    """
    try:
        limit = request.args.get('limit', 25, type=int)
        
        # Get Jamendo client ID from config (optional)
        jamendo_id = current_app.config.get('JAMENDO_CLIENT_ID')
        
        # Initialize multi-tier music service
        music_service = MusicService(
            spotify_client_id=current_app.config['SPOTIFY_CLIENT_ID'],
            spotify_client_secret=current_app.config['SPOTIFY_CLIENT_SECRET'],
            spotify_redirect_uri=current_app.config['SPOTIFY_REDIRECT_URI'],
            jamendo_client_id=jamendo_id
        )
        
        # Get recommendations with fallback
        result = music_service.get_mood_recommendations(mood, limit=limit)
        
        return jsonify({
            'success': True,
            'music': result['tracks'],
            'sources_used': result['sources_used'],
            'total_tracks': result['total_tracks'],
            'requested': result['requested']
        })
        
    except Exception as e:
        print(f"❌ Error in get_mood_recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'music': []
        }), 500

@spotify_bp.route('/test-deezer', methods=['GET'])
def test_deezer():
    """Test Deezer directly"""
    from app.utils.deezer import DeezerService
    import requests
    
    # Test 1: Direct requests call
    try:
        resp = requests.get('https://api.deezer.com/search', params={'q': 'happy music', 'limit': 5}, timeout=10)
        direct_data = resp.json()
        direct_count = len(direct_data.get('data', []))
    except Exception as e:
        direct_count = f"Error: {e}"
    
    # Test 2: Through DeezerService
    deezer = DeezerService()
    result = deezer.search_tracks('happy music', limit=5)
    service_count = len(result.get('tracks', []))
    
    return jsonify({
        'direct_request_tracks': direct_count,
        'deezer_service_tracks': service_count,
        'test': 'completed'
    })

@spotify_bp.route('/search', methods=['GET'])
def search_tracks():
    """
    Search for tracks across all services with fallback
    """
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 20, type=int)
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        # Get Jamendo client ID from config (optional)
        jamendo_id = current_app.config.get('JAMENDO_CLIENT_ID')
        
        # Initialize multi-tier music service
        music_service = MusicService(
            spotify_client_id=current_app.config['SPOTIFY_CLIENT_ID'],
            spotify_client_secret=current_app.config['SPOTIFY_CLIENT_SECRET'],
            spotify_redirect_uri=current_app.config['SPOTIFY_REDIRECT_URI'],
            jamendo_client_id=jamendo_id
        )
        
        # Search with fallback
        result = music_service.search_tracks(query, limit=limit)
        
        return jsonify({
            'success': True,
            'tracks': result['tracks'],
            'sources_used': result['sources_used'],
            'total_tracks': result['total_tracks']
        })
        
    except Exception as e:
        print(f"❌ Error in search_tracks: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'tracks': []
        }), 500