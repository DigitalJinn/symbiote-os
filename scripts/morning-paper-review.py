#!/usr/bin/env python3
"""
Morning Paper Review for SymbioteOS — IMPROVED VERSION
Daily at 9:00 AM via cron job b591756522e9

Improvements over original:
1. Copilot code review runs non-blocking (background job) — digest delivery never waits
2. Auto-delivers digest to AgentMail via MCP (with JSON fallback)
3. Structured logging to ~/.symbiote-brain/morning-review.log

Workflow:
- Hermes reads BOTH byte2byte.md and tdlr.md daily
- Extracts action items and paper insights (with deduplication)
- Sends digest to your AgentMail inbox for byte-by-byte review
- Feeds insights back into Symbiote OS brain state (~/.symbiote-brain)
- Kicks off Copilot code review in background (non-blocking)

Output:
- /tmp/agentmail-digest.json — email for your AgentMail inbox
- ~/.symbiote-brain/morning-review.log — structured log
"""

import os
import sys
import json
import re
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────────────────────────
HOME = Path.home()
BYTE2BYTE_PATH = HOME / "MEGA/The Hive/Studies/byte2byte.md"
TDLR_PATH = HOME / "MEGA/The Hive/Studies/tdlr.md"
BRIDGE_STATE_PATH = HOME / ".symbiote-brain/brain-state.json"
OUTPUT_FILE = Path("/tmp/agentmail-digest.json")
COPILOT_REVIEW_LOG = Path("/tmp/copilot-code-review.json")
LOG_FILE = HOME / ".symbiote-brain/morning-review.log"
TOXIN_DIR = str(HOME / "projects/symbiote-os/toxin/")

# ─── Logging Setup ───────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(str(LOG_FILE)),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("morning-review")


def extract_status_items(content):
    """Extract items with status markers: ✓ (done), ○ (in progress), □ (todo)."""
    items = []
    for line in content.split('\n'):
        line = line.strip()
        if any(marker in line for marker in ['✓', '○', '□']):
            match = re.search(r'[✓○□]\s*(.+)', line)
            if match:
                item_text = match.group(1).strip()
                status = 'complete' if '✓' in line else ('in_progress' if '○' in line else 'pending')
                items.append({'status': status, 'item': item_text})
    return items


def extract_checklist_items(content):
    """Extract markdown checklist items (- [ ] / - [x])."""
    items = []
    for line in content.split('\n'):
        line = line.strip()
        match = re.match(r'-\s*\[(.)\]\s+(.+)', line)
        if match:
            checkbox, item_text = match.groups()
            status = 'complete' if checkbox.lower() == 'x' else 'pending'
            items.append({'status': status, 'item': item_text.strip()})
    return items


def extract_paper_summaries(content, max_papers=10, seen_titles=None):
    """Extract paper titles, abstracts, and relevance to SymbioteOS.
    
    Args:
        seen_titles: set of titles already extracted (for deduplication)
    """
    if seen_titles is None:
        seen_titles = set()
    
    summaries = []
    # Split on either "### Paper N:" or "**Paper N:" patterns
    sections = re.split(r'(?:###\s+Paper\s+\d+:|Paper\s+\d+:\s*\n)', content)
    
    for section in sections[1:max_papers+1]:
        title_match = re.match(r'\s*"([^"]+)"', section)
        title = title_match.group(1) if title_match else "Untitled"

        # Skip duplicate papers
        if title in seen_titles:
            log.debug(f"Skipping duplicate paper: {title}")
            continue
        seen_titles.add(title)

        relevance_match = re.search(
            r'\*\*Relevance to SymbioteOS:\*\*\s*\n(.+?)(?=\n\*\*|\n---|$)',
            section, re.DOTALL
        )
        relevance = []
        if relevance_match:
            for line in relevance_match.group(1).split('\n'):
                line = line.strip()
                if line.startswith('-'):
                    relevance.append(line[1:].strip())

        abstract_match = re.search(
            r'\*\*Abstract:\*\*\s*\n(.+?)(?=\n\*\*|\n---|\\*\*Relevance)',
            section, re.DOTALL
        )
        abstract = abstract_match.group(1).strip()[:300] if abstract_match else ""

        summaries.append({
            'title': title,
            'abstract': abstract,
            'relevance': relevance[:3],
            'actions': extract_checklist_items(section)
        })
    return summaries


