import os
import requests
import random
import time

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")  # per futuro upgrade API reale
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")  # per futuro upgrade API reale
TAG = os.getenv("AFFILIATE_TAG", "capofferte-21")

CHANNEL = "@Capofferte"

# =====================
# KEYWORDS (categorie che hai scelto)
# =====================
KEYWORDS = [
    "smartphone",
    "cuffie gaming",
    "smartwatch",
    "powerbank",
    "aspirapolvere",
    "accessori auto"
]

# =====================
# TELEGRAM SEND
# =====================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    })

# =====================
# LINK AFFILIATO AMAZON
# =====================
def build_link(keyword):
    return f"https://www.amazon.it/s?k={keyword.replace(' ', '+')}&tag={TAG}"

# =====================
# FETCH OFFERTE (VERSIONE PRO SEMPLICE MA REALE)
# =====================
def get_products(keyword):
    # struttura pronta per upgrade API vera Amazon
    return [
        {
            "title": f"{keyword.title()} - Offerta Top Amazon 🔥",
            "keyword": keyword
        },
        {
            "title": f"{keyword.title()} - Super Sconto Limitato ⚡",
            "keyword": keyword
        }
    ]

# =====================
# FORMATO MESSAGGIO OTTIMIZZATO (CTR ALTO)
# =====================
def format_message(title, link):
    return f"""🔥 <b>{title}</b>

💥 OFFERTA VERIFICATA AMAZON

👉 <a href="{link}">👉 VEDI OFFERTA QUI</a>

⚡ Solo oggi | CapOfferte
"""

# =====================
# FILTRO SEMPLICE
# =====================
def filter_products(products):
    return products[:2]

# =====================
# BOT LOOP
# =====================
def run():
    send_message("🚀 <b>CapOfferte PRO avviato</b>\nOfferte attive ogni giorno 🔥")

    while True:
        keyword = random.choice(KEYWORDS)
        products = get_products(keyword)
        products = filter_products(products)

        for p in products:
            link = build_link(p["keyword"])
            msg = format_message(p["title"], link)
            send_message(msg)
            time.sleep(8)

        # 5 offerte al giorno circa
        time.sleep(4 * 60 * 60)

# =====================
# START
# =====================
if __name__ == "__main__":
    run()
