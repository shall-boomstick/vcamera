"""Video model representing an uploaded video file."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Video:
    """Represents an uploaded video file stored in the library."""
    
    id: str
    filename: str
    file_path: str
    file_size: int
    duration: float
    width: int
    height: int
    fps: float
    format: str
    upload_date: str
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert Video to dictionary for JSON serialization.
        
        Returns:
            dict: Video data as dictionary
        """
        return {
            'id': self.id,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'format': self.format,
            'upload_date': self.upload_date,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Video':
        """Create Video from dictionary.
        
        Args:
            data: Dictionary containing video data
            
        Returns:
            Video: Video instance
        """
        return cls(
            id=data['id'],
            filename=data['filename'],
            file_path=data['file_path'],
            file_size=data['file_size'],
            duration=data['duration'],
            width=data['width'],
            height=data['height'],
            fps=data['fps'],
            format=data['format'],
            upload_date=data['upload_date'],
            metadata=data.get('metadata', {})
        )

