import logging
from pathlib import Path
from typing import List
from PIL import Image, ImageDraw, ImageFont
from app.models.webhook import EmployeeData

logger = logging.getLogger(__name__)

class SlideGenerator:
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
    
    def _load_template_background(self) -> Image.Image:
        """Load template background image with fallback"""
        try:
            template_path = Path("app/utils/static/template.png")
            img = Image.open(template_path).convert('RGB')
            
            # Resize if needed to match video dimensions
            if img.size != (self.width, self.height):
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            
            return img
        except Exception:
            # Fallback to simple background if template not found
            return Image.new('RGB', (self.width, self.height), color='#f8f7fc')
    
    def _load_fonts(self, title_size: int = 90, subtitle_size: int = 48) -> tuple:
        """Load fonts with fallback options"""
        try:
            title_font = ImageFont.truetype("arial.ttf", title_size)
            subtitle_font = ImageFont.truetype("arial.ttf", subtitle_size)
            return title_font, subtitle_font
        except Exception:
            try:
                title_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", title_size)
                subtitle_font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", subtitle_size)
                return title_font, subtitle_font
            except Exception:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                return title_font, subtitle_font
    
    def _load_font(self, size: int) -> ImageFont.ImageFont:
        """Load a single font with fallback options"""
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            try:
                return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", size)
            except Exception:
                return ImageFont.load_default()
    
    def create_slides(
        self, 
        employee_data: EmployeeData,
        work_dir: Path
    ) -> List[Path]:
        """Create all visual slides for the video"""
        slides = []
        
        # Slide 1: Welcome
        slide1 = self.create_welcome_slide(employee_data, work_dir / "slide_1.png")
        slides.append(slide1)
        
        # Slide 2: Team & Role
        slide2 = self.create_role_slide(employee_data, work_dir / "slide_2.png")
        slides.append(slide2)
        
        # Slide 3: Tech Stack
        slide3 = self.create_tech_slide(employee_data, work_dir / "slide_3.png")
        slides.append(slide3)
        
        # Slide 4: Schedule
        slide4 = self.create_schedule_slide(employee_data, work_dir / "slide_4.png")
        slides.append(slide4)
        
        # Slide 5: Closing
        slide5 = self.create_closing_slide(employee_data, work_dir / "slide_5.png")
        slides.append(slide5)
        
        return slides

    def create_welcome_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create welcome slide using template background"""
        img = self._load_template_background()
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        title_font, subtitle_font = self._load_fonts(90, 48)
        
        # Add the personalized text
        # Title - adjust Y position based on where you want text on your template
        first_name = employee_data.name.split()[0]
        title = f"Welcome, {first_name}!"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(
            ((self.width - title_width) / 2, 450),  # Adjust Y position as needed
            title,
            fill='#1e293b',  # Adjust color to match your template
            font=title_font
        )
        
        # Subtitle - Position
        subtitle = employee_data.position
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(
            ((self.width - subtitle_width) / 2, 600),  # Adjust Y position as needed
            subtitle,
            fill='#22c55e',  # Adjust color to match your template
            font=subtitle_font
        )
        
        img.save(path)
        return path
    
    def create_role_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create role/team slide"""
        img = self._load_template_background()
        draw = ImageDraw.Draw(img)
        
        font = self._load_font(45)
        
        y_position = 300
        line_height = 80
        
        info = [
            f"Team: {employee_data.team}",
            f"Manager: {employee_data.manager}",
            f"Office: {employee_data.office}",
            f"Start Date: {employee_data.start_date}"
        ]
        
        for line in info:
            draw.text((200, y_position), line, fill='#1e293b', font=font)
            y_position += line_height
        
        img.save(path)
        return path
    
    def create_tech_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create tech stack slide"""
        img = self._load_template_background()
        draw = ImageDraw.Draw(img)
        
        title_font = self._load_font(60)
        item_font = self._load_font(40)
        
        draw.text((200, 200), "Your Tech Stack", fill='#16c79a', font=title_font)
        
        y_position = 350
        for tech in employee_data.tech_stack:
            draw.text((250, y_position), f"• {tech}", fill='#1e293b', font=item_font)
            y_position += 70
        
        img.save(path)
        return path
    
    def create_schedule_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create schedule slide"""
        img = self._load_template_background()
        draw = ImageDraw.Draw(img)
        
        title_font = self._load_font(60)
        item_font = self._load_font(35)
        
        draw.text((200, 150), "First Day Schedule", fill='#16c79a', font=title_font)
        
        y_position = 300
        for item in employee_data.first_day_schedule[:5]:  # Show first 5 items
            text = f"{item.time} - {item.activity}"
            draw.text((200, y_position), text, fill='#1e293b', font=item_font)
            y_position += 60
        
        img.save(path)
        return path
    
    def create_closing_slide(self, employee_data: EmployeeData, path: Path) -> Path:
        """Create closing slide"""
        img = self._load_template_background()
        draw = ImageDraw.Draw(img)
        
        font = self._load_font(70)
        
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