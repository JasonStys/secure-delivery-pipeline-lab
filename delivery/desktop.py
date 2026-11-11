"""Native offline workbench: real project inputs, analysis, searchable evidence, history and export. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Workbench — line 174
# definition: __init__ — line 177
# parameter: root — line 177
# parameter: self — line 177
# parameter: state — line 177
# variable: _kind — line 191
# variable: _label — line 191
# variable: name — line 191
# variable: style — line 206
# variable: container — line 210
# variable: _ — line 222
# variable: history — line 222
# variable: inputs — line 222
# variable: results — line 222
# variable: prepared — line 232
# parameter: _event — line 253
# variable: index — line 254
# variable: kind — line 254
# variable: label — line 254
# variable: name — line 254
# variable: label_widget — line 255
# variable: entry — line 257
# variable: button — line 272
# variable: row — line 280
# variable: filters — line 290
# parameter: _event — line 295
# variable: search — line 297
# parameter: _args — line 299
# variable: pane — line 300
# variable: table_frame — line 302
# variable: key — line 309
# variable: label — line 309
# variable: width — line 309
# variable: scroll — line 317
# variable: label — line 343
# variable: name — line 343
# variable: width — line 343
# variable: footer — line 360
# parameter: event — line 366
# variable: action — line 369
# variable: label — line 369
# variable: padding — line 369
# variable: button — line 374
# variable: variable — line 377
# parameter: _args — line 378
# parameter: _args — line 379
# definition: load_prepared — line 384
# parameter: self — line 384
# variable: selected — line 388
# variable: name — line 390
# variable: variable — line 390
# definition: show_fields — line 399
# parameter: self — line 399
# variable: active — line 401
# variable: name — line 402
# variable: widgets — line 402
# variable: widget — line 403
# definition: input_changed — line 409
# parameter: self — line 409
# definition: review_selected — line 414
# parameter: self — line 414
# definition: choose — line 418
# parameter: kind — line 418
# parameter: name — line 418
# parameter: self — line 418
# variable: value — line 423
# variable: value — line 427
# variable: value — line 431
# definition: run — line 438
# parameter: self — line 438
# variable: name — line 445
# variable: parameters — line 445
# variable: variable — line 445
# variable: selection — line 448
# variable: control — line 455
# definition: worker — line 468
# parameter: parameters — line 468
# parameter: self — line 468
# variable: directory — line 473
# variable: files — line 474
# variable: kind — line 474
# variable: summary — line 474
# variable: identity — line 475
# definition: poll — line 494
# parameter: self — line 494
# variable: identity — line 497
# variable: summary — line 497
# variable: control — line 501
# definition: show — line 520
# parameter: identity — line 520
# parameter: self — line 520
# variable: files — line 522
# definition: render — line 532
# parameter: self — line 532
# variable: query — line 535
# variable: matching — line 536
# variable: row — line 538
# variable: index — line 542
# variable: row — line 542
# definition: detail_text — line 548
# parameter: self — line 548
# parameter: value — line 548
# definition: inspect — line 555
# parameter: _event — line 555
# parameter: self — line 555
# variable: selected — line 557
# definition: refresh_history — line 563
# parameter: self — line 563
# variable: row — line 566
# definition: open_history — line 574
# parameter: self — line 574
# variable: selected — line 578
# definition: export — line 586
# parameter: self — line 586
# variable: parent — line 591
# definition: remove_history — line 606
# parameter: self — line 606
# variable: selected — line 611
# variable: identity — line 616
# variable: files — line 617
# variable: expected — line 618
# variable: data — line 619
# variable: name — line 619
# definition: help — line 644
# parameter: self — line 644
# definition: licenses — line 653
# parameter: self — line 653
# variable: name — line 656
# variable: text — line 657
# variable: dialog — line 658
# variable: frame — line 661
# variable: label — line 663
# variable: area — line 669
# variable: scroll — line 670
# definition: exit — line 684
# parameter: self — line 684
# definition: main — line 692
# parameter: argv — line 692
# variable: parser — line 694
# variable: args — line 698
# variable: state — line 703
# variable: window — line 704
# variable: root — line 705
# variable: identity — line 707
# variable: state — line 720
# variable: root — line 726
# variable: window — line 727
# END CODE MAP

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import queue
import sqlite3
import sys
import tempfile
import threading
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from . import desktop_project as project
from .desktop_io import Rejected, canonical, read_bytes
from .desktop_state import Workspace, package_identity, profile_path, unlinked


class Workbench:
    """One actual Tk application around the existing core; background jobs never update widgets off-thread."""

    def __init__(self, root: tk.Tk, state: Workspace) -> None:
        """Build real project-specific controls; inputs are never executed as commands or plugins."""
        self.root, self.state = root, state
        self.identity: dict[str, Any] = {}
        self.acceptance_result: bool | None = None
        self.worker_thread: threading.Thread | None = None
        self.busy = False
        self.closing = False
        self.selected_run = 0
        self.current: dict[str, list[dict[str, Any]]] = {}
        self.visible: list[dict[str, Any]] = []
        self.bundle_names: set[str] = set()
        self.field_widgets: dict[str, list[ttk.Widget]] = {}
        self.results: queue.Queue[tuple[int | None, str]] = queue.Queue(maxsize=1)
        self.values = {name: tk.StringVar() for name, _label, _kind in project.FIELDS}
        self.mode = tk.StringVar(value=project.MODES[0])
        self.prepared = tk.StringVar(value=project.SCENARIOS[0])
        self.authorized = tk.BooleanVar(value=False)
        self.search = tk.StringVar()
        self.view = tk.StringVar()
        self.status = tk.StringVar(
            value="Choose a prepared scenario or your supported authorized files, then run analysis."
        )
        root.title(project.TITLE + " · Jason Stys")
        if getattr(sys, "frozen", False):
            root.tk.call("wm", "iconbitmap", str(root), "-default", str(project.ROOT / "app.ico"))
        root.geometry("1260x860")
        root.minsize(980, 700)
        root.protocol("WM_DELETE_WINDOW", self.exit)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=28)
        container = ttk.Frame(root, padding=16)
        container.pack(fill="both", expand=True)
        ttk.Label(container, text=project.TITLE, font=("Segoe UI", 21, "bold")).pack(anchor="w")
        ttk.Label(
            container,
            text=f"Version {project.VERSION} · Created by Jason Stys · Owner-local offline workbench · No background uploads",
        ).pack(anchor="w", pady=(4, 12))
        ttk.Label(container, text=project.BANNER, wraplength=930, foreground="#753000").pack(
            anchor="w", pady=(0, 8)
        )
        self.tabs = ttk.Notebook(container)
        self.tabs.pack(fill="both", expand=True)
        inputs, results, history = (ttk.Frame(self.tabs, padding=14) for _ in range(3))
        self.tabs.add(inputs, text="1  Inputs and settings")
        self.tabs.add(results, text="2  Results and review")
        self.tabs.add(history, text="3  Saved reviews")
        self.inputs_page, self.results_page = inputs, results
        self.controls: list[ttk.Widget] = []
        ttk.Label(
            inputs,
            text="Prepared scenarios are optional inputs in this same application; they are not live host data.",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=8)
        prepared = ttk.Combobox(
            inputs,
            textvariable=self.prepared,
            values=project.SCENARIOS,
            state="readonly",
            width=50,
        )
        prepared.grid(row=1, column=0, sticky="ew")
        self.controls.append(
            ttk.Button(inputs, text="Load prepared scenario", command=self.load_prepared)
        )
        self.controls[-1].grid(row=1, column=1, sticky="w", padx=8)
        ttk.Label(inputs, text="Operation").grid(row=2, column=0, sticky="w", pady=(15, 4))
        self.operation = ttk.Combobox(
            inputs,
            textvariable=self.mode,
            values=project.MODES,
            state="readonly",
            width=50,
        )
        self.operation.grid(row=2, column=1, columnspan=2, sticky="ew", pady=(15, 4))
        self.operation.bind("<<ComboboxSelected>>", lambda _event: self.show_fields())
        for index, (name, label, kind) in enumerate(project.FIELDS, 3):
            label_widget = ttk.Label(inputs, text=label, wraplength=380, justify="left")
            label_widget.grid(row=index, column=0, sticky="w", pady=4)
            entry = (
                ttk.Combobox(
                    inputs,
                    textvariable=self.values[name],
                    values=project.CHOICES[name],
                    state="readonly",
                    width=42,
                )
                if name in project.CHOICES
                else ttk.Entry(inputs, textvariable=self.values[name], width=42)
            )
            entry.grid(row=index, column=1, sticky="ew", pady=4)
            self.field_widgets[name] = [label_widget, entry]
            self.controls.append(entry)
            if kind not in ("text", "choice"):
                button = ttk.Button(
                    inputs,
                    text="Choose…",
                    command=partial(self.choose, name, kind),
                )
                button.grid(row=index, column=2, padx=8)
                self.controls.append(button)
                self.field_widgets[name].append(button)
        row = len(project.FIELDS) + 3
        self.acknowledge = ttk.Checkbutton(
            inputs,
            text="I am permitted to use these files. Local state and exports can contain sensitive evidence.",
            variable=self.authorized,
        )
        self.acknowledge.grid(row=row, column=0, columnspan=3, sticky="w", pady=12)
        self.run_button = ttk.Button(inputs, text="Run selected analysis", command=self.run)
        self.run_button.grid(row=row + 1, column=0, sticky="w", pady=8)
        inputs.columnconfigure(1, weight=1)
        filters = ttk.Frame(results)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Evidence view").pack(side="left")
        self.view_box = ttk.Combobox(filters, textvariable=self.view, state="readonly", width=40)
        self.view_box.pack(side="left", padx=8)
        self.view_box.bind("<<ComboboxSelected>>", lambda _event: self.render())
        ttk.Label(filters, text="Search literal evidence").pack(side="left")
        search = ttk.Entry(filters, textvariable=self.search)
        search.pack(side="left", fill="x", expand=True, padx=8)
        self.search.trace_add("write", lambda *_args: self.render())
        pane = ttk.Panedwindow(results, orient="vertical")
        pane.pack(fill="both", expand=True)
        table_frame = ttk.Frame(pane)
        self.table = ttk.Treeview(
            table_frame,
            columns=("time", "detector", "event", "state"),
            show="headings",
            selectmode="browse",
        )
        for key, label, width in (
            ("time", project.COLUMNS[0], 220),
            ("detector", project.COLUMNS[1], 280),
            ("event", project.COLUMNS[2], 250),
            ("state", project.COLUMNS[3], 190),
        ):
            self.table.heading(key, text=label)
            self.table.column(key, width=width, minwidth=80)
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.inspect)
        pane.add(table_frame, weight=3)
        self.details = tk.Text(
            pane, height=12, wrap="word", state="disabled", font=("Consolas", 10)
        )
        pane.add(self.details, weight=2)
        self.export_button = ttk.Button(
            results, text="Export selected analysis bundle…", command=self.export
        )
        self.export_button.pack(before=pane, side="bottom", anchor="w", pady=8)
        self.review_button = None
        if project.REVIEW_MODE is not None:
            self.review_button = ttk.Button(
                results, text="Review selected resource…", command=self.review_selected
            )
            self.review_button.pack(before=self.export_button, side="bottom", anchor="w", pady=4)
        self.history_table = ttk.Treeview(
            history,
            columns=("id", "created", "kind", "summary"),
            show="headings",
            selectmode="browse",
        )
        for name, label, width in (
            ("id", "Analysis", 70),
            ("created", "Created UTC", 210),
            ("kind", "Operation", 190),
            ("summary", "Evidence summary", 410),
        ):
            self.history_table.heading(name, text=label)
            self.history_table.column(name, width=width)
        self.history_table.pack(fill="both", expand=True)
        self.open_button = ttk.Button(
            history, text="Open saved analysis", command=self.open_history
        )
        self.open_button.pack(before=self.history_table, side="bottom", anchor="w", pady=8)
        self.remove_button = ttk.Button(
            history, text="Remove selected local analysis…", command=self.remove_history
        )
        self.remove_button.pack(before=self.open_button, side="bottom", anchor="w", pady=4)
        footer = ttk.Frame(container)
        footer.pack(before=self.tabs, side="bottom", fill="x", pady=(10, 0))
        self.status_label = ttk.Label(footer, textvariable=self.status, width=1)
        self.status_label.pack(side="left", fill="x", expand=True)
        self.status_label.bind(
            "<Configure>",
            lambda event: self.status_label.configure(wraplength=max(120, event.width)),
        )
        self.footer_buttons: dict[str, ttk.Button] = {}
        for label, action, padding in (
            ("Help", self.help, 8),
            ("Licenses", self.licenses, 4),
            ("Exit application", self.exit, 0),
        ):
            button = ttk.Button(footer, text=label, command=action)
            button.pack(side="right", padx=padding)
            self.footer_buttons[label] = button
        for variable in self.values.values():
            variable.trace_add("write", lambda *_args: self.authorized.set(False))
        self.mode.trace_add("write", lambda *_args: self.input_changed())
        self.refresh_history()
        self.load_prepared()
        root.after(60, self.poll)

    def load_prepared(self) -> None:
        """Fill actual input controls with bundled fictional examples without running an analysis automatically."""
        if self.busy:
            return
        selected = project.scenario(self.prepared.get())
        self.mode.set(selected["mode"])
        for name, variable in self.values.items():
            variable.set(selected.get(name, ""))
        self.show_fields()
        self.authorized.set(False)
        self.status.set(
            "Fictional scenario prepared. Review its inputs and acknowledge permission before running."
        )
        self.tabs.tk.call(str(self.tabs), "select", str(self.inputs_page))

    def show_fields(self) -> None:
        """Show only settings used by the selected real project operation, without erasing prior input choices."""
        active = set(project.ACTIVE_FIELDS.get(self.mode.get(), ()))
        for name, widgets in self.field_widgets.items():
            for widget in widgets:
                if name in active:
                    widget.grid()
                else:
                    widget.grid_remove()

    def input_changed(self) -> None:
        """Reset acknowledgement and relevant visible fields after a mode edit; this is not authentication."""
        self.authorized.set(False)
        self.show_fields()

    def review_selected(self) -> None:
        """This offline inspector records no approvals or authenticated review identities."""
        return

    def choose(self, name: str, kind: str) -> None:
        """Choose only local supported input paths; nothing is collected, opened as code or uploaded."""
        if self.busy:
            return
        if kind == "directory":
            value = filedialog.askdirectory(
                parent=self.root, title="Choose reviewed input directory"
            )
        elif kind == "files":
            value = "\n".join(
                filedialog.askopenfilenames(parent=self.root, title="Choose authorized snapshots")
            )
        else:
            value = filedialog.askopenfilename(
                parent=self.root, title="Choose supported authorized input"
            )
        if value:
            self.values[name].set(value)
            self.authorized.set(False)

    def run(self) -> None:
        """Capture controls once and start one bounded core operation without blocking the native message loop."""
        if self.busy or self.closing:
            return
        if not self.authorized.get():
            self.status.set("Permission acknowledgement is required; no analysis was started.")
            return
        parameters = {name: variable.get() for name, variable in self.values.items()}
        parameters["mode"] = self.mode.get()
        parameters["_run"] = str(self.selected_run)
        selection = self.table.selection()
        parameters["_row"] = (
            canonical(self.visible[int(selection[0])]).decode() if selection else "null"
        )
        self.busy = True
        self.run_button.state(["disabled"])
        self.operation.state(["disabled"])
        for control in self.controls:
            control.state(["disabled"])
        self.status.set(
            "Analysis running offline. Exit waits for the current transaction; inputs are not executed as commands."
        )
        self.worker_thread = threading.Thread(
            target=self.worker,
            args=(parameters,),
            name="owned-offline-analysis",
            daemon=False,
        )
        self.worker_thread.start()

    def worker(self, parameters: dict[str, str]) -> None:
        """Run actual project analysis and atomically retain only completed bounded bundles; never touch widgets."""
        try:
            with tempfile.TemporaryDirectory(
                prefix="owned-analysis-", dir=self.state.path
            ) as directory:
                kind, summary, files = project.analyze(self.state, parameters, Path(directory))
                identity = self.state.save(kind, summary, parameters, files)
            self.results.put((identity, summary))
        except Rejected as error:
            self.results.put(
                (
                    None,
                    "Input/output rejected: "
                    + str(error)[:200]
                    + ". Earlier saved analyses were retained.",
                )
            )
        except Exception:
            self.results.put(
                (
                    None,
                    "Input/output rejected. Check supported contracts, required fields, selected evidence and history capacity; existing analyses were retained.",
                )
            )

    def poll(self) -> None:
        """Receive a completed worker on the Tk thread; never destroy the application while a write is in flight."""
        try:
            identity, summary = self.results.get_nowait()
            self.busy = False
            self.run_button.state(["!disabled"])
            self.operation.state(["!disabled", "readonly"])
            for control in self.controls:
                control.state(["!disabled"])
            try:
                if identity is not None:
                    self.show(identity)
                    self.refresh_history()
                self.status.set(summary)
            except (Rejected, sqlite3.Error, ValueError, KeyError, TypeError):
                self.status.set(
                    "Saved evidence could not be rendered; retain your private backup. No files were reset."
                )
        except queue.Empty:
            pass
        if self.closing and not self.busy:
            self.state.close()
            self.root.destroy()
            return
        self.root.after(60, self.poll)

    def show(self, identity: int) -> None:
        """Open one verified actual saved bundle; no source is re-evaluated or silently replaced on reopen."""
        files = self.state.files(identity)
        self.current = project.views(files)
        self.bundle_names = set(files)
        self.selected_run = identity
        self.view_box.configure(values=tuple(self.current))
        self.view.set(next(iter(self.current)))
        self.search.set("")
        self.render()
        self.tabs.tk.call(str(self.tabs), "select", str(self.results_page))

    def render(self) -> None:
        """Filter literal evidence and bound visible rows; full original output remains exportable."""
        self.table.delete(*self.table.get_children())
        query = self.search.get().casefold().strip()
        matching = [
            row
            for row in self.current.get(self.view.get(), [])
            if not query or query in json.dumps(row, ensure_ascii=False).casefold()
        ]
        self.visible = matching[:5000]
        for index, row in enumerate(self.visible):
            self.table.insert("", "end", iid=str(index), values=project.cells(row))
        self.detail_text(
            f"{len(self.visible)} shown / {len(matching)} matching records. At most 5,000 rows are rendered; full evidence is retained in the private bundle."
        )

    def detail_text(self, value: str) -> None:
        """Show copyable literal evidence in a read-only text area; no markup is evaluated."""
        self.details.configure(state="normal")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", value)
        self.details.configure(state="disabled")

    def inspect(self, _event: Any = None) -> None:
        """Display the exact selected record and its uncertainty/context without creating an incident verdict."""
        selected = self.table.selection()
        if selected:
            self.detail_text(
                json.dumps(self.visible[int(selected[0])], indent=2, ensure_ascii=False)
            )

    def refresh_history(self) -> None:
        """List existing analysis identities without running a fixture or contacting a host."""
        self.history_table.delete(*self.history_table.get_children())
        for row in self.state.history():
            self.history_table.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(row["id"], row["created"], row["kind"], row["summary"]),
            )

    def open_history(self) -> None:
        """Reopen only a selected retained analysis; busy operations cannot be replaced halfway through."""
        if self.busy:
            return
        selected = self.history_table.selection()
        if selected:
            try:
                self.show(int(selected[0]))
                self.status.set("Saved evidence reopened without re-running analysis.")
            except (Rejected, sqlite3.Error, ValueError, KeyError):
                self.status.set("Saved evidence could not be verified; no files were reset.")

    def export(self) -> None:
        """Export an exact verified bundle into a new directory under a user-selected private parent."""
        if self.busy or not self.selected_run:
            self.status.set("Select a completed saved analysis before exporting.")
            return
        parent = filedialog.askdirectory(
            parent=self.root,
            title="Choose private export parent; a new directory will be created",
        )
        if parent:
            try:
                self.state.export(self.selected_run, Path(parent), project.PRODUCT)
                self.status.set(
                    "Verified bundle exported to a new directory in the selected parent. Review private evidence before sharing."
                )
            except (Rejected, OSError, sqlite3.Error):
                self.status.set(
                    "Export unavailable. Existing evidence was retained; inspect any newly created partial export."
                )

    def remove_history(self) -> None:
        """Remove one confirmed exact private local copy; never delete original inputs or exported directories."""
        if self.busy:
            self.status.set("Wait for the active analysis before changing history retention.")
            return
        selected = self.history_table.selection()
        if not selected:
            self.status.set("Select a saved analysis in History before removing its local copy.")
            return
        try:
            identity = int(selected[0])
            files = self.state.files(identity)
            expected = hashlib.sha256(
                canonical({name: hashlib.sha256(data).hexdigest() for name, data in files.items()})
            ).hexdigest()
            if not messagebox.askyesno(
                "Remove local saved analysis?",
                "Export a private backup first if you need to retain this evidence. Remove only this selected local analysis? Original input files and previously exported copies are not deleted.",
                parent=self.root,
            ):
                return
            self.state.remove(identity, expected)
            if self.selected_run == identity:
                self.selected_run = 0
                self.current = {}
                self.bundle_names = set()
                self.view_box.configure(values=())
                self.view.set("")
                self.render()
            self.refresh_history()
            self.status.set(
                "Selected local analysis removed. Original inputs and exported copies were not changed."
            )
        except (Rejected, sqlite3.Error, ValueError):
            self.status.set(
                "Selected evidence changed or could not be verified; nothing was removed."
            )

    def help(self) -> None:
        """Explain purpose, controls and plaintext-owner boundaries without external content or popups from third parties."""
        messagebox.showinfo(
            project.TITLE + " — Help",
            project.HELP
            + "\n\nChoose Inputs → operation/files → permission → Run. Findings are searchable literal evidence; select a row to inspect. Saved analyses reopens exact bundles; Export creates a new private directory. Exit waits for an active analysis. Up to 20 runs / 128 MiB of retained bundle payloads (database/metadata add overhead), 64 MiB per bundle / 32 MiB per file. Export backups and explicitly remove local analyses to manage retention; no automatic eviction. Back up the entire profile only after clean exit. Created by Jason Stys: github.com/JasonStys · linkedin.com/in/jason-stys-31b30b351",
            parent=self.root,
        )

    def licenses(self) -> None:
        """Offer readable bundled runtime notices locally without opening a browser or exposing data paths."""
        try:
            name = "notices.txt" if getattr(sys, "frozen", False) else "LICENSE"
            text = read_bytes(project.ROOT / name, 8 * 1024 * 1024).decode("utf-8")
            dialog = tk.Toplevel(self.root)
            dialog.title(project.TITLE + " — Licenses")
            dialog.geometry("850x620")
            frame = ttk.Frame(dialog, padding=12)
            frame.pack(fill="both", expand=True)
            label = (
                "Bundled application and runtime notices"
                if name == "notices.txt"
                else "Authored source license; portable packages also include runtime notices"
            )
            ttk.Label(frame, text=label).pack(anchor="w", pady=8)
            area = tk.Text(frame, wrap="word", font=("Consolas", 10))
            scroll = ttk.Scrollbar(frame, command=area.yview)
            area.configure(yscrollcommand=scroll.set)
            scroll.pack(side="right", fill="y")
            area.pack(fill="both", expand=True)
            area.insert("1.0", text)
            area.configure(state="disabled")
            ttk.Button(frame, text="Close licenses", command=dialog.destroy).pack(
                anchor="e", pady=8
            )
        except (Rejected, UnicodeError, tk.TclError):
            self.status.set(
                "License text could not be read; verify the portable package before use."
            )

    def exit(self) -> None:
        """Wait for the owned worker and committed evidence rather than interrupting a write or killing another process."""
        self.closing = True
        self.status.set(
            "Closing after the owned analysis finishes. Saved evidence remains on this PC."
        )


def main(argv: list[str] | None = None) -> int:
    """Open the actual offline native workbench; special acceptance requires an explicit synthetic profile."""
    parser = argparse.ArgumentParser(description=project.TITLE + " · Jason Stys")
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--acceptance-output", type=Path)
    parser.add_argument("--acceptance-reopen", action="store_true")
    args = parser.parse_args(argv)
    if args.acceptance_output and not args.profile:
        parser.error("acceptance requires an explicit synthetic profile")
    if args.acceptance_reopen and not args.acceptance_output:
        parser.error("acceptance reopen requires the explicit acceptance mode")
    state = None
    window = None
    root = None
    try:
        identity = package_identity(
            project.ROOT,
            project.PRODUCT,
            project.VERSION,
            project.RESOURCES,
            project.RESOURCE_LIMITS,
        )
        if args.acceptance_output and not args.acceptance_reopen and args.profile.exists():
            raise Rejected("acceptance requires a new synthetic profile")
        if args.acceptance_output:
            args.acceptance_output = unlinked(args.acceptance_output)
            if args.acceptance_output.exists() or not args.acceptance_output.parent.is_dir():
                raise Rejected("acceptance output must be new under an existing unlinked parent")
        state = Workspace(
            args.profile or profile_path(project.PROFILE),
            project.PRODUCT,
            project.ROOT,
            synthetic=bool(args.acceptance_output),
        )
        root = tk.Tk()
        window = Workbench(root, state)
        window.identity = identity
        if args.acceptance_output:
            from scripts.native_acceptance import exercise

            root.after(
                100,
                lambda: exercise(window, args.acceptance_output, args.acceptance_reopen),
            )
        root.mainloop()
        return 0 if not args.acceptance_output or window.acceptance_result is True else 2
    except (Rejected, OSError, sqlite3.Error, tk.TclError):
        if not args.acceptance_output:
            with contextlib.suppress(tk.TclError):
                messagebox.showerror(
                    project.TITLE,
                    "The local workspace could not start. Close an existing instance or review profile permissions. No saved evidence was reset.",
                )
        return 2
    finally:
        if window and window.worker_thread:
            window.worker_thread.join()
        if state:
            state.close()
        if root:
            with contextlib.suppress(tk.TclError):
                root.destroy()


if __name__ == "__main__":
    raise SystemExit(main())
