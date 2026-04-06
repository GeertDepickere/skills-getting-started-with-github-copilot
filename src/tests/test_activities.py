import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""
    
    def test_get_activities_returns_list(self, client):
        """Arrange: Set up client
           Act: Make GET request to /activities
           Assert: Verify response contains activities with expected structure"""
        # Arrange
        expected_keys = {"Chess Club", "Programming Class", "Gym Class", "Basketball Team", 
                        "Soccer Club", "Art Studio", "Music Band", "Debate Club", "Science Club"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert set(activities.keys()) == expected_keys
        
    def test_activity_has_required_fields(self, client):
        """Arrange: Set up client
           Act: Fetch activities and examine structure
           Assert: Verify each activity has required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(set(activity_data.keys()))
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_successful(self, client):
        """Arrange: Prepare email and activity name
           Act: Submit signup request
           Assert: Verify student is added and response confirms signup"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Arrange: Get an already-signed-up student
           Act: Attempt duplicate signup
           Assert: Verify request is rejected"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Arrange: Prepare email and non-existent activity
           Act: Attempt signup for non-existent activity
           Assert: Verify 404 error"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRemoveParticipant:
    """Test suite for DELETE /activities/{activity_name}/remove endpoint."""
    
    def test_remove_participant_successful(self, client):
        """Arrange: Identify a participant to remove
           Act: Submit delete request
           Assert: Verify participant is removed"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email_to_remove not in activities[activity_name]["participants"]
    
    def test_remove_nonexistent_participant(self, client):
        """Arrange: Prepare email that's not in activity
           Act: Attempt to remove non-existent participant
           Assert: Verify 404 error"""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_remove_from_nonexistent_activity(self, client):
        """Arrange: Prepare remove request for non-existent activity
           Act: Submit delete request
           Assert: Verify 404 error"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestRootEndpoint:
    """Test suite for GET / endpoint."""
    
    def test_root_redirects_to_index(self, client):
        """Arrange: Set up client with follow redirects disabled
           Act: Make GET request to root
           Assert: Verify redirect to /static/index.html"""
        # Arrange & Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
