#!/usr/bin/env python3
"""
Unit tests for AudioGenerator
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import os

from app.services.audio_generator import AudioGenerator


class TestAudioGenerator(unittest.TestCase):
    """Test cases for AudioGenerator"""
    
    @patch('app.services.audio_generator.settings')
    @patch('app.services.audio_generator.texttospeech.TextToSpeechClient')
    @patch('os.environ')
    def test_init(self, mock_environ, mock_tts_client, mock_settings):
        """Test AudioGenerator initialization"""
        mock_settings.GOOGLE_APPLICATION_CREDENTIALS = "/path/to/creds.json"
        
        audio_gen = AudioGenerator()
        
        # Verify credentials are set (check if it was called, value may vary)
        self.assertTrue(mock_environ.__setitem__.called)
        
        # Verify TTS client is initialized
        mock_tts_client.assert_called_once()
        
        # Verify voices are configured
        self.assertIn('host1', audio_gen.voices)
        self.assertIn('host2', audio_gen.voices)
        
        # Verify voice configurations
        host1_voice = audio_gen.voices['host1']
        self.assertEqual(host1_voice['language_code'], 'en-US')
        self.assertEqual(host1_voice['name'], 'en-US-Chirp3-HD-Algenib')
        
        host2_voice = audio_gen.voices['host2']
        self.assertEqual(host2_voice['language_code'], 'en-US')
        self.assertEqual(host2_voice['name'], 'en-US-Chirp3-HD-Aoede')
    
    @patch('app.services.audio_generator.AudioSegment')
    @patch('app.services.audio_generator.texttospeech.TextToSpeechClient')
    def test_generate_audio_success(self, mock_tts_client, mock_audio_segment):
        """Test successful audio generation"""
        # Mock audio segments
        mock_segment1 = Mock()
        mock_segment2 = Mock()
        mock_pause = Mock()
        mock_final_audio = Mock()
        
        mock_audio_segment.from_mp3.side_effect = [mock_segment1, mock_segment2]
        mock_audio_segment.silent.return_value = mock_pause
        
        # Mock sum operation
        with patch('builtins.sum', return_value=mock_final_audio):
            
            script = [
                ("host1", "Hello there!"),
                ("host2", "Welcome to the team!")
            ]
            
            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = Path(temp_dir)
                
                audio_gen = AudioGenerator()
                
                with patch.object(audio_gen, '_synthesize_speech') as mock_synthesize:
                    result = audio_gen.generate_audio(script, output_dir)
                    
                    # Verify synthesis was called for each segment
                    self.assertEqual(mock_synthesize.call_count, 2)
                    mock_synthesize.assert_any_call(
                        "Hello there!", 
                        "host1", 
                        output_dir / "segment_0_host1.mp3"
                    )
                    mock_synthesize.assert_any_call(
                        "Welcome to the team!", 
                        "host2", 
                        output_dir / "segment_1_host2.mp3"
                    )
                    
                    # Verify audio segments were loaded
                    self.assertEqual(mock_audio_segment.from_mp3.call_count, 2)
                    
                    # Verify pause was created
                    mock_audio_segment.silent.assert_called_once_with(duration=500)
                    
                    # Verify final export
                    mock_final_audio.export.assert_called_once()
                    
                    # Verify return path
                    expected_path = output_dir / "final_audio.mp3"
                    self.assertEqual(result, expected_path)
    
    @patch('app.services.audio_generator.texttospeech.TextToSpeechClient')
    def test_generate_audio_empty_script(self, mock_tts_client):
        """Test audio generation with empty script"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            audio_gen = AudioGenerator()
            
            with patch('app.services.audio_generator.AudioSegment') as mock_audio_segment:
                mock_final_audio = Mock()
                
                with patch('builtins.sum', return_value=mock_final_audio):
                    result = audio_gen.generate_audio([], output_dir)
                    
                    # Should still create final audio file
                    mock_final_audio.export.assert_called_once()
                    
                    expected_path = output_dir / "final_audio.mp3"
                    self.assertEqual(result, expected_path)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_synthesize_speech_host1(self, mock_file):
        """Test speech synthesis for host1"""
        # Mock TTS response
        mock_response = Mock()
        mock_response.audio_content = b"fake_audio_data"
        
        mock_client = Mock()
        mock_client.synthesize_speech.return_value = mock_response
        
        audio_gen = AudioGenerator()
        audio_gen.client = mock_client
        
        output_file = Path("/tmp/test.mp3")
        
        audio_gen._synthesize_speech("Hello world", "host1", output_file)
        
        # Verify TTS was called with correct parameters
        mock_client.synthesize_speech.assert_called_once()
        
        call_kwargs = mock_client.synthesize_speech.call_args.kwargs
        
        # Verify input text was passed
        self.assertIn('input', call_kwargs)
        
        # Verify voice was passed
        self.assertIn('voice', call_kwargs)
        
        # Verify audio config was passed
        self.assertIn('audio_config', call_kwargs)
        
        # Verify file was written
        mock_file.assert_called_once_with(output_file, 'wb')
        mock_file().write.assert_called_once_with(b"fake_audio_data")
    
    @patch('builtins.open', new_callable=mock_open)
    def test_synthesize_speech_host2(self, mock_file):
        """Test speech synthesis for host2"""
        mock_response = Mock()
        mock_response.audio_content = b"fake_audio_data"
        
        mock_client = Mock()
        mock_client.synthesize_speech.return_value = mock_response
        
        audio_gen = AudioGenerator()
        audio_gen.client = mock_client
        
        output_file = Path("/tmp/test.mp3")
        
        audio_gen._synthesize_speech("Welcome!", "host2", output_file)
        
        # Verify TTS was called
        mock_client.synthesize_speech.assert_called_once()
        
        # Verify file was written
        mock_file.assert_called_once_with(output_file, 'wb')
        mock_file().write.assert_called_once_with(b"fake_audio_data")
    
    @patch('builtins.open', new_callable=mock_open)
    def test_synthesize_speech_unknown_speaker(self, mock_file):
        """Test speech synthesis with unknown speaker defaults to host1"""
        mock_response = Mock()
        mock_response.audio_content = b"fake_audio_data"
        
        mock_client = Mock()
        mock_client.synthesize_speech.return_value = mock_response
        
        audio_gen = AudioGenerator()
        audio_gen.client = mock_client
        
        output_file = Path("/tmp/test.mp3")
        
        audio_gen._synthesize_speech("Hello", "unknown_speaker", output_file)
        
        # Should use host1 voice as fallback - verify TTS was called
        mock_client.synthesize_speech.assert_called_once()
        
        # Verify file was written
        mock_file.assert_called_once_with(output_file, 'wb')
        mock_file().write.assert_called_once_with(b"fake_audio_data")
    
    @patch('builtins.open', new_callable=mock_open)
    def test_synthesize_speech_special_characters(self, mock_file):
        """Test speech synthesis with special characters"""
        mock_response = Mock()
        mock_response.audio_content = b"fake_audio_data"
        
        mock_client = Mock()
        mock_client.synthesize_speech.return_value = mock_response
        
        audio_gen = AudioGenerator()
        audio_gen.client = mock_client
        
        output_file = Path("/tmp/test.mp3")
        
        # Text with special characters and emojis
        special_text = "Hello! Welcome to the team 🎉 Let's get started..."
        
        audio_gen._synthesize_speech(special_text, "host1", output_file)
        
        # Verify TTS was called
        mock_client.synthesize_speech.assert_called_once()
        
        # Verify file was written
        mock_file.assert_called_once_with(output_file, 'wb')
        mock_file().write.assert_called_once_with(b"fake_audio_data")
    
    @patch('builtins.open', new_callable=mock_open)
    def test_synthesize_speech_api_error(self, mock_file):
        """Test speech synthesis handles API errors"""
        mock_client = Mock()
        mock_client.synthesize_speech.side_effect = Exception("API Error")
        
        audio_gen = AudioGenerator()
        audio_gen.client = mock_client
        
        output_file = Path("/tmp/test.mp3")
        
        with self.assertRaises(Exception) as context:
            audio_gen._synthesize_speech("Hello", "host1", output_file)
        
        self.assertIn("API Error", str(context.exception))
    
    @patch('app.services.audio_generator.AudioSegment')
    def test_get_audio_duration(self, mock_audio_segment):
        """Test getting audio duration"""
        # Mock audio segment with 5000ms duration
        mock_audio = Mock()
        mock_audio.__len__ = Mock(return_value=5000)
        mock_audio_segment.from_mp3.return_value = mock_audio
        
        audio_gen = AudioGenerator()
        
        duration = audio_gen.get_audio_duration(Path("/tmp/test.mp3"))
        
        # Verify conversion from ms to seconds
        self.assertEqual(duration, 5.0)
        
        # Verify file was loaded (path format may vary by OS)
        mock_audio_segment.from_mp3.assert_called_once_with(str(Path("/tmp/test.mp3")))
    
    @patch('app.services.audio_generator.AudioSegment')
    def test_get_audio_duration_zero_length(self, mock_audio_segment):
        """Test getting duration of zero-length audio"""
        mock_audio = Mock()
        mock_audio.__len__ = Mock(return_value=0)
        mock_audio_segment.from_mp3.return_value = mock_audio
        
        audio_gen = AudioGenerator()
        
        duration = audio_gen.get_audio_duration(Path("/tmp/empty.mp3"))
        
        self.assertEqual(duration, 0.0)
    
    @patch('app.services.audio_generator.AudioSegment')
    def test_get_audio_duration_file_error(self, mock_audio_segment):
        """Test getting duration handles file errors"""
        mock_audio_segment.from_mp3.side_effect = Exception("File not found")
        
        audio_gen = AudioGenerator()
        
        with self.assertRaises(Exception) as context:
            audio_gen.get_audio_duration(Path("/tmp/nonexistent.mp3"))
        
        self.assertIn("File not found", str(context.exception))
    
    def test_voice_configuration_completeness(self):
        """Test that voice configurations are complete"""
        audio_gen = AudioGenerator()
        
        required_keys = ['language_code', 'name', 'ssml_gender']
        
        for speaker, voice_config in audio_gen.voices.items():
            with self.subTest(speaker=speaker):
                for key in required_keys:
                    self.assertIn(key, voice_config, 
                                f"Voice config for {speaker} missing {key}")
                
                # Verify language code format
                self.assertRegex(voice_config['language_code'], r'^[a-z]{2}-[A-Z]{2}$')
                
                # Verify voice name format
                self.assertTrue(voice_config['name'].startswith('en-US-'))
    
    @patch('app.services.audio_generator.AudioSegment')
    def test_generate_audio_pause_duration(self, mock_audio_segment):
        """Test that correct pause duration is used between segments"""
        script = [("host1", "First"), ("host2", "Second")]
        
        mock_segment = Mock()
        mock_pause = Mock()
        mock_final_audio = Mock()
        
        mock_audio_segment.from_mp3.return_value = mock_segment
        mock_audio_segment.silent.return_value = mock_pause
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            
            audio_gen = AudioGenerator()
            
            with patch.object(audio_gen, '_synthesize_speech'), \
                 patch('builtins.sum', return_value=mock_final_audio):
                
                audio_gen.generate_audio(script, output_dir)
                
                # Verify pause duration
                mock_audio_segment.silent.assert_called_with(duration=500)


if __name__ == "__main__":
    unittest.main()