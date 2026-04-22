# hng14-stage2-devops

A containerised job processing system. Users submit jobs through a frontend,
the API stores them in Redis, and the worker picks them up and processes them.

## Services

| Service  | Description |
|----------|-------------|
| frontend | Node.js/Express UI at http://localhost:3000 |
| api      | Python/FastAPI job API at port 8000 (internal only) |
| worker   | Python background processor |
| redis    | Shared message queue (internal only, not exposed) |

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | 24+ | https://docs.docker.com/get-docker |
| Git | any | https://git-scm.com |

---

## Getting Started on a Clean Machine

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create your environment file

```bash
cp .env.example api/.env
```

Open `api/.env` and set a strong password for `REDIS_PASSWORD`.
Never commit this file — it is already in `.gitignore`.

### 3. Start the stack

```bash
docker compose up --build
```

### 4. Verify startup

You should see:
✔ Container ...-redis-1     Healthy
✔ Container ...-api-1       Healthy
✔ Container ...-worker-1    Started
✔ Container ...-frontend-1  Started

### 5. Open the app

Go to http://localhost:3000 in your browser.
Click **Submit New Job**. The job will appear as `queued` then change to `completed`.

---

## Running Unit Tests

```bash
cd api
pip install -r requirements.txt pytest pytest-cov
pytest tests/ -v --cov=main --cov-report=term-missing
```

---

## Stopping the Stack

```bash
docker compose down
```

To remove volumes too:

```bash
docker compose down -v
```

---

## CI/CD Pipeline

Runs automatically on every push via GitHub Actions.

| Stage | What it does |
|-------|-------------|
| lint | flake8, eslint, hadolint |
| test | pytest with mocked Redis, uploads coverage artifact |
| build | builds 3 images, tags with git SHA + latest, pushes to local registry |
| security-scan | Trivy scans all images, fails on CRITICAL findings |
| integration-test | brings full stack up, submits job, polls until completed |
| deploy | rolling update on pushes to main only |

### Required GitHub Secret

Add `REDIS_PASSWORD` under Settings → Secrets and variables → Actions.