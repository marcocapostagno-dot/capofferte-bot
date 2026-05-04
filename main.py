import os
import requests
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@Capofferte"
AFFILIATE = "capofferte-21"

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def get_fake_deals():
    # simulazione offerte (poi si può collegare feed reali Amazon)
    return [
        ("🔥 Amazon Deal Tech", "Smartwatch a 29€ invece di 59€"),
        ("🎮 Gaming Offer", "Cuffie gaming -40%"),
        ("📱 Smartphone Deal", "Powerbank 20000mAh super sconto"),
    ]

while True:
    deals = get_fake_deals()
    for title, desc in deals:
        msg = f"{title}\n\n{desc}\n\n👉 https://amazon.it/?tag={AFFILIATE}"
        send_message(msg)
        time.sleep(10)

    time.sleep(3600)
