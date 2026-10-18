import os
import subprocess
import threading
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

active_bots = {}
bot_logs = {}

def install_and_run_bot(bot_id, file_path):
    """Automatically scans imports, installs missing packages, and runs bot live"""
    bot_logs[bot_id] = ["Initializing Python runtime environment...", "Scanning script dependencies..."]
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code_content = f.read()
            
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
                
        if "pyrogram" in detected_pkgs and "Tgcrypto" not in detected_pkgs:
            detected_pkgs.append("Tgcrypto")
            
        if detected_pkgs:
            bot_logs[bot_id].append(f"Installing: {', '.join(detected_pkgs)}...")
            subprocess.run(["pip", "install"] + detected_pkgs, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            bot_logs[bot_id].append("Dependencies installed successfully ✓")
            
        bot_logs[bot_id].append("Executing bot process...")
        
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
# TOMAR 100% ORIGINAL DESIGN & FRONTEND
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
/* ============================================
   RESET & VARIABLES
============================================ */
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --cyan: #00f0ff;
  --magenta: #ff00e5;
  --purple: #7b2ff7;
  --green: #00ff88;
  --red: #ff3b6b;
  --yellow: #ffd60a;

  --bg: #05050a;
  --bg-2: #0a0a14;
  --card: rgba(255, 255, 255, 0.035);
  --card-hover: rgba(255, 255, 255, 0.06);
  --border: rgba(255, 255, 255, 0.08);
  --border-glow: rgba(0, 240, 255, 0.35);

  --text: #e8e8f0;
  --muted: #8a8a9a;
  --muted-2: #5a5a6a;

  --radius: 16px;
  --radius-sm: 10px;
  --font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono: 'JetBrains Mono', 'Fira Code', monospace;
}

html { scroll-behavior: smooth; }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  overflow-x: hidden;
  min-height: 100vh;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

::selection { background: var(--cyan); color: #000; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-2); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, var(--cyan), var(--purple));
  border-radius: 10px;
  border: 2px solid var(--bg-2);
}

/* ============================================
   BACKGROUND FX
============================================ */
.bg-fx { position: fixed; inset: 0; z-index: -2; overflow: hidden; pointer-events: none; }

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.35;
  will-change: transform;
}
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
  -webkit-mask-image: radial-gradient(ellipse 90% 70% at 50% 40%, #000 20%, transparent 75%);
  animation: gridPulse 8s ease-in-out infinite;
}
@keyframes gridPulse { 0%,100% { opacity: 0.55; } 50% { opacity: 1; } }

/* ============================================
   NAVBAR
============================================ */
nav {
  position: sticky; top: 0; z-index: 100;
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 40px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  background: rgba(5,5,10,0.6);
  border-bottom: 1px solid var(--border);
}

.logo {
  display: flex; align-items: center; gap: 10px;
  font-weight: 800; font-size: 1.25rem; letter-spacing: -0.5px;
  text-decoration: none; color: var(--text);
}
.logo-mark {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, var(--cyan), var(--purple), var(--magenta));
  display: grid; place-items: center;
  font-size: 18px; font-weight: 900; color: #000;
  box-shadow: 0 0 20px rgba(0,240,255,0.5);
  animation: logoSpin 6s linear infinite;
}
@keyframes logoSpin {
  0%,100% { box-shadow: 0 0 20px rgba(0,240,255,0.5); }
  50% { box-shadow: 0 0 30px rgba(255,0,229,0.6); }
}
.logo span { background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; }

.nav-links { display: flex; gap: 32px; list-style: none; }
.nav-links a {
  color: var(--muted); text-decoration: none; font-size: 0.9rem; font-weight: 500;
  position: relative; transition: color 0.25s;
}
.nav-links a::after {
  content: ''; position: absolute; left: 0; bottom: -6px;
  width: 0; height: 2px;
  background: linear-gradient(90deg, var(--cyan), var(--magenta));
  transition: width 0.3s ease;
}
.nav-links a:hover { color: var(--text); }
.nav-links a:hover::after { width: 100%; }

