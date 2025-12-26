"""Utility functions for the virtual camera server application."""
import uuid


def generate_id() -> str:
    """Generate a unique identifier (UUID).
    
    Returns:
        str: A UUID string
    """
    return str(uuid.uuid4())

