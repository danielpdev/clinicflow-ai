# ClinicFlow AI

Appointment booking with transactional slots and confirmed agent actions.

[![verification](https://github.com/danielpdev/clinicflow-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/danielpdev/clinicflow-ai/actions/workflows/ci.yml)

**Role focus:** Applied AI / Python Backend / Healthtech. **Status:** working local portfolio implementation, with synthetic data.

![Application screenshot](docs/screenshot.png)

## The engineering decision

A suggested appointment is not a booking. A conditional database update claims the slot; the booking and idempotency key commit in the same transaction. Cancellation releases only the slot still owned by that booking.

```mermaid
flowchart LR
  UI request --> Proposal; MCP --> Availability; Proposal --> Human_confirmation; Human_confirmation --> Transaction; Transaction --> Slots_and_bookings
```

## Run locally

Requirements: Python 3.12, [uv](https://docs.astral.sh/uv/getting-started/installation/) and Make.

```bash
git clone https://github.com/danielpdev/clinicflow-ai.git
cd clinicflow-ai
make setup
make demo
make test
make eval
```

`make demo` uses an isolated temporary database where relevant, so it is safe to repeat. `make eval` writes a timestamped report to `reports/evaluation-fixture.json`. Fixture mode is deterministic and does not represent model inference. There is no recurring hosting or API subscription cost.

For the React interface (Node 22+ and pnpm 11.25.0):

```bash
make web-setup web-build
make serve
```

Open `http://127.0.0.1:8101`. The same server exposes `/docs`.

### Real local model mode

Install Ollama, then in a separate terminal run:

```bash
OLLAMA_HOST=127.0.0.1:11435 OLLAMA_NO_CLOUD=1 ollama serve
```

```bash
OLLAMA_HOST=127.0.0.1:11435 ollama pull qwen3:4b
make eval-local
```

The router also uses `qwen3:1.7b` as fallback; download it explicitly when running that project. No paid API key is required. First-time model/package downloads require internet and disk space. Inference runs locally. A missing model or dependency is an explicit error, never a silent fixture fallback.

### PostgreSQL

The zero-service quickstart uses SQLite. The same SQLAlchemy domain layer also runs on PostgreSQL:

```bash
docker compose up -d postgres
DATABASE_URL=postgresql+psycopg://portfolio:local-demo-only@127.0.0.1:55440/demo make serve
```

`tests/test_postgres.py` uses `POSTGRES_TEST_URL` and drops its test tables during cleanup. Point it only at a dedicated disposable test database. CI provisions one independently. Local demonstration credentials are deliberately non-secret and must never be reused for production.

### MCP transport

```bash
uv run --frozen python -m app.server
```

This starts the official Python SDK 2.3.0 stdio server. Configure your MCP client to launch that command from this repository directory. The exposed availability/proposal tools cannot create bookings. The separate UI/API requires confirmation.

[Watch the recorded demo](docs/demo.webm) · [Reproduce the walkthrough](docs/DEMO.md)

## Verification and evidence

16 competing attempts for one slot, replayed requests, payload conflicts, cancellation after rebooking, restart persistence and PostgreSQL transactions.

- [Evaluation report](reports/evaluation-fixture.json) — measured during an actual run; inspect the mode and dataset size.
- [Development and authorship](docs/DEVELOPMENT.md).
- [Romanian interview preparation](docs/INTERVIEW_RO.md).
- [Design notes](docs/DESIGN.md).
- [Demo walkthrough](docs/DEMO.md).

CI uses standard GitHub-hosted runners and deterministic tests without downloading LLM weights. The lockfiles record exact package versions. Local-model results, when present, live in `reports/evaluation-local.json`; hardware/model identities are in `reports/environment.json`.

## Limits and next iteration

The local model requested clarification in the recorded run despite an explicit date; the transaction benchmark is a system-correctness test, not a model-quality score. The demo has no identity provider or medical functionality.

Next: Add timezone-aware slot generation and a real patient identity boundary.

The local demonstration does not include production authentication, secret management or operational service guarantees. Bind it to localhost and use synthetic data. These projects demonstrate engineering decisions; they do not claim real customers, paid production deployments or guaranteed interviews.

[Explore the complete 20-project portfolio](docs/PORTFOLIO.md)

## Project ownership

Implemented with Codex assistance for Daniel Popa. The owner should review the code, run it, make an independent change and rehearse the tradeoffs before presenting it at interview. That human understanding check is pending and cannot be verified automatically. See [development notes](docs/DEVELOPMENT.md).

MIT for original source; dependencies/models retain their own licenses. See [third-party notices](THIRD_PARTY.md).

## Reproduce browser acceptance

```bash
make web-setup web-build
uv run --frozen --group browser playwright install chromium
uv run --frozen --group browser python scripts/ui_smoke.py
```

The script starts and stops its own local API using a temporary database. It checks a meaningful UI action and mobile overflow.
