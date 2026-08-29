#!/bin/bash
# Symbiote-OS Installation Script
# Automated setup for Venom, Tendril, Toxin on Debian 13 + portable SSD host

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "========================================"
echo "  SYMBIOTE-OS  —  Installation Script"
echo "========================================"
echo -e "${NC}"

# Check if running on Debian/Linux
if ! command -v apt &> /dev/null; then
  echo -e "${RED}[ERROR] This script requires Debian/Linux with apt${NC}"
  echo "See SYMBIOTE_BUILD_VENOM_SURFACE_PRO4.md for manual installation"
  exit 1
fi

# Get current user
CURRENT_USER=$(whoami)
if [ "$CURRENT_USER" = "root" ]; then
  echo -e "${RED}[ERROR] Do not run this script as root${NC}"
  echo "Run as your regular user (with sudo privileges)"
  exit 1
fi

echo -e "${GREEN}[info]${NC} Installing as user: $CURRENT_USER"
echo

# ============================================
# Step 1: Check Prerequisites
# ============================================
echo -e "${BLUE}[Step 1/7]${NC} Checking prerequisites..."

commands=("git" "node" "npm" "python3" "curl" "sudo")
for cmd in "${commands[@]}"; do
  if ! command -v $cmd &> /dev/null; then
    echo -e "${YELLOW}[warn]${NC} $cmd not found. Installing..."
    sudo apt update && sudo apt install -y $cmd || true
  fi
done

echo -e "${GREEN}[ok]${NC} Prerequisites checked"
echo

# ============================================
# Step 2: Create Directory Structure
# ============================================
echo -e "${BLUE}[Step 2/7]${NC} Creating directory structure..."

mkdir -p ~/.symbiote-brain/{Life-OS,Business-Private,Claude-Brain}
mkdir -p ~/.symbiote-brain/Claude-Brain/{00-Handoff,01-Knowledge,02-Tools}
mkdir -p ~/.symbiote-brain/Claude-Brain/00-Handoff/{incoming-briefs,outgoing-results}
mkdir -p ~/projects/symbiote-os/{orchestrator,frontend,tendril,toxin}

echo -e "${GREEN}[ok]${NC} Directories created:"
echo "  • ~/.symbiote-brain/ (The Hive - 3 cages)"
echo "  • ~/projects/symbiote-os/ (Project root)"
echo

# ============================================
# Step 3: Initialize Hive (Vault Structure)
# ============================================
echo -e "${BLUE}[Step 3/7]${NC} Initializing The Hive (vault structure)..."

# Create BRAIN.md files
touch ~/.symbiote-brain/Life-OS/BRAIN.md
touch ~/.symbiote-brain/Business-Private/BRAIN.md
touch ~/.symbiote-brain/Claude-Brain/BRAIN.md

# Create logs
touch ~/.symbiote-brain/chats.jsonl
touch ~/.symbiote-brain/.carnage_audit.log
echo '{}' > ~/.symbiote-brain/brain-state.json

echo -e "${GREEN}[ok]${NC} The Hive initialized:"
echo "  • Life-OS/ (OPEN - publishable content)"
echo "  • Business-Private/ (LOCKED - personal data)"
echo "  • Claude-Brain/ (infrastructure & handoffs)"
echo

# ============================================
# Step 4: Set Up Carnage ACL (Access Control)
# ============================================
echo -e "${BLUE}[Step 4/7]${NC} Setting up Carnage ACL (access control)..."

# Lock Business-Private
sudo chmod 700 ~/.symbiote-brain/Business-Private
sudo chown $CURRENT_USER:$CURRENT_USER ~/.symbiote-brain/Business-Private

echo -e "${GREEN}[ok]${NC} Carnage ACL enforced:"
echo "  • Business-Private locked (mode 700)"
echo "  • Low-privilege Hermes user cannot read"
echo

# ============================================
# Step 5: Create Environment Files
# ============================================
echo -e "${BLUE}[Step 5/7]${NC} Creating environment configuration..."

cd "$(dirname "$0")"

# Create root .env
cat > .env << 'EOF'
# Symbiote-OS Environment
# DO NOT COMMIT TO GIT

# Orchestrator
ORCHESTRATOR_PORT=3030
ORCHESTRATOR_HOST=localhost

# Paths
SYMBIOTE_HIVE_ROOT=~/.symbiote-brain
JARVIS_PROJECTS_ROOT=~/projects