def build_digest():
    """Hermes reads both papers, extracts everything, builds your digest.
    
    Returns:
        digest: dict for AgentMail send_message
        stats: dict with counts
        insights: list of insight strings
        seen_titles: set of all paper titles (for dedup across files)
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    seen_titles = set()  # Track all paper titles across both files

    # Read byte2byte
    byte2byte_items = []
    byte2byte_summaries = []
    try:
        if BYTE2BYTE_PATH.exists():
            content = BYTE2BYTE_PATH.read_text()
            byte2byte_items = extract_status_items(content)
            byte2byte_summaries = extract_paper_summaries(content, seen_titles=seen_titles)
        else:
            log.warning(f"byte2byte.md not found at {BYTE2BYTE_PATH}")
            byte2byte_items = [{'status': 'error', 'item': f'File not found: {BYTE2BYTE_PATH}'}]
    except Exception as e:
        log.error(f"Error reading byte2byte.md: {e}")
        byte2byte_items = [{'status': 'error', 'item': f'Error: {e}'}]

    # Read tdlr (dedup against byte2byte)
    tdlr_items = []
    tdlr_summaries = []
    try:
        if TDLR_PATH.exists():
            content = TDLR_PATH.read_text()
            tdlr_items = extract_checklist_items(content)
            tdlr_summaries = extract_paper_summaries(content, seen_titles=seen_titles)
        else:
            log.warning(f"tdlr.md not found at {TDLR_PATH}")
            tdlr_items = [{'status': 'error', 'item': f'File not found: {TDLR_PATH}'}]
    except Exception as e:
        log.error(f"Error reading tdlr.md: {e}")
        tdlr_items = [{'status': 'error', 'item': f'Error: {e}'}]

    # Build sections
    byte2byte_section = '\n'.join([
        f"  • [{i['status'].upper()}] {i['item']}"
        for i in byte2byte_items[:10]
    ]) if byte2byte_items else "  (No items found)"

    tdlr_section = '\n'.join([
        f"  • [{i['status'].upper()}] {i['item']}"
        for i in tdlr_items[:15]
    ]) if tdlr_items else "  (No items found)"

    # Agent insights (extract ALL relevance bullets, not just the first)
    all_summaries = byte2byte_summaries + tdlr_summaries
    insights = []
    for paper in all_summaries:
        if paper['relevance']:
            for relevance_item in paper['relevance'][:2]:  # Take up to 2 per paper
                insights.append(f"  • {paper['title']}: {relevance_item}")
    insights_section = '\n'.join(insights[:10]) if insights else "  (No insights extracted)"

    # Build email body
    body = f"""Good morning! Hermes has read today's papers:

📄 BYTE2BYTE — Action Items for Your Review:
{byte2byte_section}

📝 TDLR — Daily Updates for Your Review:
{tdlr_section}

🔍 Key Insights (Hermes extracted these from both papers):
{insights_section}

🔗 Review Links:
- byte2byte.md: ~/MEGA/The Hive/Studies/byte2byte.md
- tdlr.md: ~/MEGA/The Hive/Studies/tdlr.md

Next review: Tomorrow at 9:00 AM

#SymbioteOS #Agentmail #DailyReview"""

    digest = {
        'inboxId': 'agentmail@inbox.local',
        'to': 'agentmail@inbox.local',
        'subject': f'SymbioteOS Daily Paper Digest — {date_str}',
        'body': body
    }

    stats = {
        'byte2byte_items': len(byte2byte_items),
        'tdlr_items': len(tdlr_items),
        'byte2byte_papers': len(byte2byte_summaries),
        'tdlr_papers': len(tdlr_summaries),
        'total_papers': len(byte2byte_summaries) + len(tdlr_summaries),
        'insights_extracted': len(insights),
        'duplicates_skipped': len(seen_titles) - len(byte2byte_summaries) - len(tdlr_summaries)
    }

    return digest, stats, insights, seen_titles


