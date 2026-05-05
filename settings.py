import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHANNELS = [c.strip() for c in os.getenv("CHANNELS", "@Capofferte").split(",") if c.strip()]

AMAZON_ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY", "").strip()
AMAZON_SECRET_KEY = os.getenv("AMAZON_SECRET_KEY", "").strip()
AMAZON_PARTNER_TAG = os.getenv("AMAZON_PARTNER_TAG", "").strip()
AMAZON_MARKETPLACE = os.getenv("AMAZON_MARKETPLACE", "www.amazon.it").strip()
AMAZON_HOST = os.getenv("AMAZON_HOST", "webservices.amazon.it").strip()
AMAZON_REGION = os.getenv("AMAZON_REGION", "eu-west-1").strip()

SEARCH_INDEX = os.getenv("SEARCH_INDEX", "All").strip()
KEYWORDS = [k.strip() for k in os.getenv(
    "KEYWORDS",
    "smartphone,cuffie gaming,smartwatch,powerbank,tablet,monitor gaming"
).split(",") if k.strip()]

MIN_PRICE_EUR = float(os.getenv("MIN_PRICE_EUR", "20"))
MAX_PRICE_EUR = float(os.getenv("MAX_PRICE_EUR", "300"))
MIN_SAVING_PERCENT = int(os.getenv("MIN_SAVING_PERCENT", "15"))
MAX_ITEMS_PER_CYCLE = int(os.getenv("MAX_ITEMS_PER_CYCLE", "3"))
POST_INTERVAL_SECONDS = int(os.getenv("POST_INTERVAL_SECONDS", "10800"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
PAUSE_BETWEEN_MESSAGES_SECONDS = int(os.getenv("PAUSE_BETWEEN_MESSAGES_SECONDS", "2"))
DB_PATH = os.getenv("DB_PATH", "bot_data.sqlite3")
ONLY_AMAZON = os.getenv("ONLY_AMAZON", "false").strip().lower() == "true"
ONLY_PRIME = os.getenv("ONLY_PRIME", "false").strip().lower() == "true"
MAX_RESULTS_PER_KEYWORD = int(os.getenv("MAX_RESULTS_PER_KEYWORD", "10"))

REQUIRED = {
    "BOT_TOKEN": BOT_TOKEN,
    "AMAZON_ACCESS_KEY": AMAZON_ACCESS_KEY,
    "AMAZON_SECRET_KEY": AMAZON_SECRET_KEY,
    "AMAZON_PARTNER_TAG": AMAZON_PARTNER_TAG,
}

missing = [k for k, v in REQUIRED.items() if not v]
if missing:
    raise RuntimeError(f"Variabili ambiente mancanti: {', '.join(missing)}")
if not CHANNELS:
    raise RuntimeError("Nessun canale configurato in CHANNELS")
if not KEYWORDS:
    raise RuntimeError("Nessuna keyword configurata in KEYWORDS")
