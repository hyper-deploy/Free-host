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
        # Terminate existing process if running
        if bot_id in bots_registry and bots_registry[bot_id].get("process"):
            try:
                bots_registry[bot_id]["process"].terminate()
            except:
                pass

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
            bot_logs[bot_id].append("Found requirements.txt, installing packages...")
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
        bot_logs[bot_id].append("Bot is now LIVE & RUNNING ✓")
        
        for line in process.stdout:
            msg = line.strip()
            if msg:
                bot_logs[bot_id].append(msg)
                if len(bot_logs[bot_id]) > 500:
                    bot_logs[bot_id].pop(0)
                    
    except Exception as e:
        bot_logs[bot_id].append(f"Error: {str(e)}")
        if bot_id in bots_registry:
            bots_registry[bot_id]["status"] = "stopped"
    finally:
        if bot_id in bots_registry:
            proc = bots_registry[bot_id].get("process")
            if proc and proc.poll() is not None:
                bots_registry[bot_id]["status"] = "stopped"


# ====================================================
# ULTIMATE NATIVE MOBILE APK CONTROL PANEL DESIGN
# ====================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<title>NeoHost APK Control Panel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

:root {
  --cyan: #00f0ff; --magenta: #ff00e5; --purple: #7b2ff7; --green: #00ff88; --red: #ff3b6b; --yellow: #ffd60a;
  --bg: #010104; --card: rgba(255, 255, 255, 0.035); --card-active: rgba(255, 255, 255, 0.08);
  --border: rgba(255, 255, 255, 0.08); --border-glow: rgba(0, 240, 255, 0.6);
  --text: #f0f0f5; --muted: #888898; --font: 'Inter', sans-serif; --mono: 'JetBrains Mono', monospace;
}

body { font-family: var(--font); background: var(--bg); color: var(--text); min-height: 100vh; padding-bottom: 40px; }
::selection { background: var(--cyan); color: #000; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--cyan); border-radius: 10px; }

/* Rotating Chakra Ring */
.chakra-ring {
  width: 36px; height: 36px; border-radius: 50%;
  background: conic-gradient(from 0deg, var(--cyan), var(--magenta), var(--purple), var(--green), var(--cyan));
  display: grid; place-items: center; padding: 2px;
  animation: spinChakra 2s linear infinite;
  box-shadow: 0 0 20px rgba(0,240,255,0.8), inset 0 0 10px rgba(255,0,229,0.6);
}
.chakra-inner { width: 100%; height: 100%; background: var(--bg); border-radius: 50%; display: grid; place-items: center; font-size: 13px; font-weight: 900; color: var(--cyan); }
@keyframes spinChakra { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* App Header Bar */
.app-header {
  position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; background: rgba(1,1,4,0.92); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border);
}
.app-title { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.05rem; }
.app-title span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 15px rgba(0,240,255,0.4); }

/* App Container */
.app-container { max-width: 520px; margin: 14px auto; padding: 0 12px; }

/* Stats Bar */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; }
.stat-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 10px 6px; text-align: center; position: relative; overflow: hidden; }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: var(--cyan); }
.stat-card.running::before { background: var(--green); box-shadow: 0 0 10px var(--green); }
.stat-card.stopped::before { background: var(--red); box-shadow: 0 0 10px var(--red); }
.stat-label { font-size: 0.6rem; color: var(--muted); text-transform: uppercase; font-family: var(--mono); margin-bottom: 2px; }
.stat-num { font-size: 1.25rem; font-weight: 800; font-family: var(--mono); text-shadow: 0 0 10px rgba(255,255,255,0.2); }

/* Panels */
.panel-box { background: var(--card); border: 1px solid var(--border); border-radius: 14px; margin-bottom: 14px; overflow: hidden; backdrop-filter: blur(10px); }
.panel-header { padding: 12px 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-weight: 700; font-size: 0.85rem; }

/* Upload Grid */
.upload-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 12px; }
.upload-card {
  border: 2px dashed rgba(0,240,255,0.4); border-radius: 10px; padding: 16px 8px; text-align: center; cursor: pointer; background: rgba(0,240,255,0.02); transition: 0.2s;
}
.upload-card:active { background: rgba(0,240,255,0.15); transform: scale(0.96); box-shadow: 0 0 20px rgba(0,240,255,0.5); }
.upload-card.req { border-color: rgba(255,0,229,0.4); background: rgba(255,0,229,0.02); }
.upload-card.req:active { background: rgba(255,0,229,0.15); box-shadow: 0 0 20px rgba(255,0,229,0.5); }

/* Bot Item */
.bots-list { max-height: 360px; overflow-y: auto; }
.bot-item { padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.04); display: flex; flex-direction: column; gap: 10px; }
.bot-top { display: flex; align-items: center; justify-content: space-between; }
.bot-info { display: flex; align-items: center; gap: 10px; min-width: 0; }
.bot-avatar { width: 34px; height: 34px; border-radius: 8px; background: rgba(0,240,255,0.12); border: 1px solid rgba(0,240,255,0.4); display: grid; place-items: center; font-family: var(--mono); font-weight: 700; color: var(--cyan); box-shadow: 0 0 10px rgba(0,240,255,0.3); }
.bot-name { font-weight: 600; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px; }

.status-badge { font-size: 0.58rem; font-weight: 700; padding: 2px 8px; border-radius: 100px; font-family: var(--mono); text-transform: uppercase; }
.status-badge.running { background: rgba(0,255,136,0.15); color: var(--green); border: 1px solid rgba(0,255,136,0.4); box-shadow: 0 0 8px rgba(0,255,136,0.3); }
.status-badge.stopped { background: rgba(255,59,107,0.15); color: var(--red); border: 1px solid rgba(255,59,107,0.4); box-shadow: 0 0 8px rgba(255,59,107,0.3); }

