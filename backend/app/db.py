import psycopg

from app.config import database_url


def connect(url: str | None = None) -> psycopg.Connection:
    return psycopg.connect(url or database_url())
