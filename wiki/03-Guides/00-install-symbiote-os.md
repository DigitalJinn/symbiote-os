# Install Symbiote-OS on Venom (Debian 13 SSD)

> Phase 1–3 setup instructions

## Prerequisites
- portable SSD host (or any UEFI laptop)
- USB SSD (500GB+ recommended)
- Ventoy USB (for OS installation media)
- Internet connection

## Step 1: Install Debian 13 (trixie)
1. Boot from Debian live ISO (via Ventoy)
2. Run installer:
   - Select "Install Debian"
   - Target: your USB SSD
   - Filesystem: ext4 (encrypted LUKS recommended)
   - Desktop: Hyprland (or install separately)

## Step 2: Post-Install Setup

### Install Hyprland + Surface Support
```bash
# Surface kernel (if not already using)
sudo apt install linux-image-surface

# Hyprland + dependencies
sudo apt install hyprland swaylock swayidle waybar swaybg \
  wofi wl-copy wl-paste grim slurp dunst

# Surface-specific tools
sudo apt install iptsd libwacom-surface surface-control
```

### Clone Symbiote-OS
```bash
mkdir -p ~/projects
git clone https://github.com/MaliceHermes/symbiote-os.git
cd symbiote-os
```

### Run Install Script
**Note:** The upstream `install.sh` has known issues (see Hive Structure doc for patched version).
```bash
bash install.sh
```

Or manually:

1. **Clone repo:**
   ```bash
   git clone https://github.com/MaliceHermes/symbiote-os.git ~/projects/symbiote-os
   ```

2. **Create Hive:**
   ```bash
   mkdir -p ~/.symbiote-brain/{Life-OS,Business-Private,Claude-Brain}
   mkdir -p ~/.symbiote-brain/Claude-Brain/{00-Handoff,01-Knowledge,02-Tools}
   touch ~/.symbiote-brain/{Life-OS/Business-Private/,}BRAIN.md
   touch ~/.symbiote-brain/chats.jsonl ~/.symbiote-brain/.carnage_audit.log
   echo '{}' > ~/.symbiote-brain/brain-state.json
   chmod 700 ~/.symbiote-brain/Business-Private
   ```

3. **Create hermes user:**
   ```bash
   sudo useradd --system --shell /usr/sbin/nologin hermes
   ```

4. **Write .env:**
   ```bash
   cat > ~/projects/symbiote-os/.env <<EOF
   HERMES_USER=hermes
   HERMES_UID=$(id -u hermes)
   SYMBIOTE_HIVE_ROOT=\${HOME}/.symbiote-brain
   # ... add your API keys ...
   EOF
   chmod 600 ~/projects/symbiote-os/.env
   ```

5. **Install CLIs:**
   - Hermes: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
   - Codex: `curl -fsSL https://github.com/openai/codex/releases/latest/download/codex-installer.sh | bash`
   - Ollama: `curl -fsSL https://ollama.com/install.sh | sh`

6. **Start stack:**
   ```bash
   # Terminal 1: Orchestrator
   cd ~/projects/symbiote-os/orchestrator
   node src/index.js

   # Terminal 2: Frontend
   cd ~/projects/symbiote-os/frontend
   npm run dev
   ```

The frontend will be at `http://localhost:5173`, orchestrator at `http://localhost:3030`.
