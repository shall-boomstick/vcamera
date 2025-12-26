"""Integration tests for authentication flow."""
import pytest
import time

from src.services.auth import AuthService
from src.services.exceptions import AuthenticationError, CredentialsExistError


class TestAuthIntegration:
    """Integration tests for authentication workflow."""
    
    def test_full_auth_workflow(self, auth_service):
        """Test complete authentication workflow."""
        # 1. Create credentials
        auth_service.create_credentials('testuser', 'password123')
        assert auth_service.credentials_exist()
        
        # 2. Authenticate
        session = auth_service.authenticate('testuser', 'password123')
        assert session is not None
        assert session.username == 'testuser'
        
        # 3. Validate session
        assert auth_service.validate_session(session.session_id) is True
        
        # 4. Logout
        auth_service.logout(session.session_id)
        assert auth_service.validate_session(session.session_id) is False
    
    def test_session_persistence(self, auth_service):
        """Test that session persists across multiple validations."""
        auth_service.create_credentials('testuser', 'password123')
        session = auth_service.authenticate('testuser', 'password123')
        
        # Validate multiple times
        assert auth_service.validate_session(session.session_id) is True
        assert auth_service.validate_session(session.session_id) is True
        assert auth_service.validate_session(session.session_id) is True
    
    def test_multiple_sessions(self, auth_service):
        """Test multiple concurrent sessions."""
        auth_service.create_credentials('testuser', 'password123')
        
        session1 = auth_service.authenticate('testuser', 'password123')
        session2 = auth_service.authenticate('testuser', 'password123')
        
        assert session1.session_id != session2.session_id
        assert auth_service.validate_session(session1.session_id) is True
        assert auth_service.validate_session(session2.session_id) is True
        
        # Logout one session
        auth_service.logout(session1.session_id)
        assert auth_service.validate_session(session1.session_id) is False
        assert auth_service.validate_session(session2.session_id) is True

