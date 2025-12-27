"""Stream viewer routes."""
import os
# Prevent OpenCV from showing GUI dialogs
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
os.environ['OPENCV_VIDEOIO_PRIORITY_INTEL_MFX'] = '0'

from flask import Blueprint, render_template, current_app, Response, jsonify
from ..routes.auth import login_required
from ...services.logger import get_logger
try:
    import cv2
    # Set OpenCV to not show any GUI dialogs
    cv2.setNumThreads(1)
    CV2_AVAILABLE = True
    # Check if GStreamer backend is available
    GSTREAMER_AVAILABLE = cv2.getBuildInformation().find('GStreamer') != -1
except ImportError:
    CV2_AVAILABLE = False
    GSTREAMER_AVAILABLE = False
import threading
import time

logger = get_logger(__name__)

bp = Blueprint('viewer', __name__)

# Store active stream connections
_active_streams = {}
_stream_lock = threading.Lock()


@bp.route('/viewer/<camera_id>')
@login_required
def viewer(camera_id):
    """Stream viewer page for a camera."""
    camera_manager = current_app.camera_manager
    
    try:
        camera = camera_manager.get_camera(camera_id)
        
        # Check if camera is active and warn if not
        if camera.status != 'active':
            logger.warning(f"Viewer accessed for inactive camera {camera_id} (status: {camera.status})")
            # Still render the page, but the stream will show an error frame
        
        return render_template('viewer/stream.html', camera=camera)
    except Exception as e:
        logger.error(f"Error loading camera {camera_id} for viewer: {e}", exc_info=True)
        return f"Error loading camera: {str(e)}", 404


