import os
import subprocess
import threading
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/neohost_cluster"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Centralized bot registry: {bot_id: {"name": filename, "status": "running"/"stopped", "process": proc, "file_path": path}}
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
            
        # Check requirements.txt if present in same dir
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
# ULTIMATE PREMIUM TELEGRAM HOST CONTROLLER PANEL UI
# ====================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>NeoHost — Telegram Bot Cloud Controller</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --cyan: #00f0ff; --magenta: #ff00e5; --purple: #7b2ff7; --green: #00ff88; --red: #ff3b6b; --yellow: #ffd60a;
  --bg: #030307; --bg-2: #070711; --card: rgba(255, 255, 255, 0.03); --card-hover: rgba(255, 255, 255, 0.055);
  --border: rgba(255, 255, 255, 0.08); --border-glow: rgba(0, 240, 255, 0.4);
  --text: #e8e8f0; --muted: #8a8a9a; --muted-2: #5a5a6a;
  --radius: 16px; --font: 'Inter', sans-serif; --mono: 'JetBrains Mono', monospace;
}

html { scroll-behavior: smooth; }
body { font-family: var(--font); background: var(--bg); color: var(--text); overflow-x: hidden; min-height: 100vh; line-height: 1.6; }
::selection { background: var(--cyan); color: #000; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--cyan), var(--purple)); border-radius: 10px; }

/* Background FX & Rotating Chakra Ring */
.bg-fx { position: fixed; inset: 0; z-index: -2; overflow: hidden; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(120px); opacity: 0.25; }
.orb-1 { width: 600px; height: 600px; background: var(--cyan); top: -200px; left: -200px; }
.orb-2 { width: 500px; height: 500px; background: var(--magenta); bottom: -200px; right: -200px; }

.chakra-ring {
  width: 38px; height: 38px; border-radius: 50%;
  background: conic-gradient(from 0deg, var(--cyan), var(--magenta), var(--purple), var(--green), var(--cyan));
  display: grid; place-items: center; padding: 2px;
  animation: spinChakra 3s linear infinite;
  box-shadow: 0 0 20px rgba(0,240,255,0.6);
}
.chakra-inner { width: 100%; height: 100%; background: var(--bg); border-radius: 50%; display: grid; place-items: center; font-size: 14px; font-weight: 900; color: var(--cyan); }
@keyframes spinChakra { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

nav {
  position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between;
  padding: 16px 40px; backdrop-filter: blur(20px); background: rgba(3,3,7,0.75); border-bottom: 1px solid var(--border);
}
.logo { display: flex; align-items: center; gap: 14px; font-weight: 800; font-size: 1.25rem; text-decoration: none; color: var(--text); }
.logo span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; }

.nav-links { display: flex; gap: 28px; list-style: none; }
.nav-links a { color: var(--muted); text-decoration: none; font-size: 0.88rem; font-weight: 500; transition: 0.25s; }
.nav-links a:hover { color: var(--cyan); text-shadow: 0 0 10px var(--cyan); }

.btn {
  display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; border-radius: 10px;
  font-family: var(--font); font-size: 0.88rem; font-weight: 600; cursor: pointer; border: none; text-decoration: none; transition: all 0.25s ease; white-space: nowrap;
}
.btn-primary { background: linear-gradient(135deg, var(--cyan), var(--purple)); color: #000; box-shadow: 0 0 15px rgba(0,240,255,0.3); }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 0 25px rgba(0,240,255,0.6); }
.btn-ghost { background: var(--card); color: var(--text); border: 1px solid var(--border); }
.btn-ghost:hover { background: var(--card-hover); border-color: var(--border-glow); color: var(--cyan); }

/* Glowing Interactive Buttons */
.action-btn {
  padding: 6px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; cursor: pointer; border: 1px solid var(--border); background: var(--card); color: var(--text); transition: 0.2s; display: inline-flex; align-items: center; gap: 5px;
}
.action-btn:hover { transform: scale(1.05); }
.action-btn.start { border-color: rgba(0,255,136,0.4); color: var(--green); }
.action-btn.start:hover { background: rgba(0,255,136,0.15); box-shadow: 0 0 12px var(--green); }
.action-btn.stop { border-color: rgba(255,214,10,0.4); color: var(--yellow); }
.action-btn.stop:hover { background: rgba(255,214,10,0.15); box-shadow: 0 0 12px var(--yellow); }
.action-btn.logs { border-color: rgba(0,240,255,0.4); color: var(--cyan); }
.action-btn.logs:hover { background: rgba(0,240,255,0.15); box-shadow: 0 0 12px var(--cyan); }
.action-btn.del { border-color: rgba(255,59,107,0.4); color: var(--red); }
.action-btn.del:hover { background: rgba(255,59,107,0.15); box-shadow: 0 0 12px var(--red); }

/* Main Stats & Controller Header */
.panel-container { max-width: 1240px; margin: 40px auto; padding: 0 30px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
.stat-box { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 22px 24px; backdrop-filter: blur(10px); position: relative; overflow: hidden; }
.stat-box::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--cyan); }
.stat-box.running::before { background: var(--green); }
.stat-box.stopped::before { background: var(--red); }
.stat-box.total::before { background: var(--purple); }
.stat-title { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; font-family: var(--mono); }
.stat-value { font-size: 2rem; font-weight: 800; font-family: var(--mono); }

/* Deploy & Manager Layout */
.controller-grid { display: grid; grid-template-columns: 1fr 1.3fr; gap: 24px; align-items: start; }
.card-panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; backdrop-filter: blur(10px); }
.card-header { padding: 18px 22px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-weight: 700; font-size: 1rem; }

