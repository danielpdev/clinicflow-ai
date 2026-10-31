# Demo walkthrough

## Start

```bash
make setup
make demo
make test
make eval
```

## What to show

A suggested appointment is not a booking. A conditional database update claims the slot; the booking and idempotency key commit in the same transaction. Cancellation releases only the slot still owned by that booking.

## Failure case to discuss

16 competing attempts for one slot, replayed requests, payload conflicts, cancellation after rebooking, restart persistence and PostgreSQL transactions.

## Evidence

Open the JSON evaluation report alongside the implementation. Distinguish synthetic fixture outputs, synthetic trace timing, actual elapsed evaluation time, and local model inference. Do not present a tiny test set as a production benchmark.

## Closing tradeoff

The local model requested clarification in the recorded run despite an explicit date; the transaction benchmark is a system-correctness test, not a model-quality score. The demo has no identity provider or medical functionality.

The repository's `docs/demo.webm` or `docs/demo.mp4`, when present, records the demonstration. A terminal replay is also available for focused projects as `docs/demo.cast`.
