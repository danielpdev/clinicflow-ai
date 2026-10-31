# Design record

## Decision

A suggested appointment is not a booking. A conditional database update claims the slot; the booking and idempotency key commit in the same transaction. Cancellation releases only the slot still owned by that booking.

## Failure model

16 competing attempts for one slot, replayed requests, payload conflicts, cancellation after rebooking, restart persistence and PostgreSQL transactions.

## Tradeoffs

The local model requested clarification in the recorded run despite an explicit date; the transaction benchmark is a system-correctness test, not a model-quality score. The demo has no identity provider or medical functionality.

## Next change to defend in review

Add timezone-aware slot generation and a real patient identity boundary.

## Reproducibility

`uv.lock` pins Python dependencies; the web lockfile pins the React build where present. Model-backed evaluations use a separately installed local service. Dataset examples are synthetic and intentionally small. Reported timing is a local observation, not a throughput SLA. Run `make test` after changing state transitions and `make eval` after changing decisions. Keep inference quality separate from deterministic invariant checks.
