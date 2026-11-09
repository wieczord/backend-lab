import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from psycopg import Connection

from lost_update.naive import NaiveOrders


def test_sequential_increments_preserve_both_changes(
    connection_factory: Callable[[], Connection], order_id: int
) -> None:
    """TODO: Describe what this test demonstrates.

    Scenario: TODO — initial state and sequence of operations.
    Expected result: TODO — final state and any errors.
    Why: TODO — explain the mechanism behind the result.
    """

    with connection_factory() as connection:
        naive = NaiveOrders(connection)

        naive.increase_total_amount(order_id, Decimal("5.0"))
        naive.increase_total_amount(order_id, Decimal("5.0"))

    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0] == Decimal("20.0")


def test_concurrent_increments_lose_one_update(
    connection_factory: Callable[[], Connection], order_id: int
) -> None:
    """TODO: Describe what this test demonstrates.

    Scenario: TODO — initial state and sequence of operations.
    Expected result: TODO — final state and any errors.
    Why: TODO — explain the mechanism behind the result.
    """

    barrier = threading.Barrier(2, timeout=5)

    def worker() -> None:
        with connection_factory() as connection:
            orders = NaiveOrders(connection)
            orders.increase_total_amount(
                order_id, Decimal("5.00"), after_read=barrier.wait
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker) for _ in range(2)]

        for future in futures:
            future.result(timeout=15)

    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0] == Decimal("15.0")
