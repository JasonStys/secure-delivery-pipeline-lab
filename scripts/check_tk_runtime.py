"""Require the selected interpreter's actual native Tk imports and loaded Tcl, without a display. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: inspect_runtime — line 27
# parameter: loader — line 27
# variable: load — line 29
# variable: native — line 30
# variable: wrapper — line 31
# variable: compiled_tcl — line 32
# variable: compiled_tk — line 32
# variable: interpreter — line 35
# variable: patch — line 37
# variable: provided — line 38
# definition: main — line 56
# variable: result — line 59
# END CODE MAP

from __future__ import annotations

import importlib
import json
import platform
import re
from collections.abc import Callable
from typing import Any


def inspect_runtime(loader: Callable[[str], Any] | None = None) -> dict[str, str]:
    """Load both real native/wrapper modules and execute Tcl; never substitute a distro-package assumption."""
    load = importlib.import_module if loader is None else loader
    native = load("_tkinter")
    wrapper = load("tkinter")
    compiled_tcl, compiled_tk = native.TCL_VERSION, native.TK_VERSION
    if compiled_tcl not in ("8.6", "9.0") or compiled_tk != compiled_tcl:
        raise RuntimeError("Review unsupported Tcl/Tk build families")
    interpreter = wrapper.Tcl()
    try:
        patch = interpreter.call("info", "patchlevel")
        provided = interpreter.call("package", "require", "Tcl")
        if (
            not isinstance(patch, str)
            or re.fullmatch(re.escape(compiled_tcl) + r"\.[0-9]{1,4}", patch) is None
            or provided != patch
        ):
            raise RuntimeError("Loaded Tcl does not match the native extension")
        return {
            "python": platform.python_version(),
            "compiled_tcl": compiled_tcl,
            "compiled_tk": compiled_tk,
            "loaded_tcl": patch,
            "scope": "Actual selected-Python native imports and Tcl interpreter; graphical display is separately exercised by the compiled Windows application",
        }
    finally:
        del interpreter


def main() -> int:
    """Fail closed with a value-free category on every loader/interpreter error; no skip or install fallback."""
    try:
        result = inspect_runtime()
    except Exception:
        print('{"tk_runtime":"unavailable-or-invalid"}')
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
