import logging
import time
from typing import Any

import requests

from settings import (
    AMAZON_API_BASE,
    AMAZON_CLIENT_ID,
    AMAZON_CLIENT_SECRET,
    AMAZON_MARKETPLACE,
    AMAZON_PARTNER_TAG,
    AMAZON_SCOPE,
    AMAZON_TOKEN_URL,
    MIN_DISCOUNT,
    MIN_PRICE,
    MAX_PRICE,
)

logger = logging.getLogger(__name__)

_token_cache: dict[str, Any] = {"access_token": None, "expires_at": 0}


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

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(AMAZON_TOKEN_URL, data=payload, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"OAuth2 token request failed with status {response.status_code}: {response.text}"
        )

    data = response.json()
    access_token = data.get("access_token")
    expires_in = int(data.get("expires_in", 3600))
    if not access_token:
        raise RuntimeError("OAuth2 token response missing access_token")

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + expires_in
    return access_token


def _extract_price(raw_price: Any) -> float | None:
    if raw_price is None:
        return None
    if isinstance(raw_price, (int, float)):
        return float(raw_price)
    if isinstance(raw_price, dict):
        for key in ("amount", "value", "displayAmount"):
            val = raw_price.get(key)
            if isinstance(val, (int, float)):
                return float(val)
    return None


def _extract_image(item: dict) -> str | None:
    for key in ("image", "images", "primaryImage", "primary_image"):
        value = item.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            for subkey in ("url", "small", "medium", "large"):
                subval = value.get(subkey)
                if isinstance(subval, str):
                    return subval
                if isinstance(subval, dict) and isinstance(subval.get("url"), str):
                    return subval["url"]
    return None


def _extract_url(item: dict) -> str | None:
    for key in ("detailPageUrl", "detail_page_url", "url", "productUrl"):
        value = item.get(key)
        if isinstance(value, str):
            return value
    return None


def _extract_title(item: dict) -> str | None:
    for key in ("title", "name"):
        value = item.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict) and isinstance(value.get("displayValue"), str):
            return value["displayValue"]
    item_info = item.get("itemInfo") or item.get("item_info") or {}
    title = item_info.get("title") if isinstance(item_info, dict) else None
    if isinstance(title, str):
        return title
    if isinstance(title, dict):
        return title.get("displayValue") or title.get("display_value")
    return None


def _extract_asin(item: dict) -> str | None:
    for key in ("asin", "ASIN"):
        value = item.get(key)
        if isinstance(value, str):
            return value
    return None


def _parse_items(payload: dict) -> list[dict]:
    containers = []
    for key in ("items", "searchResult", "search_result", "data", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            containers = value
            break
        if isinstance(value, dict):
            nested = value.get("items") or value.get("results")
            if isinstance(nested, list):
                containers = nested
                break

    parsed: list[dict] = []
    for item in containers:
        if not isinstance(item, dict):
            continue

        asin = _extract_asin(item)
        title = _extract_title(item)
        url = _extract_url(item)
        image = _extract_image(item)

        price = None
        for key in ("price", "currentPrice", "current_price"):
            price = _extract_price(item.get(key))
            if price is not None:
                break

        if price is None:
            offers = item.get("offers") or item.get("offersV2") or item.get("offers_v2")
            if isinstance(offers, dict):
                listings = offers.get("listings") or []
                if listings and isinstance(listings[0], dict):
                    price = _extract_price(listings[0].get("price"))

        discount_percent = 0
        for key in ("discountPercent", "discount_percent", "savingPercent", "saving_percent"):
            value = item.get(key)
            if isinstance(value, (int, float)):
                discount_percent = int(value)
                break

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
                "discount_percent": discount_percent,
            }
        )

    return parsed


def search_items(keyword: str, search_index: str = "All") -> list[dict]:
    _require(AMAZON_PARTNER_TAG, "AMAZON_PARTNER_TAG")
    _require(AMAZON_MARKETPLACE, "AMAZON_MARKETPLACE")

    access_token = _get_access_token()
    endpoint = f"{AMAZON_API_BASE}/v1/search/items"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Marketplace": AMAZON_MARKETPLACE,
    }

    payload = {
        "keywords": keyword,
        "searchIndex": search_index,
        "partnerTag": AMAZON_PARTNER_TAG,
    }

    response = requests.post(endpoint, headers=headers, json=payload, timeout=45)
    if response.status_code >= 400:
        raise RuntimeError(
            f"Creators API search failed with status {response.status_code}: {response.text}"
        )

    data = response.json()
    items = _parse_items(data)
    logger.info("Creators API keyword=%s results=%s", keyword, len(items))
    return items
