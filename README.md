# API Engineering: 24 Build-It-Yourself Projects

A progressive series of 24 HTTP API projects in Python, from a first two-route
service to a resilient multi-tenant platform. Each project is built test-first
from a written specification, and every claim in it is backed by a test run or
a live measurement.

![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.162-009688)
![Projects](https://img.shields.io/badge/projects-2%20of%2024%20done-orange)

## Projects

| # | Project | Focus | Status |
|---:|---|---|---|
| 01 | [Your first HTTP API](01-first-http-api/) | Routes, status codes, JSON, validation, timing and logging | ✅ Done |
| 02 | [Paths, query parameters and request schemas](02-typed-validation/) | Decimal money, strict types, bounds, extra fields, internal vs public models | ✅ Done |
| 03 | In-memory CRUD with correct HTTP semantics | Methods, idempotency, 201/204/409 | Planned |
| 04 | Routers, services, repositories and dependencies | Layered architecture, dependency injection | Planned |
| 05 | Persistence, migrations and transactions | Database, schema migrations | Planned |
| 06 | API testing and isolated fixtures | Test pyramid, fixture isolation | Planned |
| 07 | Stable pagination, filters and ordering | Cursor pagination | Planned |
| 08 | Consistent errors, OpenAPI and compatibility | Error contracts, API evolution | Planned |
| 09 | Authentication with a trusted token issuer | Tokens, identity | Planned |
| 10 | Authorization, object ownership and tenants | Access control, tenancy | Planned |
| 11 | Configuration, secrets and a reproducible deployment | Settings, secrets, containers | Planned |
| 12 | Async dependencies, timeouts and cancellation | Async I/O | Planned |
| 13 | Idempotent POST requests and duplicate prevention | Idempotency keys | Planned |
| 14 | Optimistic concurrency and conditional writes | ETags, `If-Match` | Planned |
| 15 | HTTP caching, conditional GET and invalidation | Cache contracts | Planned |
| 16 | Durable background jobs and an outbox | Reliable side effects | Planned |
| 17 | Signed webhooks, replay defense and an inbox | Webhook security | Planned |
| 18 | SSE streaming, cancellation and backpressure | Streaming responses | Planned |
| 19 | Bounded uploads and file-processing APIs | Upload limits | Planned |
| 20 | API traces, metrics, logs and service objectives | Observability, SLOs | Planned |
| 21 | Rate limits, quotas and capacity testing | Load testing | Planned |
| 22 | Deadlines, circuit breaking and failure recovery | Resilience | Planned |
| 23 | A versioned model prediction and batch API | Model serving | Planned |
| 24 | A resilient multi-tenant API platform | Capstone | Planned |

Detailed milestone log and lessons learned: [PROGRESS.md](PROGRESS.md).

## Repository layout

Each project is a self-contained folder with its own README:

```
NN-project-name/
├── README.md          how to run it, one complete request/response explained
├── EVIDENCE.md        test results, measurements, failures found, what is untested
├── app/               the API
├── tests/             automated tests (pytest)
├── scripts/           measurement tools
├── evidence/          raw measurement output
├── docs/              theory, scope, references and diagrams (PDF + LaTeX source)
├── requirements.txt   exact dependency versions
└── environment.yml    conda environment
```

## Method

Every project follows the same loop:

1. **Specify:** restate the requirements and the minimum behavioral test cases.
2. **Test first:** write a failing test for one behavior, then the code that passes it.
3. **Measure, don't assume:** framework defaults are checked against a live server
   (curl, real TCP), not taken from documentation.
4. **Break it on purpose:** each project records at least one failure it discovered
   and one deliberate failure that proves a test can catch it.
5. **Record evidence:** versions, test counts, latency percentiles and known
   limitations go into `EVIDENCE.md`. Unmeasured numbers are never filled in.

## Running a project

```bash
conda env create -f NN-project-name/environment.yml
conda activate apis24
cd NN-project-name
python -m pytest -q
uvicorn app.main:app --no-access-log --log-config logging.json
```

Each project README lists its exact run command and expected test count.

## Tech stack

Python 3.13 · FastAPI · Pydantic · Starlette · uvicorn · httpx · pytest ·
LaTeX/TikZ (Tectonic) for documentation.

## Acknowledgement

The project specifications come from the *APIs: Build It Yourself* workbook
(24 specification-only projects). All implementations, tests, measurements and
documentation in this repository are my own work.
