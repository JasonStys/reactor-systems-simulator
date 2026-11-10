# Reactor Systems Simulator handbook

By Jason Stys.

Explore a fictional dimensionless thermal analogy, compare forcing against matched baselines and inspect sampled numerical differences. The model contains no nuclear physics, fuel, neutron, criticality or radiation calculation and cannot monitor or control a plant.

Explore fictional dimensionless thermal lessons, compare forcing with matched baselines and export sampled differences through 1.1 portable apps.

Packages the numerical kernel and explanatory interface so a reviewer can distinguish changed forcing from changed assumptions and inspect the same evidence after extraction.

## Read the documentation

| Edition                                                      | Audience and contents                                                                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| [project-guide.docx](reports/project-guide.docx)             | User and developer guide: purpose, current usage, design, boundaries and source references.                        |
| [validation-review.docx](reports/validation-review.docx)     | Reviewer edition: exact tested baseline, observed workflows, dated local results and remaining limits.             |
| [validation-evidence.xlsx](reports/validation-evidence.xlsx) | Two filterable Excel Tables for observed workflows and test-source inventory, with recalculating outcome formulas. |

The editable Markdown remains the maintenance source. The Word files are readable editions. The workbook is an evidence index rather than a test runner. See [publication identities and review](reports/publications.json) and the [documentation refresh record](reports/documentation-refresh-2026-11-09.md).

## Current usage and help

[README quick start](../README.md) is the entry point. Use the project-specific guides below before changing inputs, operating modes or deployment assumptions.

### Usage and operations

- [RELEASE](RELEASE.md)
- [USER GUIDE](USER_GUIDE.md)

### Design and contracts

- [API](API.md)
- [ARCHITECTURE](ARCHITECTURE.md)
- [MODEL](MODEL.md)

### Security and validation

- [SECURITY](SECURITY.md)
- [VALIDATION](VALIDATION.md)

## Historical results and reproduction

The reviewed source is [`a6d4fc55f12681c5b5bdec1dcd09ddb801d94683`](https://github.com/JasonStys/reactor-systems-simulator/tree/a6d4fc55f12681c5b5bdec1dcd09ddb801d94683). The observed functional workflow baseline is `a6d4fc55f12681c5b5bdec1dcd09ddb801d94683`; those observations are recorded at `2026-11-10T05:25:40.628667+00:00`. They do not certify an unrun later revision.

- [Detailed recorded validation](reports/PORTABLE_RELEASE_20261109.md)
- [Current Actions](https://github.com/JasonStys/reactor-systems-simulator/actions) records later integration checks separately.
- Preserve dated measurements and follow the existing testing guide to reproduce them; a test-source inventory alone does not establish execution.

## Practical boundaries

- A fictional thermal analogy, with no nuclear physics, fuel, neutron, criticality, radiation or real-plant monitoring/control.
- Sampled extrema and numerical tolerances are not physical measurements, safety limits or operating recommendations.
- Unsigned educational desktop portable packages; no system installer, native mobile app, plant connection or safety certification.

## Maintaining these editions

Update the editable usage/design/test documents first. Rebuild and visually review every Word page and workbook tab before replacing an edition; verify the exact binary digests and evidence source in publications.json. Keep account data, logs with secrets, installed-app state and private test stores out of documentation. Source and release assets retain their existing security and licensing boundaries.
