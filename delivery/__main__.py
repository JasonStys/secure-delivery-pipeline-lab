"""Explicit trust-policy verification, lab promotion and rollback CLI by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 26
# parameter: argv — line 26
# variable: parser — line 28
# variable: arguments — line 36
# variable: policy — line 38
# variable: result — line 47
# variable: result — line 50
# variable: result — line 52
# variable: result — line 54
# END CODE MAP

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from delivery.deploy import promote, rollback
from delivery.io import Rejected
from delivery.verify import REPOSITORY, WORKFLOW, TrustPolicy, preflight, verify_release


def main(argv: list[str] | None = None) -> int:
    """Validate CLI arguments and fail closed on any trust, filesystem, or health error."""
    parser = argparse.ArgumentParser(description="Secure Delivery Pipeline Lab — Jason Stys")
    parser.add_argument("command", choices=["preflight", "verify", "promote", "rollback"])
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--repo", default=REPOSITORY)
    parser.add_argument("--workflow", default=WORKFLOW)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--version", required=True)
    arguments = parser.parse_args(argv)
    try:
        policy = TrustPolicy(
            arguments.repo, arguments.commit, arguments.version, arguments.workflow
        )
        if arguments.command in {"preflight", "verify", "promote"} and not arguments.directory:
            parser.error("this command requires --directory")
        if arguments.command in {"promote", "rollback"} and not arguments.root:
            parser.error("this command requires --root")
        if arguments.command == "preflight":
            preflight(arguments.directory, policy)
            result = {"status": "integrity-only-not-authenticated"}
        elif arguments.command == "verify":
            verify_release(arguments.directory, policy)
            result = {"status": "authenticated"}
        elif arguments.command == "promote":
            result = promote(arguments.directory, arguments.root, policy)
        else:
            result = rollback(arguments.root, policy)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Rejected, OSError) as error:
        print(f"Release rejected: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
