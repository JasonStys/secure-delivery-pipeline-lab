"""Actual patched Python/Tcl/Tk/PyInstaller runtime notices and authored portable icon. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 46
# definition: icon — line 49
# parameter: path — line 49
# variable: size — line 51
# variable: pixels — line 52
# variable: y — line 53
# variable: x — line 54
# variable: shield — line 55
# variable: check — line 58
# variable: color — line 61
# variable: bitmap — line 69
# definition: notices — line 81
# parameter: path — line 81
# variable: root — line 85
# variable: tcl_version — line 88
# variable: tk_version — line 89
# variable: value — line 90
# variable: runtime_notices — line 92
# variable: library — line 93
# variable: title — line 93
# variable: channel — line 97
# variable: raw — line 99
# variable: raw — line 103
# variable: sources — line 109
# variable: name — line 113
# variable: suffix — line 113
# variable: distribution — line 116
# variable: entry — line 117
# variable: matches — line 117
# variable: blocks — line 126
# variable: source — line 126
# variable: title — line 126
# variable: _ — line 127
# variable: data — line 127
# variable: data — line 129
# variable: title — line 129
# END CODE MAP

import importlib.metadata
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def icon(path: Path) -> None:
    """Generate an authored blue shield/check icon as build output, without shipping a graphics dependency."""
    size = 64
    pixels = bytearray()
    for y in reversed(range(size)):
        for x in range(size):
            shield = (
                8 <= x <= 55 and 5 <= y <= 42 or 42 < y <= 59 and abs(x - 31.5) < (60 - y) * 1.4
            )
            check = (
                15 <= x <= 29 and abs(y - (x + 8)) < 3 or 27 <= x <= 48 and abs(y - (65 - x)) < 3
            )
            color = (
                (255, 255, 255, 255)
                if shield and check
                else (220, 100, 24, 255)
                if shield
                else (0, 0, 0, 0)
            )
            pixels.extend(color)
    bitmap = (
        struct.pack("<IIIHHIIIIII", 40, size, size * 2, 1, 32, 0, len(pixels), 0, 0, 0, 0)
        + pixels
        + bytes(size * size // 8)
    )
    path.write_bytes(
        struct.pack("<HHH", 0, 1, 1)
        + struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(bitmap), 22)
        + bitmap
    )


def notices(path: Path) -> None:
    """Retain actual Python, Tcl/Tk and bootloader notices, including Tcl9 DLL-embedded resources."""
    import tkinter

    root = tkinter.Tk()
    root.withdraw()
    try:
        tcl_version = root.tk.call("info", "patchlevel")
        tk_version = root.tk.call("package", "require", "Tk")
        if not all(str(value).startswith(("8.6.", "9.0.")) for value in (tcl_version, tk_version)):
            raise ValueError("Review a different Tcl/Tk runtime family before packaging")
        runtime_notices = []
        for title, library in [
            ("Tcl " + str(tcl_version), root.tk.call("info", "library")),
            ("Tk " + str(tk_version), root.tk.eval("set tk_library")),
        ]:
            channel = root.tk.call("open", str(library) + "/license.terms", "rb")
            try:
                raw = root.tk.call("read", channel, 65537)
            finally:
                root.tk.call("close", channel)
            if isinstance(raw, str):
                raw = raw.encode("utf-8")
            if not isinstance(raw, bytes) or not 100 < len(raw) <= 65536:
                raise ValueError("Actual runtime notice is missing or outside its byte bound")
            runtime_notices.append((title, raw))
    finally:
        root.destroy()
    sources = [
        ("Authored application — MIT", ROOT / "LICENSE"),
        ("Python runtime", Path(sys.base_prefix) / "LICENSE.txt"),
    ]
    for name, suffix in [
        ("pyinstaller", "licenses/COPYING.txt"),
    ]:
        distribution = importlib.metadata.distribution(name)
        matches = [entry for entry in distribution.files or [] if str(entry).endswith(suffix)]
        if len(matches) != 1:
            raise ValueError("Review runtime license inventory before packaging")
        sources.append(
            (
                name + " license and applicable exception",
                Path(distribution.locate_file(matches[0])),
            )
        )
    blocks = [(title, source.read_bytes()) for title, source in sources] + runtime_notices
    if any(len(data) > 2 * 1024 * 1024 for _, data in blocks):
        raise ValueError("Bundled license exceeds byte bound")
    path.write_bytes(b"\n\n".join(title.encode("utf-8") + b"\n" + data for title, data in blocks))
