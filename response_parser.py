def _get(dct, *path, default=None):
    cur = dct
    for key in path:
        if isinstance(key, int):
            if isinstance(cur, list) and 0 <= key < len(cur):
                cur = cur[key]
            else:
                return default
        elif isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def parse_items(payload: dict) -> list[dict]:
    items = payload.get('items') or payload.get('ItemsResult', {}).get('Items') or []
    parsed = []

    for item in items:
        asin = item.get('asin') or item.get('ASIN')
        title = _get(item, 'itemInfo', 'title', 'displayValue') or _get(item, 'ItemInfo', 'Title', 'DisplayValue')
        url = item.get('detailPageURL') or item.get('detailPageUrl') or item.get('DetailPageURL')
        image = _get(item, 'images', 'primary', 'large', 'url') or _get(item, 'Images', 'Primary', 'Large', 'URL')

        current_price = (
            _get(item, 'offersV2', 'listings', 0, 'price', 'amount') or
            _get(item, 'Offers', 'Listings', 0, 'Price', 'Amount')
        )
        savings_pct = (
            _get(item, 'offersV2', 'listings', 0, 'savingBasis', 'savings', 'percentage') or
            _get(item, 'Offers', 'Listings', 0, 'SavingBasis', 'Savings', 'Percentage') or
            0
        )

        if not asin or not title or not url or current_price in (None, ''):
            continue

        try:
            current_price = float(current_price)
        except Exception:
            continue

        try:
            savings_pct = int(savings_pct or 0)
        except Exception:
            savings_pct = 0

        parsed.append({
            'asin': asin,
            'title': title,
            'url': url,
            'image': image,
            'price': current_price,
            'discount_percent': savings_pct,
        })

    return parsed
