"""Run the real frozen workbench twice with an owned synthetic profile and exact bundle persistence. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 67
# variable: PRODUCT — line 68
# variable: EXECUTABLE — line 69
# variable: VERSION — line 70
# definition: failure_summary — line 73
# parameter: receipt — line 73
# variable: result — line 75
# variable: name — line 76
# variable: value — line 77
# variable: line — line 80
# variable: bundles — line 83
# variable: steps — line 83
# variable: status — line 88
# variable: match — line 90
# definition: gone — line 99
# parameter: pid — line 99
# variable: kernel — line 103
# variable: handle — line 109
# definition: launch — line 120
# parameter: executable — line 121
# parameter: profile — line 122
# parameter: output — line 123
# parameter: metadata — line 124
# parameter: reopen — line 126
# variable: arguments — line 129
# variable: environment — line 138
# variable: key — line 139
# variable: child — line 142
# variable: code — line 149
# variable: path — line 150
# variable: stream — line 151
# variable: payload — line 152
# variable: receipt — line 155
# variable: diagnostic — line 157
# definition: main — line 179
# variable: executable — line 183
# variable: metadata — line 184
# variable: source — line 185
# variable: stream — line 194
# variable: digest — line 195
# variable: destination — line 200
# variable: temporary — line 202
# variable: scratch — line 203
# variable: profile — line 207
# variable: first — line 208
# variable: second — line 209
# variable: path — line 213
# variable: summary — line 215
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = "secure-delivery-pipeline-lab"
EXECUTABLE = "SecureDeliveryPipelineLab.exe"
VERSION = "1.2.0"


def failure_summary(receipt: dict[str, Any]) -> dict[str, Any]:
    """Expose only bounded authored-stage/category diagnostics, never raw status, paths, records or environment."""
    result: dict[str, Any] = {"native_acceptance": "failed"}
    for name in ("failure_stage", "failure_step", "failure_function", "failure_type"):
        value = receipt.get(name)
        if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_<>-]{1,80}", value):
            result[name] = value
    line = receipt.get("failure_line")
    if type(line) is int and 1 <= line <= 100000:
        result["failure_line"] = line
    steps, bundles = receipt.get("steps"), receipt.get("bundles")
    if isinstance(steps, list) and len(steps) <= 40:
        result["completed_steps"] = len(steps)
    if isinstance(bundles, dict) and len(bundles) <= 20:
        result["saved_bundles"] = len(bundles)
    status = receipt.get("safe_application_status")
    if isinstance(status, str) and len(status) <= 240:
        match = re.fullmatch(
            r"Input/output rejected: ((?:java|session|php|node)_[a-z0-9_]{1,70})\. Earlier saved analyses were retained\.",
            status,
        )
        if match:
            result["application_category"] = match[1]
    return result


def gone(pid: int) -> bool:
    """Query only this known child PID on Windows; never use Python os.kill for a zero-signal probe."""
    if sys.platform != "win32":
        raise OSError("owned Windows process probe requires Windows")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [ctypes.c_uint, ctypes.c_int, ctypes.c_uint]
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint]
    kernel.WaitForSingleObject.restype = ctypes.c_uint
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    handle = kernel.OpenProcess(0x1000 | 0x100000, False, pid)
    if not handle:
        if ctypes.get_last_error() == 87:
            return True
        raise OSError("owned child state unavailable")
    try:
        return kernel.WaitForSingleObject(handle, 0) == 0
    finally:
        kernel.CloseHandle(handle)


def launch(
    executable: Path,
    profile: Path,
    output: Path,
    metadata: dict[str, Any],
    *,
    reopen: bool,
) -> dict[str, Any]:
    """Launch the actual EXE without Python/Node/provider environment and require its frozen child to exit."""
    arguments = [
        str(executable),
        "--profile",
        str(profile),
        "--acceptance-output",
        str(output),
    ]
    if reopen:
        arguments.append("--acceptance-reopen")
    environment = {
        key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "TEMP", "TMP") if key in os.environ
    }
    environment["PATH"] = str(Path(os.environ.get("SYSTEMROOT", "C:/Windows")) / "System32")
    child = subprocess.Popen(
        arguments,
        cwd=profile.parent,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    code = child.wait(timeout=80)
    path = output / "acceptance.json"
    with path.open("rb") as stream:
        payload = stream.read(65537)
    if len(payload) > 65536:
        raise AssertionError("native receipt exceeds byte limit")
    receipt = json.loads(payload)
    if code != 0 or receipt.get("passed") is not True or receipt.get("synthetic") is not True:
        diagnostic = ROOT / "out/native-acceptance"
        diagnostic.mkdir(exist_ok=True)
        (diagnostic / ("failed-reopen.json" if reopen else "failed-first.json")).write_bytes(
            payload
        )
        print(json.dumps(failure_summary(receipt), sort_keys=True), flush=True)
        raise AssertionError(
            "Owned native acceptance failed at " + str(receipt.get("failure_stage", "startup"))[:60]
        )
    assert receipt["product"] == PRODUCT and receipt["version"] == VERSION
    assert receipt["python_version"] == "3.14.10"
    assert receipt["python_dll_sha256"] == metadata["resources"]["python314.dll"]
    assert (
        receipt["source"] == metadata["source"]
        and receipt["source_dirty"] is metadata["source_dirty"]
    )
    assert type(receipt["pid"]) is int and receipt["pid"] > 0 and receipt["parent_pid"] == child.pid
    assert gone(receipt["pid"]), "frozen service/mainloop survived the owned bootloader"
    assert receipt["reopen"] is reopen
    return receipt


def main() -> None:
    """Verify byte/source identity, two real native launches and identical saved bundles; never install/publish."""
    if os.name != "nt":
        raise RuntimeError("frozen application acceptance targets Windows")
    executable = ROOT / "release/portable" / EXECUTABLE
    metadata = json.loads((ROOT / "release/native-release.json").read_bytes())
    source = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert (
        metadata["source"] == source
        and metadata["version"] == VERSION
        and metadata["product"] == PRODUCT
    )
    assert type(metadata["source_dirty"]) is bool
    if os.environ.get("CI"):
        assert metadata["source_dirty"] is False, "CI must test a clean source checkout"
    with executable.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    assert (
        executable.with_name(EXECUTABLE + ".sha256").read_text(encoding="ascii")
        == digest + "  " + EXECUTABLE + "\n"
    )
    destination = ROOT / "out/native-acceptance"
    destination.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="owned-offline-native-") as temporary:
        scratch = Path(temporary).resolve()
        assert scratch.parent == Path(tempfile.gettempdir()).resolve() and scratch.name.startswith(
            "owned-offline-native-"
        )
        profile = scratch / "synthetic-profile"
        first = launch(executable, profile, scratch / "first", metadata, reopen=False)
        second = launch(executable, profile, scratch / "reopen", metadata, reopen=True)
        assert first["bundles"] == second["bundles"], (
            "restart did not retain exact original/analyst evidence"
        )
        for path in (scratch / "first").glob("*.png"):
            shutil.copyfile(path, destination / path.name)
        summary = {
            "schema": 1,
            "product": PRODUCT,
            "version": VERSION,
            "source": source,
            "source_dirty": metadata["source_dirty"],
            "executable_sha256": digest,
            "first": first,
            "reopen": second,
            "passed": True,
            "cleanup": "both owned frozen PIDs and bootloaders exited; only fresh synthetic temporary profile removed",
        }
        (destination / "acceptance.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    print(
        json.dumps(
            {
                "native_application": PRODUCT,
                "passed": True,
                "source_dirty": metadata["source_dirty"],
                "saved_bundles": len(first["bundles"]),
            }
        )
    )


if __name__ == "__main__":
    main()
