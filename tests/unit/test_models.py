"""Unit tests for data models."""
import pytest
from datetime import datetime

from src.models.user_session import UserSession
from src.models.video import Video
from src.models.virtual_camera import VirtualCamera


class TestVideo:
    """Tests for Video model."""
    
    def test_video_creation(self):
        """Test creating a Video instance."""
        video = Video(
            id='test-id',
            filename='test.mp4',
            file_path='test.mp4',
            file_size=1024,
            duration=60.0,
            width=1920,
            height=1080,
            fps=30.0,
            format='mp4',
            upload_date='2025-01-01T00:00:00Z',
            metadata={'key': 'value'}
        )
        
        assert video.id == 'test-id'
        assert video.filename == 'test.mp4'
        assert video.duration == 60.0
        assert video.width == 1920
        assert video.height == 1080
        assert video.fps == 30.0
        assert video.format == 'mp4'
        assert video.metadata == {'key': 'value'}
    
    def test_video_to_dict(self):
        """Test Video.to_dict() serialization."""
        video = Video(
            id='test-id',
            filename='test.mp4',
            file_path='test.mp4',
            file_size=1024,
            duration=60.0,
            width=1920,
            height=1080,
            fps=30.0,
            format='mp4',
            upload_date='2025-01-01T00:00:00Z',
            metadata={'key': 'value'}
        )
        
        data = video.to_dict()
        
        assert isinstance(data, dict)
        assert data['id'] == 'test-id'
        assert data['filename'] == 'test.mp4'
        assert data['duration'] == 60.0
        assert data['metadata'] == {'key': 'value'}
    
    def test_video_from_dict(self):
        """Test Video.from_dict() deserialization."""
        data = {
            'id': 'test-id',
            'filename': 'test.mp4',
            'file_path': 'test.mp4',
            'file_size': 1024,
            'duration': 60.0,
            'width': 1920,
            'height': 1080,
            'fps': 30.0,
            'format': 'mp4',
            'upload_date': '2025-01-01T00:00:00Z',
            'metadata': {'key': 'value'}
        }
        
        video = Video.from_dict(data)
        
        assert video.id == 'test-id'
        assert video.filename == 'test.mp4'
        assert video.duration == 60.0
        assert video.metadata == {'key': 'value'}
    
    def test_video_round_trip(self):
        """Test Video serialization round-trip."""
        original = Video(
            id='test-id',
            filename='test.mp4',
            file_path='test.mp4',
            file_size=1024,
            duration=60.0,
            width=1920,
            height=1080,
            fps=30.0,
            format='mp4',
            upload_date='2025-01-01T00:00:00Z',
            metadata={'key': 'value'}
        )
        
        data = original.to_dict()
        restored = Video.from_dict(data)
        
        assert restored.id == original.id
        assert restored.filename == original.filename
        assert restored.duration == original.duration
        assert restored.metadata == original.metadata


class TestVirtualCamera:
    """Tests for VirtualCamera model."""
    
    def test_virtual_camera_creation(self):
        """Test creating a VirtualCamera instance."""
        camera = VirtualCamera(
            id='camera-id',
            name='Test Camera',
            video_ids=['video1', 'video2'],
            rtsp_url='rtsp://localhost:8554/camera/camera-id',
            rtsp_port=8554,
            auth_enabled=True,
            auth_username='user',
            auth_password_hash='hash123',
            status='active',
            current_video_index=0,
            created_date='2025-01-01T00:00:00Z',
            last_modified='2025-01-01T00:00:00Z'
        )
        
        assert camera.id == 'camera-id'
        assert camera.name == 'Test Camera'
        assert camera.video_ids == ['video1', 'video2']
        assert camera.rtsp_url == 'rtsp://localhost:8554/camera/camera-id'
        assert camera.auth_enabled is True
        assert camera.auth_username == 'user'
        assert camera.status == 'active'
    
    def test_virtual_camera_to_dict(self):
        """Test VirtualCamera.to_dict() serialization."""
        camera = VirtualCamera(
            id='camera-id',
            name='Test Camera',
            video_ids=['video1'],
            rtsp_url='rtsp://localhost:8554/camera/camera-id',
            rtsp_port=8554
        )
        
        data = camera.to_dict()
        
        assert isinstance(data, dict)
        assert data['id'] == 'camera-id'
        assert data['name'] == 'Test Camera'
        assert data['video_ids'] == ['video1']
        assert data['auth_enabled'] is False
        assert data['status'] == 'inactive'
    
    def test_virtual_camera_from_dict(self):
        """Test VirtualCamera.from_dict() deserialization."""
        data = {
            'id': 'camera-id',
            'name': 'Test Camera',
            'video_ids': ['video1', 'video2'],
            'rtsp_url': 'rtsp://localhost:8554/camera/camera-id',
            'rtsp_port': 8554,
            'auth_enabled': True,
            'auth_username': 'user',
            'auth_password_hash': 'hash123',
            'status': 'active',
            'current_video_index': 1,
            'created_date': '2025-01-01T00:00:00Z',
            'last_modified': '2025-01-01T00:00:00Z'
        }
        
        camera = VirtualCamera.from_dict(data)
        
        assert camera.id == 'camera-id'
        assert camera.name == 'Test Camera'
        assert camera.video_ids == ['video1', 'video2']
        assert camera.auth_enabled is True
        assert camera.status == 'active'
    
    def test_virtual_camera_round_trip(self):
        """Test VirtualCamera serialization round-trip."""
        original = VirtualCamera(
            id='camera-id',
            name='Test Camera',
            video_ids=['video1', 'video2'],
            rtsp_url='rtsp://localhost:8554/camera/camera-id',
            rtsp_port=8554,
            auth_enabled=True,
            auth_username='user',
            auth_password_hash='hash123'
        )
        
        data = original.to_dict()
        restored = VirtualCamera.from_dict(data)
        
        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.video_ids == original.video_ids
        assert restored.auth_enabled == original.auth_enabled


class TestUserSession:
    """Tests for UserSession model."""
    
    def test_user_session_creation(self):
        """Test creating a UserSession instance."""
        now = datetime.utcnow().isoformat() + 'Z'
        session = UserSession(
            username='testuser',
            session_id='session-id',
            login_time=now,
            last_activity=now
        )
        
        assert session.username == 'testuser'
        assert session.session_id == 'session-id'
        assert session.login_time == now
        assert session.last_activity == now
    
    def test_user_session_update_activity(self):
        """Test updating session activity."""
        now = datetime.utcnow().isoformat() + 'Z'
        later = datetime.utcnow().isoformat() + 'Z'
        
        session = UserSession(
            username='testuser',
            session_id='session-id',
            login_time=now,
            last_activity=now
        )
        
        session.update_activity(later)
        
        assert session.last_activity == later
        assert session.login_time == now  # Should not change

