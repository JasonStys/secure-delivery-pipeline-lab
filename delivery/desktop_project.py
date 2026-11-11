"""Actual inventory and offline integrity-only release review; never substitute hashes for provenance. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: ROOT — line 94
# variable: PRODUCT — line 95
# variable: PROFILE — line 95
# variable: TITLE — line 96
# variable: VERSION — line 96
# variable: BANNER — line 97
# variable: COLUMNS — line 98
# variable: RESOURCES — line 99
# variable: RESOURCE_LIMITS — line 100
# variable: MODES — line 101
# variable: REVIEW_MODE — line 106
# variable: CHOICES — line 107
# variable: FIELDS — line 117
# variable: ACTIVE_FIELDS — line 126
# variable: SCENARIOS — line 131
# variable: HELP — line 139
# definition: scenario — line 144
# parameter: name — line 144
# definition: inventory_example — line 160
# parameter: name — line 160
# variable: examples — line 162
# definition: unsigned_fixture — line 180
# parameter: changed — line 180
# parameter: output — line 180
# variable: policy — line 182
# variable: buffer — line 184
# variable: archive — line 185
# variable: data — line 186
# variable: name — line 186
# variable: entry — line 195
# variable: payloads — line 198
# variable: name — line 207
# variable: raw — line 207
# variable: name — line 221
# variable: raw — line 221
# definition: snapshot_release — line 229
# parameter: policy — line 229
# parameter: source — line 229
# parameter: stage — line 229
# variable: source — line 231
# variable: p — line 232
# variable: name — line 235
# variable: raw — line 236
# definition: analyze — line 240
# parameter: parameters — line 241
# parameter: stage — line 241
# parameter: state — line 241
# variable: mode — line 244
# variable: exercise — line 247
# variable: inventory — line 250
# variable: raw — line 252
# variable: rows — line 257
# variable: totals — line 258
# variable: report — line 259
# variable: row — line 264
# variable: selected — line 275
# variable: policy — line 276
# variable: policy — line 278
# variable: selected — line 284
# variable: manifest — line 286
# variable: archive — line 287
# variable: members — line 288
# variable: name — line 294
# variable: result — line 296
# definition: views — line 319
# parameter: files — line 319
# variable: report — line 322
# variable: row — line 324
# variable: report — line 329
# variable: row — line 332
# variable: row — line 334
# definition: cells — line 339
# parameter: row — line 339
# END CODE MAP

from __future__ import annotations

import hashlib
import io
import sys
import zipfile
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .desktop_io import Rejected, canonical, json_value
from .desktop_state import Workspace, unlinked
from .inputs import read_source
from .probe import MAX_INPUT, summarize
from .verify import REPOSITORY, WORKFLOW, TrustPolicy, preflight

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
PRODUCT, PROFILE = "secure-delivery-pipeline-lab", "SecureDeliveryPipelineLab"
TITLE, VERSION = "Secure Delivery Offline Workbench", "1.2.0"
BANNER = "Offline integrity review: provenance is NOT authenticated. Incoming applications are never executed."
COLUMNS = ("Stock / asset / member", "Units / bytes", "Value / digest", "Decision / scope")
RESOURCES = ("notices.txt", "app.ico", "python314.dll")
RESOURCE_LIMITS: dict[str, int] = {}
MODES = (
    "Review authorized inventory JSON",
    "Preflight an authorized four-asset release",
    "Review prepared unsigned data exercise",
)
REVIEW_MODE = None
CHOICES = {
    "exercise": (
        "warehouse",
        "exact-cents",
        "zero-stock",
        "high-value",
        "unsigned-release",
        "unsigned-changed-member",
    )
}
FIELDS = (
    ("inventory", "Authorized inventory JSON", "file"),
    ("directory", "Authorized exact four-asset release directory", "directory"),
    ("repository", "Independently expected repository", "text"),
    ("commit", "Independently expected full source SHA", "text"),
    ("version", "Independently expected stable release version", "text"),
    ("workflow", "Expected signer workflow (NOT checked offline)", "text"),
    ("exercise", "Prepared unsigned/data-only exercise", "choice"),
)
ACTIVE_FIELDS = {
    MODES[0]: ("inventory",),
    MODES[1]: ("directory", "repository", "commit", "version", "workflow"),
    MODES[2]: ("exercise",),
}
SCENARIOS = (
    "Warehouse inventory: original exact-cent example",
    "Exact cents: three ten-cent units",
    "Valid zero-stock products",
    "High-value stock within original bounds",
    "Unsigned four-asset integrity exercise",
    "Different unsigned application member",
)
HELP = """Use this project's actual trusted inventory summarizer or original four-asset preflight. Inventory JSON uses unique stock IDs, bounded integer units and decimal USD strings with exactly two cents digits. Select a real authorized file; inspect product contributions and exact totals. No monetary floating-point calculation or incoming executable is used.
Release preflight needs the exact four allowed assets and independently supplied repository, full commit, stable version and workflow. It checks original manifest identity, asset hashes/sizes and six bounded zipapp members. SUCCESS IS INTEGRITY-ONLY: authentication and signer workflow have NOT been verified. An attacker can rewrite a matching manifest, so hashes alone cannot authorize execution, promotion or rollback. This offline GUI never runs a downloaded zipapp, invokes gh, downloads data or accesses an account. Keep original authenticated verify/impact/promote/rollback CLI controls for separately trusted workflows.
Prepared release examples are explicitly unsigned synthetic data with fictional source identities, not real builds, CI results, signatures or attestations. They populate ordinary controls. No signing keys, login tokens or provider credentials are requested. Saved inventory/report data and chosen paths are sensitive owner-local plaintext, not encrypted storage or multiuser authentication. Inspect/filter/search does not change original counts; export is exact and never overwrites. Exit retains the worker and owner lock until work commits and finishes."""


def scenario(name: str) -> dict[str, str]:
    """Populate normal editable data/identity controls without running or authenticating a release."""
    if name not in SCENARIOS:
        raise Rejected("unknown prepared offline exercise")
    return {
        "mode": MODES[2],
        "inventory": "",
        "directory": "",
        "repository": REPOSITORY,
        "commit": "a" * 40,
        "version": "1.2.0",
        "workflow": WORKFLOW,
        "exercise": CHOICES["exercise"][SCENARIOS.index(name)],
    }


def inventory_example(name: str) -> list[dict[str, Any]]:
    """Return realistic inert stock rows exercising exact cents, zero stock and bounded high values."""
    examples = {
        "warehouse": [
            {"id": "SENSOR", "units": 12, "unit_price_usd": "84.95"},
            {"id": "CABLE", "units": 30, "unit_price_usd": "9.50"},
            {"id": "ADAPTER", "units": 4, "unit_price_usd": "105.75"},
        ],
        "exact-cents": [{"id": "FASTENER", "units": 3, "unit_price_usd": "0.10"}],
        "zero-stock": [
            {"id": "EMPTY", "units": 0, "unit_price_usd": "12.99"},
            {"id": "FREE-SAMPLE", "units": 2, "unit_price_usd": "0.00"},
        ],
        "high-value": [{"id": "TEST-EQUIPMENT", "units": 2, "unit_price_usd": "9999999999.99"}],
    }
    if name not in examples:
        raise Rejected("unknown inventory exercise")
    return examples[name]


def unsigned_fixture(output: Path, changed: bool = False) -> TrustPolicy:
    """Construct inert UNSIGNED parser fixtures, never fake CI/provenance or execute their source members."""
    policy = TrustPolicy(REPOSITORY, "a" * 40, "1.2.0")
    output.mkdir()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, data in {
            "__main__.py": b"raise RuntimeError('Inert unsigned GUI fixture; never execute')\n",
            "delivery/__init__.py": b"# Explicit fictional parser fixture, not a published build\n",
            "delivery/io.py": b"# Inert synthetic member\n",
            "delivery/probe.py": b"# Inert synthetic member\n"
            + (b"# changed\n" if changed else b""),
            "LICENSE": b"Synthetic data fixture; no embedded third-party application\n",
            "BUILD.json": canonical({"fixture": True, "source": "a" * 40}),
        }.items():
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    payloads = {
        "release-probe-1.2.0.pyz": buffer.getvalue(),
        "sbom.cdx.json": canonical(
            {"fixture": True, "scope": "Unsigned synthetic inventory data, not a claimed SBOM"}
        ),
        "validation.json": canonical(
            {"fixture": True, "scope": "No real CI result or signature is asserted"}
        ),
    }
    for name, raw in payloads.items():
        (output / name).write_bytes(raw)
    (output / "release.json").write_bytes(
        canonical(
            {
                "schema": 1,
                "version": policy.version,
                "source": {
                    "repository": policy.repository,
                    "commit": policy.commit,
                    "ref": "refs/tags/v" + policy.version,
                },
                "assets": [
                    {"name": name, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
                    for name, raw in sorted(payloads.items())
                ],
            }
        )
    )
    return policy


def snapshot_release(source: Path, stage: Path, policy: TrustPolicy) -> None:
    """Copy only the exact four bounded ordinary input assets before running the original offline preflight."""
    source = unlinked(source)
    if not source.is_dir() or {p.name for p in source.iterdir()} != policy.names | {"release.json"}:
        raise Rejected("choose the exact four-asset release directory")
    stage.mkdir()
    for name in ("release.json", *sorted(policy.names)):
        raw = read_source(source / name, 65536 if name == "release.json" else 2 * 1024 * 1024)
        (stage / name).write_bytes(raw)


def analyze(
    state: Workspace, parameters: dict[str, str], stage: Path
) -> tuple[str, str, dict[str, bytes]]:
    """Use actual trusted core calculations/preflight on stable data copies; no executable, signer or deployment call."""
    mode = parameters.get("mode")
    if mode not in MODES:
        raise Rejected("choose a supported offline operation")
    exercise = parameters.get("exercise", "")
    if mode == MODES[2] and exercise not in CHOICES["exercise"]:
        raise Rejected("choose a supported prepared exercise")
    inventory = mode == MODES[0] or mode == MODES[2] and not exercise.startswith("unsigned-")
    if inventory:
        raw = (
            read_source(Path(parameters["inventory"]), MAX_INPUT)
            if mode == MODES[0]
            else canonical(inventory_example(exercise))
        )
        rows = json_value(raw)
        totals = summarize(rows)
        report = {
            "schema": 1,
            "kind": "trusted_source_inventory",
            "totals": totals,
            "products": [
                {**row, "stock_value_usd": summarize([row])["inventory_value_usd"]} for row in rows
            ],
            "input_sha256": hashlib.sha256(raw).hexdigest(),
            "scope": "Actual trusted source summarizer; input rows are data. This is not downloaded-release authentication.",
        }
        return (
            "inventory",
            f"{totals['products']} products; {totals['units']} units; USD {totals['inventory_value_usd']}; trusted source only",
            {"inventory.json": canonical(report)},
        )
    if mode == MODES[2]:
        selected = stage / "unsigned-fixture"
        policy = unsigned_fixture(selected, exercise == "unsigned-changed-member")
    else:
        policy = TrustPolicy(
            parameters.get("repository", ""),
            parameters.get("commit", ""),
            parameters.get("version", ""),
            parameters.get("workflow", ""),
        )
        selected = stage / "release-snapshot"
        snapshot_release(Path(parameters.get("directory", "")), selected, policy)
    manifest = preflight(selected, policy)
    with zipfile.ZipFile(selected / f"release-probe-{policy.version}.pyz") as archive:
        members = [
            {
                "name": name,
                "bytes": len(archive.read(name)),
                "sha256": hashlib.sha256(archive.read(name)).hexdigest(),
            }
            for name in sorted(archive.namelist())
        ]
    result = {
        "schema": 1,
        "kind": "integrity_only_release_preflight",
        "status": "INTEGRITY_ONLY_NOT_AUTHENTICATED",
        "authentication_verified": False,
        "signer_workflow_verified": False,
        "execution_permitted": False,
        "expected_identity": asdict(policy),
        "manifest": manifest,
        "manifest_sha256": hashlib.sha256(
            read_source(selected / "release.json", 65536)
        ).hexdigest(),
        "members": members,
        "prepared_unsigned_fixture": mode == MODES[2],
        "scope": "Only original structure, identity assertions and byte hashes checked. A rewritten matching manifest can pass. No attestations, signer workflow, current deployment, compatibility or safety were verified; incoming payload was never executed.",
    }
    return (
        "integrity-only-preflight",
        "INTEGRITY ONLY — NOT AUTHENTICATED; 3 asset hashes / 6 members; execution NOT permitted",
        {"preflight.json": canonical(result)},
    )


def views(files: dict[str, bytes]) -> dict[str, list[dict[str, Any]]]:
    """Keep exact stock contributions or release integrity/authentication scope separate in inspectable views."""
    if "inventory.json" in files:
        report = json_value(files["inventory.json"])
        return {
            "Stock and exact values": [{"kind": "stock", **row} for row in report["products"]],
            "Unfiltered totals and scope": [
                {"kind": "inventory_scope", **report["totals"], "scope": report["scope"]}
            ],
        }
    report = json_value(files["preflight.json"])
    return {
        "Integrity-only asset inventory": [
            {"kind": "asset", **row} for row in report["manifest"]["assets"]
        ],
        "Inert application member hashes": [{"kind": "member", **row} for row in report["members"]],
        "Authentication NOT verified": [{"kind": "scope", **report}],
    }


def cells(row: dict[str, Any]) -> tuple[str, str, str, str]:
    """Render concise actual values while retaining complete digests and scope in selected detail."""
    if row["kind"] == "stock":
        return (
            str(row["id"]),
            str(row["units"]),
            "USD " + row["stock_value_usd"],
            "Exact unit price USD " + row["unit_price_usd"],
        )
    if row["kind"] in {"asset", "member"}:
        return (
            str(row["name"]),
            str(row.get("size", row.get("bytes"))),
            str(row["sha256"])[:16] + "…",
            "INTEGRITY ONLY; not authenticated",
        )
    if row["kind"] == "inventory_scope":
        return (
            "Inventory totals",
            str(row["units"]) + " units",
            "USD " + row["inventory_value_usd"],
            str(row["products"]) + " products; trusted source",
        )
    return (
        "Authentication NOT verified",
        "Offline only",
        "No signer verification",
        "NO EXECUTION PERMISSION",
    )
