import logging
import subprocess
from pathlib import Path
from typing import List, Tuple
from app.models.webhook import EmployeeData
from app.services.script_generator import ScriptGenerator
from app.services.audio_generator import AudioGenerator
from app.services.slide_generator import SlideGenerator
from app.services.dev_utils import DevUtils
from app.config import settings

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.audio_gen = AudioGenerator()
        self.slide_gen = SlideGenerator()
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        
        # Video settings
        self.fps = 30
    
    def generate_onboarding_video(
        self, 
        employee_data: EmployeeData, 
        job_id: str
    ) -> Path:
        """
        Complete video generation pipeline
        Returns path to generated video
        """
        logger.info(f"Starting video generation for job {job_id}")
        
        work_dir = self.temp_dir / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Create development output directory
        dev_dir = Path(settings.DEV_OUTPUT_DIR) / job_id
        dev_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 1: Generate script
            logger.info("Generating script...")
            script = self.script_gen.generate_onboarding_script(employee_data)
            
            # Save script for development review
            self.script_gen.save_script_for_dev(script, employee_data, dev_dir)
            
            # Step 2: Generate audio
            logger.info("Generating audio...")
            audio_path = self.audio_gen.generate_audio(script, work_dir)
            audio_duration = self.audio_gen.get_audio_duration(audio_path)
            
            # Copy audio to dev folder
            DevUtils.copy_audio_for_dev(audio_path, dev_dir)
            
            # Step 3: Create visual slides
            logger.info("Creating visual slides...")
            slides = self.slide_gen.create_slides(employee_data, work_dir)
            
            # Copy slides to dev folder
            DevUtils.copy_slides_for_dev(slides, dev_dir)
            
            # Step 4: Compose video
            logger.info("Composing final video...")
            video_path = self._compose_video(
                slides, 
                audio_path, 
                audio_duration,
                work_dir,
                job_id
            )
            
            # Copy final video to dev folder
            DevUtils.copy_video_for_dev(video_path, dev_dir)
            
            # Create summary file
            DevUtils.create_dev_summary(employee_data, script, audio_duration, dev_dir)
            
            logger.info(f"Video generation complete: {video_path}")
            logger.info(f"Development files saved to: {dev_dir}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error in video generation: {str(e)}")
            raise
    

    
    def _compose_video(
        self,
        slides: List[Path],
        audio_path: Path,
        audio_duration: float,
        work_dir: Path,
        job_id: str
    ) -> Path:
        """Compose final video using FFmpeg"""
        
        # Calculate duration per slide
        slide_duration = audio_duration / len(slides)
        
        # Create video from slides
        slides_video = work_dir / "slides.mp4"
        
        # Build FFmpeg filter for crossfading between slides
        filter_parts = []
        for i, slide in enumerate(slides):
            filter_parts.append(f"[{i}:v]")
        
        # Simple concatenation (for MVP - can add crossfades later)
        concat_filter = f"concat=n={len(slides)}:v=1:a=0,fps={self.fps}[v]"
        
        # FFmpeg command to create video from slides
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
        ]
        
        # Add all slides as inputs
        for slide in slides:
            cmd.extend([
                '-loop', '1',
                '-t', str(slide_duration),
                '-i', str(slide)
            ])
        
        # Add audio
        cmd.extend([
            '-i', str(audio_path),
            '-filter_complex', concat_filter,
            '-map', '[v]',
            '-map', f'{len(slides)}:a',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-shortest',
            str(slides_video)
        ])
        
        # Run FFmpeg
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("FFmpeg completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise
        
        # Move to final output location
        final_path = self.output_dir / f"{job_id}.mp4"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        slides_video.rename(final_path)
        
        return final_path