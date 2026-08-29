# AgentMail — Agent-Owned Email

> MCP integration for agent-owned email inboxes

## Status: ✅ Configured + Active

### Setup
- **MCP Server:** `agentmail-mcp@1.0.2` (cached locally via npx)
- **Config:** `~/.hermes/config.yaml` → `mcp_servers.agentmail`
- **API Key:** Set via `hermes config set mcp_servers.agentmail.env.AGENTMAIL_API_KEY`

### Inbox
- **Email:** `agentmail@inbox.local`
- **Display name:** Chief Of Staff
- **Created:** 2026-08-10
- **Organization:** Unverified (run `agent_verify` when 6-digit code received)

### Tools Available (11 core + 3 utility)

| Method | Description |
|---|---|
| `list_inboxes` | List all agent inboxes |
| `get_inbox` | Get inbox by ID |
| `create_inbox` | Create a new email inbox |
| `update_inbox` | Update display name/metadata |
| `delete_inbox` | Delete an inbox |
| `list_threads` | List email threads in an inbox |
| `search_threads` | Search threads (full-text query) |
| `get_thread` | Get thread + messages |
| `get_attachment` | Get attachment from a thread |
| `update_thread` | Update thread labels |
| `delete_thread` | Delete a thread |
| `send_message` | Send email from an inbox |
| `reply_to_message` | Reply in a thread |
| `forward_message` | Forward to new recipients |
| `create_draft` | Create+schedule drafts |
| `list_drafts` | List drafts |
| `send_draft` | Send a draft immediately |

### Current Mailbox State (checked 2026-08-19 20:42)

10 unread threads:
1. **Substack** — "339456 is your Substack verification code" (today 20:33) ← **verify @[REDACTED_SOCIAL] subscription**
2. **Big Think** — "How to argue less and talk more" (today 19:05)
3. **Zapier** — "Your AI is waiting—try this one prompt" (today 17:32)
4. **ByteByteGo** — "GraphRAG: How AI Answers Questions..." (today 15:31)
5. **OpenAI** — "New sign-in to your OpenAI account" (today 14:06)
6. **Zapier** — "What project teams are automating this week" (today 14:04)
7. **TLDR AI** — "GLM-5.3 API, Cerebras' new chip..." (today 13:50)
8. **Nate's Substack** — "Personal software is here..." (today 13:01)
9. **TLDR Design** — "AirPods Get Cameras..." (today 12:22)
10. **TLDR DevOps** — "Benchmarkpocalypse, DuckDB 2.0..." (today 11:28)

### Verification Code
- **Code: `339456`** — from `uncannyblacc@substack.com`
- This verifies the `@[REDACTED_SOCIAL]` Substack subscription to `agentmail@inbox.local`
- Use within 15 minutes before expiry

### Usage Examples

```bash
# Via Hermes MCP integration (available in chat context):
# "List inboxes"
# "Read the Substack verification email"
# "Send an email from agentmail@inbox.local to..."

# Direct MCP test (manual):
export AGENTMAIL_API_KEY="«AGENTMAIL_API_KEY»..."
npx -y agentmail-mcp
```

> Note: This is a **separate** email identity from the user's personal Proton Mail. AgentMail gives the agent its own communication channel for autonomous operations (service signups, notifications, outbound messages on behalf of the agent).

### Important Security Notes
- The API key is stored in `~/.hermes/config.yaml` (masked in chat output)
- The `agent_verify` tool must be called to claim the organization
- Free tier: 3 inboxes, 3,000 emails/month
