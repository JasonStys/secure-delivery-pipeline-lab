"""Presentation-adapter unit tests with real core/SQLite workers; real widgets are separately frozen-tested. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Variable — line 207
# definition: __init__ — line 210
# parameter: self — line 210
# parameter: value — line 210
# definition: get — line 214
# parameter: self — line 214
# definition: set — line 218
# parameter: self — line 218
# parameter: value — line 218
# variable: callback — line 221
# definition: trace_add — line 224
# parameter: _event — line 224
# parameter: callback — line 224
# parameter: self — line 224
# definition: Widget — line 229
# definition: __init__ — line 232
# parameter: _args — line 232
# parameter: kwargs — line 232
# parameter: self — line 232
# parameter: _items — line 236
# definition: pack — line 238
# parameter: _kwargs — line 238
# parameter: self — line 238
# definition: grid — line 241
# parameter: _kwargs — line 241
# parameter: self — line 241
# definition: grid_remove — line 244
# parameter: self — line 244
# definition: columnconfigure — line 247
# parameter: _args — line 247
# parameter: _kwargs — line 247
# parameter: self — line 247
# definition: add — line 250
# parameter: _args — line 250
# parameter: _kwargs — line 250
# parameter: self — line 250
# definition: theme_use — line 253
# parameter: _args — line 253
# parameter: self — line 253
# definition: configure — line 256
# parameter: _args — line 256
# parameter: kwargs — line 256
# parameter: self — line 256
# definition: heading — line 260
# parameter: _args — line 260
# parameter: _kwargs — line 260
# parameter: self — line 260
# definition: column — line 263
# parameter: _args — line 263
# parameter: _kwargs — line 263
# parameter: self — line 263
# definition: bind — line 266
# parameter: _args — line 266
# parameter: self — line 266
# definition: yview — line 269
# parameter: _args — line 269
# parameter: self — line 269
# definition: set — line 272
# parameter: _args — line 272
# parameter: self — line 272
# definition: state — line 275
# parameter: flags — line 275
# parameter: self — line 275
# variable: flag — line 277
# definition: invoke — line 283
# parameter: self — line 283
# definition: insert — line 289
# parameter: _parent — line 289
# parameter: _position — line 289
# parameter: iid — line 289
# parameter: self — line 289
# parameter: values — line 289
# definition: delete — line 293
# parameter: items — line 293
# parameter: self — line 293
# variable: item — line 295
# variable: item — line 297
# definition: get_children — line 299
# parameter: self — line 299
# definition: selection — line 303
# parameter: self — line 303
# definition: selection_set — line 307
# parameter: identity — line 307
# parameter: self — line 307
# definition: Text — line 313
# definition: delete — line 316
# parameter: _args — line 316
# parameter: self — line 316
# definition: insert — line 320
# parameter: _position — line 320
# parameter: self — line 320
# parameter: text — line 320
# definition: Root — line 325
# definition: __init__ — line 328
# parameter: self — line 328
# definition: title — line 333
# parameter: _args — line 333
# parameter: self — line 333
# definition: geometry — line 336
# parameter: _args — line 336
# parameter: self — line 336
# definition: minsize — line 339
# parameter: _args — line 339
# parameter: self — line 339
# definition: protocol — line 342
# parameter: _event — line 342
# parameter: callback — line 342
# parameter: self — line 342
# definition: after — line 346
# parameter: _delay — line 346
# parameter: callback — line 346
# parameter: self — line 346
# definition: destroy — line 350
# parameter: self — line 350
# definition: mainloop — line 354
# parameter: self — line 354
# variable: _ — line 358
# definition: presentation — line 366
# parameter: monkeypatch — line 366
# parameter: _parent — line 371
# variable: name — line 373
# variable: messages — line 387
# parameter: _kwargs — line 389
# parameter: args — line 389
# parameter: _kwargs — line 392
# parameter: args — line 392
# definition: app — line 398
# parameter: presentation — line 398
# parameter: tmp_path — line 398
# variable: state — line 400
# variable: root — line 401
# variable: window — line 402
# definition: settle — line 416
# parameter: window — line 416
# variable: deadline — line 418
# definition: test_real_controller_run_filter_detail_history_export_and_help — line 425
# parameter: app — line 426
# parameter: monkeypatch — line 426
# parameter: presentation — line 426
# parameter: tmp_path — line 426
# parameter: _kwargs — line 451
# variable: original — line 452
# variable: exported — line 454
# variable: path — line 455
# parameter: _kwargs — line 460
# definition: test_explicit_retention_confirmation_removes_only_selected_local_copy — line 466
# parameter: app — line 467
# parameter: monkeypatch — line 467
# parameter: tmp_path — line 467
# variable: exported — line 477
# variable: original — line 478
# parameter: _args — line 479
# parameter: _kwargs — line 479
# parameter: _args — line 482
# parameter: _kwargs — line 482
# variable: path — line 485
# definition: test_input_selection_cancel_busy_failure_and_literal_row_cap — line 492
# parameter: app — line 492
# parameter: monkeypatch — line 492
# parameter: tmp_path — line 492
# variable: name — line 494
# parameter: _kwargs — line 498
# parameter: _kwargs — line 503
# parameter: _kwargs — line 505
# variable: kind — line 506
# variable: value — line 510
# parameter: _kwargs — line 511
# variable: index — line 528
# definition: test_close_retains_lock_until_actual_core_transaction_finishes — line 541
# parameter: app — line 541
# parameter: monkeypatch — line 541
# parameter: tmp_path — line 541
# variable: ready — line 543
# variable: release — line 543
# variable: actual — line 544
# definition: pause — line 546
# parameter: args — line 546
# variable: reopened — line 564
# definition: test_main_native_close_and_rejected_acceptance_paths — line 571
# parameter: monkeypatch — line 571
# parameter: presentation — line 571
# parameter: tmp_path — line 571
# variable: actual — line 573
# definition: create — line 575
# parameter: root — line 575
# parameter: state — line 575
# variable: window — line 577
# variable: profile — line 582
# variable: reopened — line 584
# variable: unknown — line 606
# END CODE MAP

import threading
import time
from types import SimpleNamespace

import pytest

from delivery import desktop as module
from delivery import desktop_project as project
from delivery.desktop_io import Rejected
from delivery.desktop_state import Workspace


class Variable:
    """Inert presentation variable; invokes the same registered GUI trace callbacks."""

    def __init__(self, value=""):
        """Keep a scalar control value and registered change callbacks."""
        self.value, self.callbacks = value, []

    def get(self):
        """Return the current presentation control value."""
        return self.value

    def set(self, value):
        """Change a control and exercise actual application rendering callbacks."""
        self.value = value
        for callback in self.callbacks:
            callback()

    def trace_add(self, _event, callback):
        """Retain the GUI's value-change handler."""
        self.callbacks.append(callback)


