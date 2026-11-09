import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import psycopg
from psycopg import Connection

from lost_update.repeatable_read import RepeatableReadOrders


def test_concurrent_increments_detect_conflict(
    connection_factory: Callable[[], Connection], order_id: int
) -> None:
    """Both transactions read 10 before writing; one commits 15, one aborts.

    PostgreSQL rejects the second update because its snapshot is stale.
    """

    barrier = threading.Barrier(2, timeout=5)

    def worker() -> None:
        with connection_factory() as connection:
            repeatable_read = RepeatableReadOrders(connection)
            repeatable_read.increase_total_amount(
                order_id, Decimal("5.00"), after_read=barrier.wait
            )

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker) for _ in range(2)]

        conflicts = 0
        for future in futures:
            try:
                future.result(timeout=15)
            except psycopg.errors.SerializationFailure:
                conflicts += 1

    assert conflicts == 1
    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (order_id,)
        ).fetchone()[0] == Decimal("15.0")
