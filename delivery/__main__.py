"""Explicit trust-policy verification, lab promotion and rollback CLI by Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: main — line 28
# parameter: argv — line 28
# variable: parser — line 30
# variable: arguments — line 45
# variable: policy — line 47
# variable: result — line 63
# variable: result — line 66
# variable: result — line 68
# variable: result — line 76
# variable: result — line 90
# END CODE MAP

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from delivery import impact
from delivery.deploy import promote, rollback
from delivery.io import Rejected
from delivery.verify import REPOSITORY, WORKFLOW, TrustPolicy, preflight, verify_release


def main(argv: list[str] | None = None) -> int:
    """Validate CLI arguments and fail closed on any trust, filesystem, or health error."""
    parser = argparse.ArgumentParser(description="Secure Delivery Pipeline Lab — Jason Stys")
    parser.add_argument("command", choices=["preflight", "verify", "promote", "rollback", "impact"])
    parser.add_argument("--directory", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--repo", default=REPOSITORY)
    parser.add_argument("--workflow", default=WORKFLOW)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--active-commit")
    parser.add_argument("--active-version")
    parser.add_argument("--active-repo", default=REPOSITORY)
    parser.add_argument("--active-workflow", default=WORKFLOW)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--operator", default="unspecified-local-operator")
    parser.add_argument("--change-ref", default="unspecified-change")
    arguments = parser.parse_args(argv)
    try:
        policy = TrustPolicy(
            arguments.repo, arguments.commit, arguments.version, arguments.workflow
        )
        if (
            arguments.command in {"preflight", "verify", "promote", "impact"}
            and not arguments.directory
        ):
            parser.error("this command requires --directory")
        if arguments.command in {"promote", "rollback", "impact"} and not arguments.root:
            parser.error("this command requires --root")
        if arguments.command == "impact" and (
            not arguments.active_commit or not arguments.active_version
        ):
            parser.error("impact requires --active-commit and --active-version")
        if arguments.command == "preflight":
            preflight(arguments.directory, policy)
            result = {"status": "integrity-only-not-authenticated"}
        elif arguments.command == "verify":
            verify_release(arguments.directory, policy)
            result = {"status": "authenticated"}
        elif arguments.command == "promote":
            result = promote(
                arguments.directory,
                arguments.root,
                policy,
                operator=arguments.operator,
                change_ref=arguments.change_ref,
            )
        elif arguments.command == "impact":
            result = impact.review(
                arguments.directory,
                arguments.root,
                policy,
                TrustPolicy(
                    arguments.active_repo,
                    arguments.active_commit,
                    arguments.active_version,
                    arguments.active_workflow,
                ),
            )
            if arguments.out:
                impact.export(result, arguments.out)
        else:
            result = rollback(
                arguments.root, policy, operator=arguments.operator, change_ref=arguments.change_ref
            )
        print(json.dumps(result, sort_keys=True))
        return 0
    except (Rejected, OSError) as error:
        print(f"Release rejected: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
