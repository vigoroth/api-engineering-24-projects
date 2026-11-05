# Evidence — Project 01: Your first HTTP API

Everything below was observed on this machine. Anything not run says so.
Numbers are copied from saved output, not estimated.

## Evidence log

| Field | Evidence |
|---|---|
| **Project and repository revision** | Project 01, finished 2026-11-05. Not yet in git, so the revision is pinned by SHA-1 hashes: `app/main.py` 6fb849c7, `tests/test_api.py` 3d72a082, `scripts/measure.py` 31f6274a, `logging.json` a8f3411f, `requirements.txt` dfd0cb7e. |
| **Hypothesis and changed variable** | *A single FastAPI file can meet R01–R06 if every framework default is measured and pinned by a test.* The variables changed were framework settings: `docs_url/redoc_url/openapi_url=None` (R01), `redirect_slashes=False` (R05), `response_model` (R02), `Query(min_length=1, max_length=80)` (R04), plus the timing/logging middleware and its run flags. |
| **Environment and versions** | Windows 11 (10.0.26300), Intel64 Family 6 Model 186. Conda env `apis24`: Python 3.13.18, fastapi 0.162.0, starlette 1.10.0, pydantic 2.14.2, uvicorn[standard] 0.54.0, httpx 0.28.1, pytest 9.2.0. curl 8.21.0 (`C:\Windows\System32\curl.exe`). |
| **Dataset / fixture identity** | No dataset. Fixed test inputs: `name=Nick`; names of 80 and 81 × `"a"`; empty name; unknown paths `/nope`, `/`, `/HELLO`, `/hello/extra`, `/hello/`, `/health/`; methods POST/PUT/DELETE/PATCH; log canary name `Alice-Private`; secret canary `DATABASE_PASSWORD=canary-s3cr3t-7f3a` (set by `monkeypatch`, removed after the test). |
| **Tests written and observed outcomes** | `pytest -q` → **34 passed** (2026-11-05). Breakdown below. |
| **Real integration boundaries exercised** | A live uvicorn server on 127.0.0.1:8000, called with curl.exe (200/404/405/422 plus headers, 2026-10-30 and 2026-11-05) and with httpx over real TCP by `scripts/measure.py`. The `app.access` log line was read from the server console. |
| **Known mocks and untested assumptions** | The pytest suite uses FastAPI's **TestClient**: in-memory ASGI calls, no socket, no uvicorn. So the tests do not cover uvicorn's own headers (`date`, `server`), the `--no-access-log` flag or `logging.json`; those were checked live only. `monkeypatch` stands in for a real secret store. Untested: concurrency, multiple workers, real networks, TLS, HTTP/2, very large or malformed requests. |
| **Measured quality / latency / resources** | 1000 sequential requests per route, one keep-alive connection, localhost ([evidence/latency-2026-11-05.txt](evidence/latency-2026-11-05.txt)). See the latency table below. No memory or CPU measurement was taken. |
| **Cost assumptions vs measured consumption** | Nothing billable ran: the laptop only. The workbook worksheet's $0.24 (1 instance × 4 h × $0.06) is a **hypothetical rate**, not measured. Measured consumption: about 3,000 local requests for latency plus test runs. Cost per successful request is undefined: no billed denominator. |
| **One inspected failure and its cause** | Two failures, below: the independently discovered `redirect_slashes` 307, and the intentional T06 leak. |
| **Decision and next change** | Keep the one-file design for P01 (reasoning in [docs/theory.pdf](docs/theory.pdf) §10). Next: Project 02 (paths, query parameters, request schemas). Carry over: `HEAD` → 405 (RFC 9110 §9.1 gap), 422 bodies echo input, whitespace-only names pass validation. |

## Tests (34)

All run through TestClient, i.e. HTTP-level tests of the app in memory. Each one
sends a request and checks the response, except where noted.

