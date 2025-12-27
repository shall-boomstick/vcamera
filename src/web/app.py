"""Flask web application."""
from flask import Flask, session, redirect, url_for, request
from ..services.auth import AuthService
from ..services.camera_manager import CameraManagerService
from ..services.video_library import VideoLibraryService
from ..services.storage import ensure_directories
from ..services.logger import get_logger

logger = get_logger(__name__)

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
    app.secret_key = 'vcamera-secret-key-change-in-production'

    # Make services available to routes via app context
    app.video_library = video_library
    app.camera_manager = camera_manager
    app.auth_service = auth_service

    # Register blueprints
    from .routes import auth, dashboard, api, viewer
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(viewer.bp)

    # Restore previously active camera streams on startup
    with app.app_context():
        _restore_active_streams(app)

    return app


def _restore_active_streams(app):
    """Restore RTSP streams for cameras marked as active.

    This runs on app startup to resume streams that were running before
    a server restart.
    """
    try:
        from ..services.rtsp_server import get_rtsp_manager

        cameras = camera_manager.list_cameras()
        rtsp_manager = get_rtsp_manager()

        for camera in cameras:
            if camera.status == 'active':
                logger.info(f"Restoring stream for camera {camera.name}")
                try:
                    rtsp_manager.start_stream(
                        camera, video_library, camera_manager
                    )
                    logger.info(f"Restored stream for camera {camera.name}")
                except Exception as e:
                    logger.error(
                        f"Failed to restore stream for {camera.name}: {e}"
                    )
                    # Mark camera as inactive since we couldn't restore it
                    try:
                        camera_manager.update_camera(
                            camera.id, status="inactive"
                        )
                    except Exception:
                        pass
    except Exception as e:
        logger.error(f"Error restoring active streams: {e}")

