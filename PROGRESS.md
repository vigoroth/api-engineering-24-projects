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
| 02 | Paths, query parameters and request schemas | **Done** | 2026-11-05 | 2026-11-05 | [02-typed-validation](02-typed-validation/) |
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

**P03 Milestone 0:** setup for *In-memory CRUD with correct HTTP semantics* (read `../03_APIs/projects/03-*/`).

Standing rule (2026-11-05): every project's theory doc ends with a **project scope** section and **clickable reference links**.

## Project 02 — Paths, query parameters and request schemas (Done 2026-11-05)

Deliverables in `02-typed-validation/`: `app/main.py`, `tests/test_quotes.py` + `tests/test_products.py` (23 passed), `README.md`, `EVIDENCE.md`, `evidence/live-2026-11-05.txt`, `docs/theory.pdf` (+ `.tex`).

Workbook: `../03_APIs/projects/02-typed-validation/` (the files are in the folder root, not in `docs/`). Contract: `POST /quotes` takes `unit_price` (a nonnegative decimal string) and `quantity` (int 1–1000) and returns `total` as a decimal string with 2 decimal places. `GET /products/{product_id}` validates UUID syntax. Extra fields are rejected. R01 required/optional · R02 null vs absent · R03 Decimal + explicit rounding · R04 bounds · R05 reject extra fields · R06 internal fields hidden. T01 0.10×3=0.30 · T02 qty 0→422 · T03 non-integral qty→422 · T04 bad UUID→422 · T05 missing price→422 with location · T06 password-like internal field absent.

