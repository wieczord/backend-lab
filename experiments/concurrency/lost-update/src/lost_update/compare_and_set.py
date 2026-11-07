from decimal import Decimal
from typing import Callable, Any

from psycopg import Connection


class CompareAndSetConflict(Exception):
    pass


class CompareAndSetOrders:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def increase_total_amount(
        self,
        order_id: int,
        amount: Decimal,
        after_read: Callable[[], Any] | None = None,
    ) -> None:
        current_amount = self.connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0]
        if after_read is not None:
            after_read()
        cursor = self.connection.execute(
            "UPDATE orders SET total_amount = %s WHERE id = %s and total_amount = %s",
            (current_amount + amount, order_id, current_amount),
        )
        if cursor.rowcount == 0:
            raise CompareAndSetConflict(f"Order {order_id} was modified concurrently")
