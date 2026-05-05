import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_THREAD_ID = os.getenv("TELEGRAM_THREAD_ID", "").strip()

AMAZON_CREDENTIAL_ID = os.getenv("AMAZON_CREDENTIAL_ID", "").strip()
AMAZON_CREDENTIAL_SECRET = os.getenv("AMAZON_CREDENTIAL_SECRET", "").strip()
AMAZON_CREDENTIAL_VERSION = os.getenv("AMAZON_CREDENTIAL_VERSION", "").strip()
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG", "").strip()
AMAZON_MARKETPLACE = os.getenv("AMAZON_MARKETPLACE", "www.amazon.it").strip()

MIN_PRICE = float(os.getenv("MIN_PRICE", "0"))
MAX_PRICE = float(os.getenv("MAX_PRICE", "0"))
MIN_DISCOUNT = int(os.getenv("MIN_DISCOUNT", "0"))

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "1800"))
