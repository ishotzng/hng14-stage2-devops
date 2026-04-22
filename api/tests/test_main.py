import pytest
import json
from unittest.mock import MagicMock, patch

# We patch redis.Redis BEFORE importing main
# This prevents the real Redis connection from being attempted during tests
with patch("redis.Redis") as mock_redis_class:
    mock_redis_instance = MagicMock()
    mock_redis_class.return_value = mock_redis_instance
    from main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def setup_function():
    """Reset mock before each test"""
    mock_redis_instance.reset_mock()


def test_create_job_returns_job_id():
    """POST /jobs should return a job_id"""
    mock_redis_instance.set.return_value = True
    mock_redis_instance.rpush.return_value = 1
    response = client.post("/jobs")
    assert response.status_code == 200
    assert "job_id" in response.json()


def test_create_job_pushes_to_redis_queue():
    """POST /jobs should push the job ID onto the Redis queue"""
    mock_redis_instance.set.return_value = True
    mock_redis_instance.rpush.return_value = 1
    client.post("/jobs")
    assert mock_redis_instance.rpush.called


def test_create_job_sets_status_to_queued():
    """POST /jobs should store status as 'queued' in Redis"""
    mock_redis_instance.set.return_value = True
    mock_redis_instance.rpush.return_value = 1
    response = client.post("/jobs")
    assert response.status_code == 200
    # Check that set was called with data containing "queued"
    call_args_str = str(mock_redis_instance.set.call_args)
    assert "queued" in call_args_str


def test_get_job_returns_status():
    """GET /jobs/{id} should return the job status"""
    mock_redis_instance.get.return_value = json.dumps({"status": "completed"})
    response = client.get("/jobs/abc123")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_get_job_returns_404_when_not_found():
    """GET /jobs/{id} should return 404 when job does not exist"""
    mock_redis_instance.get.return_value = None
    response = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_get_job_returns_queued_status():
    """GET /jobs/{id} returns queued status correctly"""
    mock_redis_instance.get.return_value = json.dumps({"status": "queued"})
    response = client.get("/jobs/some-job-id")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"