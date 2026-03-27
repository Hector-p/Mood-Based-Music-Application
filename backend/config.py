import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change_me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'app.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change_me_jwt')
    SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID', '')
    SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET', '')
    SPOTIFY_REDIRECT_URI = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/api/spotify/callback')
    JAMENDO_CLIENT_ID = os.getenv('JAMENDO_CLIENT_ID', None)
    FRONTEND_ORIGINS = [
        origin.strip()
        for origin in os.environ.get(
            'FRONTEND_ORIGINS',
            'http://localhost:5173,http://127.0.0.1:5173'
        ).split(',')
        if origin.strip()
    ]
