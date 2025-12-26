"""Flask web application."""
from flask import Flask, session, redirect, url_for, request
from ..services.auth import AuthService
from ..services.camera_manager import CameraManagerService
from ..services.video_library import VideoLibraryService
from ..services.storage import ensure_directories

# Initialize services
ensure_directories()
video_library = VideoLibraryService()
camera_manager = CameraManagerService(video_library)
auth_service = AuthService()


def create_app():
    """Create and configure Flask application.
    
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.secret_key = 'vcamera-secret-key-change-in-production'  # TODO: Use environment variable
    
    # Make services available to routes via app context
    app.video_library = video_library
    app.camera_manager = camera_manager
    app.auth_service = auth_service
    
    # Register blueprints
    from .routes import auth, dashboard, api
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(api.bp)
    
    return app

