@echo off
echo Starting Preboarding API Server...
echo Server will be available at http://localhost:8000
echo Press Ctrl+C to stop
cd /d "%~dp0"
python run.py
pause
