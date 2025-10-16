# test_integration.py
"""
Quick integration test script
Run this to verify your setup is working
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if server is running"""
    print("🔍 Testing server health...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Server is healthy")
    return True

def test_webhook():
    """Test webhook endpoint"""
    print("\n🔍 Testing webhook endpoint...")
    
    # Load mock data
    mock_data_path = Path("data/test_webhook.json")
    if not mock_data_path.exists():
        print("❌ Mock data file not found. Create data/test_webhook.json first")
        return None
    
    with open(mock_data_path) as f:
        payload = json.load(f)
    
    response = requests.post(
        f"{BASE_URL}/webhooks/user-onboarding",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    print(f"✅ Webhook accepted: {data['message']}")
    
    job_id = data.get('job_id')
    if job_id:
        print(f"📋 Job ID: {job_id}")
        return job_id
    return None

def test_job_status(job_id):
    """Test job status endpoint"""
    print(f"\n🔍 Checking job status for {job_id}...")
    
    max_attempts = 30  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/jobs/{job_id}/status")
        
        if response.status_code == 200:
            data = response.json()
            status = data['status']
            
            print(f"⏳ Status: {status}")
            
            if status == "completed":
                print(f"✅ Video ready: {data.get('video_url')}")
                return True
            elif status == "failed":
                print(f"❌ Job failed: {data.get('error_message')}")
                return False
            
            # Wait before next check
            time.sleep(10)
            attempt += 1
        else:
            print(f"❌ Error checking status: {response.status_code}")
            return False
    
    print("⚠️  Timeout waiting for video generation")
    return False

def test_minimal_script_generation():
    """Test just the script generation (faster)"""
    print("\n🔍 Testing script generation only...")
    
    try:
        from app.services.script_generator import ScriptGenerator
        from app.models.webhook import EmployeeData
        from datetime import date
        
        # Create minimal test data
        test_data = EmployeeData(
            employee_id="TEST001",
            name="Test User",
            email="test@example.com",
            position="Software Engineer",
            team="Engineering",
            manager="Test Manager",
            start_date=date.today(),
            office="Test Office",
            tech_stack=["Python", "FastAPI"],
            first_day_schedule=[],
            first_week_schedule={}
        )
        
        generator = ScriptGenerator()
        script = generator.generate_onboarding_script(test_data)
        
        print(f"✅ Script generated with {len(script)} segments")
        print("\nFirst few lines:")
        for speaker, text in script[:3]:
            print(f"  {speaker}: {text[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Script generation failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🚀 Preboarding Service Integration Test")
    print("=" * 60)
    
    # Quick checks first
    try:
        test_health()
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("Start server with: uvicorn app.main:app --reload")
        return
    
    # Test script generation (doesn't require worker)
    test_minimal_script_generation()
    
    # Full integration test
    print("\n" + "=" * 60)
    print("Full Integration Test (requires worker running)")
    print("=" * 60)
    
    user_input = input("\nRun full test? This requires RQ worker running (y/n): ")
    
    if user_input.lower() == 'y':
        job_id = test_webhook()
        
        if job_id:
            success = test_job_status(job_id)
            if success:
                print("\n" + "=" * 60)
                print("🎉 All tests passed! System is working correctly.")
                print("=" * 60)
            else:
                print("\n⚠️  Video generation failed or timed out")
        else:
            print("\n⚠️  No job ID returned from webhook")
    else:
        print("\n✅ Basic tests passed. Run worker and try full test later.")

if __name__ == "__main__":
    main()