class Widget:
    """Minimal inert ttk presentation adapter; no core, storage or analysis output is mocked."""

    def __init__(self, *_args, **kwargs):
        """Retain properties, rows and command closures."""
        self.options, self.rows, self.selected = kwargs, {}, ()
        self.flags = set()
        self.tk = SimpleNamespace(call=lambda *_items: None)

    def pack(self, **_kwargs):
        """Accept presentation layout."""

    def grid(self, **_kwargs):
        """Accept presentation grid coordinates."""

    def grid_remove(self):
        """Accept operation-specific hidden controls."""

    def columnconfigure(self, *_args, **_kwargs):
        """Accept resize weights."""

    def add(self, *_args, **_kwargs):
        """Accept notebook/paned-window children."""

    def theme_use(self, *_args):
        """Accept native style selection."""

    def configure(self, *_args, **kwargs):
        """Retain updated widget options."""
        self.options.update(kwargs)

    def heading(self, *_args, **_kwargs):
        """Accept a literal table heading."""

    def column(self, *_args, **_kwargs):
        """Accept table sizing."""

    def bind(self, *_args):
        """Accept event registration; tests invoke actual handlers explicitly."""

    def yview(self, *_args):
        """Accept scroll requests."""

    def set(self, *_args):
        """Accept scrollbar position updates."""

    def state(self, flags):
        """Preserve disabled controls so a simulated click cannot bypass a busy guard."""
        for flag in flags:
            if flag.startswith("!"):
                self.flags.discard(flag[1:])
            else:
                self.flags.add(flag)

    def invoke(self):
        """Invoke the actual registered command unless the control is disabled."""
        if "disabled" not in self.flags:
            return self.options["command"]()
        return None

    def insert(self, _parent, _position, *, iid, values):
        """Retain exact rows inserted by real project rendering."""
        self.rows[iid] = values

    def delete(self, *items):
        """Remove rows and their selections like a real treeview."""
        for item in items:
            self.rows.pop(item, None)
        self.selected = tuple(item for item in self.selected if item in self.rows)

    def get_children(self):
        """Return displayed row identities."""
        return tuple(self.rows)

    def selection(self):
        """Return the current selected row identity."""
        return self.selected

    def selection_set(self, identity):
        """Select one existing row like a real single-selection control."""
        assert identity in self.rows
        self.selected = (identity,)


