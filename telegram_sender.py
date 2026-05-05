import requests
from settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_message(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError('Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID')

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False,
    }
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()