| Area | Test | Runs | Covers |
|---|---|---:|---|
| R01 | `test_app_exposes_exactly_two_routes` | 1 | Route table has exactly `/health`, `/hello` (inspects the app object) |
| R01 | `test_auto_generated_docs_routes_stay_disabled` | 4 | `/docs`, `/docs/oauth2-redirect`, `/redoc`, `/openapi.json` → 404 |
| T01 | `test_hello_without_name_greets_world` | 1 | `{"greeting": "Hello, world!"}` |
| T02 | `test_hello_with_name_greets_that_name` | 1 | `Hello, Nick!` |
| R02 | `test_response_models_pin_the_field_names` | 1 | Model fields are exactly `status` / `greeting` |
| R02 | `test_every_route_declares_a_response_model` | 1 | Inspects FastAPI routes (framework-specific) |
| T03, R04 | `test_hello_rejects_name_longer_than_80_chars` | 1 | 81 chars → 422 `string_too_long` |
| Boundary | `test_hello_accepts_name_of_exactly_80_chars` | 1 | 80 chars → 200 (**boundary case not in TEST_SPEC**) |
| Boundary | `test_hello_rejects_empty_name` | 1 | `?name=` → 422 `string_too_short` |
| T04 | `test_unknown_path_returns_404` | 6 | `/nope`, `/`, `/HELLO`, `/hello/extra`, `/hello/`, `/health/` → 404 JSON |
| T05, R05 | `test_unsupported_method_returns_405` | 8 | 4 methods × 2 routes → 405 + `allow: GET` |
| Monitoring | `test_response_carries_its_own_timing` | 1 | `server-timing: app;dur=<ms>` |
| Monitoring | `test_error_responses_are_timed_too` | 1 | A 404 is timed too |
| Monitoring | `test_request_log_line_omits_the_query_string` | 1 | Log line has method/path/status, no name, no `name=` |
| R03 | `test_every_response_is_json` | 4 | 200, 404, 405, 422 all `application/json` |
| T06 | `test_health_returns_ok_without_environment_secrets` | 1 | Canary absent from body and **all** headers |

Test layers (TEST_SPEC task): all 34 are in-memory HTTP tests of the app, and
`test_every_route_declares_a_response_model` and `test_app_exposes_exactly_two_routes`
also inspect framework internals. None are real integration tests. The real
server boundary was checked by hand with curl and by `scripts/measure.py`.

R06 (README with one complete exchange) is a document, checked by hand:
[README.md](README.md).

## Latency (measured 2026-11-05)

`python scripts/measure.py 1000` against `uvicorn app.main:app --no-access-log --log-config logging.json`.

| Route | Status | Client p50 | Client p95 | Client max | Server p50 | Server p95 |
|---|---|---:|---:|---:|---:|---:|
| `/health` | 200 | 0.84 ms | 1.81 ms | 4.46 ms | 0.30 ms | 0.68 ms |
| `/hello?name=Nick` | 200 | 0.87 ms | 1.66 ms | 3.21 ms | 0.33 ms | 0.62 ms |
| `/nope` | 404 | 0.62 ms | 1.22 ms | 5.87 ms | 0.09 ms | 0.14 ms |

*Client* = time measured by httpx around each request. *Server* = the
`server-timing` value from our middleware.

- **Stable:** over 5 runs (3 × 200 requests, 2 × 1000), client p50 stayed within
  0.84–0.89 ms for `/health` and `/hello`; server p50 within 0.30–0.33 ms. Max varied
  from 1.8 to 7.4 ms, so max is noise, while p50/p95 are signal.
- **Most time is outside our code:** for `/health`, 0.84 − 0.30 = 0.54 ms (≈ 64 %)
  is uvicorn, loopback TCP and httpx.
- **Validation is cheap:** `/hello` (validates `name`) costs ≈ 0.02 ms more than `/health`.
- **A 404 is ≈ 3× cheaper in-app** (0.09 vs 0.30 ms): the router rejects it before any
  handler, validation or `response_model` runs.

**Limits:** one machine, localhost, sequential requests (latency, not capacity:
no concurrency or load test), dev server with a single process. `server-timing`
excludes uvicorn's own parsing and writing.

## Failure 1 — independently discovered: trailing slash → 307

- **Found:** while adding T04, a test for `/hello/` and `/health/` (paths not in TEST_SPEC).
- **Observed:** FastAPI's default `redirect_slashes=True` answered `GET /hello/`
  with **307** → `/hello`, with an empty body and no `content-type`. That breaks R03 (JSON)
  and R05 (deliberate statuses). An HTTP client following redirects hides it: the test
  needed `follow_redirects=False` to see the 307.
