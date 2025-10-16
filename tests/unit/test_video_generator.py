#!/usr/bin/env python3
"""
Unit tests for VideoGenerator
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from datetime import date
import tempfile
import subprocess

from app.models.webhook import EmployeeData
from app.services.video_generator import VideoGenerator


class TestVideoGenerator(unittest.TestCase):
    """Test cases for VideoGenerator"""
    
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
            tech_stack=["Python", "React"],
            first_day_schedule=[
                {"time": "9:00 AM", "activity": "Welcome"}
            ],
            first_week_schedule={
                "Monday": "Onboarding"
            }
        )
    
    @patch('app.services.video_generator.settings')
    def test_init(self, mock_settings):
        """Test VideoGenerator initialization"""
        mock_settings.TEMP_DIR = "/tmp"
        mock_settings.OUTPUT_DIR = "/output"
        
        with patch('app.services.video_generator.ScriptGenerator') as mock_script_gen, \
             patch('app.services.video_generator.AudioGenerator') as mock_audio_gen, \
             patch('app.services.video_generator.SlideGenerator') as mock_slide_gen:
            
            video_gen = VideoGenerator()
            
            # Verify all generators are initialized
            mock_script_gen.assert_called_once()
            mock_audio_gen.assert_called_once()
            mock_slide_gen.assert_called_once()
            
            # Verify paths are set
            self.assertEqual(video_gen.temp_dir, Path("/tmp"))
            self.assertEqual(video_gen.output_dir, Path("/output"))
            self.assertEqual(video_gen.fps, 30)
    
    @patch('app.services.video_generator.settings')
    @patch('app.services.video_generator.DevUtils')
    def test_generate_onboarding_video_success(self, mock_dev_utils, mock_settings):
        """Test successful video generation"""
        mock_settings.TEMP_DIR = "/tmp"
        mock_settings.OUTPUT_DIR = "/output"
        mock_settings.DEV_OUTPUT_DIR = "/dev"
        
        with patch('app.services.video_generator.ScriptGenerator') as mock_script_gen_class, \
             patch('app.services.video_generator.AudioGenerator') as mock_audio_gen_class, \
             patch('app.services.video_generator.SlideGenerator') as mock_slide_gen_class:
            
            # Mock the generator instances
            mock_script_gen = Mock()
            mock_audio_gen = Mock()
            mock_slide_gen = Mock()
            
            mock_script_gen_class.return_value = mock_script_gen
            mock_audio_gen_class.return_value = mock_audio_gen
            mock_slide_gen_class.return_value = mock_slide_gen
            
            # Mock return values
            mock_script = [("host1", "Welcome!"), ("host2", "Hello!")]
            mock_audio_path = Path("/tmp/test_job/audio.mp3")
            mock_slides = [Path("/tmp/test_job/slide1.png"), Path("/tmp/test_job/slide2.png")]
            mock_video_path = Path("/output/test_job.mp4")
            
            mock_script_gen.generate_onboarding_script.return_value = mock_script
            mock_audio_gen.generate_audio.return_value = mock_audio_path
            mock_audio_gen.get_audio_duration.return_value = 60.0
            mock_slide_gen.create_slides.return_value = mock_slides
            
            video_gen = VideoGenerator()
            
            with patch.object(video_gen, '_compose_video', return_value=mock_video_path) as mock_compose:
                result = video_gen.generate_onboarding_video(self.employee_data, "test_job")
                
                # Verify all steps were called
                mock_script_gen.generate_onboarding_script.assert_called_once_with(self.employee_data)
                mock_script_gen.save_script_for_dev.assert_called_once()
                
                mock_audio_gen.generate_audio.assert_called_once_with(mock_script, Path("/tmp/test_job"))
                mock_audio_gen.get_audio_duration.assert_called_once_with(mock_audio_path)
                
                mock_slide_gen.create_slides.assert_called_once_with(self.employee_data, Path("/tmp/test_job"))
                
                mock_compose.assert_called_once_with(
                    mock_slides, mock_audio_path, 60.0, Path("/tmp/test_job"), "test_job"
                )
                
                # Verify dev utils were called
                mock_dev_utils.copy_audio_for_dev.assert_called_once()
                mock_dev_utils.copy_slides_for_dev.assert_called_once()
                mock_dev_utils.copy_video_for_dev.assert_called_once()
                mock_dev_utils.create_dev_summary.assert_called_once()
                
                self.assertEqual(result, mock_video_path)
    
    @patch('app.services.video_generator.settings')
    def test_generate_onboarding_video_script_error(self, mock_settings):
        """Test video generation handles script generation error"""
        mock_settings.TEMP_DIR = "/tmp"
        mock_settings.OUTPUT_DIR = "/output"
        mock_settings.DEV_OUTPUT_DIR = "/dev"
        
        with patch('app.services.video_generator.ScriptGenerator') as mock_script_gen_class:
            mock_script_gen = Mock()
            mock_script_gen_class.return_value = mock_script_gen
            mock_script_gen.generate_onboarding_script.side_effect = Exception("Script error")
            
            video_gen = VideoGenerator()
            
            with self.assertRaises(Exception) as context:
                video_gen.generate_onboarding_video(self.employee_data, "test_job")
            
            self.assertIn("Script error", str(context.exception))
    
    @patch('subprocess.run')
    def test_compose_video_success(self, mock_subprocess):
        """Test successful video composition"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            slides = [
                work_dir / "slide1.png",
                work_dir / "slide2.png"
            ]
            
            # Create mock slide files
            for slide in slides:
                slide.touch()
            
            audio_path = work_dir / "audio.mp3"
            audio_path.touch()
            
            video_gen = VideoGenerator()
            video_gen.output_dir = work_dir / "output"
            
            with patch.object(Path, 'rename') as mock_rename:
                result = video_gen._compose_video(
                    slides, audio_path, 120.0, work_dir, "test_job"
                )
                
                # Verify FFmpeg was called
                mock_subprocess.assert_called_once()
                
                # Verify command structure
                call_args = mock_subprocess.call_args[0][0]
                self.assertEqual(call_args[0], 'ffmpeg')
                self.assertIn('-y', call_args)  # Overwrite flag
                
                # Verify rename was called
                mock_rename.assert_called_once()
                
                expected_path = video_gen.output_dir / "test_job.mp4"
                self.assertEqual(result, expected_path)
    
    @patch('subprocess.run')
    def test_compose_video_ffmpeg_error(self, mock_subprocess):
        """Test video composition handles FFmpeg error"""
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            1, 'ffmpeg', stderr="FFmpeg error"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            slides = [work_dir / "slide1.png"]
            audio_path = work_dir / "audio.mp3"
            
            # Create mock files
            slides[0].touch()
            audio_path.touch()
            
            video_gen = VideoGenerator()
            
            with self.assertRaises(subprocess.CalledProcessError):
                video_gen._compose_video(
                    slides, audio_path, 60.0, work_dir, "test_job"
                )
    
    @patch('subprocess.run')
    def test_compose_video_command_structure(self, mock_subprocess):
        """Test FFmpeg command structure is correct"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            slides = [
                work_dir / "slide1.png",
                work_dir / "slide2.png",
                work_dir / "slide3.png"
            ]
            
            # Create mock files
            for slide in slides:
                slide.touch()
            
            audio_path = work_dir / "audio.mp3"
            audio_path.touch()
            
            video_gen = VideoGenerator()
            video_gen.output_dir = work_dir / "output"
            
            with patch.object(Path, 'rename'):
                video_gen._compose_video(
                    slides, audio_path, 90.0, work_dir, "test_job"
                )
                
                # Verify FFmpeg command structure
                call_args = mock_subprocess.call_args[0][0]
                
                # Should have ffmpeg command
                self.assertEqual(call_args[0], 'ffmpeg')
                
                # Should have overwrite flag
                self.assertIn('-y', call_args)
                
                # Should have inputs for each slide
                slide_inputs = [i for i, arg in enumerate(call_args) if arg == '-i']
                # 3 slides + 1 audio = 4 inputs
                self.assertEqual(len(slide_inputs), 4)
                
                # Should have filter complex
                self.assertIn('-filter_complex', call_args)
                
                # Should have codec settings
                self.assertIn('-c:v', call_args)
                self.assertIn('libx264', call_args)
                self.assertIn('-c:a', call_args)
                self.assertIn('aac', call_args)
    
    @patch('subprocess.run')
    def test_compose_video_duration_calculation(self, mock_subprocess):
        """Test slide duration calculation"""
        mock_subprocess.return_value = Mock(returncode=0)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            work_dir = Path(temp_dir)
            slides = [
                work_dir / "slide1.png",
                work_dir / "slide2.png"
            ]
            
            for slide in slides:
                slide.touch()
            
            audio_path = work_dir / "audio.mp3"
            audio_path.touch()
            
            video_gen = VideoGenerator()
            video_gen.output_dir = work_dir / "output"
            
            with patch.object(Path, 'rename'):
                video_gen._compose_video(
                    slides, audio_path, 100.0, work_dir, "test_job"
                )
                
                # Verify duration per slide calculation
                call_args = mock_subprocess.call_args[0][0]
                
                # Find -t arguments (duration)
                duration_indices = [i+1 for i, arg in enumerate(call_args) if arg == '-t']
                
                # Should have 2 duration arguments (one per slide)
                self.assertEqual(len(duration_indices), 2)
                
                # Each slide should get 50.0 seconds (100.0 / 2)
                for idx in duration_indices:
                    self.assertEqual(call_args[idx], '50.0')
    
    def test_compose_video_filter_generation(self):
        """Test FFmpeg filter generation"""
        video_gen = VideoGenerator()
        
        # Test with different numbers of slides
        test_cases = [
            (2, "concat=n=2:v=1:a=0,fps=30[v]"),
            (5, "concat=n=5:v=1:a=0,fps=30[v]"),
            (1, "concat=n=1:v=1:a=0,fps=30[v]")
        ]
        
        for num_slides, expected_filter in test_cases:
            with self.subTest(num_slides=num_slides):
                with tempfile.TemporaryDirectory() as temp_dir:
                    work_dir = Path(temp_dir)
                    slides = [work_dir / f"slide{i}.png" for i in range(num_slides)]
                    
                    for slide in slides:
                        slide.touch()
                    
                    audio_path = work_dir / "audio.mp3"
                    audio_path.touch()
                    
                    with patch('subprocess.run') as mock_subprocess, \
                         patch.object(Path, 'rename'):
                        
                        mock_subprocess.return_value = Mock(returncode=0)
                        video_gen.output_dir = work_dir / "output"
                        
                        video_gen._compose_video(
                            slides, audio_path, 60.0, work_dir, "test_job"
                        )
                        
                        call_args = mock_subprocess.call_args[0][0]
                        filter_idx = call_args.index('-filter_complex') + 1
                        actual_filter = call_args[filter_idx]
                        
                        self.assertEqual(actual_filter, expected_filter)


if __name__ == "__main__":
    unittest.main()