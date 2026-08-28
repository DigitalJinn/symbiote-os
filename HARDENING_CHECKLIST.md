# 🔒 Debian 13 Hardening Checklist (User Actions Required)

## System-Level (requires sudo)
- [ ] **SSH Security:**
  - Edit `/etc/ssh/sshd_config`
  - Set `PermitRootLogin no`
  - Set `PasswordAuthentication no`
  - Set `PubkeyAuthentication yes`
  - Set `AllowUsers uncannyblacc`
  - Restart: `sudo systemctl restart ssh`

- [ ] **Firewall (UFW):**
  - `sudo apt install ufw`
  - `sudo ufw default deny incoming`
  - `sudo ufw default allow outgoing`
  - `sudo ufw allow from 127.0.0.1 to any port 3030`  # orchestrator
  - `sudo ufw allow from 127.0.0.1 to any port 8080`  # llama.cpp
  - `sudo ufw allow from 127.0.0.1 to any port 5173`  # frontend
  - `sudo ufw allow from 127.0.0.1 to any port 5678`  # n8n
  - `sudo ufw allow from 127.0.0.1 to any port 8090`  # nextcloud
  - `sudo ufw deny in on eth0 to any port 3030`
  - `sudo ufw deny in on eth0 to any port 8080`
  - `sudo ufw enable`

- [ ] **Kernel Sysctls:**
  - Edit `/etc/sysctl.conf`
  - `net.ipv4.ip_forward = 0`
  - `net.ipv4.conf.all.rp_filter = 1`
  - `kernel.randomize_va_space = 2`
  - `net.ipv4.tcp_syncookies = 1`
  - Apply: `sudo sysctl -p`

- [ ] **Automatic Updates:**
  - `sudo apt install unattended-upgrades`
  - `sudo dpkg-reconfigure --priority=low unattended-upgrades`

- [ ] **Audit Logging (AIDE):**
  - `sudo apt install aide`
  - `sudo aide --init`
  - `sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db`

- [ ] **Fail2Ban:**
  - `sudo apt install fail2ban`
  - Configure jail for SSH
  - `sudo systemctl enable --now fail2ban`

## Application-Level (automated)
- [x] **Docker containers** — Resource limits applied, localhost-only bindings
- [x] **Caddy** — Security headers configured, localhost-only binding
- [x] **llama.cpp** — Host systemd service, localhost:8080 only
- [x] **Orchestrator** — localhost:3030 only, no public exposure
- [x] **Frontend** — localhost:5173 only, dev server only
- [x] **Nextcloud** — localhost:8090 only, no public access
- [x] **n8n** — localhost:5678 only, basic auth enabled
- [x] **Tor** — SOCKS proxy on localhost:9050 only
- [x] **File permissions** — .env (600), brain dir (700), project dir (read-only for others)

## Completed Hardening Measures
1. Removed stale packages (apt autoremove)
2. Docker containers resource-limited and localhost-bound
3. Caddy security headers (HSTS, X-Frame-Options, CSP, X-Content-Type-Options)
4. Filesystem permissions hardened
5. Cron access restricted
6. No cloud API keys committed to git (verified)
