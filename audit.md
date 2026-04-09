# Container Security Visualizer - Engineering Audit
Date: 2026-04-09
Scope: backend, collector, eBPF probes, frontend, compose/runtime config

## Executive Summary
The project has a solid observability concept and workable stack, but it is not production-ready yet.
The most serious blockers are:
- Frontend build is currently broken due to malformed string literals in core API/WS files.
- Backend has no authentication/authorization on ingest/query/websocket routes.
- Security defaults are weak (hardcoded weak DB password defaults, debug-enabled config patterns).
- Data and realtime paths are tightly coupled, limiting scalability under load.
- Significant unused frontend/UI surface adds maintenance overhead.

## 1) System Understanding
Purpose:
- Collect container runtime events (syscall/network) via eBPF.
- Enrich with Docker metadata.
- Persist to PostgreSQL.
- Stream and visualize live + historical security telemetry.

Architecture:
- Collector (privileged): eBPF monitor processes + enrichment + HTTP forwarding.
- Backend (FastAPI): ingest APIs, query/stat/analytics APIs, websocket broadcaster, DB access.
- Frontend (React/Vite): live graph/timeline/alerts + historical querying.
- DB (PostgreSQL): single denormalized `events` table.

Data flow:
1. eBPF probe emits syscall/network JSON.
2. Collector reads monitor stdout and queues events.
3. Event enricher maps PID->container metadata and computes risk/category fields.
4. Collector posts event to backend `/api/events`.
5. Backend writes DB row and broadcasts event to WS clients.
6. Frontend updates graph/timeline/alerts and fetches historical data over REST.

## 2) Code Quality & Design
Strengths:
- Clear module boundaries at directory level.
- SQLAlchemy model has useful indexes.
- FastAPI structure is straightforward to navigate.

Weaknesses:
- Repeated event-mapping logic in single-event and batch endpoints.
- Backend request path mixes persistence and realtime fanout.
- Frontend uses global `(window as any)` bridges between components.
- No automated tests found for source code.
- Generated/compiled artifacts are tracked in git (`__pycache__/*.pyc`).
- Large unused shadcn/Radix UI surface.

## 3) Security Analysis
High/Critical findings:
- No authn/authz around backend APIs and websocket stream.
- Ingestion endpoint can be abused for event injection and DB flooding.
- Debug-mode behavior and exception detail exposure patterns exist.
- Weak default credentials are committed across config templates.
- Collector runs with privileged host-level access and Docker socket mount without defense-in-depth controls.

Medium findings:
- Batch ingest endpoint lacks explicit payload-size and batch-size enforcement from config.
- Collector/utilities contain broad exception swallowing (`except: pass`) and debug logs to local temp files.
- Potential sensitive argv capture/logging risk if process args contain credentials.

Dependency findings:
- `npm audit --omit=dev` reports high-severity advisories (including router and axios advisories).
- Python dependency CVE scan did not complete in this environment due local build/toolchain constraints.

## 4) Performance & Scalability
Bottlenecks:
- Timeline API loads full event set into memory and aggregates in Python.
- Realtime broadcasting happens inline on ingest request path.
- Collector posts one event per HTTP request (no buffering/backpressure strategy).
- Collector queue is unbounded.
- Frontend graph triggers relayout repeatedly as nodes are added.

Expected behavior under load:
- Ingestion latency and API tail latency will rise quickly with event bursts.
- WS fanout instability can impact write throughput.
- Timeline and analytics endpoints will degrade with dataset growth.

## 5) Dependencies & Stack Review
Stack fit:
- FastAPI + SQLAlchemy + Postgres + React is appropriate for v1.

Concerns:
- Frontend dependency set is larger than actual runtime usage.
- Mixed lock artifacts increase dependency drift risk.
- No visible CI pipeline for lint/build/test/security gates.

## 6) Unused / Redundant Features
Likely removable or consolidatable:
- Empty file: `utilities/container_mapper.py`.
- Unused backend processor module: `backend/services/event_processor.py`.
- Unused frontend helper/component surface (multiple `src/components/ui/*`, `NavLink.tsx`, `App.css` not imported).
- Tracked compiled Python cache files.
- Duplicate lock strategy (`package-lock.json` + `bun.lockb`) unless intentionally maintained with policy.

## 7) Overall Assessment
Ratings:
- Code quality: 4/10
- Security: 3/10
- Scalability: 4/10
- Maintainability: 4/10

Final verdict:
- Promising architecture direction with clear domain value.
- Needs immediate hardening and cleanup before any production or exposed deployment.