# API Keys (get from respective services)
OPENAI_API_KEY=sk-your-key-here
XAI_API_KEY=xai-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Hermes (low-privilege user ID)
# Run: id hermes (to get the actual UID)
HERMES_UID=1001

# Logging
LOG_LEVEL=debug
LOG_DIR=./logs

# Vite (Frontend)
VITE_ORCHESTRATOR_URL=http://localhost:3030
EOF

echo -e "${GREEN}[ok]${NC} Environment file created: .env"
echo -e "${YELLOW}[warn]${NC} IMPORTANT: Edit .env and add your API keys:"
echo "  • OPENAI_API_KEY (from OpenAI)"
echo "  • XAI_API_KEY (from xAI/Grok)"
echo

# ============================================
# Step 6: Install Node.js Dependencies
# ============================================
echo -e "${BLUE}[Step 6/7]${NC} Installing Node.js dependencies..."

echo -e "${YELLOW}[...]${NC} Installing orchestrator dependencies"
cd orchestrator
npm install --silent > /dev/null 2>&1 || npm install
cd ..

echo -e "${YELLOW}[...]${NC} Installing frontend dependencies"
cd frontend
npm install --silent > /dev/null 2>&1 || npm install
cd ..

echo -e "${YELLOW}[...]${NC} Installing tendril dependencies"
cd tendril
npm install --silent > /dev/null 2>&1 || npm install
cd ..

echo -e "${GREEN}[ok]${NC} Node.js dependencies installed"
echo

# ============================================
# Step 7: Verify Installation
# ============================================
echo -e "${BLUE}[Step 7/7]${NC} Verifying installation..."

echo -e "${YELLOW}[check]${NC} Checking Hermes"
if command -v hermes &> /dev/null; then
  echo -e "${GREEN}  ✓ Hermes found${NC}"
else
  echo -e "${YELLOW}  ✗ Hermes NOT installed (expected, install separately)${NC}"
fi

echo -e "${YELLOW}[check]${NC} Checking Ollama"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
  echo -e "${GREEN}  ✓ Ollama running on :11434${NC}"
else
  echo -e "${YELLOW}  ✗ Ollama NOT running (start with: sudo systemctl start ollama)${NC}"
fi

echo -e "${YELLOW}[check]${NC} Checking Node.js"
node_version=$(node --version)
echo -e "${GREEN}  ✓ Node.js $node_version${NC}"

echo -e "${YELLOW}[check]${NC} Checking directories"
if [ -d "$HOME/.symbiote-brain" ]; then
  echo -e "${GREEN}  ✓ The Hive initialized at ~/.symbiote-brain${NC}"
else
  echo -e "${RED}  ✗ The Hive not found${NC}"
  exit 1
fi

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo

echo -e "${BLUE}Next Steps:${NC}"
echo
echo "1. ${YELLOW}Edit .env and add API keys:${NC}"
echo "   nano .env"
echo "   - OPENAI_API_KEY=sk-..."
echo "   - XAI_API_KEY=xai-..."
echo
echo "2. ${YELLOW}Start Ollama (if not running):${NC}"
echo "   sudo systemctl start ollama"
echo "   # Wait for startup, then verify:"
echo "   curl http://localhost:11434/api/tags"
echo
echo "3. ${YELLOW}Start Symbiote-OS:${NC}"
echo "   bash start.sh"
echo "   # Opens dashboard at http://localhost:5173"
echo
echo "4. ${YELLOW}Install Hermes, Codex, Grok CLI:${NC}"
echo "   # Follow SYMBIOTE_BUILD_VENOM_SURFACE_PRO4.md"
echo
echo "5. ${YELLOW}For Tendril (OTG Tails jump-box):${NC}"
echo "   # Follow SYMBIOTE_TENDRIL_TOXIN_INTEGRATION.md"
echo
echo "6. ${YELLOW}For Toxin (Android prototype):${NC}"
echo "   # Open Android Studio, load toxin/ directory"
echo
echo "For detailed guides, see:"
echo "  • ${BLUE}SYMBIOTE_BUILD_VENOM_SURFACE_PRO4.md${NC}"
echo "  • ${BLUE}SYMBIOTE_ORCHESTRATOR_BOOTSTRAP_REVISED.md${NC}"
echo "  • ${BLUE}SYMBIOTE_TENDRIL_TOXIN_INTEGRATION.md${NC}"
echo
echo -e "${GREEN}Symbiote-OS is ready to build!${NC}"
echo
