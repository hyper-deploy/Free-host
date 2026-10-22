import os
import subprocess
import threading
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/neohost_cluster"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bots_registry = {}
bot_logs = {}

def run_bot_process(bot_id, file_path, filename):
    bot_logs[bot_id] = [f"[{filename}] Initializing runtime environment..."]
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
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
            
        req_path = os.path.join(os.path.dirname(file_path), "requirements.txt")
        if os.path.exists(req_path):
            bot_logs[bot_id].append("Found requirements.txt, installing dependencies...")
            subprocess.run(["pip", "install", "-r", req_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
        if detected_pkgs:
            bot_logs[bot_id].append(f"Installing packages: {', '.join(detected_pkgs)}...")
            subprocess.run(["pip", "install", "--prefer-binary"] + detected_pkgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            bot_logs[bot_id].append("Dependencies installed successfully ✓")
            
        bot_logs[bot_id].append(f"Starting process for {filename}...")
        process = subprocess.Popen(
            ["python", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        bots_registry[bot_id]["process"] = process
        bots_registry[bot_id]["status"] = "running"
        bot_logs[bot_id].append("Bot is now LIVE & Running ✓")
        
        for line in process.stdout:
            msg = line.strip()
            if msg:
                bot_logs[bot_id].append(msg)
                if len(bot_logs[bot_id]) > 400:
                    bot_logs[bot_id].pop(0)
                    
    except Exception as e:
        bot_logs[bot_id].append(f"Error: {str(e)}")
        if bot_id in bots_registry:
            bots_registry[bot_id]["status"] = "stopped"
    finally:
        if bot_id in bots_registry and bots_registry[bot_id]["process"] and bots_registry[bot_id]["process"].poll() is not None:
            bots_registry[bot_id]["status"] = "stopped"


# ====================================================
# APP-STYLE RESPONSIVE NEON GLOWING PANEL UI
# ====================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<title>NeoHost — App Panel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

:root {
  --cyan: #00f0ff; --magenta: #ff00e5; --purple: #7b2ff7; --green: #00ff88; --red: #ff3b6b; --yellow: #ffd60a;
  --bg: #030307; --bg-2: #070711; --card: rgba(255, 255, 255, 0.035); --card-hover: rgba(255, 255, 255, 0.07);
  --border: rgba(255, 255, 255, 0.09); --border-glow: rgba(0, 240, 255, 0.5);
  --text: #e8e8f0; --muted: #8a8a9a; --muted-2: #5a5a6a;
  --radius: 16px; --font: 'Inter', sans-serif; --mono: 'JetBrains Mono', monospace;
}

body { font-family: var(--font); background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; line-height: 1.5; }
::selection { background: var(--cyan); color: #000; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--cyan), var(--purple)); border-radius: 10px; }

/* Background FX & Rotating Chakra Ring */
.bg-fx { position: fixed; inset: 0; z-index: -2; overflow: hidden; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.25; }
.orb-1 { width: 400px; height: 400px; background: var(--cyan); top: -100px; left: -100px; }
.orb-2 { width: 350px; height: 350px; background: var(--magenta); bottom: -100px; right: -100px; }

.chakra-ring {
  width: 36px; height: 36px; border-radius: 50%;
  background: conic-gradient(from 0deg, var(--cyan), var(--magenta), var(--purple), var(--green), var(--cyan));
  display: grid; place-items: center; padding: 2px;
  animation: spinChakra 2.5s linear infinite;
  box-shadow: 0 0 20px rgba(0,240,255,0.7), inset 0 0 10px rgba(255,0,229,0.5);
}
.chakra-inner { width: 100%; height: 100%; background: var(--bg); border-radius: 50%; display: grid; place-items: center; font-size: 13px; font-weight: 900; color: var(--cyan); }
@keyframes spinChakra { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* App Header */
nav {
  position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between;
  padding: 12px 20px; backdrop-filter: blur(20px); background: rgba(3,3,7,0.85); border-bottom: 1px solid var(--border);
}
.logo { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.1rem; text-decoration: none; color: var(--text); }
.logo span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 15px rgba(0,240,255,0.4); }

.btn-deploy {
  padding: 8px 16px; border-radius: 10px; font-size: 0.8rem; font-weight: 700;
  background: linear-gradient(135deg, var(--cyan), var(--purple)); color: #000; border: none; cursor: pointer;
  box-shadow: 0 0 15px rgba(0,240,255,0.4); transition: 0.2s;
}
.btn-deploy:active { transform: scale(0.95); }

/* Main App Container (Responsive: Mobile APK style vs PC Dashboard) */
.app-container { max-width: 1200px; margin: 20px auto; padding: 0 16px; }

/* Stats Bar */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px; }
.stat-box { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 14px 10px; text-align: center; backdrop-filter: blur(10px); position: relative; overflow: hidden; }
.stat-box::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--cyan); }
.stat-box.running::before { background: var(--green); box-shadow: 0 0 10px var(--green); }
.stat-box.stopped::before { background: var(--red); box-shadow: 0 0 10px var(--red); }
.stat-title { font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-family: var(--mono); }
.stat-value { font-size: 1.4rem; font-weight: 800; font-family: var(--mono); text-shadow: 0 0 10px rgba(255,255,255,0.2); }

/* Panels Grid */
.panels-grid { display: grid; grid-template-columns: 1fr 1.3fr; gap: 16px; align-items: start; }
@media(max-width: 850px) { .panels-grid { grid-template-columns: 1fr; } }

.app-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; backdrop-filter: blur(10px); box-shadow: 0 10px 30px rgba(0,0,0,0.6); margin-bottom: 16px; }
.app-card-header { padding: 14px 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-weight: 700; font-size: 0.9rem; }

/* Dropzone */
.dropzone { border: 2px dashed rgba(0,240,255,0.4); border-radius: 12px; padding: 30px 15px; text-align: center; cursor: pointer; transition: 0.3s; margin: 16px; background: rgba(0,240,255,0.03); }
.dropzone:active { background: rgba(0,240,255,0.1); }

/* Bot List Rows (App style) */
.bots-list { max-height: 380px; overflow-y: auto; }
.bot-row { display: flex; align-items: center; justify-content: space-between; padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); }
.bot-info { display: flex; align-items: center; gap: 12px; min-width: 0; }
.bot-icon { width: 36px; height: 36px; border-radius: 10px; background: rgba(0,240,255,0.12); border: 1px solid rgba(0,240,255,0.4); display: grid; place-items: center; font-family: var(--mono); font-weight: 700; color: var(--cyan); box-shadow: 0 0 10px rgba(0,240,255,0.3); }
.bot-title { font-weight: 600; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 130px; }
.badge { font-size: 0.6rem; font-weight: 700; padding: 2px 8px; border-radius: 100px; font-family: var(--mono); text-transform: uppercase; }
.badge.running { background: rgba(0,255,136,0.15); color: var(--green); border: 1px solid rgba(0,255,136,0.4); box-shadow: 0 0 8px rgba(0,255,136,0.3); }
.badge.stopped { background: rgba(255,59,107,0.15); color: var(--red); border: 1px solid rgba(255,59,107,0.4); box-shadow: 0 0 8px rgba(255,59,107,0.3); }

/* Glowing Action Buttons */
.act-btn { padding: 6px 10px; border-radius: 8px; font-size: 0.7rem; font-weight: 600; cursor: pointer; border: 1px solid var(--border); background: var(--card); color: var(--text); transition: 0.2s; display: inline-flex; align-items: center; gap: 4px; }
.act-btn:active { transform: scale(0.92); }
.act-btn.start { border-color: rgba(0,255,136,0.5); color: var(--green); }
.act-btn.start:active { background: rgba(0,255,136,0.25); box-shadow: 0 0 12px var(--green); }
.act-btn.stop { border-color: rgba(255,214,10,0.5); color: var(--yellow); }
.act-btn.stop:active { background: rgba(255,214,10,0.25); box-shadow: 0 0 12px var(--yellow); }
.act-btn.logs { border-color: rgba(0,240,255,0.5); color: var(--cyan); }
.act-btn.logs:active { background: rgba(0,240,255,0.25); box-shadow: 0 0 12px var(--cyan); }
.act-btn.del { border-color: rgba(255,59,107,0.5); color: var(--red); }
.act-btn.del:active { background: rgba(255,59,107,0.25); box-shadow: 0 0 12px var(--red); }

/* Terminal Logs Console */
.terminal-box { background: #020205; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.8); margin-top: 16px; }
.terminal-head { padding: 12px 16px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-family: var(--mono); font-size: 0.78rem; }
.terminal-body { height: 260px; overflow-y: auto; padding: 14px; font-family: var(--mono); font-size: 0.72rem; line-height: 1.6; color: var(--green); text-shadow: 0 0 6px rgba(0,255,136,0.4); }
.t-line { word-break: break-word; margin-bottom: 3px; }

footer { padding: 30px; text-align: center; color: var(--muted); font-size: 0.78rem; }
</style>
</head>
<body>

<div class="bg-fx"><div class="orb orb-1"></div><div class="orb orb-2"></div></div>

<nav>
  <div class="logo">
    <div class="chakra-ring"><div class="chakra-inner">N</div></div>
    Neo<span>Host</span> APK
  </div>
  <button class="btn-deploy" onclick="triggerUpload()">+ Upload Bot</button>
</nav>

<div class="app-container">
  
  <!-- Stats Bar -->
  <div class="stats-grid">
    <div class="stat-box">
      <div class="stat-title">Total</div>
      <div class="stat-value" id="statTotal">0</div>
    </div>
    <div class="stat-box running">
      <div class="stat-title">Running</div>
      <div class="stat-value" id="statRunning" style="color:var(--green)">0</div>
    </div>
    <div class="stat-box stopped">
      <div class="stat-title">Offline</div>
      <div class="stat-value" id="statStopped" style="color:var(--red)">0</div>
    </div>
  </div>

  <!-- Panels Grid -->
  <div class="panels-grid">
    
    <!-- Upload Panel -->
    <div class="app-card">
      <div class="app-card-header">📥 Deploy Project</div>
      <div class="dropzone" id="dropzone">
        <div style="font-size:32px; margin-bottom:8px; filter: drop-shadow(0 0 10px rgba(0,240,255,0.5));">📦</div>
        <h4 style="font-size:0.88rem; margin-bottom:4px;">Tap to Upload <span style="color:var(--cyan)">.py</span></h4>
        <p style="font-size:0.7rem; color:var(--muted)">Supports requirements.txt</p>
        <input type="file" id="fileInput" accept=".py,.txt" multiple hidden />
      </div>
    </div>

    <!-- Active Fleet Manager -->
    <div class="app-card">
      <div class="app-card-header">
        <span>🤖 Active Fleet</span>
        <button class="act-btn logs" onclick="fetchBotsData()">🔄 Refresh</button>
      </div>
      <div class="bots-list" id="botsListContainer">
        <div style="padding: 40px; text-align: center; color: var(--muted); font-size: 0.8rem;">No bots running.</div>
      </div>
    </div>

  </div>

  <!-- Dedicated Bottom Logs Monitor -->
  <div class="terminal-box" id="monitor">
    <div class="terminal-head">
      <span id="activeLogTitle" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:220px;">📡 Console: Select bot</span>
      <button class="act-btn stop" onclick="clearLogs()">Clear</button>
    </div>
    <div class="terminal-body" id="logsConsoleBody">
      <div class="t-line" style="color:var(--cyan)">[neohost-app] Ready. Tap 'Logs' on any bot to monitor stream.</div>
    </div>
  </div>

</div>

<footer>
  <p>© 2026 NeoHost Mobile Cloud Panel</p>
</footer>

<script>
let viewingBotId = null;

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const botsListContainer = document.getElementById('botsListContainer');
const logsConsoleBody = document.getElementById('logsConsoleBody');
const activeLogTitle = document.getElementById('activeLogTitle');

dropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', e => {
  if (e.target.files.length) {
    uploadFiles(e.target.files);
    fileInput.value = '';
  }
});

