# Evidence — Project 02: Paths, query parameters and request schemas

Everything below was observed on this machine on 2026-11-05. Anything not run
says so. Responses are copied from saved output, not retyped from memory.

## Evidence log

| Field | Evidence |
|---|---|
| **Project and repository revision** | Project 02, finished 2026-11-05, in [vigoroth/api-engineering-24-projects](https://github.com/vigoroth/api-engineering-24-projects) (added in `ed4a3c2`; the `-0` fix is the following commit). File blobs (`git hash-object`): `app/main.py` a823ec66, `tests/test_quotes.py` b2fcd890, `tests/test_products.py` e5acafe3. |
| **Hypothesis and changed variable** | *Declarative Pydantic constraints can enforce the whole input contract (R01–R05) before any handler code runs, and a separate public response model enforces R06.* The variables changed, one per milestone: field requiredness, `Field(ge=1)`, `strict=True`, `le=1000` / `ge=0` / `max_digits` / `decimal_places`, `extra="forbid"`, and an internal `ProductRecord` vs public `ProductResponse`. |
| **Environment and versions** | Windows 11 (10.0.26300). Conda env `apis24`: Python 3.13.18, fastapi 0.162.0, starlette 1.10.0, pydantic 2.14.2 (pydantic-core 2.50.2), uvicorn[standard] 0.54.0, httpx 0.28.1, pytest 9.2.0. curl 8.21.0. |
| **Dataset / fixture identity** | No dataset. One seeded product: `3f2b8c1e-7a4d-4e9b-9c6f-1d2e3a4b5c6d` / `Notebook` / canary secret `canary-supplier-password-7d1f`. Unknown-but-valid ID `00000000-0000-4000-8000-000000000000`. All other inputs are literals in the tests. `PRODUCTS` is a module-level dict that no test mutates, so no cleanup is needed. |
| **Tests written and observed outcomes** | `pytest -q` → **23 passed** (2026-11-05, after the `-0` fix; 22 before it). Each test was seen red before green, except where noted below. |
| **Real integration boundaries exercised** | A live uvicorn server on 127.0.0.1:8002 called with curl.exe: 36 requests, plus 3 more after the `-0` fix, saved in [evidence/live-2026-11-05.txt](evidence/live-2026-11-05.txt). |
| **Known mocks and untested assumptions** | The pytest suite uses **TestClient** (in-memory ASGI, no socket, no uvicorn). The live curl run is the only real-server check, and it was done by hand, not automated. `PRODUCTS` is an in-memory dict standing in for a database (P05). |
| **Measured quality / latency / resources** | Not measured in this project. P02 is about correctness of the input contract; latency methodology is in P01. No number is claimed. |
| **Cost assumptions vs measured consumption** | Nothing billable ran: laptop only. |
| **One inspected failure and its cause** | Three are below: `"1e100"` → 500 (found and fixed), `"-0"` → `"-0.00"` (found and fixed), and the intentional removal of `response_model`. |
| **Decision and next change** | Keep declarative constraints, with `strict` only where coercion is dangerous (reasoning in [docs/theory.pdf](docs/theory.pdf), "Design decision"). Next: decide on a strict `unit_price` pattern; then Project 03. |

## Tests (23)

| Area | Test | Red first? | Covers |
|---|---|---|---|
| T01, R03 | `test_t01_total_uses_decimal_arithemetic` | yes (no app, then a 422 caused by my `units_price` typo) | `0.10 × 3` → `{"total":"0.30"}`, whole body |
| T02 | `test_t02_zero_quantity_is_rejected` | yes (200 `"0.00"`) | quantity 0 → 422 |
| R01, R02 | `test_r02_absent_quantity_is_reported_as_missing` | no, passed at once | absent → `missing` at `body.quantity` |
| R02 | `test_r02_null_quantity_is_rejected_not_treated_as_absent` | no, passed at once | `null` → `int_type`, a different error from absent |
| T03 | `test_t03_non_integral_quantity_is_rejected` | no, passed at once | `2.5` → 422 at `body.quantity` |
| R03 | `test_r03_quantity_as_string_is_rejected` | yes (200) | `"3"` → 422 (strict) |
| R03 | `test_r03_quantity_as_whole_float_is_rejected` | yes (200) | `3.0` → 422 (strict) |
| R03 | `test_r03_rounding_is_half_up` | no, passed at once | `0.125` → `"0.13"` |
| R04 boundary | `test_r04_quantity_upper_bound_is_inclusive` | no | 1000 → 200 (**boundary case not in TEST_SPEC**) |
| R04 | `test_r04_quantity_above_upper_bound_is_rejected` | yes (200) | 1001 → 422 |
| R04 boundary | `test_r04_zero_price_is_allowed` | no | `"0"` → `"0.00"` |
| R04 | `test_r04_negative_price_is_rejected` | yes (200 `"-0.01"`) | `-0.01` → 422 |
| R04 regression | `test_r04_huge_price_is_rejected_not_a_server_error` | yes (`InvalidOperation`) | `"1e100"` → 422, not 500 (**independently discovered**) |
| R04 | `test_r04_too_many_decimal_places_is_rejected` | yes (200) | `0.12345` → 422 |
| R04 regression | `test_r04_negative_zero_price_gives_unsigned_zero_total` | yes (`"-0.00"`) | `"-0"` → `{"total":"0.00"}` (**independently discovered**, Failure 2) |
| T05 | `test_t05_missing_price_reports_field_location` | no, passed at once | `missing` at `body.unit_price` |
| R05 | `test_r05_unknown_field_is_rejected` | yes (200) | `discount` → `extra_forbidden` at `body.discount` |
| R05 regression | `test_r05_misspelled_field_reports_both_problems` | yes (only `missing`) | `units_price` → `missing` + `extra_forbidden` (compared as a set) |
| T04 | `test_t04_malformed_product_id_is_rejected` | yes (404, no route) | `not-a-uuid` → 422 at `path.product_id` |
| — | `test_known_product_is_returned` | yes (404) | exact body `{"id","name"}` |
| — | `test_unknown_but_valid_product_id_is_404` | **no, passed for the wrong reason** (no route at all) | means something only next to the 200 test |
| T06 precondition | `test_t06_internal_field_exists_in_storage` | yes (`AttributeError`) | the secret really is stored, so the leak test isn't vacuous |
| T06, R06 | `test_t06_internal_field_is_absent_from_public_response` | yes, in the intentional failure below | key absent from JSON; canary absent from body text and headers |

**Test layers (TEST_SPEC task).** All 23 are in-memory HTTP tests through TestClient.
`test_t06_internal_field_exists_in_storage` also reads the app's internal
`PRODUCTS` dict (white-box, on purpose). None are real integration tests. The real
server boundary was checked by hand with curl. There are no concurrency or recovery
checks; this project has no state that changes.

**Tests that passed on their first run** (the R02 pair, T03, T05, rounding, the
inclusive-bound pair) passed because an earlier milestone already caused the
behavior. They lock that behavior in. The `strict=True` change showed they are not
vacuous: it changed T03's error type from `int_from_float` to `int_type`, and T03
stayed green only because it asserts on status and `loc`, not on library wording.

## Failure 1 — independently discovered: `"1e100"` → 500 (fixed)

- **Found:** a probe of values that the contract didn't mention, before writing the R04 tests.
- **Observed:** `{"unit_price": "1e100", "quantity": 1}` → **500 Internal Server Error**.
  Pydantic parsed it into `Decimal("1E+100")`. `quantize(Decimal("0.01"))` would need
  103 digits, but the default decimal context has 28, so it raised
  `decimal.InvalidOperation`. Any client could crash a request with an 8-character string.
- **Red:** `test_r04_huge_price_is_rejected_not_a_server_error` failed with
  `decimal.InvalidOperation` at `app\main.py:20` (TestClient re-raises server errors).
- **Fix:** `Field(ge=0, max_digits=12, decimal_places=4)`. Max total ≈ 1.0 × 10¹¹, far inside 28 digits.
- **Green:** 14/14. **Live:** 422 `decimal_max_digits`.
- **Lesson:** a number with no upper bound is not validated. Bounds protect the arithmetic, not just the business rule.

## Failure 2 — independently discovered: `"-0"` → `"-0.00"` (fixed)

- **Found:** the live curl probe during M7.
- **Observed:** `{"unit_price": "-0", "quantity": 1}` → **200 `{"total":"-0.00"}`**.
  `Decimal("-0") >= 0` is `True` (negative zero equals zero), so `ge=0` lets it through,
  but `Decimal` keeps the sign through multiplication and `quantize`.
- **Impact:** a client that shows or parses the total gets a minus sign on a zero quote.
  There's no money error, but the response breaks the "nonnegative" promise in its
  text form.
- **Red:** `test_r04_negative_zero_price_gives_unsigned_zero_total` failed with
  `{'total': '-0.00'} != {'total': '0.00'}` (1 failed, 22 passed).
- **Fix:** `total = total + 0` right after `quantize`. In Decimal arithmetic,
  `-0.00 + 0` is `0.00` (the sum of zeros with different signs is positive under
  every rounding mode except `ROUND_FLOOR`), and nonzero totals are unchanged.
  Rejecting `-0` at the boundary was the alternative, but `-0` *is* a valid zero, so
  normalizing the output is less surprising.
- **Green:** 23 passed. **Live:** `"-0"` and `"-0.00"` → `{"total":"0.00"}` (end of
  [evidence/live-2026-11-05.txt](evidence/live-2026-11-05.txt)).
- **Lesson:** a range check compares *values*, and `-0 == 0`. The *text form* the
  client sees needs its own test.

## Failure 3 — intentional: removing `response_model` from `GET /products/{id}`

The handler deliberately returns the whole `ProductRecord`, secret included. With
`response_model=ProductResponse` temporarily deleted:

```
FAILED tests/test_products.py::test_known_product_is_returned
E   Left contains 1 more item:
E   {'supplier_password': 'canary-supplier-password-7d1f'}
FAILED tests/test_products.py::test_t06_internal_field_is_absent_from_public_response
E   assert 'supplier_password' not in {'id': '3f2b8c1e-...', 'name': 'Notebook',
E          'supplier_password': 'canary-supplier-password-7d1f'}
2 failed, 20 passed
```

Restored → 22 passed (before the `-0` test was added). Two separate tests catch the same leak in two different ways:
the exact-body comparison and the canary check.

## Mistakes made during the build (kept because they taught something)

- **`units_price` typo (M1):** gave a 422 `missing`, while the real `unit_price` key
  was silently dropped. Pydantic's default is `extra="ignore"`. This became the R05
  regression test.
- **New code pasted below the old code (M6):** two `PRODUCTS` dicts and two
  `GET /products/{product_id}` routes. Python kept the second dict, FastAPI used the
  **first** route, and the old handler crashed indexing a `ProductRecord`
  (`TypeError: 'ProductRecord' object is not subscriptable`). Neither Python nor
  FastAPI warns about duplicate routes.
- **Deleted one class too many (M6):** `ProductResponse` gone → `NameError` at import,
  and **both** test files failed to collect, because they share `app.main`.

## Not run / still open

- `unit_price` is lax: it accepts JSON numbers, exponents, surrounding spaces, `+`, `_`
  separators and non-ASCII Unicode digits (all seen live). Documented in the README, not tested.
- Unknown **query parameters** are ignored (`?admin=true` → 200). R05 is enforced on the body only.
- 422 bodies echo the rejected `input`. For a `missing` error, that input is the **whole
  request object**, so a secret sent in the body would be echoed back. Not an issue for
  this contract, but it's carried to P08 (error contracts).
- No optional request field exists yet. R01's "optional" half is shown only by the
  absence of defaults, not by a real optional field.
- Alternative UUID spellings (uppercase, no hyphens, `{…}`, `urn:uuid:`) are accepted
  and canonicalized. They're seen live but not pinned by a test.
- No automated real-server test, no concurrency, no CI.
- Carried from P01: `HEAD` → 405.

## What I would simplify or measure next

- **Simplify:** the empty lines and indentation in `app/main.py` around `ProductResponse` / `PRODUCTS`. Nothing functional.
- **Measure next:** whether a strict `unit_price` pattern breaks any realistic client
  input; the latency cost of `strict=True` vs lax (expected to be negligible, but not measured).
