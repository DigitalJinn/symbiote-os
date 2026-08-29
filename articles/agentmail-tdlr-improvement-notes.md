# AgentMail Feedback for TDLR Byte2Byte Morning Review Improvements

## Review Date: August 28, 2026

### Areas Identified for Improvement

#### 1. **Paper Parsing Fragility**
**Issue:** The regex in `morning-paper-review.py` uses fragile patterns for parsing markdown paper files.

**Current problem:**
- `extract_paper_summaries()` splits on `### Paper \d+:` — breaks if paper numbering changes or uses `-` bullets
- `extract_checklist_items()` only matches `- [.] text` — misses alternative markdown checkboxes
- No handling for papers with nested sections or code blocks

**Recommended fix:**
- Use a proper markdown parser (e.g., `markdown-it-py` or `mistune`) instead of regex
- Add fallback parsing paths for common format variations
- Validate extracted content before including in digest

#### 2. **Copilot Code Review Blocking the Digest**
**Issue:** The `run_copilot_code_review()` function runs synchronously and can block the entire digest for 300 seconds.

**Current problem:**
- If Copilot hangs or the Toxin project is broken, users don't get their morning digest
- Script exits with timeout, brain state update may not happen
- No retry mechanism for Copilot review

**Recommended fix:**
```python
# Make Copilot review non-blocking — write findings async
# Use subprocess.Popen + callback, or defer to background job
# Ensure brain-state.json updates even if Copilot fails
```

#### 3. **Digest Delivery Not Automated**
**Issue:** The digest is written to `/tmp/agentmail-digest.json` but never sent automatically.

**Current problem:**
- The `SETUP_GUIDE.md` mentions "Delivery Prep: Saves digest for AgentMail delivery" but doesn't actually trigger the MCP call
- User has to manually trigger `mcp__agentmail__send_message` 
- No MCP tool is invoked from the Python script

**Recommended fix:**
- Add an MCP client call at the end of `morning-paper-review.py`
- Use `mcp__agentmail__send_draft` or `send_message` to auto-deliver
- Fall back gracefully if AgentMail MCP is unavailable

#### 4. **No Deduplication Between byte2byte and tdlr**
**Issue:** Papers are read from two separate files but there's no deduplication logic.

**Current problem:**
- Same paper could appear in both `byte2byte.md` and `tdlr.md`
- Digest would show duplicate entries
- Brain state `papers_reviewed` count could be inflated

**Recommended fix:**
- Deduplicate paper titles across both files before extraction
- Track which papers were already reviewed (compare with `brain-state.json`)

#### 5. **Missing Action Item Status Tracking**
**Issue:** The script extracts action items but doesn't update their status in the source files.

**Current problem:**
- Items marked `○` (in-progress) or `□` (todo) stay that way forever
- No mechanism to mark items as `✓` (done) after they're reviewed
- Brain state gets stale pending actions

**Recommended fix:**
- After digest, update action items that were reviewed (mark as reviewed in a separate field)
- Use a YAML frontmatter section at the top of each paper file to track metadata per paper
- Example:
  ```yaml
  ---
  last_reviewed: 2026-08-28
  status: reviewed, action_pending
  ---
  ```

#### 6. **No Daily Paper File Rotation**
**Issue:** Paper files are static — same content reviewed every day.

**Current problem:**
- The script runs daily but reads the same `byte2byte.md` and `tdlr.md`
- There's a `{{date}}` placeholder replacement but no actual new content
- No mechanism to append daily entries or archive old reviews

**Recommended fix:**
- Add a `--rotate` flag that appends today's date to filenames
- Create new daily files: `byte2byte-2026-08-28.md`, `tdlr-2026-08-28.md`
- Keep symlinks `byte2byte.md` → `byte2byte-{today}.md` for the script to read

#### 7. **Error Handling Gaps**
**Issue:** File write/read errors are caught but not surfaced.

**Current problem:**
- If `~/.symbiote-brain/brain-state.json` is unreadable, script continues silently
- No logging to a file for debugging
- No structured error reporting to AgentMail (e.g., "paper file not found")

**Recommended fix:**
- Add structured logging to `~/.symbiote-brain/morning-review.log`
- On file errors, include error info in the digest email
- Add a `--verbose` flag for debugging

#### 8. **Insight Extraction Too Shallow**
**Issue:** Only extracts the first relevance bullet per paper.

**Current problem:**
- `insights.append(f"  • {paper['title']}: {paper['relevance'][0]}")` — only takes first relevance item
- Misses actionable insights from paper abstracts
- No LLM-based summarization (could use local Qwen model)

**Recommended fix:**
- Include ALL relevance bullets in the insights section
- Add a local LLM call (via llama.cpp on :8080) to generate a one-line summary per paper
- Format insights as "Paper → Insight → Action" triplets

### Priority Recommendation

**High priority (implement next):**
1. Fix the Copilot blocking issue (#2) — move it async or background it
2. Auto-deliver digest via AgentMail MCP (#3)
3. Improve error handling + logging (#7)

**Medium priority:**
4. Deduplicate papers across files (#4)
5. Improve insight extraction (#8)

**Lower priority (nice-to-have):**
6. Add action item status tracking (#5)
7. Implement paper file rotation (#6)
8. Replace regex with proper markdown parser (#1)

### Tags
#AgentMail #TDLR #Byte2Byte #MorningReview #SymbioteOS #ImprovementNotes
