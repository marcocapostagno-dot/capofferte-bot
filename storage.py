import sqlite3
from contextlib import closing

DB_PATH = 'seen_products.db'


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS seen_products (asin TEXT PRIMARY KEY)')
        conn.commit()


def has_seen(asin: str) -> bool:
    with closing(sqlite3.connect(DB_PATH)) as conn:
        row = conn.execute('SELECT 1 FROM seen_products WHERE asin = ?', (asin,)).fetchone()
        return row is not None


def mark_seen(asin: str):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.execute('INSERT OR IGNORE INTO seen_products (asin) VALUES (?)', (asin,))
        conn.commit()
