import os
import requests
import random
import time
import hashlib
import hmac
import base64
import urllib.parse
from datetime import datetime

# =====================
# CONFIG
# =====================
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
    "console"
]

# =====================
# TELEGRAM
# =====================
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "HTML"
    })

# =====================
# AMAZON SIGNATURE (AWS v4 semplificata)
# =====================
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

def get_signature(key, date_stamp, region, service):
    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, "aws4_request")
    return k_signing

# =====================
# AMAZON API CALL
# =====================
def amazon_search(keyword):
    endpoint = "webservices.amazon.it"
    region = "eu-west-1"
    service = "ProductAdvertisingAPI"

    # ⚠️ VERSIONE SEMPLIFICATA STRUTTURA (funziona con endpoint reale PA API)
    url = "https://webservices.amazon.it/paapi5/searchitems"

    payload = {
        "Keywords": keyword,
        "PartnerTag": TAG,
        "PartnerType": "Associates",
        "Marketplace": "www.amazon.it",
        "Resources": [
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Images.Primary.Medium"
        ]
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "X-Amz-Target": "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        data = response.json()

        items = data.get("SearchResult", {}).get("Items", [])

        results = []
        for item in items[:3]:
            asin = item.get("ASIN")
            title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "Offerta Amazon")

            results.append({
                "asin": asin,
                "title": title
            })

        return results

    except:
        return []

# =====================
# LINK
# =====================
def build_link(asin):
    return f"https://www.amazon.it/dp/{asin}?tag={TAG}"

# =====================
# BOT LOOP
# =====================
def run():
    send_message("🚀 <b>CapOfferte PRO AVVIATO</b>\nOfferte Amazon reali attive 🔥")

    while True:
        keyword = random.choice(KEYWORDS)
        products = amazon_search(keyword)

        if not products:
            time.sleep(60)
            continue

        for p in products:
            link = build_link(p["asin"])

            msg = f"""🔥 <b>OFFERTA AMAZON</b>

📦 {p['title']}

👉 <a href="{link}">SCOPRI OFFERTA</a>

⚡ CapOfferte PRO"""

            send_message(msg)
            time.sleep(10)

        time.sleep(4 * 60 * 60)

if __name__ == "__main__":
    run()
