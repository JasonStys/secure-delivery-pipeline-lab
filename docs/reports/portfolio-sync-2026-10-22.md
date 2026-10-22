<!-- File: docs/reports/portfolio-sync-2026-10-22.md; Purpose: certificate-bundle security repair and evidence by Jason Stys. -->

# Certificate bundle maintenance — 2026-10-22

By Jason Stys. The live audit identified PYSEC-2026-4320 in certifi 2026.7.22. This branch advances only that resolved transitive package to the reported fixed release 2026.10.19 and replaces both distribution SHA-256 pins with the reviewed package hashes. No audit exclusion, ignored advisory, test weakening, runtime data or account change is included.

The complete existing native CI and code-scanning workflows validate the exact integration head before a normal merge; main is checked again afterward. [Actions](https://github.com/JasonStys/secure-delivery-pipeline-lab/actions) provides revision-specific results. The private full portfolio audit and archived old run evidence remain on the owner's PC, not in this public repository. Existing historical/audit references are preserved.
