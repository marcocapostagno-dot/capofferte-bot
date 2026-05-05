import logging
import random
import time

from amazon_api import search_items
from category_keywords import CATEGORIES
from response_parser import parse_item
from settings import CHANNELS, MAX_ITEMS_PER_CYCLE, POST_INTERVAL_SECONDS, PAUSE_BETWEEN_MESSAGES_SECONDS
from storage import init_db, has_been_sent, mark_as_sent
from telegram_sender import send_product

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def collect_products() -> list:
    collected = []
    seen = set()

    category_names = list(CATEGORIES.keys())
    random.shuffle(category_names)

    for category in category_names:
        keywords = CATEGORIES[category][:]
        random.shuffle(keywords)

        for keyword in keywords:
            try:
                items = search_items(keyword, search_index=category)
                logging.info("Categoria %s | Keyword '%s' | risultati %s", category, keyword, len(items))

                for item in items:
                    parsed = parse_item(item, keyword)
                    if not parsed:
                        continue
                    if parsed["asin"] in seen:
                        continue
                    if has_been_sent(parsed["asin"]):
                        continue
                    seen.add(parsed["asin"])
                    collected.append(parsed)

            except Exception as e:
                logging.exception("Errore su categoria %s keyword %s: %s", category, keyword, e)

            time.sleep(1)

    collected.sort(key=lambda x: x["score"], reverse=True)
    return collected[:MAX_ITEMS_PER_CYCLE]


def publish_cycle():
    products = collect_products()

    if not products:
        logging.warning("Nessun prodotto valido trovato in questo ciclo")
        return

    for product in products:
        sent_everywhere = True
        for channel in CHANNELS:
            try:
                send_product(channel, product)
                logging.info("Inviato a %s | %s", channel, product["title"])
                time.sleep(PAUSE_BETWEEN_MESSAGES_SECONDS)
            except Exception as e:
                sent_everywhere = False
                logging.exception("Errore invio a %s: %s", channel, e)

        if sent_everywhere:
            mark_as_sent(product["asin"], product["title"])


def run():
    init_db()
    logging.info("Bot avviato")
    logging.info("Ciclo ogni %s secondi", POST_INTERVAL_SECONDS)

    while True:
        try:
            publish_cycle()
        except Exception as e:
            logging.exception("Errore nel ciclo principale: %s", e)

        logging.info("Pausa di %s secondi", POST_INTERVAL_SECONDS)
        time.sleep(POST_INTERVAL_SECONDS)
