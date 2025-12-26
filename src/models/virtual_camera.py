"""VirtualCamera model representing a virtual camera instance."""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VirtualCamera:
    """Represents a virtual camera instance that streams video content via RTSP."""
    
    id: str
    name: str
    video_ids: List[str]
    rtsp_url: str
    rtsp_port: int
    auth_enabled: bool = False
    auth_username: Optional[str] = None
    auth_password_hash: Optional[str] = None
    status: str = "inactive"  # "active", "inactive", "error"
    current_video_index: int = 0
    created_date: str = ""
    last_modified: str = ""
    
    def to_dict(self) -> dict:
        """Convert VirtualCamera to dictionary for JSON serialization.
        
        Returns:
            dict: VirtualCamera data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'video_ids': self.video_ids,
            'rtsp_url': self.rtsp_url,
            'rtsp_port': self.rtsp_port,
            'auth_enabled': self.auth_enabled,
            'auth_username': self.auth_username,
            'auth_password_hash': self.auth_password_hash,
            'status': self.status,
            'current_video_index': self.current_video_index,
            'created_date': self.created_date,
            'last_modified': self.last_modified
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VirtualCamera':
        """Create VirtualCamera from dictionary.
        
        Args:
            data: Dictionary containing camera data
            
        Returns:
            VirtualCamera: VirtualCamera instance
        """
        return cls(
            id=data['id'],
            name=data['name'],
            video_ids=data['video_ids'],
            rtsp_url=data['rtsp_url'],
            rtsp_port=data['rtsp_port'],
            auth_enabled=data.get('auth_enabled', False),
            auth_username=data.get('auth_username'),
            auth_password_hash=data.get('auth_password_hash'),
            status=data.get('status', 'inactive'),
            current_video_index=data.get('current_video_index', 0),
            created_date=data.get('created_date', ''),
            last_modified=data.get('last_modified', '')
        )

