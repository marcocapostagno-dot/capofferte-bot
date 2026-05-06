import logging

from creatorsapi_python_sdk import ApiClient, Configuration
from creatorsapi_python_sdk.api.default_api import DefaultApi
from creatorsapi_python_sdk.models.search_items_request_content import SearchItemsRequestContent

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

    configuration = Configuration(
        username=AMAZON_CREDENTIAL_ID,
        password=AMAZON_CREDENTIAL_SECRET,
    )
    configuration.access_token = AMAZON_CREDENTIAL_VERSION

    api_client = ApiClient(configuration=configuration)
    return DefaultApi(api_client)


def search_items(keyword: str, search_index: str = "All") -> list[dict]:
    api = _build_api_client()

    request = SearchItemsRequestContent(
        keywords=keyword,
        partnerTag=AMAZON_PARTNER_TAG,
        searchIndex=search_index,
        resources=[
            "Images.Primary.Small",
            "ItemInfo.Title",
            "OffersV2.Listings.Price",
            "OffersV2.Listings.SavingBasis",
        ],
    )

    if MIN_PRICE > 0:
        request.minPrice = MIN_PRICE

    if MAX_PRICE > 0:
        request.maxPrice = MAX_PRICE

    if MIN_DISCOUNT > 0:
        request.minSavingPercent = MIN_DISCOUNT

    try:
        response = api.search_items(
            x_marketplace=AMAZON_MARKETPLACE,
            search_items_request_content=request,
        )
    except Exception as exc:
        logger.exception(
            "Creators API search_items failed for keyword=%s search_index=%s",
            keyword,
            search_index,
        )
        raise RuntimeError(f"Creators API error: {exc}") from exc

    items = getattr(response, "search_result", None)
    items = getattr(items, "items", None) or []
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
