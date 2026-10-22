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
    bot_logs[bot_id] = [f"[{filename}] Initializing control runtime..."]
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
# NATIVE APP-STYLE CONTROL PANEL (NO WEBSITE VIBE)
# ====================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<title>NeoHost Control Panel APK</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

:root {
  --cyan: #00f0ff; --magenta: #ff00e5; --purple: #7b2ff7; --green: #00ff88; --red: #ff3b6b; --yellow: #ffd60a;
  --bg: #020205; --card: rgba(255, 255, 255, 0.035); --card-active: rgba(255, 255, 255, 0.07);
  --border: rgba(255, 255, 255, 0.09); --border-glow: rgba(0, 240, 255, 0.6);
  --text: #e8e8f0; --muted: #8a8a9a; --font: 'Inter', sans-serif; --mono: 'JetBrains Mono', monospace;
}

body { font-family: var(--font); background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; padding-bottom: 30px; }
::selection { background: var(--cyan); color: #000; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--cyan), var(--purple)); border-radius: 10px; }

/* Rotating Chakra Ring */
.chakra-ring {
  width: 38px; height: 38px; border-radius: 50%;
  background: conic-gradient(from 0deg, var(--cyan), var(--magenta), var(--purple), var(--green), var(--cyan));
  display: grid; place-items: center; padding: 2px;
  animation: spinChakra 2.5s linear infinite;
  box-shadow: 0 0 25px rgba(0,240,255,0.8), inset 0 0 10px rgba(255,0,229,0.6);
}
.chakra-inner { width: 100%; height: 100%; background: var(--bg); border-radius: 50%; display: grid; place-items: center; font-size: 13px; font-weight: 900; color: var(--cyan); }
@keyframes spinChakra { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* App Header Bar */
.app-header {
  position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between;
  padding: 12px 18px; background: rgba(2,2,5,0.9); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
}
.app-title { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.05rem; }
.app-title span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 15px rgba(0,240,255,0.4); }

/* App Layout Container */
.app-container { max-width: 600px; margin: 16px auto; padding: 0 14px; }

/* Stats Bar */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
.stat-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 12px 8px; text-align: center; position: relative; overflow: hidden; }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--cyan); }
.stat-card.running::before { background: var(--green); box-shadow: 0 0 10px var(--green); }
.stat-card.stopped::before { background: var(--red); box-shadow: 0 0 10px var(--red); }
.stat-label { font-size: 0.62rem; color: var(--muted); text-transform: uppercase; font-family: var(--mono); margin-bottom: 2px; }
.stat-num { font-size: 1.3rem; font-weight: 800; font-family: var(--mono); text-shadow: 0 0 10px rgba(255,255,255,0.2); }

/* Control Panels */
.panel-box { background: var(--card); border: 1px solid var(--border); border-radius: 14px; margin-bottom: 16px; overflow: hidden; backdrop-filter: blur(10px); }
.panel-header { padding: 12px 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-weight: 700; font-size: 0.88rem; }

/* Upload Zone */
.upload-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 14px; }
.upload-btn-card {
  border: 2px dashed rgba(0,240,255,0.4); border-radius: 10px; padding: 20px 10px; text-align: center; cursor: pointer; background: rgba(0,240,255,0.03); transition: 0.2s;
}
.upload-btn-card:active { background: rgba(0,240,255,0.12); transform: scale(0.97); box-shadow: 0 0 15px rgba(0,240,255,0.4); }
.upload-btn-card.req { border-color: rgba(255,0,229,0.4); background: rgba(255,0,229,0.03); }
.upload-btn-card.req:active { background: rgba(255,0,229,0.12); box-shadow: 0 0 15px rgba(255,0,229,0.4); }

