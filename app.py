import os
import subprocess
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Dictionary to keep track of running bot processes
running_bots = {}

def run_bot_script(bot_id, file_path):
    """Runs any python telegram bot script as a real background process"""
    try:
        process = subprocess.Popen(
            ["python", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        running_bots[bot_id] = process
        
        # Read logs from the running bot
        for line in process.stdout:
            print(f"[{bot_id}] {line.strip()}")
            
    except Exception as e:
        print(f"Error running bot {bot_id}: {e}")
    finally:
        if bot_id in running_bots:
            del running_bots[bot_id]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/deploy", methods=["POST"])
def deploy_bot():
    """Receives code from frontend, saves it, and boots it live"""
    data = request.json
    filename = data.get("name", "bot.py")
    code_content = data.get("content", "")
    
    # Save uploaded bot code locally
    bot_id = "bot_" + os.urandom(4).hex()
    file_path = f"/tmp/{bot_id}_{filename}"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code_content)
        
    # Start the bot in a real background thread
    t = threading.Thread(target=run_bot_script, args=(bot_id, file_path), daemon=True)
    t.start()
    
    return jsonify({"status": "success", "bot_id": bot_id, "message": "Bot launched successfully!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
