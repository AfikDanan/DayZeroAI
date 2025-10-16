# API Documentation

## Overview
The Preboarding Service provides REST API endpoints for generating personalized onboarding videos.

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check
```http
GET /health
```
Returns the service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "preboarding-service"
}
```

### Root Information
```http
GET /
```
Returns basic service information.

**Response:**
```json
{
  "service": "Preboarding Video Service",
  "version": "1.0.0",
  "status": "operational"
}
```

### Webhook Status
```http
GET /webhooks/status
```
Returns webhook service status and available endpoints.

**Response:**
```json
{
  "status": "active",
  "endpoints": [
    "/webhooks/generic",
    "/webhooks/user-onboarding"
  ],
  "timestamp": "2025-10-15T10:30:00"
}
```

### User Onboarding Webhook
```http
POST /webhooks/user-onboarding
```
Triggers video generation for a new employee.

**Request Body:**
```json
{
  "event_type": "user.onboarding",
  "employee_data": {
    "employee_id": "EMP001",
    "name": "John Doe",
    "email": "john.doe@company.com",
    "position": "Software Engineer",
    "team": "Engineering",
    "manager": "Jane Smith",
    "start_date": "2025-10-20",
    "office": "New York",
    "tech_stack": ["Python", "React", "PostgreSQL"],
    "first_day_schedule": [
      {
        "time": "9:00 AM",
        "activity": "Welcome & HR Orientation",
        "location": "Conference Room A",
        "attendees": ["HR Team"]
      }
    ],
    "first_week_schedule": {
      "Monday": "Onboarding and Setup"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "User onboarding webhook processed: user.onboarding",
  "job_id": "abc-123-def-456",
  "processed_at": "2025-10-15T10:30:00"
}
```

### Job Status
```http
GET /jobs/{job_id}/status
```
Check the status of a video generation job.

**Response:**
```json
{
  "job_id": "abc-123-def-456",
  "status": "completed",
  "created_at": "2025-10-15T10:30:00",
  "completed_at": "2025-10-15T10:33:00",
  "video_url": "/videos/abc-123-def-456.mp4"
}
```

**Possible Status Values:**
- `queued` - Job is waiting to be processed
- `processing` - Video is being generated
- `completed` - Video generation successful
- `failed` - Video generation failed

### Video Access
```http
GET /videos/{job_id}.mp4
```
Download or stream the generated video file.

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid payload)
- `404` - Not Found (job/resource not found)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

Error response format:
```json
{
  "detail": "Error description"
}
```