# hng14-stage2-devops

A containerised job-processing system. Users submit jobs through a frontend, the API stores them in Redis, and the worker picks them up and processes them asynchronously.

## Services

| Service  | Description                               | Port         |
|----------|-------------------------------------------|--------------|
| frontend | Node.js/Express UI                        | 3000 (host)  |
| api      | Python/FastAPI job API                    | 8000 (internal) |
| worker   | Python background processor               | —            |
| redis    | Shared message queue (password-protected) | internal only |

---

## Prerequisites

| Tool           | Version | Install |
|----------------|---------|---------|
| Docker Desktop | 24+     | https://docs.docker.com/get-docker |
| Git            | any     | https://git-scm.com |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ishotzng/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Create your environment file

```bash
cp .env.example .env
```

Open `.env` and set a strong value for `REDIS_PASSWORD`. This file is already listed in `.gitignore` — never commit it.

### 3. Start the stack

```bash
docker compose up --build
```

Expected output:
```
✔ Container ...-redis-1     Healthy
✔ Container ...-api-1       Healthy
✔ Container ...-worker-1    Started
✔ Container ...-frontend-1  Started
```

### 4. Open the app

Navigate to http://localhost:3000 in your browser. Click **Submit New Job** — the job will appear as `queued` and transition to `completed`.

---

## Running Unit Tests

```bash
cd api
pip install -r requirements.txt
pytest tests/ -v --cov=main --cov-report=term-missing
```

---

## Running the Integration Script

```bash
# Stack must be running first
docker compose up -d
bash integration.sh
```

---

## Stopping the Stack

```bash
docker compose down        # keep volumes
docker compose down -v     # also remove volumes
```

---

## CI/CD Pipeline

The pipeline runs automatically on every push via GitHub Actions.

| Stage            | What it does                                                            |
|------------------|-------------------------------------------------------------------------|
| lint             | Flake8 (Python), ESLint (JS), Hadolint (Dockerfiles), secrets detection |
| test             | Pytest with mocked Redis, uploads coverage XML artifact                 |
| build            | Builds 3 images, tags with git SHA + `latest`, pushes to GHCR          |
| security-scan    | Trivy scans all images, fails on CRITICAL findings, exports SARIF       |
| integration-test | Brings full stack up, submits job, polls until completed, always tears down |
| deploy           | Rolling update — runs on `main` branch pushes only                     |

### Required GitHub Secret

Add `REDIS_PASSWORD` under **Settings → Secrets and variables → Actions**.

---

## Architecture

```
Browser → frontend:3000 → api:8000 → redis (internal)
                                          ↑
                                     worker (polls)
```

---

## Security Highlights

- Redis is never exposed to the host network
- All containers run as non-root users
- Secrets are passed via `.env` / GitHub Secrets — never baked into images
- Trivy blocks deployments with CRITICAL CVEs
- Hardcoded-secret detection runs in CI