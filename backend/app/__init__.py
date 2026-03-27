from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    load_dotenv()

    basedir = os.path.abspath(os.path.dirname(__file__))     
    backend_dir = os.path.dirname(basedir)                   
    project_root = os.path.dirname(backend_dir)              
    static_dist = os.path.join(project_root, "static", "dist")

    # Fallback if dist does not exist
    if not os.path.exists(static_dist):
        static_dist = os.path.join(project_root, "static")
        print("⚠ WARNING: 'dist' folder not found. Run `npm run build` in frontend.")

    print(f"STATIC FOLDER USING → {static_dist}")

    app = Flask(
        __name__,
        static_folder=static_dist,
        static_url_path=""
    )
    app.config.from_object(config_class)

    # JWT Configuration - Accept tokens from Authorization headers only
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # CORS Configuration - UPDATED FOR BETTER COMPATIBILITY
    CORS(
        app,
        resources={r"/*": {"origins": app.config["FRONTEND_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )

    # Register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.spotify_routes import spotify_bp
    from app.routes.music_routes import music_bp
    from app.routes.mood_routes import mood_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(spotify_bp, url_prefix="/api/spotify")
    app.register_blueprint(music_bp, url_prefix="/api/music")
    app.register_blueprint(mood_bp, url_prefix="/api/mood")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def serve_static(path):
        file_path = os.path.join(app.static_folder, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app
