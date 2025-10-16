#!/usr/bin/env python3
"""
Send a webhook request to test the onboarding API
"""

import requests
import json
from pathlib import Path
from datetime import datetime

def send_webhook():
    """Send webhook payload to the API"""
    
    # Load the mock data
    payload_file = Path("data/mock_data.json")
    
    with open(payload_file, 'r') as f:
        payload = json.load(f)
    
    # Update timestamp for this test
    payload["timestamp"] = datetime.now().isoformat() + "Z"
    
    # API endpoint
    url = "http://127.0.0.1:8000/webhooks/user-onboarding"
    
    print("🚀 Sending webhook request...")
    print(f"📧 Employee: {payload['employee_data']['name']}")
    print(f"💼 Position: {payload['employee_data']['position']}")
    print(f"🏢 Team: {payload['employee_data']['team']}")
    print()
    
    try:
        # Send the request
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook accepted successfully!")
            print(f"🆔 Job ID: {result.get('job_id', 'N/A')}")
            print(f"📝 Message: {result.get('message', 'N/A')}")
            
            if 'job_id' in result:
                print(f"\n🎬 Video generation started!")
                print(f"📁 Check dev_output/{result['job_id']}/ for intermediate files")
                print(f"🎥 Final video will be at videos/{result['job_id']}.mp4")
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("💡 Make sure the API server is running: python run.py")
    except requests.exceptions.Timeout:
        print("⏰ Request timed out!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_webhook()