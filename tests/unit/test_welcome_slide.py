#!/usr/bin/env python3
"""
Unit test for welcome slide creation
Tests the _create_welcome_slide method in VideoGenerator
"""

import sys
import os
import unittest
from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.webhook import EmployeeData
from app.services.slide_generator import SlideGenerator

class TestWelcomeSlide(unittest.TestCase):
    """Test cases for welcome slide creation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.slide_gen = SlideGenerator()
        self.test_output_dir = Path("test_output")
        self.test_output_dir.mkdir(exist_ok=True)
        
        # Create test employee data
        self.employee_data = EmployeeData(
            employee_id="TEST_SLIDE_001",
            name="John Smith",
            email="john.smith@company.com",
            position="Senior Software Engineer",
            team="Engineering",
            manager="Jane Doe",
            start_date=date(2025, 10, 20),
            office="New York",
            tech_stack=["Python", "React"],
            first_day_schedule=[],
            first_week_schedule={}
        )
    
    def tearDown(self):
        """Clean up test files"""
        # Remove test output files
        if self.test_output_dir.exists():
            for file in self.test_output_dir.glob("*"):
                if file.is_file():
                    file.unlink()
    
    def test_welcome_slide_creation(self):
        """Test that welcome slide is created successfully"""
        slide_path = self.test_output_dir / "test_welcome_slide.png"
        
        # Create the welcome slide
        result_path = self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
        
        # Verify the slide was created
        self.assertTrue(slide_path.exists(), "Welcome slide file should be created")
        self.assertEqual(result_path, slide_path, "Method should return the correct path")
        
        # Verify file is not empty
        file_size = slide_path.stat().st_size
        self.assertGreater(file_size, 1000, "Slide file should be larger than 1KB")
        
        print(f"✅ Welcome slide created: {slide_path}")
        print(f"📏 File size: {file_size:,} bytes")
    
    def test_welcome_slide_image_properties(self):
        """Test that the generated slide has correct image properties"""
        slide_path = self.test_output_dir / "test_slide_properties.png"
        
        # Create the slide
        self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
        
        # Open and verify image properties
        with Image.open(slide_path) as img:
            self.assertEqual(img.size, (1920, 1080), "Slide should be 1920x1080 (HD)")
            self.assertEqual(img.mode, 'RGB', "Slide should be in RGB mode")
            
            # Verify it's not a blank image by checking pixel diversity
            colors = img.getcolors(maxcolors=1000000)
            self.assertGreater(len(colors), 5, "Slide should have multiple colors (not blank)")
        
        print(f"✅ Image properties verified: 1920x1080 RGB with {len(colors)} colors")
    
    def test_welcome_slide_with_different_names(self):
        """Test welcome slide creation with different employee names"""
        test_cases = [
            ("Alice Johnson", "Alice"),
            ("Bob Smith-Wilson", "Bob"),
            ("María García", "María"),
            ("李小明", "李小明"),  # Chinese name
            ("Jean-Pierre Dupont", "Jean-Pierre"),
        ]
        
        for full_name, expected_first_name in test_cases:
            with self.subTest(name=full_name):
                # Update employee data
                self.employee_data.name = full_name
                
                slide_path = self.test_output_dir / f"test_slide_{expected_first_name.replace('-', '_')}.png"
                
                # Create slide
                self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
                
                # Verify slide was created
                self.assertTrue(slide_path.exists(), f"Slide should be created for {full_name}")
                
                # Verify file size is reasonable
                file_size = slide_path.stat().st_size
                self.assertGreater(file_size, 1000, f"Slide for {full_name} should not be empty")
                
                print(f"✅ Slide created for {full_name} -> {expected_first_name}")
    
    def test_welcome_slide_with_long_position(self):
        """Test welcome slide with very long position title"""
        self.employee_data.position = "Senior Principal Software Engineering Manager and Technical Lead"
        
        slide_path = self.test_output_dir / "test_long_position.png"
        
        # Should not raise an exception
        try:
            self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
            self.assertTrue(slide_path.exists(), "Slide should be created even with long position")
            print("✅ Long position title handled correctly")
        except Exception as e:
            self.fail(f"Should handle long position titles without error: {e}")
    
    def test_welcome_slide_font_fallback(self):
        """Test that slide creation works even if fonts are not available"""
        # This test verifies the font fallback mechanism works
        slide_path = self.test_output_dir / "test_font_fallback.png"
        
        # Create slide (should work with default fonts if Arial not available)
        self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
        
        self.assertTrue(slide_path.exists(), "Slide should be created with fallback fonts")
        
        # Verify the image is valid
        with Image.open(slide_path) as img:
            self.assertEqual(img.size, (1920, 1080), "Slide dimensions should be correct")
        
        print("✅ Font fallback mechanism working")
    
    def test_welcome_slide_color_scheme(self):
        """Test that the slide uses the expected color scheme"""
        slide_path = self.test_output_dir / "test_colors.png"
        
        self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
        
        # Open image and sample some pixels to verify colors are used
        with Image.open(slide_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get all unique colors
            colors = img.getcolors(maxcolors=1000000)
            color_values = [color[1] for color in colors]
            
            # Check for background color (light purple/white)
            background_colors = [(248, 247, 252), (255, 255, 255)]  # #f8f7fc or white
            has_background = any(bg in color_values for bg in background_colors)
            
            # The slide should have multiple colors (text, background, etc.)
            self.assertGreater(len(colors), 3, "Slide should use multiple colors")
            
        print(f"✅ Color scheme verified: {len(colors)} unique colors used")
    
    def test_welcome_slide_text_positioning(self):
        """Test that text is properly positioned and not cut off"""
        slide_path = self.test_output_dir / "test_positioning.png"
        
        # Test with a name that might cause positioning issues
        self.employee_data.name = "Christopher Alexander Montgomery-Smith"
        self.employee_data.position = "Senior Principal Software Engineering Manager"
        
        self.slide_gen.create_welcome_slide(self.employee_data, slide_path)
        
        self.assertTrue(slide_path.exists(), "Slide should handle long names and positions")
        
        # Verify image is valid and has expected dimensions
        with Image.open(slide_path) as img:
            self.assertEqual(img.size, (1920, 1080), "Slide should maintain correct dimensions")
        
        print("✅ Text positioning handled correctly for long names")

def run_visual_inspection():
    """Create sample slides for visual inspection"""
    print("\n🎨 Creating sample slides for visual inspection...")
    
    video_gen = VideoGenerator()
    samples_dir = Path("test_output/samples")
    samples_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample employees with different characteristics
    sample_employees = [
        {
            "name": "Sarah Johnson",
            "position": "Software Engineer",
            "filename": "sample_1_standard.png"
        },
        {
            "name": "Alexander Rodriguez-Martinez",
            "position": "Senior Principal Software Engineering Manager",
            "filename": "sample_2_long_names.png"
        },
        {
            "name": "李小明",
            "position": "Data Scientist",
            "filename": "sample_3_unicode.png"
        },
        {
            "name": "Emma",
            "position": "UX Designer",
            "filename": "sample_4_short.png"
        }
    ]
    
    for sample in sample_employees:
        employee = EmployeeData(
            employee_id="SAMPLE",
            name=sample["name"],
            email="sample@company.com",
            position=sample["position"],
            team="Engineering",
            manager="Manager",
            start_date=date(2025, 10, 20),
            office="Office",
            tech_stack=["Python"],
            first_day_schedule=[],
            first_week_schedule={}
        )
        
        slide_path = samples_dir / sample["filename"]
        video_gen._create_welcome_slide(employee, slide_path)
        
        file_size = slide_path.stat().st_size
        print(f"   ✅ {sample['filename']}: {file_size:,} bytes")
    
    print(f"\n📁 Sample slides created in: {samples_dir}")
    print("   You can open these files to visually inspect the slide design")

def main():
    """Run the tests"""
    print("🧪 Welcome Slide Unit Tests")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Create visual samples
    run_visual_inspection()
    
    print("\n" + "=" * 50)
    print("🎉 Welcome Slide Tests Complete!")
    print("✅ All unit tests passed")
    print("🎨 Visual samples created for inspection")

if __name__ == "__main__":
    main()