class Text(Widget):
    """Retain literal detail output without interpreting markup or executing event fields."""

    def delete(self, *_args):
        """Clear existing literal detail text."""
        self.text = ""

    def insert(self, _position, text):
        """Retain the exact rendered detail text."""
        self.text = text


class Root:
    """Deterministic presentation event queue; actual Tk mainloops are independently exercised by frozen acceptance."""

    def __init__(self):
        """Create a fresh owned presentation root."""
        self.callbacks, self.destroyed = [], False
        self.on_loop = None

    def title(self, *_args):
        """Accept window title."""

    def geometry(self, *_args):
        """Accept initial geometry."""

    def minsize(self, *_args):
        """Accept minimum geometry."""

    def protocol(self, _event, callback):
        """Keep the application's native close callback."""
        self.close_callback = callback

    def after(self, _delay, callback):
        """Queue the actual lifecycle callback without a platform display server."""
        self.callbacks.append(callback)

    def destroy(self):
        """Mark only this owned root as closed."""
        self.destroyed = True

    def mainloop(self):
        """Run the requested test lifecycle using real application callbacks."""
        if self.on_loop:
            self.on_loop()
        for _ in range(200):
            if self.destroyed:
                return
            self.callbacks.pop(0)()
        raise AssertionError("presentation lifecycle did not close")


@pytest.fixture
def presentation(monkeypatch):
    """Replace only OS presentation surfaces; real worker, core, SQLite and export code remain active."""
    monkeypatch.setattr(module.tk, "StringVar", Variable)
    monkeypatch.setattr(module.tk, "BooleanVar", Variable)
    monkeypatch.setattr(module.tk, "Tk", Root)
    monkeypatch.setattr(module.tk, "Toplevel", lambda _parent: Root())
    monkeypatch.setattr(module.tk, "Text", Text)
    for name in (
        "Frame",
        "Label",
        "Notebook",
        "Combobox",
        "Entry",
        "Button",
        "Checkbutton",
        "Panedwindow",
        "Treeview",
        "Scrollbar",
        "Style",
    ):
        monkeypatch.setattr(module.ttk, name, Widget)
    messages = []
    monkeypatch.setattr(
        module.messagebox, "showinfo", lambda *args, **_kwargs: messages.append(args)
    )
    monkeypatch.setattr(
        module.messagebox, "showerror", lambda *args, **_kwargs: messages.append(args)
    )
    return messages


@pytest.fixture
def app(tmp_path, presentation):
    """Build the actual workbench controller against an isolated real durable workspace."""
    state = Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT)
    root = Root()
    window = module.Workbench(root, state)
    # Presentation tests exercise the real offline domain engine and SQLite;
    # actual widgets/mainloop are separately proved by the final frozen consumer.
    window.prepared.set(project.SCENARIOS[1])
    window.load_prepared()
    try:
        yield window
    finally:
        if window.worker_thread:
            window.worker_thread.join(10)
            assert not window.worker_thread.is_alive()
        state.close()


def settle(window):
    """Observe completion of one actual owned analysis; no retries or invented report values."""
    deadline = time.monotonic() + 10
    while window.busy and time.monotonic() < deadline:
        window.poll()
        time.sleep(0.005)
    assert not window.busy


def test_real_controller_run_filter_detail_history_export_and_help(
    app, tmp_path, monkeypatch, presentation
):
    """Real core results drive controls, literal filters, exact private exports and history reopening."""
    app.export()
    assert "completed" in app.status.get()
    app.run_button.invoke()
    assert not app.busy and app.state.history() == []
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    assert app.selected_run == 1 and len(app.state.history()) == 1
    assert len(app.table.get_children()) > 0
    app.table.selection_set("0")
    app.inspect()
    assert "{" in app.details.text
    app.review_selected()
    if project.REVIEW_MODE is not None:
        assert app.mode.get() == project.REVIEW_MODE and app.authorized.get() is False
    app.search.set("not-a-supported-record-never-present")
    assert app.table.get_children() == ()
    app.inspect()
    app.search.set("")
    app.history_table.selection_set("1")
    app.open_button.invoke()
    assert "without re-running" in app.status.get()
    monkeypatch.setattr(module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path))
    original = app.state.files(1)
    app.export_button.invoke()
    exported = next(tmp_path.glob(project.PRODUCT + "-run-*"))
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.help()
    assert "plaintext" in presentation[-1][1]
    app.licenses()
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path / "missing")
    )
    app.export()
    assert "unavailable" in app.status.get()


