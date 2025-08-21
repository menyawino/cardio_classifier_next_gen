# Cardio Classifier (Next-Gen)

An updated cardiovascular variant interpretation platform implementing the latest ACMG/AMP guidelines with automation, evidence aggregation via Model Context Protocol (MCP) data fetchers, and an interactive modern web UI.

## High-Level Architecture

- Frontend: React + Vite + TypeScript + Tailwind + TanStack Query + Zustand.
- Backend API: FastAPI (Python) providing variant submission, evidence aggregation, scoring, audit trail.
- ACMG Engine: Modular rule evaluators with provenance per criterion (e.g., PVS1, PM2, PP3, BS1...).
- MCP Server: Separate service exposing structured tools to fetch external knowledge (ClinVar, gnomAD, UniProt, OMIM, HGMD placeholder, Cardio panels) consumed by backend.
- Task Queue: Celery + Redis for longer evidence aggregation tasks (future enhancement placeholder).
- Database: PostgreSQL via SQLAlchemy + Alembic migrations.
- Auth: JWT (access/refresh) with role-based control (user, curator, admin).
- Observability: Structured logging (loguru), OpenAPI docs, future Prometheus metrics.

## Quick Start (Dev)

Backend:
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Frontend:
```
cd frontend
npm install
npm run dev
```

Docker (all services):
```
cd infra
docker compose -f docker-compose.dev.yml up --build
```

MCP Server (prototype):
```
cd mcp-server
python -m venv .venv && source .venv/bin/activate
pip install -e .
python server.py
```

## ACMG Rule Strategy
Each rule implemented as a class returning EvidenceItem {code, strength, satisfied, rationale, source_refs}. Engine composes and resolves conflicts, then final classification (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign) using the 2015 + ClinGen refinements.

## Roadmap
- [ ] Complete rule coverage & unit tests
- [ ] Real external API integrations
- [ ] Dockerized CI pipeline
- [ ] Async background aggregation jobs
- [ ] User annotation UI & audit diff view
- [ ] Export (PDF/JSON VCI-compatible)

See `docs/architecture.md` for more detail.
