"""Actual same-descriptor input bounds and ownership-change cases for selected offline reports. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: test_real_source_bounds_and_hardlink_refusal — line 42
# parameter: tmp_path — line 42
# variable: source — line 44
# variable: limit — line 48
# variable: path — line 48
# definition: test_real_path_replacement_and_growth_are_not_silently_accepted — line 58
# parameter: monkeypatch — line 58
# parameter: tmp_path — line 58
# variable: replacement — line 60
# variable: source — line 60
# variable: actual_open — line 63
# definition: replaced — line 65
# parameter: flags — line 65
# parameter: path — line 65
# variable: stream — line 74
# variable: writer — line 76
# definition: test_real_no_writer_fifo_swap_does_not_block — line 84
# parameter: tmp_path — line 84
# variable: script — line 89
# variable: result — line 104
# definition: test_actual_opened_device_is_refused_by_same_descriptor — line 113
# parameter: monkeypatch — line 113
# parameter: tmp_path — line 113
# variable: source — line 115
# variable: actual_open — line 117
# definition: device — line 119
# parameter: _path — line 119
# parameter: flags — line 119
# END CODE MAP

import hashlib
import os

import pytest

from delivery import inputs as module
from delivery.desktop_io import Rejected


def test_real_source_bounds_and_hardlink_refusal(tmp_path):
    """Exact bytes/hash work; over-limit, missing, directory and multiply linked inputs cannot be admitted."""
    source = tmp_path / "source"
    source.write_bytes(b"abcdef")
    assert module.read_source(source, 6) == b"abcdef"
    assert module.file_hash(source, 6) == hashlib.sha256(b"abcdef").hexdigest()
    for path, limit in ((source, 5), (tmp_path / "missing", 10), (tmp_path, 10)):
        with pytest.raises(Rejected):
            module.read_source(path, limit)
        with pytest.raises(Rejected):
            module.file_hash(path, limit)
    os.link(source, tmp_path / "alias")
    with pytest.raises(Rejected):
        module.read_source(source, 6)


def test_real_path_replacement_and_growth_are_not_silently_accepted(tmp_path, monkeypatch):
    """An opened replacement has a different inode; an actual append changes the descriptor's own final metadata."""
    source, replacement = tmp_path / "source", tmp_path / "replacement"
    source.write_bytes(b"initial")
    replacement.write_bytes(b"changed")
    actual_open = module.os.open

    def replaced(path, flags):
        """Perform a real path replacement between the named admission and opened-descriptor check."""
        replacement.replace(source)
        return actual_open(path, flags)

    monkeypatch.setattr(module.os, "open", replaced)
    with pytest.raises(Rejected):
        module.read_source(source, 100)
    monkeypatch.setattr(module.os, "open", actual_open)
    with pytest.raises(Rejected), module.ordinary(source, 100) as stream:
        assert stream.read() == b"changed"
        with source.open("ab") as writer:
            writer.write(b" actual append")


@pytest.mark.skipif(
    os.name == "nt",
    reason="Actual no-writer FIFO swap requires POSIX; real Windows hardlink and opened-device cases remain separate",
)
def test_real_no_writer_fifo_swap_does_not_block(tmp_path):
    """An isolated inert child bounds a genuine regular-to-FIFO replacement; no retry, skip-on-failure or live data."""
    import subprocess
    import sys

    script = """
from pathlib import Path
import os,sys
from delivery import inputs
from delivery.desktop_io import Rejected
source=Path(sys.argv[1]);source.write_bytes(b'fixture')
actual=inputs.os.open
def swapped(path,flags):
 source.unlink();os.mkfifo(source)
 return actual(path,flags)
inputs.os.open=swapped
try:inputs.read_source(source,100)
except Rejected:raise SystemExit(0)
raise SystemExit(1)
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path / "source")],
        timeout=3,
        check=False,
        capture_output=True,
    )
    assert result.returncode == 0


def test_actual_opened_device_is_refused_by_same_descriptor(tmp_path, monkeypatch):
    """A regular named file swapped to an actual NUL/dev-null descriptor is not treated as an empty report."""
    source = tmp_path / "source"
    source.write_bytes(b"retained")
    actual_open = module.os.open

    def device(_path, flags):
        """Open only the OS null device to exercise descriptor-type admission without a blocking read."""
        return actual_open(os.devnull, flags)

    monkeypatch.setattr(module.os, "open", device)
    with pytest.raises(Rejected):
        module.read_source(source, 100)
    assert source.read_bytes() == b"retained"
