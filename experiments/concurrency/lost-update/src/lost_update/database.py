import psycopg


def connect(database_url: str) -> psycopg.Connection:
    return psycopg.connect(database_url, connect_timeout=5)
