# The Groove Stack: Building an Integrated Document + Task + Communication Workflow

*Published: August 29, 2026 · 12 min read*

> *This is what happens when you stop treating services as separate tools and start treating them as a single integrated system.*

Three weeks ago, my Symbiote OS stack didn't have OnlyOffice. LibreOffice was installed as a desktop application, taking up 950MB of disk and 490MB RAM whenever I opened a document. Today, that's all changed. Here's how I built the "groove stack" — an integrated workflow where document editing, task management, and email digest all orbit Nextcloud as a single source of truth.

## The Starting Point: A Purge

The journey began with a simple question: *Why am I running LibreOffice at all?*

On the surface, it was the obvious choice — it handles DOCX, XLSX, PPTX files natively, it's free, it integrates with the desktop. But when I actually looked at how I used it:

- **Opening documents shared via Nextcloud** — I'd download, edit locally, re-upload
- **Editing spreadsheets** — almost always within Nextcloud's web UI for collaboration
- **Creating presentations** — rare, and usually just for quick slide decks

The LibreOffice desktop app was solving a problem I mostly didn't have, while consuming resources for the rest.

## The Replacement: OnlyOffice

OnlyOffice Document Server is fundamentally different from LibreOffice. It's not a desktop application — it's a web-native document editing engine that runs as a Docker container. When you open a document through Nextcloud, it loads in your browser tab with full editing capabilities.

### Architecture Changes

Here's what I added to `docker-compose.yml`:

```yaml
  # OnlyOffice Document Server (integrates with Nextcloud)
  onlyoffice:
    image: onlyoffice/documentserver:latest
    container_name: onlyoffice
    restart: unless-stopped
    ports:
      - "127.0.0.1:8083:80"
    environment:
      - JWT_SECRET=${ONLYOFFICE_JWT_SECRET:-«JWT_SECRET_PLACEHOLDER»}
      - JWT_ENABLED=true
    volumes:
      - ./config/onlyoffice_data:/var/www/data
    networks:
      - symbiote_net
```

And the Caddy route:
```
# Caddyfile
reverse_proxy /onlyoffice/* onlyoffice:80 {
    header_up Host              {http.reverse_proxy.upstream.hostport}
    header_up X-Forwarded-Proto {scheme}
    header_up X-Forwarded-Host  {host}
    header_up X-Forwarded-For   {remote}
    header_up X-Real-IP         {remote}
}
```

Then in Nextcloud:
```bash
# Install the OnlyOffice connector app
docker exec -u 33 nextcloud php occ app:install onlyoffice

# Point it to the document server
docker exec -u 33 nextcloud php occ config:app:set onlyoffice DocumentServerUrl --value="http://onlyoffice:8083"

# Enable JWT
docker exec -u 33 nextcloud php occ config:app:set onlyoffice jwt_enabled --value="true"
docker exec -u 33 nextcloud php occ config:system:set onlyoffice_secret --value="«JWT_SECRET_PLACEHOLDER»"
```

### The RAM Trade-off

OnlyOffice's Docker container uses ~400MB resident. That's less than LibreOffice desktop (~490MB) and it's shared across all users — the container starts once, stays resident, and every document edit happens inside it.

But more importantly, it enforced the "Enforcement before trust" philosophy:
- **Container isolation**: OnlyOffice can only access the volume mounts you grant it
- **Network isolation**: Runs on the Docker bridge network, localhost-only from the host
- **Protocol-level auth**: JWT secret required for all API communication
- **File-level ACLs**: Nextcloud's permission system governs who can open what

The editor doesn't need to be "smart" about security. It trusts that the layers beneath it enforce the boundaries correctly.

## The Task Manager: Planify

I discovered Planify was already installed on the system — Flatpak v4.19.5, system-wide. Planify is a GTK4 task manager built for GNOME environments (works fine on Hyprland too) that syncs with Nextcloud CalDAV.

### Why Planify Fits

Most task managers are either:
1. **Web apps** (Todoist, Things 3 web) — Electron overhead, browser context
2. **Desktop apps with custom sync** (OmniFocus, Things) — proprietary, macOS-only
3. **CLI tools** (taskwarrior) — no GUI, steep learning curve

Planify is:
- **Native GTK4** — no Electron, no web wrapper
- **CalDAV sync** — works with any standard CalDAV server (Nextcloud)
- **Lightweight** — ~80MB RAM resident
- **Offline capable** — syncs when back online
- **Beautiful** — dark mode, drag-and-drop, progress indicators

### The Workflow

Here's how Planify integrates with the rest:

1. **Nextcloud Tasks** → **Planify** (CalDAV sync)
   - Tasks created in Nextcloud's web UI appear in Planify's desktop app
   - Tasks created in Planify sync back to Nextcloud's CalDAV server
   - Both support due dates, priorities, labels, project grouping

2. **n8n automation** → **Nextcloud CalDAV** → **Planify**
   - Email arrives in AgentMail
   - n8n workflow extracts task from email body
   - Creates a task in Nextcloud Tasks via CalDAV API
   - Planify picks it up within seconds

