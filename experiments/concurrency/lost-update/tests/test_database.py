from decimal import Decimal


def test_order_and_item_are_seeded(connection_factory, order_id):
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
