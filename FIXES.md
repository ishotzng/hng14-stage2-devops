# FIXES.md

All bugs found in the starter repository, with file, line, problem, and fix.

---

## api/main.py

**Bug 1 — Hardcoded Redis host**
- Line: 8
- Problem: `host="localhost"` fails inside Docker because Redis is a separate container, not localhost
- Fix: Changed to `host=os.getenv("REDIS_HOST", "localhost")`

**Bug 2 — Hardcoded Redis port**
- Line: 8
- Problem: `port=6379` hardcoded, not configurable without editing source
- Fix: Changed to `port=int(os.getenv("REDIS_PORT", 6379))`

**Bug 3 — Redis password never passed to client**
- Line: 8
- Problem: `REDIS_PASSWORD` was defined in .env but never read or passed to `redis.Redis()`
- Fix: Added `password=os.getenv("REDIS_PASSWORD")` argument

**Bug 4 — .env file never loaded**
- Line: (missing)
- Problem: No `load_dotenv()` call anywhere, so all `os.getenv()` calls return None
- Fix: Added `from dotenv import load_dotenv` and `load_dotenv()` before Redis init

**Bug 5 — Job not found returns HTTP 200 instead of 404**
- Line: ~20
- Problem: `return {"error": "not found"}` sends HTTP 200 which means success
- Fix: Changed to `return JSONResponse(status_code=404, content={"error": "not found"})`

---

## api/requirements.txt

**Bug 6 — python-dotenv missing**
- Line: (missing)
- Problem: `load_dotenv()` requires `python-dotenv`. Without it the app crashes on import
- Fix: Added `python-dotenv` to requirements.txt

---

## api/.env

**Bug 7 — Real password committed to source control**
- Line: 1
- Problem: `REDIS_PASSWORD=supersecretpassword123` — a real credential visible in git history
- Fix: Replaced with `REDIS_PASSWORD=your_redis_password_here`

**Bug 8 — REDIS_HOST and REDIS_PORT missing**
- Line: (missing)
- Problem: The fixed code reads these from env but they were never defined
- Fix: Added `REDIS_HOST=redis` and `REDIS_PORT=6379`

---

## worker/worker.py

**Bug 9 — Hardcoded Redis host**
- Line: 6
- Problem: Same as api/main.py — `localhost` does not resolve to the Redis container
- Fix: Changed to `host=os.getenv("REDIS_HOST", "localhost")`

**Bug 10 — Hardcoded Redis port**
- Line: 6
- Problem: Port not configurable
- Fix: Changed to `port=int(os.getenv("REDIS_PORT", 6379))`

**Bug 11 — Redis password never loaded or used**
- Line: 6
- Problem: No password passed to Redis client, no load_dotenv()
- Fix: Added both

**Bug 12 — signal imported but never wired up**
- Line: 4
- Problem: `import signal` present but no handlers registered — graceful shutdown not implemented
- Fix: Added `handle_shutdown` function registered for SIGTERM and SIGINT

**Bug 13 — while True loop at module level with no shutdown path**
- Line: 14
- Problem: Loop runs even on import, and can never be stopped cleanly
- Fix: Wrapped in `if __name__ == "__main__":` and changed to `while running`

**Bug 14 — No error handling in worker loop**
- Line: 14
- Problem: Any exception crashes the worker permanently with no recovery
- Fix: Wrapped loop body in `try/except Exception`

---

## worker/requirements.txt

**Bug 15 — redis package unpinned**
- Line: 1
- Problem: No version pin — a future breaking release could be silently installed
- Fix: Pinned to `redis==5.0.1`

**Bug 16 — python-dotenv missing**
- Line: (missing)
- Problem: `load_dotenv()` requires it but it was not listed
- Fix: Added `python-dotenv==1.0.0`

---

## frontend/app.js

**Bug 17 — Hardcoded API_URL**
- Line: 6
- Problem: `"http://localhost:8000"` hardcoded — fails in Docker where API is a separate container
- Fix: Changed to `process.env.API_URL || "http://localhost:8000"`

**Bug 18 — No CSRF protection**
- Line: 10
- Problem: POST route accepts requests from any origin with no token validation (CWE-352)
- Fix: Added `csurf` and `cookie-parser` middleware, added `/csrf-token` endpoint

**Bug 19 — Unvalidated job ID in URL (SSRF risk)**
- Line: 21
- Problem: Any string in `:id` is interpolated directly into the upstream URL (CWE-918)
- Fix: Added UUID regex validation, returns 400 if ID does not match

---

## frontend/package.json

**Bug 20 — csurf and cookie-parser missing from dependencies**
- Line: (missing)
- Problem: app.js requires both packages but they were not declared
- Fix: Added both to the dependencies section

---

## frontend/views/index.html

**Bug 21 — CSRF token never fetched or sent**
- Line: 21
- Problem: POST requests sent without token — rejected by the CSRF middleware with 403
- Fix: Added `init()` to fetch token on load, passed as `CSRF-Token` header in submitJob

**Bug 22 — No error handling in submitJob or pollJob**
- Line: 21
- Problem: Unhandled promise rejections, no user feedback on failure
- Fix: Wrapped both functions in try/catch, errors shown in the UI

---

## Root level (missing files)

**Bug 23 — No .gitignore**
- Problem: Without it, .env and node_modules could be committed, leaking credentials
- Fix: Created .gitignore covering .env, node_modules/, __pycache__/, etc.

**Bug 24 — No .env.example**
- Problem: No reference file for required environment variables
- Fix: Created .env.example with all required variables set to safe placeholder values

File: frontend/Dockerfile
Line: (The line number where npm ci was)
Issue: The Dockerfile used npm ci, but the repository was missing a package-lock.json file, causing the build to fail.
- Fix: Changed npm ci to npm install (or added the lockfile).