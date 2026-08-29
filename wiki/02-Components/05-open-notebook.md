# Open Notebook — Knowledge Management

> Phase 7 — Privacy-focused research + knowledge management for SymbioteOS.
> Built on [Open Notebook](https://github.com/lfwa/open-notebook) with SurrealDB backend.

## Status: **Running** ✅

### Architecture
```
┌─────────────────────────────────────────────┐
│  portable SSD host (Venom SSD)                   │
│                                              │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Frontend   │  │  Backend  │  │ SurrealDB│ │
│  │  (Next.js)  │  │  (FastAPI│  │  (v2.1.4)│ │
│  │  Port 8502  │  │  Port 5055│  │ Port 8000│ │
│  └──────┬──────┘  └────┬─────┘  └─────┬────┘ │
│         │ API calls     │              │      │
│         └───────────────┼──────────────┘      │
│                         │                      │
│  ┌─────────────────────┴─────────────────────┐ │
│  │  Nous Research API (poolside/laguna-s-2.1) │ │
│  │  https://inference-api.nousresearch.com   │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### Components

| Component | Port | Version | Notes |
|-----------|------|---------|-------|
| **Frontend** | 8502 | Next.js 15 | Web UI for notebooks, sources, insights |
| **Backend API** | 5055 | FastAPI | REST + WebSocket API |
| **SurrealDB** | 8000 | v2.1.4 | Vector store + conversation memory |
| **Docker** | — | 26.1.5 | Container runtime |

### Setup

#### Prerequisites
- Docker 26+ with user in `docker` group
- `SURREAL_URL` pointing to SurrealDB instance
- Nous Research API token (from `~/.hermes/shared/nous_auth.json`)

#### Installation
```bash
# 1. Start SurrealDB (v2.1.4 — matches Python client compatibility)
sg docker -c "docker run -d --name surrealdb \
  -p 8000:8000 --restart unless-stopped \
  surrealdb/surrealdb:v2.1.4 \
  start --user=root --pass=symbioteos --bind 0.0.0.0:8000 memory"

# 2. Start Open Notebook
sg docker -c "docker run -d --name open-notebook \
  --add-host=host.docker.internal:host-gateway \
  -p 3000:3000 -p 5055:5055 -p 8502:8502 \
  -e OPENAI_API_KEY=<your-nous-token> \
  -e OPENAI_BASE_URL='https://inference-api.nousresearch.com/v1' \
  -e DEFAULT_MODEL_NAME='poolside/laguna-s-2.1:free' \
  -e SURREAL_URL='ws://host.docker.internal:8000/rpc' \
  -e SURREAL_USER=root -e SURREAL_PASS=symbioteos \
  -e SURREAL_NAMESPACE=main -e SURREAL_DATABASE=main \
  --restart unless-stopped \
  chewcw/open-notebook:20260422"
```

#### Quick Start
```bash
~/bin/open-notebook           # Start (with auto-SurrealDB)
~/bin/open-notebook status    # Check running services
~/bin/open-notebook logs      # View logs
~/bin/open-notebook restart   # Restart container
~/bin/open-notebook stop      # Stop container
```

### Known Issues & Fixes

1. **Cbor encoding error** (`Invalid schema for Cbor WS encoding`)
   - **Cause:** `SURREAL_NAMESPACE` and `SURREAL_DATABASE` env vars must be set
   - **Fix:** Set both to `main` (the default SurrealDB namespace/database)

2. **SQL parse error during migration** (`Found 'title' in SELECT clause... GROUP BY`)
   - **Cause:** SurrealDB v1.5.0 incompatible with migration SQL
   - **Fix:** Use SurrealDB v2.1.4 (matches the image's expected version)

3. **Frontend not on port 3000**
   - The Next.js frontend binds to port 8502, not 3000
   - Port 3000 is mapped but unused by the frontend process

### API Endpoints

```
GET  /health              — Health check
GET  /                   — API info
GET  /docs               — OpenAPI docs
GET  /api/notebooks      — List notebooks
GET  /api/sources        — List sources
GET  /api/notes          — List notes
GET  /api/insights       — List insights
```

### Integration with SymbioteOS

- **Hive Sync**: Open Notebook data persists in `/tmp/open-notebook-data/` (Docker volume)
- **Paper Review**: Daily cron job feeds paper summaries as notes
- **Venom Brain**: Notes can be exported to `~/.symbiote-brain/` for vault sync

See also:
- [[../05-Reference/00-cli-reference]]
- [[02-toxin-android]]
