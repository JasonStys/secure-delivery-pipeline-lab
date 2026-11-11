"""Actual final portable widgets/core/native-window acceptance with independent oracles. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: capture — line 118
# parameter: target — line 118
# parameter: window — line 118
# variable: load — line 124
# variable: gdi — line 125
# variable: user — line 125
# variable: pointer — line 126
# variable: arguments — line 127
# variable: library — line 127
# variable: name — line 127
# variable: result — line 127
# variable: function — line 153
# variable: handle — line 157
# variable: rectangle — line 158
# variable: height — line 161
# variable: width — line 161
# variable: source — line 164
# variable: destination — line 165
# variable: bitmap — line 166
# variable: previous — line 167
# variable: pixels — line 172
# variable: header — line 173
# variable: raw — line 191
# variable: scanlines — line 192
# variable: row — line 193
# variable: column — line 195
# variable: offset — line 196
# definition: chunk — line 199
# parameter: data — line 199
# parameter: name — line 199
# definition: oracle — line 221
# parameter: files — line 221
# parameter: index — line 221
# variable: result — line 224
# variable: expected — line 225
# variable: result — line 232
# definition: exercise — line 244
# parameter: output — line 244
# parameter: reopen — line 244
# parameter: window — line 244
# variable: expected — line 249
# variable: started — line 249
# variable: receipt — line 250
# variable: deadline — line 267
# definition: progress — line 269
# parameter: stage — line 269
# definition: finish — line 276
# parameter: failed — line 276
# variable: name — line 286
# variable: raw — line 286
# variable: row — line 288
# definition: checked — line 293
# parameter: callback — line 293
# variable: trace — line 301
# variable: trace — line 306
# definition: callback_failed — line 309
# parameter: _traceback — line 309
# parameter: _value — line 309
# parameter: kind — line 309
# definition: wait — line 314
# parameter: callback — line 314
# definition: layout — line 324
# variable: widgets — line 329
# variable: name — line 330
# variable: widget — line 332
# definition: rejected — line 354
# definition: licenses — line 360
# variable: dialogs — line 363
# variable: child — line 364
# variable: dialog — line 367
# variable: pending — line 368
# variable: texts — line 369
# variable: widget — line 371
# variable: text — line 377
# variable: value — line 378
# definition: completed — line 382
# parameter: index — line 382
# variable: files — line 385
# variable: parent — line 407
# variable: target — line 411
# variable: path — line 412
# definition: delete_transient — line 421
# variable: invalid — line 433
# definition: start — line 443
# parameter: index — line 443
# variable: source — line 452
# variable: selected — line 460
# variable: policy — line 461
# variable: field — line 463
# definition: begin — line 474
# variable: identity — line 478
# END CODE MAP

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import sys
import time
import tkinter as tk
import zlib
from pathlib import Path
from tkinter import ttk
from typing import TYPE_CHECKING, Any

from delivery import desktop_project as project
from delivery.desktop_io import json_value

if TYPE_CHECKING:
    from delivery.desktop import Workbench


def capture(window: Workbench, target: Path) -> None:
    """Capture only this owned synthetic Tk window via PrintWindow, never the user's whole desktop."""
    if sys.platform != "win32":
        raise OSError("native screenshot acceptance targets Windows")
    from ctypes import wintypes

    load = ctypes.WinDLL
    user, gdi = load("user32", use_last_error=True), load("gdi32", use_last_error=True)
    pointer = ctypes.c_void_p
    for library, name, arguments, result in [
        (user, "GetAncestor", [pointer, ctypes.c_uint], pointer),
        (user, "GetWindowDC", [pointer], pointer),
        (gdi, "CreateCompatibleDC", [pointer], pointer),
        (gdi, "CreateCompatibleBitmap", [pointer, ctypes.c_int, ctypes.c_int], pointer),
        (gdi, "SelectObject", [pointer, pointer], pointer),
        (gdi, "DeleteObject", [pointer], ctypes.c_int),
        (gdi, "DeleteDC", [pointer], ctypes.c_int),
        (user, "ReleaseDC", [pointer, pointer], ctypes.c_int),
        (user, "PrintWindow", [pointer, pointer, ctypes.c_uint], ctypes.c_int),
        (user, "GetWindowRect", [pointer, ctypes.POINTER(wintypes.RECT)], ctypes.c_int),
        (
            gdi,
            "GetDIBits",
            [
                pointer,
                pointer,
                ctypes.c_uint,
                ctypes.c_uint,
                pointer,
                pointer,
                ctypes.c_uint,
            ],
            ctypes.c_int,
        ),
    ]:
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, result
    # Flush this owned native window's pending control messages before reading its pixels.
    window.root.update()
    handle = user.GetAncestor(window.root.winfo_id(), 2)
    rectangle = wintypes.RECT()
    if not user.GetWindowRect(handle, ctypes.byref(rectangle)):
        raise OSError("owned window bounds unavailable")
    width, height = rectangle.right - rectangle.left, rectangle.bottom - rectangle.top
    if not 1 <= width <= 4096 or not 1 <= height <= 4096:
        raise OSError("owned screenshot outside bounded dimensions")
    source = user.GetWindowDC(handle)
    destination = gdi.CreateCompatibleDC(source)
    bitmap = gdi.CreateCompatibleBitmap(source, width, height)
    previous = gdi.SelectObject(destination, bitmap)
    try:
        if not user.PrintWindow(handle, destination, 2):
            raise OSError("owned window rendering unavailable")
        gdi.SelectObject(destination, previous)
        pixels = ctypes.create_string_buffer(width * height * 4)
        header = ctypes.create_string_buffer(
            struct.pack(
                "<IiiHHIIiiII",
                40,
                width,
                -height,
                1,
                32,
                0,
                width * height * 4,
                0,
                0,
                0,
                0,
            )
        )
        if gdi.GetDIBits(source, bitmap, 0, height, pixels, header, 0) != height:
            raise OSError("owned screenshot pixels incomplete")
        raw = pixels.raw
        scanlines = bytearray()
        for row in range(height):
            scanlines.append(0)
            for column in range(width):
                offset = (row * width + column) * 4
                scanlines.extend((raw[offset + 2], raw[offset + 1], raw[offset]))

        def chunk(name: bytes, data: bytes) -> bytes:
            """Encode a bounded standard PNG chunk with its actual CRC."""
            return (
                struct.pack(">I", len(data))
                + name
                + data
                + struct.pack(">I", zlib.crc32(name + data))
            )

        target.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(scanlines)))
            + chunk(b"IEND", b"")
        )
    finally:
        gdi.SelectObject(destination, previous)
        gdi.DeleteObject(bitmap)
        gdi.DeleteDC(destination)
        user.ReleaseDC(handle, source)


