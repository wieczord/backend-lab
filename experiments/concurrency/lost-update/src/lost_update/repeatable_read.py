from collections.abc import Callable
from decimal import Decimal

import psycopg
from psycopg import Connection


class RepeatableReadOrders:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def increase_total_amount(
        self,
        order_id: int,
        amount: Decimal,
        after_read: Callable[[], object] | None = None,
    ) -> None:
        if self.connection.isolation_level != psycopg.IsolationLevel.REPEATABLE_READ:
            self.connection.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
        current_amount = self.connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0]

        if after_read is not None:
            after_read()

        self.connection.execute(
            "UPDATE orders SET total_amount = %s WHERE id = %s",
            (current_amount + amount, order_id),
        )
