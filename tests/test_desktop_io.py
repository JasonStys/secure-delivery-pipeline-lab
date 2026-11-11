"""Private state JSON and bounded descriptor-read boundary cases with actual file bytes. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_regular_exact_limit_and_oversize_rejection — line 26
# parameter: tmp_path — line 26
# variable: path — line 28
# definition: test_ambiguous_invalid_or_nonfinite_json_never_enters_a_saved_bundle — line 50
# parameter: raw — line 50
# definition: test_finite_float_and_canonical_order_are_actual_values — line 56
# definition: test_swapped_opened_descriptor_is_not_an_ordinary_file — line 62
# parameter: monkeypatch — line 62
# parameter: tmp_path — line 62
# variable: path — line 64
# variable: actual — line 66
# definition: opened_device — line 68
# parameter: _path — line 68
# parameter: flags — line 68
# END CODE MAP

import os

import pytest

from delivery import desktop_io as io


def test_regular_exact_limit_and_oversize_rejection(tmp_path):
    """Real bytes at the cap are accepted; one extra byte or a directory never becomes truncated valid data."""
    path = tmp_path / "authorized.json"
    path.write_bytes(b"1234")
    assert io.read_bytes(path, 4) == b"1234"
    with pytest.raises(io.Rejected, match="size limit"):
        io.read_bytes(path, 3)
    with pytest.raises(io.Rejected, match="regular"):
        io.read_bytes(tmp_path, 4)
    with pytest.raises(io.Rejected, match="unavailable"):
        io.read_bytes(tmp_path / "absent", 4)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}',
        b'{"n":NaN}',
        b'{"n":Infinity}',
        b'{"n":1e999}',
        b'"\xff"',
        b"[" * 2000,
    ],
)
def test_ambiguous_invalid_or_nonfinite_json_never_enters_a_saved_bundle(raw):
    """Duplicate keys, exponent overflow, encoding and recursion failures are explicit refusals."""
    with pytest.raises(io.Rejected, match="ambiguous JSON"):
        io.json_value(raw)


def test_finite_float_and_canonical_order_are_actual_values():
    """Valid fractions remain finite numbers and exact order/UTF-8 bytes are stable."""
    assert io.json_value(b'{"n":1.25}') == {"n": 1.25}
    assert io.canonical({"z": "α", "a": 1}) == b'{"a":1,"z":"\\u03b1"}\n'


def test_swapped_opened_descriptor_is_not_an_ordinary_file(tmp_path, monkeypatch):
    """An actual opened null-device descriptor must be rejected even after an ordinary-path precheck."""
    path = tmp_path / "ordinary.json"
    path.write_bytes(b"{}")
    actual = os.open

    def opened_device(_path, flags):
        """Control only the race interleaving; the guard reads a real nonregular descriptor."""
        return actual(os.devnull, flags)

    monkeypatch.setattr(io.os, "open", opened_device)
    with pytest.raises(io.Rejected, match="changed file type"):
        io.read_bytes(path, 4)
