"""Measures how long the app takes to prepare a walk, to put real numbers in the post.

Needs the app running (make run). Only uses the standard library:

    python3 scripts/benchmark.py              # 5 walks against http://localhost:8000
    python3 scripts/benchmark.py 10 http://my-app.onrender.com

Tip: run it once with Gemma cold (restart Ollama first) and once warm, and again against the
GPU Droplet, so the post can compare them.
"""

import json
import statistics
import sys
import time
import urllib.request
import uuid

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 5
BASE = (sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000").rstrip("/")


def call(path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(f"{BASE}/api{path}", data=data, method="POST",
                                     headers={"Content-Type": "application/json"})
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=120) as response:
        body = response.read()
    return time.perf_counter() - started, body


def main():
    seconds, _ = call("/warmup")
    print(f"warm-up (loads the model): {seconds:.1f}s")

    times = []
    for language in ["es", "en"] * RUNS:
        payload = {"user_id": f"bench-{uuid.uuid4()}", "mood": "calm", "minutes": 30, "weather": "sunny",
                   "challenges_count": 3, "note": "Día largo, quiero algo tranquilo.", "language": language}
        seconds, body = call("/walks", payload)
        walk_id = json.loads(body)["id"]
        with urllib.request.urlopen(f"{BASE}/api/walks/{walk_id}") as response:
            first = json.loads(response.read())["challenges"][0]["text"]
        times.append(seconds)
        print(f"walk ({language}): {seconds:.1f}s  ->  {first}")

    print(f"\n{len(times)} walks: median {statistics.median(times):.1f}s, "
          f"fastest {min(times):.1f}s, slowest {max(times):.1f}s")
    print("If every walk takes under ~1s with the same text, Ollama was probably down and the template fallback answered.")


main()
