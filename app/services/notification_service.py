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
        video_url: str,
        use_fallback: bool = False
    ) -> bool:
        """Send email notification when video is ready"""
        
        if use_fallback:
            return self._send_fallback_notification(to_email, name, video_url, "video_ready")
        
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
            
            if response.status_code == 202:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.warning(
                    f"Email send returned status {response.status_code} for {to_email}"
                )
                return False
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error sending email to {to_email}: {error_msg}")
            
            # Log specific SendGrid errors for debugging
            if "403" in error_msg:
                logger.error("SendGrid 403 Error - Check API key and sender verification")
            elif "401" in error_msg:
                logger.error("SendGrid 401 Error - Invalid API key")
            elif "400" in error_msg:
                logger.error("SendGrid 400 Error - Invalid request format")
            
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
    
    def _send_fallback_notification(
        self,
        to_email: str,
        name: str,
        video_url: str,
        notification_type: str
    ) -> bool:
        """Fallback notification method for development/testing"""
        
        first_name = name.split()[0]
        full_video_url = f"{self.base_url}{video_url}"
        
        logger.info("=" * 60)
        logger.info("📧 EMAIL NOTIFICATION (FALLBACK MODE)")
        logger.info("=" * 60)
        logger.info(f"To: {to_email}")
        logger.info(f"From: {self.from_email}")
        logger.info(f"Type: {notification_type}")
        
        if notification_type == "video_ready":
            logger.info(f"Subject: Welcome to the team, {first_name}! 🎉")
            logger.info(f"Video URL: {full_video_url}")
            logger.info("Content: Personalized welcome video is ready!")
        else:
            logger.info(f"Subject: Welcome to the team, {first_name}!")
            logger.info("Content: Error notification - video generation failed")
        
        logger.info("=" * 60)
        logger.info("✅ Fallback notification logged successfully")
        logger.info("💡 In production, this would be sent via SendGrid")
        logger.info("=" * 60)
        
        return True
    
    def test_sendgrid_connection(self) -> dict:
        """Test SendGrid API connection and configuration"""
        
        result = {
            "api_key_configured": bool(self.sg.api_key),
            "from_email_set": bool(self.from_email),
            "base_url_set": bool(self.base_url),
            "connection_test": False,
            "error_message": None
        }
        
        try:
            # Try to create a test message (don't send it)
            test_message = Mail(
                from_email=Email(self.from_email),
                to_emails=To("test@example.com"),
                subject="Connection Test",
                html_content=Content("text/html", "<p>Test</p>")
            )
            
            result["connection_test"] = True
            result["message"] = "SendGrid client configured correctly"
            
        except Exception as e:
            result["error_message"] = str(e)
            result["message"] = f"SendGrid configuration error: {e}"
        
        return result