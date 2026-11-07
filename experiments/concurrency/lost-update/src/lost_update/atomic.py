from decimal import Decimal

from psycopg import Connection


class AtomicOrders:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def increase_total_amount(self, order_id: int, amount: Decimal) -> None:

        self.connection.execute(
            "UPDATE orders SET total_amount = total_amount + %s WHERE id = %s",
            (amount, order_id),
        )
