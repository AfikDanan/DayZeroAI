#!/usr/bin/env python3
"""
Start the RQ worker for video generation
"""

import sys
import os
from rq import Worker, Queue, Connection
import redis
from app.config import settings

def start_worker():
    """Start the RQ worker"""
    print("🚀 Starting Preboarding Background Worker...")
    print("📋 Worker will process video generation jobs")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        # Connect to Redis
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=False  # Match webhook processor setting
        )
        
        # Test Redis connection
        redis_conn.ping()
        print(f"✅ Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        # Create queue
        queue = Queue('video_generation', connection=redis_conn)
        print(f"📋 Listening on queue: video_generation")
        print(f"📊 Jobs in queue: {len(queue)}")
        
        # Create worker with explicit connection
        worker = Worker(['video_generation'], connection=redis_conn)
        print(f"👷 Worker created: {worker.name}")
        print(f"🔗 Worker connection: {worker.connection}")
        print()
        
        # Register worker and start (Windows compatible)
        print("🎬 Worker starting! Waiting for jobs...")
        print("🪟 Running in Windows-compatible mode (no forking)")
        worker.work(with_scheduler=False)
            
    except redis.ConnectionError:
        print("❌ Could not connect to Redis!")
        print("💡 Make sure Redis is running on localhost:6379")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Worker stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting worker: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    start_worker()