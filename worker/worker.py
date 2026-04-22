import redis
import json
import time
import os
import signal
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

running = True


def handle_shutdown(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def process_job(job_id):
    print(f"Processing job: {job_id}")
    time.sleep(1)
    job_data = json.dumps({"status": "completed"})
    r.set(f"job:{job_id}", job_data)
    print(f"Job {job_id} completed")


if __name__ == "__main__":
    print("Worker started, waiting for jobs...")
    while running:
        try:
            result = r.blpop("jobs_queue", timeout=5)
            if result:
                _, job_id = result
                process_job(job_id)
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(2)
    print("Worker shutting down cleanly")