/* Bot List Items */
.bots-list { max-height: 350px; overflow-y: auto; }
.bot-item { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); display: flex; flex-direction: column; gap: 10px; }
.bot-top { display: flex; align-items: center; justify-content: space-between; }
.bot-info { display: flex; align-items: center; gap: 10px; min-width: 0; }
.bot-avatar { width: 34px; height: 34px; border-radius: 8px; background: rgba(0,240,255,0.12); border: 1px solid rgba(0,240,255,0.4); display: grid; place-items: center; font-family: var(--mono); font-weight: 700; color: var(--cyan); box-shadow: 0 0 10px rgba(0,240,255,0.3); }
.bot-name { font-weight: 600; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px; }

.status-badge { font-size: 0.58rem; font-weight: 700; padding: 2px 8px; border-radius: 100px; font-family: var(--mono); text-transform: uppercase; }
.status-badge.running { background: rgba(0,255,136,0.15); color: var(--green); border: 1px solid rgba(0,255,136,0.4); box-shadow: 0 0 8px rgba(0,255,136,0.3); }
.status-badge.stopped { background: rgba(255,59,107,0.15); color: var(--red); border: 1px solid rgba(255,59,107,0.4); box-shadow: 0 0 8px rgba(255,59,107,0.3); }

/* Button Bar with Text & Neon Glow Effect */
.btn-bar { display: flex; gap: 6px; flex-wrap: wrap; }
.action-btn {
  flex: 1; min-width: 65px; padding: 7px 10px; border-radius: 8px; font-size: 0.72rem; font-weight: 700; cursor: pointer; border: 1px solid var(--border); background: var(--card); color: var(--text); text-align: center; transition: 0.15s ease; font-family: var(--mono); text-transform: uppercase;
}
.action-btn:active { transform: scale(0.92); }
.action-btn.start { border-color: rgba(0,255,136,0.6); color: var(--green); }
.action-btn.start:active { background: rgba(0,255,136,0.3); box-shadow: 0 0 15px var(--green); text-shadow: 0 0 8px var(--green); }
.action-btn.stop { border-color: rgba(255,214,10,0.6); color: var(--yellow); }
.action-btn.stop:active { background: rgba(255,214,10,0.3); box-shadow: 0 0 15px var(--yellow); text-shadow: 0 0 8px var(--yellow); }
.action-btn.logs { border-color: rgba(0,240,255,0.6); color: var(--cyan); }
.action-btn.logs:active { background: rgba(0,240,255,0.3); box-shadow: 0 0 15px var(--cyan); text-shadow: 0 0 8px var(--cyan); }
.action-btn.del { border-color: rgba(255,59,107,0.6); color: var(--red); }
.action-btn.del:active { background: rgba(255,59,107,0.3); box-shadow: 0 0 15px var(--red); text-shadow: 0 0 8px var(--red); }

