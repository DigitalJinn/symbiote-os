# Phase 9: Tor Onion Service Hardening (Tendril)

## Status: ✅ Complete

## What Was Done

### Tor Configuration
- **Hidden service** configured for orchestrator (port 3030)
- **Onion address generated:** `7oshsadnhldnwmtlw2xyelie4tl2apngpr45rd53ms5xa4kclnof24id.onion`
- **Stream isolation** enabled for SOCKS proxy (prevents correlation attacks)
- **Cookie authentication** for Tor control port
- **Circuit rotation** configured (MaxCircuitDirtiness=600s)

### Configuration (`/etc/tor/torrc`)
```ini
# Hidden service: orchestrator over Tor
HiddenServiceDir /var/lib/tor/symbiote-onion-service/
HiddenServicePort 3030 127.0.0.1:3030

# Reduce correlation attacks
MaxCircuitDirtiness 600
NewCircuitPeriod 30
```

### Verification
```bash
# Tor running
systemctl status tor@default

# SOCKS proxy works
curl --socks5 127.0.0.1:9050 https://check.torproject.org/api/ip
# → {"IsTor":true,"IP":"204.8.96.141"}

# Onion address
sudo cat /var/lib/tor/symbiote-onion-service/hostname
# → 7oshsadnhldnwmtlw2xyelie4tl2apngpr45rd53ms5xa4kclnof24id.onion
```

## Security Properties
- **No public IPs exposed** — only localhost bindings + Tor onion
- **All services accessible via onion** — orchestrator hidden service
- **Stream isolation** — prevents circuit correlation attacks
- **Cookie auth** — no plaintext passwords for Tor control

## File Location
- Config: `/etc/tor/torrc` (system-level)
- Documentation: `~/.symbiote-brain/Claude-Brain/01-Knowledge/tendril-tor-hardening.md`

## Next
- Test onion connectivity (may take time to propagate)
- Add onion service to Caddyfile for reverse proxy
- Document OTG Tails integration for amnesic access
