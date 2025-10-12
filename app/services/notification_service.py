import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.from_email = settings.FROM_EMAIL
        self.base_url = settings.BASE_URL
    
    def send_video_ready_email(
        self,
        to_email: str,
        name: str,
        video_url: str
    ) -> bool:
        """Send email notification when video is ready"""
        
        first_name = name.split()[0]
        full_video_url = f"{self.base_url}{video_url}"
        
        subject = f"Welcome to the team, {first_name}! 🎉"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .button:hover {{
                    background: #764ba2;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to the Team! 🎉</h1>
            </div>
            <div class="content">
                <p>Hi {first_name},</p>
                
                <p>We're so excited to have you joining us! We've prepared a personalized 
                welcome video just for you, covering everything you need to know about your 
                first day and week.</p>
                
                <p>Your video includes:</p>
                <ul>
                    <li>Your team and role overview</li>
                    <li>Tech stack you'll be working with</li>
                    <li>Your first day schedule</li>
                    <li>What to expect in your first week</li>
                </ul>
                
                <div style="text-align: center;">
                    <a href="{full_video_url}" class="button">
                        Watch Your Welcome Video
                    </a>
                </div>
                
                <p>If you have any questions before your start date, feel free to reach out 
                to your manager or HR team.</p>
                
                <p>See you soon!</p>
                
                <p><strong>The Team</strong></p>
            </div>
            <div class="footer">
                <p>This is an automated message from your onboarding system.</p>
            </div>
        </body>
        </html>
        """
        
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sg.send(message)
            
            logger.info(
                f"Email sent to {to_email}, status: {response.status_code}"
            )
            
            return response.status_code == 202
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_error_notification(
        self,
        to_email: str,
        name: str,
        error_message: str
    ) -> bool:
        """Send notification if video generation fails"""
        
        first_name = name.split()[0]
        subject = f"Welcome to the team, {first_name}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>Welcome to the Team, {first_name}! 🎉</h2>
            
            <p>We're excited to have you joining us!</p>
            
            <p>We attempted to create a personalized welcome video for you, but 
            encountered a technical issue. Don't worry - our team has been notified 
            and we'll send you the video shortly.</p>
            
            <p>In the meantime, here's what you need to know about your first day...</p>
            
            <p>If you have any questions, please reach out to HR.</p>
            
            <p>See you soon!</p>
        </body>
        </html>
        """
        
        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sg.send(message)
            return response.status_code == 202
            
        except Exception as e:
            logger.error(f"Error sending error notification: {str(e)}")
            return False