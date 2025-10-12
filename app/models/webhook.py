# app/models/webhook.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class WebhookPayload(BaseModel):
    """Generic webhook payload"""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)

class ScheduleItem(BaseModel):
    """Single schedule item"""
    time: str
    activity: str
    location: Optional[str] = None
    attendees: Optional[List[str]] = None

class EmployeeData(BaseModel):
    """Employee information from HR system"""
    employee_id: str
    name: str
    email: EmailStr
    position: str
    team: str
    manager: str
    start_date: date
    office: str
    tech_stack: List[str] = []
    first_day_schedule: List[ScheduleItem] = []
    first_week_schedule: Dict[str, str] = {}
    department: Optional[str] = None
    buddy: Optional[str] = None

class UserOnboardingWebhook(BaseModel):
    """Specific webhook for user onboarding"""
    event_type: str = "user.onboarding"
    employee_data: EmployeeData
    timestamp: datetime = Field(default_factory=datetime.now)

class WebhookResponse(BaseModel):
    """Standard webhook response"""
    success: bool
    message: str
    job_id: Optional[str] = None
    processed_at: datetime

class VideoGenerationJob(BaseModel):
    """Video generation job model"""
    job_id: str
    employee_id: str
    status: str  # queued, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    video_url: Optional[str] = None
    error_message: Optional[str] = None