from collections.abc import Callable
from decimal import Decimal

from psycopg import Connection


def test_order_and_item_are_seeded(
    connection_factory: Callable[[], Connection], order_id: int
) -> None:
    """TODO: Describe what this test demonstrates.

    Scenario: TODO — initial state and sequence of operations.
    Expected result: TODO — final state and any errors.
    Why: TODO — explain the mechanism behind the result.
    """

    connection = connection_factory()

    order = connection.execute(
        "SELECT total_amount, version FROM orders WHERE id = %s", (order_id,)
    ).fetchone()
    item = connection.execute(
        "SELECT order_id, quantity, unit_price FROM order_items WHERE order_id = %s",
        (order_id,),
    ).fetchone()

    assert order == (Decimal("10.00"), 0)
    assert item == (order_id, 1, Decimal("10.00"))
