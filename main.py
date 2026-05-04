import os
import requests
import random
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@Capofferte"
AFFILIATE = "capofferte-21"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    })

def build_link(keyword):
    return f"https://www.amazon.it/s?k={keyword.replace(' ', '+')}&tag={AFFILIATE}"

DEALS = [
    ("🔥 TECH", "Smartwatch Amazfit in super sconto", "smartwatch amazfit"),
    ("📱 SMARTPHONE", "Powerbank 20000mAh super offerta", "powerbank 20000mah"),
    ("🎮 GAMING", "Cuffie gaming RGB top qualità", "cuffie gaming rgb"),
    ("🏠 CASA", "Aspirapolvere senza fili in offerta", "aspirapolvere senza fili"),
    ("🚗 AUTO", "Supporto telefono magnetico auto", "supporto telefono auto"),
    ("💪 FITNESS", "Smartband fitness economico", "smartband fitness"),
]

def run_bot():
    while True:
        picks = random.sample(DEALS, 3)

        for category, title, keyword in picks:
            link = build_link(keyword)

            message = f"""🔥 <b>{category}</b>

{title}

👉 <a href="{link}">SCOPRI SU AMAZON</a>
"""

            send_message(message)
            time.sleep(10)

        # pausa per non spammare troppo
        time.sleep(4 * 60 * 60)

run_bot()
