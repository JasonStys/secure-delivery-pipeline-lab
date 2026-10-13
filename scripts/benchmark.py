"""Measured inventory throughput and reproducible payload gates. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: measure — line 35
# variable: rows — line 37
# variable: index — line 38
# variable: samples — line 40
# variable: _ — line 41
# variable: start — line 42
# variable: result — line 43
# variable: _ — line 49
# variable: peak — line 49
# variable: p95 — line 51
# variable: median — line 52
# definition: main — line 68
# variable: output — line 70
# variable: result — line 72
# END CODE MAP

from __future__ import annotations

import json
import platform
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delivery.io import atomic_write, canonical
from delivery.probe import summarize


def measure() -> dict[str, object]:
    """Measure 30 actual 10,000-row runs; report p95, throughput and traced peak memory."""
    rows = [
        {"id": f"SKU-{index}", "units": 3, "unit_price_usd": "12.34"} for index in range(10_000)
    ]
    samples = []
    for _ in range(30):
        start = time.perf_counter()
        result = summarize(rows)
        samples.append((time.perf_counter() - start) * 1000)
        if result["inventory_value_usd"] != "370200.00":
            raise RuntimeError("benchmark correctness failure")
    tracemalloc.start()
    summarize(rows)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    p95 = sorted(samples)[28]
    median = statistics.median(samples)
    return {
        "schema": 1,
        "rows": len(rows),
        "iterations": len(samples),
        "p50_ms": round(median, 3),
        "p95_ms": round(p95, 3),
        "rows_per_second_at_p50": round(len(rows) * 1000 / median),
        "peak_traced_bytes": peak,
        "python": platform.python_version(),
        "system": platform.system(),
        "limits": {"p95_ms": 1000, "peak_traced_bytes": 8 * 1024 * 1024},
        "passed": p95 < 1000 and peak < 8 * 1024 * 1024,
    }


def main() -> int:
    """Write measured evidence to the ignored artifacts directory; nonzero means a failed gate."""
    output = Path("artifacts")
    output.mkdir(exist_ok=True)
    result = measure()
    atomic_write(output / "benchmark.json", canonical(result))
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
