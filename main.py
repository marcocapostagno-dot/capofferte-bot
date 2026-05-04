import os
import requests
import random
import time
from datetime import datetime

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
TAG = os.getenv("AFFILIATE_TAG", "capofferte-21")

# MULTI CANALE (scaling)
CHANNELS = [
    "@Capofferte",
    # puoi aggiungerne altri in futuro
]

# =====================
# KEYWORDS (base crescita)
# =====================
KEYWORDS = [
    "smartphone",
    "cuffie gaming",
    "smartwatch",
    "powerbank",
    "aspirapolvere",
    "accessori auto",
    "tablet",
    "monitor gaming"
]

# =====================
# AI SCORING (simulato ma evolutivo)
# =====================
def ai_score(keyword):
    weights = {
        "smartphone": 10,
        "tablet": 9,
        "cuffie gaming": 9,
        "smartwatch": 8,
        "monitor gaming": 8,
        "aspirapolvere": 7,
        "powerbank": 7,
        "accessori auto": 6
    }
    return weights.get(keyword, 5) + random.uniform(0, 1)

# =====================
# TELEGRAM SEND (con immagine)
# =====================
def send_product(channel, title, link, image_url=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"

    caption = f"""🔥 <b>OFFERTA AMAZON</b>

📦 {title}

💥 Prezzo scontato disponibile ora

👉 <a href="{link}">VEDI OFFERTA</a>

⚡ CapOfferte AI System"""

    data = {
        "chat_id": channel,
        "caption": caption,
        "parse_mode": "HTML"
    }

    if image_url:
        data["photo"] = image_url
    else:
        data["photo"] = "https://via.placeholder.com/500x500.png?text=Amazon+Deal"

    requests.post(url, data=data)

# =====================
# AMAZON LINK BUILDER
# =====================
def build_link(keyword):
    return f"https://www.amazon.it/s?k={keyword.replace(' ', '+')}&tag={TAG}"

# =====================
# AI PRODUCT GENERATOR (base reale + scalabile API futura)
# =====================
def get_ai_products(keyword):
    return [
        {
            "title": f"{keyword.title()} - Offerta Top Amazon 🔥",
            "keyword": keyword,
            "image": None  # futuro: Amazon API image
        }
    ]

# =====================
# AI SELECT BEST KEYWORD
# =====================
def choose_best_keyword():
    scored = [(k, ai_score(k)) for k in KEYWORDS]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]

# =====================
# FILTER (anti spam + quality)
# =====================
def filter_products(products):
    return products[:1]

# =====================
# MAIN LOOP (SCALING ENGINE)
# =====================
def run():
    print("CAPOFFERTES SCALE BUSINESS AI STARTED")

    while True:
        keyword = choose_best_keyword()
        products = get_ai_products(keyword)
        products = filter_products(products)

        for p in products:
            link = build_link(p["keyword"])

            for channel in CHANNELS:
                send_product(
                    channel=channel,
                    title=p["title"],
                    link=link,
                    image_url=p.get("image")
                )

                time.sleep(3)

        # ritmo scalabile (non spam)
        time.sleep(3 * 60 * 60)

# =====================
# START
# =====================
if __name__ == "__main__":
    run()
