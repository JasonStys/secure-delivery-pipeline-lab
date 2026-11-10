# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `e37b189fa604bb0d6951e4a926d20ed9606298a1`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File | Bytes | SHA-256 | Reviewed scope |
| --- | ---: | --- | --- |
| [project-guide.docx](project-guide.docx) | 44463 | `66032e1438ae4e3fc92d3001d21aca2d4eba11b40a62820b0a6fef14c9a8d160` | 5 pages, each viewed individually |
| [validation-review.docx](validation-review.docx) | 44289 | `4e32b72e73ecf2724ba462b6ffb70544349065d02de0e9dae1b52f3d17fe9c9b` | 5 pages, each viewed individually |
| [validation-evidence.xlsx](validation-evidence.xlsx) | 7266 | `59cad1ccb78cd07be2a4c2857bf4d8ef451eaf6920d8048aa4241c90c5223cd6` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `e37b189fa604bb0d6951e4a926d20ed9606298a1`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Integration-local checks

Observed at `2026-11-10T07:30:55.154472+00:00` on Windows in this repository’s isolated locked development environment. Commands below use its activated Python environment. The documentation source baseline remains the immutable revision above; these checks validate this documentation integration locally.

| Command | Observed result |
| --- | --- |
| `python -m ruff check .` | Passed, exit 0. |
| `python -m ruff format --check .` | Passed, exit 0. |
| `python -m mypy` | Passed, exit 0. |
| `python scripts/code_map.py --check` | Passed, exit 0. |
| `python -m pytest --cov --cov-report=term-missing` | Passed, exit 0. |

The independent publication audit also matched every copied Office file to its approved SHA-256, checked ZIP package integrity and current page/tab approvals, compared immutable workflow/source metadata, and resolved every local handbook/report link within the repository. Hosted PR/main, browser, platform and container jobs remain separate required checks; they are not inferred from these local results.

The unchanged full Python suite passed 140 tests at 93.05% combined statement/branch coverage, retaining the 85% floor. The release workflow was not dispatched and no installed application or deployment slot was changed.