@bp.route('/api/stream/<camera_id>')
@login_required
def stream_proxy(camera_id):
    """Proxy RTSP stream as MJPEG for web viewing."""
    camera_manager = current_app.camera_manager
    
    try:
        camera = camera_manager.get_camera(camera_id)
        
        # Check if camera is active
        if camera.status != 'active':
            logger.warning(f"Stream request for inactive camera {camera_id} (status: {camera.status})")
            # Return error frame instead of JSON (so img tag can display it)
            error_frame = create_error_frame("Camera is not active. Please start the camera first.")
            return Response(
                (b'--frame\r\n'
                 b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n'),
                mimetype='multipart/x-mixed-replace; boundary=frame'
            )
        
        rtsp_url = camera.rtsp_url
        logger.info(f"Starting stream proxy for camera {camera_id} at {rtsp_url}")
        
        # Verify RTSP stream is actually active (but don't block if status says active)
        try:
            from ...services.rtsp_server import get_rtsp_manager
            rtsp_manager = get_rtsp_manager()
            if not rtsp_manager.is_streaming(camera_id):
                logger.warning(f"RTSP stream not active for camera {camera_id}, but camera status is {camera.status}")
                # If camera status is active but stream isn't, try to auto-start it
                if camera.status == 'active':
                    logger.info(f"Attempting to auto-start RTSP stream for camera {camera_id}")
                    try:
                        video_library = current_app.video_library
                        rtsp_manager.start_stream(camera, video_library, camera_manager)
                        # Wait a moment for stream to initialize
                        time.sleep(2.0)
                        if rtsp_manager.is_streaming(camera_id):
                            logger.info(f"Successfully auto-started RTSP stream for camera {camera_id}")
                        else:
                            logger.warning(f"Auto-start attempted but stream still not active")
                    except Exception as start_error:
                        logger.error(f"Failed to auto-start stream: {start_error}", exc_info=True)
                        # Continue to try connecting anyway - might work
                else:
                    # Camera status is not active, show error
                    error_frame = create_error_frame(
                        "RTSP stream is not active.\n\n"
                        "The camera status shows 'active' but the RTSP stream\n"
                        "has not been started. Please restart the camera."
                    )
                    return Response(
                        (b'--frame\r\n'
                         b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n'),
                        mimetype='multipart/x-mixed-replace; boundary=frame'
                    )
        except Exception as e:
            logger.warning(f"Could not verify RTSP stream status: {e}")
            # Continue anyway - might still work
        
        # Handle authentication in RTSP URL if needed
        if camera.auth_enabled and camera.auth_username and camera.auth_password_rtsp:
            # Decrypt password and add to RTSP URL
            import base64
            try:
                rtsp_password = base64.b64decode(camera.auth_password_rtsp.encode()).decode()
                # Build RTSP URL with authentication
                from urllib.parse import urlparse, urlunparse
                parsed = urlparse(rtsp_url)
                # Create authenticated URL: rtsp://username:password@host:port/path
                netloc = f"{camera.auth_username}:{rtsp_password}@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                authenticated_url = urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                rtsp_url = authenticated_url
            except Exception as e:
                logger.error(f"Failed to decrypt RTSP password: {e}")
                # Fall back to URL without auth
        
        def generate_frames():
            """Generate MJPEG frames from RTSP stream."""
            if not CV2_AVAILABLE:
                error_frame = create_error_frame("OpenCV not available")
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
                return
            
            cap = None
            try:
                logger.info(f"Attempting to connect to RTSP stream: {rtsp_url}")
                
                # Quick connection test - verify RTSP server is responding
                # Note: This test may fail even if server is running due to RTSP protocol requirements
                # We'll continue anyway and let the actual RTSP connection attempt determine success
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(rtsp_url)
                    import socket
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.settimeout(1.0)  # Shorter timeout
                    result = test_socket.connect_ex((parsed.hostname or 'localhost', parsed.port or 8554))
                    test_socket.close()
                    if result == 0:
                        logger.info("RTSP server port is reachable")
                    else:
                        logger.debug(f"Socket test failed (result={result}), but continuing - RTSP may still work")
                except Exception as e:
                    logger.debug(f"RTSP server connection test failed: {e} (this is often normal, continuing)")
                    # Continue anyway - RTSP protocol is more complex than simple socket test
                
                # Give RTSP server a moment to be ready (if stream was just started)
                try:
                    from ...services.rtsp_server import get_rtsp_manager
                    rtsp_manager = get_rtsp_manager()
                    if rtsp_manager.is_streaming(camera_id):
                        logger.info("RTSP stream is active")
                    else:
                        logger.warning("RTSP stream is not active, but camera status is active")
                except Exception as e:
                    logger.debug(f"Error checking stream status: {e}")
                
                # Try direct OpenCV RTSP connection (simple and reliable)
                logger.info(f"Connecting to RTSP stream: {rtsp_url}")
                cap = cv2.VideoCapture(rtsp_url)

                if cap.isOpened():
                    # Wait for first frame with retries
                    for attempt in range(10):
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            logger.info("RTSP stream connected successfully")
                            break
                        time.sleep(0.3)
                    else:
                        logger.warning("Stream opened but no frames available")
                        cap.release()
                        cap = None
                else:
                    logger.warning("Failed to open RTSP stream")
                    cap = None
                
                if not cap or not cap.isOpened():
                    logger.error(f"Failed to open RTSP stream with any backend after retries: {rtsp_url}")
                    error_frame = create_error_frame(
                        f"Cannot connect to RTSP stream\n\n"
                        f"URL: {rtsp_url}\n\n"
                        f"Troubleshooting:\n"
                        f"1. Verify camera is started (status = active)\n"
                        f"2. Test RTSP URL: ffplay {rtsp_url}\n"
                        f"3. Check RTSP server is running\n"
                        f"4. Verify network connectivity\n"
                        f"5. Wait 5-10 seconds after starting camera"
                    )
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
                    return
                
                logger.info(f"RTSP stream opened successfully: {rtsp_url}")
                
                # Try to read a frame to verify connection (with retries)
                test_retries = 10
                test_success = False
                for i in range(test_retries):
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None and test_frame.size > 0:
                        test_success = True
                        logger.info(f"Successfully verified RTSP stream connection (attempt {i+1})")
                        break
                    time.sleep(0.3)  # Wait a bit between retries
                
                if not test_success:
                    logger.warning("RTSP stream opened but cannot read frames after retries")
                    error_frame = create_error_frame(
                        "RTSP stream connected but no frames available.\n\n"
                        "Possible causes:\n"
                        "1. Stream is still initializing (wait 5-10 seconds)\n"
                        "2. Video file is corrupted or unreadable\n"
                        "3. RTSP server issue\n\n"
                        "Try refreshing the page."
                    )
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
                    # Continue anyway - might work after a few frames
                
                logger.info(f"Starting frame generation for RTSP stream: {rtsp_url}")
                
                frame_count = 0
                consecutive_failures = 0
                max_failures = 10
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        consecutive_failures += 1
                        if consecutive_failures >= max_failures:
                            logger.error(f"Failed to read {max_failures} consecutive frames from RTSP stream")
                            error_frame = create_error_frame("Stream connection lost. Trying to reconnect...")
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
                            # Try to reopen the stream
                            cap.release()
                            time.sleep(1)
                            cap = cv2.VideoCapture(rtsp_url)
                            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                            if not cap.isOpened():
                                error_frame = create_error_frame("Cannot reconnect to RTSP stream")
                                yield (b'--frame\r\n'
                                       b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
                                break
                            consecutive_failures = 0
                        else:
                            time.sleep(0.1)  # Brief pause before retry
                        continue
                    
                    # Reset failure counter on successful read
                    consecutive_failures = 0
                    frame_count += 1
                    
                    # Encode frame as JPEG
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if not ret:
                        logger.warning("Failed to encode frame as JPEG")
                        continue
                    
                    frame_bytes = buffer.tobytes()
                    
                    # Yield MJPEG frame
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                    # Small delay to control frame rate
                    time.sleep(0.033)  # ~30 fps
                    
            except Exception as e:
                # Send error frame
                logger.error(f"Error in stream generation: {e}", exc_info=True)
                error_frame = create_error_frame(f"Stream error: {str(e)}")
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n')
            finally:
                if cap:
                    cap.release()
                    logger.info(f"Released RTSP stream connection for camera {camera_id}")
        
        return Response(
            generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
        
    except Exception as e:
        logger.error(f"Error in stream_proxy for camera {camera_id}: {e}", exc_info=True)
        # Return error frame instead of JSON
        error_frame = create_error_frame(f"Server error: {str(e)}")
        return Response(
            (b'--frame\r\n'
             b'Content-Type: image/jpeg\r\n\r\n' + error_frame + b'\r\n'),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )


def create_error_frame(message):
    """Create a JPEG frame with error message."""
    try:
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple error image
        img = Image.new('RGB', (640, 480), color='black')
        draw = ImageDraw.Draw(img)
        
        # Try to use a default font, fallback to basic if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Draw error message
        text = f"Stream Error: {message}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((640 - text_width) // 2, (480 - text_height) // 2)
        draw.text(position, text, fill='white', font=font)
        
        # Convert to numpy array then to bytes
        img_array = np.array(img)
        if CV2_AVAILABLE:
            _, buffer = cv2.imencode('.jpg', img_array)
            return buffer.tobytes()
        else:
            # Fallback: return a minimal valid JPEG using PIL
            import io
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            return buffer.getvalue()
    except Exception:
        # Ultimate fallback: return a minimal black JPEG
        return b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' $"#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x01\xe0\x02\x80\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xff\xd9'

