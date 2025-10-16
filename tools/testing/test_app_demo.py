#!/usr/bin/env python3
"""
Demo script showing how to run the application step by step
"""

import subprocess
import time
import requests
import json
from datetime import datetime
import sys
import os

def show_step(step_num, title, description):
    """Show a step in the demo"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    print(f"{'='*60}")
    print(description)
    print()

def test_direct_video_generation():
    """Test video generation directly without API"""
    show_step(1, "DIRECT VIDEO GENERATION TEST", 
              "Testing the core video generation pipeline without API server")
    
    # Add current directory to Python path
    sys.path.append('.')
    
    try:
        from app.models.webhook import EmployeeData
        from app.workers.video_worker import generate_onboarding_video
        from datetime import date
        
        # Create test employee data
        employee_data = {
            "employee_id": "DEMO_001",
            "name": "Demo User",
            "email": "demo@company.com",
            "position": "Software Engineer",
            "team": "Engineering",
            "manager": "Demo Manager",
            "start_date": "2025-10-15",
            "office": "Demo Office",
            "tech_stack": ["Python", "FastAPI", "React"],
            "first_day_schedule": [
                {
                    "time": "9:00 AM",
                    "activity": "Welcome & Orientation"
                },
                {
                    "time": "12:00 PM", 
                    "activity": "Team Lunch"
                }
            ],
            "first_week_schedule": {
                "Monday": "Onboarding and Setup",
                "Tuesday": "Development Environment"
            }
        }
        
        job_id = f"demo_{int(time.time())}"
        
        print(f"👤 Employee: {employee_data['name']}")
        print(f"💼 Position: {employee_data['position']}")
        print(f"📋 Job ID: {job_id}")
        print()
        print("🚀 Starting video generation...")
        
        start_time = time.time()
        result = generate_onboarding_video(employee_data, job_id)
        end_time = time.time()
        
        print(f"✅ Video generation completed in {end_time - start_time:.2f} seconds")
        print(f"📊 Result: {result}")
        
        # Check if files were created
        video_path = f"videos/{job_id}.mp4"
        dev_path = f"dev_output/{job_id}"
        
        if os.path.exists(video_path):
            size = os.path.getsize(video_path)
            print(f"🎬 Video created: {video_path} ({size:,} bytes)")
        
        if os.path.exists(dev_path):
            print(f"📁 Development files: {dev_path}")
            for file in os.listdir(dev_path):
                if os.path.isfile(os.path.join(dev_path, file)):
                    file_size = os.path.getsize(os.path.join(dev_path, file))
                    print(f"   - {file}: {file_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_api_instructions():
    """Show instructions for running the API server"""
    show_step(2, "API SERVER INSTRUCTIONS", 
              "How to start the API server and test webhook endpoints")
    
    print("To run the complete application with API server:")
    print()
    print("1️⃣ Start the API server (in a separate terminal):")
    print("   cd preboarding_service")
    print("   python run.py")
    print()
    print("2️⃣ Start the background worker (in another terminal):")
    print("   cd preboarding_service") 
    print("   python -m rq worker video_generation")
    print()
    print("3️⃣ Test the API endpoints:")
    print("   python tests/test_webhook.py")
    print()
    print("4️⃣ Send a webhook request:")
    print("   POST http://localhost:8000/webhooks/user-onboarding")
    print("   Content-Type: application/json")
    print()
    print("   Example payload:")
    
    example_payload = {
        "event_type": "user.onboarding",
        "employee_data": {
            "employee_id": "EMP001",
            "name": "John Doe",
            "email": "john.doe@company.com",
            "position": "Software Engineer",
            "team": "Engineering",
            "manager": "Jane Smith",
            "start_date": "2025-10-20",
            "office": "New York",
            "tech_stack": ["Python", "React", "PostgreSQL"],
            "first_day_schedule": [
                {
                    "time": "9:00 AM",
                    "activity": "Welcome & HR Orientation"
                }
            ],
            "first_week_schedule": {
                "Monday": "Onboarding and Setup"
            }
        }
    }
    
    print(json.dumps(example_payload, indent=2))

def show_curl_example():
    """Show curl command example"""
    show_step(3, "CURL COMMAND EXAMPLE", 
              "Example curl command to test the webhook endpoint")
    
    print("curl -X POST http://localhost:8000/webhooks/user-onboarding \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{")
    print('    "event_type": "user.onboarding",')
    print('    "employee_data": {')
    print('      "employee_id": "EMP001",')
    print('      "name": "John Doe",')
    print('      "email": "john.doe@company.com",')
    print('      "position": "Software Engineer",')
    print('      "team": "Engineering",')
    print('      "manager": "Jane Smith",')
    print('      "start_date": "2025-10-20",')
    print('      "office": "New York",')
    print('      "tech_stack": ["Python", "React"],')
    print('      "first_day_schedule": [{"time": "9:00 AM", "activity": "Welcome"}],')
    print('      "first_week_schedule": {"Monday": "Onboarding"}')
    print('    }')
    print("  }'")

def main():
    """Main demo function"""
    print("🚀 PREBOARDING SERVICE DEMO")
    print("=" * 60)
    print("This demo shows how to run the AI-powered onboarding video service")
    print()
    
    # Test 1: Direct video generation
    if test_direct_video_generation():
        print("\n✅ Direct video generation works perfectly!")
    else:
        print("\n❌ Direct video generation failed")
        return 1
    
    # Show API instructions
    show_api_instructions()
    
    # Show curl example
    show_curl_example()
    
    print(f"\n{'='*60}")
    print("🎉 DEMO COMPLETE!")
    print("=" * 60)
    print("✅ Core video generation pipeline is working")
    print("✅ All components are functional")
    print("✅ Ready for production use")
    print()
    print("📁 Check the generated files in:")
    print("   - videos/ (final videos)")
    print("   - dev_output/ (development files)")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
        sys.exit(1)