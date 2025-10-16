# 🏗️ Architecture Documentation

## System Overview

The Preboarding Service is a modern microservice architecture designed for generating personalized AI-powered onboarding videos. The system processes employee data through a sophisticated pipeline that combines multiple AI services to create engaging welcome videos automatically.

## 🎯 Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   HR System    │───▶│   FastAPI       │───▶│   Redis Queue   │
│   (Webhook)     │    │   Web Server    │    │   (RQ Jobs)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │  Background     │
                       │   (Videos/Dev)  │    │  Worker (RQ)    │
                       └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ AI Video Pipeline│
                                              │ ┌─────────────┐ │
                                              │ │ OpenAI GPT  │ │
                                              │ │ 4o-mini     │ │
                                              │ │ (Scripts)   │ │
                                              │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                                              │ │ Google TTS  │ │
                                              │ │ Neural2     │ │
                                              │ │ (Audio)     │ │
                                              │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                                              │ │ PIL + FFmpeg│ │
                                              │ │ (Slides +   │ │
                                              │ │  Video)     │ │
                                              │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                                              │ │ SendGrid    │ │
                                              │ │ (Email)     │ │
                                              │ └─────────────┘ │
                                              └─────────────────┘
                                                        │
                                                        ▼
                                              ┌─────────────────┐
                                              │ AWS Deployment  │
                                              │ ┌─────────────┐ │
                                              │ │ Lambda      │ │
                                              │ │ Functions   │ │
                                              │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                                              │ │ S3 Storage  │ │
                                              │ │ (Videos)    │ │
                                              │ └─────────────┘ │
                                              │ ┌─────────────┐ │
                                              │ │ ElastiCache │ │
                                              │ │ (Redis)     │ │
                                              │ └─────────────┘ │
                                              └─────────────────┘
```

## 🧩 Core Components

### 1. FastAPI Web Server (`app/main.py`)
- **Purpose**: HTTP API server for webhook handling and job management
- **Technology**: FastAPI with Pydantic validation
- **Responsibilities**:
  - Receive webhook requests from HR systems
  - Validate employee data payloads
  - Queue background video generation jobs
  - Serve generated videos and development files
  - Provide job status and monitoring endpoints
  - Health checks and service status

### 2. Redis Queue System (RQ)
- **Purpose**: Asynchronous job processing and status tracking
- **Technology**: Redis with Python RQ (Redis Queue)
- **Responsibilities**:
  - Queue video generation jobs with priorities
  - Track job status (queued → processing → completed/failed)
  - Enable horizontal scaling with multiple workers
  - Provide job persistence and retry mechanisms
  - Store job metadata and results

### 3. Background Worker (`app/workers/video_worker.py`)
- **Purpose**: Process video generation jobs asynchronously
- **Technology**: Python RQ Worker
- **Responsibilities**:
  - Pick up jobs from Redis queue
  - Execute complete video generation pipeline
  - Update job status in real-time
  - Handle errors, retries, and timeouts
  - Clean up temporary files
  - Send completion notifications

### 4. AI-Powered Video Generation Pipeline (`app/services/`)

#### Script Generator (`script_generator.py`)
- **Technology**: OpenAI GPT-4o-mini API
- **Purpose**: Generate personalized conversational scripts
- **Input**: Employee data (name, role, team, schedule, tech stack, etc.)
- **Output**: Structured dialogue between two AI hosts (Alex & Jordan)
- **Features**:
  - Context-aware script generation
  - Personalized content based on role and team
  - Natural conversation flow
  - Configurable script length and tone

#### Audio Generator (`audio_generator.py`)
- **Technology**: Google Cloud Text-to-Speech (Neural2 voices)
- **Purpose**: Convert script to professional-quality audio
- **Features**:
  - Dual-host voices (en-US-Neural2-J male, en-US-Neural2-F female)
  - High-quality 24kHz audio output
  - Proper pacing with strategic pauses
  - SSML support for natural speech patterns
  - MP3 format optimization

#### Slide Generator (`slide_generator.py`)
- **Technology**: PIL (Python Imaging Library)
- **Purpose**: Create dynamic visual slides with employee information
- **Features**:
  - Professional slide templates
  - Dynamic text rendering with custom fonts
  - Employee data integration (name, role, schedule)
  - HD 1920x1080 resolution
  - Branded visual elements
  - Multiple slide types (welcome, schedule, tech stack)

#### Video Compositor (`video_generator.py`)
- **Technology**: FFmpeg with Python integration
- **Purpose**: Compose final video from audio and slides
- **Features**:
  - HD 1920x1080 video output
  - Audio-visual synchronization
  - Slide timing optimization
  - MP4 format with H.264 encoding
  - Configurable quality settings
  - Development file preservation

#### Notification Service (`notification_service.py`)
- **Technology**: SendGrid Email API
- **Purpose**: Automated email delivery to new hires
- **Features**:
  - HTML email templates with branding
  - Video link delivery with secure access
  - Error notifications to administrators
  - Delivery status tracking
  - Personalized email content

## 🔄 Data Flow

### 1. Webhook Reception
```
HR System → POST /webhooks/user-onboarding → FastAPI Server
                                           ↓
                                    Pydantic Validation
                                           ↓
                                    Generate Job ID
