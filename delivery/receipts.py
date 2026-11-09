"""Bounded committed local deployment receipts; asserted context, not signatures. Created by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# variable: LIMIT — line 47
# variable: SLOT — line 48
# definition: context — line 51
# parameter: value — line 51
# variable: c — line 57
# definition: valid_slot — line 63
# parameter: value — line 63
# definition: validate — line 68
# parameter: active — line 68
# parameter: previous — line 68
# parameter: rows — line 68
# variable: prior — line 72
# variable: row — line 73
# variable: identity — line 101
# variable: value — line 105
# variable: policy — line 108
# variable: prior — line 130
# definition: committed — line 135
# parameter: previous — line 136
# parameter: slot — line 137
# parameter: policy — line 138
# parameter: directory — line 139
# parameter: action — line 140
# parameter: operator — line 141
# parameter: change_ref — line 142
# variable: rows — line 145
# variable: sequence — line 146
# variable: row — line 147
# variable: history — line 159
# variable: result — line 160
# END CODE MAP

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from delivery.io import Rejected, read_bytes
from delivery.verify import TrustPolicy

LIMIT = 20
SLOT = re.compile(r"v[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}-[a-f0-9]{40}\Z")


def context(value: Any) -> str:
    """Bound printable asserted operator/change identifiers; never record credentials in these fields."""
    if (
        not isinstance(value, str)
        or not value.strip()
        or len(value) > 120
        or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value)
    ):
        raise Rejected("invalid receipt context")
    return value


def valid_slot(value: Any) -> bool:
    """Check local slot syntax only; it does not establish trust in source or bytes."""
    return value is None or isinstance(value, str) and SLOT.fullmatch(value) is not None


def validate(rows: Any, active: Any, previous: Any) -> None:
    """Validate <=20 contiguous state receipts, retaining the independent caller-selected trust boundary."""
    if not isinstance(rows, list) or not 1 <= len(rows) <= LIMIT:
        raise Rejected("invalid receipt history bound")
    prior = None
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "sequence",
            "action",
            "from",
            "to",
            "identity",
            "manifest_sha256",
            "health",
            "verified_at",
            "operator",
            "change_ref",
        }:
            raise Rejected("invalid receipt fields")
        if (
            type(row["sequence"]) is not int
            or not 1 <= row["sequence"] <= 1000000000
            or row["action"] not in ("promote", "rollback")
            or row["health"] != "passed"
        ):
            raise Rejected("invalid receipt outcome")
        if (
            not valid_slot(row["from"])
            or not valid_slot(row["to"])
            or row["to"] is None
            or row["from"] == row["to"]
        ):
            raise Rejected("invalid receipt pointers")
        identity = row["identity"]
        if (
            not isinstance(identity, dict)
            or set(identity) != {"repository", "commit", "version", "workflow"}
            or not all(isinstance(value, str) for value in identity.values())
        ):
            raise Rejected("invalid receipt identity")
        policy = TrustPolicy(**identity)
        if (
            row["to"] != f"v{policy.version}-{policy.commit}"
            or not isinstance(row["manifest_sha256"], str)
            or re.fullmatch(r"[a-f0-9]{64}", row["manifest_sha256"]) is None
        ):
            raise Rejected("receipt identity mismatch")
        context(row["operator"])
        context(row["change_ref"])
        if (
            not isinstance(row["verified_at"], str)
            or re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", row["verified_at"]) is None
        ):
            raise Rejected("invalid receipt timestamp")
        try:
            datetime.strptime(row["verified_at"], "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as error:
            raise Rejected("invalid receipt timestamp") from error
        if prior is not None and (
            row["sequence"] != prior["sequence"] + 1 or row["from"] != prior["to"]
        ):
            raise Rejected("receipt history is not contiguous")
        prior = row
    if rows[-1]["to"] != active or rows[-1]["from"] != previous:
        raise Rejected("receipt does not match committed pointers")


def committed(
    previous: dict[str, Any],
    slot: str,
    policy: TrustPolicy,
    directory: Path,
    action: str,
    operator: str,
    change_ref: str,
) -> dict[str, Any]:
    """Build pointer+receipt as one atomic-write payload, bounded to the newest20 successful transitions."""
    rows = previous.get("receipts", [])
    sequence = rows[-1]["sequence"] + 1 if rows else 1
    row = {
        "sequence": sequence,
        "action": action,
        "from": previous["active"],
        "to": slot,
        "identity": asdict(policy),
        "manifest_sha256": hashlib.sha256(read_bytes(directory / "release.json")).hexdigest(),
        "health": "passed",
        "verified_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "operator": context(operator),
        "change_ref": context(change_ref),
    }
    history = [*rows, row][-LIMIT:]
    result = {"schema": 2, "active": slot, "previous": previous["active"], "receipts": history}
    validate(history, result["active"], result["previous"])
    return result
