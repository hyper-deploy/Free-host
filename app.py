import os
import subprocess
import threading
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Multi-hosting storage
UPLOAD_FOLDER = "/tmp/neohost_bots"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

active_bots = {}
bot_logs = {}

def install_and_run_bot(bot_id, bot_dir, main_filename):
    """Handles multi-file hosting, dependency scanning, and live execution"""
    bot_logs[bot_id] = ["Initializing Multi-Hosting Environment...", "Scanning uploaded files and dependencies..."]
    
    try:
        main_file_path = os.path.join(bot_dir, main_filename)
        
        # Read main script to find imports
        with open(main_file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
            
        module_to_pkg = {
            "telegram": "python-telegram-bot",
            "telebot": "pyTelegramBotAPI",
            "pyrogram": "pyrogram",
            "aiogram": "aiogram",
            "requests": "requests",
            "bs4": "beautifulsoup4",
            "aiohttp": "aiohttp",
            "motor": "motor",
            "pymongo": "pymongo",
            "yt_dlp": "yt-dlp",
            "PIL": "Pillow",
            "openai": "openai",
            "gtts": "gtts",
            "psutil": "psutil"
        }
        
        detected_pkgs = []
        for mod, pkg in module_to_pkg.items():
            if re.search(r'\b(import|from)\s+' + mod + r'\b', code_content):
                detected_pkgs.append(pkg)
                
        if "pyrogram" in detected_pkgs and "Tgcrypto" not in detected_pkgs:
            detected_pkgs.append("Tgcrypto")
            
        if detected_pkgs:
            bot_logs[bot_id].append(f"Installing packages: {', '.join(detected_pkgs)}...")
            subprocess.run(["pip", "install", "--prefer-binary"] + detected_pkgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            bot_logs[bot_id].append("All packages ready ✓")
            
        bot_logs[bot_id].append(f"Launching multi-hosted bot: {main_filename}...")
        
        # Run process inside the specific bot directory so relative files/configs work seamlessly
        process = subprocess.Popen(
            ["python", main_filename],
            cwd=bot_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        active_bots[bot_id] = process
        bot_logs[bot_id].append("Multi-Bot process is now LIVE ✓")
        
        for line in process.stdout:
            msg = line.strip()
            if msg:
                bot_logs[bot_id].append(msg)
                if len(bot_logs[bot_id]) > 250:
                    bot_logs[bot_id].pop(0)
                    
    except Exception as e:
        bot_logs[bot_id].append(f"Execution Error: {str(e)}")
    finally:
        if bot_id in active_bots:
            del active_bots[bot_id]


# ====================================================
# 100% ORIGINAL DESIGN + MULTI-HOSTING SUPPORT
# ====================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>NeoHost — Deploy Python Bots at Light Speed</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --cyan: #00f0ff; --magenta: #ff00e5; --purple: #7b2ff7; --green: #00ff88; --red: #ff3b6b; --yellow: #ffd60a;
  --bg: #05050a; --bg-2: #0a0a14; --card: rgba(255, 255, 255, 0.035); --card-hover: rgba(255, 255, 255, 0.06);
  --border: rgba(255, 255, 255, 0.08); --border-glow: rgba(0, 240, 255, 0.35);
  --text: #e8e8f0; --muted: #8a8a9a; --muted-2: #5a5a6a;
  --radius: 16px; --radius-sm: 10px; --font: 'Inter', sans-serif; --mono: 'JetBrains Mono', monospace;
}

html { scroll-behavior: smooth; }
body { font-family: var(--font); background: var(--bg); color: var(--text); overflow-x: hidden; min-height: 100vh; line-height: 1.6; }
::selection { background: var(--cyan); color: #000; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--cyan), var(--purple)); border-radius: 10px; border: 2px solid var(--bg-2); }

.bg-fx { position: fixed; inset: 0; z-index: -2; overflow: hidden; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.35; }
.orb-1 { width: 550px; height: 550px; background: var(--cyan); top: -180px; left: -150px; }
.orb-2 { width: 450px; height: 450px; background: var(--magenta); bottom: -150px; right: -150px; }
.orb-3 { width: 400px; height: 400px; background: var(--purple); top: 45%; left: 50%; }

.grid-bg {
  position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background-image: linear-gradient(rgba(0,240,255,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.045) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse 90% 70% at 50% 40%, #000 20%, transparent 75%);
}

nav {
  position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between;
  padding: 16px 40px; backdrop-filter: blur(20px); background: rgba(5,5,10,0.6); border-bottom: 1px solid var(--border);
}
.logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.25rem; text-decoration: none; color: var(--text); }
.logo-mark {
  width: 34px; height: 34px; border-radius: 10px; background: linear-gradient(135deg, var(--cyan), var(--purple), var(--magenta));
  display: grid; place-items: center; font-size: 18px; font-weight: 900; color: #000; box-shadow: 0 0 20px rgba(0,240,255,0.5);
}
.logo span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; }

.nav-links { display: flex; gap: 32px; list-style: none; }
.nav-links a { color: var(--muted); text-decoration: none; font-size: 0.9rem; font-weight: 500; transition: color 0.25s; }
.nav-links a:hover { color: var(--text); }

.btn {
  display: inline-flex; align-items: center; gap: 8px; padding: 11px 22px; border-radius: 10px;
  font-family: var(--font); font-size: 0.9rem; font-weight: 600; cursor: pointer; border: none; text-decoration: none; transition: all 0.25s ease; white-space: nowrap;
}
.btn-primary { background: linear-gradient(135deg, var(--cyan), var(--purple)); color: #000; }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,240,255,0.45); }
.btn-ghost { background: var(--card); color: var(--text); border: 1px solid var(--border); }
.btn-ghost:hover { background: var(--card-hover); border-color: var(--border-glow); }
.btn-sm { padding: 8px 14px; font-size: 0.8rem; border-radius: 8px; }

.hero { padding: 110px 40px 70px; max-width: 1240px; margin: 0 auto; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 60px; align-items: center; }
.badge {
  display: inline-flex; align-items: center; gap: 8px; padding: 7px 14px; border-radius: 100px;
  background: rgba(0,240,255,0.08); border: 1px solid rgba(0,240,255,0.25); font-size: 0.78rem; font-weight: 600; color: var(--cyan); margin-bottom: 26px;
}
.badge .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); }

.hero h1 { font-size: clamp(2.4rem, 5.5vw, 4.2rem); font-weight: 900; line-height: 1.05; letter-spacing: -2px; margin-bottom: 22px; }
.hero h1 .gradient { background: linear-gradient(90deg, var(--cyan), var(--magenta), var(--purple)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p { font-size: 1.1rem; color: var(--muted); max-width: 520px; margin-bottom: 36px; }
.hero-cta { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 42px; }

.hero-stats { display: flex; gap: 40px; flex-wrap: wrap; padding-top: 28px; border-top: 1px solid var(--border); }
.hero-stats .stat-num { font-size: 1.7rem; font-weight: 800; background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-stats .stat-label { font-size: 0.8rem; color: var(--muted); }

.code-window { background: linear-gradient(180deg, rgba(15,15,25,0.95), rgba(8,8,15,0.98)); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,0.6); }
.code-header { display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border); }
.code-header .dots { display: flex; gap: 6px; }
.code-header .dots span { width: 11px; height: 11px; border-radius: 50%; }
.code-header .dots span:nth-child(1) { background: #ff5f57; }
.code-header .dots span:nth-child(2) { background: #febc2e; }
.code-header .dots span:nth-child(3) { background: #28c840; }
.code-header .filename { margin-left: 8px; font-family: var(--mono); font-size: 0.78rem; color: var(--muted); }
.code-body { padding: 22px 20px; font-family: var(--mono); font-size: 0.82rem; line-height: 1.85; }
.kw { color: var(--magenta); } .fn { color: var(--cyan); } .str { color: var(--green); } .cm { color: var(--muted-2); }

section { padding: 90px 40px; max-width: 1240px; margin: 0 auto; }
.section-tag { font-family: var(--mono); font-size: 0.8rem; color: var(--cyan); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 14px; display: block; }
.section-title { font-size: clamp(1.8rem, 3.5vw, 2.7rem); font-weight: 800; letter-spacing: -1.5px; margin-bottom: 14px; }
.section-sub { color: var(--muted); max-width: 600px; margin-bottom: 50px; }

.features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
.feature-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 30px 26px; backdrop-filter: blur(10px); transition: 0.3s; }
.feature-card:hover { transform: translateY(-6px); border-color: var(--border-glow); background: var(--card-hover); }
.feature-icon { width: 48px; height: 48px; border-radius: 12px; display: grid; place-items: center; font-size: 22px; background: rgba(0,240,255,0.08); border: 1px solid rgba(0,240,255,0.2); margin-bottom: 20px; }
.feature-card h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }
.feature-card p { font-size: 0.9rem; color: var(--muted); }

.deploy-wrap { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 24px; align-items: start; }
.dropzone { background: var(--card); border: 2px dashed rgba(0,240,255,0.3); border-radius: var(--radius); padding: 60px 30px; text-align: center; cursor: pointer; transition: 0.3s; }
.dropzone:hover { border-color: var(--cyan); background: rgba(0,240,255,0.04); }
.dropzone .dz-icon { font-size: 48px; margin-bottom: 16px; display: inline-block; }
.deploy-side { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 26px; }
.deploy-side ul { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.deploy-side li { font-size: 0.86rem; color: var(--muted); display: flex; gap: 10px; }
.deploy-side li .check { color: var(--green); }

.dashboard { display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; align-items: start; }
.bots-panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
.panel-head { padding: 18px 22px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.count-badge { font-size: 0.72rem; padding: 2px 9px; border-radius: 100px; background: rgba(0,240,255,0.12); color: var(--cyan); font-family: var(--mono); }
.bots-list { max-height: 480px; overflow-y: auto; }
.empty-state { padding: 60px 30px; text-align: center; color: var(--muted); }
.bot-item { display: flex; align-items: center; gap: 16px; padding: 16px 22px; border-bottom: 1px solid rgba(255,255,255,0.04); }
.bot-icon { width: 42px; height: 42px; border-radius: 10px; display: grid; place-items: center; background: rgba(0,240,255,0.1); font-family: var(--mono); font-weight: 700; color: var(--cyan); }
.bot-info { flex: 1; min-width: 0; }
.bot-name { font-weight: 600; font-size: 0.92rem; }
.bot-meta { font-size: 0.75rem; color: var(--muted); font-family: var(--mono); display: flex; gap: 10px; margin-top: 4px; }
.status-pill { font-size: 0.72rem; font-weight: 600; padding: 4px 10px; border-radius: 100px; font-family: var(--mono); display: inline-flex; align-items: center; gap: 6px; }
.status-pill.running { background: rgba(0,255,136,0.1); color: var(--green); border: 1px solid rgba(0,255,136,0.3); }
.status-pill.running .led { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); }
.icon-btn { width: 36px; height: 36px; border-radius: 8px; border: 1px solid var(--border); background: rgba(255,255,255,0.03); cursor: pointer; color: var(--text); }

.console-panel { background: #07070d; border: 1px solid var(--border); border-radius: var(--radius); height: 560px; display: flex; flex-direction: column; }
.console-head { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
.console-body { flex: 1; overflow-y: auto; padding: 16px 18px; font-family: var(--mono); font-size: 0.78rem; line-height: 1.8; }
.console-line { display: flex; gap: 10px; word-break: break-word; }
.console-line .time { color: var(--muted-2); }
.console-line.success { color: var(--green); }
.console-line.sys { color: var(--cyan); }
.prefix { color: var(--purple); font-weight: 700; }

footer { border-top: 1px solid var(--border); padding: 50px 40px 30px; margin-top: 60px; text-align: center; color: var(--muted); font-size: 0.85rem; }

@media (max-width: 980px) {
  .hero { grid-template-columns: 1fr; padding: 60px 20px 40px; text-align: center; }
  .deploy-wrap, .dashboard { grid-template-columns: 1fr; }
  .console-panel { height: 400px; }
  .nav-links { display: none; }
}
</style>
</head>
<body>

<div class="bg-fx"><div class="orb orb-1"></div><div class="orb orb-2"></div><div class="orb orb-3"></div></div>
<div class="grid-bg"></div>

<nav>
  <a href="#" class="logo"><div class="logo-mark">N</div>Neo<span>Host</span></a>
  <ul class="nav-links">
    <li><a href="#features">Features</a></li>
    <li><a href="#deploy">Deploy</a></li>
    <li><a href="#dashboard">Dashboard</a></li>
  </ul>
  <button class="btn btn-primary" onclick="scrollToSection('deploy')">⚡ Get Started</button>
</nav>

<div class="hero">
  <div>
    <div class="badge"><span class="dot"></span> Python 3.11 · Multi-Hosting Runtime</div>
    <h1>Deploy Multiple Bots.<br><span class="gradient">Simultaneously.</span></h1>
    <p>Upload multiple Python files or project folders together. Run multiple Telegram bots at once on live cloud infrastructure.</p>
    <div class="hero-cta">
      <button class="btn btn-primary" onclick="scrollToSection('deploy')">🚀 Deploy Multi-Bots</button>
      <button class="btn btn-ghost" onclick="scrollToSection('dashboard')">📊 View Fleet</button>
    </div>
  </div>
  <div class="code-window">
    <div class="code-header"><div class="dots"><span></span><span></span><span></span></div><div class="filename">multi_bot.py</div></div>
    <div class="code-body">
      <span class="kw">import</span> asyncio, logging<br>
      <span class="cm"># Multi-hosting ready container</span><br>
      <span class="kw">async def</span> <span class="fn">main</span>():<br>
      &nbsp;&nbsp;<span class="kw">print</span>(<span class="str">"Running bot cluster..."</span>)<br>
      asyncio.<span class="fn">run</span>(main())
    </div>
  </div>
</div>

<section id="features">
  <span class="section-tag">// multi-hosting capability</span>
  <h2 class="section-title">Run multiple bots <br>without limitations.</h2>
  <p class="section-sub">Upload multiple files concurrently — each bot gets its own isolated multi-hosting process.</p>

  <div class="features-grid">
    <div class="feature-card">
      <div class="feature-icon">📂</div>
      <h3>Multi-File Upload</h3>
      <p>Select and send multiple .py files or custom configuration scripts at once.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">⚡</div>
      <h3>Simultaneous Run</h3>
      <p>Host several Telegram bots concurrently without interrupting each other.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">📡</div>
      <h3>Real-Time Logs</h3>
      <p>Switch between active bots to stream live stdout and debugging traces instantly.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">♾️</div>
      <h3>24/7 Cloud Power</h3>
      <p>Keep your bot cluster permanently online with zero downtime guarantees.</p>
    </div>
  </div>
</section>

<section id="deploy">
  <span class="section-tag">// multi-deploy zone</span>
  <h2 class="section-title">Upload your <span style="color:var(--cyan)">bot files</span></h2>
  <p class="section-sub">Select multiple files (or drag & drop them) to host and run them simultaneously.</p>
  <div class="deploy-wrap">
    <div class="dropzone" id="dropzone">
      <div class="dz-icon">📦</div>
      <h3>Drop your <code style="color:var(--cyan)">.py</code> files here</h3>
      <p>or click to select multiple files</p>
      <input type="file" id="fileInput" accept=".py,.txt,.env" multiple hidden />
    </div>
    <div class="deploy-side">
      <h4>✅ Multi-Hosting Checklist</h4>
      <ul>
        <li><span class="check">✓</span> Select multiple .py files together</li>
        <li><span class="check">✓</span> Auto-installs required python libraries</li>
        <li><span class="check">✓</span> Individual stop and monitor controls</li>
      </ul>
    </div>
  </div>
</section>

<section id="dashboard">
  <span class="section-tag">// dashboard</span>
  <h2 class="section-title">Your bot cluster</h2>
  <div class="dashboard">
    <div class="bots-panel">
      <div class="panel-head">
        <h3>🤖 Active Cluster <span class="count-badge" id="botCount">0</span></h3>
      </div>
      <div class="bots-list" id="botsList">
        <div class="empty-state" id="emptyState">
          <p>No bots running in cluster — upload files above.</p>
        </div>
      </div>
    </div>
    <div class="console-panel">
      <div class="console-head">
        <h3>📡 Cluster Console</h3>
        <button class="btn btn-ghost btn-sm" onclick="clearConsole()">Clear</button>
      </div>
      <div class="console-body" id="consoleBody">
        <div class="console-line sys"><span class="time">--:--:--</span><span class="msg"><span class="prefix">neohost</span> › Multi-Hosting runtime online.</span></div>
      </div>
    </div>
  </div>
</section>

<footer><p>© 2026 NeoHost — Multi-Hosting Python Bot Cloud.</p></footer>

<script>
const bots = [];
let activeBotId = null;
let logPollTimer = null;

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const botsList = document.getElementById('botsList');
const emptyState = document.getElementById('emptyState');
const botCount = document.getElementById('botCount');
const consoleBody = document.getElementById('consoleBody');

function scrollToSection(id) { document.getElementById(id).scrollIntoView({ behavior: 'smooth' }); }
function timeStr() { const d = new Date(); return [d.getHours(), d.getMinutes(), d.getSeconds()].map(n => String(n).padStart(2, '0')).join(':'); }

function log(msg, type = 'sys', source = 'neohost') {
  const line = document.createElement('div');
  line.className = `console-line ${type}`;
  line.innerHTML = `<span class="time">${timeStr()}</span><span class="msg"><span class="prefix">${source}</span> › ${msg}</span>`;
  consoleBody.appendChild(line);
  consoleBody.scrollTop = consoleBody.scrollHeight;
}
function clearConsole() { consoleBody.innerHTML = ''; log('Console cleared.', 'sys'); }

dropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => { if (e.target.files.length) uploadMultipleFiles(e.target.files); });

function uploadMultipleFiles(files) {
  const formData = new FormData();
  let mainPy = null;
  
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
    if (files[i].name.endsWith('.py') && !mainPy) {
      mainPy = files[i].name; // Pick first .py file as main runner
    }
  }

  if (!mainPy) {
    alert('Please include at least one .py file!');
    return;
  }

  log(`Uploading ${files.length} file(s) for multi-hosting...`, 'sys');
  fetch('/api/deploy-multi', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      data.bots.forEach(b => {
        bots.push(b);
        log(`Multi-Bot <b>${b.name}</b> deployed successfully! ID: ${b.id}`, 'success');
      });
      renderBots();
      if (data.bots.length > 0) {
        activeBotId = data.bots[data.bots.length - 1].id;
        startLogPolling();
      }
    } else {
      log(`Deployment failed: ${data.message}`, 'sys');
    }
  });
}

function renderBots() {
  botCount.textContent = bots.length;
  botsList.querySelectorAll('.bot-item').forEach(n => n.remove());
  if (bots.length === 0) { emptyState.style.display = 'block'; return; }
  emptyState.style.display = 'none';

  bots.forEach(bot => {
    const item = document.createElement('div');
    item.className = 'bot-item';
    item.innerHTML = `
      <div class="bot-icon">${bot.name.charAt(0).toUpperCase()}</div>
      <div class="bot-info">
        <div class="bot-name">${bot.name}</div>
        <div class="bot-meta"><span class="status-pill running"><span class="led"></span>RUNNING</span></div>
      </div>
      <button class="icon-btn" onclick="stopBot('${bot.id}')">⏹</button>
    `;
    botsList.appendChild(item);
  });
}

function stopBot(id) {
  fetch(`/api/stop/${id}`, { method: 'POST' }).then(() => {
    const idx = bots.findIndex(b => b.id === id);
    if (idx !== -1) bots.splice(idx, 1);
    renderBots();
    log(`Bot process terminated.`, 'sys');
  });
}

function startLogPolling() {
  if (logPollTimer) clearInterval(logPollTimer);
  logPollTimer = setInterval(() => {
    if (!activeBotId) return;
    fetch(`/api/logs/${activeBotId}`)
    .then(res => res.json())
    .then(data => {
      if (data.logs && data.logs.length) {
        consoleBody.innerHTML = '';
        data.logs.forEach(l => log(l, 'success', 'bot'));
      }
    });
  }, 2500);
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/deploy-multi", methods=["POST"])
def deploy_multi():
    uploaded_files = request.files.getlist("files")
    if not uploaded_files:
        return jsonify({"status": "error", "message": "No files provided"})
    
    bot_session_id = "cluster_" + os.urandom(3).hex()
    bot_dir = os.path.join(UPLOAD_FOLDER, bot_session_id)
    os.makedirs(bot_dir, exist_ok=True)
    
    saved_py_files = []
    for file in uploaded_files:
        if file.filename:
            file_path = os.path.join(bot_dir, file.filename)
            file.save(file_path)
            if file.filename.endswith('.py'):
                saved_py_files.append(file.filename)
                
    if not saved_py_files:
        return jsonify({"status": "error", "message": "No .py files found in selection"})
    
    deployed_response = []
    for py_file in saved_py_files:
        bot_id = "bot_" + os.urandom(4).hex()
        bot_logs[bot_id] = [f"Preparing multi-host for {py_file}..."]
        
        t = threading.Thread(target=install_and_run_bot, args=(bot_id, bot_dir, py_file), daemon=True)
        t.start()
        
        deployed_response.append({"id": bot_id, "name": py_file})
        
    return jsonify({"status": "success", "bots": deployed_response})

@app.route("/api/logs/<bot_id>")
def get_logs(bot_id):
    return jsonify({"logs": bot_logs.get(bot_id, [])})

@app.route("/api/stop/<bot_id>", methods=["POST"])
def stop_bot(bot_id):
    if bot_id in active_bots:
        try:
            active_bots[bot_id].terminate()
            del active_bots[bot_id]
        except:
            pass
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
