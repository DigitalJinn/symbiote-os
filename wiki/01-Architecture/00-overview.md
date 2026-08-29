# Symbiote-OS — Architecture Overview

## Core Concept
Symbiote-OS is a portable, privacy-first agentic operating system that runs from a USB SSD ("Venom") and can securely sync across three domains via Tor:

```
┌─────────────────────────────┐
│   portable SSD host (Eddie)     │
│  ┌───────────────────────┐  │
│  │ Venom (SSD)           │  │  Debian 13 + Hyprland
│  │ • Orchestrator :3030  │  │  Hermes, Codex, Ollama
│  │ • The Hive (3 cages)  │  │  Carnage, Tendril
│  │ • Carnage ACL         │  │
│  └───────────────────────┘  │
│        ↓                     │
│   Tor .onion:3030           │
└─────────────┬───────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───▼──────────┐   ┌─────▼──────────┐
│ OTG Tails    │   │  Toxin Phone   │
│ (jump-box)   │   │  (Android)     │
│ USB-C OTG    │   │  Prototype NOW │
│ Amnesic      │   │  Real device   │
│ Tendril      │   │  when acquired │
└──────────────┘   └────────────────┘
```

## Components

### Venom (SSD Brain)
- Debian 13 + Hyprland on portable USB SSD
- Hosts the Hive, Orchestrator, and CLIs
- Ephemeral — the SSD is the "brain" you carry

### Eddie (Host Body)
- Temporary machine (portable SSD host) used to boot Venom
- Leaves no persistent traces after shutdown

### The Hive (Vault)
- Three-cage structure: `Life-OS` / `Business-Private` / `Claude-Brain`
- Synced via MEGA to `~/MEGA/The Hive/`
- `Business-Private` is ACL-locked (mode 700, hermes user blocked)

### Carnage (ACL)
- OS-level access control: hermes system user (uid 996)
- PII redaction + audit logging
- Logs to `.carnage_audit.log`

### Phage (LLM Layer)
| Local: Ollama (hermes3:8b, qwen2.5-coder:1.5b, phi4-mini, llama3.2:3b) |
| Cloud: OpenAI (GPT-4o), Nous Research (poolside/laguna-s-2.1:free) |
| Codex + Copilot dual-brain (Grok retired) |

### Tendril (Tor Integration)
- Tor hidden service routing Venom ↔ Tails ↔ Toxin
- Onion address: `7oshsadnhldnwmtlw2xyelie4tl2apngpr45rd53ms5xa4kclnof24id.onion`
- SOCKS proxy: localhost:9050

### Toxin (Android Prototype)
- Android app scaffold in `~/projects/symbiote-os/toxin/`
- Designed for microG (not full GApps) for Google app support
- Syncthing sync with desktop Hive
