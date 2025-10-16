#!/usr/bin/env python3
"""
Clear Redis queues and corrupted data
"""

import redis
from app.config import settings

def clear_redis():
    """Clear Redis queues and data"""
    try:
        # Connect to Redis
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=False  # Don't decode to avoid unicode errors
        )
        
        # Test connection
        redis_conn.ping()
        print(f"✅ Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        # Clear all RQ related keys
        print("🧹 Clearing Redis queues and job data...")
        
        # Get all keys
        keys = redis_conn.keys("rq:*")
        if keys:
            redis_conn.delete(*keys)
            print(f"🗑️  Deleted {len(keys)} RQ keys")
        
        # Clear video_generation queue specifically
        queue_keys = redis_conn.keys("*video_generation*")
        if queue_keys:
            redis_conn.delete(*queue_keys)
            print(f"🗑️  Deleted {len(queue_keys)} video_generation keys")
        
        # Clear any job keys
        job_keys = redis_conn.keys("*job*")
        if job_keys:
            redis_conn.delete(*job_keys)
            print(f"🗑️  Deleted {len(job_keys)} job keys")
        
        print("✅ Redis cleared successfully!")
        print("🔄 You can now restart the worker safely")
        
    except redis.ConnectionError:
        print("❌ Could not connect to Redis!")
        print("💡 Make sure Redis is running on localhost:6379")
    except Exception as e:
        print(f"❌ Error clearing Redis: {e}")

if __name__ == "__main__":
    clear_redis()