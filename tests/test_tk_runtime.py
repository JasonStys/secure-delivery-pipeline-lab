"""Actual isolated native Tcl positive plus fail-closed loader/interpreter/version controls. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 58
# definition: test_actual_selected_runtime_in_owned_child — line 61
# variable: result — line 63
# variable: data — line 70
# definition: test_missing_native_or_wrapper_loader_cannot_pass — line 78
# parameter: missing — line 78
# definition: loader — line 81
# parameter: name — line 81
# definition: test_invalid_interpreter_or_native_identity_cannot_pass — line 95
# parameter: fault — line 95
# definition: Interpreter — line 98
# definition: call — line 101
# parameter: args — line 101
# parameter: self — line 101
# definition: constructor — line 108
# definition: loader — line 114
# parameter: name — line 114
# definition: test_cli_error_is_nonzero_and_value_free — line 128
# parameter: capsys — line 128
# parameter: monkeypatch — line 128
# definition: fail — line 131
# definition: validate_selected_runtime_step — line 140
# parameter: source — line 140
# variable: match — line 142
# variable: quality — line 144
# variable: found — line 145
# variable: test_positions — line 152
# variable: token — line 154
# definition: test_actual_workflow_requires_real_selected_runtime — line 166
# definition: test_actual_workflow_probe_mutants — line 174
# parameter: mutation — line 174
# variable: source — line 176
# variable: step — line 177
# variable: source — line 180
# variable: source — line 182
# variable: source — line 186
# variable: source — line 190
# variable: source — line 194
# variable: source — line 198
# variable: target — line 199
# variable: source — line 205
# END CODE MAP

import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import check_tk_runtime as probe

ROOT = Path(__file__).resolve().parents[1]


def test_actual_selected_runtime_in_owned_child():
    """A real fresh selected-Python process must import the native extension and execute Tcl without a display."""
    result = subprocess.run(
        [sys.executable, "-I", str(ROOT / "scripts/check_tk_runtime.py")],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    data = json.loads(result.stdout)
    assert data["compiled_tcl"] in ("8.6", "9.0")
    assert data["compiled_tk"] == data["compiled_tcl"]
    assert data["loaded_tcl"].startswith(data["compiled_tcl"] + ".")
    assert set(data) == {"python", "compiled_tcl", "compiled_tk", "loaded_tcl", "scope"}


@pytest.mark.parametrize("missing", ["_tkinter", "tkinter"])
def test_missing_native_or_wrapper_loader_cannot_pass(missing):
    """Inject only a missing loader; neither normal Python availability nor a wrapper alone can pass."""

    def loader(name):
        """Preserve the other actual module; simulate the selected interpreter missing one required component."""
        if name == missing:
            raise ModuleNotFoundError("inert missing-loader control")
        return importlib.import_module(name)

    with pytest.raises(ModuleNotFoundError):
        probe.inspect_runtime(loader)


@pytest.mark.parametrize(
    "fault",
    ["constructor", "query", "mismatched-patch", "unsupported-family", "different-tk-family"],
)
def test_invalid_interpreter_or_native_identity_cannot_pass(fault):
    """Minimal inert failure controls test refusal only; the successful path always uses the real child above."""

    class Interpreter:
        """Answer only the two authored commands with deliberately invalid/query-failure observations."""

        def call(self, *args):
            """Never evaluate a script; simulate one fixed Tcl query failure or mismatched version."""
            assert args in (("info", "patchlevel"), ("package", "require", "Tcl"))
            if fault == "query":
                raise RuntimeError("inert native query failure")
            return "8.6.14" if args[0] == "info" else "8.6.15"

    def constructor():
        """Refuse a failed real-interpreter construction independently of native import availability."""
        if fault == "constructor":
            raise RuntimeError("inert native constructor failure")
        return Interpreter()

    def loader(name):
        """Return closed fake components only for negative identity/initialization controls."""
        if name == "_tkinter":
            return SimpleNamespace(
                TCL_VERSION="8.5" if fault == "unsupported-family" else "8.6",
                TK_VERSION="9.0" if fault == "different-tk-family" else "8.6",
            )
        assert name == "tkinter"
        return SimpleNamespace(Tcl=constructor)

    with pytest.raises(RuntimeError):
        probe.inspect_runtime(loader)


def test_cli_error_is_nonzero_and_value_free(monkeypatch, capsys):
    """An unexpected loader failure cannot become a successful skip or expose arbitrary exception contents."""

    def fail():
        """Use an inert sentinel that must never be emitted by the public gate."""
        raise OSError("inert-private-sentinel-never-print")

    monkeypatch.setattr(probe, "inspect_runtime", fail)
    assert probe.main() == 1
    assert json.loads(capsys.readouterr().out) == {"tk_runtime": "unavailable-or-invalid"}


def validate_selected_runtime_step(source):
    """Require the exact real probe after SDK selection and before source tests in this authored quality-job format."""
    match = re.search(r"^  quality:\n(.*?)(?=^  [a-z][a-z0-9-]*:|\Z)", source, re.M | re.S)
    assert match is not None
    quality = match[1]
    found = re.findall(
        r"^      - name: Require actual selected-Python Tk runtime \(no display\)\n(.*?)(?=^      - |\Z)",
        quality,
        re.M | re.S,
    )
    assert found == ["        run: python -I scripts/check_tk_runtime.py\n"]
    assert "continue-on-error" not in quality
    test_positions = [
        quality.index(token)
        for token in ("bash scripts/validate.sh", "python -m pytest")
        if token in quality
    ]
    assert test_positions
    assert (
        quality.index("uses: actions/setup-python@")
        < quality.index("name: Require actual selected-Python Tk runtime")
        < min(test_positions)
    )
    assert "python3-tk" not in quality


def test_actual_workflow_requires_real_selected_runtime():
    """This is a narrow authored-step contract; native actionlint separately validates the entire YAML."""
    validate_selected_runtime_step((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf8"))


@pytest.mark.parametrize(
    "mutation", ["missing", "weak-import", "conditional", "ignored", "fallback", "late"]
)
def test_actual_workflow_probe_mutants(mutation):
    """Actual source mutations cannot silently skip, weaken, ignore or postpone the required native-runtime proof."""
    source = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf8")
    step = "      - name: Require actual selected-Python Tk runtime (no display)\n        run: python -I scripts/check_tk_runtime.py\n"
    assert source.count(step) == 1
    if mutation == "missing":
        source = source.replace(step, "")
    elif mutation == "weak-import":
        source = source.replace(
            "python -I scripts/check_tk_runtime.py", "python -c 'import tkinter'"
        )
    elif mutation == "conditional":
        source = source.replace(
            step, step.replace("        run:", "        if: runner.os == 'Windows'\n        run:")
        )
    elif mutation == "ignored":
        source = source.replace(
            step, step.replace("        run:", "        continue-on-error: true\n        run:")
        )
    elif mutation == "fallback":
        source = source.replace(
            "python -I scripts/check_tk_runtime.py", "python -I scripts/check_tk_runtime.py || true"
        )
    else:
        source = source.replace(step, "")
        target = re.search(
            r"^ {6,8}(?:- )?run: (?:bash scripts/validate\.sh|python -m pytest[^\n]*)\n",
            source,
            re.M,
        )
        assert target is not None
        source = source[: target.end()] + step + source[target.end() :]
    with pytest.raises(AssertionError):
        validate_selected_runtime_step(source)
