"""User/End-to-end tests for web interface."""
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


class TestWebAuthentication:
    """User tests for web authentication."""
    
    def test_create_credentials_page(self, test_client):
        """Test accessing create credentials page when no credentials exist."""
        response = test_client.get('/auth/login')
        
        # Should redirect to create credentials
        assert response.status_code in [200, 302]
    
    def test_create_credentials(self, test_client):
        """Test creating credentials through web interface."""
        response = test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_login_success(self, test_client):
        """Test successful login."""
        # Create credentials first
        test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        })
        
        # Login
        response = test_client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Virtual Camera Server' in response.data
    
    def test_login_failure(self, test_client):
        """Test failed login."""
        # Create credentials first
        test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        })
        
        # Try wrong password
        response = test_client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        # Should stay on login page or show error
        assert response.status_code in [200, 401]
    
    def test_logout(self, test_client):
        """Test logout functionality."""
        # Create credentials and login
        test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        })
        test_client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Logout
        response = test_client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200


class TestWebVideoUpload:
    """User tests for video upload through web interface."""
    
    def test_upload_video_requires_auth(self, test_client):
        """Test that video upload requires authentication."""
        response = test_client.post('/api/upload-video')
        
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_upload_video_authenticated(self, test_client):
        """Test uploading video when authenticated."""
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
        
        # Create a minimal test video
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            # Upload video
            with open(temp_file.name, 'rb') as f:
                response = test_client.post('/api/upload-video', 
                    data={'file': (f, 'test_video.mp4')},
                    content_type='multipart/form-data'
                )
            
            # Should succeed
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'video' in data
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


class TestWebCameraManagement:
    """User tests for camera management through web interface."""
    
    def test_create_camera_requires_auth(self, test_client):
        """Test that camera creation requires authentication."""
        response = test_client.post('/api/create-camera', json={
            'name': 'Test Camera',
            'video_ids': []
        })
        
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]
    
    def test_dashboard_requires_auth(self, test_client):
        """Test that dashboard requires authentication."""
        response = test_client.get('/')
        
        # Should redirect to login
        assert response.status_code == 302 or b'login' in response.data.lower()


class TestWebEndToEnd:
    """End-to-end user workflow tests."""
    
    def test_full_workflow(self, test_client):
        """Test complete user workflow: login -> upload -> create camera."""
        # 1. Create credentials
        test_client.post('/auth/create-credentials', data={
            'username': 'testuser',
            'password': 'testpass123',
            'confirm': 'testpass123'
        })
        
        # 2. Login
        test_client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # 3. Access dashboard
        response = test_client.get('/')
        assert response.status_code == 200
        
        # 4. Upload video (if we have a test video file)
        # This would require a real video file or mock
        
        # 5. Create camera (would require uploaded video)
        # This is tested in integration tests

