import os
import subprocess
import threading
import re
import zipfile
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

UPLOAD_FOLDER = "/tmp/neohost_cluster"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bots_registry = {}
bot_logs = {}

def python_zip_runner(bot_id, bot_dir, filename):
    bot_logs[bot_id] = [f"[{filename}] Initializing Python & ZIP runtime..."]
    try:
        if bot_id in bots_registry and bots_registry[bot_id].get("process"):
            try:
                proc = bots_registry[bot_id]["process"]
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=1)
            except:
                try:
                    proc.kill()
                except:
                    pass

        file_ext = os.path.splitext(filename)[1].lower()
        target_dir = bot_dir

        # Handle ZIP Archives containing Python projects & requirements.txt
        if file_ext == '.zip':
            bot_logs[bot_id].append("Extracting ZIP archive...")
            zip_path = os.path.join(bot_dir, filename)
            extract_dir = os.path.join(bot_dir, "extracted_" + bot_id)
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            target_dir = extract_dir
            files_in_ext = os.listdir(target_dir)
            
            # Find main python script
            if 'main.py' in files_in_ext:
                filename = 'main.py'
            else:
                found = False
                for f in files_in_ext:
                    if f.endswith('.py'):
                        filename = f
                        found = True
                        break
                if not found:
                    bot_logs[bot_id].append("Error: No Python (.py) script found inside ZIP.")
                    bots_registry[bot_id]["status"] = "stopped"
                    return

        file_path = os.path.join(target_dir, filename)

        if os.path.exists(file_path):
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
            
            detected_pkgs = [pkg for mod, pkg in module_to_pkg.items() if re.search(r'\b(import|from)\s+' + mod + r'\b', code_content)]
            if "pyrogram" in detected_pkgs and "Tgcrypto" not in detected_pkgs:
                detected_pkgs.append("Tgcrypto")
            
            # Install requirements.txt if present in target directory
            req_path = os.path.join(target_dir, "requirements.txt")
            if os.path.exists(req_path):
                bot_logs[bot_id].append("Installing requirements.txt dependencies...")
                subprocess.run(["pip", "install", "-r", req_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
            if detected_pkgs:
                bot_logs[bot_id].append(f"Auto-installing packages: {', '.join(detected_pkgs)}...")
                subprocess.run(["pip", "install", "--prefer-binary"] + detected_pkgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
            bot_logs[bot_id].append("Dependencies configured successfully ✓")

        bot_logs[bot_id].append(f"Launching Python process for {filename}...")
        process = subprocess.Popen(
            ["python", file_path],
            cwd=target_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        bots_registry[bot_id]["process"] = process
        bots_registry[bot_id]["status"] = "running"
        bot_logs[bot_id].append("Bot is LIVE & RUNNING ✓")
        
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
# ULTRA-PREMIUM CYBERPUNK NEON APK CONTROL PANEL UI
# ====================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
<title>NeoHost Pro APK Controller</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }

:root {
  --cyan: #00f0ff; --magenta: #ff00e5; --purple: #9d4edd; --green: #00ff88; --red: #ff3366; --yellow: #ffb703;
  --bg: #030308; --card: rgba(18, 18, 30, 0.85); --card-hover: rgba(28, 28, 48, 0.95);
  --border: rgba(0, 240, 255, 0.22); --border-glow: rgba(0, 240, 255, 0.8);
  --text: #f4f4f8; --muted: #9494a8; --font: 'Inter', sans-serif; --mono: 'JetBrains Mono', monospace;
}

body { font-family: var(--font); background: var(--bg); color: var(--text); min-height: 100vh; padding-bottom: 40px; }
::selection { background: var(--cyan); color: #000; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--cyan); border-radius: 10px; box-shadow: 0 0 10px var(--cyan); }

/* Glowing Background FX */
.bg-fx { position: fixed; inset: 0; z-index: -2; overflow: hidden; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(140px); opacity: 0.25; }
.orb-1 { width: 400px; height: 400px; background: var(--cyan); top: -100px; left: -100px; }
.orb-2 { width: 400px; height: 400px; background: var(--magenta); bottom: -100px; right: -100px; }

/* Rotating Premium Chakra Ring */
.chakra-ring {
  width: 38px; height: 38px; border-radius: 50%;
  background: conic-gradient(from 0deg, var(--cyan), var(--magenta), var(--purple), var(--green), var(--cyan));
  display: grid; place-items: center; padding: 2px;
  animation: spinChakra 2s linear infinite;
  box-shadow: 0 0 20px rgba(0,240,255,0.8), inset 0 0 10px rgba(255,0,229,0.6);
}
.chakra-inner { width: 100%; height: 100%; background: var(--bg); border-radius: 50%; display: grid; place-items: center; font-size: 13px; font-weight: 900; color: var(--cyan); }
@keyframes spinChakra { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* App Header */
.app-header {
  position: sticky; top: 0; z-index: 100; display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; background: rgba(3,3,8,0.92); backdrop-filter: blur(25px); border-bottom: 1px solid var(--border);
  box-shadow: 0 10px 30px rgba(0,0,0,0.8);
}
.app-title { display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.1rem; }
.app-title span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 0 20px rgba(0,240,255,0.6); }

/* Container */
.app-container { max-width: 520px; margin: 16px auto; padding: 0 12px; }

/* Stats Cards */
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 16px; }
.stat-card {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 12px 8px; text-align: center;
  position: relative; overflow: hidden; backdrop-filter: blur(10px); box-shadow: 0 8px 25px rgba(0,0,0,0.5);
}
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; background: var(--cyan); box-shadow: 0 0 12px var(--cyan); }
.stat-card.running::before { background: var(--green); box-shadow: 0 0 15px var(--green); }
.stat-card.stopped::before { background: var(--red); box-shadow: 0 0 15px var(--red); }
.stat-label { font-size: 0.62rem; color: var(--muted); text-transform: uppercase; font-family: var(--mono); margin-bottom: 3px; letter-spacing: 0.5px; }
.stat-num { font-size: 1.35rem; font-weight: 800; font-family: var(--mono); text-shadow: 0 0 12px rgba(255,255,255,0.3); }

/* Panels */
.panel-box {
  background: var(--card); border: 1px solid var(--border); border-radius: 16px; margin-bottom: 16px; overflow: hidden;
  backdrop-filter: blur(15px); box-shadow: 0 12px 35px rgba(0,0,0,0.6);
}
.panel-header {
  padding: 12px 16px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;
  font-weight: 700; font-size: 0.88rem; background: rgba(0,240,255,0.03);
}

/* Upload Grid */
.upload-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 14px; }
.upload-card {
  border: 2px dashed rgba(0,240,255,0.4); border-radius: 12px; padding: 16px 8px; text-align: center; cursor: pointer;
  background: rgba(0,240,255,0.03); transition: all 0.2s ease;
}
.upload-card:active { background: rgba(0,240,255,0.2); transform: scale(0.96); box-shadow: 0 0 25px rgba(0,240,255,0.8); border-color: var(--cyan); }
.upload-card.zip { border-color: rgba(0,255,136,0.4); background: rgba(0,255,136,0.03); }
.upload-card.zip:active { background: rgba(0,255,136,0.2); box-shadow: 0 0 25px rgba(0,255,136,0.8); border-color: var(--green); }

/* Bot Items */
.bots-list { max-height: 400px; overflow-y: auto; }
.bot-item { padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; gap: 12px; transition: 0.2s; }
.bot-item:hover { background: var(--card-hover); }
.bot-top { display: flex; align-items: center; justify-content: space-between; }
.bot-info { display: flex; align-items: center; gap: 12px; min-width: 0; }
.bot-avatar {
  width: 36px; height: 36px; border-radius: 10px; background: rgba(0,240,255,0.15); border: 1px solid rgba(0,240,255,0.5);
  display: grid; place-items: center; font-family: var(--mono); font-weight: 700; color: var(--cyan); box-shadow: 0 0 12px rgba(0,240,255,0.4);
}
.bot-name { font-weight: 600; font-size: 0.88rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 170px; }

.status-badge { font-size: 0.6rem; font-weight: 700; padding: 3px 9px; border-radius: 100px; font-family: var(--mono); text-transform: uppercase; }
.status-badge.running { background: rgba(0,255,136,0.15); color: var(--green); border: 1px solid rgba(0,255,136,0.5); box-shadow: 0 0 10px rgba(0,255,136,0.4); }
.status-badge.stopped { background: rgba(255,51,102,0.15); color: var(--red); border: 1px solid rgba(255,51,102,0.5); box-shadow: 0 0 10px rgba(255,51,102,0.4); }

/* Separate Neon Glowing Action Buttons */
.btn-bar { display: flex; gap: 6px; }
.action-btn {
  flex: 1; padding: 8px 4px; border-radius: 9px; font-size: 0.72rem; font-weight: 700; cursor: pointer;
  border: 1px solid var(--border); background: rgba(255,255,255,0.03); color: var(--text); text-align: center;
  transition: all 0.15s ease; font-family: var(--mono); text-transform: uppercase;
}
.action-btn:active { transform: scale(0.90); }

/* START BUTTON (Neon Green) */
.action-btn.start { border-color: rgba(0,255,136,0.6); color: var(--green); }
.action-btn.start:active { background: rgba(0,255,136,0.35); box-shadow: 0 0 20px var(--green); text-shadow: 0 0 10px var(--green); }

/* STOP BUTTON (Neon Amber/Yellow) */
.action-btn.stop { border-color: rgba(255,183,3,0.6); color: var(--yellow); }
.action-btn.stop:active { background: rgba(255,183,3,0.35); box-shadow: 0 0 20px var(--yellow); text-shadow: 0 0 10px var(--yellow); }

/* LOGS BUTTON (Neon Cyan) */
.action-btn.logs { border-color: rgba(0,240,255,0.6); color: var(--cyan); }
.action-btn.logs:active { background: rgba(0,240,255,0.35); box-shadow: 0 0 20px var(--cyan); text-shadow: 0 0 10px var(--cyan); }

/* DELETE BUTTON (Neon Red) */
.action-btn.del { border-color: rgba(255,51,102,0.6); color: var(--red); }
.action-btn.del:active { background: rgba(255,51,102,0.35); box-shadow: 0 0 20px var(--red); text-shadow: 0 0 10px var(--red); }

/* Terminal Console Box */
.terminal-box {
  background: #010105; border: 1px solid var(--border); border-radius: 16px; overflow: hidden;
  box-shadow: 0 20px 50px rgba(0,0,0,0.9);
}
.terminal-header {
  padding: 10px 16px; background: rgba(0,240,255,0.03); border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;
  font-family: var(--mono); font-size: 0.75rem;
}
.terminal-body {
  height: 240px; overflow-y: auto; padding: 14px; font-family: var(--mono); font-size: 0.7rem; line-height: 1.6;
  color: var(--green); text-shadow: 0 0 8px rgba(0,255,136,0.5);
}
.t-line { word-break: break-word; margin-bottom: 3px; }
</style>
</head>
<body>

<div class="bg-fx"><div class="orb orb-1"></div><div class="orb orb-2"></div></div>

<div class="app-header">
  <div class="app-title">
    <div class="chakra-ring"><div class="chakra-inner">N</div></div>
    Neo<span>Host</span> Pro
  </div>
  <button class="action-btn logs" onclick="fetchBotsData()" style="flex:none; padding:6px 12px;">Refresh</button>
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

  <!-- Upload Panel -->
  <div class="panel-box">
    <div class="panel-header">📥 Python & ZIP Deployment Center</div>
    <div class="upload-grid">
      <div class="upload-card" onclick="triggerUpload('.py')">
        <div style="font-size:26px; margin-bottom:4px;">🐍</div>
        <div style="font-size:0.78rem; font-weight:700; color:var(--cyan)">Upload .py Script</div>
      </div>
      <div class="upload-card zip" onclick="triggerUpload('.zip')">
        <div style="font-size:26px; margin-bottom:4px;">📦</div>
        <div style="font-size:0.78rem; font-weight:700; color:var(--green)">Upload ZIP Project</div>
      </div>
    </div>
    <input type="file" id="fileInput" multiple hidden />
  </div>

  <!-- Active Fleet Box -->
  <div class="panel-box">
    <div class="panel-header">
      <span>🤖 Active Python Fleet</span>
    </div>
    <div class="bots-list" id="botsListContainer">
      <div style="padding: 30px; text-align: center; color: var(--muted); font-size: 0.78rem;">No bots active in cluster.</div>
    </div>
  </div>

  <!-- Terminal Logs Box -->
  <div class="terminal-box">
    <div class="terminal-header">
      <span id="activeLogTitle" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:210px;">📡 Console: Ready</span>
      <button class="action-btn stop" onclick="clearLogs()" style="flex:none; padding:4px 10px;">Clear</button>
    </div>
    <div class="terminal-body" id="logsConsoleBody">
      <div class="t-line" style="color:var(--cyan)">[neohost-pro] Python runtime ready. Tap 'Logs' on any bot.</div>
    </div>
  </div>

</div>

<script>
let viewingBotId = null;

const fileInput = document.getElementById('fileInput');
const botsListContainer = document.getElementById('botsListContainer');
const logsConsoleBody = document.getElementById('logsConsoleBody');
const activeLogTitle = document.getElementById('activeLogTitle');

function triggerUpload(acceptExt) {
  fileInput.accept = acceptExt + ',.txt';
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
            <button class="action-btn start" onclick="controlBot('${id}', 'start')">Start</button>
            <button class="action-btn stop" onclick="controlBot('${id}', 'stop')">Stop</button>
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
            
    exec_files = [item for item in saved_files if item[0].lower().endswith(('.py', '.zip'))]
    
    if not exec_files:
        return jsonify({"status": "error", "message": "Please upload a valid .py script or .zip project"})
        
    for filename, filepath in exec_files:
        bot_id = "bot_" + os.urandom(3).hex()
        bots_registry[bot_id] = {
            "name": filename,
            "status": "running",
            "process": None,
            "file_path": filepath,
            "dir_path": session_dir
        }
        t = threading.Thread(target=python_zip_runner, args=(bot_id, session_dir, filename), daemon=True)
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
                info["process"].wait(timeout=0.5)
            except:
                try:
                    info["process"].kill()
                except:
                    pass
        info["process"] = None
        info["status"] = "stopped"
        bot_logs[bot_id].append("Bot stopped manually ⏹")
    elif action == "start":
        if info["status"] != "running":
            t = threading.Thread(target=python_zip_runner, args=(bot_id, info["dir_path"], info["name"]), daemon=True)
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
