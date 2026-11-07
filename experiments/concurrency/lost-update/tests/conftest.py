from contextlib import ExitStack
from pathlib import Path

import psycopg
import pytest


DATABASE_URL = "postgresql://lab:lab@127.0.0.1:55432/lost_update"


@pytest.fixture(scope="session")
def database_url():
    return DATABASE_URL


@pytest.fixture(scope="session")
def schema(database_url):
    sql = Path(__file__).with_name("schema.sql").read_text()
    with psycopg.connect(database_url, connect_timeout=5) as connection:
        connection.execute(sql)


@pytest.fixture(autouse=True)
def reset_data(database_url, schema):
    with psycopg.connect(database_url, connect_timeout=5) as connection:
        connection.execute("TRUNCATE order_items, orders RESTART IDENTITY")
        connection.execute("INSERT INTO orders (total_amount) VALUES (10.00)")
        connection.execute(
            """
            INSERT INTO order_items (order_id, product_name, quantity, unit_price)
            VALUES (1, 'Example product', 1, 10.00)
            """
        )


@pytest.fixture
def connection_factory(database_url, reset_data):
    with ExitStack() as stack:

        def connect():
            connection = psycopg.connect(
                database_url,
                connect_timeout=5,
                options="-c statement_timeout=10000 -c lock_timeout=5000",
            )
            connection.isolation_level = psycopg.IsolationLevel.READ_COMMITTED
            stack.callback(connection.close)
            return connection

        yield connect
