// Symbiote-OS Orchestrator (Venom)
// Phase 1–7 — minimal functional implementation
// Serves: health check, Hive metadata, chat routing, Carnage audit logging
// Venom Revamp: llama.cpp replaces Ollama (host service on port 8080)

import express from 'express';
import http from 'http';
import { Server as SocketIOServer } from 'socket.io';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';
import { writeFile, readFile, appendFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import chalk from 'chalk';
import { initializeSymbioteACL } from './carnage-acl.js';

// Load .env
dotenv.config({ path: path.resolve(process.env.ENV_PATH || '.env') });

const PORT = process.env.ORCHESTRATOR_PORT || 3030;
const HOST = process.env.ORCHESTRATOR_HOST || 'localhost';
const HIVE_ROOT = process.env.SYMBIOTE_HIVE_ROOT || path.join(process.env.HOME, '.symbiote-brain');
const LLAMACPP_URL = process.env.LLAMACPP_URL || 'http://localhost:8080';

// ─── Carnage ACL: Initialize with Symbiote policies ─────────────────
// Enforces Business-Private cage isolation (hermes uid 996 blocked)
const carnage = initializeSymbioteACL();

const app = express();
const server = http.createServer(app);
const io = new SocketIOServer(server, {
  cors: { origin: '*' }
});

// Middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// ─── Routes ───────────────────────────────────────────────────────────

// Health check — includes llama.cpp status
app.get('/api/health', async (req, res) => {
  let llamaStatus = 'disconnected';
  try {
    const r = await fetch(`${LLAMACPP_URL}/health`);
    llamaStatus = r.ok ? 'ok' : 'degraded';
  } catch {
    llamaStatus = 'disconnected';
  }

  res.json({
    status: 'ok',
    service: 'symbiote-orchestrator',
    uptime: process.uptime(),
    hive: HIVE_ROOT,
    llama_cpp: llamaStatus,
    timestamp: new Date().toISOString()
  });
});

// Orchestrator info
app.get('/api/info', (req, res) => {
  res.json({
    name: 'symbiote-orchestrator',
    version: '0.2.0',
    description: 'Local-first agentic hub for Venom (Debian 13)',
    phase: 'Phase 1–7 active',
    components: ['venom', 'tendril', 'toxin'],
    clis: ['hermes', 'codex', 'copilot', 'openai'],
    backends: ['llama.cpp (Qwen2.5-3B-Instruct Q4_0)'],
    hive_root: HIVE_ROOT,
    orchestrator_port: PORT,
    frontend_port: 5173,
    llama_cpp_url: LLAMACPP_URL
  });
});

// Hive endpoints
app.get('/api/hive', (req, res) => {
  const cages = ['Life-OS', 'Business-Private', 'Claude-Brain'];
  const structure = cages.map(cage => {
    const cagePath = path.join(HIVE_ROOT, cage);
    const decision = carnage.validatePathAccess(cagePath);

    return {
      name: cage,
      path: cagePath,
      locked: cage === 'Business-Private',
      exists: existsSync(cagePath),
      // Carnage ACL: report access status for hermes user
      access: decision.allowed ? 'read' : 'denied',
      cage: decision.cage
    };
  });
  res.json({ cages: structure, root: HIVE_ROOT });
});

// Carnage ACL: Validate path access before any filesystem operation
app.get('/api/hive/:path(*)', carnage.pathAccessMiddleware('path'), async (req, res) => {
  try {
    const requestedPath = path.join(HIVE_ROOT, req.params.path);
    const fullPath = path.resolve(requestedPath);

    if (!existsSync(fullPath)) {
      return res.status(404).json({ error: 'Path not found' });
    }

    const data = await readFile(fullPath, 'utf-8');
    res.json({ path: fullPath, content: data, carnage: req.carnageDecision });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Carnage ACL: Validate path write access
app.post('/api/hive/:path(*)/write', carnage.pathAccessMiddleware('path'), async (req, res) => {
  try {
    const requestedPath = path.join(HIVE_ROOT, req.params.path);
    const fullPath = path.resolve(requestedPath);

    await writeFile(fullPath, req.body.content || '');
    res.json({ success: true, path: fullPath, carnage: req.carnageDecision });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Carnage ACL: Endpoint to check path access decisions
app.get('/api/acl/check', (req, res) => {
  const { path: checkPath } = req.query;
  if (!checkPath) {
    return res.status(400).json({ error: 'path query param required' });
  }

  const decision = carnage.validatePathAccess(checkPath);
  res.json({
    allowed: decision.allowed,
    cage: decision.cage,
    user: decision.user,
    uid: decision.uid,
    is_hermes: decision.is_hermes,
    path: decision.path,
    decision_id: decision.decision_id
  });
});

// Brain state
app.get('/api/brain-state', async (req, res) => {
  try {
    const statePath = path.join(HIVE_ROOT, 'brain-state.json');
    if (existsSync(statePath)) {
      const data = await readFile(statePath, 'utf-8');
      res.json(JSON.parse(data));
    } else {
      res.json({ error: 'brain-state.json not found' });
    }
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Chat log
app.get('/api/chats', async (req, res) => {
  try {
    const chatPath = path.join(HIVE_ROOT, 'chats.jsonl');
    if (!existsSync(chatPath)) {
      return res.json({ chats: [] });
    }
    const data = await readFile(chatPath, 'utf-8');
    const chats = data.trim().split('\n')
      .filter(line => line)
      .map(line => JSON.parse(line));
    res.json({ chats });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Save chat
app.post('/api/chats', async (req, res) => {
  try {
    const chatPath = path.join(HIVE_ROOT, 'chats.jsonl');
    await appendFile(chatPath, JSON.stringify({
      id: uuidv4(),
      timestamp: new Date().toISOString(),
      ...req.body
    }) + '\n');
    res.status(201).json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Carnage audit log
app.get('/api/carnage', async (req, res) => {
  try {
    const auditPath = path.join(HIVE_ROOT, '.carnage_audit.log');
    if (!existsSync(auditPath)) {
      return res.json({ entries: [] });
    }
    const data = await readFile(auditPath, 'utf-8');
    const entries = data.trim().split('\n')
      .filter(line => line)
      .map(line => JSON.parse(line));
    res.json({ entries });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// llama.cpp proxy — chat completion endpoint
app.post('/api/llm/chat', async (req, res) => {
  try {
    const response = await fetch(`${LLAMACPP_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'llama.cpp not reachable', detail: err.message });
  }
});

// llama.cpp models endpoint
app.get('/api/llm/models', async (req, res) => {
  try {
    const response = await fetch(`${LLAMACPP_URL}/v1/models`);
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'llama.cpp not reachable' });
  }
});

// llama.cpp health
app.get('/api/llm/health', async (req, res) => {
  try {
    const response = await fetch(`${LLAMACPP_URL}/health`);
    const data = await response.json();
    res.json(data);
  } catch (err) {
    res.status(502).json({ error: 'llama.cpp not reachable', detail: err.message });
  }
});

// ─── WebSocket ───────────────────────────────────────────────────────

io.on('connection', (socket) => {
  console.log(chalk.blue('[socket] Client connected:', socket.id));

  // Echo + broadcast
  socket.on('chat', (data) => {
    console.log(chalk.gray('[socket] chat:', data));
    socket.broadcast.emit('chat', data);
  });

  socket.on('disconnect', () => {
    console.log(chalk.blue('[socket] Client disconnected:', socket.id));
  });
});

// ─── Startup ─────────────────────────────────────────────────────────

server.listen(PORT, HOST, () => {
  console.log(chalk.green.bold('======================================='));
  console.log(chalk.green.bold('  Symbiote-OS Orchestrator (Venom)'));
  console.log(chalk.green.bold('======================================='));
  console.log(chalk.gray(`  ${new Date().toISOString()}`));
  console.log(chalk.blue(`  Orchestrator: http://${HOST}:${PORT}`));
  console.log(chalk.blue(`  Frontend:     http://localhost:5173`));
  console.log(chalk.blue(`  llama.cpp:    ${LLAMACPP_URL} (host service)`));
  console.log(chalk.blue(`  Hive:         ${HIVE_ROOT}`));
  console.log();
  console.log(chalk.gray('  Endpoints:'));
  console.log(chalk.gray('    GET  /api/health       — health check (includes llama.cpp)'));
  console.log(chalk.gray('    GET  /api/info         — orchestrator info'));
  console.log(chalk.gray('    GET  /api/hive         — Hive cage structure'));
  console.log(chalk.gray('    GET  /api/hive/:path   — read file from Hive (ACL-enforced)'));
  console.log(chalk.gray('    POST /api/hive/:path/write — write file to Hive (ACL-enforced)'));
  console.log(chalk.gray('    GET  /api/acl/check   — check path access decision'));
  console.log(chalk.gray('    GET  /api/brain-state  — brain-state.json'));
  console.log(chalk.gray('    GET  /api/chats        — chat history'));
  console.log(chalk.gray('    POST /api/chats        — save chat entry'));
  console.log(chalk.gray('    GET  /api/carnage      — audit log'));
  console.log(chalk.gray('    GET  /api/llm/health   — llama.cpp health'));
  console.log(chalk.gray('    GET  /api/llm/models   — llama.cpp models'));
  console.log(chalk.gray('    POST /api/llm/chat     — llama.cpp chat (proxied)'));
  console.log();
  console.log(chalk.green('  🔒 Carnage ACL initialized — Business-Private cage enforced'));
  console.log();
});
