"""API routes for AJAX operations."""
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from ..routes.auth import login_required
from ...services.logger import get_logger

logger = get_logger(__name__)

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/upload-video', methods=['POST'])
@login_required
def upload_video():
    """Upload a video file."""
    if 'file' not in request.files:
        logger.warning("Upload attempt with no file provided")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("Upload attempt with empty filename")
        return jsonify({'error': 'No file selected'}), 400
    
    video_library = current_app.video_library
    
    try:
        filename = secure_filename(file.filename)
        logger.info(f"Uploading video: {filename}")
        
        # Save to a temporary location first (not in videos/ directory)
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Upload to library (this will copy to videos/ directory)
            video = video_library.upload_video(temp_path, filename)
            
            logger.info(f"Video uploaded successfully: {video.id} ({filename})")
            
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
        logger.error(f"Video upload failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/camera/<camera_id>', methods=['GET'])
@login_required
def get_camera(camera_id):
    """Get camera details."""
    camera_manager = current_app.camera_manager
    
    try:
        camera = camera_manager.get_camera(camera_id)
        return jsonify({
            'success': True,
            'camera': {
                'id': camera.id,
                'name': camera.name,
                'video_ids': camera.video_ids,
                'rtsp_url': camera.rtsp_url,
                'status': camera.status,
                'auth_enabled': camera.auth_enabled,
                'auth_username': camera.auth_username
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/videos', methods=['GET'])
@login_required
def list_videos():
    """List all videos."""
    video_library = current_app.video_library
    
    try:
        videos = video_library.list_videos()
        return jsonify({
            'success': True,
            'videos': [{
                'id': v.id,
                'filename': v.filename,
                'duration': v.duration
            } for v in videos]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/cameras', methods=['GET'])
@login_required
def list_cameras():
    """List all cameras."""
    camera_manager = current_app.camera_manager
    
    try:
        cameras = camera_manager.list_cameras()
        return jsonify({
            'success': True,
            'cameras': [{
                'id': c.id,
                'name': c.name,
                'video_ids': c.video_ids,
                'rtsp_url': c.rtsp_url,
                'status': c.status,
                'auth_enabled': c.auth_enabled,
                'auth_username': c.auth_username
            } for c in cameras]
        })
    except Exception as e:
        logger.error(f"Failed to list cameras: {e}", exc_info=True)
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
        
        # Get updated camera info
        camera = camera_manager.get_camera(camera_id)
        
        return jsonify({
            'success': True, 
            'message': f'Camera {camera.name} started',
            'rtsp_url': camera.rtsp_url
        })
    except Exception as e:
        logger.error(f"Failed to start camera {camera_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/stop-camera/<camera_id>', methods=['POST'])
@login_required
def stop_camera(camera_id):
    """Stop a camera stream."""
    camera_manager = current_app.camera_manager
    
    try:
        from ...services.rtsp_server import get_rtsp_manager
        from ...services.exceptions import StreamNotFoundError
        camera = camera_manager.get_camera(camera_id)
        rtsp_manager = get_rtsp_manager()
        
        # Check if stream is actually active before trying to stop
        if rtsp_manager.is_streaming(camera_id):
            rtsp_manager.stop_stream(camera_id, camera_manager)
        else:
            # Stream not active, just update camera status
            logger.info(f"Stream not active for camera {camera_id}, updating status only")
            camera_manager.update_camera(camera_id, status="inactive")
        
        return jsonify({'success': True, 'message': f'Camera {camera.name} stopped'})
    except StreamNotFoundError:
        # Stream not found, just update status
        try:
            camera = camera_manager.get_camera(camera_id)
            camera_manager.update_camera(camera_id, status="inactive")
            return jsonify({'success': True, 'message': f'Camera {camera.name} stopped (stream was not active)'})
        except Exception as e:
            logger.error(f"Failed to update camera status: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Failed to stop camera {camera_id}: {e}", exc_info=True)
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


@bp.route('/update-camera/<camera_id>', methods=['POST'])
@login_required
def update_camera(camera_id):
    """Update camera configuration."""
    data = request.get_json()
    camera_manager = current_app.camera_manager
    
    try:
        # Extract update fields
        name = data.get('name', '').strip() if 'name' in data else None
        video_ids = data.get('video_ids') if 'video_ids' in data else None
        auth_enabled = data.get('auth_enabled') if 'auth_enabled' in data else None
        auth_username = data.get('auth_username', '').strip() if 'auth_username' in data else None
        auth_password = data.get('auth_password', '') if 'auth_password' in data else None
        
        # Validate name if provided
        if name is not None and not name:
            return jsonify({'error': 'Camera name cannot be empty'}), 400
        
        # Validate video_ids if provided
        if video_ids is not None and not video_ids:
            return jsonify({'error': 'At least one video is required'}), 400
        
        # Update camera
        camera = camera_manager.update_camera(
            camera_id=camera_id,
            name=name,
            video_ids=video_ids,
            auth_enabled=auth_enabled,
            auth_username=auth_username,
            auth_password=auth_password
        )
        
        return jsonify({
            'success': True,
            'message': f'Camera {camera.name} updated successfully',
            'camera': {
                'id': camera.id,
                'name': camera.name,
                'rtsp_url': camera.rtsp_url,
                'status': camera.status,
                'auth_enabled': camera.auth_enabled
            }
        })
    except Exception as e:
        logger.error(f"Failed to update camera {camera_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/delete-camera/<camera_id>', methods=['POST'])
@login_required
def delete_camera(camera_id):
    """Delete a camera."""
    camera_manager = current_app.camera_manager
    
    try:
        from ...services.rtsp_server import get_rtsp_manager
        
        # Stop camera if active
        camera = camera_manager.get_camera(camera_id)
        if camera.status == 'active':
            try:
                rtsp_manager = get_rtsp_manager()
                rtsp_manager.stop_stream(camera_id, camera_manager)
                logger.info(f"Stopped camera {camera_id} before deletion")
            except Exception as e:
                logger.warning(f"Failed to stop camera before deletion: {e}")
        
        # Delete camera
        camera_manager.delete_camera(camera_id)
        
        logger.info(f"Camera {camera_id} deleted successfully")
        return jsonify({
            'success': True,
            'message': f'Camera {camera.name} deleted successfully'
        })
    except Exception as e:
        logger.error(f"Failed to delete camera {camera_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/delete-video/<video_id>', methods=['POST'])
@login_required
def delete_video(video_id):
    """Delete a video from the library."""
    video_library = current_app.video_library
    camera_manager = current_app.camera_manager
    
    try:
        video = video_library.get_video(video_id)
        video_library.delete_video(video_id, camera_manager)
        
        logger.info(f"Video {video_id} ({video.filename}) deleted successfully")
        return jsonify({
            'success': True,
            'message': f'Video {video.filename} deleted successfully'
        })
    except Exception as e:
        logger.error(f"Failed to delete video {video_id}: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/rtsp-server-info', methods=['GET'])
@login_required
def rtsp_server_info():
    """Get RTSP server information for debugging."""
    try:
        from ...services.rtsp_server import get_rtsp_manager
        rtsp_manager = get_rtsp_manager()
        info = rtsp_manager.get_server_info()

        # Get active camera streams
        active_cameras = []
        for camera_id in info['active_streams']:
            try:
                camera = current_app.camera_manager.get_camera(camera_id)
                active_cameras.append({
                    'id': camera_id,
                    'name': camera.name,
                    'rtsp_url': camera.rtsp_url,
                    'status': camera.status
                })
            except Exception:
                active_cameras.append({
                    'id': camera_id,
                    'error': 'Camera not found'
                })

        info['active_cameras'] = active_cameras
        return jsonify({'success': True, 'info': info})
    except Exception as e:
        logger.error(f"Error getting RTSP server info: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/sync-camera-status/<camera_id>', methods=['POST'])
@login_required
def sync_camera_status(camera_id):
    """Sync camera status with actual RTSP stream state."""
    camera_manager = current_app.camera_manager
    
    try:
        from ...services.rtsp_server import get_rtsp_manager
        camera = camera_manager.get_camera(camera_id)
        rtsp_manager = get_rtsp_manager()
        
        is_streaming = rtsp_manager.is_streaming(camera_id)
        
        # Update camera status to match actual stream state
        if is_streaming and camera.status != 'active':
            camera_manager.update_camera(camera_id, status="active")
            logger.info(f"Synced camera {camera_id} status to 'active' (stream is running)")
        elif not is_streaming and camera.status == 'active':
            camera_manager.update_camera(camera_id, status="inactive")
            logger.info(f"Synced camera {camera_id} status to 'inactive' (stream is not running)")
        
        # Get updated camera
        camera = camera_manager.get_camera(camera_id)
        
        return jsonify({
            'success': True,
            'message': 'Camera status synced',
            'camera': {
                'id': camera.id,
                'name': camera.name,
                'status': camera.status,
                'rtsp_stream_active': is_streaming
            }
        })
    except Exception as e:
        logger.error(f"Failed to sync camera status {camera_id}: {e}",
                     exc_info=True)
        return jsonify({'error': str(e)}), 500


@bp.route('/test-rtsp/<camera_id>', methods=['GET'])
@login_required
def test_rtsp_stream(camera_id):
    """Test RTSP stream connectivity for debugging."""
    camera_manager = current_app.camera_manager

    try:
        from ...services.rtsp_server import get_rtsp_manager
        camera = camera_manager.get_camera(camera_id)
        rtsp_manager = get_rtsp_manager()

        # Check mount point registration
        mount_point_registered = rtsp_manager.is_mount_point_registered(
            camera_id
        )

        mount_path = f"/camera/{camera_id}"
        result = {
            'camera_id': camera_id,
            'camera_name': camera.name,
            'camera_status': camera.status,
            'rtsp_url': camera.rtsp_url,
            'stream_active': rtsp_manager.is_streaming(camera_id),
            'mount_point_registered': mount_point_registered,
            'mount_path': mount_path,
            'server_info': rtsp_manager.get_server_info()
        }

        if not mount_point_registered and camera.status == 'active':
            result['warning'] = (
                'Camera status is active but mount point is not registered. '
                'Try stopping and restarting the camera.'
            )

        # Test GStreamer pipeline
        import subprocess
        test_cmd = (
            f"timeout 5 gst-launch-1.0 rtspsrc location={camera.rtsp_url} "
            "latency=0 ! fakesink 2>&1"
        )
        try:
            proc = subprocess.run(
                test_cmd, shell=True, capture_output=True, text=True
            )
            result['gst_test'] = {
                'returncode': proc.returncode,
                'stdout': proc.stdout[:500] if proc.stdout else '',
                'stderr': proc.stderr[:500] if proc.stderr else ''
            }
        except Exception as e:
            result['gst_test'] = {'error': str(e)}

        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"RTSP test failed: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

