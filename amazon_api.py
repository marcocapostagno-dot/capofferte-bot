import logging
import time
import requests
from requests.auth import HTTPBasicAuth

from settings import (
    AMAZON_CLIENT_ID,
    AMAZON_CLIENT_SECRET,
    AMAZON_PARTNER_TAG,
    AMAZON_MARKETPLACE,
    AMAZON_TOKEN_URL,
    AMAZON_SCOPE,
    MIN_PRICE,
    MAX_PRICE,
    MIN_DISCOUNT,
)

logger = logging.getLogger(__name__)

TOKEN_CACHE = {
    "access_token": None,
    "expires_at": 0,
}

SEARCH_URL = "https://creatorsapi.amazon/catalog/v1/searchItems"


def get_access_token() -> str:
    now = time.time()

    if TOKEN_CACHE["access_token"] and now < TOKEN_CACHE["expires_at"] - 60:
        return TOKEN_CACHE["access_token"]

    data = {
        "grant_type": "client_credentials",
    }

    if AMAZON_SCOPE:
        data["scope"] = AMAZON_SCOPE

    response = requests.post(
        AMAZON_TOKEN_URL,
        data=data,
        auth=HTTPBasicAuth(AMAZON_CLIENT_ID, AMAZON_CLIENT_SECRET),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=30,
    )

    if not response.ok:
        logger.error("Token error %s: %s", response.status_code, response.text)

    response.raise_for_status()
    payload = response.json()

    access_token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 3600))

    TOKEN_CACHE["access_token"] = access_token
    TOKEN_CACHE["expires_at"] = now + expires_in

    return access_token


def search_items(keyword: str, search_index: str = "All") -> list[dict]:
    token = get_access_token()

    body = {
        "keywords": keyword,
        "partnerTag": AMAZON_PARTNER_TAG,
        "marketplace": AMAZON_MARKETPLACE,
        "searchIndex": search_index,
        "resources": [
            "images.primary.small",
            "itemInfo.title",
            "offersV2.listings.price",
            "offersV2.listings.savingBasis"
        ]
    }

    if MIN_PRICE > 0:
        body["minPrice"] = MIN_PRICE

    if MAX_PRICE > 0:
        body["maxPrice"] = MAX_PRICE

    if MIN_DISCOUNT > 0:
        body["minSavingPercent"] = MIN_DISCOUNT

    response = requests.post(
        SEARCH_URL,
        json=body,
        headers={
            "Authorization": f"Bearer {token}",
            "x-marketplace": AMAZON_MARKETPLACE,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        timeout=30,
    )

    if not response.ok:
        logger.error("Search error %s: %s", response.status_code, response.text)

    response.raise_for_status()
    payload = response.json()

    items = payload.get("items", [])
    parsed = []

    for item in items:
        try:
            asin = item.get("asin")
            title = item.get("itemInfo", {}).get("title", {}).get("displayValue")
            url = item.get("detailPageUrl")
            image = (
                item.get("images", {})
                .get("primary", {})
                .get("small", {})
                .get("url")
            )

            listings = item.get("offersV2", {}).get("listings", [])
            if not listings:
                continue

            first_listing = listings[0]
            price = first_listing.get("price", {}).get("amount")
            discount = (
                first_listing.get("savingBasis", {})
                .get("savings", {})
                .get("percentage", 0)
            )

            if not asin or not title or not url or price is None:
                continue

            parsed.append(
                {
                    "asin": asin,
                    "title": title,
                    "url": url,
                    "image": image,
                    "price": float(price),
                    "discount_percent": int(discount or 0),
                }
            )
        except Exception as exc:
            logger.warning("Errore parsing item: %s", exc)

    return parsed
