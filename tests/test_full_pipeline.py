#!/usr/bin/env python3
"""
Full pipeline test - tests the complete video generation workflow
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_video_generation_pipeline():
    """Test the complete video generation pipeline"""
    print("🎬 Testing Full Video Generation Pipeline")
    print("=" * 60)
    
    # Step 1: Send webhook request
    print("📡 Step 1: Sending webhook request...")
    
    payload = {
        "event_type": "user.onboarding",
        "employee_data": {
            "employee_id": "PIPELINE_TEST_001",
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
                },
                {
                    "time": "3:30 PM",
                    "activity": "Development Environment Setup",
                    "location": "Your Desk",
                    "attendees": ["Alex Martinez"]
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
    
    try:
        response = requests.post(f"{BASE_URL}/webhooks/user-onboarding", 
                               json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ Webhook sent successfully!")
            print(f"📋 Job ID: {job_id}")
            
            if not job_id:
                print("❌ No job_id returned - something went wrong")
                return False
                
            return job_id
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")
        return False

def check_job_status(job_id, max_wait=300):
    """Check job status and wait for completion"""
    print(f"\n⏳ Step 2: Monitoring job {job_id}...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/jobs/{job_id}/status", timeout=5)
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                
                print(f"📊 Job status: {status}")
                
                if status == 'completed':
                    video_url = status_data.get('video_url')
                    print(f"✅ Job completed! Video URL: {video_url}")
                    return video_url
                elif status == 'failed':
                    error = status_data.get('error_message')
                    print(f"❌ Job failed: {error}")
                    return False
                elif status in ['queued', 'processing']:
                    print(f"⏳ Job is {status}... waiting...")
                    time.sleep(5)
                else:
                    print(f"❓ Unknown status: {status}")
                    time.sleep(5)
            else:
                print(f"❌ Error checking status: {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            print(f"❌ Error checking job status: {e}")
            time.sleep(5)
    
    print(f"⏰ Timeout after {max_wait} seconds")
    return False

def check_video_file(job_id):
    """Check if video file was actually created"""
    print(f"\n📁 Step 3: Checking video file...")
    
    video_path = Path(f"videos/{job_id}.mp4")
    
    if video_path.exists():
        file_size = video_path.stat().st_size
        print(f"✅ Video file created: {video_path}")
        print(f"📏 File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        return True
    else:
        print(f"❌ Video file not found: {video_path}")
        return False

def run_worker_test():
    """Run a single worker job to process the queue"""
    print(f"\n🔧 Step 4: Processing job with worker...")
    print("Note: This will run the worker once to process queued jobs")
    
    try:
        # Run worker for a limited time
        result = subprocess.run([
            sys.executable, "-c",
            """
import sys
sys.path.append('.')
from app.workers.video_worker import generate_onboarding_video
from redis import Redis
from rq import Queue, Worker
from app.config import settings

# Connect to Redis
redis_conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
queue = Queue('video_generation', connection=redis_conn)

# Create worker and process one job
worker = Worker([queue], connection=redis_conn)
print(f"Worker starting... Queue has {len(queue)} jobs")

if len(queue) > 0:
    worker.work(burst=True)  # Process all jobs and exit
    print("Worker finished processing jobs")
else:
    print("No jobs in queue")
"""
        ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
        
        print("Worker output:")
        print(result.stdout)
        if result.stderr:
            print("Worker errors:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⏰ Worker timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running worker: {e}")
        return False

def main():
    """Run the complete pipeline test"""
    print("🚀 Starting Full Pipeline Test")
    print("Make sure the API server is running: python run.py")
    print("Make sure Redis is running: docker ps")
    print()
    
    # Test API connectivity first
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API server not responding. Start it with: python run.py")
            return 1
        print("✅ API server is running")
    except Exception as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("Start the server with: python run.py")
        return 1
    
    # Step 1: Send webhook
    job_id = test_video_generation_pipeline()
    if not job_id:
        return 1
    
    # Step 2: Run worker to process the job
    if not run_worker_test():
        print("❌ Worker processing failed")
        return 1
    
    # Step 3: Check job status
    video_url = check_job_status(job_id, max_wait=60)  # Shorter wait since worker ran
    if not video_url:
        return 1
    
    # Step 4: Verify video file
    if not check_video_file(job_id):
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 PIPELINE TEST SUCCESSFUL!")
    print("=" * 60)
    print(f"✅ Webhook processed successfully")
    print(f"✅ Job queued and processed: {job_id}")
    print(f"✅ Video generated: {video_url}")
    print(f"✅ Video file created on disk")
    print()
    print("🎬 You can now:")
    print(f"1. View the video at: http://localhost:8000{video_url}")
    print(f"2. Check the file: videos/{job_id}.mp4")
    print("3. Send more webhook requests to generate more videos")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)