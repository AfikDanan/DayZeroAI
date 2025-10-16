#!/usr/bin/env python3
"""
Check RQ queue status
"""

from redis import Redis
from rq import Queue
from app.config import settings

def main():
    print("🔍 Checking RQ Queue Status")
    print("=" * 40)
    
    try:
        # Connect to Redis
        redis_conn = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        
        # Check Redis connection
        redis_conn.ping()
        print("✅ Redis connection successful")
        
        # Check queue
        queue = Queue('video_generation', connection=redis_conn)
        
        print(f"📊 Queue: {queue.name}")
        print(f"📈 Jobs in queue: {len(queue)}")
        print(f"🔄 Failed jobs: {len(queue.failed_job_registry)}")
        print(f"✅ Finished jobs: {len(queue.finished_job_registry)}")
        print(f"⏳ Started jobs: {len(queue.started_job_registry)}")
        
        # List recent jobs
        if len(queue) > 0:
            print("\n📋 Jobs in queue:")
            for job in queue.jobs:
                print(f"  - {job.id}: {job.func_name}")
        
        if len(queue.failed_job_registry) > 0:
            print("\n❌ Failed jobs:")
            for job_id in queue.failed_job_registry.get_job_ids():
                job = queue.failed_job_registry.requeue(job_id)
                print(f"  - {job_id}: {job.exc_info if job else 'Unknown error'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()