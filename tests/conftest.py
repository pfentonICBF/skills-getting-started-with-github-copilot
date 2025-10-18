"""
Test configuration and fixtures for the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return {
        "Test Activity": {
            "description": "A test activity for testing purposes",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        }
    }


@pytest.fixture
def reset_activities():
    """Reset activities to original state after each test."""
    from src.app import activities
    
    # Store original activities
    original_activities = activities.copy()
    
    yield
    
    # Restore original activities
    activities.clear()
    activities.update(original_activities)