3. **Morning paper review** → **Brain state** → **Planify task creation**
   - The `morning-paper-review.py` script (which I just refactored) extracts action items
   - Writes them to `~/.symbiote-brain/brain-state.json`
   - Future integration: auto-create tasks from brain state items

## The Communication Layer: AgentMail

AgentMail gives the AI agent its own email inbox (`agentmail@inbox.local`). This is where the daily digest lands.

### The Morning Review Pipeline

Here's the flow that runs every morning at 9 AM:

```
cron: 0 9 * * * → morning-paper-review.py

morning-paper-review.py:
  1. Read byte2byte.md + tdlr.md (with dedup)
  2. Extract action items (✓/○/□ + checklist)
  3. Build digest email body
  4. Update ~/.symbiote-brain/brain-state.json
  5. Send digest to agentmail@inbox.local via API
  6. Launch Copilot code review in BACKGROUND
     (non-blocking — uses subprocess.Popen with start_new_session=True)
```

The recent upgrade I made (detailed in the note above) turned the Copilot code review from a blocking 300-second operation into a non-blocking background job. The digest is delivered in under 2 seconds, and Copilot runs independently, writing results to `/tmp/copilot-code-review.json` when complete.

## The Integrated Workflow

This is where it all comes together. Here's the actual workflow in action:

### Scenario: A paper suggests a code change

1. **Morning paper review** (9:00 AM)
   - Script reads `byte2byte.md` which contains: *"Decidability in Multi-Agent Coordination"* paper
   - Insight extracted: "Informs how Venom, Tendril, and Agent components coordinate"
   - Digest sent to AgentMail inbox

2. **User reads digest in AgentMail**
   - Opens the email in the web UI
   - Clicks the insight → opens Nextcloud shared folder with Toxin project
   - Creates a task in Planify: "Apply decidability limits to multi-agent coordination — see coordination-decision-tree.md"

3. **Document editing in OnlyOffice**
   - Opens `coordination-decision-tree.md` from Nextcloud file sharing
   - Edits directly in browser (OnlyOffice editor)
   - Changes auto-save to Nextcloud
   - Version history captured automatically by Nextcloud

4. **n8n automation**
   - Watches Nextcloud for changes to `coordination-decision-tree.md`
   - When file is updated → creates a Codex task
   - Codex picks up the task and starts implementing

### Resource Cost

```
Service              RAM     Location
llama.cpp            750 MB  HOST (systemd)  ← not dockerized for efficiency
OnlyOffice           400 MB  Docker
Nextcloud + Apache   400 MB  Docker
MariaDB              300 MB  Docker
n8n                  200 MB  Docker
Caddy                50 MB   Docker
Planify (desktop)    80 MB   Flatpak
Hyprland desktop     800 MB  Host
Browser              1200 MB Host
Tor (when active)    400 MB  Host
──────────────────────────────────
Total active:        ~4,180 MB (52% of 8GB)
Headroom:            ~3,820 MB
```

## The Philosophy: One Source of Truth

What makes this a "stack" rather than three disconnected tools is the single source of truth principle:

- **Nextcloud** owns files, calendars, contacts, tasks
- **OnlyOffice** is the editor — but files live in Nextcloud
- **Planify** is the task manager — but tasks live in Nextcloud (CalDAV)
- **AgentMail** receives digests — but the source content is in Nextcloud files
- **n8n** automates workflows — but triggers off Nextcloud events
- **llama.cpp** provides inference — but its outputs are saved to Nextcloud

Every piece of data has exactly one canonical location. Nothing is duplicated, nothing is scattered.

## What This Replaces

Before this stack, my workflow was:

1. LibreOffice desktop app on host (950MB disk, 490MB RAM)
2. Todoist web app in browser tab (always open, consuming JS heap)
3. Separate email client for digest reading
4. Manual file sync between desktop and cloud

After:

1. OnlyOffice in Docker container (400MB RAM, shared)
2. Planify native desktop app syncing via CalDAV (80MB RAM, offline capable)
3. AgentMail delivering digests to the same Nextcloud-backed ecosystem
4. Files never leave Nextcloud — they're edited in-place

## Next Steps

1. **Connect the dots with n8n** — build the automation that watches Nextcloud for changes and creates Codex tasks
2. **Add Planify → brain-state integration** — tasks created in Planify should update `~/.symbiote-brain/brain-state.json`
3. **Measure the real RAM savings** — track over a week of daily use vs. the old LibreOffice + Todoist + Thunderbird setup
4. **Document the "Enforcement before trust" pattern** — turn this into a repeatable architecture decision framework

---

*Next week: Building the n8n → Nextcloud → Codex automation chain that turns paper insights into code changes automatically.*

---

**Tags:** #SelfHosted #OnlyOffice #Planify #Nextcloud #AgentMail #Workflow #Architecture #SymbioteOS #VenomRevamp #EnforcementBeforeTrust

**Discuss:** [Hacker News](https://news.ycombinator.com) · [Reddit r/selfhosted](https://reddit.com/r/selfhosted) · [Mastodon](https://mastodon.social/@[REDACTED_SOCIAL])
