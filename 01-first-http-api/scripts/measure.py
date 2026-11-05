"""Measure the latency of the running API, from the client and from the server.

Start the server first (run.bat), then from the project folder:
    python scripts/measure.py          # 200 requests per route
    python scripts/measure.py 1000     # or choose the number
"""

import sys
import time


import httpx


BASE_URL = "http://127.0.0.1:8000"
ROUTES = ["/health", "/hello?name=Nick", "/nope"]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
WARMUP = 10


def percentile(values, p):
    # Nearest-rank percentile: sort, then pick the value p% of the way along.
    ordered = sorted(values)
    index = round(p/100 * (len(ordered) - 1))
    return ordered[index]

def server_ms(response):
    # The middleware sends "server-timing: app;dur=2.08". Return 2.08 as a number.
    return float(response.headers["server-timing"].split("dur=")[1])


def measure(client, path):
    # Warm up: open the connection and warm caches; these times are thrown away.
    for _ in range(WARMUP):
        client.get(path)

    client_times = []
    server_times = []
    statuses = set()

    for _ in range(N):
        start = time.perf_counter()
        response = client.get(path)
        client_times.append((time.perf_counter() - start) * 1000)
        server_times.append(server_ms(response))
        statuses.add(response.status_code)
    return client_times, server_times, statuses


def main():
    print(f"{N} requests per route to {BASE_URL} (after {WARMUP} warm-up requests)")
    print(f"{'route':18} {'status':>6} {'client p50':>10} {'p95':>6} {'max':>6}"
          f" {'server p50':>10} {'p95':>6}   (ms)")
    with httpx.Client(base_url=BASE_URL) as client:
        for path in ROUTES:
            c, s, statuses = measure(client, path)
            status_text = ",".join(str(code) for code in sorted(statuses))
            print(f"{path:18} {status_text:>6} {percentile(c, 50):10.2f}"
                  f" {percentile(c, 95):6.2f} {max(c):6.2f}"
                  f" {percentile(s, 50):10.2f} {percentile(s, 95):6.2f}")


if __name__ == "__main__":
    main()