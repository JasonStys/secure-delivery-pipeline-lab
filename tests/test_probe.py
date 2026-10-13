"""Inventory schema, exact arithmetic, CLI and property regressions by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: row — line 29
# parameter: changes — line 29
# definition: test_exact_cents — line 34
# definition: test_invalid_inventory — line 64
# parameter: rows — line 64
# definition: test_money_property — line 71
# parameter: cents — line 71
# parameter: units — line 71
# variable: result — line 73
# variable: total — line 74
# definition: test_probe_cli — line 78
# parameter: capsys — line 78
# parameter: tmp_path — line 78
# variable: path — line 82
# END CODE MAP

import json
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from delivery.probe import main, summarize


def row(**changes: object) -> dict[str, object]:
    """Construct one valid fictional inventory row with optional invalid field overrides."""
    return {"id": "SENSOR-A", "units": 3, "unit_price_usd": "0.10"} | changes


def test_exact_cents() -> None:
    """Floating-point 0.1 errors must never enter inventory totals."""
    assert summarize([row()]) == {"products": 1, "units": 3, "inventory_value_usd": "0.30"}


@pytest.mark.parametrize(
    "rows",
    [
        None,
        {},
        [],
        [1],
        [row(), row()],
        [row(extra=True)],
        [row(id="../x")],
        [row(id=123)],
        [row(id="x")],
        [row(units=True)],
        [row(units=-1)],
        [row(units=1.1)],
        [row(units=1_000_001)],
        [row(unit_price_usd=1.1)],
        [row(unit_price_usd="NaN")],
        [row(unit_price_usd="01.20")],
        [row(unit_price_usd="1.001")],
        [row(unit_price_usd="-1.00")],
        [row(unit_price_usd="10000000000.00")],
        [row()] * 10001,
    ],
)
def test_invalid_inventory(rows: object) -> None:
    """Reject malformed, duplicate, excessive or ambiguous inventory records."""
    with pytest.raises(ValueError):
        summarize(rows)


@given(units=st.integers(0, 1_000_000), cents=st.integers(0, 999_999_999_999))
def test_money_property(units: int, cents: int) -> None:
    """Across 100 deterministic generated examples, decimal output equals exact integer math."""
    result = summarize([row(units=units, unit_price_usd=f"{cents // 100}.{cents % 100:02}")])
    total = cents * units
    assert result["inventory_value_usd"] == f"{total // 100}.{total % 100:02}"


def test_probe_cli(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Exercise both self-test and real bounded JSON input, then controlled failure."""
    assert main(["--self-test"]) == 0
    assert json.loads(capsys.readouterr().out)["inventory_value_usd"] == "0.30"
    path = tmp_path / "inventory.json"
    path.write_text(json.dumps([row()]), encoding="utf-8")
    assert main(["--input", str(path)]) == 0
    path.write_text("not JSON", encoding="utf-8")
    assert main(["--input", str(path)]) == 2
    with pytest.raises(SystemExit):
        main([])
