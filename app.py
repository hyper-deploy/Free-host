import os
import subprocess
import threading
from flask import Flask, render_template

app = Flask(__name__)

# List of your bot script filenames that you put in your GitHub repository
BOT_SCRIPTS = ["main.py", "bot.py"]  # Tomar bot-er filename gulo ekhane diye dibe

def run_real_bot(script_name):
    """Executes real python telegram bot scripts continuously"""
    file_path = os.path.join(os.getcwd(), script_name)
    if os.path.exists(file_path):
        print(f"Starting real Telegram bot: {script_name}")
        while True:
            try:
                # Run the bot and capture logs
                process = subprocess.Popen(
                    ["python", file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    print(f"[{script_name}] {line.strip()}")
                process.wait()
            except Exception as e:
                print(f"Error in {script_name}: {e}")
    else:
        print(f"Bot script {script_name} not found in repository.")

# Automatically start all bots in background threads when Flask starts
def start_all_bots():
    for bot_script in BOT_SCRIPTS:
        t = threading.Thread(target=run_real_bot, args=(bot_script,), daemon=True)
        t.start()

# Start background bots thread
start_all_bots()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
