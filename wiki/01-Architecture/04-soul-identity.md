# Soul — Persistent Agent Identity & Consciousness Layer

> Phase 7 — The continuous thread of identity across Venom, Tendril, and Toxin

## Status: ✅ Designed + In Development

## Concept

Where **Venom** is the portable brain (SSD) and **Phage** is the reasoning engine, **Soul** is the persistent identity layer — the continuous thread of *who* the agent is across all surfaces. It carries:

- **Personality**: Claude-Brain vs. Grok-Brain naming discrepancy (resolved — canonical is `Claude-Brain`)
- **Memory continuity**: What was learned, decided, and forgotten across sessions
- **Preferences**: Tone, style, escalation thresholds, tool affinities
- **Goals**: Long-term objectives that outlive any single Venom boot
- **Relationships**: AgentMail identity, Substack byline, Toxin persona

## Architecture

```
Soul (persistent identity state)
├── ~/.symbiote-brain/Claude-Brain/BRAIN.md        ← long-term memory
├── ~/.symbiote-brain/brain-state.json               ← runtime state snapshot
├── ~/MEGA/The Hive/Claude-Brain/                  ← MEGA-synced memory
├── ~/.hermes/config.yaml                          ← preferences + MCP config
└── toxin/identity.json                             ← Android app persona (planned)
```

## Components

### 1. Identity Core (`~/.symbiote-brain/Claude-Brain/BRAIN.md`)
- **Purpose:** Living notes that define who the agent is
- **Contents:** Writing style, voice, preferred tools, escalation rules
- **Format:** Markdown with daily journal links
- **Sync:** MEGA → `~/MEGA/The Hive/Claude-Brain/`

### 2. State Tracker (`~/.symbiote-brain/brain-state.json`)
- **Purpose:** Fast-read JSON snapshot of current concerns
- **Current fields:**

| Field | Type | Description |
|---|---|---|
| `last_paper_review` | ISO timestamp | When papers were last read |
| `pending_actions` | string[] | 4-6 current priority actions |
| `agent_insights` | string[] | Key findings from daily paper review |
| `byte2byte_items` | number | Count of byte2byte action items |
| `tdlr_items` | number | Count of tdlr checklist items |
| `papers_reviewed` | number | Total papers processed today |
| `brains_active` | string[] | Active agent brains: hermes, codex, copilot |

### 3. MCP Configuration (`~/.hermes/config.yaml`)
- **Purpose:** Tool permissions, model fallback chain, server configs
- **Key sections:**
  - `mcp_servers.agentmail` — API key, inbox routing
  - `model.fallback` — Nous → OpenRouter → Z.ai
  - `skills.enabled` — Active skill list

### 4. MEGA Sync (`~/MEGA/The Hive/`)
- **Purpose:** Cross-machine persistence (portable SSD host + future Toxin device)
- **Cages synced:** Life-OS (public) + Claude-Brain (private)
- **NOT synced:** Business-Private (PII locked, Carnage-enforced)
- **Note:** MEGA folder still contains `grok-Brain` (legacy naming) alongside `Claude-Brain` — both map to the same local `~/.symbiote-brain/Claude-Brain/`

## Data Flow

```
Daily at 9:00 AM (cron: b591756522e9)
  ↓
morning-paper-review.sh
  → morning-paper-review.py
    ├── Reads byte2byte.md + tdlr.md
    ├── Replaces {{date}} placeholder with current date
    ├── Extracts action items + insights
    ├── Writes /tmp/agentmail-digest.json
    ├── Updates brain-state.json (Hermes — 1st brain)
    ├── Copilot: code review of Toxin project
    │   (scoped to ~/projects/symbiote-os/toxin/)
    │   (timeout: 300s, --no-auto-update)
    │   → /tmp/copilot-code-review.json
    └── Digest → AgentMail (9:00 AM)
```

## Identity Persistence Across Surfaces

| Surface | Soul Component | Sync Method |
|---|---|---|
| Venom (portable SSD host) | `brain-state.json`, `Claude-Brain/` | Local + MEGA |
| Toxin (Android) | `identity.json` (planned) | MEGA + Syncthing |
| Tails OTG | Ephemeral only | Onion relay through Tendril |
| AgentMail | `agentmail@inbox.local` | Cloud MCP |

## Naming Discrepancy: grok-Brain vs Claude-Brain

- **Local canonical:** `~/.symbiote-brain/Claude-Brain/`
- **MEGA sync folder:** `~/MEGA/The Hive/grok-Brain/` (legacy from pre-Grok-retirement config)
- **Resolution:** Both map to the same content. The orchestrator (`SYMBIOTE_HIVE_ROOT`) uses `Claude-Brain` as canonical. MEGA folder name is a cosmetic discrepancy — no functional impact.

## Soul Integrity Checks

- **Carnage audit:** `~/.symbiote-brain/.carnage_audit.log` — tracks PII leaks
- **Date staleness:** Script auto-updates `{{date}}` placeholder to prevent stale markers
- **Action drift:** `brain-state.json` pending_actions are regenerated daily — stale items should be purged when completed
- **MEGA sync health:** Verify `Claude-Brain/` and `grok-Brain/` stay in sync

## Daily Review Questions (soul-specific)

1. What identity elements changed today and why?
2. Did any preferences drift from previous sessions?
3. Are pending actions still aligned with long-term goals?
4. Did any new relationships (AgentMail threads, Substack mentions) need tracking?
