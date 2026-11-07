import psycopg


DATABASE_URL = "postgresql://lab:lab@127.0.0.1:55432/lost_update"


def connect(database_url: str = DATABASE_URL) -> psycopg.Connection:
    return psycopg.connect(database_url, connect_timeout=5)
