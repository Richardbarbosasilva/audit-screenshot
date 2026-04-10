# Product Rollout Status

## Context

This report consolidates the current state of the Screenshot Audit project after the lab phase
of infrastructure, endpoint flow and initial product backend delivery.

It is meant to answer three questions:

1. what is already working
2. what is being used as the current technology baseline
3. what comes next in the product roadmap

---

## What Is Already Working

### Operational control plane

- `Semaphore UI` running with custom UI and `Ativos` integration
- `Ansible + WinRM/PSRP + Kerberos` validated against the Windows pilot hosts
- `GPO` used only for bootstrap concerns such as `WinRM`
- `ShareX` deployed and redirected to the controlled spool
- `Lightshot` removed in the pilot

### Endpoint layer

- `ScreenshotAuditAgent` running as a Windows service
- spool at `%ProgramData%\\ScreenshotAudit\\spool`
- temporary files at `%ProgramData%\\ScreenshotAudit\\tmp`
- durable local queue in `SQLite`
- queue path:
  - `%ProgramData%\\ScreenshotAudit\\data\\queue.db`
- local watermark generation working
- upload to `MinIO` working
- heartbeat and ingest confirmation to the central API working

### Central platform

- `PostgreSQL` database:
  - `audit_sharex`
- `Redis` already available in infrastructure
- `MinIO` buckets already provisioned
- `FastAPI` telemetry/ingest backend already running
- operational page `/ativos` already running
- initial product pages already created:
  - `/produto`
  - `/produto/eventos`
  - `/produto/casos`

---

## Current Technology Decisions

### Backend

Current choice:

- `FastAPI`
- `SQLAlchemy`
- `psycopg`
- `Redis`
- `boto3`
- `PostgreSQL`
- `MinIO`

Why:

- the agent is already Python
- OCR, enrichment and scoring fit naturally in Python
- API and worker can share the same domain model
- operational and product backend can evolve in one repository without artificial split

### Frontend

Current MVP choice:

- `FastAPI + Jinja templates + CSS + vanilla JS`

Why:

- fastest way to deliver the first internal product screens
- avoids prematurely creating another application surface
- enough for dashboard, review queue, detail pages and admin bootstrap

Future likely evolution:

- dedicated SPA only if the review workflow becomes significantly more interactive
- likely candidates:
  - `React + Vite`
  - or `Next.js`

### What We Are Not Using Now

- `MongoDB`
- `Flask`

Reason:

- current domains are strongly relational
- `PostgreSQL + Redis + MinIO` already cover the needs well
- adding a second Python web framework now would increase complexity without benefit

---

## Repository Strategy

### Backend repository

Keep using:

- `leakguard-api`

This repository is already the correct home for:

- telemetry
- ingest
- event catalog
- risk scoring
- review cases
- product templates
- workers

### Operational repository

Keep using:

- `leakguard`

This remains the home for:

- agent
- Windows service logic
- rollout playbooks
- operational runbooks
- infrastructure helper files

### Frontend repository

Not required yet.

Recommendation:

- only create a dedicated frontend repo after backend contracts, IAM and review flow stabilize

---

## Docker Rollout Decision

We are now moving the product backend to Docker in the lab infrastructure.

### Deployment approach

Use one image with two runtimes:

- `api`
- `worker`

### Deploy artifacts prepared

In `leakguard-api`:

- `Dockerfile`
- `deploy/start-api.sh`
- `deploy/start-worker.sh`
- `deploy/docker-compose.lab.yml`
- `deploy/.env.lab.example`

### Intended public lab URLs

- `http://leakguard.homelab.local`
- `http://leakguard-api.homelab.local`

These are exposed through `Traefik`.

### Windows hosts file note

For lab access from the Windows workstation, add host entries pointing these names to the lab Linux host IP.

Example:

```txt
192.168.1.12 leakguard.homelab.local
192.168.1.12 leakguard-api.homelab.local
```

### Current Docker Status

The product stack is already running in Docker on the lab host.

Current containers:

- `LEAKGUARD-API`
- `LEAKGUARD-WORKER`

Current image:

- `local/leakguard:product-v1`

Current compose path:

- `/opt/1panel/docker/compose/leakguard/docker-compose.yml`

Current env path:

- `/opt/1panel/docker/compose/leakguard/.env`

### Current Live Access Validation

Validated through the reverse proxy:

- `http://leakguard.homelab.local/health`
- `http://leakguard.homelab.local/ativos`
- `http://leakguard.homelab.local/produto`
- `http://leakguard.homelab.local/produto/eventos`
- `http://leakguard.homelab.local/produto/casos`
- `http://leakguard-api.homelab.local/health`

Temporary direct port access is also still available:

- `http://192.168.1.12:8010`

---

## Redis And Backend Scope Right Now

We do still need the backend side of Redis from the beginning.

This is not a later optional piece.

Why:

- the API should receive and persist quickly
- analysis must be decoupled from HTTP ingest
- worker processing must happen outside the request thread

So the correct order is:

1. bring the minimal product web interface online
2. bring the worker online in the same stack
3. keep Redis in the path from day one

This means we are not choosing between:

- “interface first”
- or “backend/Redis first”

We are shipping the minimal product stack together:

- API
- worker
- Redis
- Postgres
- MinIO
- web interface

### Exact MVP Stack From This Point Forward

- `FastAPI` for API and first product pages
- `Jinja templates` for the first web UI
- `CSS + vanilla JS` for the first interaction layer
- `PostgreSQL` as the source of truth
- `Redis` for queue and transient processing state
- `MinIO` for screenshots and artifacts
- `Python worker runtime` for analysis/scoring jobs

This keeps the system simple while still matching the final architecture.

---

## Product Screens Now Available

### Operational

- `/ativos`

Purpose:

- agent health
- heartbeat
- queue state
- endpoint drill-down

### Product MVP

- `/produto`
- `/produto/eventos`
- `/produto/casos`

Purpose:

- dashboard executivo inicial
- catalog of screenshot events
- review queue bootstrap

---

## Next Steps

### Immediate product phase

1. stabilize product backend contracts
2. mature the review queue and event detail
3. implement secure preview and access audit
4. connect Redis-backed worker flow for OCR/scoring promotion
5. define IAM baseline:
   - `LDAP/OIDC`
   - `TOTP`
   - `RBAC`

### Near-term UX phase

1. improve dashboard KPI layout
2. improve event filters and review workflow
3. add host and user drill-down views
4. add policy and retention screens

### Infra hardening phase

1. convert local image build to versioned registry image
2. add production-grade `.env` and secret handling
3. define lifecycle/retention by severity
4. enable encryption and access audit for evidence handling

---

## Recommended Next Product Steps

### Step 1. Put the product stack behind Docker and Traefik

- build image
- run API container
- run worker container
- validate URLs

### Step 2. Secure evidence access

- preview endpoint
- short-lived object access
- access audit log on visualization/download

### Step 3. Review workflow

- assign case
- change case status
- add reviewer comments
- basic SLA lifecycle

### Step 4. IAM

- `LDAP` or `OIDC`
- `TOTP`
- `RBAC`
- scoped visibility by tenant/site

### Step 5. Better risk pipeline

- OCR maturity
- configurable rules
- promotion thresholds
- false-positive loop

---

## Strategic Recommendation

The operational phase is no longer the bottleneck.

The next bottleneck is product maturity:

- secure evidence access
- review ergonomics
- IAM
- scoring quality

The project should now be treated as a real internal product, not only as an automation flow.
