#!/usr/bin/env python3
"""
Service startup helper script
Helps start Redis and the application
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_docker():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, check=True)
        print("✅ Docker is available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found")
        return False

def start_redis():
    """Start Redis using Docker"""
    print("🔴 Starting Redis...")
    
    # Check if container already exists
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--filter', 'name=redis-preboarding'], 
                              capture_output=True, text=True, check=True)
        
        if 'redis-preboarding' in result.stdout:
            print("  Container exists, starting it...")
            subprocess.run(['docker', 'start', 'redis-preboarding'], 
                         capture_output=True, text=True, check=True)
        else:
            print("  Creating new Redis container...")
            subprocess.run(['docker', 'run', '-d', '--name', 'redis-preboarding', 
                          '-p', '6379:6379', 'redis:7-alpine'], 
                         capture_output=True, text=True, check=True)
        
        print("✅ Redis started successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Redis: {e}")
        return False

def wait_for_redis():
    """Wait for Redis to be ready"""
    print("⏳ Waiting for Redis to be ready...")
    
    for i in range(10):
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            print("✅ Redis is ready")
            return True
        except Exception:
            time.sleep(1)
            print(f"  Attempt {i+1}/10...")
    
    print("❌ Redis not ready after 10 seconds")
    return False

def show_instructions():
    """Show instructions for manual startup"""
    print("\n" + "=" * 60)
    print("🚀 MANUAL STARTUP INSTRUCTIONS")
    print("=" * 60)
    print()
    print("1. Start Redis (in a separate terminal):")
    print("   docker run -d --name redis-preboarding -p 6379:6379 redis:7-alpine")
    print()
    print("2. Start the API server (in a separate terminal):")
    print("   cd preboarding_service")
    print("   python run.py")
    print()
    print("3. Start the background worker (in a separate terminal):")
    print("   cd preboarding_service")
    print("   rq worker video_generation")
    print()
    print("4. Test the API:")
    print("   python test_basic_api.py")
    print("   python test_webhook.py")
    print()
    print("5. Check service status:")
    print("   python check_setup.py")
    print()
    print("=" * 60)

def main():
    """Main startup helper"""
    print("🚀 Preboarding Service Startup Helper")
    print("=" * 50)
    
    if not check_docker():
        print("\n❌ Docker is required to run Redis")
        show_instructions()
        return 1
    
    print("\nThis script will help you start the required services.")
    print("Note: The API server and worker need to be started manually in separate terminals.")
    print()
    
    # Start Redis
    if start_redis():
        if wait_for_redis():
            print("\n✅ Redis is running and ready!")
        else:
            print("\n⚠️ Redis started but may not be fully ready")
    else:
        print("\n❌ Failed to start Redis")
        show_instructions()
        return 1
    
    # Show next steps
    print("\n" + "=" * 50)
    print("✅ REDIS IS READY!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Start API server in a new terminal:")
    print("   cd preboarding_service && python run.py")
    print()
    print("2. Start worker in another terminal:")
    print("   cd preboarding_service && rq worker video_generation")
    print()
    print("3. Test the service:")
    print("   python test_basic_api.py")
    print("   python test_webhook.py")
    print()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ Startup interrupted by user")
        sys.exit(1)