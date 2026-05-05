from html import escape


def build_caption(product: dict) -> str:
    title = escape(product["title"])
    url = escape(product["url"], quote=True)
    price = escape(str(product.get("price_display") or product.get("price_amount") or ""))
    savings = escape(str(product.get("savings_percent") or ""))
    keyword = escape(product.get("keyword", ""))
    merchant = escape(product.get("merchant", "Amazon"))
    saving_basis = escape(product.get("saving_basis_display", ""))

    parts = [
        "🔥 <b>OFFERTA AMAZON.IT</b>",
        "",
        f"📦 {title}",
        f"💰 Prezzo: <b>{price}</b>",
        f"📉 Sconto: <b>{savings}%</b>",
    ]

    if saving_basis:
        parts.append(f"🏷️ Prezzo di riferimento: {saving_basis}")
    if keyword:
        parts.append(f"🔎 Keyword: {keyword}")

    for feature in product.get("features", [])[:2]:
        parts.append(f"• {escape(feature)}")

    parts.extend([
        f"🏪 Venditore: {merchant}",
        "",
        f"👉 <a href=\"{url}\">Vedi offerta su Amazon</a>",
        "",
        "ℹ️ Link affiliato / paid link"
    ])

    return "\n".join(parts)