- **Red:** 2 failed. **Fix:** `FastAPI(redirect_slashes=False)`. **Green:** 22/22.
- **Live check:** curl.exe → `/hello/`, `/health/`, `/nope`, `/docs` all 404 `{"detail":"Not Found"}`.

## Failure 2 — intentional: leaking a secret from `/health` (2026-11-05)

`app/main.py` was backed up (SHA-1 6fb849c7), changed, tested, then restored
(same SHA-1, 34 passed).

**Experiment A — leak into the body.**
```python
return {"status": "ok", "db_password": os.environ.get("DATABASE_PASSWORD")}
```
Result: **34 passed**. Not a test miss: `response_model=HealthResponse` dropped
the undeclared `db_password` key before sending, so nothing leaked. This shows
R02's filter works as a second line of defense.

**Experiment B — leak into a header** (where `response_model` does not reach).
```python
def health(response: Response) -> HealthResponse:
    response.headers["x-debug-db"] = os.environ.get("DATABASE_PASSWORD", "")
```
Result: **1 failed, 33 passed**. The body checks passed. Only the last assert
caught it:
```
>       assert canary not in str(response.headers)
E       'canary-s3cr3t-7f3a' is contained here:
E           bug-db': 'canary-s3cr3t-7f3a', 'server-timing': 'app;dur=1.09'})
```
**The earlier version of that assert would have missed it.** It checked only
`Server-Timing`; re-run against the leaking app it returned *passes: True*.
It was widened to `str(response.headers)` in the 7a tidy-up, minutes before
this experiment.

**Lesson:** a regression test only proves something once it has been seen
failing. T06 passed on its first run (2026-10-30), so until today it was
unproven, and it did in fact have a blind spot.

## Monitoring signals (MONITORING.md, kept local as the brief asks)

| Field | Specification |
|---|---|
| Name and purpose | `app.access` log line + `server-timing` header: one record per request, to see what was asked, how it ended and how long it took. |
| Type and unit | Log: text line `METHOD path status duration`. Duration: milliseconds, 2 decimals, `time.perf_counter()` (monotonic). |
| Numerator / denominator / aggregation | Request count = number of lines; error rate = lines with status ≥ 400 / all lines; latency = p50/p95 over a window (computed offline, e.g. `scripts/measure.py`). |
| Version scope | One process, versions as above; no version label in the line yet. |
| Window, minimum evidence, missing data | Local inspection only. ≥ 200 requests before quoting a percentile. No line for a request = logging misconfigured (no `logging.json`), not "no traffic". |
| Safe dimensions and cardinality | Method (≤ 7 values), status (≈ 4), path. Path is safe here (2 routes + a few 404s). An attacker can create unlimited 404 paths, so aggregate metrics must group unknown paths. |
| Retention and redaction | Query string never logged (`request.url.path`); uvicorn's access log is off (`--no-access-log`) because it prints `?name=...`. No bodies, no headers logged. |
| Owner and diagnostic action | Me. A rise in 404/405/422 means the clients are wrong (check what they send); 5xx means our code is (none observed). No automatic restart: `/health` is liveness only. |

**Failure drill:** T04 (`GET /nope`) is diagnosable from the signals alone:
`app.access GET /nope 404 0.19ms` plus `server-timing: app;dur=0.19`. The 0.09–0.19 ms
duration (vs 0.30 for `/health`) shows the request never reached a handler, so the
failing boundary is routing, not our code.

## Not run / still open

- No git repository yet, so there's no commit hash (SHA-1 file hashes are used instead).
- No concurrency, load or multi-worker test (Project 21).
- No CI.
- `HEAD /health` → 405, against RFC 9110 §9.1 ("MUST support GET and HEAD"). Measured, not fixed.
- Whitespace-only names (`?name=%20`) pass validation. Repeated `?name=` keeps the last value.
- Starlette 1.10.0 warns that `httpx` with TestClient is deprecated. Harmless today.

## What I would simplify or measure next

- **Simplify:** nothing to remove. Each line maps to a requirement or a measured default.
- **Measure next:** memory per request; latency under concurrent clients; the cost of
  the middleware itself (run with and without it); latency with uvicorn's access log
  on vs off.
