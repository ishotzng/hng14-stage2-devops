# FIXES.md

All bugs found and fixed, plus all marking-criteria gaps addressed.

---

## api/main.py

**Bug 1 — Hardcoded Redis host**
- Line: 8 | Problem: `host="localhost"` fails inside Docker
- Fix: `host=os.getenv("REDIS_HOST", "localhost")`

**Bug 2 — Hardcoded Redis port**
- Line: 8 | Problem: `port=6379` not configurable
- Fix: `port=int(os.getenv("REDIS_PORT", 6379))`

**Bug 3 — Redis password never passed**
- Line: 8 | Problem: `REDIS_PASSWORD` env var never read or used
- Fix: Added `password=os.getenv("REDIS_PASSWORD")`

**Bug 4 — .env never loaded**
- Problem: No `load_dotenv()` call; all `os.getenv()` returned None
- Fix: Added `from dotenv import load_dotenv` and `load_dotenv()`

**Bug 5 — Job not found returned HTTP 200**
- Line: ~20 | Problem: `return {"error": "not found"}` sends HTTP 200
- Fix: `return JSONResponse(status_code=404, content={"error": "not found"})`

**Bug 6 — Missing /health endpoint**
- Problem: No health endpoint for Docker HEALTHCHECK or CI polling
- Fix: Added `GET /health` that pings Redis and returns `{"status": "ok"}`

---

## api/requirements.txt

**Bug 7 — python-dotenv missing**
- Fix: Added `python-dotenv==1.0.1`

**Bug 8 — httpx missing (required by FastAPI TestClient)**
- Fix: Added `httpx==0.27.0`

---

## worker/worker.py

**Bug 9 — Hardcoded Redis host/port/password**
- Fix: All three read from environment variables via `os.getenv()`

**Bug 10 — No graceful shutdown**
- Fix: `SIGTERM`/`SIGINT` handlers set `running = False`; loop exits cleanly

**Bug 11 — `while True` at module level**
- Fix: Wrapped in `if __name__ == "__main__":` and changed to `while running`

**Bug 12 — No error handling in worker loop**
- Fix: `try/except Exception` wraps loop body; worker sleeps 2s and continues

---

## docker-compose.yml

**Gap 1 — No restart policies**
- Fix: Added `restart: always` to redis; `restart: on-failure` to api, worker, frontend

**Gap 2 — No resource limits**
- Fix: Added `deploy.resources.limits` (cpu + memory) to all services

**Gap 3 — Redis had no password**
- Fix: Redis command now includes `--requirepass ${REDIS_PASSWORD}`; healthcheck uses `-a`

**Gap 4 — Environment vars hardcoded inline**
- Fix: Replaced inline `environment:` blocks with `env_file: - .env` on all services

**Gap 5 — Redis port exposed to host (risk)**
- Fix: Removed any `ports:` from redis; it is only reachable on the internal network

---

## api/Dockerfile — created from scratch

- Multi-stage build: `builder` stage installs deps; final stage is minimal
- Base image: `python:3.11-slim` (slim variant)
- Non-root user: `RUN adduser --disabled-password ... appuser`
- `USER appuser` instruction present
- `HEALTHCHECK` instruction present
- No `ENV` instructions that leak secrets

---

## frontend/Dockerfile — created from scratch

- Multi-stage build: `builder` installs node_modules; final stage copies only what's needed
- Base image: `node:20-alpine` (alpine variant)
- Non-root user: `RUN adduser -D -H -S appuser`
- `HEALTHCHECK` instruction using `wget`
- `npm ci` → `npm install` (lockfile not present in repo)

---

## worker/Dockerfile — created from scratch

- Multi-stage build with `python:3.11-slim`
- Non-root user via `adduser`
- `HEALTHCHECK` pings Redis to verify connectivity

---

## .github/workflows/ci.yml — created from scratch

- **Lint job**: Flake8, ESLint, Hadolint, secrets detection (grep-based)
- **Test job**: Pytest + coverage, uploads XML artifact
- **Build job**: Builds all 3 images with SHA tag + `latest`; layer caching via `cache-from/cache-to gha`
- **Security job**: Trivy scans all images, fails on CRITICAL, exports SARIF artifacts
- **Integration job**: Spins up full Compose stack, runs `integration.sh`, teardown in `always` step
- **Deploy job**: Only on `main` branch; rolling update service-by-service

---

## integration.sh — created

- Health check → submit job → poll until `completed` with 60 s timeout
- Exits 0 on success, 1 on failure or timeout

---

## api/tests/test_api.py — created

- 5 tests covering: health, job submission, status retrieval, 404 for missing job, missing payload
- Redis fully mocked with `unittest.mock.patch` — no live Redis required

---

## .env.example — updated

- All required variables present with safe placeholder values
- Inline comments explain each variable

---

## Root / Miscellaneous

**Bug 13 — Real Redis password committed**
- Fixed: `.env` excluded via `.gitignore`; `.env.example` uses placeholder

**Bug 14 — No .gitignore**
- Fixed: `.gitignore` covers `.env`, `node_modules/`, `__pycache__/`, coverage artefacts