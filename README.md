# backend-lab

## TODO

### Concurrency

- **Write skew** — dwóch lekarzy równocześnie kończy dyżur, choć co najmniej jeden musi zostać. Czy poprawne zapisy różnych rekordów mogą razem złamać regułę? Porównać PostgreSQL REPEATABLE READ i SERIALIZABLE.
- **Deadlocks** — dwa przelewy blokują konta w odwrotnej kolejności. Jak odtworzyć zakleszczenie, rozpoznać przerwaną transakcję i zapobiec problemowi przez stałą kolejność blokad?
- **Check-then-insert** — dwa żądania sprawdzają dostępność tego samego loginu i próbują go utworzyć. Porównać sprawdzanie w aplikacji, UNIQUE i INSERT ON CONFLICT.
- **Concurrent job claiming** — kilku workerów pobiera zadania z Postgresa. Porównać zwykły SELECT, FOR UPDATE i SKIP LOCKED; sprawdzić wyłączne przejęcie zadania oraz zachowanie po awarii workera.
- **Read consistency** — raport odczytuje powiązane dane w kilku zapytaniach podczas równoległego przelewu. Kiedy widzi spójny snapshot, a kiedy miesza stany sprzed i po zmianie?
- **Lock contention** — wiele transakcji aktualizuje jeden gorący rekord. Zmierzyć wpływ długości transakcji, oczekiwania na blokady i timeoutów na przepustowość oraz opóźnienia.
- **Cache stampede** — wielu klientów trafia jednocześnie na wygasły wpis. Jak ograniczyć równoległe odczyty ze źródła, także przy kilku procesach aplikacji?

### Messaging i pozostałe pomysły

- Transactional outbox
- Dead-letter queue (DLQ)
- Idempotent consumer
- Distributed rate limiter
