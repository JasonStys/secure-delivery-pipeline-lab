"""Dependency-free inventory release probe with exact cents. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MAX_ROWS — line 34
# variable: MAX_INPUT — line 35
# definition: summarize — line 38
# parameter: rows — line 38
# variable: identifiers — line 42
# variable: units — line 43
# variable: cents — line 44
# variable: row — line 45
# variable: identifier — line 48
# variable: count — line 49
# variable: price — line 50
# variable: units — line 60
# variable: cents — line 61
# definition: main — line 69
# parameter: argv — line 69
# variable: parser — line 71
# variable: arguments — line 74
# variable: result — line 77
# variable: result — line 83
# END CODE MAP

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

MAX_ROWS = 10_000
MAX_INPUT = 1024 * 1024


def summarize(rows: Any) -> dict[str, int | str]:
    """Validate unique stock records and compute USD totals in O(n) time/O(n) ID space."""
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_ROWS:
        raise ValueError("expected 1 to 10000 inventory records")
    identifiers: set[str] = set()
    units = 0
    cents = 0
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "units", "unit_price_usd"}:
            raise ValueError("inventory fields must match the documented schema")
        identifier = row["id"]
        count = row["units"]
        price = row["unit_price_usd"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[A-Z0-9_-]{1,64}", identifier):
            raise ValueError("invalid stock ID")
        if identifier in identifiers:
            raise ValueError("duplicate stock ID")
        if type(count) is not int or not 0 <= count <= 1_000_000:
            raise ValueError("units must be an integer from zero to one million")
        if not isinstance(price, str) or not re.fullmatch(r"(0|[1-9][0-9]{0,9})\.[0-9]{2}", price):
            raise ValueError("price must be a nonnegative decimal USD string with two cents digits")
        identifiers.add(identifier)
        units += count
        cents += int(Decimal(price) * 100) * count
    return {
        "products": len(rows),
        "units": units,
        "inventory_value_usd": f"{cents // 100}.{cents % 100:02}",
    }


def main(argv: list[str] | None = None) -> int:
    """Run a fixed self-test or summarize a bounded user-chosen local JSON inventory."""
    parser = argparse.ArgumentParser(description="Inventory release probe by Jason Stys")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        if arguments.self_test:
            result = summarize([{"id": "DEMO", "units": 3, "unit_price_usd": "0.10"}])
            if result["inventory_value_usd"] != "0.30":
                raise ValueError("self-test failed")
        elif arguments.input:
            from delivery.io import load_json

            result = summarize(load_json(arguments.input, MAX_INPUT))
        else:
            parser.error("choose --input or --self-test")
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError):
        print("Probe rejected the input; see the documented inventory schema.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
