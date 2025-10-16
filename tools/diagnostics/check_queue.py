#!/usr/bin/env python3
"""
Check Redis queue status
"""

import redis
from rq import Queue, Worker
from app.config import settings

def check_queue():
    """Check the status of the video generation queue"""
    try:
        # Connect to Redis
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=False  # Don't decode to avoid UTF-8 issues
        )
        
        # Test connection
        redis_conn.ping()
        print(f"✅ Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        # Check video_generation queue  
        queue = Queue('video_generation', connection=redis_conn)
        
        # Check active workers
        workers = Worker.all(connection=redis_conn)
        
        print(f"\n📋 Queue Status:")
        print(f"   Queue Name: video_generation")
        print(f"   Jobs in queue: {len(queue)}")
        print(f"   Failed jobs: {len(queue.failed_job_registry)}")
        print(f"   Started jobs: {len(queue.started_job_registry)}")
        print(f"   Finished jobs: {len(queue.finished_job_registry)}")
        print(f"   Active workers: {len(workers)}")
        
        if workers:
            print(f"\n👷 Active Workers:")
            for worker in workers:
                print(f"   - Worker: {worker.name}")
                print(f"     State: {worker.get_state()}")
                print(f"     Queues: {[q.name for q in worker.queues]}")
        else:
            print(f"\n⚠️  No active workers found!")
            print(f"   The worker process needs to be restarted")
            print(f"   💡 Restart with: python tools/local_development/start_worker.py")
            
            # Offer to manually process a job for testing
            if len(queue) > 0:
                print(f"\n🧪 Would you like to manually process the first job to test the system?")
                print(f"   This will verify that the video generation pipeline works")
        
        # List jobs in queue
        if len(queue) > 0:
            print(f"\n📝 Jobs in queue:")
            for job in queue.jobs:
                print(f"   - Job ID: {job.id}")
                print(f"     Function: {job.func_name}")
                print(f"     Status: {job.get_status()}")
                print(f"     Created: {job.created_at}")
        
        # Check failed jobs
        if len(queue.failed_job_registry) > 0:
            print(f"\n❌ Failed jobs:")
            for job_id in queue.failed_job_registry.get_job_ids():
                try:
                    job = queue.failed_job_registry[job_id]
                    print(f"   - Job ID: {job_id}")
                    if job and hasattr(job, 'exc_info'):
                        print(f"     Error: {job.exc_info}")
                except Exception as e:
                    print(f"   - Job ID: {job_id} (Error reading: {e})")
        
        # Check started jobs
        if len(queue.started_job_registry) > 0:
            print(f"\n🔄 Currently running jobs:")
            for job_id in queue.started_job_registry.get_job_ids():
                print(f"   - Job ID: {job_id}")
        
        # Check finished jobs (recent)
        if len(queue.finished_job_registry) > 0:
            print(f"\n✅ Recently finished jobs:")
            for job_id in queue.finished_job_registry.get_job_ids()[-5:]:  # Last 5
                print(f"   - Job ID: {job_id}")
        
    except redis.ConnectionError:
        print("❌ Could not connect to Redis!")
        print("💡 Make sure Redis is running on localhost:6379")
    except Exception as e:
        print(f"❌ Error checking queue: {e}")

if __name__ == "__main__":
    check_queue()