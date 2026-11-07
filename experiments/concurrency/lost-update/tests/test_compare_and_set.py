import threading
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from lost_update.compare_and_set import CompareAndSetConflict, CompareAndSetOrders


def test_concurrent_increments_detect_conflict(connection_factory):
    barrier = threading.Barrier(2, timeout=5)

    def worker():
        with connection_factory() as connection:
            orders = CompareAndSetOrders(connection)
            orders.increase_total_amount(1, Decimal("5.00"), after_read=barrier.wait)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(worker) for _ in range(2)]

        conflicts = 0
        for future in futures:
            try:
                future.result(timeout=15)
            except CompareAndSetConflict:
                conflicts += 1

    assert conflicts == 1
