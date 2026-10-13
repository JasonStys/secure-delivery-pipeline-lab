# Formats and command contracts

Author: Jason Stys. Runtime: Python >=3.12; verification additionally needs official GitHub CLI with the documented attestation flags.

## Inventory

UTF-8 JSON array, 1–10,000 records, at most 1 MiB. Each object has exactly `id`, `units`, `unit_price_usd`. ID is a unique uppercase ASCII `[A-Z0-9_-]` string of 1–64 characters. Units is an integer, not boolean, from 0 to 1,000,000. Price is a nonnegative USD decimal string with exactly two cent digits, no leading zero ambiguity, and at most ten whole-number digits. Unknown fields, duplicate keys/IDs, NaN, Infinity and malformed bytes are rejected. This intentionally does not support currency conversion.

Output fields: `products`, `units`, `inventory_value_usd`; price output is exact cents. Synthetic example total: 3 products, 46 units, USD 1727.40.

## Release bundle

Exactly four files: `release.json`, `release-probe-VERSION.pyz`, `sbom.cdx.json`, `validation.json`. The manifest is at most 64 KiB; each asset at most 2 MiB. Extra local files must be kept in a different directory.

```json
{
  "schema": 1,
  "version": "1.0.0",
  "source": {
    "repository": "JasonStys/secure-delivery-pipeline-lab",
    "commit": "INDEPENDENT_FULL_LOWERCASE_40_HEX_SHA",
    "ref": "refs/tags/v1.0.0"
  },
  "assets": [{"name":"ALLOWLISTED_FILE","size":123,"sha256":"64_LOWERCASE_HEX"}]
}
```

This illustrative abbreviated manifest is **not** a valid release. A valid manifest has all three distinct assets, exact field sets and real hashes/sizes. A modified manifest with recomputed hashes must still fail cryptographic authentication.

The zipapp contains exactly `__main__.py`, `delivery/__init__.py`, `delivery/io.py`, `delivery/probe.py`, `LICENSE`, `BUILD.json`; regular entries only, <=512 KiB/member and <=1 MiB total expansion. The builder uses fixed timestamps and stored compression. `BUILD.json` is explanatory metadata, not the trust anchor.

The CycloneDX 1.6 SBOM's root application has MIT licensing, VCS identity and no external package dependencies. Its `urn:uuid:` serial number is deterministic UUIDv5 from repository/commit/version, satisfying the pinned attester's stricter identity contract without introducing random build bytes. It explicitly documents external interpreter/OS scope. Validation JSON records actual release-job JUnit counts, combined statement/branch coverage and benchmark measurements; other CI scanner gates are independently checked by workflow run status.

## Trust policy and CLI

`--repo` defaults to this repository; `--workflow` to `.github/workflows/release.yml`. `--commit` is independently obtained full lowercase SHA, required; `--version` is stable `major.minor.patch` with no leading zero components and <=6 digits/component. Source ref is derived as `refs/tags/vVERSION`. CLI passes fixed argument arrays, not shell strings.

`preflight`: structure/integrity only, never authentication. `verify`: cryptographic verification of all four files. `promote`: verified stage and actual authored health, then pointer swap. `rollback`: previous slot only, independently specified identity, fresh verification.

Exit 0: command's explicitly labeled success. Exit 2: rejection/input/operational failure. Argument-parser usage errors also return 2. A successful preflight's status deliberately contains `not-authenticated`. Never use its exit code as a deployment approval.

## Deployment state

New/empty user-selected root gets `lab.json`, `.lock`, `slots/`, and later `active.json`. Existing nonempty roots without the exact marker are refused. Slot names are `vVERSION-FULLSHA`. State schema has `schema:1`, `active`, `previous`; pointers are null or validated slot names. No pointer may select an arbitrary file or supply repository/commit trust by itself.

Slots remain immutable for ordinary tool operations. An existing matching slot is reverified. Active pointer changes only after staged authentication and health pass. Previous slot data is preserved; no automatic pruning or destructive cleanup is provided.
