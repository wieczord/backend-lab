from decimal import Decimal


def test_order_and_item_are_seeded(connection_factory):
    connection = connection_factory()

    order = connection.execute(
        "SELECT total_amount, version FROM orders WHERE id = 1"
    ).fetchone()
    item = connection.execute(
        "SELECT order_id, quantity, unit_price FROM order_items WHERE id = 1"
    ).fetchone()

    assert order == (Decimal("10.00"), 0)
    assert item == (1, 1, Decimal("10.00"))