def test_explicit_retention_confirmation_removes_only_selected_local_copy(
    app, tmp_path, monkeypatch
):
    """Cancellation preserves data; confirmation deletes one exact DB bundle without touching a prior export."""
    app.remove_history()
    assert "Select" in app.status.get()
    app.review_selected()
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    app.history_table.selection_set("1")
    exported = app.state.export(1, tmp_path, project.PRODUCT)
    original = app.state.files(1)
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: False)
    app.remove_button.invoke()
    assert app.state.files(1) == original
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: True)
    app.remove_button.invoke()
    assert app.state.history() == [] and app.selected_run == 0
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.busy = True
    app.remove_history()
    assert "Wait" in app.status.get()
    app.busy = False


def test_input_selection_cancel_busy_failure_and_literal_row_cap(app, tmp_path, monkeypatch):
    """Operator mistakes do not silently run a prepared fixture, overwrite results or defeat close semantics."""
    name = "inventory"
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilename",
        lambda **_kwargs: str(tmp_path / "authorized.json"),
    )
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilenames",
        lambda **_kwargs: ("one.json", "two.json"),
    )
    monkeypatch.setattr(module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path))
    for kind in ("file", "files", "directory"):
        app.authorized.set(True)
        app.choose(name, kind)
        assert app.authorized.get() is False
    value = app.values[name].get()
    monkeypatch.setattr(module.filedialog, "askopenfilename", lambda **_kwargs: "")
    app.choose(name, "file")
    assert app.values[name].get() == value
    app.busy = True
    app.choose(name, "file")
    app.load_prepared()
    app.open_history()
    app.run()
    assert app.state.history() == []
    app.busy = False
    app.load_prepared()
    app.mode.set("unsupported-operation")
    app.authorized.set(True)
    app.run()
    settle(app)
    assert "rejected" in app.status.get().lower() and app.state.history() == []
    app.current = {
        "bounded": [{"kind": "alert", "packet": index, "rule": str(index)} for index in range(5001)]
    }
    app.view.set("bounded")
    app.render()
    assert len(app.table.get_children()) == 5000
    app.search.set('"5000"')
    assert len(app.table.get_children()) == 1
    app.exit()
    app.run()
    app.poll()
    assert app.root.destroyed and app.state.lock == -1


def test_close_retains_lock_until_actual_core_transaction_finishes(app, tmp_path, monkeypatch):
    """An in-flight real analysis is drained rather than abandoned, force-killed or exposed to a second owner."""
    ready, release = threading.Event(), threading.Event()
    actual = project.analyze

    def pause(*args):
        """Control only scheduling; completion still invokes the actual project core and durable output."""
        ready.set()
        assert release.wait(5)
        return actual(*args)

    monkeypatch.setattr(project, "analyze", pause)
    app.authorized.set(True)
    app.run_button.invoke()
    assert ready.wait(3)
    app.exit()
    app.poll()
    assert not app.root.destroyed and app.busy
    with pytest.raises((Rejected, OSError)):
        Workspace(app.state.path, project.PRODUCT, project.ROOT)
    release.set()
    settle(app)
    assert app.root.destroyed and app.state.lock == -1
    reopened = Workspace(app.state.path, project.PRODUCT, project.ROOT)
    try:
        assert len(reopened.history()) == 1
    finally:
        reopened.close()


def test_main_native_close_and_rejected_acceptance_paths(tmp_path, presentation, monkeypatch):
    """Normal startup never auto-analyzes; test flags cannot enter existing real-profile state or claim partial success."""
    actual = module.Workbench

    def create(root, state):
        """Use actual controls/controller; request the normal close callback at the start of the event loop."""
        window = actual(root, state)
        root.on_loop = window.exit
        return window

    monkeypatch.setattr(module, "Workbench", create)
    profile = tmp_path / "normal"
    assert module.main(["--profile", str(profile)]) == 0
    reopened = Workspace(profile, project.PRODUCT, project.ROOT)
    assert reopened.history() == []
    reopened.close()
    with pytest.raises(SystemExit):
        module.main(["--acceptance-output", str(tmp_path / "output")])
    with pytest.raises(SystemExit):
        module.main(["--acceptance-reopen"])
    assert (
        module.main(["--profile", str(profile), "--acceptance-output", str(tmp_path / "output")])
        == 2
    )
    assert (
        module.main(
            [
                "--profile",
                str(tmp_path / "synthetic"),
                "--acceptance-output",
                str(tmp_path / "new-output"),
            ]
        )
        == 2
    )
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    (unknown / "keep").write_bytes(b"unchanged")
    assert module.main(["--profile", str(unknown)]) == 2
    assert (unknown / "keep").read_bytes() == b"unchanged"
    assert presentation and "No saved evidence was reset" in presentation[-1][1]
