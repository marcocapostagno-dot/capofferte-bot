import os
import requests
import random
import time

# =====================
# CONFIG
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
TAG = os.getenv("AFFILIATE_TAG", "capofferte-21")

CHANNEL = "@Capofferte"

# =====================
# KEYWORDS (categorie ad alta conversione)
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
# HOT SCORE (priorità conversione)
# =====================
def hot_score(keyword):
    scores = {
        "smartphone": 10,
        "cuffie gaming": 9,
        "smartwatch": 8,
        "powerbank": 7,
        "aspirapolvere": 7,
        "accessori auto": 6
    }
    return scores.get(keyword, 5)

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
# LINK AMAZON AFFILIATO
# =====================
def build_link(keyword):
    return f"https://www.amazon.it/s?k={keyword.replace(' ', '+')}&tag={TAG}"

# =====================
# PRODOTTI (STRUTTURA PRONTA PER AMAZON API FUTURA)
# =====================
def get_products(keyword):
    return [
        {
            "title": f"{keyword.title()} - Offerta Amazon 🔥",
            "keyword": keyword
        },
        {
            "title": f"{keyword.title()} - Super Sconto ⚡",
            "keyword": keyword
        }
    ]

# =====================
# FILTRO PRODOTTI
# =====================
def filter_products(products):
    return products[:2]

# =====================
# FORMAT MESSAGGIO (ALTO CTR)
# =====================
def format_message(title, link):
    return f"""🔥 <b>OFFERTA AMAZON VERIFICATA</b>

📦 {title}

💥 Prezzo scontato disponibile ora

👉 <a href="{link}">👉 APRI OFFERTA QUI</a>

⚡ Solo oggi | CapOfferte
"""

# =====================
# MAIN LOOP MONEY PRO
# =====================
def run():
    send_message("🚀 <b>CAPOFFERTES MONEY PRO ATTIVO</b>\n🔥 Solo offerte selezionate")

    while True:
        # categoria prioritaria
        keyword = random.choice(
            sorted(KEYWORDS, key=lambda x: hot_score(x), reverse=True)
        )

        products = get_products(keyword)
        products = filter_products(products)

        for p in products:
            link = build_link(p["keyword"])
            msg = format_message(p["title"], link)

            send_message(msg)
            time.sleep(10)

        # ritmo ottimizzato conversioni
        time.sleep(4 * 60 * 60)

# =====================
# START
# =====================
if __name__ == "__main__":
    run()
