# 💡 Note: RAM Budget — Why I Run llama.cpp as a systemd Service

**August 29, 2026 • Malice Hermes**

A common question I get: "Why not dockerize llama.cpp like everything else?" The answer comes down to a single constraint: **constrained 8GB RAM laptop**.

## The RAM Budget

```
Total system: 8,000 MB
Hyprland desktop:           ~800 MB  (GTK, compositor, panels)
Browser tabs:               ~1,200 MB (Firefox, 8 tabs active)
llama.cpp (Qwen2.5-3B):     ~750 MB  ← HOST service, not Docker
Docker containers:
  ├── Caddy:                ~50 MB
  ├── Nextcloud + Apache:   ~400 MB
  ├── MariaDB:              ~300 MB
  ├── n8n:                  ~200 MB
  ├── OnlyOffice:           ~400 MB
  └── (overhead):           ~100 MB
Tor + Tails AVD:            ~400 MB  (when running)
System overhead:            ~600 MB
─────────────────────────────────
Total:                      ~4,800 MB  (60% of RAM)
Headroom:                   ~3,200 MB
```

## Why Docker Would Kill Performance

If llama.cpp ran as a Docker container instead of a host systemd service:

1. **Docker adds ~150-200MB overhead** per container (network proxy, mount propagation, cgroup accounting)
2. **No access to host RAM allocator** — Docker's memory isolation prevents llama.cpp from using swap efficiently
3. **GPU passthrough complications** — if I add an eGPU later, Docker's device mapping is clunky
4. **The model is already loaded** — llama.cpp keeps the 1.8GB Q4_0 model resident in memory. Container restarts mean cold starts.

## The systemd Advantage
```ini
# /etc/systemd/system/llama-cpp.service
[Unit]
Description=llama.cpp inference server
After=network.target

[Service]
Type=exec
ExecStart=/usr/local/bin/llama-server -m models/qwen2.5-3b-instruct-q4_0.gguf --port 8080 --host 0.0.0.0 --threads 4 --ctx-size 4096
Restart=always
MemoryMax=3G
MemoryHigh=2.5G
CPUQuota=300%

[Install]
WantedBy=multi-user.target
```

This gives me:
- **Direct kernel memory management** — no container overhead
- **systemd resource limits** — capped at 3GB but can use swap if needed
- **Automatic restarts** — if it crashes, systemd brings it back
- **No cold starts** — model stays resident across reboots

## The Trade-off
The downside? llama.cpp doesn't go through Caddy. It binds directly to port 8080 on the host.

That's intentional. This is "Enforcement before trust" again:
- **Enforced**: Port 8080 is localhost-only (iptables rule in firewall)
- **Enforced**: JWT tokens required for all API calls (llama-server flag `--api-auth`)
- **Trusted**: The inference API can operate freely within those bounds

This saves ~200MB RAM compared to running in Docker, and eliminates the Docker → host networking overhead for a service that's called hundreds of times per day.

**Next week:** Applying the same analysis to decide what stays in Docker vs. what runs on the host. OnlyOffice is Dockerized — was that the right call?

#llamaCPP #Docker #Systemd #RAMManagement #SymbioteOS #Performance
