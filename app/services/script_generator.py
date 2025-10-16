import logging
from pathlib import Path
from typing import List, Tuple
from openai import OpenAI
from app.models.webhook import EmployeeData
from app.config import settings

logger = logging.getLogger(__name__)

class ScriptGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
    def generate_onboarding_script(
        self, 
        employee_data: EmployeeData
    ) -> List[Tuple[str, str]]:
        """
        Generate conversational script for onboarding video
        Returns list of tuples: [(speaker, text), ...]
        speaker is either "host1" or "host2"
        """
        
        prompt = self._build_prompt(employee_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective choice
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            script_text = response.choices[0].message.content
            script = self._parse_script(script_text)
            
            logger.info(
                f"Generated script with {len(script)} lines "
                f"for {employee_data.name}"
            )
            
            return script
            
        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise
    
    def _get_system_prompt(self) -> str:
        return """You are a creative script writer for onboarding videos. 
        Create a warm, engaging conversation between two friendly AI hosts 
        (Alex and Jordan) discussing a new employee's onboarding.
        
        Guidelines:
        - Keep it conversational and natural
        - Use a welcoming, enthusiastic tone
        - Each speaker should have 3-5 turns
        - Total script should be 2-3 minutes when spoken
        - Include all important information but keep it digestible
        - End on an encouraging note
        
        Format your response EXACTLY as:
        Alex: [text]
        Jordan: [text]
        Alex: [text]
        ..."""
    
    def _build_prompt(self, employee_data: EmployeeData) -> str:
        """Build the prompt with employee data"""
        
        tech_stack_str = ", ".join(employee_data.tech_stack)
        
        schedule_str = "\n".join([
            f"- {item.time}: {item.activity}"
            for item in employee_data.first_day_schedule
        ])
        
        week_schedule_str = "\n".join([
            f"- {day}: {activity}"
            for day, activity in employee_data.first_week_schedule.items()
        ])
        
        prompt = f"""Create an onboarding welcome script for:

Name: {employee_data.name}
Position: {employee_data.position}
Team: {employee_data.team}
Manager: {employee_data.manager}
Start Date: {employee_data.start_date}
Office: {employee_data.office}
Tech Stack: {tech_stack_str}

First Day Schedule:
{schedule_str}

First Week Overview:
{week_schedule_str}

Create an engaging conversation that welcomes {employee_data.name} and 
covers these key points naturally. Make them feel excited and prepared!"""
        
        return prompt
    
    def _parse_script(self, script_text: str) -> List[Tuple[str, str]]:
        """Parse script text into structured format"""
        lines = script_text.strip().split('\n')
        script = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Parse "Speaker: text" format
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip().lower()
                    text = parts[1].strip()
                    
                    # Normalize speaker names to host1/host2
                    if speaker in ['alex', 'host1', 'speaker1']:
                        speaker = 'host1'
                    elif speaker in ['jordan', 'host2', 'speaker2']:
                        speaker = 'host2'
                    
                    if text:
                        script.append((speaker, text))
        
        return script
    
    def save_script_for_dev(
        self, 
        script: List[Tuple[str, str]], 
        employee_data: EmployeeData, 
        dev_dir: Path
    ) -> None:
        """Save script in readable format for development review"""
        from pathlib import Path
        
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