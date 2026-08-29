# Symbiote-OS

> Local-first, portable agentic operating system.
> **Venom** (Debian 13 SSD) + **Tendril** (Tor) + **Toxin** (Android + microG).
> **CLIs:** Hermes + Codex + Copilot + OpenAI API. (Model runtime: llama.cpp on host.)

**Status:** Phase 1–7 active. Venom portable SSD ready. Tendril (Tor onion service) integrated. Toxin prototype scaffolded. Soul identity layer designed. Copilot CLI active.

---

## The Concept

**Symbiote OS** is a privacy-first, portable brain you can carry on a USB SSD and boot on any UEFI laptop. It consists of:

- **Venom** (SSD brain) — Debian 13 + Hyprland, portable across machines
- **Eddie** (host body) — Any UEFI laptop
- **The Hive** — 3-cage vault (Life-OS / Business-Private / Claude-Brain), synced via cloud storage
- **Carnage** — ACL enforcement + PII redaction + audit logging
- **Phage** — LLM layer (llama.cpp local + cloud providers)
- **Tendril** — Tor onion service + OTG amnesic jump-box (Tails/LiveOS)
- **Toxin** — Mobile spawn (Android + microG, prototype)
- **Soul** — Persistent agent identity layer (cross-surface continuity)
- **Copilot** — GitHub Copilot CLI (4th brain, code review + repo ops)

All three setups (Venom/Eddie, OTG Tendril, Toxin phone) sync securely via Tor without leaving traces.

---

## Quick Start

### Option A: Automatic Install (Recommended)

```bash
cd ~/projects
git clone https://github.com/MaliceHermes/symbiote-os.git
cd symbiote-os
bash install.sh
```

The install script will:
- ✅ Create directory structure
- ✅ Clone/install all dependencies
- ✅ Initialize The Hive (`.symbiote-brain/`)
- ✅ Set up Carnage ACL
- ✅ Configure environment files
- ✅ Start Venom orchestrator + frontend

### Option B: Manual Steps

Follow the three master build guides:
1. [SYMBIOTE_BUILD_VENOM_SURFACE_PRO4.md](SYMBIOTE_BUILD_VENOM_SURFACE_PRO4.md) — Debian 13 SSD setup
2. [SYMBIOTE_ORCHESTRATOR_BOOTSTRAP_REVISED.md](SYMBIOTE_ORCHESTRATOR_BOOTSTRAP_REVISED.md) — Orchestrator + CLIs
3. [SYMBIOTE_TENDRIL_TOXIN_INTEGRATION.md](SYMBIOTE_TENDRIL_TOXIN_INTEGRATION.md) — Tor + OTG + Android

---

## Architecture

```
┌─────────────────────────────────────┐
│   Host Machine (Eddie)              │  Temporary host
│  ┌─────────────────────────────┐  │
│  │ Venom (SSD)                 │  │  Debian 13 + Hyprland
│  │ • Orchestrator (:3030)      │  │  Hermes, Codex, Copilot
│  │ • The Hive (3 cages)        │  │  Carnage, Tendril, Soul
│  │ • Carnage ACL               │  │
│  │ • Soul (identity)           │  │
│  └─────────────────────────────┘  │
│          ↓                          │
│   Tor onion :3030                 │
└─────────────┬───────────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───▼──────────┐   ┌─────▼──────────┐
│ OTG Tails    │   │  Toxin Phone   │
│ (jump-box)   │   │  (Android)     │
│ USB-C OTG    │   │  Prototype     │
│ Amnesic      │   │  microG +      │
│ Tendril      │   │  Syncthing     │
└──────────────┘   └────────────────┘
```

---

## Three Brains + Shell

| Brain | CLI | Role | Status |
|---|---|---|---|
| **Hermes** | v0.20.4 | Chief-of-staff reasoning (primary agent) | ✅ Ready |
| **Codex** | latest | Code execution (implements Hermes designs) | ✅ Ready |
| **Copilot** | latest | Code review + repo ops (4th brain) | ✅ Active |
| **Phage** | llama.cpp | Local inference (Qwen2.5-3B Q4_0) | ✅ Ready |

### Workflow: Design → Implement → Review

1. **Type prompt in frontend** or chat with Hermes
2. **Hermes** — designs solution, outputs architecture doc
3. **Codex** — receives design, implements in code
4. **Copilot** — code review, PR creation, suggestions (via ACP or CLI)
5. **All → Hive** — saved to `~/.symbiote-brain/`, synced via cloud storage

Example: `"Build Python script to sync vault to S3"`
→ Hermes designs (config, error handling, logging)
→ Codex implements (working script, tests)
→ Copilot reviews (lint, security, best practices)

---

## Phage — LLM Layer

| Model | Provider | Purpose |
|---|---|---|
| `poolside/laguna-s-2.1:free` | Nous Research | Primary reasoning (via Hermes) |
| `Qwen2.5-3B-Instruct-Q4_0` | llama.cpp (host) | Local inference (systemd service on :8080) |
| `gpt-4o` | OpenAI (cloud) | Cloud reasoning |

**Fallback chain:** Nous → OpenRouter (Claude Sonnet) → Z.ai (GLM-4.5)

---

## Phases

### ✅ Phase 1: Venom (Complete)
Portable Debian 13 SSD + Hyprland desktop + all CLIs

