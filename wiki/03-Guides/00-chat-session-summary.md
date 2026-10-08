# SymbioteOS Chat Session Summary

This document captures the final decisions and architecture agreed on during the current planning session for the SymbioteOS project.

## Final Decision Summary

- Keep the existing repository: `MaliceHermes/symbiote-os`
- Do not create a new repository
- Use a `dev` branch for active work and merge to `main` only after testing
- Use Nextcloud Hub as the primary self-hosted work hub
- Keep AppFlowy, AFFiNE, and Open Notebook in the stack
- Use local Ollama + Jan for private AI tasks
- Use GitHub Copilot as the main coding assistant
- Keep Claude Personal at $17/month if desired, but do not pay for Claude API unless there is a specific workflow that needs it
- Use AgentMail and ProtonMail as separate communication channels
- Use Nextcloud Passwords as the primary local password manager, with Proton Pass as a secondary backup option
- Keep Syncthing for file sync where useful

## Final Stack

### Core hub
- Nextcloud Hub
  - Files
  - Office via Collabora
  - Calendar
  - Contacts
  - Tasks
  - Passwords
  - Music
  - Photos
  - Flow automation

### Workspace tools
- AppFlowy
  - project management and personal task workflows
- AFFiNE
  - visual workspace and real-time collaborative planning
- Open Notebook
  - notebook-based school or study work

### Automation and AI
- n8n
  - workflow automation between cloud, files, and tasks
- Ollama
  - local inference runtime for DeepSeek-Coder and Phi models
- Jan
  - local UI for local LLM chat
- GitHub Copilot
  - coding assistant in VS Code / Cursor
- Optional: Composio
  - tool integrations and LLM tool use

### Communication and identity
- AgentMail
  - agent-facing / operational email
- ProtonMail
  - personal email inbox
- Proton Pass
  - backup / secondary password manager

## Why This Stack

This stack balances three goals:

1. Local-first privacy
2. Self-hosted practicality
3. Reasonable subscription cost

The final stack avoids overcomplicating the project with too many overlapping services. Nextcloud is the central hub, while the other tools remain specialized and do not duplicate the same function in a redundant way.

## Budget Reality

Recommended monthly spend:

- Claude Personal: $17/month (optional but useful)
- GitHub Copilot: free or paid depending on status
- Everything else: self-hosted and free

This keeps the system practical and not dependent on expensive premium AI subscriptions while still allowing strong coding and reasoning support.

## Recommended Branch Strategy

Use a clean branch model:

```
main
└── dev
    └── feature/*
```

### Recommended use
- `main`: tested, stable production branch
- `dev`: active development branch for the next stack iteration
- `feature/*`: experimental features or isolated work items

## Recommended Repo Workflow

1. Create `dev` from `main`
2. Update the stack in `dev`
3. Test locally with Docker Compose
4. Validate the services and apps
5. Merge `dev` to `main`
6. Keep `dev` alive for the next cycle

## Final Docker Stack

The working stack includes:

- Caddy
- Nextcloud
- MariaDB
- Redis
- Collabora
- AppFlowy
- AFFiNE
- n8n
- Ollama
- Tor

A corrected Compose file should keep the `networks:` block at the top level, not nested inside a service.

## `.env` Model

Use a local `.env` file with values such as:

```bash
MYSQL_ROOT_PASSWORD=your-secure-root-password-here
MYSQL_PASSWORD=your-secure-nextcloud-db-password-here
NEXTCLOUD_ADMIN_USER=admin
NEXTCLOUD_ADMIN_PASSWORD=your-secure-admin-password-here
AFFINE_DB_PASSWORD=your-secure-affine-db-password-here
N8N_BASIC_AUTH_PASSWORD=your-secure-n8n-password-here
```

Do not commit `.env` to the repo.

## First-Run Verification Checklist

After deploying locally:

```bash
docker-compose up -d
docker-compose ps
curl -I http://localhost:8090
curl -I http://localhost:8000
curl -I http://localhost:3010
curl -I http://localhost:5678
curl -I http://localhost:11434
```

Then install the Nextcloud apps:

```bash
docker exec symbiote-nextcloud occ app:install office
docker exec symbiote-nextcloud occ app:install calendar
docker exec symbiote-nextcloud occ app:install contacts
docker exec symbiote-nextcloud occ app:install tasks
docker exec symbiote-nextcloud occ app:install notes
docker exec symbiote-nextcloud occ app:install music
docker exec symbiote-nextcloud occ app:install photos
docker exec symbiote-nextcloud occ app:install passwords
docker exec symbiote-nextcloud occ app:install flow
```

Then pull local models:

```bash
docker exec symbiote-ollama ollama pull deepseek-coder:6.7b
docker exec symbiote-ollama ollama pull phi3.5
```

## Merge Plan

After validation on `dev`:

```bash
git checkout main
git merge dev
```

Optional:

```bash
git tag -a v2.0.0 -m "SymbioteOS 2026 Production Stack"
git push origin main --tags
```

## Key Takeaways

- Keep the repo as a single project
- Use dev → main workflow
- Use Nextcloud as the central hub
- Keep local AI running privately via Ollama
- Use Copilot as the practical coding layer
- Keep the stack budget-conscious and maintainable
- Avoid overcomplicating the repo with redundant services

## Final Position

The final architecture is not a total replacement of all tools. Instead, it is a layered setup:

- Nextcloud for shared data and host-level convenience
- AppFlowy and AFFiNE for structured workflow and visual planning
- Obsidian for personal knowledge management
- Open Notebook for school and notebooks
- Local AI for privacy-sensitive tasks
- Copilot for coding support
- AgentMail + ProtonMail for communication separation

This is the version of SymbioteOS that best fits the current planning decisions and budget constraints.
