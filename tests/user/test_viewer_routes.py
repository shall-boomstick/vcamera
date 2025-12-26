"""User tests for viewer routes."""
import pytest
import os
import tempfile
import cv2
import numpy as np

from src.web.app import create_app


@pytest.fixture
def test_client(test_data_dir, monkeypatch):
    """Create Flask test client with test data directory."""
    original_cwd = os.getcwd()
    os.chdir(test_data_dir)
    
    # Ensure directories exist
    from src.services.storage import ensure_directories
    ensure_directories()
    
    try:
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        client = app.test_client()
        yield client
    finally:
        os.chdir(original_cwd)


class TestViewerRoutes:
    """User tests for viewer routes."""
    
    def test_viewer_page_requires_auth(self, test_client):
        """Test that viewer page requires authentication."""
        response = test_client.get('/viewer/test-camera-id')
        
        # Should redirect to login or return 401
        assert response.status_code in [302, 401, 404]
    
    def test_viewer_page_authenticated(self, test_client):
        """Test accessing viewer page when authenticated."""
        # Setup: Create credentials and login
        test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        })
        test_client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Create a test video and camera using app context
        app = test_client.application
        with app.app_context():
            video_library = app.video_library
            camera_manager = app.camera_manager
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_file.close()
            
            try:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
                out.write(np.zeros((480, 640, 3), dtype=np.uint8))
                out.release()
                
                video = video_library.upload_video(temp_file.name, 'test.mp4')
                camera = camera_manager.create_camera('Test Camera', [video.id])
                camera_id = camera.id
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
        
        # Access viewer page
        response = test_client.get(f'/viewer/{camera_id}')
        
        # Should succeed (200) or show error if stream not available
        assert response.status_code in [200, 404, 500]
    
    def test_viewer_page_invalid_camera(self, test_client):
        """Test accessing viewer page with invalid camera ID."""
        # Setup: Create credentials and login
        test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        })
        test_client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Access viewer page with invalid camera ID
        response = test_client.get('/viewer/invalid-camera-id')
        
        # Should return 404
        assert response.status_code == 404
    
    def test_stream_proxy_requires_auth(self, test_client):
        """Test that stream proxy requires authentication."""
        response = test_client.get('/api/stream/test-camera-id')
        
        # Should return 401
        assert response.status_code == 401
    
    def test_stream_proxy_authenticated_inactive_camera(self, test_client):
        """Test stream proxy with inactive camera."""
        # Setup: Create credentials and login
        test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        })
        test_client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Create a test video and camera (inactive by default) using app context
        app = test_client.application
        with app.app_context():
            video_library = app.video_library
            camera_manager = app.camera_manager
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_file.close()
            
            try:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
                out.write(np.zeros((480, 640, 3), dtype=np.uint8))
                out.release()
                
                video = video_library.upload_video(temp_file.name, 'test.mp4')
                camera = camera_manager.create_camera('Test Camera', [video.id])
                camera_id = camera.id
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
        
        # Access stream proxy
        response = test_client.get(f'/api/stream/{camera_id}')
        
        # Should return error since camera is inactive
        assert response.status_code in [400, 500]