### ✅ Phase 2: Hive (Active)
3-cage vault structure + cloud sync

### ✅ Phase 3: Carnage (Active)
OS-level ACL + PII redaction + audit logging

### ✅ Phase 4: Phage (Active)
llama.cpp (Qwen2.5-3B) as host systemd service + Nous Research + OpenAI cloud

### ✅ Phase 5: Tendril (Ready)
Tor onion service + Tails OTG jump-box

### ✅ Phase 6: Toxin (Prototype)
Android Studio + microG AVD + Syncthing sync

### ✅ Phase 7: Soul (Active)
Persistent agent identity layer — `brain-state.json`, `Claude-Brain/BRAIN.md`

### ✅ Phase 7b: Copilot (Active)
GitHub Copilot CLI — code review and repo operations

### ✅ Phase 8: Hardening (Active)
Debian 13 security baseline — Docker resource limits, Caddy security headers, filesystem permissions

### ✅ Phase 9: Tor Onion Service (Active)
Hidden service for orchestrator — onion routing, stream isolation, SOCKS proxy

### ✅ Phase 10: Toxin Integration (Active)
Android prototype connected via ADB reverse port forwarding + Tor onion

---

## Project Structure

```
symbiote-os/
├── install.sh                  # One-click setup script
├── start.sh                    # Start orchestrator + frontend
├── stop.sh                     # Stop all services
├── AGENTS.md                   # Project guide for Copilot/Hermes/Codex
| docker-compose.yml          | Docker stack (Caddy, n8n, Nextcloud, MariaDB, OnlyOffice) |
├── .env                        # Environment file (NOT committed to git)
├── frontend/                   # React + Vite + Tailwind UI
│   ├── App.jsx                 # Main app (Hive/Carnage/Phage/Roadmap tabs)
│   └── src/                    # Component source
├── orchestrator/               # Node.js + Express backend (:3030)
│   ├── carnage-acl.js          # ACL enforcement + PII redaction
│   ├── temporal-prompt.js      # Temporal logic prompt engine
│   └── index.js                # Main server
├── config/                     # Service configs (Caddy, n8n, Nextcloud)
│   ├── caddy/Caddyfile         # Reverse proxy routes
│   └── n8n_data/               # n8n workflows + credentials
├── toxin/                      # Android app (microG + Syncthing)
│   ├── app/                    # Main Android app source
│   └── setup scripts           # microG, F-Droid, Aurora Store
├── tendril/                    # Tor + OTG jump-box
└── wiki/                       # Knowledge base (synced from cloud storage)
    ├── 01-Architecture/        # Venom, Hive, Carnage, Phage, Soul
    └── 02-Components/          # Tendril, Toxin, AgentMail, Open Notebook
```

---

## Live Services

| Service | URL / Port |
|---|---|
| Orchestrator | http://localhost:3030 |
| Frontend | http://localhost:5173 |
| llama.cpp | http://localhost:8080/v1 |
| Caddy (reverse proxy) | http://localhost:80 |
| n8n (workflow engine) | http://localhost:5678 |
| Nextcloud | http://localhost:8090 |
| OnlyOffice | http://localhost:8083 |
| MariaDB | localhost:3306 (Docker network) |
| Tor SOCKS | localhost:9050 |
| Tor Onion | onion address hidden (security) |
| Toxin AVD | 127.0.0.1:3030-8090 (via ADB reverse) |

---

## Environment

```bash
# .env (NOT committed to git)
ORCHESTRATOR_PORT=3030
SYMBIOTE_HIVE_ROOT=~/.symbiote-brain
JARVIS_PROJECTS_ROOT=~/projects
N8N_BASIC_AUTH_PASSWORD=symbiote
MYSQL_PASSWORD=«MYSQL_PASSWORD_PLACEHOLDER»
MYSQL_DATABASE=nextcloud
MYSQL_USER=nextcloud
```

---

## Security

- **Carnage ACL:** Business-Private cage locked at OS level
- **PII Redaction:** SSN, phone, email, address auto-stripped before handoff
- **Audit Logging:** Every redaction stamped with SHA256, logged to `.carnage_audit.log`
- **Tor Encryption:** Venom ↔ Tendril ↔ Toxin all via Tor onion service
- **Amnesic Jump-Box:** Tails/LiveOS leaves no trace on host
- **No Secrets in Git:** API keys, service addresses, credentials never committed

---

## Next Steps

1. ✅ Clone this repo (you're here)
2. ✅ Run `bash install.sh` to set up locally
3. ✅ Follow `SYMBIOTE_BUILD_VENOM_SURFACE_PRO4.md` to build portable SSD
4. ✅ Follow `SYMBIOTE_ORCHESTRATOR_BOOTSTRAP_REVISED.md` to run orchestrator
5. ✅ Follow `SYMBIOTE_TENDRIL_TOXIN_INTEGRATION.md` to set up Tor + OTG + Android
6. ⏳ Build React frontend (Hive | Chats | Carnage | Roadmap tabs)
7. ⏳ Test end-to-end: Venom → Tendril → Toxin via Tor

---

## Author

**Malice** — learning in public, building Symbiote-OS as a year-long infrastructure journey.

Read the build log: https://mallic3.substack.com

---

## License

MIT
