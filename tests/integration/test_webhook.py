import requests
import json
from datetime import datetime

# Test the webhook endpoints
BASE_URL = "http://localhost:8000"

def test_generic_webhook():
    """Test the generic webhook endpoint"""
    payload = {
        "event_type": "user.onboarding",
        "data": {
            "employee_id": "EMP001",
            "name": "Test User",
            "email": "test@example.com",
            "position": "Software Engineer",
            "team": "Engineering",
            "manager": "John Doe",
            "start_date": "2025-10-20",
            "office": "Remote",
            "tech_stack": ["Python", "FastAPI"],
            "first_day_schedule": [
                {
                    "time": "9:00 AM",
                    "activity": "Welcome & Orientation"
                }
            ],
            "first_week_schedule": {
                "Monday": "Onboarding and Setup"
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/webhooks/generic", json=payload)
    print(f"Generic webhook response: {response.status_code}")
    print(f"Response body: {response.json()}")

def test_user_onboarding_webhook():
    """Test the user onboarding webhook endpoint with proper structure"""
    payload = {
        "event_type": "user.onboarding",
        "employee_data": {
            "employee_id": "EMP002",
            "name": "Sarah Johnson",
            "email": "sarah.johnson@company.com",
            "position": "Senior Software Engineer",
            "team": "Platform Engineering",
            "manager": "Michael Chen",
            "start_date": "2025-10-20",
            "office": "San Francisco HQ",
            "department": "Engineering",
            "buddy": "Alex Martinez",
            "tech_stack": [
                "Python",
                "FastAPI",
                "Kubernetes",
                "PostgreSQL",
                "Redis",
                "React"
            ],
            "first_day_schedule": [
                {
                    "time": "9:00 AM",
                    "activity": "Welcome & HR Orientation",
                    "location": "Conference Room A",
                    "attendees": ["HR Team"]
                },
                {
                    "time": "10:30 AM",
                    "activity": "IT Setup & Equipment Distribution",
                    "location": "IT Department",
                    "attendees": ["IT Support"]
                },
                {
                    "time": "12:00 PM",
                    "activity": "Team Lunch",
                    "location": "Cafeteria",
                    "attendees": ["Platform Team"]
                }
            ],
            "first_week_schedule": {
                "Monday": "Onboarding, IT Setup, Team Introductions",
                "Tuesday": "Development Environment Setup, Codebase Overview",
                "Wednesday": "Architecture Deep Dive, Meet Key Stakeholders",
                "Thursday": "First Small Task, Pair Programming Session",
                "Friday": "Week Review, Q&A, Team Social Event"
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    response = requests.post(f"{BASE_URL}/webhooks/user-onboarding", json=payload)
    print(f"User onboarding webhook response: {response.status_code}")
    print(f"Response body: {response.json()}")
    return response.json().get("job_id")

def test_job_status(job_id):
    """Test job status endpoint"""
    if not job_id:
        print("No job_id to test")
        return
        
    response = requests.get(f"{BASE_URL}/jobs/{job_id}/status")
    print(f"Job status response: {response.status_code}")
    print(f"Response body: {response.json()}")

def test_webhook_status():
    """Test the webhook status endpoint"""
    response = requests.get(f"{BASE_URL}/webhooks/status")
    print(f"Webhook status response: {response.status_code}")
    print(f"Response body: {response.json()}")

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check response: {response.status_code}")
    print(f"Response body: {response.json()}")

if __name__ == "__main__":
    print("Testing webhook endpoints...")
    print("Make sure the server is running with: python run.py")
    print("Also ensure Redis is running for background jobs")
    print()
    
    try:
        # Test basic endpoints
        test_health_check()
        print()
        test_webhook_status()
        print()
        
        # Test webhook processing
        print("Testing user onboarding webhook...")
        job_id = test_user_onboarding_webhook()
        print()
        
        # Test job status
        if job_id:
            print(f"Testing job status for job_id: {job_id}")
            test_job_status(job_id)
            print()
        
        print("Testing generic webhook...")
        test_generic_webhook()
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure it's running on localhost:8000")