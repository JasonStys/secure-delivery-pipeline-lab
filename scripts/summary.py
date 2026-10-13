"""Publish actual non-sensitive test/benchmark evidence to Actions summaries. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 24
# variable: evidence — line 27
# variable: content — line 32
# variable: content — line 38
# variable: path — line 39
# variable: stream — line 41
# END CODE MAP

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from delivery.build import test_evidence
from delivery.io import Rejected


def main() -> int:
    """Render collected measurements; missing or failed evidence is explicitly not a success."""
    try:
        evidence = test_evidence(
            Path("artifacts/junit.xml"),
            Path("artifacts/coverage.json"),
            Path("artifacts/benchmark.json"),
        )
        content = (
            "## Measured validation evidence\n\n```json\n"
            + json.dumps(evidence, indent=2)
            + "\n```\n"
        )
    except (Rejected, OSError):
        content = "## Validation evidence\n\nA required gate failed or evidence is unavailable. Inspect the job logs; no passing report was fabricated.\n"
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with Path(path).open("a", encoding="utf-8") as stream:
            stream.write(content)
    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
