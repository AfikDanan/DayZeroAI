# Setup Guide

## Prerequisites

### System Requirements
- Python 3.10+
- Docker (for Redis)
- FFmpeg
- Windows/macOS/Linux

### API Keys Required
- OpenAI API Key (for script generation)
- Google Cloud Service Account (for text-to-speech)
- SendGrid API Key (for email notifications)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd preboarding_service
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy example environment file
cp examples/google_credencial.json.example google_credencial.json

# Create .env file with your API keys
# See examples/.env.example for template
```

### 5. Start Redis
```bash
docker run -d --name redis-preboarding -p 6379:6379 redis:7-alpine
```

### 6. Validate Setup
```bash
python tests/check_setup.py
```

## Configuration

### Environment Variables (.env)
```env
# OpenAI API Key
OPENAI_API_KEY="your-openai-api-key"

# SendGrid API Key  
SENDGRID_API_KEY="your-sendgrid-api-key"

# Google Cloud Credentials
GOOGLE_APPLICATION_CREDENTIALS="google_credencial.json"

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Email Configuration
FROM_EMAIL=your-email@company.com
BASE_URL=http://localhost:8000
```

### Google Cloud Setup
1. Create a Google Cloud Project
2. Enable Text-to-Speech API
3. Create a Service Account
4. Download JSON key file
5. Save as `google_credencial.json`

## Running the Application

### Development Mode
```bash
# Terminal 1: Start API Server
python run.py

# Terminal 2: Start Background Worker
python -m rq worker video_generation

# Terminal 3: Test the API
python tests/test_webhook.py
```

### Production Mode
```bash
# Use the startup scripts
scripts/start_api_server.bat    # Windows
scripts/start_worker.bat        # Windows

# Or run manually
python run.py &
python -m rq worker video_generation &
```

## Testing

### Quick Test
```bash
python tests/test_basic_api.py
```

### Full Pipeline Test
```bash
python tests/test_with_dev_output.py
```

### Unit Tests
```bash
python tests/test_welcome_slide.py
```

## Troubleshooting

### Common Issues

**Redis Connection Failed**
```bash
# Check if Redis is running
docker ps | grep redis

# Start Redis if not running
docker run -d --name redis-preboarding -p 6379:6379 redis:7-alpine
```

**OpenAI API Error**
- Verify API key is correct
- Check API key has sufficient credits
- Ensure no environment variable conflicts

**Google Cloud TTS Error**
- Verify service account has TTS permissions
- Check credentials file path is correct
- Ensure Text-to-Speech API is enabled

**FFmpeg Not Found**
- Install FFmpeg from https://ffmpeg.org/
- Ensure FFmpeg is in system PATH

### Debug Tools
```bash
# Validate complete setup
python tests/check_setup.py

# Debug configuration
python tools/debug_config.py

# Debug Google Cloud
python tools/debug_google_cloud.py

# Check Redis queue
python tests/check_queue.py
```

## Monitoring

### Health Checks
```bash
curl http://localhost:8000/health
```

### Queue Status
```bash
python tests/check_queue.py
```

### Logs
- API Server: Check terminal output
- Worker: Check RQ worker terminal
- Redis: `docker logs redis-preboarding`