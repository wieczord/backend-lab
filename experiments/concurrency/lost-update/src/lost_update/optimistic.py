from decimal import Decimal
from typing import Any, Callable

from psycopg import Connection


class OptimisticLockConflict(Exception):
    pass


class OptimisticOrders:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def increase_total_amount(
        self,
        order_id: int,
        amount: Decimal,
        after_read: Callable[[], Any] | None = None,
    ) -> None:
        raise NotImplementedError
