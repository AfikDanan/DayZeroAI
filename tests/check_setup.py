#!/usr/bin/env python3
"""
Setup validation script for preboarding service
Checks all required dependencies and services
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path

def check_python_packages():
    """Check if all required Python packages are installed"""
    print("🐍 Checking Python packages...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pydantic', 'pydantic_settings',
        'redis', 'rq', 'openai', 'google.cloud.texttospeech',
        'PIL', 'pydub', 'sendgrid', 'httpx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'google.cloud.texttospeech':
                importlib.import_module('google.cloud.texttospeech')
            else:
                importlib.import_module(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_redis():
    """Check if Redis is running"""
    print("\n🔴 Checking Redis...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("  ✅ Redis is running")
        return True
    except Exception as e:
        print(f"  ❌ Redis connection failed: {e}")
        print("  💡 Start Redis with: redis-server")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, check=True)
        print("  ✅ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  ❌ FFmpeg not found")
        print("  💡 Install FFmpeg from: https://ffmpeg.org/download.html")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'SENDGRID_API_KEY',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    
    # Try to load from .env file
    env_file = Path('.env')
    if env_file.exists():
        print(f"  📄 Found .env file")
        with open(env_file) as f:
            env_content = f.read()
            for var in required_vars:
                if f"{var}=" in env_content:
                    print(f"  ✅ {var} (from .env)")
                else:
                    print(f"  ❌ {var} - MISSING from .env")
                    missing_vars.append(var)
    else:
        print("  ❌ .env file not found")
        # Check system environment
        for var in required_vars:
            if os.getenv(var):
                print(f"  ✅ {var} (from system)")
            else:
                print(f"  ❌ {var} - MISSING")
                missing_vars.append(var)
    
    return len(missing_vars) == 0

def check_google_credentials():
    """Check Google Cloud credentials"""
    print("\n☁️ Checking Google Cloud credentials...")
    
    creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'google_credencial.json')
    
    if os.path.exists(creds_file):
        print(f"  ✅ Credentials file found: {creds_file}")
        try:
            import json
            with open(creds_file) as f:
                creds = json.load(f)
                if 'type' in creds and creds['type'] == 'service_account':
                    print("  ✅ Valid service account credentials")
                    return True
                else:
                    print("  ❌ Invalid credentials format")
                    return False
        except Exception as e:
            print(f"  ❌ Error reading credentials: {e}")
            return False
    else:
        print(f"  ❌ Credentials file not found: {creds_file}")
        return False

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking directories...")
    
    dirs = ['videos', 'data']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✅ {dir_name}/ directory exists")
        else:
            print(f"  ⚠️ {dir_name}/ directory missing - will be created automatically")
    
    return True

def main():
    """Run all checks"""
    print("🚀 Preboarding Service Setup Validation")
    print("=" * 50)
    
    checks = [
        ("Python Packages", check_python_packages),
        ("Redis Service", check_redis),
        ("FFmpeg", check_ffmpeg),
        ("Environment Variables", check_environment_variables),
        ("Google Cloud Credentials", check_google_credentials),
        ("Directories", check_directories)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Error during {name} check: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run the service.")
        print("\nTo start the service:")
        print("1. python run.py (start the API server)")
        print("2. rq worker video_generation (start the background worker)")
        return 0
    else:
        print("⚠️ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- pip install -r requirements.txt")
        print("- Install Redis and start it")
        print("- Install FFmpeg")
        print("- Create .env file with API keys")
        print("- Set up Google Cloud service account")
        return 1

if __name__ == "__main__":
    sys.exit(main())