```

### 2. Job Queuing
```
FastAPI → Create Job Record → Queue in Redis → Return Job ID
                                    ↓
                            Job Status: "queued"
```

### 3. Background Processing
```
RQ Worker → Pick Job from Queue → Update Status: "processing"
                                        ↓
                                Video Pipeline Execution
```

### 4. AI Video Pipeline (Detailed)
```
Employee Data → OpenAI GPT-4o-mini → Personalized Script
                        ↓
              Google Cloud TTS → Dual-Host Audio (Male/Female)
                        ↓
              PIL Slide Generator → Dynamic Visual Slides
                        ↓
              FFmpeg Compositor → HD Video (1920x1080)
                        ↓
              SendGrid Email → Notification to Employee
                        ↓
              Update Status: "completed"
```

### 5. Video Delivery & Access
```
GET /videos/{job_id}.mp4 → Static File Serving (Local)
GET /jobs/{job_id}/status → Job Status & Metadata
GET /dev_output/{job_id}/ → Development Files (Debug)
```

### 6. AWS Production Flow
```
Lambda API → S3 Storage → ElastiCache Redis → Lambda Worker
                ↓                                    ↓
        Video Storage                        Pipeline Execution
                ↓                                    ↓
        CloudFront CDN ← S3 Video URL ← Completed Job
```

## 💾 Data Storage Schema

### Redis Job Storage
```
Key: job:{job_id}
Fields:
- job_id: string (UUID format)
- employee_id: string
- employee_name: string
- employee_email: string
- status: queued|processing|completed|failed
- created_at: timestamp (ISO format)
- started_at: timestamp
- completed_at: timestamp
- video_url: string (relative path)
- dev_files_url: string (development files path)
- error_message: string (if failed)
- retry_count: integer
- processing_time: float (seconds)
```

### File System Structure
```
videos/
├── {job_id}.mp4                    # Final video output
└── thumbnails/
    └── {job_id}.jpg               # Video thumbnail

dev_output/
└── {job_id}/
    ├── script.txt                 # Generated script
    ├── audio/
    │   ├── host1_segments/        # Male voice segments
    │   ├── host2_segments/        # Female voice segments
    │   └── final_audio.mp3        # Combined audio
    ├── slides/
    │   ├── welcome_slide.png      # Individual slides
    │   ├── schedule_slide.png
    │   └── tech_stack_slide.png
    └── metadata.json              # Job metadata
```

### AWS S3 Storage (Production)
```
s3://preboarding-videos/
├── videos/
│   └── {job_id}.mp4              # Final videos
├── dev-output/
│   └── {job_id}/                 # Development files
└── thumbnails/
    └── {job_id}.jpg              # Video thumbnails