def send_digest_via_agentmail(digest):
    """Attempt to send digest via AgentMail MCP.
    
    Uses the agentmail CLI directly if available, falls back to JSON file.
    """
    log.info("Attempting to deliver digest via AgentMail MCP...")

    AGENTMAIL_API_KEY = os.environ.get("AGENTMAIL_API_KEY", "")
    
    # Try the agentmail MCP via npx in subprocess
    # Write digest to a temp file that the MCP script can read
    temp_digest_path = "/tmp/agentmail-digest-mcp-input.json"
    try:
        with open(temp_digest_path, 'w') as f:
            json.dump(digest, f)
    except Exception as e:
        log.error(f"Failed to write temp digest file: {e}")
    
    # Save to output file (the primary fallback)
    try:
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(digest, f, indent=2)
        log.info(f"  ✓ Digest saved to {OUTPUT_FILE}")
    except Exception as e:
        log.error(f"  ❌ Failed to save digest: {e}")
    
    # Try sending via agentmail MCP tool
    # When run from Hermes agent context, mcp__agentmail__send_message is available
    # When run standalone (cron), we attempt the CLI approach
    if AGENTMAIL_API_KEY:
        try:
            import urllib.request
            import urllib.error
            
            url = "https://api.agentmail.to/v1/inboxes/agentmail@inbox.local/drafts"
            req_data = json.dumps({
                "to": "agentmail@inbox.local",
                "subject": digest['subject'],
                "body": digest['body']
            }).encode('utf-8')
            
            req = urllib.request.Request(
                url, 
                data=req_data,
                headers={
                    "Authorization": f"Bearer {AGENTMAIL_API_KEY}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode())
                log.info(f"  ✓ Sent via AgentMail API: {result.get('id', 'unknown')}")
                
                # Send the draft
                draft_id = result.get('id')
                if draft_id:
                    send_url = f"https://api.agentmail.to/v1/inboxes/agentmail@inbox.local/drafts/{draft_id}/send"
                    send_req = urllib.request.Request(send_url, method="POST", headers={
                        "Authorization": f"Bearer {AGENTMAIL_API_KEY}",
                        "Content-Type": "application/json"
                    })
                    try:
                        urllib.request.urlopen(send_req, timeout=15)
                        log.info("  ✓ Draft sent successfully")
                        return {'status': 'sent_via_api', 'draft_id': draft_id}
                    except Exception as e:
                        log.warning(f"  ⚠ Could not send draft: {e}")
                        return {'status': 'draft_saved', 'draft_id': draft_id}
                
        except urllib.error.HTTPError as e:
            log.warning(f"  ⚠ AgentMail API error: {e.code} — digest saved to file")
        except Exception as e:
            log.warning(f"  ⚠ AgentMail MCP delivery failed: {e} — digest saved to file")
    else:
        log.info("  ℹ AGENTMAIL_API_KEY not set — digest saved to file for manual send")
    
    return {'status': 'saved_to_file', 'path': str(OUTPUT_FILE)}


def update_paper_dates():
    """Replace {{date}} placeholder with current date in paper files."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    for paper_path in [BYTE2BYTE_PATH, TDLR_PATH]:
        if paper_path.exists():
            content = paper_path.read_text()
            updated = content.replace('{{date}}', date_str)
            if updated != content:
                paper_path.write_text(updated)
                log.info(f"Updated dates in {paper_path.name}")


def update_brain_state(stats, insights):
    """Update symbiote-brain with today's findings."""
    state_updates = {
        'last_paper_review': datetime.now().isoformat(),
        'papers_reviewed': stats['total_papers'],
        'byte2byte_items': stats['byte2byte_items'],
        'tdlr_items': stats['tdlr_items'],
        'insights_extracted': len(insights),
        'agent_insights': insights,
        'brains_active': ['hermes', 'codex', 'copilot'],
        'pending_actions': [
            'Review byte2byte papers for Venom SSD optimizations',
            'Apply TDLR decidability limits to agentmail workflows',
            'Implement temporal logic in Phage LLM prompts',
            'Update delegation map with complexity bounds'
        ]
    }

    existing = {}
    try:
        if BRIDGE_STATE_PATH.exists():
            content = BRIDGE_STATE_PATH.read_text()
            existing = json.loads(content)
    except Exception as e:
        log.error(f"Error reading brain-state.json: {e}")

    # Merge: keep existing keys, update with new values
    existing.update(state_updates)

    try:
        BRIDGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(BRIDGE_STATE_PATH, 'w') as f:
            json.dump(existing, f, indent=2)
        log.info("Brain state updated successfully")
    except Exception as e:
        log.error(f"Failed to update brain state: {e}")

    return state_updates


def start_copilot_review_background(insights):
    """Start Copilot code review as a non-blocking background job.
    
    Uses subprocess.Popen so the digest delivery is NOT blocked.
    Results are written to /tmp/copilot-code-review.json.
    """
    log.info("Starting Copilot code review in background (non-blocking)...")

    # Build prompt for Copilot
    prompt_parts = [
        "Review the SymbioteOS codebase for code changes related to the following insights from today's paper review:"
    ]
    for insight in insights:
        clean = insight.replace("  • ", "").strip()
        prompt_parts.append(f"- {clean}")
    prompt_parts.append("")
    prompt_parts.append("Scope: focus on the Toxin Android project at the given directory. Check for:")
    prompt_parts.append("1. Temporal logic integration in LLM prompts (Phage layer)")
    prompt_parts.append("2. Self-modifying code patterns in Toxin component")
    prompt_parts.append("3. Byte-level optimization primitives")
    prompt_parts.append("4. Bounded complexity patterns in AI workflows")
    prompt_parts.append("5. Decidability-based security in Carnage ACL")
    prompt_parts.append("")
    prompt_parts.append("Output format: list any issues found, any code suggestions, and confirm the Toxin Android build is not broken.")
    prompt = "\n".join(prompt_parts)

    review_entry = {
        "timestamp": datetime.now().isoformat(),
        "brain": "copilot",
        "role": "4th brain - code review + Toxin project",
        "scoped_dir": TOXIN_DIR,
        "prompt": prompt,
        "status": "launched_background",
        "findings": [],
        "suggestions": []
    }

    # Write initial entry immediately
    try:
        with open(COPILOT_REVIEW_LOG, 'w') as f:
            json.dump(review_entry, f, indent=2)
    except Exception as e:
        log.error(f"Failed to write initial copilot review log: {e}")

    # Launch Copilot as a detached background process
    # It will write its result to /tmp/copilot-code-review.json when done
    copilot_launcher = f"""
import subprocess, json, os
from datetime import datetime

prompt = '''{prompt}'''
TOXIN_DIR = '{TOXIN_DIR}'

try:
    result = subprocess.run(
        ['npx', '-y', '@github/copilot-linux-x64', '-p', prompt,
         '--add-dir', TOXIN_DIR, '--allow-all', '--silent', '--no-auto-update'],
        capture_output=True, text=True, timeout=300
    )
    
    findings = []
    suggestions = []
    for line in result.stdout.split('\\n'):
        if any(kw in line.lower() for kw in ['bug', 'issue', 'broken', 'error', 'problem']):
            findings.append(line.strip())
        if any(kw in line.lower() for kw in ['suggestion', 'recommend', 'should', 'consider']):
            suggestions.append(line.strip())
    
    review = {{
        "timestamp": datetime.now().isoformat(),
        "brain": "copilot",
        "role": "4th brain - code review + Toxin project",
        "scoped_dir": TOXIN_DIR,
        "prompt": prompt,
        "status": "completed" if result.returncode == 0 else "error",
        "findings": findings,
        "suggestions": suggestions,
        "response": result.stdout.strip() if result.stdout else "",
        "stderr": result.stderr.strip() if result.stderr else ""
    }}
except subprocess.TimeoutExpired:
    review = {{
        "timestamp": datetime.now().isoformat(),
        "brain": "copilot",
        "status": "timeout",
        "error": "copilot review timed out after 300s"
    }}
except FileNotFoundError:
    review = {{
        "timestamp": datetime.now().isoformat(),
        "brain": "copilot",
        "status": "copilot_cli_not_found",
        "error": "npx or copilot CLI not found in PATH"
    }}
except Exception as e:
    review = {{
        "timestamp": datetime.now().isoformat(),
        "brain": "copilot",
        "status": "error",
        "error": str(e)
    }}

with open('{COPILOT_REVIEW_LOG}', 'w') as f:
    json.dump(review, f, indent=2)
"""

    try:
        # Launch completely detached — this process will exit, the background job continues
        subprocess.Popen(
            ['python3', '-c', copilot_launcher],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True  # Fully detach
        )
        log.info("Copilot review launched in background — digest delivery continues")
    except Exception as e:
        log.error(f"Failed to launch Copilot review background job: {e}")
        # Don't block the digest delivery — just log the error


if __name__ == '__main__':
    log.info("=" * 60)
    log.info("Morning Paper Review - SymbioteOS (Hermes reads both)")
    log.info("=" * 60)

    # Step 1: Read papers + extract
    log.info("📚 Hermes reading byte2byte.md + tdlr.md...")
    update_paper_dates()
    digest, stats, insights, seen_titles = build_digest()

    log.info(f"  ✓ Papers reviewed: {stats['total_papers']}")
    log.info(f"  ✓ byte2byte action items: {stats['byte2byte_items']}")
    log.info(f"  ✓ tdlr action items: {stats['tdlr_items']}")
    log.info(f"  ✓ Agent insights extracted: {len(insights)}")
    log.info(f"  ✓ Duplicates skipped: {stats.get('duplicates_skipped', 0)}")

    # Step 2: Update brain state (BEFORE digest delivery — never skip this)
    log.info("🧠 Updating brain state...")
    try:
        updates = update_brain_state(stats, insights)
        log.info(f"  ✓ Brain state updated ({len(updates['pending_actions'])} pending actions)")
    except Exception as e:
        log.error(f"  ❌ Error updating brain: {e}")

    # Step 3: Send digest via AgentMail MCP (non-blocking Copilot)
    log.info("📧 Preparing + delivering agentmail digest...")
    try:
        delivery = send_digest_via_agentmail(digest)
        log.info(f"  ✓ Delivery status: {delivery.get('status', 'unknown')}")
        if delivery.get('path'):
            log.info(f"  ✓ Fallback file: {delivery['path']}")
    except Exception as e:
        log.error(f"  ❌ Error delivering digest: {e}")
        # Fallback: save JSON
        try:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(digest, f, indent=2)
            log.info(f"  ✓ Fallback: digest saved to {OUTPUT_FILE}")
        except Exception as e2:
            log.error(f"  ❌ Failed to save fallback digest: {e2}")

    # Step 4: Launch Copilot review in BACKGROUND (non-blocking)
    log.info("👁️  Launching Copilot (4th brain) code review...")
    try:
        start_copilot_review_background(insights)
    except Exception as e:
        log.error(f"  ❌ Copilot review launch failed: {e}")
        # Create error entry in review log
        error_review = {
            "timestamp": datetime.now().isoformat(),
            "brain": "copilot",
            "status": "launch_error",
            "error": str(e)
        }
        try:
            with open(COPILOT_REVIEW_LOG, 'w') as f:
                json.dump(error_review, f, indent=2)
        except:
            pass

    log.info("✅ Morning review complete!")
    log.info("   Digest delivered or saved to /tmp/agentmail-digest.json")
    log.info("   Copilot review running in background")
    log.info("   Log: ~/.symbiote-brain/morning-review.log")
    log.info("=" * 60)
