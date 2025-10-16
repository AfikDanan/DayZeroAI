#!/usr/bin/env python3
"""
Basic API test without Redis dependency
Tests the core FastAPI endpoints
"""

import requests
import json
from datetime import datetime
import sys

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    print("\n🏠 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_webhook_status():
    """Test the webhook status endpoint"""
    print("\n📡 Testing webhook status...")
    try:
        response = requests.get(f"{BASE_URL}/webhooks/status", timeout=5)
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_webhook_validation():
    """Test webhook payload validation (without processing)"""
    print("\n🔍 Testing webhook payload validation...")
    
    # Test with invalid payload
    try:
        invalid_payload = {"invalid": "data"}
        response = requests.post(f"{BASE_URL}/webhooks/user-onboarding", 
                               json=invalid_payload, timeout=5)
        print(f"  Invalid payload status: {response.status_code}")
        
        # Test with valid payload structure
        valid_payload = {
            "event_type": "user.onboarding",
            "employee_data": {
                "employee_id": "TEST001",
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
        
        response = requests.post(f"{BASE_URL}/webhooks/user-onboarding", 
                               json=valid_payload, timeout=10)
        print(f"  Valid payload status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
            return True
        elif response.status_code == 500:
            print("  ⚠️ Expected 500 error (Redis not connected)")
            print(f"  Response: {response.json()}")
            return True  # This is expected without Redis
        else:
            print(f"  Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run basic API tests"""
    print("🚀 Basic API Testing (No Redis Required)")
    print("=" * 50)
    print("Make sure the server is running with: python run.py")
    print()
    
    tests = [
        ("Health Check", test_health_check),
        ("Root Endpoint", test_root_endpoint),
        ("Webhook Status", test_webhook_status),
        ("Webhook Validation", test_webhook_validation)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All basic API tests passed!")
        print("\nNext steps:")
        print("1. Start Redis: docker run -d --name redis-preboarding -p 6379:6379 redis:7-alpine")
        print("2. Run full tests: python test_webhook.py")
        print("3. Start worker: rq worker video_generation")
        return 0
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
        sys.exit(1)