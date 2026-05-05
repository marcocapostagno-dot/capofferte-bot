def build_message(item: dict) -> str:
    title = item['title']
    price = f"{item['price']:.2f}".replace('.', ',')
    discount = item.get('discount_percent', 0)
    url = item['url']

    lines = [
        '🔥 <b>Offerta Amazon</b>',
        '',
        f'<b>{title}</b>',
        f'💶 Prezzo: <b>{price} €</b>',
    ]

    if discount > 0:
        lines.append(f'🏷️ Sconto: <b>-{discount}%</b>')

    lines.extend([
        '',
        f'🛒 <a href="{url}">Apri offerta</a>'
    ])

    return '\n'.join(lines)