```

## 🌐 API Endpoints

### Core Endpoints
- `POST /webhooks/user-onboarding` - Trigger video generation job
  - **Input**: Employee data payload (JSON)
  - **Output**: Job ID and status
  - **Status Codes**: 200 (success), 400 (validation error), 500 (server error)

- `GET /jobs/{job_id}/status` - Check job processing status
  - **Output**: Job status, progress, video URL (if completed)
  - **Status Codes**: 200 (found), 404 (job not found)

- `GET /videos/{job_id}.mp4` - Download generated video
  - **Output**: MP4 video file (streaming)
  - **Status Codes**: 200 (success), 404 (not found)

- `GET /dev_output/{job_id}/` - Access development files
  - **Output**: Directory listing or specific files
  - **Purpose**: Debugging and development

### Health & Monitoring Endpoints
- `GET /health` - Service health check
  - **Output**: Service status, dependencies status
  - **Checks**: Redis connection, disk space, API keys

- `GET /` - Service information
  - **Output**: Service name, version, uptime

- `GET /webhooks/status` - Webhook service status
  - **Output**: Available endpoints, queue status

### Development & Testing Endpoints
- `GET /jobs/` - List recent jobs (development only)
- `DELETE /jobs/{job_id}` - Cancel/delete job (development only)
- `POST /jobs/{job_id}/retry` - Retry failed job (development only)

## ⚙️ Configuration Management

### Environment Variables
- `OPENAI_API_KEY` - OpenAI API access for script generation
- `SENDGRID_API_KEY` - Email service access for notifications
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud TTS credentials
- `REDIS_HOST/PORT` - Redis queue configuration
- `FROM_EMAIL` - Sender email address for notifications
- `BASE_URL` - Service base URL for video links
- `ENVIRONMENT` - Deployment environment (development/production)

### Project Structure
```
preboarding_service/
├── app/                          # Main application code
│   ├── api/                      # FastAPI endpoints
│   │   ├── webhooks.py           # Webhook endpoints
│   │   └── jobs.py               # Job status endpoints
│   ├── models/                   # Pydantic data models
│   │   └── webhook.py            # Employee data models
│   ├── services/                 # Business logic services
│   │   ├── video_generator.py    # Main video orchestrator
│   │   ├── script_generator.py   # AI script generation
│   │   ├── audio_generator.py    # Text-to-speech
│   │   ├── slide_generator.py    # Image generation
│   │   └── notification_service.py # Email notifications
│   ├── workers/                  # Background job workers
│   │   └── video_worker.py       # RQ video generation worker
│   ├── utils/                    # Utility functions
│   ├── config.py                 # Configuration management
│   └── main.py                   # FastAPI application
├── aws/                          # AWS deployment code
│   ├── deployment/               # Deployment scripts
│   ├── lambda_handler.py         # Lambda function handlers
│   ├── s3_service.py            # S3 storage service
│   └── config.py                # AWS-specific configuration
├── tools/                        # Development and testing tools
│   ├── diagnostics/              # Debug and diagnostic scripts
│   ├── local_development/        # Local development utilities
│   └── testing/                  # Testing and demo scripts
├── tests/                        # Test suite
├── docs/                         # Documentation
├── examples/                     # Example configurations
└── data/                         # Sample data
```

## 🚀 Deployment Architectures

### Local Development
- FastAPI server running on localhost:8000
- Redis server (local or Docker)
- Background worker process
- Local file storage for videos

### AWS Production
- **API Layer**: AWS Lambda + API Gateway
- **Queue**: ElastiCache Redis
- **Worker**: Lambda functions for video processing
- **Storage**: S3 for videos and development files
- **CDN**: CloudFront for video delivery
- **Monitoring**: CloudWatch logs and metrics

## 📈 Scalability Considerations

### Horizontal Scaling
- Multiple worker instances can process jobs in parallel
- Redis queue enables distributed processing across workers
- Stateless API server allows multiple instances behind load balancer
- AWS Lambda auto-scaling for production workloads

### Performance Optimization
- Background processing prevents API request blocking
- Redis caching for job status and metadata
- Static file serving for videos with CDN
- Optimized video encoding settings for quality/size balance
- Parallel processing of audio segments

### Resource Management
- Configurable worker concurrency based on system resources
- Job timeout settings to prevent stuck processes
- Automatic temporary file cleanup after processing
- Memory-efficient image processing with PIL
- Streaming video delivery to reduce memory usage

## 🔒 Security

### API Security
- Input validation with Pydantic models
- Error handling without sensitive information leakage
- Rate limiting (recommended for production)
- CORS configuration for web clients
- Request size limits for webhook payloads

### Credential Management
- Environment variable configuration for all secrets
- Service account authentication for Google Cloud
- API key rotation support
- Secure credential storage in AWS Secrets Manager (production)

### Data Privacy
- Automatic temporary file cleanup after processing
- No persistent employee data storage beyond job metadata
- Secure credential handling with proper access controls
- Video access through secure URLs with expiration (optional)

## 📊 Monitoring and Observability

### Health Checks
- Comprehensive service health endpoint
- Dependency health validation (Redis, external APIs)
- Queue status monitoring and alerting
- Disk space and resource monitoring

### Logging
- Structured logging throughout the entire pipeline
- Error tracking and reporting with context
- Performance metrics and timing data
- Job processing audit trail

### Debugging Tools
- Setup validation scripts for environment configuration
- Configuration debugging utilities
- Queue inspection and management tools
- Development file preservation for troubleshooting
- Comprehensive test suite with multiple scenarios

## 🛠️ Development Tools

### Organized Tool Structure
- **`tools/diagnostics/`**: Debug and diagnostic scripts
  - Redis queue monitoring and cleanup
  - Google Cloud TTS connection testing
  - Template loading debugging
  - SendGrid email testing

- **`tools/local_development/`**: Local development utilities
  - Webhook testing scripts
  - Background worker startup
  - Development server management

- **`tools/testing/`**: Testing and demo scripts
  - Complete application demos
  - Production API testing
  - Email notification testing
  - Performance benchmarking

### Quality Assurance
- Comprehensive test coverage for all components
- Integration tests for complete workflows
- Performance testing for video generation pipeline
- Error handling validation
- Mock services for development and testing