function triggerUpload() {
  fileInput.click();
}

function uploadFiles(files) {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append('files', files[i]);
  }

  fetch('/api/deploy', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    if(data.status === 'success') {
      fetchBotsData();
    } else {
      alert("Deploy Error: " + data.message);
    }
  });
}

function fetchBotsData() {
  fetch('/api/bots')
  .then(res => res.json())
  .then(data => {
    const bots = data.bots || {};
    let total = 0, running = 0, stopped = 0;
    let html = '';

    const entries = Object.entries(bots);
    if(entries.length === 0) {
      botsListContainer.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--muted); font-size: 0.8rem;">No bots running.</div>`;
      return;
    }

    entries.forEach(([id, bot]) => {
      total++;
      if(bot.status === 'running') running++; else stopped++;

      html += `
        <div class="bot-row">
          <div class="bot-info">
            <div class="bot-icon">${bot.name.charAt(0).toUpperCase()}</div>
            <div>
              <div class="bot-title" title="${bot.name}">${bot.name}</div>
              <div style="margin-top:2px;"><span class="badge ${bot.status}">${bot.status}</span></div>
            </div>
          </div>
          <div style="display: flex; gap: 4px; flex-wrap: wrap;">
            ${bot.status === 'stopped' ? `<button class="act-btn start" onclick="controlBot('${id}', 'start')">▶</button>` : `<button class="act-btn stop" onclick="controlBot('${id}', 'stop')">⏹</button>`}
            <button class="act-btn logs" onclick="selectBotLogs('${id}', '${bot.name}')">📜</button>
            <button class="act-btn del" onclick="controlBot('${id}', 'delete')">🗑</button>
          </div>
        </div>
      `;
    });

    botsListContainer.innerHTML = html;
    document.getElementById('statTotal').textContent = total;
    document.getElementById('statRunning').textContent = running;
    document.getElementById('statStopped').textContent = stopped;
  });
}