.dropzone { border: 2px dashed rgba(0,240,255,0.3); border-radius: 12px; padding: 45px 20px; text-align: center; cursor: pointer; transition: 0.3s; margin: 20px; background: rgba(0,240,255,0.02); }
.dropzone:hover { border-color: var(--cyan); background: rgba(0,240,255,0.05); box-shadow: inset 0 0 20px rgba(0,240,255,0.1); }

.bots-table-wrap { max-height: 400px; overflow-y: auto; }
.bot-row { display: flex; align-items: center; justify-content: space-between; padding: 16px 22px; border-bottom: 1px solid rgba(255,255,255,0.04); transition: 0.2s; }
.bot-row:hover { background: var(--card-hover); }
.bot-details { display: flex; align-items: center; gap: 14px; min-width: 0; }
.bot-avatar { width: 38px; height: 38px; border-radius: 10px; background: rgba(0,240,255,0.1); border: 1px solid rgba(0,240,255,0.3); display: grid; place-items: center; font-family: var(--mono); font-weight: 700; color: var(--cyan); }
.bot-name { font-weight: 600; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px; }
.badge-status { font-size: 0.68rem; font-weight: 700; padding: 3px 9px; border-radius: 100px; font-family: var(--mono); text-transform: uppercase; }
.badge-status.running { background: rgba(0,255,136,0.12); color: var(--green); border: 1px solid rgba(0,255,136,0.3); }
.badge-status.stopped { background: rgba(255,59,107,0.12); color: var(--red); border: 1px solid rgba(255,59,107,0.3); }

