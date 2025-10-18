"""
Tests for the main API endpoints of the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestActivitiesAPI:
    """Test class for activities API endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test client for each test."""
        self.client = TestClient(app)
        
        # Store original activities and restore after test
        self.original_activities = activities.copy()
        
        # Clean up after test
        yield
        activities.clear()
        activities.update(self.original_activities)
    
    def test_root_redirect(self):
        """Test that root endpoint redirects to static index.html."""
        response = self.client.get("/")
        assert response.status_code == 200
        # Check if it's serving the HTML content or redirecting
        assert response.url.path.endswith("/static/index.html")
    
    def test_get_activities_success(self):
        """Test successful retrieval of all activities."""
        response = self.client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have the expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        
        # Verify structure of an activity
        chess_club = data["Chess Club"]
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in chess_club
            
        assert isinstance(chess_club["participants"], list)
        assert isinstance(chess_club["max_participants"], int)
    
    def test_signup_for_activity_success(self):
        """Test successful signup for an activity."""
        activity_name = "Chess Club"
        test_email = "newstudent@mergington.edu"
        
        # Ensure student is not already signed up
        response = self.client.get("/activities")
        initial_participants = response.json()[activity_name]["participants"]
        assert test_email not in initial_participants
        
        # Sign up for activity
        response = self.client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was added
        response = self.client.get("/activities")
        updated_participants = response.json()[activity_name]["participants"]
        assert test_email in updated_participants
    
    def test_signup_for_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist."""
        response = self.client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self):
        """Test that a student cannot sign up for the same activity twice."""
        activity_name = "Chess Club"
        
        # Get an existing participant
        response = self.client.get("/activities")
        existing_participant = response.json()[activity_name]["participants"][0]
        
        # Try to sign up again
        response = self.client.post(
            f"/activities/{activity_name}/signup?email={existing_participant}"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_unregister_from_activity_success(self):
        """Test successful unregistration from an activity."""
        activity_name = "Chess Club"
        
        # Get an existing participant
        response = self.client.get("/activities")
        participant_to_remove = response.json()[activity_name]["participants"][0]
        
        # Unregister the participant
        response = self.client.delete(
            f"/activities/{activity_name}/unregister?email={participant_to_remove}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert participant_to_remove in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was removed
        response = self.client.get("/activities")
        updated_participants = response.json()[activity_name]["participants"]
        assert participant_to_remove not in updated_participants
    
    def test_unregister_from_nonexistent_activity(self):
        """Test unregistration from an activity that doesn't exist."""
        response = self.client.delete(
            "/activities/NonexistentActivity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_unregister_non_participant(self):
        """Test unregistration of a student who is not registered."""
        activity_name = "Chess Club"
        non_participant = "notregistered@mergington.edu"
        
        # Ensure student is not registered
        response = self.client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert non_participant not in participants
        
        # Try to unregister
        response = self.client.delete(
            f"/activities/{activity_name}/unregister?email={non_participant}"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
    
    def test_activity_capacity_tracking(self):
        """Test that activities correctly track available spots."""
        response = self.client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_data in activities_data.items():
            max_participants = activity_data["max_participants"]
            current_participants = len(activity_data["participants"])
            
            # Verify that current participants don't exceed maximum
            assert current_participants <= max_participants
            
            # Verify that all fields are present and valid
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_email_validation_in_participants(self):
        """Test that participant emails follow expected format."""
        response = self.client.get("/activities")
        activities_data = response.json()
        
        for activity_name, activity_data in activities_data.items():
            for participant_email in activity_data["participants"]:
                # Basic email format validation
                assert "@" in participant_email
                assert "mergington.edu" in participant_email
                assert len(participant_email) > 5  # Basic length check
    
    def test_signup_and_unregister_workflow(self):
        """Test complete workflow of signing up and then unregistering."""
        activity_name = "Programming Class"
        test_email = "workflow_test@mergington.edu"
        
        # Step 1: Sign up
        response = self.client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert response.status_code == 200
        
        # Step 2: Verify registration
        response = self.client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert test_email in participants
        
        # Step 3: Unregister
        response = self.client.delete(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        assert response.status_code == 200
        
        # Step 4: Verify unregistration
        response = self.client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert test_email not in participants