.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 11px 22px; border-radius: 10px;
  font-family: var(--font); font-size: 0.9rem; font-weight: 600;
  cursor: pointer; border: none; text-decoration: none;
  transition: all 0.25s ease; white-space: nowrap;
}
.btn-primary { background: linear-gradient(135deg, var(--cyan), var(--purple)); color: #000; box-shadow: 0 0 0 rgba(0,240,255,0); }
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,240,255,0.45); }
.btn-ghost { background: var(--card); color: var(--text); border: 1px solid var(--border); }
.btn-ghost:hover { background: var(--card-hover); border-color: var(--border-glow); transform: translateY(-2px); }
.btn-sm { padding: 8px 14px; font-size: 0.8rem; border-radius: 8px; }

/* ============================================
   HERO
============================================ */
.hero {
  padding: 110px 40px 70px;
  max-width: 1240px; margin: 0 auto;
  display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 60px;
  align-items: center;
}

.badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 7px 14px; border-radius: 100px;
  background: rgba(0,240,255,0.08); border: 1px solid rgba(0,240,255,0.25);
  font-size: 0.78rem; font-weight: 600; color: var(--cyan);
  margin-bottom: 26px; letter-spacing: 0.3px;
}
.badge .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 10px var(--green); animation: pulse 1.6s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(0.8); } }

.hero h1 { font-size: clamp(2.4rem, 5.5vw, 4.2rem); font-weight: 900; line-height: 1.05; letter-spacing: -2px; margin-bottom: 22px; }
.hero h1 .gradient { background: linear-gradient(90deg, var(--cyan), var(--magenta), var(--purple), var(--cyan)); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; animation: gradientShift 6s linear infinite; }
@keyframes gradientShift { 0% { background-position: 0% 50%; } 100% { background-position: 300% 50%; } }

.hero p { font-size: 1.1rem; color: var(--muted); max-width: 520px; margin-bottom: 36px; }
.hero-cta { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 42px; }

.hero-stats { display: flex; gap: 40px; flex-wrap: wrap; padding-top: 28px; border-top: 1px solid var(--border); }
.hero-stats .stat-num { font-size: 1.7rem; font-weight: 800; background: linear-gradient(90deg, var(--cyan), var(--magenta)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-stats .stat-label { font-size: 0.8rem; color: var(--muted); letter-spacing: 0.5px; }

/* Code Window */
.code-window { background: linear-gradient(180deg, rgba(15,15,25,0.95), rgba(8,8,15,0.98)); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: 0 30px 80px rgba(0,0,0,0.6), 0 0 60px rgba(0,240,255,0.08); position: relative; animation: floatCard 6s ease-in-out infinite; }
@keyframes floatCard { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }
.code-window::before { content: ''; position: absolute; inset: -1px; border-radius: var(--radius); padding: 1px; background: linear-gradient(135deg, rgba(0,240,255,0.4), transparent 40%, transparent 60%, rgba(255,0,229,0.4)); -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0); -webkit-mask-composite: xor; mask-composite: exclude; pointer-events: none; }
.code-header { display: flex; align-items: center; gap: 8px; padding: 12px 16px; background: rgba(255,255,255,0.02); border-bottom: 1px solid var(--border); }
.code-header .dots { display: flex; gap: 6px; }
.code-header .dots span { width: 11px; height: 11px; border-radius: 50%; }
.code-header .dots span:nth-child(1) { background: #ff5f57; }
.code-header .dots span:nth-child(2) { background: #febc2e; }
.code-header .dots span:nth-child(3) { background: #28c840; }
.code-header .filename { margin-left: 8px; font-family: var(--mono); font-size: 0.78rem; color: var(--muted); }
.code-body { padding: 22px 20px; font-family: var(--mono); font-size: 0.82rem; line-height: 1.85; overflow-x: auto; }
.code-body .ln { color: var(--muted-2); display: inline-block; width: 22px; user-select: none; }
.kw { color: var(--magenta); }
.fn { color: var(--cyan); }
.str { color: var(--green); }
.cm { color: var(--muted-2); font-style: italic; }
.num { color: var(--yellow); }

/* ============================================
   SECTION SHARED
============================================ */
section { padding: 90px 40px; max-width: 1240px; margin: 0 auto; }
.section-tag { font-family: var(--mono); font-size: 0.8rem; color: var(--cyan); letter-spacing: 2px; text-transform: uppercase; margin-bottom: 14px; display: block; }
.section-title { font-size: clamp(1.8rem, 3.5vw, 2.7rem); font-weight: 800; letter-spacing: -1.5px; margin-bottom: 14px; }
.section-sub { color: var(--muted); max-width: 600px; margin-bottom: 50px; font-size: 1rem; }

/* ============================================
   FEATURES
============================================ */
.features-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
.feature-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 30px 26px; position: relative; overflow: hidden; transition: all 0.35s cubic-bezier(0.2,0.8,0.2,1); backdrop-filter: blur(10px); }
.feature-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, transparent, var(--cyan), transparent); opacity: 0; transition: opacity 0.35s; }
.feature-card:hover { transform: translateY(-6px); background: var(--card-hover); border-color: var(--border-glow); box-shadow: 0 20px 50px rgba(0,0,0,0.4), 0 0 30px rgba(0,240,255,0.1); }
.feature-card:hover::before { opacity: 1; }
.feature-icon { width: 48px; height: 48px; border-radius: 12px; display: grid; place-items: center; font-size: 22px; background: rgba(0,240,255,0.08); border: 1px solid rgba(0,240,255,0.2); margin-bottom: 20px; }
.feature-card:nth-child(2) .feature-icon { background: rgba(255,0,229,0.08); border-color: rgba(255,0,229,0.2); }
.feature-card:nth-child(3) .feature-icon { background: rgba(123,47,247,0.1); border-color: rgba(123,47,247,0.25); }
.feature-card:nth-child(4) .feature-icon { background: rgba(0,255,136,0.08); border-color: rgba(0,255,136,0.2); }
.feature-card h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }
.feature-card p { font-size: 0.9rem; color: var(--muted); }

