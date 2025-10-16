#!/usr/bin/env python3
"""
Unit tests for SlideGenerator
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import date
import tempfile
from types import SimpleNamespace
from PIL import Image, ImageFont

from app.models.webhook import EmployeeData, ScheduleItem
from app.services.slide_generator import SlideGenerator


class TestSlideGenerator(unittest.TestCase):
    """Test cases for SlideGenerator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.slide_gen = SlideGenerator()
        self.employee_data = EmployeeData(
            employee_id="TEST_001",
            name="John Smith",
            email="john.smith@company.com",
            position="Software Engineer",
            team="Engineering",
            manager="Jane Doe",
            start_date=date(2025, 10, 20),
            office="New York",
            tech_stack=["Python", "React", "PostgreSQL"],
            first_day_schedule=[
                ScheduleItem(time="9:00 AM", activity="Welcome & Setup"),
                ScheduleItem(time="12:00 PM", activity="Team Lunch"),
                ScheduleItem(time="2:00 PM", activity="Code Review"),
                ScheduleItem(time="4:00 PM", activity="Team Meeting"),
                ScheduleItem(time="5:00 PM", activity="Wrap-up")
            ],
            first_week_schedule={
                "Monday": "Onboarding",
                "Tuesday": "Development Setup"
            }
        )
    
    def test_init_default_dimensions(self):
        """Test SlideGenerator initialization with default dimensions"""
        slide_gen = SlideGenerator()
        
        self.assertEqual(slide_gen.width, 1920)
        self.assertEqual(slide_gen.height, 1080)
    
    def test_init_custom_dimensions(self):
        """Test SlideGenerator initialization with custom dimensions"""
        slide_gen = SlideGenerator(width=1280, height=720)
        
        self.assertEqual(slide_gen.width, 1280)
        self.assertEqual(slide_gen.height, 720)
    
    @patch('app.services.slide_generator.Path')
    @patch('app.services.slide_generator.Image')
    def test_load_template_background_success(self, mock_image, mock_path):
        """Test successful template background loading"""
        # Mock template file exists and can be opened
        mock_template_path = Mock()
        mock_path.return_value = mock_template_path
        
        mock_img = Mock()
        mock_img.size = (1920, 1080)
        mock_img.convert.return_value = mock_img
        mock_image.open.return_value = mock_img
        
        result = self.slide_gen._load_template_background()
        
        # Verify template was loaded
        mock_image.open.assert_called_once_with(mock_template_path)
        mock_img.convert.assert_called_once_with('RGB')
        self.assertEqual(result, mock_img)
    
    @patch('app.services.slide_generator.Path')
    @patch('app.services.slide_generator.Image')
    def test_load_template_background_resize(self, mock_image, mock_path):
        """Test template background loading with resize"""
        # Mock template file with different size
        mock_template_path = Mock()
        mock_path.return_value = mock_template_path
        
        mock_img = Mock()
        mock_img.size = (1280, 720)  # Different size
        mock_resized_img = Mock()
        mock_img.convert.return_value = mock_img
        mock_img.resize.return_value = mock_resized_img
        mock_image.open.return_value = mock_img
        
        result = self.slide_gen._load_template_background()
        
        # Verify resize was called with correct dimensions
        mock_img.resize.assert_called_once()
        self.assertEqual(result, mock_resized_img)
    
    @patch('app.services.slide_generator.Path')
    @patch('app.services.slide_generator.Image')
    def test_load_template_background_fallback(self, mock_image, mock_path):
        """Test template background fallback when file not found"""
        # Mock template file doesn't exist
        mock_image.open.side_effect = Exception("File not found")
        
        mock_fallback_img = Mock()
        mock_image.new.return_value = mock_fallback_img
        
        result = self.slide_gen._load_template_background()
        
        # Verify fallback was used
        mock_image.new.assert_called_once_with('RGB', (1920, 1080), color='#f8f7fc')
        self.assertEqual(result, mock_fallback_img)
    
    @patch('app.services.slide_generator.ImageFont')
    def test_load_fonts_success(self, mock_font):
        """Test successful font loading"""
        mock_title_font = Mock()
        mock_subtitle_font = Mock()
        mock_font.truetype.side_effect = [mock_title_font, mock_subtitle_font]
        
        title_font, subtitle_font = self.slide_gen._load_fonts(90, 48)
        
        # Verify fonts were loaded
        self.assertEqual(mock_font.truetype.call_count, 2)
        mock_font.truetype.assert_any_call("arial.ttf", 90)
        mock_font.truetype.assert_any_call("arial.ttf", 48)
        
        self.assertEqual(title_font, mock_title_font)
        self.assertEqual(subtitle_font, mock_subtitle_font)
    
    @patch('app.services.slide_generator.ImageFont')
    def test_load_fonts_windows_fallback(self, mock_font):
        """Test font loading with Windows fallback"""
        mock_title_font = Mock()
        mock_subtitle_font = Mock()
        
        # Mock fallback behavior
        def side_effect(*args, **kwargs):
            if "arial.ttf" in args[0]:
                raise Exception("Font not found")
            elif "Windows" in args[0]:
                return mock_title_font if args[1] == 90 else mock_subtitle_font
            else:
                raise Exception("Font not found")
        
        mock_font.truetype.side_effect = side_effect
        
        title_font, subtitle_font = self.slide_gen._load_fonts(90, 48)
        
        # Verify fonts were returned (may be fallback)
        self.assertIsNotNone(title_font)
        self.assertIsNotNone(subtitle_font)
    
    @patch('app.services.slide_generator.ImageFont')
    def test_load_fonts_default_fallback(self, mock_font):
        """Test font loading with default fallback"""
        mock_default_font = Mock()
        
        # All truetype calls fail, use default
        mock_font.truetype.side_effect = Exception("Font not found")
        mock_font.load_default.return_value = mock_default_font
        
        title_font, subtitle_font = self.slide_gen._load_fonts(90, 48)
        
        # Verify default fonts were used
        self.assertEqual(mock_font.load_default.call_count, 2)
        self.assertEqual(title_font, mock_default_font)
        self.assertEqual(subtitle_font, mock_default_font)
    
    @patch('app.services.slide_generator.ImageFont')
    def test_load_font_single_success(self, mock_font):
        """Test single font loading success"""
        mock_single_font = Mock()
        mock_font.truetype.return_value = mock_single_font
        
        font = self.slide_gen._load_font(60)
        
        mock_font.truetype.assert_called_once_with("arial.ttf", 60)
        self.assertEqual(font, mock_single_font)
    
    @patch('app.services.slide_generator.ImageFont')
    def test_load_font_single_fallback(self, mock_font):
        """Test single font loading with fallback"""
        mock_default_font = Mock()
        
        mock_font.truetype.side_effect = Exception("Font not found")
        mock_font.load_default.return_value = mock_default_font
        
        font = self.slide_gen._load_font(60)
        
        # Should try both paths then default
        self.assertEqual(mock_font.truetype.call_count, 2)
        mock_font.load_default.assert_called_once()
        self.assertEqual(font, mock_default_font)
    
    def test_create_slides(self):
        """Test creating all slides"""
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            
            # Mock the individual slide creation methods
            with patch.object(self.slide_gen, 'create_welcome_slide') as mock_welcome, \
                 patch.object(self.slide_gen, 'create_role_slide') as mock_role, \
                 patch.object(self.slide_gen, 'create_tech_slide') as mock_tech, \
                 patch.object(self.slide_gen, 'create_schedule_slide') as mock_schedule, \
                 patch.object(self.slide_gen, 'create_closing_slide') as mock_closing:
                
                # Set return values
                mock_welcome.return_value = work_dir / "slide_1.png"
                mock_role.return_value = work_dir / "slide_2.png"
                mock_tech.return_value = work_dir / "slide_3.png"
                mock_schedule.return_value = work_dir / "slide_4.png"
                mock_closing.return_value = work_dir / "slide_5.png"
                
                slides = self.slide_gen.create_slides(self.employee_data, work_dir)
                
                # Verify all methods were called
                mock_welcome.assert_called_once_with(self.employee_data, work_dir / "slide_1.png")
                mock_role.assert_called_once_with(self.employee_data, work_dir / "slide_2.png")
                mock_tech.assert_called_once_with(self.employee_data, work_dir / "slide_3.png")
                mock_schedule.assert_called_once_with(self.employee_data, work_dir / "slide_4.png")
                mock_closing.assert_called_once_with(self.employee_data, work_dir / "slide_5.png")
                
                # Verify return value
                self.assertEqual(len(slides), 5)
                self.assertEqual(slides[0], work_dir / "slide_1.png")
                self.assertEqual(slides[4], work_dir / "slide_5.png")
    
    @patch('app.services.slide_generator.ImageDraw')
    def test_create_welcome_slide(self, mock_draw):
        """Test welcome slide creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            slide_path = Path(temp_dir) / "welcome.png"
            
            # Mock image and drawing
            mock_img = Mock()
            mock_draw_obj = Mock()
            mock_draw.Draw.return_value = mock_draw_obj
            
            # Mock textbbox to return proper tuple
            mock_draw_obj.textbbox.return_value = (0, 0, 200, 50)
            
            with patch.object(self.slide_gen, '_load_template_background', return_value=mock_img), \
                 patch.object(self.slide_gen, '_load_fonts', return_value=(Mock(), Mock())):
                
                result = self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
                
                # Verify image operations
                mock_draw.Draw.assert_called_once_with(mock_img)
                mock_img.save.assert_called_once_with(slide_path)
                
                # Verify text drawing was called
                self.assertGreater(mock_draw_obj.textbbox.call_count, 0)
                self.assertGreater(mock_draw_obj.text.call_count, 0)
                
                self.assertEqual(result, slide_path)
    
    @patch('app.services.slide_generator.ImageDraw')
    def test_create_role_slide(self, mock_draw):
        """Test role slide creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            slide_path = Path(temp_dir) / "role.png"
            
            mock_img = Mock()
            mock_draw_obj = Mock()
            mock_draw.Draw.return_value = mock_draw_obj
            
            with patch.object(self.slide_gen, '_load_template_background', return_value=mock_img), \
                 patch.object(self.slide_gen, '_load_font', return_value=Mock()):
                
                result = self.slide_gen.create_role_slide(self.employee_data, slide_path)
                
                # Verify text was drawn for each info line
                expected_calls = 4  # Team, Manager, Office, Start Date
                self.assertEqual(mock_draw_obj.text.call_count, expected_calls)
                
                # Verify employee info was used
                call_args = [call[0][1] for call in mock_draw_obj.text.call_args_list]
                text_content = " ".join(call_args)
                self.assertIn("Engineering", text_content)
                self.assertIn("Jane Doe", text_content)
                self.assertIn("New York", text_content)
                
                self.assertEqual(result, slide_path)
    
    @patch('app.services.slide_generator.ImageDraw')
    def test_create_tech_slide(self, mock_draw):
        """Test tech stack slide creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            slide_path = Path(temp_dir) / "tech.png"
            
            mock_img = Mock()
            mock_draw_obj = Mock()
            mock_draw.Draw.return_value = mock_draw_obj
            
            with patch.object(self.slide_gen, '_load_template_background', return_value=mock_img), \
                 patch.object(self.slide_gen, '_load_font', return_value=Mock()):
                
                result = self.slide_gen.create_tech_slide(self.employee_data, slide_path)
                
                # Verify title + tech items were drawn
                expected_calls = 1 + len(self.employee_data.tech_stack)  # Title + tech items
                self.assertEqual(mock_draw_obj.text.call_count, expected_calls)
                
                # Verify tech stack items were included
                call_args = [call[0][1] for call in mock_draw_obj.text.call_args_list]
                text_content = " ".join(call_args)
                self.assertIn("Your Tech Stack", text_content)
                self.assertIn("Python", text_content)
                self.assertIn("React", text_content)
                self.assertIn("PostgreSQL", text_content)
                
                self.assertEqual(result, slide_path)
    
    @patch('app.services.slide_generator.ImageDraw')
    def test_create_schedule_slide(self, mock_draw):
        """Test schedule slide creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            slide_path = Path(temp_dir) / "schedule.png"
            
            mock_img = Mock()
            mock_draw_obj = Mock()
            mock_draw.Draw.return_value = mock_draw_obj
            
            with patch.object(self.slide_gen, '_load_template_background', return_value=mock_img), \
                 patch.object(self.slide_gen, '_load_font', return_value=Mock()):
                
                result = self.slide_gen.create_schedule_slide(self.employee_data, slide_path)
                
                # Verify title + first 5 schedule items were drawn
                expected_calls = 1 + min(5, len(self.employee_data.first_day_schedule))
                self.assertEqual(mock_draw_obj.text.call_count, expected_calls)
                
                # Verify schedule content
                call_args = [call[0][1] for call in mock_draw_obj.text.call_args_list]
                text_content = " ".join(call_args)
                self.assertIn("First Day Schedule", text_content)
                self.assertIn("9:00 AM", text_content)
                self.assertIn("Welcome & Setup", text_content)
                
                self.assertEqual(result, slide_path)
    
    @patch('app.services.slide_generator.ImageDraw')
    def test_create_schedule_slide_long_schedule(self, mock_draw):
        """Test schedule slide with more than 5 items"""
        # Add more schedule items
        long_schedule = [
            ScheduleItem(time=f"{i}:00 AM", activity=f"Activity {i}")
            for i in range(9, 18)  # 9 items
        ]
        self.employee_data.first_day_schedule = long_schedule
        
        with tempfile.TemporaryDirectory() as temp_dir:
            slide_path = Path(temp_dir) / "schedule.png"
            
            mock_img = Mock()
            mock_draw_obj = Mock()
            mock_draw.Draw.return_value = mock_draw_obj
            
            with patch.object(self.slide_gen, '_load_template_background', return_value=mock_img), \
                 patch.object(self.slide_gen, '_load_font', return_value=Mock()):
                
                self.slide_gen.create_schedule_slide(self.employee_data, slide_path)
                
                # Should only show first 5 items + title
                expected_calls = 1 + 5
                self.assertEqual(mock_draw_obj.text.call_count, expected_calls)
    
    @patch('app.services.slide_generator.ImageDraw')
    def test_create_closing_slide(self, mock_draw):
        """Test closing slide creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            slide_path = Path(temp_dir) / "closing.png"
            
            mock_img = Mock()
            mock_draw_obj = Mock()
            mock_draw_obj.textbbox.return_value = (0, 0, 200, 50)  # Mock text dimensions
            mock_draw.Draw.return_value = mock_draw_obj
            
            with patch.object(self.slide_gen, '_load_template_background', return_value=mock_img), \
                 patch.object(self.slide_gen, '_load_font', return_value=Mock()):
                
                result = self.slide_gen.create_closing_slide(self.employee_data, slide_path)
                
                # Verify text operations
                mock_draw_obj.textbbox.assert_called_once()
                mock_draw_obj.text.assert_called_once()
                
                # Verify closing message
                call_args = mock_draw_obj.text.call_args[0]
                self.assertIn("See you soon!", call_args[1])
                
                self.assertEqual(result, slide_path)
    
    def test_create_welcome_slide_name_parsing(self):
        """Test welcome slide handles different name formats"""
        test_cases = [
            ("John Smith", "John"),
            ("Mary Jane Watson", "Mary"),
            ("Jean-Pierre", "Jean-Pierre"),
            ("李小明", "李小明"),
            ("O'Connor", "O'Connor")
        ]
        
        for full_name, expected_first in test_cases:
            with self.subTest(name=full_name):
                self.employee_data.name = full_name
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    slide_path = Path(temp_dir) / f"welcome_{expected_first}.png"
                    
                    with patch.object(self.slide_gen, '_load_template_background'), \
                         patch.object(self.slide_gen, '_load_fonts', return_value=(Mock(), Mock())), \
                         patch('app.services.slide_generator.ImageDraw') as mock_draw:
                        
                        mock_draw_obj = Mock()
                        mock_draw_obj.textbbox.return_value = (0, 0, 200, 50)
                        mock_draw.Draw.return_value = mock_draw_obj
                        
                        self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
                        
                        # Verify first name was extracted and used
                        call_args = mock_draw_obj.text.call_args_list
                        title_text = call_args[0][0][1]  # First text call should be title
                        self.assertIn(f"Welcome, {expected_first}!", title_text)


if __name__ == "__main__":
    unittest.main()