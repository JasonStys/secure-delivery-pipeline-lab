"""Authenticated immutable lab slots and atomic promotion/rollback. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: MARKER — line 60
# definition: owned_root — line 63
# parameter: root — line 63
# variable: allowed — line 72
# variable: path — line 75
# variable: slots — line 78
# definition: deployment_lock — line 84
# parameter: root — line 84
# variable: stream — line 86
# definition: state — line 116
# parameter: root — line 116
# variable: path — line 118
# variable: value — line 121
# variable: name — line 129
# variable: slot — line 130
# definition: health_check — line 139
# parameter: path — line 139
# variable: environment — line 141
# variable: name — line 143
# variable: value — line 143
# variable: result — line 147
# definition: promote — line 161
# parameter: directory — line 162
# parameter: expected_previous — line 162
# parameter: policy — line 162
# parameter: root — line 162
# variable: root — line 166
# variable: previous — line 168
# variable: slot_name — line 171
# variable: slot — line 172
# variable: temporary — line 173
# variable: staged — line 174
# variable: name — line 176
# variable: result — line 188
# definition: rollback — line 193
# parameter: policy — line 193
# parameter: root — line 193
# variable: root — line 195
# variable: expected — line 196
# END CODE MAP

from __future__ import annotations

import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from delivery.io import Rejected, atomic_write, canonical, load_json, read_bytes
from delivery.verify import TrustPolicy, preflight, verify_release

MARKER = {"schema": 1, "purpose": "secure-delivery-pipeline-lab-disposable-deployment"}


def owned_root(root: Path) -> Path:
    """Initialize only a new/empty directory, or recognize this lab's exact existing marker."""
    if root.is_symlink() or root.is_junction() or root.resolve() == Path(root.anchor):
        raise Rejected("invalid deployment root")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not any(root.iterdir()):
        atomic_write(root / "lab.json", canonical(MARKER))
    if load_json(root / "lab.json", 1024) != MARKER:
        raise Rejected("directory is not a disposable lab deployment")
    allowed = {"lab.json", "slots", "active.json", ".lock"}
    if any(
        path.name not in allowed or path.is_symlink() or path.is_junction()
        for path in root.iterdir()
    ):
        raise Rejected("unexpected files or links in deployment root")
    slots = root / "slots"
    slots.mkdir(exist_ok=True, mode=0o700)
    return root.resolve()


@contextlib.contextmanager
def deployment_lock(root: Path) -> Iterator[None]:
    """Take a nonblocking OS lock so concurrent promotions cannot lose the previous pointer."""
    with (root / ".lock").open("a+b") as stream:
        stream.seek(0)
        stream.write(b"0")
        stream.flush()
        stream.seek(0)
        try:
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise Rejected("another promotion is in progress") from error
        try:
            yield
        finally:
            stream.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def state(root: Path) -> dict[str, Any]:
    """Read bounded slot pointers; state data never chooses a trust policy or arbitrary path."""
    path = root / "active.json"
    if not path.exists():
        return {"schema": 1, "active": None, "previous": None}
    value = load_json(path, 4096)
    if (
        not isinstance(value, dict)
        or set(value) != {"schema", "active", "previous"}
        or type(value["schema"]) is not int
        or value["schema"] != 1
    ):
        raise Rejected("invalid deployment state")
    for name in ("active", "previous"):
        slot = value[name]
        if slot is not None and (
            not isinstance(slot, str)
            or not re.fullmatch(r"v[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}-[a-f0-9]{40}", slot)
        ):
            raise Rejected("invalid deployment slot")
    return value


def health_check(path: Path) -> None:
    """Execute ONLY already-authenticated authored probe bytes with a fixed self-test command."""
    environment = {
        name: value
        for name, value in os.environ.items()
        if name in {"PATH", "SystemRoot", "WINDIR", "TEMP", "TMP", "LANG"}
    }
    try:
        result = subprocess.run(
            [sys.executable, "-I", str(path), "--self-test"],
            env=environment,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if result.returncode != 0 or json.loads(result.stdout).get("inventory_value_usd") != "0.30":
            raise Rejected("candidate health check failed; previous release retained")
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        raise Rejected("candidate health check unavailable; previous release retained") from error


def promote(
    directory: Path, root: Path, policy: TrustPolicy, expected_previous: str | None = None
) -> dict[str, Any]:
    """Stage exact asset bytes, authenticate and smoke-test them, then swap only the pointer."""
    preflight(directory, policy)
    root = owned_root(root)
    with deployment_lock(root):
        previous = state(root)
        if expected_previous is not None and previous["previous"] != expected_previous:
            raise Rejected("rollback target changed during the operation")
        slot_name = f"v{policy.version}-{policy.commit}"
        slot = root / "slots" / slot_name
        with tempfile.TemporaryDirectory(prefix=".stage-", dir=root / "slots") as temporary:
            staged = Path(temporary)
            # Never verify one file and later execute a fresh read of its untrusted source.
            for name in ["release.json", *sorted(policy.names)]:
                atomic_write(staged / name, read_bytes(directory / name))
            verify_release(staged, policy)
            health_check(staged / f"release-probe-{policy.version}.pyz")
            if slot.exists():
                verify_release(slot, policy)
                if read_bytes(slot / "release.json") != read_bytes(staged / "release.json"):
                    raise Rejected("existing immutable slot differs")
            else:
                os.replace(staged, slot)
            if previous["active"] == slot_name:
                return previous
            result = {"schema": 1, "active": slot_name, "previous": previous["active"]}
            atomic_write(root / "active.json", canonical(result))
            return result


def rollback(root: Path, policy: TrustPolicy) -> dict[str, Any]:
    """Reauthenticate an explicitly trusted previous release; never just trust the state file."""
    root = owned_root(root)
    expected = f"v{policy.version}-{policy.commit}"
    if state(root)["previous"] != expected:
        raise Rejected("explicit rollback target is not the previous release")
    return promote(root / "slots" / expected, root, policy, expected_previous=expected)
