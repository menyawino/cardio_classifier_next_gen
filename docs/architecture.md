# Architecture Detail

## Components
1. Backend API (FastAPI)
2. MCP Server (data acquisition microservice) exposing tools:
   - clinvar_lookup(hgvs)
   - gnomad_summary(hgvs)
   - in_silico_predictions(hgvs)
3. ACMG Engine (within backend) orchestrates rule evaluation.
4. Frontend SPA (React/Vite) interacts with backend `/variants/classify`.

## Data Flow
User submits HGVS -> Backend enqueues / executes evidence aggregation -> Calls MCP server tools (HTTP) -> Normalizes evidence -> Applies rule evaluators -> Persists snapshot -> Returns classification & evidence table.

## Rule Engine Strategy
Each rule implemented as a function or class with signature `(variant_ctx) -> EvidenceItem | None`. Variant context is a dataclass containing normalized variant, gene info, population frequencies, computational predictions, segregation, etc. Engine runs all rules, filters unsatisfied, performs conflict resolution (e.g., PVS1 with BP7) and calculates final classification with standard combining logic.

## Classification Logic (Planned Full Matrix)
Pathogenic: (1 VeryStrong + >=1 Strong) OR (1 VeryStrong + >=2 Moderate) OR (1 VeryStrong + 1 Moderate + 1 Supporting) OR (>=2 Strong + >=1 Moderate) OR (1 Strong + >=3 Moderate) OR (1 VeryStrong + >=2 Supporting) etc.
Likely Pathogenic: (1 VeryStrong + 1 Moderate) OR (1 Strong + 1-2 Moderate + >=2 Supporting) ... (Simplified currently).
Benign: (1 StandAlone) OR (>=2 StrongBenign)
Likely Benign: (1 StrongBenign + 1 SupportingBenign) OR (>=2 SupportingBenign)

Will implement full grid with scoring abstraction mapping to thresholds.

## MCP Integration
The MCP server provides structured, cacheable endpoints; backend may implement an adaptive caching layer (Redis) keyed by hgvs|build. Rate limiting and exponential backoff for external APIs (ClinVar, gnomAD, UniProt) via tenacity.

## Future Enhancements
- Websocket progress updates
- User curated evidence overrides
- Audit & version lineage
- Multi-variant batch classification CSV import
- Authentication & roles

