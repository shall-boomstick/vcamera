"""User tests for API routes."""
import pytest
import os
import tempfile
import cv2
import numpy as np
import json

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


@pytest.fixture
def authenticated_client(test_client):
    """Create authenticated test client."""
    test_client.post('/auth/create-credentials', data={
        'username': 'testuser',
        'password': 'testpass123',
        'confirm': 'testpass123'
    })
    test_client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    })
    return test_client


@pytest.fixture
def test_video(test_client):
    """Create a test video and return its ID."""
    # Use the test_client's app
    app = test_client.application
    
    with app.app_context():
        video_library = app.video_library
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_file.close()
        
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_file.name, fourcc, 20.0, (640, 480))
            out.write(np.zeros((480, 640, 3), dtype=np.uint8))
            out.release()
            
            video = video_library.upload_video(temp_file.name, 'test.mp4')
            yield video.id
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


class TestAPICameraEndpoints:
    """Tests for camera API endpoints."""
    
    def test_get_camera_requires_auth(self, test_client):
        """Test that get camera requires authentication."""
        response = test_client.get('/api/camera/test-id')
        assert response.status_code == 401
    
    def test_get_camera_success(self, authenticated_client, test_video):
        """Test getting camera details."""
        app = authenticated_client.application
        with app.app_context():
            camera_manager = app.camera_manager
            camera = camera_manager.create_camera('Test Camera', [test_video])
            
            response = authenticated_client.get(f'/api/camera/{camera.id}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'camera' in data
            assert data['camera']['id'] == camera.id
            assert data['camera']['name'] == 'Test Camera'
    
    def test_get_camera_not_found(self, authenticated_client):
        """Test getting non-existent camera."""
        response = authenticated_client.get('/api/camera/nonexistent-id')
        assert response.status_code == 500
    
    def test_create_camera_success(self, authenticated_client, test_video):
        """Test creating camera via API."""
        response = authenticated_client.post('/api/create-camera', 
            json={
                'name': 'API Camera',
                'video_ids': [test_video]
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'camera' in data
        assert data['camera']['name'] == 'API Camera'
    
    def test_create_camera_missing_name(self, authenticated_client, test_video):
        """Test creating camera without name."""
        response = authenticated_client.post('/api/create-camera',
            json={'video_ids': [test_video]},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_camera_no_videos(self, authenticated_client):
        """Test creating camera without videos."""
        response = authenticated_client.post('/api/create-camera',
            json={'name': 'Test Camera', 'video_ids': []},
            content_type='application/json'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_camera_with_auth(self, authenticated_client, test_video):
        """Test creating camera with authentication enabled."""
        response = authenticated_client.post('/api/create-camera',
            json={
                'name': 'Auth Camera',
                'video_ids': [test_video],
                'auth_enabled': True,
                'auth_username': 'rtsp_user',
                'auth_password': 'rtsp_pass'
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_update_camera_requires_auth(self, test_client):
        """Test that update camera requires authentication."""
        response = test_client.post('/api/update-camera/test-id',
            json={'name': 'New Name'},
            content_type='application/json'
        )
        assert response.status_code == 401
    
    def test_update_camera_success(self, authenticated_client, test_video):
        """Test updating camera via API."""
        app = authenticated_client.application
        with app.app_context():
            camera_manager = app.camera_manager
            camera = camera_manager.create_camera('Original Name', [test_video])
            
            response = authenticated_client.post(f'/api/update-camera/{camera.id}',
                json={'name': 'Updated Name'},
                content_type='application/json'
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['camera']['name'] == 'Updated Name'
    
    def test_update_camera_empty_name(self, authenticated_client, test_video):
        """Test updating camera with empty name."""
        app = authenticated_client.application
        with app.app_context():
            camera_manager = app.camera_manager
            camera = camera_manager.create_camera('Test Camera', [test_video])
            
            response = authenticated_client.post(f'/api/update-camera/{camera.id}',
                json={'name': ''},
                content_type='application/json'
            )
            assert response.status_code == 400
    
    def test_delete_camera_requires_auth(self, test_client):
        """Test that delete camera requires authentication."""
        response = test_client.post('/api/delete-camera/test-id')
        assert response.status_code == 401
    
    def test_delete_camera_success(self, authenticated_client, test_video):
        """Test deleting camera via API."""
        app = authenticated_client.application
        with app.app_context():
            camera_manager = app.camera_manager
            camera = camera_manager.create_camera('To Delete', [test_video])
            
            response = authenticated_client.post(f'/api/delete-camera/{camera.id}')
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
    
    def test_start_camera_requires_auth(self, test_client):
        """Test that start camera requires authentication."""
        response = test_client.post('/api/start-camera/test-id')
        assert response.status_code == 401
    
    def test_stop_camera_requires_auth(self, test_client):
        """Test that stop camera requires authentication."""
        response = test_client.post('/api/stop-camera/test-id')
        assert response.status_code == 401


class TestAPIVideoEndpoints:
    """Tests for video API endpoints."""
    
    def test_list_videos_requires_auth(self, test_client):
        """Test that list videos requires authentication."""
        response = test_client.get('/api/videos')
        assert response.status_code == 401
    
    def test_list_videos_success(self, authenticated_client, test_video):
        """Test listing videos via API."""
        response = authenticated_client.get('/api/videos')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'videos' in data
        assert len(data['videos']) >= 1
    
    def test_delete_video_requires_auth(self, test_client):
        """Test that delete video requires authentication."""
        response = test_client.post('/api/delete-video/test-id')
        assert response.status_code == 401
    
    def test_delete_video_success(self, authenticated_client, test_video):
        """Test deleting video via API."""
        response = authenticated_client.post(f'/api/delete-video/{test_video}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_scan_videos_requires_auth(self, test_client):
        """Test that scan videos requires authentication."""
        response = test_client.post('/api/scan-videos')
        assert response.status_code == 401
    
    def test_scan_videos_success(self, authenticated_client):
        """Test scanning videos via API."""
        response = authenticated_client.post('/api/scan-videos')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data

