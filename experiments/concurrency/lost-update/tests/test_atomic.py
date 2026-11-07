import threading
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from lost_update.atomic import AtomicOrders


def test_concurrent_increments_preserve_both_changes(connection_factory) -> None:
    barrier = threading.Barrier(2, timeout=5)

    def worker():
        with connection_factory() as connection:
            atomic = AtomicOrders(connection)
            atomic.increase_total_amount(1, Decimal("5.00"))

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker) for _ in range(2)]

        for future in futures:
            future.result(timeout=15)

    with connection_factory() as connection:
        assert connection.execute(
            "SELECT total_amount FROM orders WHERE id = %s", (1,)
        ).fetchone()[0] == Decimal("20.0")
