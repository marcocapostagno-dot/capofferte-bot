import os
import requests
import random
import time
import hashlib
import hmac
import base64
from datetime import datetime

# ======================
# CONFIG
# ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
TAG = os.getenv("AFFILIATE_TAG", "capofferte-21")

CHANNEL = "@Capofferte"

KEYWORDS = [
    "smartphone",
    "cuffie gaming",
    "smartwatch",
    "powerbank",
    "aspirapolvere",
    "console gaming"
]

# ======================
# TELEGRAM SEND
# ======================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

# ======================
# AMAZON LINK BUILDER (AFFILIATE)
# ======================
def build_amazon_link(asin):
    return f"https://www.amazon.it/dp/{asin}?tag={TAG}"

# ======================
# AMAZON API (SEMPLIFICATA STRUTTURA)
# ======================
def amazon_search(keyword):
    """
    NOTA: struttura pronta per API vera Amazon PA API 5.0
    Qui simuliamo risposta finché non colleghi firma AWS.
    """

    fake_products = [
        {
            "title": f"{keyword.title()} - Offerta Amazon 🔥",
            "asin": "B0EXAMPLE01"
        },
        {
            "title": f"{keyword.title()} Super Sconto Limitato ⚡",
            "asin": "B0EXAMPLE02"
        },
        {
            "title": f"{keyword.title()} Bestseller Amazon ⭐",
            "asin": "B0EXAMPLE03"
        }
    ]

    return fake_products

# ======================
# MAIN LOOP
# ======================
def run_bot():
    send_message("🚀 <b>CapOfferte Bot Avviato!</b>\nOfferte attive ogni giorno 🔥")

    while True:
        keyword = random.choice(KEYWORDS)
        products = amazon_search(keyword)

        for p in products:
            link = build_amazon_link(p["asin"])

            msg = f"""🔥 <b>OFFERTA AMAZON</b>

📦 {p['title']}

👉 <a href="{link}">SCOPRI OFFERTA</a>

⚡ CapOfferte - Amazon Deals"""

            send_message(msg)
            time.sleep(8)

        # 5 offerte al giorno circa
        time.sleep(4 * 60 * 60)

# ======================
# START
# ======================
if __name__ == "__main__":
    run_bot()
