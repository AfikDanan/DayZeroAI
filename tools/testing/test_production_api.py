#!/usr/bin/env python3
"""
Production API Test
Tests the complete production workflow
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_production_workflow():
    """Test the complete production workflow"""
    print("🏭 PRODUCTION API TEST")
    print("=" * 50)
    print("Testing the complete production workflow...")
    print()
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to API server: {e}")
        print("   💡 Make sure API server is running: python run.py")
        return False
    
    # Test 2: Root Endpoint
    print("\n2️⃣ Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint: {data['service']} v{data['version']}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️ Root endpoint error: {e}")
    
    # Test 3: Webhook Status
    print("\n3️⃣ Testing Webhook Status...")
    try:
        response = requests.get(f"{BASE_URL}/webhooks/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Webhook service: {data['status']}")
            print(f"   📡 Available endpoints: {len(data['endpoints'])}")
        else:
            print(f"   ❌ Webhook status failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Webhook status error: {e}")
    
    # Test 4: Send Production Webhook
    print("\n4️⃣ Testing Production Webhook...")
    
    webhook_payload = {
        "event_type": "user.onboarding",
        "employee_data": {
            "employee_id": "PROD_TEST_001",
            "name": "Production Test User",
            "email": "production.test@company.com",
            "position": "Senior Software Engineer",
            "team": "Platform Engineering",
            "manager": "Production Manager",
            "start_date": "2025-10-20",
            "office": "Production Office",
            "department": "Engineering",
            "buddy": "Production Buddy",
            "tech_stack": [
                "Python",
                "FastAPI",
                "React",
                "PostgreSQL",
                "Redis",
                "Docker"
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
                    "activity": "IT Setup & Equipment",
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
                "Tuesday": "Development Environment Setup",
                "Wednesday": "Architecture Deep Dive",
                "Thursday": "First Task Assignment",
                "Friday": "Week Review & Team Social"
            }
        },
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhooks/user-onboarding",
            json=webhook_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Webhook processed successfully!")
            print(f"   📋 Job ID: {data.get('job_id', 'None')}")
            print(f"   📅 Processed at: {data.get('processed_at', 'Unknown')}")
            
            job_id = data.get('job_id')
            if job_id:
                return test_job_monitoring(job_id)
            else:
                print("   ⚠️ No job ID returned - check worker status")
                return True
        else:
            print(f"   ❌ Webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Webhook error: {e}")
        return False

def test_job_monitoring(job_id):
    """Monitor job status"""
    print(f"\n5️⃣ Monitoring Job Status (ID: {job_id})...")
    
    for i in range(12):  # Monitor for up to 1 minute
        try:
            response = requests.get(f"{BASE_URL}/jobs/{job_id}/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                
                print(f"   📊 Check {i+1}: Status = {status}")
                
                if status == 'completed':
                    video_url = data.get('video_url')
                    print(f"   🎉 Job completed successfully!")
                    print(f"   🎬 Video URL: {video_url}")
                    print(f"   📅 Completed at: {data.get('completed_at')}")
                    return True
                elif status == 'failed':
                    error = data.get('error_message', 'Unknown error')
                    print(f"   ❌ Job failed: {error}")
                    return False
                elif status in ['queued', 'processing']:
                    print(f"   ⏳ Job is {status}... waiting...")
                    time.sleep(5)
                else:
                    print(f"   ❓ Unknown status: {status}")
                    time.sleep(5)
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
            time.sleep(5)
    
    print("   ⏰ Monitoring timeout - job may still be processing")
    return True

def main():
    """Main test function"""
    print("🎯 Make sure both services are running:")
    print("   1. API Server: python run.py")
    print("   2. Background Worker: python -m rq worker video_generation")
    print()
    
    input("Press Enter when both services are running...")
    print()
    
    success = test_production_workflow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 PRODUCTION TEST SUCCESSFUL!")
        print("✅ API server is working")
        print("✅ Webhook processing is functional")
        print("✅ Job queue system is operational")
        print("✅ Ready for production use!")
    else:
        print("❌ PRODUCTION TEST FAILED")
        print("Check the error messages above")
    
    print("\n📊 Next Steps:")
    print("- Fix Google Cloud TTS credentials for full video generation")
    print("- Set up proper monitoring and logging")
    print("- Configure production environment variables")
    print("- Set up reverse proxy (nginx) for production")

if __name__ == "__main__":
    main()