| M | Milestone | Status | Date | Tests (pass/total) | What I learned |
|---|---|---|---|---|---|
| 0 | Setup: folder, copied run.bat/logging.json/env/requirements/pyproject/.gitignore | Done | 2026-11-05 | n/a | No new libraries: `decimal` and `uuid` are in the standard library |
| 1 | Required/optional fields + T01 (0.10 × 3 = 0.30) | Done | 2026-11-05 | 1/1 | A Pydantic model parameter is read from the JSON body. Send money as a decimal string: `Decimal` × int is exact, `quantize(Decimal("0.01"), ROUND_HALF_UP)` sets the rounding policy (Python's default is HALF_EVEN). My typo `units_price` gave 422 for every client, and the real `unit_price` key was silently ignored, because extra fields are dropped by default. R05 will fix that |
| 2 | Null vs absent + T02 (qty 0 → 422) | Done | 2026-11-05 | 4/4 | Absent and null are different messages: Pydantic reports absent as `missing` and null as `int_type`, both at `loc ["body","quantity"]`. The R02 tests passed right away (no default = required), and T02 was red (0 gave 200 `"0.00"`) until `Field(ge=1)`. `Field` with no default keeps the field required; `Field(1, ge=1)` would make 1 the default |
| 3 | Decimal + rounding + T03 (non-integral qty → 422) | Done | 2026-11-05 | 8/8 | Pydantic's default *lax mode* silently turns `"3"` and `3.0` into int 3 (probed: both 200). Decision: `Field(ge=1, strict=True)` on `quantity` only (`unit_price` must stay lax to parse `"0.10"` into a Decimal). Strict mode changes 2.5's error from `int_from_float` to `int_type`, so tests assert on status + loc, not library wording. `0.125` → `"0.13"` locks in ROUND_HALF_UP (HALF_EVEN would give 0.12). Open: `unit_price` still accepts a JSON number (0.1) and exponent strings (`"1e2"` → 100.00) |
| 4 | Bounds + T04 (bad UUID → 422) | Done | 2026-11-05 | 17/17 | **Found a bug myself:** `unit_price: "1e100"` → **500**, because `quantize` needs 103 digits and the decimal context has 28 → `InvalidOperation`. Fix: `Field(ge=0, max_digits=12, decimal_places=4)`, so the max total ≈ 10¹¹ fits easily. Negative price and qty 1001 were also accepted (200) before `ge=0` / `le=1000`. Test boundary pairs (1000 ✅ / 1001 ❌, 0 ✅ / -0.01 ❌). `GET /products/{product_id}: UUID`: malformed → 422 `loc ["path","product_id"]`, well-formed but unknown → 404. The 404 test was green before the route existed (route-missing 404), so it only means something next to the 200 test. Probed: uppercase, no-hyphen, `{braces}` and `urn:uuid:` spellings are all accepted and canonicalized to lowercase in the response (documented coercion) |
| 5 | Reject extra fields + T05 (missing price → 422 with location) | Done | 2026-11-05 | 20/20 | Pydantic's default `extra="ignore"` silently drops unknown keys (a client's `discount` would be ignored and they'd pay full price). `model_config = ConfigDict(extra="forbid")` on the request model only → `extra_forbidden` with `loc`. My M1 typo is now a regression test: `units_price` gives two errors (missing `unit_price` + extra_forbidden `units_price`), compared as a set of `(type, tuple(loc))` so order doesn't matter. T05 passed already (required since M1). Open: **unknown query parameters** are still ignored (`/products/{id}?admin=true` → 200, `/quotes?unit_price=999` ignored); R05 is enforced on the body only |
| 6 | Internal fields hidden + T06 | Done | 2026-11-05 | 22/22 | Two models per resource: `ProductRecord` (internal, has `supplier_password`) vs `ProductResponse` (public, `id`+`name`). The handler returns the whole record on purpose; `response_model` re-validates it into the public shape. T06 has a **precondition test** (the canary secret really is stored), so the leak test isn't vacuous. **Intentional failure:** removing `response_model` → 2 red (exact-body test: "Left contains 1 more item: supplier_password"; T06: key in JSON) → restored → 22 green. Mistakes along the way: pasting the new block below the old one left two `PRODUCTS` and two routes; FastAPI used the *first* route (old handler indexing a `ProductRecord` → TypeError), with no warning about duplicate routes. Deleting too much (`ProductResponse`) → NameError at import, which broke *both* test files |
| 7 | Theory, measurements, EVIDENCE.md, push | Done | 2026-11-05 | 22/22 | Live curl check (36 requests, `evidence/live-2026-11-05.txt`) found a **second bug**: `"-0"` → `{"total":"-0.00"}`, because −0 passes `ge=0` and Decimal keeps the sign. **Fixed the same day:** regression test red (`'-0.00' != '0.00'`), then `total = total + 0` after `quantize` → 23 passed, confirmed live. A range check compares values (−0 == 0); the text form the client sees needs its own test. It also showed that `Decimal()` accepts `" 0.10 "`, `"+0.10"`, `"1_0"` and Arabic-Indic digits. Theory PDF ends with **Scope** + **References** (19 links; 14 checked 200, the 5 fastapi.tiangolo.com links not checkable here because of a local TLS certificate error). README documents rounding, bounds and the coercion table |

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

- GitHub: https://github.com/vigoroth/api-engineering-24-projects (public, created 2026-11-05). This `solutions/` folder is the repo root; each project is a subfolder with its own README, and the root README holds the 24-project table. Commit author is `Nick Kantiotis <62105877+vigoroth@users.noreply.github.com>` (set per repo), with no co-author lines. gh has two accounts: `vigoroth` (personal, active) and `nkantiotis`. Switch with `gh auth switch`. After each finished project: update the root README table and badge, then commit and push.

- Run command: `uvicorn app.main:app --no-access-log --log-config logging.json`, or double-click `run.bat` (`run.bat 8001` for another port). Copy `run.bat` into each new project. "Port already in use" (Errno 10048) means a server is already running.
- In Git Bash, bare `python`/`python3` hangs (Windows Store alias): use `envs\apis24\python.exe`. `conda run` can't run multi-line `python -c`.
- Git Bash's `curl`, `timeout` and `sort` are blocked: use `C:\Windows\System32\curl.exe`.
- LaTeX → PDF: Tectonic in conda env `latex`: `envs\latex\Library\bin\tectonic.exe file.tex`. `step` is a built-in TikZ key, so don't name a style `step`. Write `-{}-` for `--` in text.
- Starlette 1.10.0 warns that `httpx` with TestClient is deprecated (suggests `httpx2`). Harmless so far.
- When adding a test, check that the count goes up: an indented `def` becomes a nested function and is silently skipped.