def oracle(index: int, files: dict[str, bytes]) -> None:
    """Require literal exact-cent outputs or explicit unauthenticated status on actual original preflight results."""
    if index < 4 or index == 6:
        result = json_value(files["inventory.json"])
        expected = ("1727.40", "0.30", "0.00", "19999999999.98")
        assert result["totals"]["inventory_value_usd"] == (
            "0.30" if index == 6 else expected[index]
        )
        if index == 6:
            assert result["products"][0]["id"] == "PRIVATE-NATIVE-STOCK"
    else:
        result = json_value(files["preflight.json"])
        assert result["status"] == "INTEGRITY_ONLY_NOT_AUTHENTICATED"
        assert (
            result["authentication_verified"]
            is result["signer_workflow_verified"]
            is result["execution_permitted"]
            is False
        )
        assert len(result["manifest"]["assets"]) == 3 and len(result["members"]) == 6
        assert result["prepared_unsigned_fixture"] is (index != 7)


def exercise(window: Workbench, output: Path, reopen: bool) -> None:
    """Drive the same real offline widgets/core worker and retained-owner close; supply only OS file-picker selection."""
    from unittest.mock import patch

    output.mkdir(mode=0o700)
    started, expected = time.monotonic(), 8
    receipt: dict[str, Any] = {
        "schema": 1,
        "product": project.PRODUCT,
        "version": project.VERSION,
        "source": window.identity["source"],
        "source_dirty": window.identity["source_dirty"],
        "python_version": sys.version.split()[0],
        "python_dll_sha256": window.identity.get("python_dll_sha256"),
        "pid": os.getpid(),
        "parent_pid": os.getppid(),
        "synthetic": True,
        "reopen": reopen,
        "passed": False,
        "steps": [],
        "tcl_version": str(window.root.tk.call("info", "patchlevel")),
        "tk_version": str(window.root.tk.call("package", "require", "Tk")),
    }
    deadline = started + 65

    def progress(stage: str) -> None:
        """Keep value-free milestone evidence if a native service or UI step fails."""
        receipt["last_stage"] = stage
        (output / "acceptance.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    def finish(failed: bool = False) -> None:
        """Request normal close and preserve exact bundle identities; failure is never replaced by success on cleanup."""
        window.acceptance_result = not failed
        receipt["passed"] = not failed
        if failed:
            receipt["safe_application_status"] = window.status.get()[:240]
        receipt["journey_elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
        receipt["bundles"] = {
            str(row["id"]): {
                name: hashlib.sha256(raw).hexdigest()
                for name, raw in window.state.files(row["id"]).items()
            }
            for row in window.state.history()
        }
        progress("failed-retained" if failed else "normal-close-requested")
        window.exit()

    def checked(callback: Any) -> None:
        """A failed assertion becomes a nonzero normal app exit, without private exception/body output."""
        try:
            callback()
        except Exception as error:
            receipt["failure_stage"] = callback.__name__
            receipt["failure_type"] = type(error).__name__[:60]
            receipt["failure_step"] = receipt.get("last_stage")
            trace = error.__traceback__
            while trace is not None:
                if Path(trace.tb_frame.f_code.co_filename).name == "native_acceptance.py":
                    receipt["failure_function"] = trace.tb_frame.f_code.co_name[:60]
                    receipt["failure_line"] = trace.tb_lineno
                trace = trace.tb_next
            finish(True)

    def callback_failed(kind: type[BaseException], _value: BaseException, _traceback: Any) -> None:
        """Do not lose Tk callback errors in a windowed executable without stderr."""
        receipt["failure_type"] = kind.__name__[:60]
        finish(True)

    def wait(callback: Any) -> None:
        """Wait for the actual retained worker with one fixed deadline; no audit repetition or forced child abandonment."""
        if time.monotonic() > deadline:
            receipt["failure_stage"] = "owned-workflow-deadline"
            finish(True)
        elif window.busy:
            window.root.after(60, lambda: wait(callback))
        else:
            checked(callback)

    def layout() -> None:
        """Require real active controls and Exit to fit the minimum supported native window."""
        window.root.geometry("980x700")
        window.tabs.tk.call(str(window.tabs), "select", str(window.inputs_page))
        window.root.update()
        widgets: list[ttk.Widget] = [window.run_button, *window.footer_buttons.values()]
        for name in project.ACTIVE_FIELDS[window.mode.get()]:
            widgets.extend(window.field_widgets[name])
        for widget in widgets:
            assert widget.winfo_ismapped()
            assert (
                widget.winfo_rootx() >= window.root.winfo_rootx()
                and widget.winfo_rooty() >= window.root.winfo_rooty()
            )
            assert (
                widget.winfo_rootx() + widget.winfo_width()
                <= window.root.winfo_rootx() + window.root.winfo_width()
            )
            assert (
                widget.winfo_rooty() + widget.winfo_height()
                <= window.root.winfo_rooty() + window.root.winfo_height()
            )
        receipt["minimum_layout"] = {
            "width": 980,
            "height": 700,
            "activeInputsRunAndLifecycleVisible": True,
        }
        window.root.geometry("1260x860")
        window.root.update()

    def rejected() -> None:
        """A duplicate-key selected input must preserve every earlier real result and produce a visible rejection."""
        assert len(window.state.history()) == expected and "rejected" in window.status.get().lower()
        receipt["steps"].append("actual-invalid-input-retains-all-bundles")
        finish()

    def licenses() -> None:
        """Inspect the actual bundled text notice window, not a source-only declaration that licenses exist."""
        window.licenses()
        dialogs = [
            child for child in window.root.winfo_children() if isinstance(child, tk.Toplevel)
        ]
        assert len(dialogs) == 1
        dialog = dialogs[0]
        pending: list[tk.Misc] = [dialog]
        texts: list[tk.Text] = []
        while pending:
            widget = pending.pop()
            if isinstance(widget, tk.Text):
                texts.append(widget)
            pending.extend(widget.winfo_children())
            assert len(pending) < 1000
        assert len(texts) == 1
        text = texts[0].get("1.0", "end")
        assert all(value in text for value in ("Python", "Tcl", "Tk"))
        dialog.destroy()
        receipt["steps"].append("actual-bundled-runtime-license-window")

    def completed(index: int) -> None:
        """Inspect real selected output, preserve exact rows and save actual native screenshots before lifecycle/export tests."""
        assert len(window.state.history()) == index + 1 and window.selected_run == index + 1
        files = window.state.files(index + 1)
        oracle(index, files)
        if index in (0, 7):
            window.view.set(
                "Stock and exact values" if index == 0 else "Authentication NOT verified"
            )
            window.render()
            window.table.selection_set("0")
            window.inspect()
            assert json.loads(window.details.get("1.0", "end"))
            window.root.update()
            capture(
                window,
                output / ("selected-evidence.png" if index == 0 else "owner-unknown-review.png"),
            )
        receipt["steps"].append("actual-workflow-" + str(index + 1))
        if index + 1 < expected:
            start(index + 1)
        else:
            progress("runtime-license-window")
            licenses()
            progress("exact-export")
            parent = output / "exact-export"
            parent.mkdir()
            with patch("delivery.desktop.filedialog.askdirectory", return_value=str(parent)):
                window.export_button.invoke()
            target = next(parent.iterdir())
            assert {path.name: path.read_bytes() for path in target.iterdir()} == files
            receipt["steps"].append("actual-exact-export")
            # Create one additional real analysis solely to test both deletion choices.
            window.prepared.set(project.SCENARIOS[0])
            window.load_prepared()
            window.authorized.set(True)
            window.run_button.invoke()
            wait(delete_transient)

    def delete_transient() -> None:
        """Cancel and then confirm the real Delete action for one extra transient result; original bundles remain identical."""
        assert len(window.state.history()) == expected + 1
        window.refresh_history()
        window.history_table.selection_set(str(expected + 1))
        with patch("delivery.desktop.messagebox.askyesno", return_value=False):
            window.remove_button.invoke()
        assert len(window.state.history()) == expected + 1
        with patch("delivery.desktop.messagebox.askyesno", return_value=True):
            window.remove_button.invoke()
        assert len(window.state.history()) == expected
        receipt["steps"].append("actual-cancel-and-confirm-transient-deletion")
        invalid = output / "invalid-input.json"
        invalid.write_bytes(b'{"duplicate":1,"duplicate":2}')
        window.mode.set(project.MODES[0])
        with patch("delivery.desktop.filedialog.askopenfilename", return_value=str(invalid)):
            window.choose("inventory", "file")
        window.show_fields()
        window.authorized.set(True)
        window.run_button.invoke()
        wait(rejected)

    def start(index: int) -> None:
        """Prepared cases use normal controls; final workflows use actual selected external inputs and explicit parameters."""
        progress("workflow-" + str(index + 1))
        window.prepared.set(
            project.SCENARIOS[index] if index < len(project.SCENARIOS) else project.SCENARIOS[0]
        )
        window.load_prepared()
        assert not window.authorized.get()
        if index == 6:
            source = output / "selected-private-inventory.json"
            source.write_text(
                '[{"id":"PRIVATE-NATIVE-STOCK","units":3,"unit_price_usd":"0.10"}]', encoding="utf8"
            )
            window.mode.set(project.MODES[0])
            with patch("delivery.desktop.filedialog.askopenfilename", return_value=str(source)):
                window.choose("inventory", "file")
        if index == 7:
            selected = output / "selected-unsigned-release"
            policy = project.unsigned_fixture(selected)
            window.mode.set(project.MODES[1])
            for field in ("repository", "commit", "version", "workflow"):
                window.values[field].set(str(getattr(policy, field)))
            with patch("delivery.desktop.filedialog.askdirectory", return_value=str(selected)):
                window.choose("directory", "directory")
        window.show_fields()
        layout()
        window.authorized.set(True)
        window.run_button.invoke()
        assert window.busy and window.worker_thread and window.worker_thread.is_alive()
        wait(lambda: completed(index))

    def begin() -> None:
        """A separate real process reopens all exact bundles without rerunning services or recomputing a prior report."""
        if reopen:
            assert len(window.state.history()) == expected
            for identity in range(1, expected + 1):
                window.history_table.selection_set(str(identity))
                window.open_button.invoke()
                assert window.selected_run == identity
                oracle(identity - 1, window.state.files(identity))
            receipt["steps"].append("actual-process-reopen-all-exact-bundles")
            finish()
        else:
            assert not window.state.history()
            window.run_button.invoke()
            assert not window.state.history() and "permission" in window.status.get().lower()
            start(0)

    window.root.report_callback_exception = callback_failed
    checked(begin)
