# SymbioteOS Copilot Instructions

## Who I Am

**SymbioteOS** is a privacy-first, portable agentic operating system running from a USB SSD ("Venom") that syncs across three surfaces via Tor.

### Metaphor Map
| Name | Role | Path |
|---|---|---|
| **Venom** | Portable SSD brain (Debian 13 + Hyprland) | `/` portable SSD |
| **Eddie** | Host body (portable SSD host) | Temporary |
| **Hive** | 3-cage vault (Life-OS, Business-Private, Claude-Brain) | `~/.symbiote-brain/` |
| **Carnage** | ACL + PII redaction + audit logging | `orchestrator/carnage-acl.js` |
| **Phage** | LLM layer (Ollama local + OpenAI/Nous cloud) | `~/.hermes/config.yaml` |
| **Tendril** | Tor + OTG amnesic jump-box | `orchestrator/tendril/` |
| **Toxin** | Android prototype (microG + Syncthing) | `toxin/` |
| **Soul** | Persistent agent identity | `~/.symbiote-brain/Claude-Brain/` |

## My Workflow

1. **Hermes** designs solutions (architecture docs)
2. **Codex** implements them (code execution)
3. **Copilot** reviews + creates PRs (you are here)
4. Results → **Hive** for persistence

## Security Rules (Carnage ACL Enforced)

- **Never commit secrets** — `.env`, API keys, Tor private keys, `.onion` addresses
- **PII redaction** — flag SSN, phone, email, address in code/outputs
- **No binaries** — exclude `cmdline-tools.zip`, `gradle-wrapper.jar`, `local.properties`
- Business-Private cage is OS-locked (hermes user blocked)

## Project Structure

```
symbiote-os/
├── install.sh                  # One-click setup
├── start.sh                    # Start all services
├── stop.sh                     # Stop all services
├── AGENTS.md                   # Detailed project guide
├── frontend/                   # React + Vite + Tailwind (:5173)
├── orchestrator/               # Node.js backend (:3030)
├── toxin/                      # Android app (microG + Syncthing)
├── tendril/                    # Tor + Tails OTG
├── wiki/                       # Knowledge base (from MEGA)
├── .gitignore                  # Excludes binaries, .env, etc.
└── .github/copilot-instructions.md  # Detailed Copilot config
```

## Build & Test

```bash
# Orchestrator
cd orchestrator && npm install && npm start

# Frontend
cd frontend && npm install && npm run dev && npm run build

# Toxin (Android)
cd toxin && ./scripts/setup-toxin.sh && ./gradlew build
```

## Commit Convention

```
Component: Brief description

What changed and why.

Refs: #issue
```

Example: `Toxin: Add temporal logic to ComponentState.kt`

## Code Style

- Comments reference the Symbiote metaphor: `// Carnage: validate PII before Toxin sync`
- Kotlin for Android (Toxin), JavaScript/React for frontend, Node.js for orchestrator
- Keep changes minimal — this is a learning-in-public project
- Reference `wiki/` docs for architecture decisions

## Testing

- Run existing tests before changes
- Add/update tests for new code
- Verify builds compile in all 3 layers (orchestrator, frontend, toxin)
