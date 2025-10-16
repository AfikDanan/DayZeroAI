import logging
import shutil
from pathlib import Path
from typing import List, Tuple
from app.models.webhook import EmployeeData

logger = logging.getLogger(__name__)

class DevUtils:
    """Utilities for development and debugging"""
    
    @staticmethod
    def save_script_for_dev(
        script: List[Tuple[str, str]], 
        employee_data: EmployeeData, 
        dev_dir: Path
    ) -> None:
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
    
    @staticmethod
    def copy_audio_for_dev(audio_path: Path, dev_dir: Path) -> None:
        """Copy audio file to development folder"""
        dev_audio_path = dev_dir / "final_audio.mp3"
        shutil.copy2(audio_path, dev_audio_path)
        logger.info(f"Audio copied to: {dev_audio_path}")
    
    @staticmethod
    def copy_slides_for_dev(slides: List[Path], dev_dir: Path) -> None:
        """Copy slide images to development folder"""
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
    
    @staticmethod
    def copy_video_for_dev(video_path: Path, dev_dir: Path) -> None:
        """Copy final video to development folder"""
        dev_video_path = dev_dir / "final_video.mp4"
        shutil.copy2(video_path, dev_video_path)
        logger.info(f"Video copied to: {dev_video_path}")
    
    @staticmethod
    def create_dev_summary(
        employee_data: EmployeeData, 
        script: List[Tuple[str, str]], 
        audio_duration: float, 
        dev_dir: Path
    ) -> None:
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