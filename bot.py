import logging
import time

from amazon_api import search_items
from category_keywords import CATEGORIES
from create_messages import build_message
from settings import CHECK_INTERVAL, MIN_DISCOUNT, TOP_N
from storage import init_db, has_seen, mark_seen
from telegram_sender import send_message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


def collect_products() -> list[dict]:
    found = []

    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            try:
                items = search_items(keyword, search_index=category)
                for item in items:
                    if item.get('discount_percent', 0) < MIN_DISCOUNT:
                        continue
                    if has_seen(item['asin']):
                        continue
                    found.append(item)
            except Exception as exc:
                logger.exception('Errore su categoria %s keyword %s: %s', category, keyword, exc)

    found.sort(key=lambda x: (x.get('discount_percent', 0), -x.get('price', 0)), reverse=True)
    return found[:TOP_N]


def run_cycle():
    products = collect_products()
    if not products:
        logger.warning('Nessun prodotto valido trovato in questo ciclo')
        return

    for item in products:
        text = build_message(item)
        send_message(text)
        mark_seen(item['asin'])
        logger.info('Inviato prodotto %s', item['asin'])
        time.sleep(2)


def run():
    init_db()
    logger.info('Bot avviato')
    logger.info('Ciclo ogni %s secondi', CHECK_INTERVAL)

    while True:
        run_cycle()
        logger.info('Pausa di %s secondi', CHECK_INTERVAL)
        time.sleep(CHECK_INTERVAL)
