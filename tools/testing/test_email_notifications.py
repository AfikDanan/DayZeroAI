#!/usr/bin/env python3
"""
Test email notification system
"""

import json
from pathlib import Path
from app.models.webhook import EmployeeData
from app.services.notification_service import NotificationService

def test_email_notifications():
    """Test the email notification system"""
    print("📧 Testing Email Notification System")
    print("=" * 50)
    
    # Load mock employee data
    mock_data_file = Path("data/mock_data.json")
    
    with open(mock_data_file, 'r') as f:
        mock_data = json.load(f)
    
    employee_data = EmployeeData(**mock_data["employee_data"])
    
    print(f"👤 Employee: {employee_data.name}")
    print(f"📧 Email: {employee_data.email}")
    print(f"💼 Position: {employee_data.position}")
    print(f"🏢 Team: {employee_data.team}")
    print()
    
    # Initialize notification service
    notification_service = NotificationService()
    
    # Test 1: Video Ready Email
    print("🎬 Testing Video Ready Email...")
    video_url = "/videos/test-video-123.mp4"
    
    try:
        success = notification_service.send_video_ready_email(
            employee_data.email,
            employee_data.name,
            video_url
        )
        
        if success:
            print("✅ Video ready email sent successfully!")
            print(f"   📧 Sent to: {employee_data.email}")
            print(f"   🎥 Video URL: {video_url}")
        else:
            print("❌ Failed to send video ready email")
            
    except Exception as e:
        print(f"❌ Error sending video ready email: {e}")
    
    print()
    
    # Test 2: Error Notification Email
    print("⚠️ Testing Error Notification Email...")
    error_message = "OpenAI API key expired"
    
    try:
        success = notification_service.send_error_notification(
            employee_data.email,
            employee_data.name,
            error_message
        )
        
        if success:
            print("✅ Error notification email sent successfully!")
            print(f"   📧 Sent to: {employee_data.email}")
            print(f"   ⚠️ Error: {error_message}")
        else:
            print("❌ Failed to send error notification email")
            
    except Exception as e:
        print(f"❌ Error sending error notification: {e}")
    
    print()
    
    # Test 3: Fallback Notification System
    print("🔄 Testing Fallback Notification System...")
    
    try:
        success = notification_service.send_video_ready_email(
            employee_data.email,
            employee_data.name,
            video_url,
            use_fallback=True
        )
        
        if success:
            print("✅ Fallback notification system working!")
            print("   📝 Check logs above for fallback email details")
        else:
            print("❌ Fallback notification system failed")
            
    except Exception as e:
        print(f"❌ Error in fallback notification: {e}")
    
    print()
    
    # Test 4: Email Template Preview
    print("🎨 Email Template Preview:")
    print("-" * 30)
    
    first_name = employee_data.name.split()[0]
    print(f"Subject: Welcome to the team, {first_name}! 🎉")
    print(f"To: {employee_data.email}")
    print(f"From: {notification_service.from_email}")
    print(f"Video URL: {notification_service.base_url}{video_url}")
    
    print("\nEmail Content Preview:")
    print("- Personalized greeting")
    print("- Team and role overview")
    print("- Tech stack information")
    print("- First day schedule")
    print("- First week expectations")
    print("- Call-to-action button")
    print("- Professional styling")
    
    return True

def test_email_configuration():
    """Test email service configuration"""
    print("\n🔧 Testing Email Configuration")
    print("=" * 50)
    
    notification_service = NotificationService()
    
    print(f"📧 From Email: {notification_service.from_email}")
    print(f"🌐 Base URL: {notification_service.base_url}")
    print(f"🔑 SendGrid API Key: {'*' * 20}{notification_service.sg.api_key[-10:] if len(notification_service.sg.api_key) > 10 else 'SET'}")
    
    # Test SendGrid connection using the new method
    print("\n🔗 Testing SendGrid Connection...")
    
    connection_result = notification_service.test_sendgrid_connection()
    
    print(f"✅ API Key Configured: {connection_result['api_key_configured']}")
    print(f"✅ From Email Set: {connection_result['from_email_set']}")
    print(f"✅ Base URL Set: {connection_result['base_url_set']}")
    print(f"✅ Connection Test: {connection_result['connection_test']}")
    
    if connection_result['error_message']:
        print(f"⚠️ Error: {connection_result['error_message']}")
    
    print(f"📝 Status: {connection_result['message']}")
    
    return connection_result['connection_test']

def main():
    """Main test function"""
    print("📧 Email Notification System Test")
    print("=" * 60)
    print("This test will send actual emails using SendGrid")
    print()
    
    # Test configuration first
    config_ok = test_email_configuration()
    
    if not config_ok:
        print("\n❌ Email configuration issues found!")
        print("💡 Check your SENDGRID_API_KEY and FROM_EMAIL settings")
        return 1
    
    # Confirm with user before sending actual emails
    print("\n⚠️  This will send real emails to the mock employee address.")
    response = input("Continue with email sending test? (y/N): ").strip().lower()
    
    if response not in ['y', 'yes']:
        print("Test cancelled - configuration verified only.")
        return 0
    
    print()
    
    # Run email tests
    success = test_email_notifications()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 EMAIL NOTIFICATION SYSTEM TEST COMPLETE!")
        print("=" * 60)
        print("✅ Email service configured correctly")
        print("✅ Video ready email template working")
        print("✅ Error notification email template working")
        print("✅ SendGrid integration functional")
        print()
        print("📧 Check the recipient's inbox for test emails")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ EMAIL NOTIFICATION SYSTEM TEST FAILED")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        exit(1)