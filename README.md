# 🎬 Preboarding Service - AI-Powered Onboarding Videos

An automated service that generates personalized welcome videos for new hires, featuring AI-generated conversational scripts and professional audio narration.

## ✨ Features

- **Webhook-Triggered**: Automatically generates videos when HR system triggers onboarding event
- **AI-Generated Scripts**: Uses GPT-4o-mini to create engaging conversational content
- **Professional Audio**: Google Cloud Text-to-Speech with natural-sounding voices
- **Personalized Content**: Includes team info, tech stack, schedules, and more
- **Email Notifications**: Automatic delivery to new hire's inbox
- **Background Processing**: Async job queue for reliable video generation

## 🏗️ Architecture

```
HR System → Webhook → FastAPI → Redis Queue → Worker
                                              ↓
                                    ┌─────────┴─────────┐
                                    │  Video Pipeline   │
                                    ├───────────────────┤
                                    │ 1. Script Gen     │
                                    │ 2. Audio Gen      │
                                    │ 3. Visual Slides  │
                                    │ 4. FFmpeg Compose │
                                    └─────────┬─────────┘
                                              ↓
                                    Email → New Hire
```

## 🚀 Quick Start

### Prerequisites

```bash
# Install system dependencies
sudo apt-get install ffmpeg redis-server  # Ubuntu/Debian
brew install ffmpeg redis                  # macOS

# Start Redis
redis-server
```

### Quick Start

```bash
# 1. Clone and install
git clone https://github.com/AfikDanan/DayZeroAI
cd preboarding-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp examples/.env.example .env
cp examples/google_credencial.json.example google_credencial.json
# Edit both files with your API keys

# 3. Start services
docker run -d --name redis-preboarding -p 6379:6379 redis:7-alpine
python scripts/start_api_server.bat  # Windows
python scripts/start_worker.bat      # Windows

# 4. Test the service
python tests/check_setup.py
python tests/test_webhook.py
```

## Documentation

- 📖 [Setup Guide](docs/SETUP.md) - Detailed installation and configuration
- 🏗️ [Architecture](docs/ARCHITECTURE.md) - System design and components  
- 🔌 [API Reference](docs/API.md) - Complete API documentation

### Running Locally

```bash
# Terminal 1: Start API
uvicorn app.main:app --reload

# Terminal 2: Start Worker
rq worker video_generation --url redis://localhost:6379

# Terminal 3: Test
python test_integration.py
```

## 📝 API Documentation

### POST `/webhooks/user-onboarding`

Trigger video generation for new hire.

**Request:**
```json
{
  "event_type": "user.onboarding",
  "employee_data": {
    "employee_id": "EMP001",
    "name": "Sarah Johnson",
    "email": "sarah@company.com",
    "position": "Software Engineer",
    "team": "Engineering",
    "manager": "John Doe",
    "start_date": "2025-10-20",
    "office": "SF",
    "tech_stack": ["Python", "React"],
    "first_day_schedule": [...],
    "first_week_schedule": {...}
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "User onboarding webhook processed",
  "job_id": "abc-123-def-456",
  "processed_at": "2025-10-05T10:30:00"
}
```

### GET `/jobs/{job_id}/status`

Check video generation status.

**Response:**
```json
{
  "job_id": "abc-123",
  "status": "completed",
  "video_url": "/videos/abc-123.mp4",
  "created_at": "2025-10-05T10:30:00",
  "completed_at": "2025-10-05T10:33:00"
}
```

Possible statuses: `queued`, `processing`, `completed`, `failed`

## 🔧 Configuration

Key environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `SENDGRID_API_KEY` | SendGrid API key | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP JSON | Yes |
| `REDIS_HOST` | Redis server host | No (default: localhost) |
| `FROM_EMAIL` | Sender email address | Yes |
| `BASE_URL` | Base URL for video links | Yes |

## 💰 Cost Breakdown (50 videos/month)

- **OpenAI (GPT-4o-mini)**: ~$5/month
- **Google TTS**: Free (1M chars/month)
- **SendGrid**: Free (100 emails/day)
- **Hosting**: $5-10/month (Render/Railway)
- **Total**: ~$10-15/month

## 🎯 MVP Features

### ✅ Implemented
- Webhook receiver
- Background job processing
- AI script generation
- Text-to-speech audio
- Basic video composition
- Email notifications
- Job status tracking

### 🔜 Future Enhancements
- S3/CDN storage
- Custom branding/templates
- Video preview/approval flow
- Analytics dashboard
- Multiple language support
- Interactive video elements

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Integration test
python test_integration.py

# Manual webhook test
curl -X POST http://localhost:8000/webhooks/user-onboarding \
  -H "Content-Type: application/json" \
  -d @data/test_webhook.json
```

## 📦 Deployment

### Render.com (Recommended for MVP)

1. Create new Web Service
2. Connect your Git repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 127.0.0.1 --port $PORT`
5. Add Redis addon
6. Set environment variables
7. Create Background Worker service with command: `rq worker video_generation`

### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway login
railway init
railway up
```

## 🐛 Troubleshooting

**Video generation fails:**
- Check worker logs: `rq worker video_generation --burst`
- Verify FFmpeg installed: `ffmpeg -version`
- Check Google credentials: `echo $GOOGLE_APPLICATION_CREDENTIALS`

**Redis connection error:**
- Verify Redis running: `redis-cli ping`
- Check Redis URL in .env

**Email not sending:**
- Verify SendGrid API key
- Check sender email is verified in SendGrid
- Look for email in spam folder

## 📊 Monitoring

**Check job queue:**
```python
from redis import Redis
from rq import Queue

redis_conn = Redis()
queue = Queue('video_generation', connection=redis_conn)
print(f"Jobs: {len(queue)}")
```

**View worker status:**
```bash
rq info --url redis://localhost:6379
```

## 🔐 Security Considerations

- [ ] Add webhook signature verification
- [ ] Implement rate limiting
- [ ] Add API authentication
- [ ] Sanitize user inputs
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS in production
- [ ] Implement CORS properly

## 📄 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📞 Support

For issues or questions:
- Check the [Quick Start Guide](QUICKSTART.md)
- Review [Troubleshooting](#-troubleshooting)
- Open an issue on GitHub

---

Built with ❤️ for better employee onboarding experiences
