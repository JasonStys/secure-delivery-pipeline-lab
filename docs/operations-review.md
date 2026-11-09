# Authenticated impact review and committed receipts

Created by Jason Stys. Release engineers can inspect what would change before running an already authenticated candidate. Recovery engineers can see why a successful local slot transition occurred. Neither feature weakens the exact caller-selected signer/source trust policy.

## Review a candidate against the actual active slot

Obtain both full source SHAs and version tags independently. Use an existing marked disposable deployment root with an active release; this command cannot initialize an empty deployment.

```text
python -m delivery impact --directory out/candidate --root lab-state --version CANDIDATE_VERSION --commit CANDIDATE_FULL_SHA --active-version ACTIVE_VERSION --active-commit ACTIVE_FULL_SHA --out artifacts/impact-review
```

The independently supplied active identity must match the current active pointer. Active and candidate each have their own `--repo`/`--workflow` or `--active-repo`/`--active-workflow` options, with this repository's release workflow defaults. Under the deployment lock, the command copies allowlisted bytes into private temporary snapshots and invokes the full existing GitHub CLI attestation verifier for **both manifests and all six assets**. Integrity-only preflight is never sufficient. Verification/network/identity failure produces no authenticated review. No payload is executed and no health probe or pointer update occurs.

The output identifies exact trust policies, observed active slot, manifest hashes, logical application/SBOM/validation asset hashes and byte-size deltas, and per-member changed/unchanged/added/removed states without extracting or importing code. The current strict six-member archive allowlist normally means member additions/removals are impossible; the table still describes the compared set explicitly. BUILD.json metadata normally changes with version/commit even if application logic is unchanged. Hash differences do not establish compatibility, security or performance improvement. Another operation may change the pointer after review; normal promotion must reauthenticate/recheck health again. Outputs are new-directory-only private JSON and escaped, scriptless HTML; their parent must exist.

## Successful transition receipts

```text
python -m delivery promote --directory out/candidate --root lab-state --version VERSION --commit FULL_SHA --operator "Release engineer" --change-ref CHG-201
python -m delivery rollback --root lab-state --version PREVIOUS_VERSION --commit PREVIOUS_FULL_SHA --operator "Recovery engineer" --change-ref INC-202
```

After the existing staged authentication and fixed health self-test succeed, **active pointer, previous pointer and successful receipt history are one atomic `active.json` write**. A write failure preserves both the old pointers and old receipts. A verified immutable slot may remain for a later retry. Failed authentication/health attempts do not get successful receipts; inspect the command's sanitized error and CI results. Idempotently promoting the already-active identity does not append another transition. Explicit rollback still requires the independently trusted immediate previous identity.

State schema 2 contains the newest **20** successful transition receipts with increasing sequence, promote/rollback action, from/to slots, independently supplied trust policy, exact accepted manifest SHA-256, passed health, UTC verification time and bounded asserted operator/change reference. It validates continuity and last-receipt/pointer consistency before use. No source trust is inferred from state or receipt contents. Operator labels default to explicitly unspecified context; they are **local assertions, not authenticated identities, signatures, an append-only audit log or external approval**. An owner able to edit the entire local state can rewrite that metadata. Keep runtime state private and do not place secrets in context fields.

Legacy schema-1 pointers are accepted, with no invented historical receipts. The next successful transition atomically writes schema 2 and starts honest history at that transition. Very old history is dropped at the 20-entry bound; this does not delete release slots. Malformed history is rejected rather than silently reset. The log is bounded to 64 KiB of input; slot and context contracts remain closed. These are disposable local lab operations, not production deployment management or a malware sandbox.

Unit tests mock only external attestation service responses and label their release fixtures unsigned. They run actual authored zipapp health, staged bytes and pointer/receipt commits in owned temporary directories. Live cryptographic behavior remains covered by the unchanged hosted release smoke gate; an unsigned unit fixture is never claimed to be genuinely signed.
