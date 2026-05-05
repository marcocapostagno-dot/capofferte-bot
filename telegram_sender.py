import requests

from create_messages import build_caption
from settings import BOT_TOKEN, REQUEST_TIMEOUT

session = requests.Session()
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def telegram_api(method: str, payload: dict) -> dict:
    response = session.post(f"{BASE_URL}/{method}", data=payload, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data


def send_product(channel: str, product: dict):
    caption = build_caption(product)

    if product.get("image"):
        return telegram_api(
            "sendPhoto",
            {
                "chat_id": channel,
                "photo": product["image"],
                "caption": caption,
                "parse_mode": "HTML",
            },
        )

    return telegram_api(
        "sendMessage",
        {
            "chat_id": channel,
            "text": caption,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        },
    )
