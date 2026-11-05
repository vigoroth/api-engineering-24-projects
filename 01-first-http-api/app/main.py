"""A minimal HTTP API with exactly two routes: GET /health and GET /hello.

Run locally:   uvicorn app.main:app --reload --no-access-log --log-config logging.json
"""

import logging
import time

from fastapi import FastAPI, Query, Request, Response
from pydantic import BaseModel


access_log = logging.getLogger("app.access")


# --- Response models: the stable shape of every response body (R02) ---------
#
# A Pydantic model declares field names and types. Used as a route's
# response_model, it filters the outgoing data: undeclared fields are dropped
# and missing ones cause a server error instead of a silently broken body.

class HealthResponse(BaseModel):
    # The health body has exactly one string field: {"status": "ok"}
    status: str


class GreetingResponse(BaseModel):
    # The hello body has exactly one string field: {"greeting": "Hello, ...!"}
    greeting: str


# --- Application ---------------------------------------------------------------
#
# The application object. uvicorn imports it by the name "app" (app.main:app).
#
# FastAPI normally adds four extra routes: /docs, /docs/oauth2-redirect,
# /redoc and /openapi.json (measured with FastAPI 0.162.0). The spec says
# "exactly two routes" (R01), so we switch them all off.
# Setting openapi_url=None also removes the docs pages, because they depend on it.
#
# redirect_slashes defaults to True: GET /hello/ is then answered with a
# 307 redirect to /hello (empty body, no JSON). That status is not one we
# chose (R05), so we turn it off and /hello/ becomes an ordinary 404 (T04).
app = FastAPI(
    title="First HTTP API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    redirect_slashes=False,
)

@app.middleware("http")
async def time_and_log(request: Request, call_next) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["Server-Timing"] = f"app;dur={duration_ms:.2f}"
    access_log.info(f"{request.method} {request.url.path} {response.status_code} {duration_ms:.2f}ms")
    return response



# --- Routes ----------------------------------------------------------------------

# The decorator registers the function below for method GET on path /health.
# Any other method on /health -> 405; any other path -> 404 (handled by the framework).
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    # FastAPI serializes the model to JSON and sets
    # Content-Type: application/json for us (R03).
    return HealthResponse(status="ok")


@app.get("/hello", response_model=GreetingResponse)
def hello(
    # Query(...) says "read this from the query string" and attaches rules:
    #   "world"       -> default when ?name is absent (T01)
    #   min_length=1  -> ?name= (empty) is rejected with 422
    #   max_length=80 -> 81+ characters are rejected with 422 (R04, T03)
    # FastAPI checks these BEFORE calling hello(), so bad input never reaches
    # this function; the framework builds the 422 JSON response itself.
    name: str = Query("world", min_length=1, max_length=80),
) -> GreetingResponse:
    return GreetingResponse(greeting=f"Hello, {name}!")
