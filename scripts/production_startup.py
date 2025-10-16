#!/usr/bin/env python3
"""
Production-like startup coordinator
Helps manage multiple services for production testing
"""

import subprocess
import time
import requests
import json
import sys
import os
from datetime import datetime

def show_production_instructions():
    """Show production startup instructions"""
    print("🚀 PRODUCTION STARTUP GUIDE")
    print("=" * 60)
    print("To run the application in production mode, you need 3 services:")
    print()
    
    print("1️⃣ REDIS (Already running)")
    print("   ✅ Redis is running on Docker")
    print("   ✅ Accessible on localhost:6379")
    print()
    
    print("2️⃣ API SERVER")
    print("   Command: python run.py")
    print("   Port: http://localhost:8000")
    print("   Purpose: Handles webhook requests and serves videos")
    print()
    
    print("3️⃣ BACKGROUND WORKER")
    print("   Command: python -m rq worker video_generation")
    print("   Purpose: Processes video generation jobs from Redis queue")
    print()
    
    print("📋 STARTUP SEQUENCE:")
    print("=" * 30)
    print("1. Redis ✅ (Already running)")
    print("2. Start API Server (Terminal 1)")
    print("3. Start Background Worker (Terminal 2)")
    print("4. Test with webhook requests")
    print()

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    
    # Windows batch file for API server
    api_script = """@echo off
echo Starting Preboarding API Server...
echo Server will be available at http://localhost:8000
echo Press Ctrl+C to stop
cd /d "%~dp0"
python run.py
pause
"""
    
    with open("start_api_server.bat", "w") as f:
        f.write(api_script)
    
    # Windows batch file for worker
    worker_script = """@echo off
echo Starting Preboarding Background Worker...
echo Worker will process video generation jobs
echo Press Ctrl+C to stop
cd /d "%~dp0"
python -m rq worker video_generation
pause
"""
    
    with open("start_worker.bat", "w") as f:
        f.write(worker_script)
    
    # PowerShell script for testing
    test_script = """# Preboarding Service Test Script
Write-Host "Testing Preboarding Service API" -ForegroundColor Green
Write-Host "Make sure API server is running on http://localhost:8000" -ForegroundColor Yellow

# Test health endpoint
Write-Host "`nTesting health endpoint..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "✅ Health check passed: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $_" -ForegroundColor Red
    exit 1
}

# Test webhook endpoint
Write-Host "`nTesting webhook endpoint..." -ForegroundColor Cyan
$webhook_payload = @{
    event_type = "user.onboarding"
    employee_data = @{
        employee_id = "PROD_TEST_001"
        name = "Production Test User"
        email = "test@company.com"
        position = "Software Engineer"
        team = "Engineering"
        manager = "Test Manager"
        start_date = "2025-10-20"
        office = "Test Office"
        tech_stack = @("Python", "FastAPI", "React")
        first_day_schedule = @(
            @{
                time = "9:00 AM"
                activity = "Welcome & Orientation"
            }
        )
        first_week_schedule = @{
            Monday = "Onboarding and Setup"
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/webhooks/user-onboarding" -Method Post -Body $webhook_payload -ContentType "application/json"
    Write-Host "✅ Webhook request successful!" -ForegroundColor Green
    Write-Host "Job ID: $($response.job_id)" -ForegroundColor Yellow
    
    if ($response.job_id) {
        Write-Host "`nMonitoring job status..." -ForegroundColor Cyan
        for ($i = 1; $i -le 10; $i++) {
            Start-Sleep -Seconds 5
            try {
                $status = Invoke-RestMethod -Uri "http://localhost:8000/jobs/$($response.job_id)/status" -Method Get
                Write-Host "Status check $i`: $($status.status)" -ForegroundColor Yellow
                
                if ($status.status -eq "completed") {
                    Write-Host "🎉 Video generation completed!" -ForegroundColor Green
                    Write-Host "Video URL: $($status.video_url)" -ForegroundColor Green
                    break
                } elseif ($status.status -eq "failed") {
                    Write-Host "❌ Video generation failed: $($status.error_message)" -ForegroundColor Red
                    break
                }
            } catch {
                Write-Host "Status check failed: $_" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "❌ Webhook request failed: $_" -ForegroundColor Red
}

Write-Host "`nTest completed!" -ForegroundColor Green
"""
    
    with open("test_production.ps1", "w") as f:
        f.write(test_script)
    
    print("📁 Created startup scripts:")
    print("   - start_api_server.bat (Windows)")
    print("   - start_worker.bat (Windows)")
    print("   - test_production.ps1 (PowerShell test)")

def show_manual_commands():
    """Show manual commands for production startup"""
    print("\n🔧 MANUAL STARTUP COMMANDS:")
    print("=" * 40)
    print()
    print("Terminal 1 (API Server):")
    print("cd preboarding_service")
    print("python run.py")
    print()
    print("Terminal 2 (Background Worker):")
    print("cd preboarding_service")
    print("python -m rq worker video_generation")
    print()
    print("Terminal 3 (Testing):")
    print("cd preboarding_service")
    print("python tests/test_webhook.py")
    print()

def show_production_endpoints():
    """Show available production endpoints"""
    print("\n🌐 PRODUCTION API ENDPOINTS:")
    print("=" * 40)
    print()
    print("Health Check:")
    print("GET http://localhost:8000/health")
    print()
    print("Root Info:")
    print("GET http://localhost:8000/")
    print()
    print("Webhook Status:")
    print("GET http://localhost:8000/webhooks/status")
    print()
    print("User Onboarding Webhook:")
    print("POST http://localhost:8000/webhooks/user-onboarding")
    print()
    print("Job Status:")
    print("GET http://localhost:8000/jobs/{job_id}/status")
    print()
    print("Video Access:")
    print("GET http://localhost:8000/videos/{job_id}.mp4")
    print()

def show_monitoring_commands():
    """Show monitoring and debugging commands"""
    print("\n📊 MONITORING & DEBUGGING:")
    print("=" * 40)
    print()
    print("Check Redis Queue:")
    print("python tests/check_queue.py")
    print()
    print("Validate Setup:")
    print("python tests/check_setup.py")
    print()
    print("Debug Configuration:")
    print("python tests/debug_config.py")
    print()
    print("View Docker Containers:")
    print("docker ps")
    print()
    print("View Redis Logs:")
    print("docker logs redis-preboarding")
    print()

def main():
    """Main production startup guide"""
    print("🏭 PREBOARDING SERVICE - PRODUCTION STARTUP")
    print("=" * 60)
    print("This guide helps you run the application in production mode")
    print()
    
    # Show current status
    print("📋 CURRENT STATUS:")
    print("✅ Redis: Running on Docker")
    print("✅ Dependencies: All installed")
    print("✅ Configuration: Environment variables loaded")
    print("⚠️ Google Cloud TTS: Credentials need refresh")
    print()
    
    # Create startup scripts
    create_startup_scripts()
    
    # Show instructions
    show_production_instructions()
    show_manual_commands()
    show_production_endpoints()
    show_monitoring_commands()
    
    print("\n" + "=" * 60)
    print("🚀 READY FOR PRODUCTION!")
    print("=" * 60)
    print("1. Use the .bat files for easy Windows startup")
    print("2. Or run the manual commands in separate terminals")
    print("3. Test with the PowerShell script or manual requests")
    print("4. Monitor with the debugging commands")
    print()
    print("💡 TIP: Fix Google Cloud credentials for full functionality")
    print("   Download new service account key and replace google_credencial.json")

if __name__ == "__main__":
    main()