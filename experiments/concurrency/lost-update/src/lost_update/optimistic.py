from collections.abc import Callable
from decimal import Decimal

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
        after_read: Callable[[], object] | None = None,
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

    def apply_discount(
        self,
        order_id: int,
        discount_rate: Decimal,
        after_read: Callable[[], object] | None = None,
    ) -> None:
        """Apply a fractional rate (e.g. 0.10) to the lab's single eligible item."""
        current_amount, current_version, is_eligible_for_discount, item_amount = (
            self.connection.execute(
                """
            SELECT o.total_amount, o.version, i.is_eligible_for_discount, i.quantity * i.unit_price
            FROM orders o JOIN order_items i ON i.order_id = o.id
            WHERE o.id = %s
            """,
                (order_id,),
            ).fetchone()
        )
        if not is_eligible_for_discount:
            return
        discount = (item_amount * discount_rate).quantize(Decimal("0.01"))
        if after_read is not None:
            after_read()
        cursor = self.connection.execute(
            "UPDATE orders SET total_amount = %s, version = version + 1 WHERE id = %s AND version = %s",
            (current_amount - discount, order_id, current_version),
        )
        if cursor.rowcount == 0:
            raise OptimisticLockConflict("Order changed while calculating the discount")
