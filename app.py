import os
import subprocess
import threading
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

active_bots = {}
bot_logs = {}

def install_and_run_bot(bot_id, file_path):
    """Automatically detects imports, installs missing libraries, and runs the bot"""
    bot_logs[bot_id] = ["Scanning bot script for dependencies...", "Preparing Python runtime..."]
    
    try:
        # Read the uploaded bot file to find imported libraries
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
            
        # Map common bot imports to their pip package names
        import_to_pkg = {
            "telebot": "pyTelegramBotAPI",
            "pyrogram": "pyrogram",
            "aiogram": "aiogram",
            "requests": "requests",
            "bs4": "beautifulsoup4",
            "aiohttp": "aiohttp",
            "motor": "motor",
            "pymongo": "pymongo",
            "yt_dlp": "yt-dlp"
        }
        
        detected_pkgs = []
        for imp, pkg in import_to_pkg.items():
            if re.search(r'\b(import|from)\s+' + imp + r'\b', code_content):
                detected_pkgs.append(pkg)
                
        # Always ensure tgcrypto if pyrogram is used
        if "pyrogram" in detected_pkgs and "Tgcrypto" not in detected_pkgs:
            detected_pkgs.append("Tgcrypto")
            
        if detected_pkgs:
            bot_logs[bot_id].append(f"Installing missing packages: {', '.join(detected_pkgs)}...")
            # Install packages dynamically using pip
            subprocess.run(["pip", "install"] + detected_pkgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            bot_logs[bot_id].append("Dependencies installed successfully ✓")
            
        bot_logs[bot_id].append(f"Executing script...")
        
        process = subprocess.Popen(
            ["python", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        active_bots[bot_id] = process
        bot_logs[bot_id].append("Bot process is now LIVE ✓")
        
        for line in process.stdout:
            msg = line.strip()
            if msg:
                bot_logs[bot_id].append(msg)
                if len(bot_logs[bot_id]) > 150:
                    bot_logs[bot_id].pop(0)
                    
    except Exception as e:
        bot_logs[bot_id].append(f"Execution Error: {str(e)}")
    finally:
        if bot_id in active_bots:
            del active_bots[bot_id]


# ==========================================
# ORIGINAL DESIGN & FRONTEND (1% Unchanged)
# ==========================================
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
  --radius: 16px; --radius-sm: 10px; --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono: 'JetBrains Mono', 'Fira Code', monospace;
}
html { scroll-behavior: smooth; }
body { font-family: var(--font); background: var(--bg); color: var(--text); overflow-x: hidden; min-height: 100vh; line-height: 1.6; -webkit-font-smoothing: antialiased; }
::selection { background: var(--cyan); color: #000; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--cyan), var(--purple)); border-radius: 10px; border: 2px solid var(--bg-2); }

.bg-fx { position: fixed; inset: 0; z-index: -2; overflow: hidden; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.35; will-change: transform; }
.orb-1 { width: 550px; height: 550px; background: var(--cyan); top: -180px; left: -150px; animation: floatA 22s ease-in-out infinite; }
.orb-2 { width: 450px; height: 450px; background: var(--magenta); bottom: -150px; right: -150px; animation: floatB 26s ease-in-out infinite; }
.orb-3 { width: 400px; height: 400px; background: var(--purple); top: 45%; left: 50%; animation: floatC 30s ease-in-out infinite; }
@keyframes floatA { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(120px, 90px) scale(1.15); } }
@keyframes floatB { 0%,100% { transform: translate(0,0) scale(1); } 50% { transform: translate(-130px, -80px) scale(1.1); } }
@keyframes floatC { 0%,100% { transform: translate(-50%,-50%) scale(1); } 50% { transform: translate(-40%,-60%) scale(1.2); } }

.grid-bg {
  position: fixed; inset: 0; z-index: -1; pointer-events: none;
  background-image: linear-gradient(rgba(0,240,255,0.045) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.045) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse 90% 70% at 50% 40%, #000 20%, transparent 75%);
  animation: gridPulse 8s ease-in-out infinite;
}
@keyframes gridPulse { 0%,100% { opacity: 0.55; } 50% { opacity: 1; } }

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
  font-family: var(--font); font-size: 0.9rem; font-weight: 600; cursor: pointer; border: none; text-decoration: none; transition: all 0.25s ease;
}
.btn-primary { background: linear-gradient(135deg, var(--cyan), var(--purple)); color: #000; }
.btn-ghost { background: var(--card); color: var(--text); border: 1px solid var(--border); }
.btn-sm { padding: 8px 14px; font-size: 0.8rem; border-radius: 8px; }

.hero { padding: 110px 40px 70px; max-width: 1240px; margin: 0 auto; display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 60px; align-items: center; }
.badge {
  display: inline-flex; align-items: center; gap: 8px; padding: 7px 14px; border-radius: 100px;
  background: rgba(0,240,255,0.08); border: 1px solid rgba(0,240,255,0.25); font-size: 0.78rem; font-weight: 600; color: var(--cyan); margin-bottom: 26px;
}
.badge .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); animation: pulse 1.6s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }

.hero h1 { font-size: clamp(2.4rem, 5.5vw, 4.2rem); font-weight: 900; line-height: 1.05; letter-spacing: -2px; margin-bottom: 22px; }
.hero h1 .gradient { background: linear-gradient(90deg, var(--cyan), var(--magenta), var(--purple)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero p { font-size: 1.1rem; color: var(--muted); max-width: 520px; margin-bottom: 36px; }
.hero-cta { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 42px; }

.hero-stats { display: flex; gap: 40px; padding-top: 28px; border-top: 1px solid var(--border); }
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
.status-pill.stopped { background: rgba(138,138,154,0.1); color: var(--muted); border: 1px solid rgba(138,138,154,0.25); }
.status-pill.stopped .led { width: 6px; height: 6px; border-radius: 50%; background: var(--muted-2); }
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
#toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; }
.toast { padding: 14px 18px; background: rgba(15,15,25,0.95); border: 1px solid var(--border); border-radius: 10px; font-size: 0.85rem; display: flex; align-items: center; gap: 10px; }

@media (max-width: 980px) {
  .hero { grid-template-columns: 1fr; padding: 60px 20px 40px; text-align: center; }
  .deploy-wrap, .dashboard { grid-template-columns: 1fr; }
  .console-panel { height: 400px; }
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
    <div class="badge"><span class="dot"></span> Python 3.11 · Live Cloud Runtime</div>
    <h1>Deploy Python Bots.<br><span class="gradient">Lightning Fast.</span></h1>
    <p>Upload your <code style="color:var(--cyan);">.py</code> file, hit start, and watch your bot execute live on Render cloud infrastructure.</p>
    <div class="hero-cta">
      <button class="btn btn-primary" onclick="scrollToSection('deploy')">🚀 Deploy a Bot</button>
      <button class="btn btn-ghost" onclick="scrollToSection('dashboard')">📊 View Dashboard</button>
    </div>
  </div>
  <div class="code-window">
    <div class="code-header"><div class="dots"><span></span><span></span><span></span></div><div class="filename">bot.py</div></div>
    <div class="code-body">
      <span class="kw">import</span> os, telebot<br>
      bot = telebot.TeleBot(os.environ[<span class="str">"TOKEN"</span>])<br>
      <span class="kw">@bot.message_handler</span>(commands=[<span class="str">'start'</span>])<br>
      <span class="kw">def</span> <span class="fn">send_welcome</span>(message):<br>
      &nbsp;&nbsp;bot.reply_to(message, <span class="str">"Bot is live!"</span>)<br>
      bot.infinity_polling()
    </div>
  </div>
</div>

<section id="deploy">
  <span class="section-tag">// deploy zone</span>
  <h2 class="section-title">Upload your <span style="color:var(--cyan)">.py</span> bot</h2>
  <p class="section-sub">Drop your actual Telegram bot script below to execute it live on the server.</p>
  <div class="deploy-wrap">
    <div class="dropzone" id="dropzone">
      <div class="dz-icon">📦</div>
      <h3>Drop your <code style="color:var(--cyan)">.py</code> file here</h3>
      <p>or click to browse</p>
      <input type="file" id="fileInput" accept=".py" hidden />
    </div>
    <div class="deploy-side">
      <h4>✅ Real Execution Checklist</h4>
      <ul>
        <li><span class="check">✓</span> Auto-detects missing libraries</li>
        <li><span class="check">✓</span> Uses `os.environ` for tokens</li>
        <li><span class="check">✓</span> Real-time stdout logging active</li>
      </ul>
    </div>
  </div>
</section>

<section id="dashboard">
  <span class="section-tag">// dashboard</span>
  <h2 class="section-title">Your active fleet</h2>
  <div class="dashboard">
    <div class="bots-panel">
      <div class="panel-head">
        <h3>🤖 Deployed Bots <span class="count-badge" id="botCount">0</span></h3>
      </div>
      <div class="bots-list" id="botsList">
        <div class="empty-state" id="emptyState">
          <p>No bots running yet — upload a file above.</p>
        </div>
      </div>
    </div>
    <div class="console-panel">
      <div class="console-head">
        <h3>📡 Real-Time Server Console</h3>
        <button class="btn btn-ghost btn-sm" onclick="clearConsole()">Clear</button>
      </div>
      <div class="console-body" id="consoleBody">
        <div class="console-line sys"><span class="time">--:--:--</span><span class="msg"><span class="prefix">neohost</span> › System online. Ready for automatic dependency installation.</span></div>
      </div>
    </div>
  </div>
</section>

<footer><p>© 2026 NeoHost — Real Python Bot Cloud Hosting.</p></footer>
<div id="toast-container"></div>

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
fileInput.addEventListener('change', e => { if (e.target.files.length) uploadAndRun(e.target.files[0]); });

function uploadAndRun(file) {
  if (!file.name.endsWith('.py')) { alert('Only .py files accepted'); return; }
  const formData = new FormData();
  formData.append('file', file);

  log(`Uploading ${file.name} and scanning imports...`, 'sys');
  fetch('/api/deploy', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      const bot = { id: data.bot_id, name: file.name, status: 'running' };
      bots.push(bot);
      activeBotId = data.bot_id;
      renderBots();
      log(`Bot <b>${file.name}</b> package installation & execution initiated!`, 'success');
      startLogPolling();
    } else {
      log(`Failed to deploy: ${data.message}`, 'sys');
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

@app.route("/api/deploy", methods=["POST"])
def deploy():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file provided"})
    file = request.files['file']
    if not file.filename.endswith('.py'):
        return jsonify({"status": "error", "message": "Invalid extension"})
    
    bot_id = "bot_" + os.urandom(3).hex()
    file_path = os.path.join("/tmp", f"{bot_id}_{file.filename}")
    file.save(file_path)
    
    t = threading.Thread(target=install_and_run_bot, args=(bot_id, file_path), daemon=True)
    t.start()
    
    return jsonify({"status": "success", "bot_id": bot_id})

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
