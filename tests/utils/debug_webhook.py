#!/usr/bin/env python3
"""
Debug webhook processing
"""

from app.models.webhook import UserOnboardingWebhook, EmployeeData
from app.services.webhook_processor import WebhookProcessor
from datetime import datetime, date
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_webhook_processing():
    """Test webhook processing directly"""
    print("🔍 Testing webhook processing directly...")
    
    # Create test data
    employee_data = EmployeeData(
        employee_id="TEST003",
        name="Debug Test User",
        email="debug@example.com",
        position="Software Engineer",
        team="Engineering",
        manager="John Doe",
        start_date=date(2025, 10, 20),
        office="Remote",
        tech_stack=["Python", "FastAPI"],
        first_day_schedule=[
            {
                "time": "9:00 AM",
                "activity": "Welcome & Orientation"
            }
        ],
        first_week_schedule={
            "Monday": "Onboarding and Setup"
        }
    )
    
    payload = UserOnboardingWebhook(
        event_type="user.onboarding",
        employee_data=employee_data,
        timestamp=datetime.now()
    )
    
    print(f"✅ Created payload for {employee_data.name}")
    
    try:
        processor = WebhookProcessor()
        print("✅ Created webhook processor")
        
        job_id = processor.process_user_onboarding_webhook(payload)
        print(f"✅ Processed webhook, job_id: {job_id}")
        
        if job_id:
            # Check job status
            job_data = processor.get_job_status(job_id)
            print(f"📊 Job data: {job_data}")
        
        return job_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_webhook_processing()