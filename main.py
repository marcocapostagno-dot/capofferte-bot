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
# PROFIT SCORE SYSTEM
# =====================
def profit_score(keyword):
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
# AMAZON LINK BUILDER
# =====================
def build_link(keyword):
    return f"https://www.amazon.it/s?k={keyword.replace(' ', '+')}&tag={TAG}"

# =====================
# GENERAZIONE PRODOTTI (BASE + FUTURE READY API)
# =====================
def get_products(keyword):
    return [
        {
            "title": f"{keyword.title()} - Offerta Amazon 🔥",
            "keyword": keyword
        }
    ]

# =====================
# FORMAT MESSAGGIO (ALTA CONVERSIONE)
# =====================
def format_message(title, link):
    return f"""🔥 <b>OFFERTA AMAZON SELEZIONATA</b>

📦 {title}

💥 Prezzo scontato attivo ora

👉 <a href="{link}">👉 APRI OFFERTA ORA</a>

⚡ Solo oggi | CapOfferte"""

# =====================
# SCELTA MIGLIORE CATEGORIA
# =====================
def choose_best_keyword(keywords):
    return sorted(keywords, key=lambda k: profit_score(k), reverse=True)[0]

# =====================
# FILTRO PRODOTTI
# =====================
def filter_products(products):
    return products[:1]  # solo TOP 1 per conversione alta

# =====================
# BOT LOOP (SYSTEM PRO)
# =====================
def run():
    send_message("🚀 <b>CAPOFFERTES SYSTEM BUSINESS PRO ATTIVO</b>\n🔥 Ottimizzato per conversioni")

    while True:
        keyword = choose_best_keyword(KEYWORDS)
        products = get_products(keyword)
        products = filter_products(products)

        for p in products:
            link = build_link(p["keyword"])
            msg = format_message(p["title"], link)
            send_message(msg)
            time.sleep(10)

        # timing ottimizzato conversioni
        time.sleep(4 * 60 * 60)

# =====================
# START
# =====================
if __name__ == "__main__":
    run()
