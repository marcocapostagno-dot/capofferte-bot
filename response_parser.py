from settings import MIN_PRICE_EUR, MAX_PRICE_EUR, MIN_SAVING_PERCENT, ONLY_AMAZON, ONLY_PRIME


def parse_item(item: dict, keyword: str) -> dict | None:
    listings = item.get("Offers", {}).get("Listings", [])
    if not listings:
        return None

    listing = listings[0]
    price = listing.get("Price", {})
    savings = price.get("Savings", {})
    title = item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue", "").strip()
    asin = item.get("ASIN", "").strip()
    url = item.get("DetailPageURL", "").strip()
    image = item.get("Images", {}).get("Primary", {}).get("Large", {}).get("URL")
    merchant = listing.get("MerchantInfo", {}).get("Name", "Amazon")
    is_prime = listing.get("DeliveryInfo", {}).get("IsPrimeEligible", False)
    availability_type = listing.get("Availability", {}).get("Type", "")
    amount = price.get("Amount")
    display_amount = price.get("DisplayAmount", "")
    savings_percent = savings.get("Percentage", 0)
    savings_display = savings.get("DisplayAmount", "")
    saving_basis = listing.get("SavingBasis", {}).get("DisplayAmount", "")
    feature_values = item.get("ItemInfo", {}).get("Features", {}).get("DisplayValues", [])[:3]

    if not title or not asin or not url or amount is None:
        return None
    if availability_type not in {"IN_STOCK", "IN_STOCK_SCARCE"}:
        return None
    if amount < MIN_PRICE_EUR or amount > MAX_PRICE_EUR:
        return None
    if savings_percent < MIN_SAVING_PERCENT:
        return None
    if ONLY_AMAZON and merchant.lower() != "amazon":
        return None
    if ONLY_PRIME and not is_prime:
        return None

    score = float(savings_percent) * 1000 - float(amount)

    return {
        "asin": asin,
        "title": title,
        "url": url,
        "image": image,
        "merchant": merchant,
        "is_prime": is_prime,
        "price_amount": amount,
        "price_display": display_amount,
        "savings_percent": savings_percent,
        "savings_display": savings_display,
        "saving_basis_display": saving_basis,
        "features": feature_values,
        "keyword": keyword,
        "score": score,
    }
