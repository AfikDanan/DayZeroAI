#!/usr/bin/env python3
"""
Diagnose SendGrid configuration issues
"""

import requests
from app.config import settings

def diagnose_sendgrid():
    """Diagnose SendGrid API and configuration"""
    print("🔍 SendGrid Configuration Diagnosis")
    print("=" * 50)
    
    api_key = settings.SENDGRID_API_KEY
    from_email = settings.FROM_EMAIL
    
    print(f"📧 From Email: {from_email}")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else 'SHORT'}")
    print()
    
    # Test 1: API Key Validation
    print("🔑 Testing API Key...")
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test API key with a simple GET request
        response = requests.get(
            'https://api.sendgrid.com/v3/user/profile',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ API Key Valid")
            print(f"   Account: {profile.get('username', 'N/A')}")
            print(f"   Email: {profile.get('email', 'N/A')}")
        else:
            print(f"❌ API Key Invalid - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API Key Test Failed: {e}")
    
    print()
    
    # Test 2: Sender Identity Verification
    print("👤 Checking Sender Identity...")
    try:
        response = requests.get(
            'https://api.sendgrid.com/v3/verified_senders',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            senders = response.json()
            print(f"✅ Sender Identity API Accessible")
            
            verified_emails = []
            for sender in senders.get('results', []):
                if sender.get('verified'):
                    verified_emails.append(sender.get('from_email'))
            
            print(f"📧 Verified Sender Emails: {verified_emails}")
            
            if from_email in verified_emails:
                print(f"✅ Your FROM_EMAIL ({from_email}) is verified!")
            else:
                print(f"❌ Your FROM_EMAIL ({from_email}) is NOT verified!")
                print("💡 You need to verify this email in SendGrid dashboard")
                
        else:
            print(f"❌ Sender Identity Check Failed - Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Sender Identity Check Failed: {e}")
    
    print()
    
    # Test 3: Account Status
    print("🏢 Checking Account Status...")
    try:
        response = requests.get(
            'https://api.sendgrid.com/v3/user/account',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            account = response.json()
            print(f"✅ Account Status: {account.get('type', 'Unknown')}")
            print(f"📊 Reputation: {account.get('reputation', 'N/A')}")
        else:
            print(f"❌ Account Status Check Failed - Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Account Status Check Failed: {e}")
    
    print()
    
    # Test 4: API Permissions
    print("🔐 Checking API Key Permissions...")
    try:
        response = requests.get(
            'https://api.sendgrid.com/v3/scopes',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            scopes = response.json()
            print(f"✅ API Key Permissions: {len(scopes)} scopes")
            
            required_scopes = ['mail.send', 'sender_verification_eligible']
            has_mail_send = 'mail.send' in scopes
            
            print(f"📧 Mail Send Permission: {'✅' if has_mail_send else '❌'}")
            
            if not has_mail_send:
                print("💡 Your API key needs 'mail.send' permission")
                
        else:
            print(f"❌ Permissions Check Failed - Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Permissions Check Failed: {e}")

def provide_solutions():
    """Provide solutions for common SendGrid issues"""
    print("\n💡 SendGrid Setup Solutions")
    print("=" * 50)
    
    print("🔧 To Fix SendGrid 403 Errors:")
    print()
    
    print("1. 📧 Verify Sender Identity:")
    print("   - Go to SendGrid Dashboard > Settings > Sender Authentication")
    print("   - Click 'Verify a Single Sender'")
    print(f"   - Add and verify: {settings.FROM_EMAIL}")
    print("   - Check your email for verification link")
    print()
    
    print("2. 🔑 Check API Key Permissions:")
    print("   - Go to SendGrid Dashboard > Settings > API Keys")
    print("   - Ensure your API key has 'Mail Send' permission")
    print("   - Create a new API key if needed")
    print()
    
    print("3. 🏢 Account Verification:")
    print("   - Complete SendGrid account verification if prompted")
    print("   - Some accounts need phone/identity verification")
    print()
    
    print("4. 🌐 Domain Authentication (Optional but Recommended):")
    print("   - Go to Settings > Sender Authentication")
    print("   - Set up domain authentication for better deliverability")

def test_simple_email():
    """Test sending a simple email after fixing permissions"""
    print("\n🧪 Testing Simple Email Send")
    print("=" * 50)
    
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    
    try:
        sg = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=settings.FROM_EMAIL,  # Send to yourself for testing
            subject='SendGrid Test Email',
            html_content='<p>This is a test email from your onboarding system!</p>'
        )
        
        response = sg.send(message)
        
        if response.status_code == 202:
            print("✅ Test email sent successfully!")
            print(f"📧 Check your inbox: {settings.FROM_EMAIL}")
            print("🎉 SendGrid is now working correctly!")
        else:
            print(f"❌ Email send failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test email failed: {e}")

def main():
    """Main diagnostic function"""
    try:
        diagnose_sendgrid()
        provide_solutions()
        
        print("\n" + "=" * 50)
        print("🎯 Next Steps:")
        print("1. Fix the API key permissions issue above")
        print("2. Update your .env file with new API key")
        print("3. Re-run this diagnostic: python tools/diagnostics/diagnose_sendgrid.py")
        print("4. Test emails: python tools/testing/test_email_notifications.py")
        
        # Offer to test if user has fixed the issue
        print("\n💡 If you've already fixed the API key, we can test it now:")
        test_response = input("Test email sending now? (y/N): ").strip().lower()
        
        if test_response in ['y', 'yes']:
            test_simple_email()
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")

if __name__ == "__main__":
    main()