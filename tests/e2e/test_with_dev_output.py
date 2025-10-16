#!/usr/bin/env python3
"""
Test video generation with development output
Uses real APIs but saves all intermediate files for review
"""

import sys
import time
from pathlib import Path
from datetime import datetime, date

# Add the app to the path
sys.path.append('..')

from app.models.webhook import EmployeeData
from app.workers.video_worker import generate_onboarding_video

def test_with_dev_output():
    """Test video generation and save development files"""
    print("🎬 Video Generation Test with Development Output")
    print("=" * 60)
    print("This will use real OpenAI and Google Cloud APIs")
    print("All intermediate files will be saved to dev_output/ folder")
    print()
    
    # Create test employee data
    employee_data = {
        "employee_id": "DEV_TEST_001",
        "name": "Alex Rodriguez",
        "email": "alex.rodriguez@company.com",
        "position": "Full Stack Developer",
        "team": "Product Engineering",
        "manager": "Sarah Chen",
        "start_date": "2025-10-15",
        "office": "New York Office",
        "department": "Engineering",
        "buddy": "Jordan Kim",
        "tech_stack": [
            "React",
            "Node.js",
            "TypeScript",
            "PostgreSQL",
            "Docker",
            "AWS"
        ],
        "first_day_schedule": [
            {
                "time": "9:00 AM",
                "activity": "Welcome & Company Overview",
                "location": "Main Conference Room",
                "attendees": ["HR Team", "Sarah Chen"]
            },
            {
                "time": "10:30 AM",
                "activity": "IT Setup & Security Training",
                "location": "IT Department",
                "attendees": ["IT Support"]
            },
            {
                "time": "12:00 PM",
                "activity": "Team Lunch & Introductions",
                "location": "Company Cafeteria",
                "attendees": ["Product Engineering Team"]
            },
            {
                "time": "2:00 PM",
                "activity": "Codebase Walkthrough",
                "location": "Team Area",
                "attendees": ["Jordan Kim", "Senior Developers"]
            },
            {
                "time": "4:00 PM",
                "activity": "First Day Wrap-up & Q&A",
                "location": "Sarah's Office",
                "attendees": ["Sarah Chen"]
            }
        ],
        "first_week_schedule": {
            "Monday": "Onboarding, IT Setup, Team Introductions",
            "Tuesday": "Development Environment Setup, First Code Review",
            "Wednesday": "Product Architecture Deep Dive, Stakeholder Meetings",
            "Thursday": "First Feature Assignment, Pair Programming",
            "Friday": "Week Review, Team Retrospective, Happy Hour"
        }
    }
    
    job_id = f"dev_test_{int(time.time())}"
    
    print(f"👤 Employee: {employee_data['name']}")
    print(f"💼 Position: {employee_data['position']}")
    print(f"🏢 Team: {employee_data['team']}")
    print(f"📋 Job ID: {job_id}")
    print()
    
    # Show what will be generated
    print("📁 Development files that will be created:")
    print(f"   dev_output/{job_id}/")
    print("   ├── script.txt           # Generated script with speaker assignments")
    print("   ├── final_audio.mp3      # Complete audio track")
    print("   ├── slides/              # Individual slide images")
    print("   │   ├── 01_welcome.png")
    print("   │   ├── 02_role_team.png")
    print("   │   ├── 03_tech_stack.png")
    print("   │   ├── 04_schedule.png")
    print("   │   └── 05_closing.png")
    print("   ├── final_video.mp4      # Complete video")
    print("   └── summary.md           # Summary with all details")
    print()
    
    try:
        print("🚀 Starting video generation...")
        print("⏳ This may take a few minutes...")
        start_time = time.time()
        
        # Call the video generation function
        result = generate_onboarding_video(employee_data, job_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Generation completed in {duration:.2f} seconds")
        print(f"📊 Result: {result}")
        
        # Check development output
        dev_dir = Path(f"dev_output/{job_id}")
        if dev_dir.exists():
            print(f"\n📁 Development files created in: {dev_dir}")
            
            files_created = []
            for file_path in dev_dir.rglob("*"):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    files_created.append((file_path.relative_to(dev_dir), size))
            
            if files_created:
                print("\n📋 Files generated:")
                for file_rel_path, size in sorted(files_created):
                    size_str = f"{size:,} bytes"
                    if size > 1024:
                        size_str += f" ({size/1024:.1f} KB)"
                    if size > 1024*1024:
                        size_str += f" ({size/1024/1024:.1f} MB)"
                    print(f"   ✅ {file_rel_path} - {size_str}")
            
            return True
        else:
            print(f"⚠️ Development directory not found: {dev_dir}")
            return False
            
    except Exception as e:
        print(f"❌ Error during video generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🎯 Development Output Test")
    print("This test generates a video and saves all intermediate files")
    print("You can review the script, audio, and slides before the final video")
    print()
    
    # Confirm with user
    response = input("Continue with video generation? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Test cancelled.")
        return 0
    
    print()
    
    # Run video generation test
    if test_with_dev_output():
        print("\n" + "=" * 60)
        print("🎉 VIDEO GENERATION WITH DEV OUTPUT SUCCESSFUL!")
        print("=" * 60)
        print("✅ Video generated successfully")
        print("✅ All intermediate files saved for review")
        print()
        print("🔍 Next steps:")
        print("1. Review the script in dev_output/[job_id]/script.txt")
        print("2. Listen to the audio in dev_output/[job_id]/final_audio.mp3")
        print("3. Check the slides in dev_output/[job_id]/slides/")
        print("4. Watch the final video in dev_output/[job_id]/final_video.mp4")
        print("5. Read the summary in dev_output/[job_id]/summary.md")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ VIDEO GENERATION FAILED")
        print("=" * 60)
        print("Check the error messages above for details")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)