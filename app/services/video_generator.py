import logging
import subprocess
from pathlib import Path
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont
from app.models.webhook import EmployeeData
from app.services.script_generator import ScriptGenerator
from app.services.audio_generator import AudioGenerator
from app.config import settings

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        self.script_gen = ScriptGenerator()
        self.audio_gen = AudioGenerator()
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        
        # Video settings
        self.width = 1920
        self.height = 1080
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
            self._save_script_for_dev(script, employee_data, dev_dir)
            
            # Step 2: Generate audio
            logger.info("Generating audio...")
            audio_path = self.audio_gen.generate_audio(script, work_dir)
            audio_duration = self.audio_gen.get_audio_duration(audio_path)
            
            # Copy audio to dev folder
            self._copy_audio_for_dev(audio_path, dev_dir)
            
            # Step 3: Create visual slides
            logger.info("Creating visual slides...")
            slides = self._create_slides(employee_data, script, work_dir)
            
            # Copy slides to dev folder
            self._copy_slides_for_dev(slides, dev_dir)
            
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
            self._copy_video_for_dev(video_path, dev_dir)
            
            # Create summary file
            self._create_dev_summary(employee_data, script, audio_duration, dev_dir)
            
            logger.info(f"Video generation complete: {video_path}")
            logger.info(f"Development files saved to: {dev_dir}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error in video generation: {str(e)}")
            raise
    
    def _create_slides(
        self, 
        employee_data: EmployeeData,
        script: List[Tuple[str, str]],
        work_dir: Path
    ) -> List[Path]:
        """Create visual slides for the video"""
        slides = []
        
        # Slide 1: Welcome
        slide1 = self._create_welcome_slide(employee_data, work_dir / "slide_1.png")
        slides.append(slide1)
        
        # Slide 2: Team & Role
        slide2 = self._create_role_slide(employee_data, work_dir / "slide_2.png")
        slides.append(slide2)
        
        # Slide 3: Tech Stack
        slide3 = self._create_tech_slide(employee_data, work_dir / "slide_3.png")
        slides.append(slide3)
        
        # Slide 4: Schedule
        slide4 = self._create_schedule_slide(employee_data, work_dir / "slide_4.png")
        slides.append(slide4)
        
        # Slide 5: Closing
        slide5 = self._create_closing_slide(employee_data, work_dir / "slide_5.png")
        slides.append(slide5)
        
        return slides
    
    def _create_welcome_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create welcome slide"""
        img = Image.new('RGB', (self.width, self.height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # Try to load a nice font, fallback to default
        try:
            # Windows font paths
            title_font = ImageFont.truetype("arial.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 50)
        except:
            try:
                # Alternative Windows fonts
                title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 80)
                subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 50)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
        
        # Title
        title = f"Welcome, {employee_data.name.split()[0]}!"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((self.width - title_width) / 2, 400),
            title,
            fill='#ffffff',
            font=title_font
        )
        
        # Subtitle
        subtitle = employee_data.position
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(
            ((self.width - subtitle_width) / 2, 550),
            subtitle,
            fill='#16c79a',
            font=subtitle_font
        )
        
        img.save(path)
        return path
    
    def _create_role_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create role/team slide"""
        img = Image.new('RGB', (self.width, self.height), color='#0f3460')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 45)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 45)
            except:
                font = ImageFont.load_default()
        
        y_position = 300
        line_height = 80
        
        info = [
            f"Team: {employee_data.team}",
            f"Manager: {employee_data.manager}",
            f"Office: {employee_data.office}",
            f"Start Date: {employee_data.start_date}"
        ]
        
        for line in info:
            draw.text((200, y_position), line, fill='#ffffff', font=font)
            y_position += line_height
        
        img.save(path)
        return path
    
    def _create_tech_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create tech stack slide"""
        img = Image.new('RGB', (self.width, self.height), color='#16213e')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
            item_font = ImageFont.truetype("arial.ttf", 40)
        except:
            try:
                title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
                item_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 40)
            except:
                title_font = ImageFont.load_default()
                item_font = ImageFont.load_default()
        
        draw.text((200, 200), "Your Tech Stack", fill='#16c79a', font=title_font)
        
        y_position = 350
        for tech in employee_data.tech_stack:
            draw.text((250, y_position), f"• {tech}", fill='#ffffff', font=item_font)
            y_position += 70
        
        img.save(path)
        return path
    
    def _create_schedule_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create schedule slide"""
        img = Image.new('RGB', (self.width, self.height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
            item_font = ImageFont.truetype("arial.ttf", 35)
        except:
            try:
                title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 60)
                item_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 35)
            except:
                title_font = ImageFont.load_default()
                item_font = ImageFont.load_default()
        
        draw.text((200, 150), "First Day Schedule", fill='#16c79a', font=title_font)
        
        y_position = 300
        for item in employee_data.first_day_schedule[:5]:  # Show first 5 items
            text = f"{item.time} - {item.activity}"
            draw.text((200, y_position), text, fill='#ffffff', font=item_font)
            y_position += 60
        
        img.save(path)
        return path
    
    def _create_closing_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create closing slide"""
        img = Image.new('RGB', (self.width, self.height), color='#0f3460')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 70)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 70)
            except:
                font = ImageFont.load_default()
        
        text = "See you soon!"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(
            ((self.width - text_width) / 2, 450),
            text,
            fill='#16c79a',
            font=font
        )
        
        img.save(path)
        return path
    
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
    
    def _save_script_for_dev(self, script: List[Tuple[str, str]], employee_data: EmployeeData, dev_dir: Path) -> None:
        """Save script in readable format for development review"""
        script_file = dev_dir / "script.txt"
        
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write("ONBOARDING VIDEO SCRIPT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Employee: {employee_data.name}\n")
            f.write(f"Position: {employee_data.position}\n")
            f.write(f"Team: {employee_data.team}\n")
            f.write(f"Manager: {employee_data.manager}\n")
            f.write(f"Start Date: {employee_data.start_date}\n\n")
            f.write("SCRIPT:\n")
            f.write("-" * 30 + "\n\n")
            
            for i, (speaker, text) in enumerate(script, 1):
                speaker_name = "Alex" if speaker == "host1" else "Jordan"
                f.write(f"{i}. {speaker_name.upper()}:\n")
                f.write(f"   {text}\n\n")
            
            f.write(f"\nTotal script lines: {len(script)}\n")
        
        logger.info(f"Script saved to: {script_file}")
    
    def _copy_audio_for_dev(self, audio_path: Path, dev_dir: Path) -> None:
        """Copy audio file to development folder"""
        import shutil
        
        dev_audio_path = dev_dir / "final_audio.mp3"
        shutil.copy2(audio_path, dev_audio_path)
        logger.info(f"Audio copied to: {dev_audio_path}")
    
    def _copy_slides_for_dev(self, slides: List[Path], dev_dir: Path) -> None:
        """Copy slide images to development folder"""
        import shutil
        
        slides_dir = dev_dir / "slides"
        slides_dir.mkdir(exist_ok=True)
        
        slide_names = [
            "01_welcome.png",
            "02_role_team.png", 
            "03_tech_stack.png",
            "04_schedule.png",
            "05_closing.png"
        ]
        
        for i, slide_path in enumerate(slides):
            if i < len(slide_names):
                dev_slide_path = slides_dir / slide_names[i]
                shutil.copy2(slide_path, dev_slide_path)
                logger.info(f"Slide {i+1} copied to: {dev_slide_path}")
    
    def _copy_video_for_dev(self, video_path: Path, dev_dir: Path) -> None:
        """Copy final video to development folder"""
        import shutil
        
        dev_video_path = dev_dir / "final_video.mp4"
        shutil.copy2(video_path, dev_video_path)
        logger.info(f"Video copied to: {dev_video_path}")
    
    def _create_dev_summary(self, employee_data: EmployeeData, script: List[Tuple[str, str]], 
                           audio_duration: float, dev_dir: Path) -> None:
        """Create a summary file with all the details"""
        summary_file = dev_dir / "summary.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Onboarding Video Generation Summary\n\n")
            
            f.write("## Employee Information\n")
            f.write(f"- **Name:** {employee_data.name}\n")
            f.write(f"- **Position:** {employee_data.position}\n")
            f.write(f"- **Team:** {employee_data.team}\n")
            f.write(f"- **Manager:** {employee_data.manager}\n")
            f.write(f"- **Start Date:** {employee_data.start_date}\n")
            f.write(f"- **Office:** {employee_data.office}\n")
            if employee_data.department:
                f.write(f"- **Department:** {employee_data.department}\n")
            if employee_data.buddy:
                f.write(f"- **Buddy:** {employee_data.buddy}\n")
            f.write("\n")
            
            f.write("## Tech Stack\n")
            for tech in employee_data.tech_stack:
                f.write(f"- {tech}\n")
            f.write("\n")
            
            f.write("## First Day Schedule\n")
            for item in employee_data.first_day_schedule:
                f.write(f"- **{item.time}:** {item.activity}")
                if hasattr(item, 'location') and item.location:
                    f.write(f" (Location: {item.location})")
                f.write("\n")
            f.write("\n")
            
            f.write("## First Week Overview\n")
            for day, activity in employee_data.first_week_schedule.items():
                f.write(f"- **{day}:** {activity}\n")
            f.write("\n")
            
            f.write("## Video Details\n")
            f.write(f"- **Script Lines:** {len(script)}\n")
            f.write(f"- **Audio Duration:** {audio_duration:.2f} seconds ({audio_duration/60:.1f} minutes)\n")
            f.write(f"- **Slides:** 5 slides\n")
            f.write("\n")
            
            f.write("## Files Generated\n")
            f.write("- `script.txt` - Full script with speaker assignments\n")
            f.write("- `final_audio.mp3` - Complete audio track\n")
            f.write("- `slides/` - Individual slide images\n")
            f.write("- `final_video.mp4` - Complete video\n")
            f.write("- `summary.md` - This summary file\n")
        
        logger.info(f"Summary saved to: {summary_file}")