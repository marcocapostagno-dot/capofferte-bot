import os
import requests
import random
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@Capofferte"
AFFILIATE = "capofferte-21"

# 🔥 OFFERTA REALI (feed base semplificato)
FEED = [
    ("🔥 TECH", "Smartwatch Amazfit in super sconto", "https://www.amazon.it/dp/B0?tag="),
    ("📱 SMARTPHONE", "Powerbank 20000mAh -50%", "https://www.amazon.it/dp/B1?tag="),
    ("🎮 GAMING", "Cuffie gaming RGB top qualità", "https://www.amazon.it/dp/B2?tag="),
    ("🏠 CASA", "Aspirapolvere senza fili super sconto", "https://www.amazon.it/dp/B3?tag="),
    ("🚗 AUTO", "Supporto telefono magnetico auto", "https://www.amazon.it/dp/B4?tag="),
]

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHANNEL, "text": text, "parse_mode": "HTML"})

def pick_deals():
    return random.sample(FEED, 3)

while True:
    deals = pick_deals()

    for category, title, link in deals:
        full_link = f"{link}{AFFILIATE}"

        msg = f"""🔥 <b>{category}</b>

{title}

👉 <a href="{full_link}">SCOPRI OFFERTA</a>
"""

        send_message(msg)
        time.sleep(5)

    # 5 offerte al giorno circa
    time.sleep(4 * 60 * 60)
