# Lost update

## Goal

TODO: Explain the lost update problem and the question this lab explores.

## Shared scenario

An order starts with a total of `10.00`. Two operations each attempt to increase it by `5.00`.

TODO: Describe the intended outcome and the role of separate connections and transactions. Keep the precise operation ordering in the test docstrings.

## Running the tests

Requirements: Python 3.12 or newer, `uv`, and a running Docker daemon accessible to the current user.
Testcontainers starts PostgreSQL 17 for the tests; no manual database setup is needed.

From the repository root:

```bash
bash experiments/concurrency/lost-update/run.sh
```

Run the tests for a single approach:

```bash
bash experiments/concurrency/lost-update/run.sh tests/test_pessimistic.py -v
```

The script uses `uv run pytest`; `uv` prepares the environment and dependencies.

## Comparison

These outcomes refer to the scenarios arranged by the current tests. Some approaches require retrying an operation to apply both increments.

| Approach | Tested outcome | Strengths | Limitations |
| --- | --- | --- | --- |
| [Naive read-modify-write](docs/naive.md) | 15 — one increment is lost | TODO | TODO |
| [Atomic UPDATE](docs/atomic-update.md) | 20 — both increments are preserved | TODO | TODO |
| [Compare-and-set on amount](docs/compare-and-set.md) | 15 and one conflict | TODO | TODO |
| [Version-based optimistic locking](docs/optimistic-locking.md) | 15 and one conflict | TODO | TODO |
| [Pessimistic locking](docs/pessimistic-locking.md) | 20; separate blocking test: 15 and a lock timeout | TODO | TODO |
| [Repeatable Read](docs/repeatable-read.md) | 15 and one serialization failure | TODO | TODO |

TODO: Complete the comparison after describing each mechanism. Amount-based CAS and version checks are both forms of optimistic concurrency control.

## Where to find details

- `src/lost_update/` — minimal implementations.
- `tests/` — executable scenarios; each test docstring explains the expected behavior and why it occurs.
- `docs/` — notes on mechanisms, limitations, and use cases, linked in the comparison table.

## Takeaways

TODO: Summarize what you learned and which requirements determine the choice of approach.