/* Dedicated Bottom Logs Monitor */
.logs-container { margin-top: 30px; background: #05050a; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.8); }
.logs-header { padding: 14px 22px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-family: var(--mono); font-size: 0.85rem; }
.logs-body { height: 320px; overflow-y: auto; padding: 18px; font-family: var(--mono); font-size: 0.78rem; line-height: 1.7; color: var(--green); }
.log-line { word-break: break-word; margin-bottom: 4px; }

footer { border-top: 1px solid var(--border); padding: 40px; text-align: center; color: var(--muted); font-size: 0.85rem; margin-top: 60px; }

@media(max-width: 900px) {
  .controller-grid { grid-template-columns: 1fr; }
  nav { padding: 16px 20px; }
  .panel-container { padding: 0 15px; }
}
</style>
</head>
<body>

<div class="bg-fx"><div class="orb orb-1"></div><div class="orb orb-2"></div></div>

<nav>
  <div class="logo">
    <div class="chakra-ring"><div class="chakra-inner">N</div></div>
    Neo<span>Host</span> Panel
  </div>
  <ul class="nav-links">
    <li><a href="#controller">Cluster Hub</a></li>
    <li><a href="#monitor">Live Monitor</a></li>
  </ul>
  <button class="btn btn-primary" onclick="triggerUploadModal()">⚡ Deploy Bot</button>
</nav>

<div class="panel-container" id="controller">
  <!-- Top Stats Bar -->
  <div class="stats-grid">
    <div class="stat-box total">
      <div class="stat-title">// Total Deployed</div>
      <div class="stat-value" id="statTotal">0</div>
    </div>
    <div class="stat-box running">
      <div class="stat-title">// Running Bots</div>
      <div class="stat-value" id="statRunning" style="color:var(--green)">0</div>
    </div>
    <div class="stat-box stopped">
      <div class="stat-title">// Offline / Stopped</div>
      <div class="stat-value" id="statStopped" style="color:var(--red)">0</div>
    </div>
  </div>

  <!-- Controller Grid -->
  <div class="controller-grid">
    
    <!-- Upload Panel -->
    <div class="card-panel">
      <div class="card-header">📥 Upload & Auto-Host Bot</div>
      <div class="dropzone" id="dropzone">
        <div style="font-size:36px; margin-bottom:10px;">📦</div>
        <h4 style="margin-bottom:6px; font-size:0.95rem;">Drop your <span style="color:var(--cyan)">.py</span> file here</h4>
        <p style="font-size:0.78rem; color:var(--muted)">Auto-detects modules & installs requirements.txt</p>
        <input type="file" id="fileInput" accept=".py,.txt" multiple hidden />
      </div>
      <div style="padding: 0 22px 22px; font-size:0.82rem; color:var(--muted);">
        <p>💡 <b>Pro Tip:</b> You can upload `requirements.txt` alongside your `.py` file to install custom packages instantly.</p>
      </div>
    </div>

    <!-- Active Fleet Manager -->
    <div class="card-panel">
      <div class="card-header">
        <span>🤖 Telegram Host Controller</span>
        <button class="action-btn logs" onclick="fetchBotsData()">🔄 Refresh</button>
      </div>
      <div class="bots-table-wrap" id="botsListContainer">
        <div style="padding: 50px; text-align: center; color: var(--muted);">No bots deployed in cluster.</div>
      </div>
    </div>

  </div>

  <!-- Dedicated Bottom Logs Monitor -->
  <div class="logs-container" id="monitor">
    <div class="logs-header">
      <span id="activeLogTitle">📡 Terminal Monitor: Select a bot to view logs</span>
      <button class="action-btn stop" onclick="clearLogs()">Clear Console</button>
    </div>
    <div class="logs-body" id="logsConsoleBody">
      <div class="log-line" style="color:var(--cyan)">[neohost-cluster] Ready. Click 'Logs' on any active bot above to stream stdout in real-time.</div>
    </div>
  </div>

</div>

<footer>
  <p>© 2026 NeoHost — Professional Telegram Bot Cloud Controller.</p>
</footer>

<script>
let viewingBotId = null;
let logPollInterval = null;

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

function triggerUploadModal() {
  document.getElementById('controller').scrollIntoView({ behavior: 'smooth' });
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
      botsListContainer.innerHTML = `<div style="padding: 50px; text-align: center; color: var(--muted);">No bots deployed in cluster.</div>`;
      return;
    }

    entries.forEach(([id, bot]) => {
      total++;
      if(bot.status === 'running') running++; else stopped++;

      html += `
        <div class="bot-row">
          <div class="bot-details">
            <div class="bot-avatar">${bot.name.charAt(0).toUpperCase()}</div>
            <div>
              <div class="bot-name" title="${bot.name}">${bot.name}</div>
              <div style="margin-top:4px;"><span class="badge-status ${bot.status}">${bot.status}</span></div>
            </div>
          </div>
          <div style="display: flex; gap: 6px; flex-wrap: wrap;">
            ${bot.status === 'stopped' ? `<button class="action-btn start" onclick="controlBot('${id}', 'start')">▶ Start</button>` : `<button class="action-btn stop" onclick="controlBot('${id}', 'stop')">⏹ Stop</button>`}
            <button class="action-btn logs" onclick="selectBotLogs('${id}', '${bot.name}')">📜 Logs</button>
            <button class="action-btn del" onclick="controlBot('${id}', 'delete')">🗑 Del</button>
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
      activeLogTitle.textContent = "📡 Terminal Monitor: Select a bot to view logs";
      logsConsoleBody.innerHTML = `<div class="log-line" style="color:var(--cyan)">[neohost] Bot deleted.</div>`;
    }
    fetchBotsData();
  });
}

function selectBotLogs(id, name) {
  viewingBotId = id;
  activeLogTitle.textContent = `📡 Live Logs Monitor: ${name} (${id})`;
  logsConsoleBody.innerHTML = `<div class="log-line">Loading logs for ${name}...</div>`;
}

function clearLogs() {
  logsConsoleBody.innerHTML = `<div class="log-line" style="color:var(--cyan)">Console cleared.</div>`;
}

// Poll logs & stats every 2.5 seconds
setInterval(() => {
  fetchBotsData();
  if(viewingBotId) {
    fetch(`/api/logs/${viewingBotId}`)
    .then(res => res.json())
    .then(data => {
      if(data.logs && data.logs.length) {
        logsConsoleBody.innerHTML = data.logs.map(l => `<div class="log-line">› ${l}</div>`).join('');
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
        # verify process status
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
