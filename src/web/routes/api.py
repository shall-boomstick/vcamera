"""API routes for AJAX operations."""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from ..routes.auth import login_required

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/upload-video', methods=['POST'])
@login_required
def upload_video():
    """Upload a video file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    video_library = current_app.video_library
    
    try:
        filename = secure_filename(file.filename)
        
        # Save to a temporary location first (not in videos/ directory)
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Upload to library (this will copy to videos/ directory)
            video = video_library.upload_video(temp_path, filename)
            
            return jsonify({
                'success': True,
                'video': {
                    'id': video.id,
                    'filename': video.filename,
                    'duration': video.duration,
                    'size': video.file_size
                }
            })
        finally:
            # Always clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/create-camera', methods=['POST'])
@login_required
def create_camera():
    """Create a new virtual camera."""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    video_ids = data.get('video_ids', [])
    auth_enabled = data.get('auth_enabled', False)
    auth_username = data.get('auth_username', '').strip() if auth_enabled else None
    auth_password = data.get('auth_password', '') if auth_enabled else None
    
    if not name:
        return jsonify({'error': 'Camera name is required'}), 400
    
    if not video_ids:
        return jsonify({'error': 'At least one video is required'}), 400
    
    camera_manager = current_app.camera_manager
    
    try:
        camera = camera_manager.create_camera(
            name=name,
            video_ids=video_ids,
            auth_enabled=auth_enabled,
            auth_username=auth_username,
            auth_password=auth_password
        )
        
        return jsonify({
            'success': True,
            'camera': {
                'id': camera.id,
                'name': camera.name,
                'rtsp_url': camera.rtsp_url,
                'status': camera.status
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/start-camera/<camera_id>', methods=['POST'])
@login_required
def start_camera(camera_id):
    """Start a camera stream."""
    camera_manager = current_app.camera_manager
    video_library = current_app.video_library
    
    try:
        from ...services.rtsp_server import get_rtsp_manager
        camera = camera_manager.get_camera(camera_id)
        rtsp_manager = get_rtsp_manager()
        rtsp_manager.start_stream(camera, video_library, camera_manager)
        
        return jsonify({'success': True, 'message': f'Camera {camera.name} started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/stop-camera/<camera_id>', methods=['POST'])
@login_required
def stop_camera(camera_id):
    """Stop a camera stream."""
    camera_manager = current_app.camera_manager
    
    try:
        from ...services.rtsp_server import get_rtsp_manager
        camera = camera_manager.get_camera(camera_id)
        rtsp_manager = get_rtsp_manager()
        rtsp_manager.stop_stream(camera_id, camera_manager)
        
        return jsonify({'success': True, 'message': f'Camera {camera.name} stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/scan-videos', methods=['POST'])
@login_required
def scan_videos():
    """Scan videos directory and add any missing videos to the library."""
    video_library = current_app.video_library
    
    try:
        added_videos = video_library.scan_and_add_missing_videos()
        
        return jsonify({
            'success': True,
            'message': f'Found and added {len(added_videos)} video(s)',
            'videos': [{
                'id': v.id,
                'filename': v.filename,
                'duration': v.duration
            } for v in added_videos]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

