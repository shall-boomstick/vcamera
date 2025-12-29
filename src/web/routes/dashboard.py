"""Dashboard routes."""
from flask import Blueprint, render_template, current_app, flash
from ..routes.auth import login_required

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """Main dashboard."""
    video_library = current_app.video_library
    camera_manager = current_app.camera_manager
    
    try:
        videos = video_library.list_videos()
        cameras = camera_manager.list_cameras()
    except Exception as e:
        flash(f'Error loading data: {str(e)}', 'error')
        videos = []
        cameras = []
    
    return render_template('dashboard/index.html', videos=videos, cameras=cameras)

