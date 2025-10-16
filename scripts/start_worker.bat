@echo off
echo Starting Preboarding Background Worker...
echo Worker will process video generation jobs
echo Press Ctrl+C to stop
cd /d "%~dp0"
python -m rq worker video_generation
pause
