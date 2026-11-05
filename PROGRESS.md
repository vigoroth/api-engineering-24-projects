# Course progress — 24 Build-It-Yourself API projects

Workbook: `../03_APIs/` · Solutions: this folder (one GitHub-ready folder per project)

## Environment

- Conda env: **`apis24`**. Python 3.13.18, Miniconda 26.1.1 (`C:\Users\nkantiotis\AppData\Local\miniconda3`; not on PATH, so call `Scripts\conda.exe`)
- Libraries added per project:
  - P01 (2026-10-30): fastapi 0.162.0, starlette 1.10.0, pydantic 2.14.2, uvicorn[standard] 0.54.0, httpx 0.28.1, pytest 9.2.0

## Projects

| # | Project | Status | Started | Finished | Folder |
|---|---|---|---|---|---|
| 01 | Your first HTTP API | **Done** | 2026-10-30 | 2026-11-05 | [01-first-http-api](01-first-http-api/) |
| 02 | Paths, query parameters and request schemas | Not started | | | |
| 03 | In-memory CRUD with correct HTTP semantics | Not started | | | |
| 04 | Routers, services, repositories and dependencies | Not started | | | |
| 05 | Persistence, migrations and transactions | Not started | | | |
| 06 | API testing and isolated fixtures | Not started | | | |
| 07 | Stable pagination, filters and ordering | Not started | | | |
| 08 | Consistent errors, OpenAPI and compatibility | Not started | | | |
| 09 | Authentication with a trusted token issuer | Not started | | | |
| 10 | Authorization, object ownership and tenants | Not started | | | |
| 11 | Configuration, secrets and a reproducible deployment | Not started | | | |
| 12 | Async dependencies, timeouts and cancellation | Not started | | | |
| 13 | Idempotent POST requests and duplicate prevention | Not started | | | |
| 14 | Optimistic concurrency and conditional writes | Not started | | | |
| 15 | HTTP caching, conditional GET and invalidation | Not started | | | |
| 16 | Durable background jobs and an outbox | Not started | | | |
| 17 | Signed webhooks, replay defense and an inbox | Not started | | | |
| 18 | SSE streaming, cancellation and backpressure | Not started | | | |
| 19 | Bounded uploads and file-processing APIs | Not started | | | |
| 20 | API traces, metrics, logs and service objectives | Not started | | | |
| 21 | Rate limits, quotas and capacity testing | Not started | | | |
| 22 | Deadlines, circuit breaking and failure recovery | Not started | | | |
| 23 | A versioned model prediction and batch API | Not started | | | |
| 24 | A resilient multi-tenant API platform | Not started | | | |

## Next step

**Start Project 02: Paths, query parameters and request schemas** (workbook: `../03_APIs/projects/02-typed-validation/`). First read its `docs/SPEC.md` and `docs/BUILD_PLAN.md`, then Milestone 0: create `solutions/02-.../`, copy `run.bat`, `logging.json`, `environment.yml`, `requirements.txt` from P01 and add any new libraries.

Carry over from P01 (open items, see `01-first-http-api/EVIDENCE.md`): `HEAD` → 405 (RFC 9110 §9.1 gap); 422 bodies echo the rejected input; whitespace-only names pass `min_length=1`; repeated query params keep the last value. P02 is about request schemas, so the last two belong there.

## Project 01 — Your first HTTP API (Done 2026-11-05)

Deliverables in `01-first-http-api/`: `app/main.py`, `tests/test_api.py` (34 passed), `scripts/measure.py`, `README.md`, `EVIDENCE.md`, `evidence/latency-2026-11-05.txt`, `docs/theory.pdf` + `docs/request-flow.pdf` (LaTeX sources next to them).

