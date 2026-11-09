import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal

import psycopg
import pytest
from psycopg import Connection

from lost_update.pessimistic import PessimisticOrders


def test_concurrent_increments_preserve_both_changes(
    connection_factory: Callable[[], Connection], order_id: int
) -> None:
    """Two workers increment 10 by 5; both changes must persist.

    The barrier aligns their start, but does not guarantee lock contention.
    It must precede SELECT FOR UPDATE: waiting for both readers after locking
    would leave the first reader waiting while the second waits for its lock.
    """
    barrier = threading.Barrier(2, timeout=5)

    def worker() -> None:
        with connection_factory() as connection:
            orders = PessimisticOrders(connection)
            barrier.wait()
            orders.increase_total_amount(order_id, Decimal("5.00"))

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker) for _ in range(2)]

        for future in futures:
            future.result(timeout=15)

    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0] == Decimal("20.00")


def test_competing_transaction_times_out_before_reading(
    connection_factory: Callable[[], Connection], order_id: int
) -> None:
    """TODO: Describe the scenario and explain why this test passes."""
    allow_transaction_to_finish = threading.Event()

    def worker() -> None:
        with connection_factory() as connection:
            connection.execute("SET LOCAL lock_timeout = '500ms';")
            orders = PessimisticOrders(connection)
            orders.increase_total_amount(
                order_id,
                Decimal("5.00"),
                after_read=allow_transaction_to_finish.wait,
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker) for _ in range(2)]
        completed_futures = as_completed(futures, timeout=5)
        try:
            timed_out_future = next(completed_futures)
            with pytest.raises(psycopg.errors.LockNotAvailable):
                timed_out_future.result()
        finally:
            allow_transaction_to_finish.set()

        next(completed_futures).result()

    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0] == Decimal("15.00")
