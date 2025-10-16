#!/usr/bin/env python3
"""
Unit tests for ScriptGenerator
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import date
import tempfile
import os

from app.models.webhook import EmployeeData
from app.services.script_generator import ScriptGenerator


class TestScriptGenerator(unittest.TestCase):
    """Test cases for ScriptGenerator"""
    
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
            tech_stack=["Python", "React", "PostgreSQL"],
            first_day_schedule=[
                {"time": "9:00 AM", "activity": "Welcome & Setup"},
                {"time": "12:00 PM", "activity": "Team Lunch"}
            ],
            first_week_schedule={
                "Monday": "Onboarding",
                "Tuesday": "Development Setup"
            }
        )
    
    @patch('app.services.script_generator.OpenAI')
    def test_init(self, mock_openai):
        """Test ScriptGenerator initialization"""
        script_gen = ScriptGenerator()
        
        # Verify OpenAI client is initialized
        mock_openai.assert_called_once()
        self.assertIsNotNone(script_gen.client)
    
    def test_get_system_prompt(self):
        """Test system prompt generation"""
        script_gen = ScriptGenerator()
        prompt = script_gen._get_system_prompt()
        
        # Verify prompt contains key elements
        self.assertIn("Alex", prompt)
        self.assertIn("Jordan", prompt)
        self.assertIn("conversational", prompt)
        self.assertIn("Format your response EXACTLY as:", prompt)
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 100)
    
    def test_build_prompt(self):
        """Test prompt building with employee data"""
        script_gen = ScriptGenerator()
        prompt = script_gen._build_prompt(self.employee_data)
        
        # Verify employee data is included
        self.assertIn("John Smith", prompt)
        self.assertIn("Software Engineer", prompt)
        self.assertIn("Engineering", prompt)
        self.assertIn("Jane Doe", prompt)
        self.assertIn("Python", prompt)
        self.assertIn("React", prompt)
        self.assertIn("9:00 AM", prompt)
        self.assertIn("Welcome & Setup", prompt)
        self.assertIn("Monday", prompt)
        self.assertIn("Onboarding", prompt)
    
    def test_parse_script_valid_format(self):
        """Test script parsing with valid format"""
        script_gen = ScriptGenerator()
        
        script_text = """Alex: Welcome to the team, John!
Jordan: We're excited to have you join us.
Alex: Let's go over your first day schedule.
Jordan: Don't worry, we'll help you get settled in."""
        
        result = script_gen._parse_script(script_text)
        
        expected = [
            ("host1", "Welcome to the team, John!"),
            ("host2", "We're excited to have you join us."),
            ("host1", "Let's go over your first day schedule."),
            ("host2", "Don't worry, we'll help you get settled in.")
        ]
        
        self.assertEqual(result, expected)
    
    def test_parse_script_mixed_formats(self):
        """Test script parsing with mixed speaker formats"""
        script_gen = ScriptGenerator()
        
        script_text = """Alex: Hello there!
jordan: Nice to meet you.
HOST1: This should work too.
speaker2: And this as well."""
        
        result = script_gen._parse_script(script_text)
        
        expected = [
            ("host1", "Hello there!"),
            ("host2", "Nice to meet you."),
            ("host1", "This should work too."),
            ("host2", "And this as well.")
        ]
        
        self.assertEqual(result, expected)
    
    def test_parse_script_empty_lines(self):
        """Test script parsing ignores empty lines"""
        script_gen = ScriptGenerator()
        
        script_text = """Alex: First line.

Jordan: Second line.


Alex: Third line."""
        
        result = script_gen._parse_script(script_text)
        
        expected = [
            ("host1", "First line."),
            ("host2", "Second line."),
            ("host1", "Third line.")
        ]
        
        self.assertEqual(result, expected)
    
    def test_parse_script_invalid_format(self):
        """Test script parsing handles invalid format gracefully"""
        script_gen = ScriptGenerator()
        
        script_text = """This is not a valid format
No colons here
Alex: This is valid
Invalid line again
Jordan: This is also valid"""
        
        result = script_gen._parse_script(script_text)
        
        expected = [
            ("host1", "This is valid"),
            ("host2", "This is also valid")
        ]
        
        self.assertEqual(result, expected)
    
    def test_parse_script_empty_text(self):
        """Test script parsing handles empty text after colon"""
        script_gen = ScriptGenerator()
        
        script_text = """Alex: 
