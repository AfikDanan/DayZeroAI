#!/usr/bin/env python3
"""
Unit tests for DevUtils
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import date
import tempfile
import shutil
from types import SimpleNamespace

from app.models.webhook import EmployeeData, ScheduleItem
from app.services.dev_utils import DevUtils


class TestDevUtils(unittest.TestCase):
    """Test cases for DevUtils"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.employee_data = EmployeeData(
            employee_id="TEST_001",
            name="John Smith",
            email="john.smith@company.com",
            position="Software Engineer",
            team="Engineering",
            manager="Jane Doe",
            start_date=date(2025, 10, 20),
            office="New York",
            department="Technology",
            buddy="Alice Johnson",
            tech_stack=["Python", "React", "PostgreSQL"],
            first_day_schedule=[
                ScheduleItem(
                    time="9:00 AM",
                    activity="Welcome & Setup",
                    location="Conference Room A"
                ),
                ScheduleItem(
                    time="12:00 PM",
                    activity="Team Lunch"
                )
            ],
            first_week_schedule={
                "Monday": "Onboarding and Setup",
                "Tuesday": "Development Environment"
            }
        )
        
        self.script = [
            ("host1", "Welcome to the team, John!"),
            ("host2", "We're excited to have you here."),
            ("host1", "Let's get started with your onboarding.")
        ]
    
    def test_save_script_for_dev(self):
        """Test saving script for development"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            DevUtils.save_script_for_dev(self.script, self.employee_data, dev_dir)
            
            script_file = dev_dir / "script.txt"
            self.assertTrue(script_file.exists())
            
            # Verify file content
            content = script_file.read_text(encoding='utf-8')
            
            # Check header
            self.assertIn("ONBOARDING VIDEO SCRIPT", content)
            self.assertIn("=" * 50, content)
            
            # Check employee information
            self.assertIn("Employee: John Smith", content)
            self.assertIn("Position: Software Engineer", content)
            self.assertIn("Team: Engineering", content)
            self.assertIn("Manager: Jane Doe", content)
            self.assertIn("Start Date: 2025-10-20", content)
            
            # Check script section
            self.assertIn("SCRIPT:", content)
            self.assertIn("-" * 30, content)
            
            # Check script content
            self.assertIn("1. ALEX:", content)
            self.assertIn("Welcome to the team, John!", content)
            self.assertIn("2. JORDAN:", content)
            self.assertIn("We're excited to have you here.", content)
            self.assertIn("3. ALEX:", content)
            self.assertIn("Let's get started with your onboarding.", content)
            
            # Check summary
            self.assertIn("Total script lines: 3", content)
    
    def test_save_script_for_dev_empty_script(self):
        """Test saving empty script"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            DevUtils.save_script_for_dev([], self.employee_data, dev_dir)
            
            script_file = dev_dir / "script.txt"
            self.assertTrue(script_file.exists())
            
            content = script_file.read_text(encoding='utf-8')
            self.assertIn("Total script lines: 0", content)
            self.assertIn("SCRIPT:", content)
    
    def test_save_script_for_dev_unicode_content(self):
        """Test saving script with unicode characters"""
        unicode_script = [
            ("host1", "¡Bienvenido María! 🎉"),
            ("host2", "Nous sommes ravis de vous avoir ici! 😊")
        ]
        
        unicode_employee = EmployeeData(
            employee_id="TEST_UNICODE",
            name="María García-López",
            email="maria@company.com",
            position="Développeur Senior",
            team="Engineering",
            manager="Jean-Pierre Dubois",
            start_date=date(2025, 10, 20),
            office="Paris",
            tech_stack=["Python"],
            first_day_schedule=[],
            first_week_schedule={}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            DevUtils.save_script_for_dev(unicode_script, unicode_employee, dev_dir)
            
            script_file = dev_dir / "script.txt"
            content = script_file.read_text(encoding='utf-8')
            
            # Verify unicode content is preserved
            self.assertIn("María García-López", content)
            self.assertIn("Développeur Senior", content)
            self.assertIn("Jean-Pierre Dubois", content)
            self.assertIn("¡Bienvenido María! 🎉", content)
            self.assertIn("😊", content)
    
    @patch('shutil.copy2')
    def test_copy_audio_for_dev(self, mock_copy):
        """Test copying audio file for development"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            audio_path = Path("source/audio.mp3")
            
            DevUtils.copy_audio_for_dev(audio_path, dev_dir)
            
            expected_dest = dev_dir / "final_audio.mp3"
            mock_copy.assert_called_once_with(audio_path, expected_dest)
    
    @patch('shutil.copy2')
    def test_copy_slides_for_dev(self, mock_copy):
        """Test copying slide files for development"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            slides = [
                Path("source/slide_1.png"),
                Path("source/slide_2.png"),
                Path("source/slide_3.png"),
                Path("source/slide_4.png"),
                Path("source/slide_5.png")
            ]
            
            DevUtils.copy_slides_for_dev(slides, dev_dir)
            
            # Verify slides directory was created
            slides_dir = dev_dir / "slides"
            
            # Verify all slides were copied
            expected_names = [
                "01_welcome.png",
                "02_role_team.png",
                "03_tech_stack.png",
                "04_schedule.png",
                "05_closing.png"
            ]
            
            self.assertEqual(mock_copy.call_count, 5)
            
            for i, expected_name in enumerate(expected_names):
                expected_dest = slides_dir / expected_name
                mock_copy.assert_any_call(slides[i], expected_dest)
    
    @patch('shutil.copy2')
    def test_copy_slides_for_dev_fewer_slides(self, mock_copy):
        """Test copying fewer slides than expected names"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            slides = [
                Path("source/slide_1.png"),
                Path("source/slide_2.png")
            ]
            
            DevUtils.copy_slides_for_dev(slides, dev_dir)
            
            # Should only copy the slides that exist
            self.assertEqual(mock_copy.call_count, 2)
    
    @patch('shutil.copy2')
    def test_copy_video_for_dev(self, mock_copy):
        """Test copying video file for development"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            video_path = Path("source/video.mp4")
            
            DevUtils.copy_video_for_dev(video_path, dev_dir)
            
            expected_dest = dev_dir / "final_video.mp4"
            mock_copy.assert_called_once_with(video_path, expected_dest)
    
    def test_create_dev_summary(self):
        """Test creating development summary"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            audio_duration = 125.5  # 2 minutes 5.5 seconds
            
            DevUtils.create_dev_summary(
                self.employee_data, 
                self.script, 
                audio_duration, 
                dev_dir
            )
            
            summary_file = dev_dir / "summary.md"
            self.assertTrue(summary_file.exists())
            
            content = summary_file.read_text(encoding='utf-8')
            
            # Check header
            self.assertIn("# Onboarding Video Generation Summary", content)
            
            # Check employee information section
            self.assertIn("## Employee Information", content)
            self.assertIn("- **Name:** John Smith", content)
            self.assertIn("- **Position:** Software Engineer", content)
            self.assertIn("- **Team:** Engineering", content)
            self.assertIn("- **Manager:** Jane Doe", content)
            self.assertIn("- **Start Date:** 2025-10-20", content)
            self.assertIn("- **Office:** New York", content)
            self.assertIn("- **Department:** Technology", content)
            self.assertIn("- **Buddy:** Alice Johnson", content)
            
            # Check tech stack section
            self.assertIn("## Tech Stack", content)
            self.assertIn("- Python", content)
            self.assertIn("- React", content)
            self.assertIn("- PostgreSQL", content)
            
            # Check first day schedule section
            self.assertIn("## First Day Schedule", content)
            self.assertIn("- **9:00 AM:** Welcome & Setup (Location: Conference Room A)", content)
            self.assertIn("- **12:00 PM:** Team Lunch", content)
            
            # Check first week overview section
            self.assertIn("## First Week Overview", content)
            self.assertIn("- **Monday:** Onboarding and Setup", content)
            self.assertIn("- **Tuesday:** Development Environment", content)
            
            # Check video details section
            self.assertIn("## Video Details", content)
            self.assertIn("- **Script Lines:** 3", content)
            self.assertIn("- **Audio Duration:** 125.50 seconds (2.1 minutes)", content)
            self.assertIn("- **Slides:** 5 slides", content)
            
            # Check files generated section
            self.assertIn("## Files Generated", content)
            self.assertIn("- `script.txt`", content)
            self.assertIn("- `final_audio.mp3`", content)
            self.assertIn("- `slides/`", content)
            self.assertIn("- `final_video.mp4`", content)
            self.assertIn("- `summary.md`", content)
    
    def test_create_dev_summary_minimal_employee_data(self):
        """Test creating summary with minimal employee data"""
        minimal_employee = EmployeeData(
            employee_id="MINIMAL_001",
            name="Jane Doe",
            email="jane@company.com",
            position="Developer",
            team="Tech",
            manager="Boss",
            start_date=date(2025, 10, 20),
            office="Remote",
            tech_stack=["JavaScript"],
            first_day_schedule=[],
            first_week_schedule={}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            DevUtils.create_dev_summary(
                minimal_employee, 
                [], 
                60.0, 
                dev_dir
            )
            
            summary_file = dev_dir / "summary.md"
            content = summary_file.read_text(encoding='utf-8')
            
            # Should handle missing optional fields gracefully
            self.assertIn("- **Name:** Jane Doe", content)
            self.assertNotIn("- **Department:**", content)  # Should not appear if None
            self.assertNotIn("- **Buddy:**", content)  # Should not appear if None
            
            # Should handle empty collections
            self.assertIn("## Tech Stack", content)
            self.assertIn("- JavaScript", content)
            self.assertIn("## First Day Schedule", content)
            self.assertIn("## First Week Overview", content)
    
    def test_create_dev_summary_schedule_with_location(self):
        """Test summary handles schedule items with and without location"""
        from types import SimpleNamespace
        
        schedule_with_mixed_locations = [
            ScheduleItem(
                time="9:00 AM",
                activity="Meeting with location",
                location="Room 101"
            ),
            ScheduleItem(
                time="10:00 AM",
                activity="Meeting without location"
            )
        ]
        
        self.employee_data.first_day_schedule = schedule_with_mixed_locations
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            DevUtils.create_dev_summary(
                self.employee_data, 
                self.script, 
                60.0, 
                dev_dir
            )
            
            summary_file = dev_dir / "summary.md"
            content = summary_file.read_text(encoding='utf-8')
            
            # Should include location when present
            self.assertIn("Meeting with location (Location: Room 101)", content)
            # Should not include location info when not present
            self.assertIn("- **10:00 AM:** Meeting without location\n", content)
    
    def test_create_dev_summary_long_duration(self):
        """Test summary formats long audio duration correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            long_duration = 3665.75  # 1 hour, 1 minute, 5.75 seconds
            
            DevUtils.create_dev_summary(
                self.employee_data, 
                self.script, 
                long_duration, 
                dev_dir
            )
            
            summary_file = dev_dir / "summary.md"
            content = summary_file.read_text(encoding='utf-8')
            
            # Should format duration correctly
            self.assertIn("3665.75 seconds (61.1 minutes)", content)


if __name__ == "__main__":
    unittest.main()