import os
import time
import random
import logging
from datetime import datetime
from urllib.parse import quote_plus
from html import escape

import requests

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
AFFILIATE_TAG = os.getenv("AFFILIATE_TAG", "capofferte-21").strip()
POST_INTERVAL_SECONDS = int(os.getenv("POST_INTERVAL_SECONDS", "10800"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "20"))

CHANNELS_RAW = os.getenv("CHANNELS", "@Capofferte")
CHANNELS = [c.strip() for c in CHANNELS_RAW.split(",") if c.strip()]

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

if not BOT_TOKEN:
    raise RuntimeError("Variabile BOT_TOKEN mancante")
if not AFFILIATE_TAG:
    raise RuntimeError("Variabile AFFILIATE_TAG mancante")
if not CHANNELS:
    raise RuntimeError("Nessun canale configurato in CHANNELS")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

session = requests.Session()


def ai_score(keyword: str) -> float:
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


def choose_best_keyword() -> str:
    scored = [(k, ai_score(k)) for k in KEYWORDS]
    scored.sort(key=lambda x: x[1], reverse=True)
    best_keyword = scored[0][0]
    logging.info("Keyword selezionata: %s", best_keyword)
    return best_keyword


def build_amazon_search_link(keyword: str) -> str:
    encoded_keyword = quote_plus(keyword)
    return f"https://www.amazon.it/s?k={encoded_keyword}&tag={AFFILIATE_TAG}"


def get_ai_products(keyword: str) -> list:
    return [
        {
            "title": f"{keyword.title()} in offerta su Amazon",
            "keyword": keyword,
            "price_text": "Controlla il prezzo aggiornato su Amazon",
            "image": None,
        }
    ]


def filter_products(products: list) -> list:
    valid = []
    seen = set()

    for product in products:
        title = product.get("title", "").strip()
        keyword = product.get("keyword", "").strip()

        if not title or not keyword:
            continue

        uniq = (title.lower(), keyword.lower())
        if uniq in seen:
            continue

        seen.add(uniq)
        valid.append(product)

    return valid[:1]


def build_caption(title: str, link: str, price_text: str | None = None) -> str:
    safe_title = escape(title)
    safe_price = escape(price_text) if price_text else None
    safe_link = escape(link, quote=True)

    parts = [
        "🔥 <b>OFFERTA AMAZON</b>",
        "",
        f"📦 {safe_title}",
    ]

    if safe_price:
        parts.extend([
            "",
            f"💰 {safe_price}"
        ])

    parts.extend([
        "",
        f"👉 <a href=\"{safe_link}\">VEDI OFFERTA</a>",
        "",
        "ℹ️ (paid link)",
        "⚡ CapOfferte AI System"
    ])

    return "\n".join(parts)


def telegram_api(method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    response = session.post(url, data=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")

    return data


def send_product(channel: str, title: str, link: str, image_url: str | None = None, price_text: str | None = None) -> bool:
    caption = build_caption(title=title, link=link, price_text=price_text)

    try:
        if image_url:
            telegram_api(
                "sendPhoto",
                {
                    "chat_id": channel,
                    "photo": image_url,
                    "caption": caption,
                    "parse_mode": "HTML"
                }
            )
        else:
            telegram_api(
                "sendMessage",
                {
                    "chat_id": channel,
                    "text": caption,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False
                }
            )

        logging.info("Invio riuscito al canale %s", channel)
        return True

    except requests.RequestException as e:
        logging.exception("Errore HTTP verso Telegram per %s: %s", channel, e)
        return False
    except Exception as e:
        logging.exception("Errore invio messaggio per %s: %s", channel, e)
        return False


def publish_cycle():
    keyword = choose_best_keyword()
    products = filter_products(get_ai_products(keyword))

    if not products:
        logging.warning("Nessun prodotto valido trovato per %s", keyword)
        return

    for product in products:
        link = build_amazon_search_link(product["keyword"])

        for channel in CHANNELS:
            send_product(
                channel=channel,
                title=product["title"],
                link=link,
                image_url=product.get("image"),
                price_text=product.get("price_text")
            )
            time.sleep(3)


def run():
    logging.info("CapOfferte publisher avviato alle %s", datetime.now().isoformat())
    logging.info("Canali attivi: %s", ", ".join(CHANNELS))
    logging.info("Intervallo pubblicazione: %s secondi", POST_INTERVAL_SECONDS)

    while True:
        try:
            publish_cycle()
        except Exception as e:
            logging.exception("Errore nel ciclo principale: %s", e)

        logging.info("Pausa di %s secondi", POST_INTERVAL_SECONDS)
        time.sleep(POST_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
