import base64
import datetime as dt
import hashlib
import hmac
import json
import logging
import os
import random
import time
from html import escape
from urllib.parse import quote_plus

import requests

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNELS_RAW = os.getenv("CHANNELS", "@Capofferte")
CHANNELS = [c.strip() for c in CHANNELS_RAW.split(",") if c.strip()]

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY", "").strip()
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY", "").strip()
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG", "").strip()
AMAZON_MARKETPLACE = os.getenv("AMAZON_MARKETPLACE", "www.amazon.it").strip()
AMAZON_HOST = os.getenv("AMAZON_HOST", "webservices.amazon.it").strip()
AMAZON_REGION = os.getenv("AMAZON_REGION", "eu-west-1").strip()

KEYWORDS_RAW = os.getenv("KEYWORDS", "smartphone,cuffie gaming,smartwatch,powerbank,tablet,monitor gaming")
KEYWORDS = [k.strip() for k in KEYWORDS_RAW.split(",") if k.strip()]

SEARCH_INDEX = os.getenv("SEARCH_INDEX", "All").strip()
MIN_PRICE_EUR = float(os.getenv("MIN_PRICE_EUR", "20"))
MAX_PRICE_EUR = float(os.getenv("MAX_PRICE_EUR", "300"))
MIN_SAVING_PERCENT = int(os.getenv("MIN_SAVING_PERCENT", "15"))
MAX_ITEMS_PER_CYCLE = int(os.getenv("MAX_ITEMS_PER_CYCLE", "3"))
POST_INTERVAL_SECONDS = int(os.getenv("POST_INTERVAL_SECONDS", "10800"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
ONLY_AMAZON = os.getenv("ONLY_AMAZON", "false").strip().lower() == "true"
ONLY_PRIME = os.getenv("ONLY_PRIME", "false").strip().lower() == "true"

if not BOT_TOKEN:
    raise RuntimeError("Variabile BOT_TOKEN mancante")
if not AMAZON_ACCESS_KEY or not AMAZON_SECRET_KEY or not AMAZON_PARTNER_TAG:
    raise RuntimeError("Credenziali Amazon PA-API mancanti")
if not CHANNELS:
    raise RuntimeError("Nessun canale configurato in CHANNELS")
if not KEYWORDS:
    raise RuntimeError("Nessuna keyword configurata in KEYWORDS")

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
session = requests.Session()

PAAPI_TARGET = "com.amazon.paapi5.v1.ProductAdvertisingAPIv1.SearchItems"
PAAPI_URI = "/paapi5/searchitems"
TG_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"


def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature_key(key, date_stamp, region_name, service_name):
    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = hmac.new(k_date, region_name.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service_name.encode("utf-8"), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
    return k_signing


def amz_price_to_cents(eur: float) -> int:
    return int(round(eur * 100))


def build_headers(payload_json: str):
    t = dt.datetime.utcnow()
    amz_date = t.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = t.strftime("%Y%m%d")

    payload_hash = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    canonical_headers = (
        f"content-encoding:amz-1.0\n"
        f"content-type:application/json; charset=utf-8\n"
        f"host:{AMAZON_HOST}\n"
        f"x-amz-date:{amz_date}\n"
        f"x-amz-target:{PAAPI_TARGET}\n"
    )
    signed_headers = "content-encoding;content-type;host;x-amz-date;x-amz-target"

    canonical_request = "\n".join([
        "POST",
        PAAPI_URI,
        "",
        canonical_headers,
        signed_headers,
        payload_hash,
    ])

    algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{date_stamp}/{AMAZON_REGION}/ProductAdvertisingAPI/aws4_request"
    string_to_sign = "\n".join([
        algorithm,
        amz_date,
        credential_scope,
        hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
    ])

    signing_key = get_signature_key(AMAZON_SECRET_KEY, date_stamp, AMAZON_REGION, "ProductAdvertisingAPI")
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    authorization_header = (
        f"{algorithm} Credential={AMAZON_ACCESS_KEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, Signature={signature}"
    )

    return {
        "Content-Encoding": "amz-1.0",
        "Content-Type": "application/json; charset=utf-8",
        "Host": AMAZON_HOST,
        "X-Amz-Date": amz_date,
        "X-Amz-Target": PAAPI_TARGET,
        "Authorization": authorization_header,
    }


def search_items(keyword: str) -> list:
    payload = {
        "Keywords": keyword,
        "SearchIndex": SEARCH_INDEX,
        "ItemCount": 10,
        "ItemPage": 1,
        "Marketplace": AMAZON_MARKETPLACE,
        "PartnerTag": AMAZON_PARTNER_TAG,
        "PartnerType": "Associates",
        "MinPrice": amz_price_to_cents(MIN_PRICE_EUR),
        "MaxPrice": amz_price_to_cents(MAX_PRICE_EUR),
        "MinSavingPercent": MIN_SAVING_PERCENT,
        "Resources": [
            "Images.Primary.Large",
            "ItemInfo.Title",
            "Offers.Listings.Price",
            "Offers.Listings.Availability.Message",
            "Offers.Listings.Availability.Type",
            "Offers.Listings.Condition",
            "Offers.Listings.MerchantInfo",
            "Offers.Listings.ProgramEligibility.IsPrimeExclusive",
            "Offers.Listings.DeliveryInfo.IsPrimeEligible"
        ]
    }

    payload_json = json.dumps(payload, separators=(",", ":"))
    headers = build_headers(payload_json)
    url = f"https://{AMAZON_HOST}{PAAPI_URI}"

    response = session.post(url, data=payload_json, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if data.get("Errors"):
        raise RuntimeError(f"PA-API error: {data['Errors']}")

    return data.get("SearchResult", {}).get("Items", [])


def extract_listing(item: dict) -> dict | None:
    listings = item.get("Offers", {}).get("Listings", [])
    if not listings:
        return None

    listing = listings[0]
    price = listing.get("Price", {})
    savings = price.get("Savings", {})
    merchant = listing.get("MerchantInfo", {}).get("Name", "")
    availability_type = listing.get("Availability", {}).get("Type", "")
    is_prime = listing.get("DeliveryInfo", {}).get("IsPrimeEligible", False)

    if ONLY_AMAZON and merchant.lower() != "amazon":
        return None
    if ONLY_PRIME and not is_prime:
        return None
    if availability_type not in {"IN_STOCK", "IN_STOCK_SCARCE"}:
        return None

    title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "").strip()
    detail_url = item.get("DetailPageURL", "").strip()
    asin = item.get("ASIN", "").strip()
    image = item.get("Images", {}).get("Primary", {}).get("Large", {}).get("URL")

    amount = price.get("Amount")
    display_amount = price.get("DisplayAmount")
    savings_percent = savings.get("Percentage", 0)
    savings_display = savings.get("DisplayAmount")

    if not title or not detail_url or amount is None:
        return None
    if amount < MIN_PRICE_EUR or amount > MAX_PRICE_EUR:
        return None
    if savings_percent < MIN_SAVING_PERCENT:
        return None

    score = float(savings_percent) * 1000 - float(amount)

    return {
        "asin": asin,
        "title": title,
        "url": detail_url,
        "image": image,
        "price_amount": amount,
        "price_display": display_amount or f"€{amount}",
        "savings_percent": savings_percent,
        "savings_display": savings_display,
        "merchant": merchant or "Amazon",
        "is_prime": is_prime,
        "score": score,
    }


def collect_best_items() -> list:
    all_items = []
    seen_asins = set()

    keywords = KEYWORDS[:]
    random.shuffle(keywords)

    for keyword in keywords:
        try:
            results = search_items(keyword)
            logging.info("Keyword '%s' -> %s risultati", keyword, len(results))

            for item in results:
                parsed = extract_listing(item)
                if not parsed:
                    continue
                if parsed["asin"] in seen_asins:
                    continue
                seen_asins.add(parsed["asin"])
                parsed["keyword"] = keyword
                all_items.append(parsed)

        except Exception as e:
            logging.exception("Errore ricerca keyword %s: %s", keyword, e)

        time.sleep(1)

    all_items.sort(key=lambda x: x["score"], reverse=True)
    return all_items[:MAX_ITEMS_PER_CYCLE]


def build_caption(product: dict) -> str:
    title = escape(product["title"])
    url = escape(product["url"], quote=True)
    price = escape(str(product["price_display"]))
    savings = escape(str(product["savings_percent"]))
    merchant = escape(product.get("merchant", "Amazon"))
    keyword = escape(product.get("keyword", ""))

    parts = [
        "🔥 <b>OFFERTA AMAZON.IT</b>",
        "",
        f"📦 {title}",
        f"💰 Prezzo: <b>{price}</b>",
        f"📉 Sconto: <b>{savings}%</b>",
    ]

    if keyword:
        parts.append(f"🔎 Keyword: {keyword}")

    parts.extend([
        f"🏪 Venditore: {merchant}",
        "",
        f"👉 <a href=\"{url}\">Vedi offerta su Amazon</a>",
        "",
        "ℹ️ Link affiliato / paid link"
    ])

    return "\n".join(parts)


def telegram_api(method: str, payload: dict) -> dict:
    response = session.post(f"{TG_BASE}/{method}", data=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data


def send_product(channel: str, product: dict) -> bool:
    caption = build_caption(product)

    try:
        if product.get("image"):
            telegram_api("sendPhoto", {
                "chat_id": channel,
                "photo": product["image"],
                "caption": caption,
                "parse_mode": "HTML"
            })
        else:
            telegram_api("sendMessage", {
                "chat_id": channel,
                "text": caption,
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            })

        logging.info("Prodotto inviato a %s: %s", channel, product["title"])
        return True
    except Exception as e:
        logging.exception("Errore invio Telegram su %s: %s", channel, e)
        return False


def publish_cycle():
    best_items = collect_best_items()

    if not best_items:
        logging.warning("Nessun prodotto trovato con i filtri attuali")
        return

    for product in best_items:
        for channel in CHANNELS:
            send_product(channel, product)
            time.sleep(2)


def run():
    logging.info("PA-API autopost bot avviato")
    logging.info("Marketplace: %s", AMAZON_MARKETPLACE)
    logging.info("Keyword attive: %s", ", ".join(KEYWORDS))
    logging.info("Range prezzo: %.2f - %.2f EUR", MIN_PRICE_EUR, MAX_PRICE_EUR)
    logging.info("Sconto minimo: %s%%", MIN_SAVING_PERCENT)
    logging.info("Max items per cycle: %s", MAX_ITEMS_PER_CYCLE)

    while True:
        try:
            publish_cycle()
        except Exception as e:
            logging.exception("Errore nel ciclo principale: %s", e)

        logging.info("Pausa di %s secondi", POST_INTERVAL_SECONDS)
        time.sleep(POST_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
