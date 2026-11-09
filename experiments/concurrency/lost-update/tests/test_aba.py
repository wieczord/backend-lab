from collections.abc import Callable
from decimal import Decimal

import pytest
from psycopg import Connection

from lost_update.compare_and_set import CompareAndSetOrders
from lost_update.optimistic import OptimisticLockConflict, OptimisticOrders
from lost_update.order_items import OrderItems


@pytest.fixture
def replace_product_with_gift_card(
    connection_factory: Callable[[], Connection], order_id: int
) -> Callable[[], None]:
    def replace() -> None:
        with connection_factory() as connection:
            OrderItems(connection).replace_product(
                order_id, "Other product", Decimal("20"), is_eligible_for_discount=True
            )
        with connection_factory() as connection:
            OrderItems(connection).replace_product(
                order_id, "Gift card", Decimal("10"), is_eligible_for_discount=False
            )

    return replace


def test_amount_cas_applies_stale_discount_after_aba(
    connection_factory: Callable[[], Connection],
    order_id: int,
    replace_product_with_gift_card: Callable[[], None],
) -> None:
    """TODO: Explain why amount-based CAS misses the product replacement."""
    with connection_factory() as connection:
        CompareAndSetOrders(connection).apply_discount(
            order_id,
            discount_rate=Decimal("0.10"),
            after_read=replace_product_with_gift_card,
        )

    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0] == Decimal("9.00")


def test_version_check_rejects_stale_discount_after_aba(
    connection_factory: Callable[[], Connection],
    order_id: int,
    replace_product_with_gift_card: Callable[[], None],
) -> None:
    """TODO: Explain why the version detects changes despite the same amount."""
    with pytest.raises(OptimisticLockConflict):
        with connection_factory() as connection:
            OptimisticOrders(connection).apply_discount(
                order_id,
                discount_rate=Decimal("0.10"),
                after_read=replace_product_with_gift_card,
            )

    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0] == Decimal("10.00")
