import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '').strip()
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '1800'))

AMAZON_CLIENT_ID = os.getenv('AMAZON_CLIENT_ID', '').strip()
AMAZON_CLIENT_SECRET = os.getenv('AMAZON_CLIENT_SECRET', '').strip()
AMAZON_PARTNER_TAG = os.getenv('AMAZON_PARTNER_TAG', '').strip()
AMAZON_MARKETPLACE = os.getenv('AMAZON_MARKETPLACE', 'www.amazon.it').strip()
AMAZON_REGION = os.getenv('AMAZON_REGION', 'eu').strip().lower()
AMAZON_TOKEN_URL = os.getenv('AMAZON_TOKEN_URL', 'https://api.amazon.com/auth/o2/token').strip()
AMAZON_API_BASE = os.getenv('AMAZON_API_BASE', 'https://creator-connections.amazon.com').strip().rstrip('/')
AMAZON_SCOPE = os.getenv('AMAZON_SCOPE', 'creator_connections:manage').strip()
AMAZON_CREDENTIAL_VERSION = os.getenv('AMAZON_CREDENTIAL_VERSION', '3.2').strip()

MIN_PRICE = float(os.getenv('MIN_PRICE', '0'))
MAX_PRICE = float(os.getenv('MAX_PRICE', '0'))
MIN_DISCOUNT = int(os.getenv('MIN_DISCOUNT', '0'))
TOP_N = int(os.getenv('TOP_N', '5'))

KEYWORDS = [
    'Android', 'Xiaomi', 'Samsung', 'Tablet', 'iPhone', 'Smartphone', 'iPad'
]