function controlBot(id, action) {
  fetch(`/api/bot/${id}/${action}`, { method: 'POST' })
  .then(res => res.json())
  .then(data => {
    if(action === 'delete' && viewingBotId === id) {
      viewingBotId = null;
      activeLogTitle.textContent = "📡 Console: Select bot";
      logsConsoleBody.innerHTML = `<div class="t-line" style="color:var(--cyan)">[neohost] Bot deleted.</div>`;
    }
    fetchBotsData();
  });
}

function selectBotLogs(id, name) {
  viewingBotId = id;
  activeLogTitle.textContent = `📡 Logs: ${name}`;
  logsConsoleBody.innerHTML = `<div class="t-line">Loading logs...</div>`;
}

function clearLogs() {
  logsConsoleBody.innerHTML = `<div class="t-line" style="color:var(--cyan)">Console cleared.</div>`;
}

setInterval(() => {
  fetchBotsData();
  if(viewingBotId) {
    fetch(`/api/logs/${viewingBotId}`)
    .then(res => res.json())
    .then(data => {
      if(data.logs && data.logs.length) {
        logsConsoleBody.innerHTML = data.logs.map(l => `<div class="t-line">› ${l}</div>`).join('');
        logsConsoleBody.scrollTop = logsConsoleBody.scrollHeight;
      }
    });
  }
}, 2500);

