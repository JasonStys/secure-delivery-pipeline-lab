"""Actual pre-existing alias refusal and ordinary SQLite recovery continuity. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ENTRIES — line 49
# definition: prepared — line 59
# parameter: tmp_path — line 59
# variable: path — line 61
# variable: state — line 62
# variable: identity — line 63
# definition: test_existing_hardlink_refused_before_any_initialization_write — line 69
# parameter: entry — line 69
# parameter: tmp_path — line 69
# variable: _ — line 71
# variable: path — line 71
# variable: outside — line 72
# variable: selected — line 72
# variable: before — line 79
# definition: test_existing_directory_refused_without_reset — line 87
# parameter: entry — line 87
# parameter: tmp_path — line 87
# variable: _ — line 89
# variable: path — line 89
# variable: selected — line 90
# definition: test_existing_symbolic_alias_refused_where_os_allows — line 101
# parameter: dangling — line 101
# parameter: tmp_path — line 101
# variable: _ — line 103
# variable: path — line 103
# variable: outside — line 104
# variable: selected — line 104
# definition: test_ordinary_recovery_sidecars_retain_committed_history — line 119
# parameter: mode — line 119
# parameter: tmp_path — line 119
# variable: identity — line 121
# variable: path — line 121
# variable: script — line 122
# variable: completed — line 135
# variable: sidecar — line 142
# variable: state — line 144
# END CODE MAP

import os
import subprocess
import sys

import pytest

from delivery import desktop_state as module

ENTRIES = (
    "profile.json",
    "instance.lock",
    "history.sqlite",
    "history.sqlite-journal",
    "history.sqlite-wal",
    "history.sqlite-shm",
)


def prepared(tmp_path):
    """Create one real marked app history with an independently checked retained output."""
    path = tmp_path / "profile"
    state = module.Workspace(path, "fixture-app", tmp_path / "installation")
    identity = state.save("fixture", "original intact", {}, {"result.json": b'{"preserved":true}'})
    state.close()
    return path, identity


@pytest.mark.parametrize("entry", ENTRIES)
def test_existing_hardlink_refused_before_any_initialization_write(tmp_path, entry):
    """Every fixed entry is admitted before opening SQLite/locking; outside owned fixtures are unchanged."""
    path, _ = prepared(tmp_path)
    selected, outside = path / entry, tmp_path / "outside-fixture"
    if selected.exists():
        outside.write_bytes(selected.read_bytes())
        selected.unlink()
    else:
        outside.write_bytes(b"inert owned sentinel")
    os.link(outside, selected)
    before = outside.read_bytes()
    with pytest.raises((module.Rejected, OSError)):
        module.Workspace(path, "fixture-app", tmp_path / "installation")
    assert outside.read_bytes() == before
    assert selected.exists() and selected.stat().st_nlink == 2


@pytest.mark.parametrize("entry", ENTRIES)
def test_existing_directory_refused_without_reset(tmp_path, entry):
    """Nonregular fixed entries are rejected, not replaced, interpreted as missing or deleted."""
    path, _ = prepared(tmp_path)
    selected = path / entry
    if selected.exists():
        selected.unlink()
    selected.mkdir()
    (selected / "keep").write_bytes(b"unchanged")
    with pytest.raises((module.Rejected, OSError)):
        module.Workspace(path, "fixture-app", tmp_path / "installation")
    assert (selected / "keep").read_bytes() == b"unchanged"


@pytest.mark.parametrize("dangling", [False, True])
def test_existing_symbolic_alias_refused_where_os_allows(tmp_path, dangling):
    """A pre-existing Windows/POSIX symbolic alias is rejected without following or deleting its target."""
    path, _ = prepared(tmp_path)
    selected, outside = path / "history.sqlite-shm", tmp_path / "outside-fixture"
    if not dangling:
        outside.write_bytes(b"inert owned sentinel")
    try:
        selected.symlink_to(outside)
    except OSError as error:
        pytest.skip("OS cannot create this synthetic symbolic link: " + type(error).__name__)
    with pytest.raises((module.Rejected, OSError)):
        module.Workspace(path, "fixture-app", tmp_path / "installation")
    assert selected.is_symlink() and (
        not outside.exists() if dangling else outside.read_bytes() == b"inert owned sentinel"
    )


@pytest.mark.parametrize("mode", ["WAL", "DELETE"])
def test_ordinary_recovery_sidecars_retain_committed_history(tmp_path, mode):
    """Actual committed WAL and hot rollback-journal files remain usable; no blanket sidecar rejection/deletion."""
    path, identity = prepared(tmp_path)
    script = """
import os,sqlite3,sys
connection=sqlite3.connect(sys.argv[1])
connection.execute('PRAGMA journal_mode='+sys.argv[2])
if sys.argv[2]=='WAL':
 connection.execute('UPDATE run SET summary=? WHERE id=1',('committed through WAL',))
 connection.commit()
else:
 connection.execute('PRAGMA cache_size=1')
 connection.execute('BEGIN IMMEDIATE')
 connection.execute('UPDATE bundle SET payload=? WHERE run_id=1',(b'x'*65536,))
os._exit(0)
"""
    completed = subprocess.run(
        [sys.executable, "-c", script, str(path / "history.sqlite"), mode],
        capture_output=True,
        timeout=5,
        check=False,
    )
    assert completed.returncode == 0
    sidecar = path / ("history.sqlite-wal" if mode == "WAL" else "history.sqlite-journal")
    assert sidecar.is_file() and sidecar.stat().st_size > 0 and sidecar.stat().st_nlink == 1
    state = module.Workspace(path, "fixture-app", tmp_path / "installation")
    try:
        assert state.files(identity) == {"result.json": b'{"preserved":true}'}
        assert state.history()[0]["summary"] == (
            "committed through WAL" if mode == "WAL" else "original intact"
        )
    finally:
        state.close()
