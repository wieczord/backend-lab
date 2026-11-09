from decimal import Decimal

from psycopg import Connection


class OrderItems:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def replace_product(
        self,
        order_id: int,
        product_name: str,
        unit_price: Decimal,
        *,
        is_eligible_for_discount: bool,
    ) -> None:
        """Replace the lab order's single item and update its total and version.

        The caller commits the item and order changes in one transaction.
        """
        self.connection.execute(
            "UPDATE order_items SET product_name = %s, quantity = 1, unit_price = %s, is_eligible_for_discount = %s WHERE order_id = %s",
            (product_name, unit_price, is_eligible_for_discount, order_id),
        )
        self.connection.execute(
            "UPDATE orders SET total_amount = %s, version = version + 1 WHERE id = %s",
            (unit_price, order_id),
        )
