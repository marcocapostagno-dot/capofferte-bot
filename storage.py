import sqlite3
from contextlib import closing

from settings import DB_PATH


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sent_items (
                asin TEXT PRIMARY KEY,
                title TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def has_been_sent(asin: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT 1 FROM sent_items WHERE asin = ? LIMIT 1", (asin,)).fetchone()
        return row is not None


def mark_as_sent(asin: str, title: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sent_items (asin, title) VALUES (?, ?)",
            (asin, title),
        )
        conn.commit()
