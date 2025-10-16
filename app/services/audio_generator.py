import logging
from pathlib import Path
from typing import List, Tuple
from google.cloud import texttospeech
from pydub import AudioSegment
from app.config import settings

logger = logging.getLogger(__name__)

class AudioGenerator:
    def __init__(self):
        # Ensure credentials are set correctly
        import os
        from app.config import settings
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        self.client = texttospeech.TextToSpeechClient()
        
        # Configure voices for each host
        self.voices = {
            'host1': {
                'language_code': 'en-US',
                'name': 'en-US-Chirp3-HD-Algenib',  # Male voice
                'ssml_gender': texttospeech.SsmlVoiceGender.MALE
            },
            'host2': {
                'language_code': 'en-US',
                'name': 'en-US-Chirp3-HD-Aoede',  # Female voice
                'ssml_gender': texttospeech.SsmlVoiceGender.FEMALE
            }
        }
    
    def generate_audio(
        self, 
        script: List[Tuple[str, str]], 
        output_dir: Path
    ) -> Path:
        """
        Generate audio from script and combine into single file
        Returns path to final audio file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_segments = []
        pause = AudioSegment.silent(duration=500)  # 500ms pause between speakers
        
        for idx, (speaker, text) in enumerate(script):
            audio_file = output_dir / f"segment_{idx}_{speaker}.mp3"
            
            # Generate audio for this segment
            self._synthesize_speech(text, speaker, audio_file)
            
            # Load and add to segments
            segment = AudioSegment.from_mp3(str(audio_file))
            audio_segments.append(segment)
            audio_segments.append(pause)
            
            logger.info(f"Generated audio segment {idx} for {speaker}")
        
        # Combine all segments
        final_audio = sum(audio_segments)
        final_path = output_dir / "final_audio.mp3"
        final_audio.export(str(final_path), format="mp3", bitrate="192k")
        
        logger.info(f"Combined audio saved to {final_path}")
        return final_path
    
    def _synthesize_speech(
        self, 
        text: str, 
        speaker: str, 
        output_file: Path
    ) -> None:
        """Synthesize speech for a single text segment"""
        
        voice_config = self.voices.get(speaker, self.voices['host1'])
        
        # Set the text input
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # Build voice parameters
        voice = texttospeech.VoiceSelectionParams(
            language_code=voice_config['language_code'],
            name=voice_config['name'],
            ssml_gender=voice_config['ssml_gender']
        )
        
        # Select audio format
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # Normal speed
            pitch=0.0  # Normal pitch
        )
        
        # Perform the text-to-speech request
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Write the response to file
        with open(output_file, 'wb') as out:
            out.write(response.audio_content)
    
    def get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds"""
        audio = AudioSegment.from_mp3(str(audio_path))
        return len(audio) / 1000.0  # Convert ms to seconds