/* Neon Glowing Action Buttons with Clear Text */
.btn-bar { display: flex; gap: 6px; }
.action-btn {
  flex: 1; padding: 7px 4px; border-radius: 8px; font-size: 0.7rem; font-weight: 700; cursor: pointer; border: 1px solid var(--border); background: var(--card); color: var(--text); text-align: center; transition: all 0.15s ease; font-family: var(--mono); text-transform: uppercase;
}
.action-btn:active { transform: scale(0.90); }

.action-btn.start { border-color: rgba(0,255,136,0.6); color: var(--green); }
.action-btn.start:active { background: rgba(0,255,136,0.35); box-shadow: 0 0 18px var(--green); text-shadow: 0 0 8px var(--green); }

.action-btn.stop { border-color: rgba(255,214,10,0.6); color: var(--yellow); }
.action-btn.stop:active { background: rgba(255,214,10,0.35); box-shadow: 0 0 18px var(--yellow); text-shadow: 0 0 8px var(--yellow); }

.action-btn.logs { border-color: rgba(0,240,255,0.6); color: var(--cyan); }
.action-btn.logs:active { background: rgba(0,240,255,0.35); box-shadow: 0 0 18px var(--cyan); text-shadow: 0 0 8px var(--cyan); }

.action-btn.del { border-color: rgba(255,59,107,0.6); color: var(--red); }
.action-btn.del:active { background: rgba(255,59,107,0.35); box-shadow: 0 0 18px var(--red); text-shadow: 0 0 8px var(--red); }

/* Terminal Console Box */
.terminal-box { background: #000002; border: 1px solid var(--border); border-radius: 14px; overflow: hidden; box-shadow: 0 15px 40px rgba(0,0,0,0.8); }
.terminal-header { padding: 10px 14px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-family: var(--mono); font-size: 0.72rem; }
.terminal-body { height: 220px; overflow-y: auto; padding: 12px; font-family: var(--mono); font-size: 0.68rem; line-height: 1.6; color: var(--green); text-shadow: 0 0 6px rgba(0,255,136,0.4); }
.t-line { word-break: break-word; margin-bottom: 3px; }
</style>
</head>
<body>

<div class="app-header">
  <div class="app-title">
    <div class="chakra-ring"><div class="chakra-inner">N</div></div>
    Neo<span>Host</span> APK
  </div>
  <button class="action-btn logs" onclick="fetchBotsData()" style="padding:5px 10px; flex:none;">Refresh</button>
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
      <div class="upload-card" onclick="triggerUpload('.py')">
        <div style="font-size:24px; margin-bottom:4px;">📦</div>
        <div style="font-size:0.75rem; font-weight:700; color:var(--cyan)">Upload .py</div>
      </div>
      <div class="upload-card req" onclick="triggerUpload('requirements.txt')">
        <div style="font-size:24px; margin-bottom:4px;">📄</div>
        <div style="font-size:0.75rem; font-weight:700; color:var(--magenta)">Upload requirements.txt</div>
      </div>
    </div>
    <input type="file" id="fileInput" multiple hidden />
  </div>

  <!-- Active Fleet Box -->
  <div class="panel-box">
    <div class="panel-header">
      <span>🤖 Active Fleet Control</span>
    </div>
    <div class="bots-list" id="botsListContainer">
      <div style="padding: 25px; text-align: center; color: var(--muted); font-size: 0.75rem;">No bots active in cluster.</div>
    </div>
  </div>

  <!-- Terminal Logs Box -->
  <div class="terminal-box">
    <div class="terminal-header">
      <span id="activeLogTitle" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:210px;">📡 Console: Ready</span>
      <button class="action-btn stop" onclick="clearLogs()" style="flex:none; padding:3px 8px;">Clear</button>
    </div>
    <div class="terminal-body" id="logsConsoleBody">
      <div class="t-line" style="color:var(--cyan)">[neohost-apk] Control center online. Tap 'Logs' on any bot.</div>
    </div>
  </div>

</div>

<script>
let viewingBotId = null;
let targetExtension = '.py';

const fileInput = document.getElementById('fileInput');
const botsListContainer = document.getElementById('botsListContainer');
const logsConsoleBody = document.getElementById('logsConsoleBody');
const activeLogTitle = document.getElementById('activeLogTitle');

function triggerUpload(ext) {
  targetExtension = ext;
  if(ext === '.py') {
    fileInput.accept = '.py';
  } else {
    fileInput.accept = '.txt';
  }
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
      botsListContainer.innerHTML = `<div style="padding: 25px; text-align: center; color: var(--muted); font-size: 0.75rem;">No bots active in cluster.</div>`;
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
    
    # If requirements.txt uploaded alone, check if we can add it to existing session or create placeholder
    if not py_scripts and any(item[0] == 'requirements.txt' for item in saved_files):
        return jsonify({"status": "success", "message": "requirements.txt uploaded successfully"})
        
    if not py_scripts:
        return jsonify({"status": "error", "message": "Please upload a valid .py script"})
        
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
        return jsonify({"status": "error", "message": "Bot not found"})
        
    info = bots_registry[bot_id]
    if action == "stop":
        if info["process"]:
            try:
                info["process"].terminate()
                info["process"].wait(timeout=1)
            except:
                try:
                    info["process"].kill()
                except:
                    pass
        info["process"] = None
        info["status"] = "stopped"
        bot_logs[bot_id].append("Bot stopped by user ⏹")
    elif action == "start":
        if info["status"] != "running":
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
