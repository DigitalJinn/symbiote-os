#!/bin/bash
# Symbiote-OS startup for Venom (Debian 13 + Surface Pro 4)
# Venom Revamp: Docker stack + llama.cpp systemd service
# Note: Docker Compose v2 plugin not available; using individual docker run commands

set -e
cd "$(dirname "$0")"

echo "========================================="
echo "  SYMBIOTE-OS  —  Venom (portable brain)"
echo "========================================="
echo

# Load environment
if [ ! -f .env ]; then
  echo "[error] .env file not found. Run install.sh first."
  exit 1
fi

source .env

# 1. Ensure llama.cpp is running (systemd service on host)
if ! curl -sf http://localhost:8080/health > /dev/null 2>&1; then
  echo "[startup] starting llama.cpp systemd service..."
  sudo systemctl start llama-cpp
  sleep 3
  if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
    echo "[startup] llama.cpp healthy on :8080"
  else
    echo "[error] llama.cpp failed to start"
    exit 1
  fi
fi

# 2. Ensure Tor is running (for Tendril)
if ! pgrep -x "tor" > /dev/null; then
  echo "[startup] starting Tor..."
  sudo systemctl start tor
  sleep 2
fi

# 3. Create Docker network if it doesn't exist
if ! docker network ls | grep -q symbiote_net; then
  echo "[startup] creating Docker network symbiote_net..."
  docker network create symbiote_net
fi

# 4. Start containers (only if not already running)
# MariaDB
if ! docker ps --format "{{.Names}}" | grep -q "^nextcloud_db$"; then
  echo "[startup] starting MariaDB..."
  docker run -d \
    --name nextcloud_db \
    --network symbiote_net \
    -e MYSQL_ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD}" \
    -e MYSQL_PASSWORD="${MYSQL_PASSWORD}" \
    -e MYSQL_DATABASE="${MYSQL_DATABASE}" \
    -e MYSQL_USER="${MYSQL_USER}" \
    -v ./config/nextcloud_db/mysql:/var/lib/mysql \
    --restart unless-stopped \
    mariadb:11 --transaction-isolation=READ-COMMITTED --binlog-format=ROW --innodb-file-format=Barracuda
  sleep 10
fi

# Nextcloud
if ! docker ps --format "{{.Names}}" | grep -q "^nextcloud$"; then
  echo "[startup] starting Nextcloud..."
  docker run -d \
    --name nextcloud \
    --network symbiote_net \
    -p 127.0.0.1:8090:80 \
    -e MYSQL_HOST=nextcloud_db \
    -e MYSQL_DATABASE="${MYSQL_DATABASE}" \
    -e MYSQL_USER="${MYSQL_USER}" \
    -e MYSQL_PASSWORD="${MYSQL_PASSWORD}" \
    -e TRUSTED_DOMAINS="localhost 127.0.0.1" \
    -v ./config/nextcloud_data:/var/www/html \
    --restart unless-stopped \
    nextcloud:28-apache
  sleep 10
fi

# n8n
if ! docker ps --format "{{.Names}}" | grep -q "^n8n$"; then
  echo "[startup] starting n8n..."
  docker run -d \
    --name n8n \
    --network symbiote_net \
    -p 127.0.0.1:5678:5678 \
    -e N8N_HOST=localhost \
    -e N8N_PORT=5678 \
    -e N8N_BASIC_AUTH_ACTIVE=true \
    -e N8N_BASIC_AUTH_USER=admin \
    -e N8N_BASIC_AUTH_PASSWORD="${N8N_BASIC_AUTH_PASSWORD}" \
    -e WEBHOOK_URL=http://localhost:5678 \
    -e DB_TYPE=sqlite \
    -e EXECUTIONS_PROCESS=main \
    -v ./config/n8n_data:/home/node/.n8n \
    --restart unless-stopped \
    n8nio/n8n:latest
  sleep 5
fi

# Caddy
if ! docker ps --format "{{.Names}}" | grep -q "^caddy$"; then
  echo "[startup] starting Caddy..."
  docker run -d \
    --name caddy \
    --network symbiote_net \
    -p 127.0.0.1:80:80 \
    -p 127.0.0.1:443:443 \
    -v ./config/caddy/Caddyfile:/etc/caddy/Caddyfile \
    -v ./config/caddy_data:/data \
    -v ./config/caddy_config:/config \
    --restart unless-stopped \
    caddy:2-alpine caddy run --config /etc/caddy/Caddyfile
fi

# 5. Start Orchestrator (:3030)
if ! curl -sf http://localhost:3030/api/health > /dev/null 2>&1; then
  echo "[startup] starting orchestrator..."
  cd orchestrator
  npm install --silent 2>/dev/null || true
  node src/index.js > /tmp/orchestrator.log 2>&1 &
  ORCH_PID=$!
  cd ..
  sleep 2
else
  echo "[startup] orchestrator already running"
fi

# 6. Set up file discovery cron (if not already installed)
( crontab -l 2>/dev/null | grep -v "files:scan.*Workspace" ; echo "0 * * * * docker exec -u www-data nextcloud php occ files:scan --path=\"nextcloud/files/Workspace\" 2>/dev/null" ) | crontab -

# 7. Open browser
echo "[startup] opening dashboard..."
xdg-open http://localhost:5173 2>/dev/null || \
  echo "Open http://localhost:5173 in your browser manually"

echo
echo "Symbiote-OS running:"
echo "  • Orchestrator:   http://localhost:3030"
echo "  • Frontend:       http://localhost:5173"
echo "  • Caddy (proxy):  http://localhost:80"
echo "  • n8n:            http://localhost:5678 (admin/${N8N_BASIC_AUTH_PASSWORD})"
echo "  • Nextcloud:      http://localhost:8090"
echo "  • llama.cpp:      http://localhost:8080/v1 (host systemd service)"
echo "  • Tor SOCKS:      localhost:9050"
echo
echo "Logs:"
echo "  • tail -f /tmp/orchestrator.log"
echo "  • docker logs -f n8n"
echo "  • docker logs -f nextcloud"
echo
echo "Press Ctrl+C to stop the orchestrator (Docker containers keep running)."
echo

wait $ORCH_PID 2>/dev/null
