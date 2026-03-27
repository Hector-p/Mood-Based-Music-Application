from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Spotify tokens (if user links Spotify account)
    spotify_access = db.Column(db.String, nullable=True)
    spotify_refresh = db.Column(db.String, nullable=True)
    spotify_expires_at = db.Column(db.Float, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class FavoriteTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spotify_track_id = db.Column(db.String(100), nullable=False)
    track_name = db.Column(db.String(200))
    artist_name = db.Column(db.String(200))
    album_name = db.Column(db.String(200))
    preview_url = db.Column(db.String(500))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('favorite_tracks', lazy=True))
    
    __table_args__ = (db.UniqueConstraint('user_id', 'spotify_track_id', name='unique_user_track'),)


class ListeningHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    spotify_track_id = db.Column(db.String(100), nullable=False)
    track_name = db.Column(db.String(200))
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('listening_history', lazy=True))