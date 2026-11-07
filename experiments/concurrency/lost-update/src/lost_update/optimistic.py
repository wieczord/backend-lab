from decimal import Decimal
from typing import Any, Callable

from psycopg import Connection


class OptimisticLockConflict(Exception):
    pass


class OptimisticOrders:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def increase_total_amount(
        self,
        order_id: int,
        amount: Decimal,
        after_read: Callable[[], Any] | None = None,
    ) -> None:
        current_amount, current_version = self.connection.execute(
            "SELECT total_amount, version FROM orders WHERE id = %s", (order_id,)
        ).fetchone()
        if after_read is not None:
            after_read()
        cursor = self.connection.execute(
            "UPDATE orders SET total_amount = %s, version = version + 1 WHERE id = %s AND version = %s",
            (current_amount + amount, order_id, current_version),
        )
        if cursor.rowcount == 0:
            raise OptimisticLockConflict("Version mismatch")
