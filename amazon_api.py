import logging
from creators_api.api.default_api import DefaultApi
from creators_api.models.search_items_request import SearchItemsRequest

from settings import (
    AMAZON_CREDENTIAL_ID,
    AMAZON_CREDENTIAL_SECRET,
    AMAZON_CREDENTIAL_VERSION,
    AMAZON_PARTNER_TAG,
    AMAZON_MARKETPLACE,
    MIN_PRICE,
    MAX_PRICE,
    MIN_DISCOUNT,
)

logger = logging.getLogger(__name__)


def _build_api_client() -> DefaultApi:
    if not AMAZON_CREDENTIAL_ID:
        raise RuntimeError("Missing AMAZON_CREDENTIAL_ID")
    if not AMAZON_CREDENTIAL_SECRET:
        raise RuntimeError("Missing AMAZON_CREDENTIAL_SECRET")
    if not AMAZON_CREDENTIAL_VERSION:
        raise RuntimeError("Missing AMAZON_CREDENTIAL_VERSION")
    if not AMAZON_PARTNER_TAG:
        raise RuntimeError("Missing AMAZON_PARTNER_TAG")
    if not AMAZON_MARKETPLACE:
        raise RuntimeError("Missing AMAZON_MARKETPLACE")

    return DefaultApi(
        credential_id=AMAZON_CREDENTIAL_ID,
        credential_secret=AMAZON_CREDENTIAL_SECRET,
        version=AMAZON_CREDENTIAL_VERSION,
        marketplace=AMAZON_MARKETPLACE,
    )


def search_items(keyword: str, search_index: str = "All") -> list[dict]:
    api = _build_api_client()

    request = SearchItemsRequest(
        keywords=keyword,
        partner_tag=AMAZON_PARTNER_TAG,
        marketplace=AMAZON_MARKETPLACE,
        search_index=search_index,
        resources=[
            "images.primary.small",
            "itemInfo.title",
            "offersV2.listings.price",
            "offersV2.listings.savingBasis",
        ],
    )

    if MIN_PRICE > 0:
        request.min_price = MIN_PRICE

    if MAX_PRICE > 0:
        request.max_price = MAX_PRICE

    if MIN_DISCOUNT > 0:
        request.min_saving_percent = MIN_DISCOUNT

    try:
        response = api.search_items(search_items_request=request)
    except Exception as exc:
        logger.exception(
            "Creators API search_items failed for keyword=%s search_index=%s",
            keyword,
            search_index,
        )
        raise RuntimeError(f"Creators API error: {exc}") from exc

    items = getattr(response, "items", None) or []
    parsed = []

    for item in items:
        try:
            asin = getattr(item, "asin", None)

            title = None
            item_info = getattr(item, "item_info", None)
            if item_info and getattr(item_info, "title", None):
                title = getattr(item_info.title, "display_value", None)

            url = getattr(item, "detail_page_url", None)

            image = None
            images = getattr(item, "images", None)
            if images and getattr(images, "primary", None) and getattr(images.primary, "small", None):
                image = getattr(images.primary.small, "url", None)

            listings = None
            offers = getattr(item, "offers_v2", None)
            if offers:
                listings = getattr(offers, "listings", None)

            if not listings:
                continue

            first_listing = listings[0]

            price = None
            if getattr(first_listing, "price", None):
                price = getattr(first_listing.price, "amount", None)

            discount = 0
            saving_basis = getattr(first_listing, "saving_basis", None)
            if saving_basis and getattr(saving_basis, "savings", None):
                discount = getattr(saving_basis.savings, "percentage", 0) or 0

            if not asin or not title or not url or price is None:
                continue

            parsed.append(
                {
                    "asin": asin,
                    "title": title,
                    "url": url,
                    "image": image,
                    "price": float(price),
                    "discount_percent": int(discount),
                }
            )
        except Exception as exc:
            logger.warning("Errore parsing item Creators API: %s", exc)

    return parsed
