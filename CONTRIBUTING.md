# Contributing

Use focused pull requests with a synthetic regression reproducer. Keep release trust policy explicit, verification fail-closed, runtime dependencies minimal and generated secrets/data outside Git.

Run the README's local gates. Format Python before running `python scripts/code_map.py`; then run `--check`. Update the README file guide when adding files and the contracts/threat model when changing a boundary. Function/class docstrings describe purpose, inputs, outputs and meaningful failure behavior; name variables clearly and label nonobvious security-critical sections.

Never add advisory suppressions, verification bypasses, mutable action tags, `pull_request_target` execution of fork code, Actions artifact uploads or production deployment credentials without a separately reviewed design change. Releases are maintainer-dispatched from exact green tags; publication does not happen automatically on arbitrary pushes.
