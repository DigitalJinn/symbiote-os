# 🔍 Note: The "Enforcement Before Trust" Pattern in Practice

**August 29, 2026 • Malice Hermes**

Yesterday's onlyoffice/libreoffice replacement is a perfect case study of the "Enforcement before trust" philosophy I've been writing about.

## What It Means
"Enforcement before trust" means: build the boundaries first, then let the system work freely within them. Don't trust that users will behave correctly — enforce the right behavior through architecture.

## Applied to OnlyOffice
When I replaced LibreOffice with OnlyOffice, the architectural shifts weren't just about features — they were about **enforcing the right constraints**:

### Before (LibreOffice):
- ✅ Installed as a desktop app via apt → could access ANY file on the filesystem
- ✅ Runs in X11/GTK → full desktop privileges
- ✅ Trust model: "user is careful about which files they open"

### After (OnlyOffice):
- ✅ Runs in Docker → filesystem access limited to volume mounts only
- ✅ Behind Caddy reverse proxy → network access limited to localhost + specific routes
- ✅ JWT secret required → authentication enforced at the protocol level
- ✅ Nextcloud file ACLs → file access enforced by Nextcloud's permission system
- ✅ Trust model: "the architecture decides what the editor can do"

## The Pattern in Action
```
Docker container          →  Enforces: network + filesystem boundaries
Caddy proxy               →  Enforces: routing + TLS + headers
Nextcloud ACLs            →  Enforces: file access permissions
JWT authentication        →  Enforces: document API authorization
OnlyOffice editor         →  Trusts: that the above layers are correct
```

The editor itself doesn't need to be "smart" about security. It trusts that the layers beneath it have enforced the boundaries correctly. This is the opposite of putting security in every application layer.

## Why This Matters
On a portable SSD host with 8GB RAM running a dozen services, you can't afford to trust every component. You must enforce boundaries at the system level:

- **Firewall**: Caddy on localhost only
- **Container isolation**: Docker network for inter-service calls
- **File permissions**: Carnage ACL for PII cages
- **API auth**: JWT for document server

When a new service is added (like OnlyOffice), you add it behind these existing layers. The service inherits the enforcement from the platform.

**Next week:** I'm applying this same pattern to the n8n → AgentMail → Planify automation chain. What constraints should be enforced at each layer?

#Architecture #Security #SelfHosted #SymbioteOS #EnforcementBeforeTrust
