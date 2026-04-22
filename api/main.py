from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import redis
import uuid
import json
import os

load_dotenv()

app = FastAPI()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    job_data = json.dumps({"status": "queued"})
    r.set(f"job:{job_id}", job_data)
    r.rpush("jobs_queue", job_id)
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    data = r.get(f"job:{job_id}")
    if data is None:
        return JSONResponse(status_code=404, content={"error": "not found"})
    return json.loads(data)

