#!/usr/bin/env python3
"""
Test only script generation (no audio/video)
"""

import sys
import os
from datetime import date

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.webhook import EmployeeData
from app.services.script_generator import ScriptGenerator

def test_script_generation():
    """Test only the script generation part"""
    print("📝 Testing Script Generation Only")
    print("=" * 50)
    
    # Create test employee data
    employee_data = EmployeeData(
        employee_id="SCRIPT_TEST_001",
        name="Alex Rodriguez",
        email="alex.rodriguez@company.com",
        position="Full Stack Developer",
        team="Product Engineering",
        manager="Sarah Chen",
        start_date=date(2025, 10, 15),
        office="New York Office",
        tech_stack=["React", "Node.js", "TypeScript", "PostgreSQL"],
        first_day_schedule=[
            {
                "time": "9:00 AM",
                "activity": "Welcome & Company Overview"
            },
            {
                "time": "12:00 PM",
                "activity": "Team Lunch"
            }
        ],
        first_week_schedule={
            "Monday": "Onboarding and Setup",
            "Tuesday": "Development Environment Setup"
        }
    )
    
    print(f"👤 Employee: {employee_data.name}")
    print(f"💼 Position: {employee_data.position}")
    print(f"🏢 Team: {employee_data.team}")
    print()
    
    try:
        print("🚀 Generating script...")
        script_gen = ScriptGenerator()
        script = script_gen.generate_onboarding_script(employee_data)
        
        print(f"✅ Script generated successfully!")
        print(f"📊 Script has {len(script)} lines")
        print()
        print("📝 Generated Script:")
        print("-" * 40)
        
        for i, (speaker, text) in enumerate(script, 1):
            speaker_name = "Alex" if speaker == "host1" else "Jordan"
            print(f"{i}. {speaker_name.upper()}:")
            print(f"   {text}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🎯 Script Generation Test")
    print("This test only generates the AI script using OpenAI")
    print()
    
    if test_script_generation():
        print("=" * 50)
        print("🎉 SCRIPT GENERATION SUCCESSFUL!")
        print("=" * 50)
        print("✅ OpenAI API is working correctly")
        print("✅ Script generation pipeline is functional")
        return 0
    else:
        print("=" * 50)
        print("❌ SCRIPT GENERATION FAILED")
        print("=" * 50)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)