Jordan: Valid text
Alex:
Jordan: More valid text"""
        
        result = script_gen._parse_script(script_text)
        
        expected = [
            ("host2", "Valid text"),
            ("host2", "More valid text")
        ]
        
        self.assertEqual(result, expected)
    
    @patch('app.services.script_generator.OpenAI')
    def test_generate_onboarding_script_success(self, mock_openai_class):
        """Test successful script generation"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """Alex: Welcome to the company, John!
Jordan: We're thrilled to have you on the Engineering team.
Alex: Your manager Jane Doe is looking forward to working with you.
Jordan: Let's make your first day amazing!"""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        script_gen = ScriptGenerator()
        result = script_gen.generate_onboarding_script(self.employee_data)
        
        # Verify API was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify result format
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], ("host1", "Welcome to the company, John!"))
        self.assertEqual(result[1], ("host2", "We're thrilled to have you on the Engineering team."))
    
    @patch('app.services.script_generator.OpenAI')
    def test_generate_onboarding_script_api_error(self, mock_openai_class):
        """Test script generation handles API errors"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        script_gen = ScriptGenerator()
        
        with self.assertRaises(Exception):
            script_gen.generate_onboarding_script(self.employee_data)
    
    def test_save_script_for_dev(self):
        """Test saving script for development"""
        script_gen = ScriptGenerator()
        
        script = [
            ("host1", "Welcome to the team!"),
            ("host2", "We're excited to have you here."),
            ("host1", "Let's get started with your onboarding.")
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            script_gen.save_script_for_dev(script, self.employee_data, dev_dir)
            
            script_file = dev_dir / "script.txt"
            self.assertTrue(script_file.exists())
            
            # Verify file content
            content = script_file.read_text(encoding='utf-8')
            
            # Check header information
            self.assertIn("ONBOARDING VIDEO SCRIPT", content)
            self.assertIn("John Smith", content)
            self.assertIn("Software Engineer", content)
            self.assertIn("Engineering", content)
            self.assertIn("Jane Doe", content)
            
            # Check script content
            self.assertIn("1. ALEX:", content)
            self.assertIn("Welcome to the team!", content)
            self.assertIn("2. JORDAN:", content)
            self.assertIn("We're excited to have you here.", content)
            self.assertIn("3. ALEX:", content)
            self.assertIn("Let's get started with your onboarding.", content)
            
            # Check summary
            self.assertIn("Total script lines: 3", content)
    
    def test_save_script_for_dev_empty_script(self):
        """Test saving empty script for development"""
        script_gen = ScriptGenerator()
        
        script = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            script_gen.save_script_for_dev(script, self.employee_data, dev_dir)
            
            script_file = dev_dir / "script.txt"
            self.assertTrue(script_file.exists())
            
            content = script_file.read_text(encoding='utf-8')
            self.assertIn("Total script lines: 0", content)
    
    def test_save_script_for_dev_unicode_content(self):
        """Test saving script with unicode characters"""
        script_gen = ScriptGenerator()
        
        script = [
            ("host1", "Welcome María! 🎉"),
            ("host2", "We're excited to have you here! 😊")
        ]
        
        # Create employee with unicode name
        unicode_employee = EmployeeData(
            employee_id="TEST_UNICODE",
            name="María García",
            email="maria@company.com",
            position="Développeur Senior",
            team="Engineering",
            manager="Jean-Pierre",
            start_date=date(2025, 10, 20),
            office="Paris",
            tech_stack=["Python"],
            first_day_schedule=[],
            first_week_schedule={}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            dev_dir = Path(temp_dir)
            
            script_gen.save_script_for_dev(script, unicode_employee, dev_dir)
            
            script_file = dev_dir / "script.txt"
            self.assertTrue(script_file.exists())
            
            content = script_file.read_text(encoding='utf-8')
            self.assertIn("María García", content)
            self.assertIn("Développeur Senior", content)
            self.assertIn("Jean-Pierre", content)
            self.assertIn("Welcome María! 🎉", content)
            self.assertIn("😊", content)


if __name__ == "__main__":
    unittest.main()