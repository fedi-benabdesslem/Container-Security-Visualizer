# `enhance-plan.md` - Enhancement Plan (Execution-Ready)

## Summary
Stabilize build/runtime first, harden security second, then decouple ingestion for scale.  
The first milestone is a safe, buildable baseline that preserves existing behavior for local development.

## Implementation Changes
1. **Baseline Reliability (Quick Wins)**
- Fix malformed frontend URL literals in API and websocket hooks.
- Remove stray JSX artifacts and restore clean build/lint baseline.
- Add basic runtime guards for missing/bad API base URL config.
- Keep behavior backward-compatible for current docker-compose flow.

2. **Security Hardening (High Priority)**
- Add optional collector authentication for ingest endpoints using `X-Collector-Api-Key`.
- Introduce env/config key `COLLECTOR_API_KEY`; enforce only when configured.
- Keep unauthenticated local dev behavior when key is unset.
- Disable debug defaults in repo configs and align env variable naming (`BACKEND_DEBUG`, `BACKEND_RELOAD`).
- Remove weak password defaults from committed config templates and require explicit value at deploy time.

3. **Ingestion Safety Controls**
- Enforce max batch size on `/api/events/batch` from config.
- Reject oversize payloads early with explicit 4xx responses.
- Add bounded queue/backpressure handling in collector to avoid unbounded memory growth.
- Add ingest request timeout/retry policy with bounded retries and structured errors.

4. **Performance & Data Path Improvements**
- Move timeline aggregation to SQL (`date_trunc`) and return bounded windows.
- Decouple websocket fanout from ingest transaction path via async queue in backend process.
- Keep API contract unchanged for frontend while improving server-side execution.

5. **Codebase Cleanup & Maintainability**
- Remove tracked compiled artifacts (`__pycache__`, `.pyc`) and enforce ignore policy.
- Remove clearly unused placeholder files and dead modules.
- Prune unused UI component files/deps to reduce surface and update churn.
- Add minimal CI checks for backend syntax, frontend build, lint, and dependency audit.

## Public Interfaces / Config Changes
- New optional request header: `X-Collector-Api-Key` on ingest endpoints.
- New optional env var: `COLLECTOR_API_KEY`.
- Clarified backend env usage: `BACKEND_DEBUG`, `BACKEND_RELOAD`.
- Batch ingest now returns explicit validation errors when batch exceeds configured max.

## Test Plan
- Frontend:
  - `npm run build` must pass.
  - `npm run lint` must pass or only known-accepted warnings remain.
- Backend:
  - Ingest accepts valid event with auth disabled.
  - Ingest rejects missing/invalid auth when `COLLECTOR_API_KEY` is set.
  - Batch ingest rejects payloads above max batch size.
  - Timeline endpoint returns correct interval buckets using SQL aggregation.
- Integration:
  - Collector -> backend -> websocket live path works with and without auth (based on config).
  - Historical endpoints still return prior-compatible response shape.

## Assumptions and Defaults
- Local/dev deployments remain easy: auth disabled unless `COLLECTOR_API_KEY` is set.
- Existing API response schemas remain backward-compatible unless explicitly noted.
- Privileged collector model stays for now; hardening focuses on access controls and operational safeguards.
- No major architectural split (broker/microservices) in this phase; only preparatory decoupling inside current backend service.
