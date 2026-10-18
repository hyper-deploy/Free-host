import os
import threading
from flask import Flask, render_template

app = Flask(__name__)

# ==========================================
# BACKGROUND BOT RUNNER PLACEHOLDER
# ==========================================
def run_telegram_bot():
    """
    Place your actual Python telegram bot loop or runner code here.
    Example:
        import telebot
        bot = telebot.TeleBot(os.environ.get("BOT_TOKEN"))
        bot.infinity_polling()
    """
    print("Telegram bot background worker initialized...")

# Start the background bot thread when the server starts
bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
bot_thread.start()

# ==========================================
# WEB ROUTES
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # Render assigns a dynamic port via environment variable; fallback to 5000 for local testing
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
