#!/usr/bin/env python3
"""
Debug Google Cloud Text-to-Speech connection
"""

import sys
import os
from pathlib import Path

# Add the parent directory to Python path
sys.path.append('.')

def test_google_cloud_connection():
    """Test Google Cloud Text-to-Speech connection step by step"""
    print("🔍 Google Cloud Text-to-Speech Debug")
    print("=" * 50)
    
    # Step 1: Check credentials file
    print("1️⃣ Checking credentials file...")
    
    from app.config import settings
    creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
    print(f"   📄 Credentials path: {creds_path}")
    
    if os.path.exists(creds_path):
        file_size = os.path.getsize(creds_path)
        print(f"   ✅ File exists: {file_size:,} bytes")
        
        # Check if it's valid JSON
        try:
            import json
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            
            print(f"   ✅ Valid JSON structure")
            print(f"   📋 Project ID: {creds.get('project_id', 'Missing')}")
            print(f"   📧 Client Email: {creds.get('client_email', 'Missing')}")
            print(f"   🔑 Has Private Key: {'Yes' if creds.get('private_key') else 'No'}")
            
        except Exception as e:
            print(f"   ❌ Invalid JSON: {e}")
            return False
    else:
        print(f"   ❌ File not found: {creds_path}")
        return False
    
    # Step 2: Test environment variable
    print(f"\n2️⃣ Checking environment variable...")
    env_creds = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if env_creds:
        print(f"   ⚠️ Environment variable set: {env_creds}")
        print(f"   💡 This might override the config file")
    else:
        print(f"   ✅ No environment variable (using config file)")
    
    # Step 3: Test Google Cloud client initialization
    print(f"\n3️⃣ Testing Google Cloud client initialization...")
    try:
        from google.cloud import texttospeech
        
        # Set the credentials explicitly
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        
        client = texttospeech.TextToSpeechClient()
        print(f"   ✅ Client initialized successfully")
        
        # Step 4: Test a simple API call
        print(f"\n4️⃣ Testing simple API call...")
        
        # List available voices (this is a simple API call)
        try:
            voices_request = texttospeech.ListVoicesRequest()
            voices_response = client.list_voices(request=voices_request)
            
            # Count voices
            voice_count = len(voices_response.voices)
            print(f"   ✅ API call successful!")
            print(f"   🎤 Available voices: {voice_count}")
            
            # Find our specific voices
            en_us_voices = [v for v in voices_response.voices if 'en-US' in v.language_codes]
            neural_voices = [v for v in en_us_voices if 'Neural2' in v.name]
            
            print(f"   🇺🇸 English US voices: {len(en_us_voices)}")
            print(f"   🧠 Neural2 voices: {len(neural_voices)}")
            
            # Check for our specific voices
            target_voices = ['en-US-Neural2-J', 'en-US-Neural2-F']
            for voice_name in target_voices:
                found = any(voice_name in v.name for v in voices_response.voices)
                status = "✅" if found else "❌"
                print(f"   {status} {voice_name}: {'Available' if found else 'Not found'}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ API call failed: {e}")
            print(f"   🔍 Error type: {type(e).__name__}")
            
            # Check for specific error types
            if "invalid_grant" in str(e).lower():
                print(f"   💡 This suggests credentials are expired or invalid")
                print(f"   🔧 Try downloading fresh credentials from Google Cloud Console")
            elif "permission" in str(e).lower():
                print(f"   💡 This suggests missing permissions")
                print(f"   🔧 Ensure Text-to-Speech API is enabled and service account has access")
            elif "quota" in str(e).lower():
                print(f"   💡 This suggests quota/billing issues")
                print(f"   🔧 Check Google Cloud Console for billing and quotas")
            
            return False
            
    except Exception as e:
        print(f"   ❌ Client initialization failed: {e}")
        return False

def test_simple_synthesis():
    """Test a simple text synthesis"""
    print(f"\n5️⃣ Testing simple text synthesis...")
    
    try:
        from google.cloud import texttospeech
        from app.config import settings
        
        # Set credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        client = texttospeech.TextToSpeechClient()
        
        # Simple synthesis request
        synthesis_input = texttospeech.SynthesisInput(text="Hello, this is a test.")
        
        voice = texttospeech.VoiceSelectionParams(
            language_code='en-US',
            name='en-US-Neural2-J',
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Check response
        if response.audio_content:
            audio_size = len(response.audio_content)
            print(f"   ✅ Synthesis successful!")
            print(f"   🎵 Audio size: {audio_size:,} bytes")
            
            # Save test audio
            test_audio_path = Path("debug_test_audio.mp3")
            with open(test_audio_path, 'wb') as f:
                f.write(response.audio_content)
            
            print(f"   💾 Test audio saved: {test_audio_path}")
            return True
        else:
            print(f"   ❌ No audio content returned")
            return False
            
    except Exception as e:
        print(f"   ❌ Synthesis failed: {e}")
        return False

def main():
    """Main debug function"""
    print("🔧 Google Cloud Text-to-Speech Diagnostics")
    print("This will help identify and fix the credentials issue")
    print()
    
    success = test_google_cloud_connection()
    
    if success:
        print(f"\n🎯 Connection successful! Testing synthesis...")
        synthesis_success = test_simple_synthesis()
        
        if synthesis_success:
            print(f"\n" + "=" * 50)
            print("🎉 GOOGLE CLOUD TTS IS WORKING!")
            print("=" * 50)
            print("✅ Credentials are valid")
            print("✅ API access is working")
            print("✅ Text synthesis is functional")
            print("✅ Ready for video generation!")
            
            # Clean up test file
            test_file = Path("debug_test_audio.mp3")
            if test_file.exists():
                test_file.unlink()
                print("🧹 Cleaned up test audio file")
            
            return 0
        else:
            print(f"\n" + "=" * 50)
            print("⚠️ CONNECTION OK, SYNTHESIS FAILED")
            print("=" * 50)
            print("✅ Credentials are valid")
            print("✅ API connection works")
            print("❌ Text synthesis failed")
            return 1
    else:
        print(f"\n" + "=" * 50)
        print("❌ GOOGLE CLOUD CONNECTION FAILED")
        print("=" * 50)
        print("🔧 Troubleshooting steps:")
        print("1. Download fresh service account key from Google Cloud Console")
        print("2. Replace google_credencial.json with the new file")
        print("3. Ensure Text-to-Speech API is enabled")
        print("4. Check service account permissions")
        print("5. Verify project billing is active")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Debug interrupted by user")
        sys.exit(1)