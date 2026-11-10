# Documentation refresh — 2026-11-09

By Jason Stys.

This documentation-only edition describes source `a6d4fc55f12681c5b5bdec1dcd09ddb801d94683`. It does not change application behavior, accounts, private data, installers or published releases.

## Published editions and completed review

| File                                                 | Bytes | SHA-256                                                            | Reviewed scope                                                                                                                      |
| ---------------------------------------------------- | ----: | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [project-guide.docx](project-guide.docx)             | 90303 | `b9db0394d443879568faff22db39a321db087a7f96ffa500fe20a397b6736a04` | 4 pages, each viewed individually                                                                                                   |
| [validation-review.docx](validation-review.docx)     | 43667 | `df8cc7bb8302e529fdf6301c1ae6bbb5709f5f7a0067e11bcc650591fc34aaa2` | 4 pages, each viewed individually                                                                                                   |
| [validation-evidence.xlsx](validation-evidence.xlsx) |  7388 | `6a668366b06626ad045462f2010ffb2cd0aa37c397b7b07def018e4ba059b168` | Both tab previews; two actual Excel Tables/autoFilters; four formulas; failure-change/restore recalculation and zero formula errors |

Word review checked plain black titles, readable pagination, whole table rows, source references, practical limits and absence of clipping or overflow. Render receipts were matched to the current DOCX digest before approval. Workbook review inspected both tab previews and actual exported Table/autoFilter elements; recalculated success/failure summaries were compared independently with workflow metadata. Static previews do not draw Excel dropdown arrows; the exported workbook contains the actual filters.

## Evidence and change boundary

- Functional baseline: `a6d4fc55f12681c5b5bdec1dcd09ddb801d94683`.
- Workflow observation: `2026-11-10T05:25:40.628667+00:00`; exact run URLs and source identities remain in [publications.json](publications.json).
- Local document-package validation verifies exact copied bytes, Office ZIP integrity, approved page/tab identities and internal documentation links. Repository-specific documentation and source-policy commands are run separately and recorded in the integration handoff.
- Source/index metadata is regenerated using the repository’s existing tools. Existing privacy, security, coverage and workflow gates are retained.
- PR and later main workflows must pass independently. This record does not claim future or unrun integration CI success.

## Interpretation

The Word files document the cited source; dated source reports retain their original execution scope. A passing workflow is distinct from completed analysis with zero findings, and neither establishes production suitability. The Excel source inventory is not a per-test execution report. Checksums identify exact bytes, not a signature or publisher attestation.

Use the [handbook](../handbook.md) to choose usage, design, security and test documentation. Keep editable Markdown and reviewed editions together; do not replace historical measurements with undated claims.

## Integration-local checks

Observed at `2026-11-10T07:53:00.516203+00:00` on Windows with this repository’s existing development tools. Python commands use its isolated development environment. The documentation source baseline remains the immutable revision above; these checks validate this documentation integration locally.

| Command                                                           | Observed result |
| ----------------------------------------------------------------- | --------------- |
| `python tools/verify_repo.py --write`                             | Passed, exit 0. |
| `python tools/verify_repo.py`                                     | Passed, exit 0. |
| `python -m ruff check simulator tests tools launcher.py`          | Passed, exit 0. |
| `python -m ruff format --check simulator tests tools launcher.py` | Passed, exit 0. |
| `python -m mypy simulator`                                        | Passed, exit 0. |
| `python -m pytest --cov=simulator --cov-report=term-missing`      | Passed, exit 0. |
| `node node_modules/prettier/bin/prettier.cjs --check .`           | Passed, exit 0. |
| `node node_modules/vitest/vitest.mjs run`                         | Passed, exit 0. |

The independent publication audit also matched every copied Office file to its approved SHA-256, checked ZIP package integrity and current page/tab approvals, compared immutable workflow/source metadata, and resolved every local handbook/report link within the repository. Hosted PR/main, browser, platform and container jobs remain separate required checks; they are not inferred from these local results.

The existing suite passed 193 Python tests at 99.50% combined coverage (90% floor retained) and 17 TypeScript tests. No user service was adopted or modified, no coverage floor was reduced, and no runtime implementation changed.
