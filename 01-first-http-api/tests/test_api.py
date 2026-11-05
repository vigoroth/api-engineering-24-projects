"""Behavioral tests for the first HTTP API.

Each test sends a real HTTP request *in memory* to the app through
FastAPI's TestClient (built on httpx). No network port is opened, so the
tests are fast and deterministic. They exercise routing, validation and
JSON serialization, but NOT the uvicorn server itself (see EVIDENCE.md).
"""

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from app.main import GreetingResponse, HealthResponse, app

# One client shared by all tests. The app holds no state, so sharing is safe.
client = TestClient(app)


# --- R01: exactly two routes -------------------------------------------------

def test_app_exposes_exactly_two_routes():
    # app.routes lists every route the framework will match, including the
    # ones FastAPI adds automatically (/docs, /redoc, /openapi.json).
    paths = sorted(route.path for route in app.routes)
    assert paths == ["/health", "/hello"]


# --- T01: no name provided -> greeting uses "world" --------------------------

def test_hello_without_name_greets_world():
    response = client.get("/hello")

    assert response.status_code == 200
    assert response.json() == {"greeting": "Hello, world!"}


# --- T02: name is Nick -> greeting includes Nick -----------------------------

def test_hello_with_name_greets_that_name():
    # params= lets httpx URL-encode the value (e.g. spaces -> %20) for us.
    response = client.get("/hello", params={"name": "Nick"})

    assert response.status_code == 200
    # Compare the whole body: proves the name arrived AND no extra fields leaked.
    assert response.json() == {"greeting": "Hello, Nick!"}


# --- R02: response fields are stable -----------------------------------------

def test_response_models_pin_the_field_names():
    # model_fields maps field name -> field info; list() gives the names in order.
    # Renaming a field breaks this test before it breaks a client.
    assert list(HealthResponse.model_fields) == ["status"]
    assert list(GreetingResponse.model_fields) == ["greeting"]


def test_every_route_declares_a_response_model():
    # A model that exists but is not attached to its route protects nothing,
    # so check the wiring as well.
    expected = {"/health": HealthResponse, "/hello": GreetingResponse}
    for route in app.routes:
        if isinstance(route, APIRoute):
            assert route.response_model is expected[route.path]





# --- T03 / R04: name length is bounded at 80 characters ----------------------

def test_hello_rejects_name_longer_than_80_chars():
    # "a" * 81 builds a string one character over the limit.
    response = client.get("/hello", params={"name": "a" * 81})

    # 422 = well-formed HTTP whose content breaks our rules (project contract).
    assert response.status_code == 422
    # loc says WHERE the bad input was: query string, field "name".
    # This proves the 422 came from the name rule and nothing else.
    assert response.json()["detail"][0]["loc"] == ["query", "name"]


def test_hello_accepts_name_of_exactly_80_chars():
    # Boundary: the largest valid value must still succeed (catches off-by-one).
    response = client.get("/hello", params={"name": "a" * 80})

    assert response.status_code == 200
    assert response.json() == {"greeting": f"Hello, {'a' * 80}!"}


def test_hello_rejects_empty_name():
    # Boundary: ?name= sends "", which used to produce "Hello, !".
    response = client.get("/hello", params={"name": ""})

    assert response.status_code == 422


# --- T04 / R05: unknown paths return 404 --------------------------------------

@pytest.mark.parametrize(
    "path",
    [
        "/nope",          # T04: a path that was never defined
        "/",              # the root is not a route either
        "/HELLO",         # paths are case-sensitive
        "/hello/extra",   # a known prefix does not make a longer path valid
        "/hello/",        # trailing slash: the framework default is a 307 redirect
        "/health/",
    ],
)
def test_unknown_path_returns_404(path):
    # follow_redirects=False: report the status the server actually sent.
    # Otherwise the client silently follows a 307 and the test sees the final 200.
    response = client.get(path, follow_redirects=False)

    assert response.status_code == 404
    # Same body FastAPI uses for every 404, so clients can rely on its shape.
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.parametrize(
    "path",
    ["/docs", "/docs/oauth2-redirect", "/redoc", "/openapi.json"],
)
def test_auto_generated_docs_routes_stay_disabled(path):
    # Regression guard for R01: if someone deletes docs_url=None (or the
    # others) from FastAPI(...), these routes come back and this test fails.
    response = client.get(path, follow_redirects=False)

    assert response.status_code == 404


# --- T05 / R05: wrong method on a known path returns 405 ---------------------

@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
@pytest.mark.parametrize("path", ["/hello", "/health"])
def test_unsupported_method_returns_405(method, path):
    # Two stacked parametrize decorators = every combination (4 x 2 = 8 runs).
    response = client.request(method, path)

    assert response.status_code == 405
    assert response.json() == {"detail": "Method Not Allowed"}
    # HTTP requires a 405 to say which methods ARE allowed (RFC 9110 15.5.6).
    assert response.headers["allow"] == "GET"


# --- Measurement: every response is timed and logged -------------------------

def test_response_carries_its_own_timing():
    response = client.get("/health")

    # Server-Timing is the standard header for this; format: app;dur=<ms>
    name, dur = response.headers["server-timing"].split(";dur=")
    assert name == "app"
    assert float(dur) >= 0


def test_error_responses_are_timed_too():
    # Middleware wraps the whole app, so 404s are measured like 200s.
    response = client.get("/nope")

    assert "server-timing" in response.headers


def test_request_log_line_omits_the_query_string(caplog):
    # caplog is a built-in pytest fixture that captures log records.
    secret_name = "Alice-Private"
    with caplog.at_level("INFO", logger="app.access"):
        client.get("/hello", params={"name": secret_name})

    messages = [r.getMessage() for r in caplog.records if r.name == "app.access"]
    assert len(messages) == 1
    # Method, path and status are logged; the user's name is not.
    assert messages[0].startswith("GET /hello 200 ")
    assert secret_name not in messages[0]
    assert "name=" not in messages[0]


# --- R03: every response, success or error, is JSON --------------------------

@pytest.mark.parametrize(
    "method, path",
    [
        ("GET", "/health"),                  # 200
        ("GET", "/nope"),                    # 404
        ("POST", "/hello"),                  # 405
        ("GET", "/hello?name=" + "a" * 81),  # 422
    ],
)
def test_every_response_is_json(method, path):
    # parametrize runs this test once per row above.
    response = client.request(method, path)

    assert response.headers["content-type"] == "application/json"


# --- T06: health reports status and leaks nothing from the environment -------


def test_health_returns_ok_without_environment_secrets(monkeypatch):
    canary = "canary-s3cr3t-7f3a"
    monkeypatch.setenv("DATABASE_PASSWORD", canary)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert canary not in response.text
    assert "DATABASE_PASSWORD" not in response.text
    assert canary not in str(response.headers)