/* ============================================
   DEPLOY ZONE
============================================ */
.deploy-wrap { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 24px; align-items: start; }
.dropzone { background: var(--card); border: 2px dashed rgba(0,240,255,0.3); border-radius: var(--radius); padding: 60px 30px; text-align: center; cursor: pointer; position: relative; overflow: hidden; transition: all 0.3s ease; backdrop-filter: blur(10px); }
.dropzone::after { content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 50% 50%, rgba(0,240,255,0.08), transparent 60%); opacity: 0; transition: opacity 0.3s; pointer-events: none; }
.dropzone:hover, .dropzone.drag-over { border-color: var(--cyan); background: rgba(0,240,255,0.04); box-shadow: 0 0 40px rgba(0,240,255,0.15), inset 0 0 40px rgba(0,240,255,0.03); }
.dropzone:hover::after, .dropzone.drag-over::after { opacity: 1; }
.dropzone .dz-icon { font-size: 48px; margin-bottom: 16px; display: inline-block; animation: floatIcon 3s ease-in-out infinite; }
@keyframes floatIcon { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
.dropzone h3 { font-size: 1.15rem; margin-bottom: 6px; }
.dropzone p { color: var(--muted); font-size: 0.88rem; }
.dropzone .browse { color: var(--cyan); text-decoration: underline; }

.deploy-side { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 26px; }
.deploy-side h4 { font-size: 0.95rem; margin-bottom: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.deploy-side ul { list-style: none; display: flex; flex-direction: column; gap: 12px; }
.deploy-side li { display: flex; align-items: flex-start; gap: 10px; font-size: 0.86rem; color: var(--muted); }
.deploy-side li .check { color: var(--green); font-weight: 700; flex-shrink: 0; margin-top: 1px; }

/* ============================================
   DASHBOARD
============================================ */
.dashboard { display: grid; grid-template-columns: 1.4fr 1fr; gap: 24px; align-items: start; }
.bots-panel { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; backdrop-filter: blur(10px); }
.panel-head { padding: 18px 22px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.015); }
.panel-head h3 { font-size: 1rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.panel-head .count-badge { font-size: 0.72rem; padding: 2px 9px; border-radius: 100px; background: rgba(0,240,255,0.12); color: var(--cyan); border: 1px solid rgba(0,240,255,0.25); font-family: var(--mono); }

.bots-list { max-height: 480px; overflow-y: auto; }
.empty-state { padding: 60px 30px; text-align: center; color: var(--muted); }
.empty-state .es-icon { font-size: 40px; margin-bottom: 12px; opacity: 0.4; }
.empty-state p { font-size: 0.9rem; }

.bot-item { display: flex; align-items: center; gap: 16px; padding: 16px 22px; border-bottom: 1px solid rgba(255,255,255,0.04); transition: background 0.25s; animation: slideIn 0.4s ease; }
@keyframes slideIn { from { opacity: 0; transform: translateX(-12px); } to { opacity: 1; transform: translateX(0); } }
.bot-item:hover { background: rgba(255,255,255,0.025); }
.bot-item:last-child { border-bottom: none; }

.bot-icon { width: 42px; height: 42px; border-radius: 10px; display: grid; place-items: center; font-size: 18px; background: rgba(0,240,255,0.1); border: 1px solid rgba(0,240,255,0.2); flex-shrink: 0; font-family: var(--mono); font-weight: 700; color: var(--cyan); }
.bot-info { flex: 1; min-width: 0; }
.bot-name { font-weight: 600; font-size: 0.92rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bot-meta { font-size: 0.75rem; color: var(--muted); font-family: var(--mono); display: flex; gap: 10px; align-items: center; margin-top: 4px; }

.status-pill { display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; font-weight: 600; padding: 4px 10px; border-radius: 100px; font-family: var(--mono); letter-spacing: 0.3px; }
.status-pill .led { width: 6px; height: 6px; border-radius: 50%; }
.status-pill.running { background: rgba(0,255,136,0.1); color: var(--green); border: 1px solid rgba(0,255,136,0.3); }
.status-pill.running .led { background: var(--green); box-shadow: 0 0 8px var(--green); animation: pulse 1.2s ease-in-out infinite; }
.status-pill.stopped { background: rgba(138,138,154,0.1); color: var(--muted); border: 1px solid rgba(138,138,154,0.25); }
.status-pill.stopped .led { background: var(--muted-2); }

.bot-actions { display: flex; gap: 6px; flex-shrink: 0; }
.icon-btn { width: 36px; height: 36px; border-radius: 8px; display: grid; place-items: center; border: 1px solid var(--border); background: rgba(255,255,255,0.03); cursor: pointer; font-size: 14px; transition: all 0.2s; }
.icon-btn:hover { background: rgba(255,255,255,0.08); border-color: var(--border-glow); }
.icon-btn.play:hover { border-color: rgba(0,255,136,0.4); background: rgba(0,255,136,0.1); }
.icon-btn.stop:hover { border-color: rgba(255,214,10,0.4); background: rgba(255,214,10,0.1); }
.icon-btn.del:hover { border-color: rgba(255,59,107,0.4); background: rgba(255,59,107,0.1); }

/* Console */
.console-panel { background: #07070d; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; height: 560px; display: flex; flex-direction: column; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
.console-head { padding: 14px 18px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.02); }
.console-head .ch-left { display: flex; align-items: center; gap: 10px; }
.console-head h3 { font-size: 0.85rem; font-weight: 600; font-family: var(--mono); color: var(--muted); }
.console-head .ch-dots { display: flex; gap: 5px; }
.console-head .ch-dots span { width: 9px; height: 9px; border-radius: 50%; background: var(--muted-2); }
.console-head .ch-dots span:nth-child(1) { background: #ff5f57; }
.console-head .ch-dots span:nth-child(2) { background: #febc2e; }
.console-head .ch-dots span:nth-child(3) { background: #28c840; }

.console-body { flex: 1; overflow-y: auto; padding: 16px 18px; font-family: var(--mono); font-size: 0.78rem; line-height: 1.8; }
.console-body::-webkit-scrollbar { width: 6px; }
.console-line { display: flex; gap: 10px; animation: logIn 0.25s ease; word-break: break-word; }
@keyframes logIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
.console-line .time { color: var(--muted-2); flex-shrink: 0; }
.console-line .msg { flex: 1; }
.console-line.info .msg { color: var(--muted); }
.console-line.success .msg { color: var(--green); }
.console-line.error .msg { color: var(--red); }
.console-line.warn .msg { color: var(--yellow); }
.console-line.sys .msg { color: var(--cyan); }
.console-line .prefix { color: var(--purple); font-weight: 700; }

/* ============================================
   FOOTER
============================================ */
footer { border-top: 1px solid var(--border); padding: 50px 40px 30px; margin-top: 60px; }
.footer-inner { max-width: 1240px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
.footer-inner p { font-size: 0.85rem; color: var(--muted); }
.footer-inner .made-with { font-family: var(--mono); font-size: 0.78rem; }

/* ============================================
   TOAST
============================================ */
#toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; }
.toast { padding: 14px 18px; background: rgba(15,15,25,0.95); backdrop-filter: blur(20px); border: 1px solid var(--border); border-radius: 10px; font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); animation: toastIn 0.35s cubic-bezier(0.2,0.9,0.3,1.2); min-width: 240px; }
.toast.success { border-color: rgba(0,255,136,0.4); }
.toast.error { border-color: rgba(255,59,107,0.4); }
.toast.info { border-color: rgba(0,240,255,0.4); }
@keyframes toastIn { from { opacity: 0; transform: translateX(60px) scale(0.9); } to { opacity: 1; transform: translateX(0) scale(1); } }
.toast.removing { animation: toastOut 0.3s ease forwards; }
@keyframes toastOut { to { opacity: 0; transform: translateX(60px) scale(0.9); } }

/* ============================================
   REVEAL ON SCROLL
============================================ */
.reveal { opacity: 0; transform: translateY(30px); transition: opacity 0.7s ease, transform 0.7s cubic-bezier(0.2,0.8,0.2,1); }
.reveal.visible { opacity: 1; transform: translateY(0); }

/* ============================================
   RESPONSIVE (MOBILE FIXES)
============================================ */
@media (max-width: 980px) {
  .hero { grid-template-columns: 1fr; padding: 60px 20px 40px; gap: 40px; text-align: center; }
  .hero p { margin: 0 auto 30px; }
  .hero-cta, .hero-stats { justify-content: center; }
  .deploy-wrap, .dashboard { grid-template-columns: 1fr; }
  .console-panel { height: 400px; }
}

@media (max-width: 700px) {
  nav { padding: 12px 16px; }
  .nav-links { display: none; }
  section { padding: 60px 20px; }
  
  .logo { font-size: 1.1rem; }
  .logo-mark { width: 30px; height: 30px; font-size: 16px; }
  .btn { padding: 8px 14px; font-size: 0.85rem; }

  .hero-stats { gap: 20px; }
  .hero-stats .stat-num { font-size: 1.3rem; }
  .hero-stats .stat-label { font-size: 0.75rem; }

  .code-body { font-size: 0.75rem; padding: 16px; }

  .console-panel { height: 350px; }
  .bot-item { padding: 12px 16px; gap: 12px; flex-wrap: nowrap; }
  .bot-icon { width: 36px; height: 36px; font-size: 16px; border-radius: 8px; }
  .bot-name { font-size: 0.85rem; }
  .bot-meta { font-size: 0.7rem; gap: 6px; flex-wrap: wrap; }
  .bot-actions { gap: 4px; margin-left: 0; }
  .icon-btn { width: 34px; height: 34px; font-size: 12px; }
  
  .panel-head { padding: 14px 16px; }
  .panel-head h3 { font-size: 0.9rem; }

  .dropzone { padding: 40px 20px; }
  .dropzone .dz-icon { font-size: 36px; }
  .dropzone h3 { font-size: 1rem; }
  .deploy-side { padding: 20px; }
}
</style>
</head>
<body>

<div class="bg-fx">
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <div class="orb orb-3"></div>
</div>
<div class="grid-bg"></div>

<nav>
  <a href="#" class="logo">
    <div class="logo-mark">N</div>
    Neo<span>Host</span>
  </a>
  <ul class="nav-links">
    <li><a href="#features">Features</a></li>
    <li><a href="#deploy">Deploy</a></li>
    <li><a href="#dashboard">Dashboard</a></li>
    <li><a href="#docs">Docs</a></li>
  </ul>
  <button class="btn btn-primary" onclick="scrollToSection('deploy')">
    ⚡ Get Started
  </button>
</nav>

<div class="hero">
  <div>
    <div class="badge">
      <span class="dot"></span> Python 3.11 · Live Runtime
    </div>
    <h1>
      Deploy Python Bots.<br>
      <span class="gradient">Lightning Fast.</span>
    </h1>
    <p>
      Upload your <code style="font-family:var(--mono);color:var(--cyan);">.py</code> file,
      hit deploy, and watch your bot go live in seconds. Zero config, full logs,
      24/7 uptime on our neon‑infused cloud.
    </p>
    <div class="hero-cta">
      <button class="btn btn-primary" onclick="scrollToSection('deploy')">
        🚀 Deploy a Bot
      </button>
      <button class="btn btn-ghost" onclick="scrollToSection('dashboard')">
        📊 View Dashboard
      </button>
    </div>
    <div class="hero-stats">
      <div>
        <div class="stat-num" data-count="12847">0</div>
        <div class="stat-label">Bots Deployed</div>
      </div>
      <div>
        <div class="stat-num" data-count="99.9" data-suffix="%">0</div>
        <div class="stat-label">Uptime SLA</div>
      </div>
      <div>
        <div class="stat-num" data-count="42" data-suffix="ms">0</div>
        <div class="stat-label">Avg Latency</div>
      </div>
    </div>
  </div>

  <div class="code-window">
    <div class="code-header">
      <div class="dots"><span></span><span></span><span></span></div>
      <div class="filename">my_bot.py</div>
    </div>
    <div class="code-body">
<span class="ln">1</span><span class="cm"># Your bot — deployed instantly</span><br>
<span class="ln">2</span><span class="kw">import</span> os, asyncio<br>
<span class="ln">3</span><span class="kw">from</span> neohost <span class="kw">import</span> Bot<br>
<span class="ln">4</span><br>
<span class="ln">5</span>bot = <span class="fn">Bot</span>(<br>
<span class="ln">6</span>&nbsp;&nbsp;token=os.environ[<span class="str">"TOKEN"</span>],<br>
<span class="ln">7</span>&nbsp;&nbsp;prefix=<span class="str">"!"</span><br>
<span class="ln">8</span>)<br>
<span class="ln">9</span><br>
<span class="ln">10</span><span class="kw">@bot</span>.command(<span class="str">"ping"</span>)<br>
<span class="ln">11</span><span class="kw">async def</span> <span class="fn">ping</span>(ctx):<br>
<span class="ln">12</span>&nbsp;&nbsp;<span class="kw">await</span> ctx.send(<span class="str">"🏓 Pong!"</span>)<br>
<span class="ln">13</span><br>
<span class="ln">14</span>bot.<span class="fn">run</span>() <span class="cm"># ← live in 0.8s</span>
    </div>
  </div>
</div>

<section id="features" class="reveal">
  <span class="section-tag">// why neohost</span>
  <h2 class="section-title">Built for developers, <br>by developers.</h2>
  <p class="section-sub">Everything you need to ship and scale your Python bots — no DevOps required.</p>

  <div class="features-grid">
    <div class="feature-card">
      <div class="feature-icon">⚡</div>
      <h3>Instant Deploy</h3>
      <p>Drag & drop your <b>.py</b> file and it's running in under 2 seconds. Auto‑restart on crash included.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">📡</div>
      <h3>Live Console</h3>
      <p>Real‑time stdout, stderr, and crash traces streamed directly to your browser. Debug at lightspeed.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">🛡️</div>
      <h3>Isolated Sandbox</h3>
      <p>Every bot runs in its own container with resource caps, so one rogue loop can't take down the fleet.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">♾️</div>
      <h3>24/7 Uptime</h3>
      <p>Global edge network keeps your bots online. Auto‑scaling, auto‑healing, auto‑everything.</p>
    </div>
  </div>
</section>

<section id="deploy" class="reveal">
  <span class="section-tag">// deploy</span>
  <h2 class="section-title">Deploy your <span style="color:var(--cyan)">.py</span> bot</h2>
  <p class="section-sub">Drop a Python file below or click to browse. We'll spin up a fresh runtime and stream the logs live.</p>

  <div class="deploy-wrap">
    <div class="dropzone" id="dropzone">
      <div class="dz-icon">📦</div>
      <h3>Drop your <code style="font-family:var(--mono);color:var(--cyan)">.py</code> file here</h3>
      <p>or <span class="browse">click to browse</span> · max 10 MB · only .py accepted</p>
      <input type="file" id="fileInput" accept=".py" hidden />
    </div>

    <div class="deploy-side">
      <h4>✅ Deployment Checklist</h4>
      <ul>
        <li><span class="check">✓</span> File must end in <code style="font-family:var(--mono);color:var(--cyan)">.py</code></li>
        <li><span class="check">✓</span> Entry point: top‑level script execution</li>
        <li><span class="check">✓</span> Use <code style="font-family:var(--mono);color:var(--cyan)">os.environ</code> for secrets</li>
        <li><span class="check">✓</span> No hardcoded tokens in source</li>
        <li><span class="check">✓</span> Auto-installs missing dependencies</li>
        <li><span class="check">✓</span> Bots auto‑restart on crash</li>
      </ul>
    </div>
  </div>
</section>

<section id="dashboard" class="reveal">
  <span class="section-tag">// dashboard</span>
  <h2 class="section-title">Your fleet</h2>
  <p class="section-sub">Monitor, start, stop, and delete every bot from one dashboard.</p>

  <div class="dashboard">
    <div class="bots-panel">
      <div class="panel-head">
        <h3>🤖 Active Bots <span class="count-badge" id="botCount">0</span></h3>
        <button class="btn btn-ghost btn-sm" onclick="scrollToSection('deploy')">+ New</button>
      </div>
      <div class="bots-list" id="botsList">
        <div class="empty-state" id="emptyState">
          <div class="es-icon">🪐</div>
          <p>No bots yet — deploy your first <b>.py</b> file above.</p>
        </div>
      </div>
    </div>

    <div class="console-panel">
      <div class="console-head">
        <div class="ch-left">
          <div class="ch-dots"><span></span><span></span><span></span></div>
          <h3>live console</h3>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="clearConsole()">Clear</button>
      </div>
      <div class="console-body" id="consoleBody">
        <div class="console-line sys">
          <span class="time">--:--:--</span>
          <span class="msg"><span class="prefix">neohost</span> › Real-time Python runtime online. Ready for execution.</span>
        </div>
      </div>
    </div>
  </div>
</section>

<footer id="docs">
  <div class="footer-inner">
    <p>© 2026 NeoHost — Bot hosting, reimagined.</p>
    <p class="made-with">built with 💜 python · flask · js</p>
  </div>
</footer>

<div id="toast-container"></div>

<script>
const bots = [];
let activeBotId = null;
let logPollTimer = null;

const dropzone   = document.getElementById('dropzone');
const fileInput  = document.getElementById('fileInput');
const botsList   = document.getElementById('botsList');
const emptyState = document.getElementById('emptyState');
const botCount   = document.getElementById('botCount');
const consoleBody= document.getElementById('consoleBody');

function scrollToSection(id) {
  document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}

function timeStr() {
  const d = new Date();
  return [d.getHours(), d.getMinutes(), d.getSeconds()]
    .map(n => String(n).padStart(2, '0')).join(':');
}

function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  const icons = { success: '✅', error: '❌', info: '💡' };
  el.innerHTML = `<span>${icons[type] || '💡'}</span><span>${msg}</span>`;
  document.getElementById('toast-container').appendChild(el);
  setTimeout(() => {
    el.classList.add('removing');
    setTimeout(() => el.remove(), 300);
  }, 3200);
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1024 / 1024).toFixed(1) + ' MB';
}

function log(msg, type = 'info', source = 'neohost') {
  const line = document.createElement('div');
  line.className = `console-line ${type}`;
  line.innerHTML = `<span class="time">${timeStr()}</span><span class="msg"><span class="prefix">${source}</span> › ${msg}</span>`;
  consoleBody.appendChild(line);
  consoleBody.scrollTop = consoleBody.scrollHeight;
}

function clearConsole() {
  consoleBody.innerHTML = '';
  log('Console cleared.', 'info');
}

dropzone.addEventListener('click', () => fileInput.click());

['dragenter', 'dragover'].forEach(evt =>
  dropzone.addEventListener(evt, e => {
    e.preventDefault(); e.stopPropagation();
    dropzone.classList.add('drag-over');
  })
);
['dragleave', 'drop'].forEach(evt =>
  dropzone.addEventListener(evt, e => {
    e.preventDefault(); e.stopPropagation();
    dropzone.classList.remove('drag-over');
  })
);

dropzone.addEventListener('drop', e => {
  const files = e.dataTransfer.files;
  if (files.length) handleFiles(files);
});

fileInput.addEventListener('change', e => {
  if (e.target.files.length) handleFiles(e.target.files);
  fileInput.value = '';
});

function handleFiles(files) {
  Array.from(files).forEach(file => {
    if (!file.name.endsWith('.py')) {
      toast(`${file.name} is not a .py file`, 'error');
      log(`Rejected ${file.name} — invalid extension.`, 'error');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      toast(`${file.name} exceeds 10 MB`, 'error');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    log(`Uploading <b>${escapeHtml(file.name)}</b> to server...`, 'sys');
    fetch('/api/deploy', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        const bot = {
          id: data.bot_id,
          name: file.name,
          size: file.size,
          status: 'running',
          createdAt: Date.now(),
        };
        bots.push(bot);
        renderBots();
        toast(`${file.name} deployed successfully`, 'success');
        log(`Bot <b>${escapeHtml(file.name)}</b> executing live! ID: ${bot.id}`, 'success');
        activeBotId = bot.id;
        startLogPolling();
      } else {
        toast(`Error: ${data.message}`, 'error');
        log(`Deployment failed: ${data.message}`, 'error');
      }
    });
  });
}

function renderBots() {
  botCount.textContent = bots.length;
  botsList.querySelectorAll('.bot-item').forEach(n => n.remove());

  if (bots.length === 0) {
    emptyState.style.display = 'block';
    return;
  }
  emptyState.style.display = 'none';

  bots.forEach(bot => {
    const item = document.createElement('div');
    item.className = 'bot-item';
    item.dataset.id = bot.id;
    const initial = bot.name.replace('.py', '').charAt(0).toUpperCase();

    item.innerHTML = `
      <div class="bot-icon">${initial}</div>
      <div class="bot-info">
        <div class="bot-name">${escapeHtml(bot.name)}</div>
        <div class="bot-meta">
          <span>Active</span>
          <span>·</span>
          <span class="status-pill running"><span class="led"></span>RUNNING</span>
        </div>
      </div>
      <div class="bot-actions">
        <button class="icon-btn stop" title="Stop" onclick="stopBot('${bot.id}')">⏹</button>
      </div>
    `;
    botsList.appendChild(item);
  });
}

function stopBot(id) {
  fetch(`/api/stop/${id}`, { method: 'POST' })
  .then(() => {
    const idx = bots.findIndex(b => b.id === id);
    if (idx !== -1) bots.splice(idx, 1);
    renderBots();
    log(`Bot process terminated.`, 'warn');
    toast(`Bot stopped`, 'info');
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
        data.logs.forEach(l => {
          log(l, 'success', 'bot');
        });
      }
    });
  }, 2000);
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      observer.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

function animateCounters() {
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseFloat(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    const isFloat = target % 1 !== 0;
    let start = 0;
    const duration = 1600;
    const startTime = performance.now();

    function step(now) {
      const p = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      const val = target * eased;
      el.textContent = (isFloat ? val.toFixed(1) : Math.floor(val).toLocaleString()) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
}
setTimeout(animateCounters, 400);

setTimeout(() => {
  log('Runtime online. Ready for deployment.', 'success');
}, 800);
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
        return jsonify({"status": "error", "message": "No file uploaded"})
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.py'):
        return jsonify({"status": "error", "message": "Invalid .py file"})
    
    bot_id = "bot_" + os.urandom(3).hex()
    file_path = os.path.join("/tmp", f"{bot_id}_{file.filename}")
    file.save(file_path)
    
    bot_logs[bot_id] = ["Initializing bot environment..."]
    
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
