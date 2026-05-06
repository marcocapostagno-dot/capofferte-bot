import time
import html
import logging
import requests

from settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CHECK_INTERVAL, KEYWORDS, TOP_N
from amazon_api import search_items

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

_sent_asins = set()


def send_telegram_message(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID:
        raise RuntimeError("Missing TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()


def format_product(item: dict) -> str:
    title = html.escape(item.get("title", "Prodotto Amazon"))
    price = item.get("price", 0)
    discount = item.get("discount_percent", 0)
    url = item.get("url", "")

    return (
        f"🔥 <b>{title}</b>\n"
        f"💰 Prezzo: {price:.2f}€\n"
        f"🏷️ Sconto: {discount}%\n"
        f"🛒 <a href=\"{url}\">Vai all'offerta</a>"
    )


def collect_products() -> list[dict]:
    results = []

    for keyword in KEYWORDS:
        try:
            items = search_items(keyword)
            logger.info("Trovati %s prodotti per keyword=%s", len(items), keyword)
            results.extend(items[:TOP_N])
        except Exception as exc:
            logger.exception("Errore su keyword %s: %s", keyword, exc)

    return results


def unique_new_products(products: list[dict]) -> list[dict]:
    fresh = []
    for item in products:
        asin = item.get("asin")
        if not asin:
            continue
        if asin in _sent_asins:
            continue
        _sent_asins.add(asin)
        fresh.append(item)
    return fresh


def main() -> None:
    logger.info("Bot avviato")

    while True:
        try:
            products = collect_products()
            products = unique_new_products(products)

            if not products:
                logger.warning("Nessun prodotto valido trovato in questo ciclo")
            else:
                for item in products:
                    try:
                        message = format_product(item)
                        send_telegram_message(message)
                        time.sleep(2)
                    except Exception as exc:
                        logger.exception("Errore invio Telegram: %s", exc)

        except Exception as exc:
            logger.exception("Errore generale del ciclo: %s", exc)

        logger.info("Pausa di %s secondi", CHECK_INTERVAL)
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
