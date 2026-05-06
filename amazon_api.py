import base64
import logging
import time
from typing import Any

import requests

from settings import (
    AMAZON_API_BASE,
    AMAZON_CLIENT_ID,
    AMAZON_CLIENT_SECRET,
    AMAZON_CREDENTIAL_VERSION,
    AMAZON_MARKETPLACE,
    AMAZON_PARTNER_TAG,
    AMAZON_SCOPE,
    AMAZON_TOKEN_URL,
    MAX_PRICE,
    MIN_DISCOUNT,
    MIN_PRICE,
)

logger = logging.getLogger(__name__)

_token_cache: dict[str, Any] = {
    "access_token": None,
    "expires_at": 0,
}


def _require(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"Missing {name}")
    return value


def _get_access_token() -> str:
    now = time.time()
    cached = _token_cache.get("access_token")
    expires_at = _token_cache.get("expires_at", 0)

    if cached and now < expires_at - 60:
        return cached

    client_id = _require(AMAZON_CLIENT_ID, "AMAZON_CLIENT_ID")
    client_secret = _require(AMAZON_CLIENT_SECRET, "AMAZON_CLIENT_SECRET")

    basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": AMAZON_SCOPE or "creatorsapi/default",
    }

    response = requests.post(
        AMAZON_TOKEN_URL,
        headers=headers,
        data=data,
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"OAuth2 token request failed with status {response.status_code}: {response.text}"
        )

    payload = response.json()
    access_token = payload.get("access_token")
    expires_in = int(payload.get("expires_in", 3600))

    if not access_token:
        raise RuntimeError(f"OAuth2 token response missing access_token: {payload}")

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + expires_in
    return access_token


def _extract_price(raw_price: Any) -> float | None:
    if raw_price is None:
        return None

    if isinstance(raw_price, (int, float)):
        return float(raw_price)

    if isinstance(raw_price, dict):
        for key in ("amount", "value"):
            val = raw_price.get(key)
            if isinstance(val, (int, float)):
                return float(val)

    return None


def _extract_image(item: dict) -> str | None:
    images = item.get("images", {})
    if isinstance(images, dict):
        primary = images.get("primary", {})
        if isinstance(primary, dict):
            for size in ("large", "medium", "small"):
                node = primary.get(size)
                if isinstance(node, dict) and isinstance(node.get("url"), str):
                    return node["url"]

    for key in ("image", "imageUrl", "image_url"):
        val = item.get(key)
        if isinstance(val, str):
            return val

    return None


def _extract_title(item: dict) -> str | None:
    item_info = item.get("itemInfo", {})
    if isinstance(item_info, dict):
        title = item_info.get("title", {})
        if isinstance(title, dict):
            display = title.get("displayValue")
            if isinstance(display, str):
                return display

    title = item.get("title")
    if isinstance(title, str):
        return title

    return None


def _extract_url(item: dict) -> str | None:
    for key in ("detailPageUrl", "url"):
        val = item.get(key)
        if isinstance(val, str):
            return val
    return None


def _extract_discount(item: dict) -> int:
    offers_v2 = item.get("offersV2", {})
    if isinstance(offers_v2, dict):
        listings = offers_v2.get("listings", [])
        if listings and isinstance(listings[0], dict):
            saving = listings[0].get("savingBasis") or listings[0].get("saving_basis")
            if isinstance(saving, dict):
                pct = saving.get("percentage")
                if isinstance(pct, (int, float)):
                    return int(pct)

    for key in ("discountPercent", "discount_percent"):
        val = item.get(key)
        if isinstance(val, (int, float)):
            return int(val)

    return 0


def _extract_price_from_item(item: dict) -> float | None:
    offers_v2 = item.get("offersV2", {})
    if isinstance(offers_v2, dict):
        listings = offers_v2.get("listings", [])
        if listings and isinstance(listings[0], dict):
            price = listings[0].get("price")
            parsed = _extract_price(price)
            if parsed is not None:
                return parsed

    return _extract_price(item.get("price"))


def search_items(keyword: str, search_index: str = "All") -> list[dict]:
    _require(AMAZON_PARTNER_TAG, "AMAZON_PARTNER_TAG")
    _require(AMAZON_MARKETPLACE, "AMAZON_MARKETPLACE")

    token = _get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-marketplace": AMAZON_MARKETPLACE,
    }

    payload = {
        "keywords": keyword,
        "partnerTag": AMAZON_PARTNER_TAG,
        "marketplace": AMAZON_MARKETPLACE,
        "searchIndex": search_index,
        "resources": [
            "images.primary.small",
            "itemInfo.title",
            "offersV2.listings.price",
        ],
    }

    response = requests.post(
        f"{AMAZON_API_BASE}/catalog/v1/searchItems",
        headers=headers,
        json=payload,
        timeout=45,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"Creators API search failed with status {response.status_code}: {response.text}"
        )

    data = response.json()
    search_result = data.get("searchResult", {})
    items = search_result.get("items", [])

    parsed = []

    for item in items:
        try:
            asin = item.get("asin")
            title = _extract_title(item)
            url = _extract_url(item)
            image = _extract_image(item)
            price = _extract_price_from_item(item)
            discount_percent = _extract_discount(item)

            if not asin or not title or not url or price is None:
                continue

            if MIN_PRICE > 0 and price < MIN_PRICE:
                continue
            if MAX_PRICE > 0 and price > MAX_PRICE:
                continue
            if MIN_DISCOUNT > 0 and discount_percent < MIN_DISCOUNT:
                continue

            parsed.append(
                {
                    "asin": asin,
                    "title": title,
                    "url": url,
                    "image": image,
                    "price": float(price),
                    "discount_percent": int(discount_percent),
                }
            )
        except Exception as exc:
            logger.warning("Errore parsing item Creators API: %s", exc)

    logger.info("Creators API keyword=%s risultati=%s", keyword, len(parsed))
    return parsed