window.onload = fetchBotsData;
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/deploy", methods=["POST"])
def deploy():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"status": "error", "message": "No files uploaded"})
    
    session_dir = os.path.join(UPLOAD_FOLDER, "session_" + os.urandom(3).hex())
    os.makedirs(session_dir, exist_ok=True)
    
    py_files = []
    for f in files:
        if f.filename:
            f_path = os.path.join(session_dir, f.filename)
            f.save(f_path)
            if f.filename.endswith('.py'):
                py_files.append((f.filename, f_path))
                
    if not py_files:
        return jsonify({"status": "error", "message": "No .py script found"})
        
    for filename, filepath in py_files:
        bot_id = "bot_" + os.urandom(3).hex()
        bots_registry[bot_id] = {
            "name": filename,
            "status": "running",
            "process": None,
            "file_path": filepath
        }
        t = threading.Thread(target=run_bot_process, args=(bot_id, filepath, filename), daemon=True)
        t.start()
        
    return jsonify({"status": "success"})

@app.route("/api/bots")
def get_bots():
    summary = {}
    for bid, info in bots_registry.items():
        status = info["status"]
        if info["process"] and info["process"].poll() is not None:
            status = "stopped"
            info["status"] = "stopped"
        summary[bid] = {
            "name": info["name"],
            "status": status
        }
    return jsonify({"bots": summary})

@app.route("/api/bot/<bot_id>/<action>", methods=["POST"])
def bot_action(bot_id, action):
    if bot_id not in bots_registry:
        return jsonify({"status": "error"})
        
    info = bots_registry[bot_id]
    if action == "stop":
        if info["process"]:
            try:
                info["process"].terminate()
            except:
                pass
        info["status"] = "stopped"
    elif action == "start":
        t = threading.Thread(target=run_bot_process, args=(bot_id, info["file_path"], info["name"]), daemon=True)
        t.start()
    elif action == "delete":
        if info["process"]:
            try:
                info["process"].terminate()
            except:
                pass
        bots_registry.pop(bot_id, None)
        bot_logs.pop(bot_id, None)
        
    return jsonify({"status": "success"})

@app.route("/api/logs/<bot_id>")
def get_logs(bot_id):
    return jsonify({"logs": bot_logs.get(bot_id, ["No logs available yet..."])})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