| M | Milestone | Status | Date | Tests (pass/total) | What I learned |
|---|---|---|---|---|---|
| M | Milestone | Status | Date | Tests (pass/total) | What I learned |
|---|---|---|---|---|---|
| 0 | Setup: conda env, requirements, folder | Done | 2026-10-30 | n/a | A conda env isolates Python and libraries. `requirements.txt` pins exact versions so others can reproduce the setup |
| 1 | Two routes + T01 (default "world") | Done | 2026-10-30 | 2/2 | A default FastAPI app has 6 routes (4 docs routes added automatically). A function parameter that isn't in the path becomes a query parameter |
| 2 | T02 (name=Nick) + stable response models | Done | 2026-10-30 | 5/5 | `response_model` filters the outgoing body. Measured: an extra `db_password` key leaks without it and is dropped with it |
| 3 | T03 (81 chars → 422) + JSON media type + boundaries | Done | 2026-10-30 | 12/12 | `Query(min_length, max_length)` rejects input before the handler runs. The 422 body echoes the rejected `input` back to the caller |
| 4 | T04 (unknown path → 404) + /docs regression | Done | 2026-10-30 | 22/22 | Unknown paths return 404 by default, but a trailing slash (`/hello/`) got a 307 redirect with no JSON body. `redirect_slashes=False` makes it a deliberate 404 (R05). Tests need `follow_redirects=False`, or the client hides the 307 |
| 5 | T05 (POST → 405) + timing/logging middleware | Done | 2026-10-30 | 33/33 | The framework already returns 405 with `allow: GET`. Middleware runs for every request, so one typo in it (missing `=`) broke 30/33 tests. `request.url.path` leaves out the query string. A test passing (pytest captures logs) ≠ logs appearing on a real server: that needs a handler (`logging.json`) and `--no-access-log`. From M5 on I write the code myself |
| 6 | T06 (health, no secrets) + README exchange | Done (README + flowchart PDF finished 2026-11-05) | 2026-10-30 → 2026-11-05 | 34/34 | A `monkeypatch.setenv` canary checks for secret leaks and is undone after the test. An indented `def` became a nested function, so pytest silently skipped it (still "33 passed"). Always check that the test count goes up. pytest only provides a fixture you name as a parameter. Commenting out `docs_url/redoc_url/openapi_url=None` (2026-11-05) turned 5 R01 tests red at once: the regression guard works |
| 7 | Theory, tidy-ups, latency, intentional failure, EVIDENCE.md | Done | 2026-11-05 | 34/34 | **Theory:** `HEAD /health` → 405, though RFC 9110 §9.1 says servers MUST support GET and HEAD; `max_length` counts characters, not bytes; repeated `?name=` keeps the last value; a space passes `min_length=1`. **Latency** (1000 sequential requests, localhost): client p50 0.84 ms vs server 0.30 ms for `/health`, so ≈64% of the time is outside my code; validation ≈0.02 ms; a 404 is ≈3× cheaper in-app. Percentiles are stable, max is noise. My `statuses` list printed 200 codes: a set keeps distinct values. **Intentional failure:** a body leak was silently dropped by `response_model` (34 passed); a header leak turned T06 red, but only thanks to the `str(response.headers)` check added in the tidy-up. The old `Server-Timing`-only check would have missed it. A test proves nothing until it has been seen failing |

## Tooling notes (this PC)

- Run command: `uvicorn app.main:app --no-access-log --log-config logging.json`, or double-click `run.bat` (`run.bat 8001` for another port). Copy `run.bat` into each new project. "Port already in use" (Errno 10048) means a server is already running.
- In Git Bash, bare `python`/`python3` hangs (Windows Store alias): use `envs\apis24\python.exe`. `conda run` can't run multi-line `python -c`.
- Git Bash's `curl`, `timeout` and `sort` are blocked: use `C:\Windows\System32\curl.exe`.
- LaTeX → PDF: Tectonic in conda env `latex`: `envs\latex\Library\bin\tectonic.exe file.tex`. `step` is a built-in TikZ key, so don't name a style `step`. Write `-{}-` for `--` in text.
- Starlette 1.10.0 warns that `httpx` with TestClient is deprecated (suggests `httpx2`). Harmless so far.
- When adding a test, check that the count goes up: an indented `def` becomes a nested function and is silently skipped.
