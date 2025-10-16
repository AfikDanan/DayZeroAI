#!/usr/bin/env python3
"""
Debug configuration loading
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

def debug_config():
    """Debug configuration loading"""
    print("🔍 Configuration Debug")
    print("=" * 40)
    
    # Check current working directory
    print(f"📁 Current directory: {os.getcwd()}")
    
    # Check if .env file exists
    env_file = Path(".env")
    print(f"📄 .env file exists: {env_file.exists()}")
    if env_file.exists():
        print(f"📄 .env file path: {env_file.absolute()}")
    
    # Check environment variables
    print(f"\n🔧 Environment Variables:")
    print(f"OPENAI_API_KEY (env): {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")
    print(f"SENDGRID_API_KEY (env): {os.getenv('SENDGRID_API_KEY', 'NOT SET')[:20]}...")
    
    # Check settings object
    print(f"\n⚙️ Settings Object:")
    print(f"OPENAI_API_KEY (settings): {settings.OPENAI_API_KEY[:20]}...")
    print(f"SENDGRID_API_KEY (settings): {settings.SENDGRID_API_KEY[:20]}...")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
    print(f"DEBUG: {settings.DEBUG}")
    print(f"LOG_LEVEL: {settings.LOG_LEVEL}")
    
    # Read .env file directly
    if env_file.exists():
        print(f"\n📖 .env file contents:")
        with open(env_file) as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
                if 'API_KEY' in line:
                    # Mask the key for security
                    if '=' in line:
                        key, value = line.split('=', 1)
                        masked_value = value[:20] + "..." if len(value) > 20 else value
                        print(f"  {i}: {key}={masked_value.strip()}")
                    else:
                        print(f"  {i}: {line.strip()}")
                else:
                    print(f"  {i}: {line.strip()}")

if __name__ == "__main__":
    debug_config()