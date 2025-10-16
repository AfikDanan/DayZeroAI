#!/usr/bin/env python3
"""
Direct video generation test - bypasses API and tests core functionality
"""

import sys
import time
from pathlib import Path
from datetime import datetime, date

# Add the app to the path
sys.path.append('.')

from app.models.webhook import EmployeeData
from app.workers.video_worker import generate_onboarding_video

def test_direct_video_generation():
    """Test video generation directly without API"""
    print("🎬 Direct Video Generation Test")
    print("=" * 50)
    
    # Create test employee data
    employee_data = {
        "employee_id": "DIRECT_TEST_001",
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
            },
            {
                "time": "2:00 PM",
                "activity": "Meet Your Manager & Team Introduction",
                "location": "Team Space",
                "attendees": ["Michael Chen", "Platform Team"]
            }
        ],
        "first_week_schedule": {
            "Monday": "Onboarding, IT Setup, Team Introductions",
            "Tuesday": "Development Environment Setup, Codebase Overview",
            "Wednesday": "Architecture Deep Dive, Meet Key Stakeholders",
            "Thursday": "First Small Task, Pair Programming Session",
            "Friday": "Week Review, Q&A, Team Social Event"
        }
    }
    
    job_id = "direct_test_" + str(int(time.time()))
    
    print(f"👤 Employee: {employee_data['name']}")
    print(f"💼 Position: {employee_data['position']}")
    print(f"🏢 Team: {employee_data['team']}")
    print(f"📋 Job ID: {job_id}")
    print()
    
    try:
        print("🚀 Starting video generation...")
        start_time = time.time()
        
        # Call the video generation function directly
        result = generate_onboarding_video(employee_data, job_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Generation completed in {duration:.2f} seconds")
        print(f"📊 Result: {result}")
        
        # Check if video file was created
        video_path = Path(f"videos/{job_id}.mp4")
        if video_path.exists():
            file_size = video_path.stat().st_size
            print(f"✅ Video file created: {video_path}")
            print(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            
            # Check if file is not empty
            if file_size > 1000:  # At least 1KB
                print("✅ Video file appears to be valid (non-empty)")
                return True
            else:
                print("⚠️ Video file is very small - might be corrupted")
                return False
        else:
            print(f"❌ Video file not found: {video_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites")
    print("=" * 30)
    
    checks = []
    
    # Check Redis
    try:
        from redis import Redis
        from app.config import settings
        redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        redis_conn.ping()
        print("✅ Redis connection")
        checks.append(True)
    except Exception as e:
        print(f"❌ Redis connection: {e}")
        checks.append(False)
    
    # Check OpenAI API key
    try:
        from app.config import settings
        if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 10:
            print("✅ OpenAI API key")
            checks.append(True)
        else:
            print("❌ OpenAI API key missing or invalid")
            checks.append(False)
    except Exception as e:
        print(f"❌ OpenAI API key: {e}")
        checks.append(False)
    
    # Check Google Cloud credentials
    try:
        from google.cloud import texttospeech
        client = texttospeech.TextToSpeechClient()
        print("✅ Google Cloud Text-to-Speech")
        checks.append(True)
    except Exception as e:
        print(f"❌ Google Cloud Text-to-Speech: {e}")
        checks.append(False)
    
    # Check FFmpeg
    try:
        import subprocess
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        print("✅ FFmpeg")
        checks.append(True)
    except Exception as e:
        print(f"❌ FFmpeg: {e}")
        checks.append(False)
    
    # Check directories
    try:
        Path("videos").mkdir(exist_ok=True)
        Path("data").mkdir(exist_ok=True)
        print("✅ Directories")
        checks.append(True)
    except Exception as e:
        print(f"❌ Directories: {e}")
        checks.append(False)
    
    print()
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All {total} prerequisites met!")
        return True
    else:
        print(f"⚠️ {passed}/{total} prerequisites met")
        return False

def main():
    """Main test function"""
    print("🎯 Direct Video Generation Test")
    print("This test bypasses the API and tests video generation directly")
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return 1
    
    print()
    
    # Run video generation test
    if test_direct_video_generation():
        print("\n" + "=" * 50)
        print("🎉 VIDEO GENERATION SUCCESSFUL!")
        print("=" * 50)
        print("✅ All components working correctly")
        print("✅ Video file generated successfully")
        print()
        print("🎬 Next steps:")
        print("1. Check the generated video in the videos/ folder")
        print("2. Test the full API pipeline with: python test_full_pipeline.py")
        print("3. Start the API server and worker for production use")
        return 0
    else:
        print("\n" + "=" * 50)
        print("❌ VIDEO GENERATION FAILED")
        print("=" * 50)
        print("Check the error messages above for details")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)