/* Terminal Console Box */
.terminal-box { background: #010103; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.8); }
.terminal-header { padding: 10px 16px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-family: var(--mono); font-size: 0.75rem; }
.terminal-body { height: 240px; overflow-y: auto; padding: 12px 14px; font-family: var(--mono); font-size: 0.7rem; line-height: 1.6; color: var(--green); text-shadow: 0 0 6px rgba(0,255,136,0.4); }
.t-line { word-break: break-word; margin-bottom: 3px; }
</style>
</head>
<body>

<div class="app-header">
  <div class="app-title">
    <div class="chakra-ring"><div class="chakra-inner">N</div></div>
    Neo<span>Host</span> APK
  </div>
  <button class="action-btn logs" onclick="fetchBotsData()" style="padding:6px 12px;">Refresh</button>
</div>

<div class="app-container">
  
  <!-- Stats Bar -->
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Total</div>
      <div class="stat-num" id="statTotal">0</div>
    </div>
    <div class="stat-card running">
      <div class="stat-label">Running</div>
      <div class="stat-num" id="statRunning" style="color:var(--green)">0</div>
    </div>
    <div class="stat-card stopped">
      <div class="stat-label">Offline</div>
      <div class="stat-num" id="statStopped" style="color:var(--red)">0</div>
    </div>
  </div>

  <!-- Upload Panel Box -->
  <div class="panel-box">
    <div class="panel-header">📥 Project Deployment Center</div>
    <div class="upload-grid">
      <div class="upload-btn-card" onclick="triggerUpload('py')">
        <div style="font-size:26px; margin-bottom:4px;">📦</div>
        <div style="font-size:0.78rem; font-weight:700; color:var(--cyan)">Upload .py Script</div>
      </div>
      <div class="upload-btn-card req" onclick="triggerUpload('txt')">
        <div style="font-size:26px; margin-bottom:4px;">📄</div>
        <div style="font-size:0.78rem; font-weight:700; color:var(--magenta)">Upload requirements.txt</div>
      </div>
    </div>
    <input type="file" id="fileInput" accept=".py,.txt" multiple hidden />
  </div>

  <!-- Active Fleet Box -->
  <div class="panel-box">
    <div class="panel-header">
      <span>🤖 Active Fleet Control</span>
    </div>
    <div class="bots-list" id="botsListContainer">
      <div style="padding: 30px; text-align: center; color: var(--muted); font-size: 0.78rem;">No bots active in cluster.</div>
    </div>
  </div>

  <!-- Terminal Logs Box -->
  <div class="terminal-box">
    <div class="terminal-header">
      <span id="activeLogTitle" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:220px;">📡 Console: Ready</span>
      <button class="action-btn stop" onclick="clearLogs()" style="min-width:50px; padding:4px 8px;">Clear</button>
    </div>
    <div class="terminal-body" id="logsConsoleBody">
      <div class="t-line" style="color:var(--cyan)">[neohost-apk] Control panel online. Tap 'Logs' on any bot.</div>
    </div>
  </div>

</div>

<script>
let viewingBotId = null;

const fileInput = document.getElementById('fileInput');
const botsListContainer = document.getElementById('botsListContainer');
const logsConsoleBody = document.getElementById('logsConsoleBody');
const activeLogTitle = document.getElementById('activeLogTitle');

function triggerUpload(type) {
  fileInput.click();
}

fileInput.addEventListener('change', e => {
  if (e.target.files.length) {
    uploadFiles(e.target.files);
    fileInput.value = '';
  }
});

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
      botsListContainer.innerHTML = `<div style="padding: 30px; text-align: center; color: var(--muted); font-size: 0.78rem;">No bots active in cluster.</div>`;
      return;
    }

    entries.forEach(([id, bot]) => {
      total++;
      if(bot.status === 'running') running++; else stopped++;

      html += `
        <div class="bot-item">
          <div class="bot-top">
            <div class="bot-info">
              <div class="bot-avatar">${bot.name.charAt(0).toUpperCase()}</div>
              <div class="bot-name" title="${bot.name}">${bot.name}</div>
            </div>
            <div><span class="status-badge ${bot.status}">${bot.status}</span></div>
          </div>
          <div class="btn-bar">
            ${bot.status === 'stopped' ? `<button class="action-btn start" onclick="controlBot('${id}', 'start')">Start</button>` : `<button class="action-btn stop" onclick="controlBot('${id}', 'stop')">Stop</button>`}
            <button class="action-btn logs" onclick="selectBotLogs('${id}', '${bot.name}')">Logs</button>
            <button class="action-btn del" onclick="controlBot('${id}', 'delete')">Delete</button>
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
      activeLogTitle.textContent = "📡 Console: Ready";
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
    
    saved_files = []
    for f in files:
        if f.filename:
            f_path = os.path.join(session_dir, f.filename)
            f.save(f_path)
            saved_files.append((f.filename, f_path))
            
    py_scripts = [item for item in saved_files if item[0].endswith('.py')]
    if not py_scripts:
        return jsonify({"status": "error", "message": "No .py script found"})
        
    for filename, filepath in py_scripts:
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
