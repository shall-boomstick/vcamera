"""UserSession model representing an authenticated user session."""
from dataclasses import dataclass


@dataclass
class UserSession:
    """Represents an authenticated user session in the GUI."""
    
    username: str
    session_id: str
    login_time: str
    last_activity: str
    
    def update_activity(self, timestamp: str):
        """Update last activity timestamp.
        
        Args:
            timestamp: ISO 8601 timestamp
        """
        self.last_activity = timestamp

