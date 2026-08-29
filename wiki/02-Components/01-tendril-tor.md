# Tendril — Tor Integration

> Phase 5 — Secure Tor onion service + Tails OTG jump-box

## Status: Prepared

### Components
1. **Tor hidden service** (on Venom desktop)
2. **Tails USB** (OTG jump-box)

## Tor Hidden Service

### Configuration
- **Onion address:** `7oshsadnhldnwmtlw2xyelie4tl2apngpr45rd53ms5xa4kclnof24id.onion`
- **Service port:** `3030` → `127.0.0.1:3030` (orchestrator)
- **SOCKS proxy:** `localhost:9050`
- **Control port:** `localhost:9051`

### Config File (`/etc/tor/torrc`)
```
HiddenServiceDir /var/lib/tor/symbiote-onion-service/
HiddenServicePort 3030 127.0.0.1:3030
SocksPort 9050
ControlPort 9051
```

### Commands
```bash
# Start
sudo systemctl start tor

# Check status
sudo systemctl status tor

# View onion address
cat /var/lib/tor/symbiote-onion-service/hostname

# Test connectivity
curl --socks5 localhost:9050 http://check.torproject.org
```

## Tails USB (OTG Jump-Box)

### USB Device
- **Device:** /dev/sda (SanDisk 3.2Gen1, 57.3 GB)
- **Image:** tails-amd64-7.10.1.img (1.74 GB)
- **Source image:** /home/uncannyblacc/Documents/tails-amd64-7.10.1.img

### Partition Layout
| Partition | Size | Type | Purpose |
|---|---|---|---|
| `/dev/sda1` | 1.7 GB | EFI System (FAT32) | Tails boot |
| `/dev/sda2` | 55 GB | Linux (ext4) | Tails persistence (label: TailsData) |

### Persistence Config
```
/live/persistence/TailsData_unlocked/persistence.conf
→ "/ union"
```

### Setup Commands
```bash
# Flash Tails
sudo dd if=/home/uncannyblacc/Documents/tails-amd64-7.10.1.img of=/dev/sda bs=4M status=progress oflag=sync

# Fix GPT + create persistence partition
sudo sgdisk -e /dev/sda
sudo sgdisk -n 2:0:+55GiB /dev/sda --typecode 2:8300 --change-name 2:"TailsData"

# Format + configure (run on any Linux box)
sudo mkfs.ext4 -L "TailsData" /dev/sda2
sudo mkdir -p /mnt/persist
sudo mount /dev/sda2 /mnt/persist
sudo mkdir -p /mnt/persist/live/persistence/TailsData_unlocked
echo "/ union" | sudo tee /mnt/persist/live/persistence/TailsData_unlocked/persistence.conf
sudo umount /mnt/persist
```

### Usage
1. Insert USB into portable SSD host via USB-C OTG adapter
2. Boot Tails (hold Volume Up + tap Power)
3. Unlock persistence (set passphrase on first boot)
4. Everything persists across sessions, encrypted on-device

## Network Architecture
```
Venom (:3030) ←Tor→ Tails OTG (.onion:3030) ←Tor→ Toxin Phone (when acquired)
                ↑
                └── localhost:9050 (SOCKS)
```