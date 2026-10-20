# Validation evidence and test strategy

Author: Jason Stys. Status below distinguishes local observations from hosted checks; authoritative current results are the linked workflow runs. These tests verify an invented mathematical analogy and software contracts, **not real-reactor physics or safety**.

## Local results — 2026-10-20

| Check                                               | Observed result                                                                                                  |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| C++20 MSVC 19.51, Release, warnings as errors       | Build and 3 CTest entries passed                                                                                 |
| Python 3.14.6 unit/property/scientific/HTTP/SQL/CLI | 98 passed; 99.44% combined line/branch coverage; 90% gate                                                        |
| TypeScript display/preference units                 | 15 passed                                                                                                        |
| Chromium / WebKit production-server tests           | 12 passed (six each), including real downloads, failures, stale responses, keyboard/mobile and axe scans         |
| Firefox production-server tests                     | 6 passed; all 18 browser tests passed across three engines                                                       |
| Dependency audits                                   | npm: 0 vulnerabilities; pip-audit: no known vulnerabilities in locked development graph                          |
| Ruff / strict mypy / TypeScript production build    | Passed in local checks                                                                                           |
| Windows frozen portable app                         | Real executable export, built assets, health and scenario API smoke passed; hosted cross-platform checks pending |

The first local MSBuild attempt was blocked by sandbox registry access before compilation; stable Visual Studio selection and normal build permissions resolved that environment issue. Initial test fixtures also required a writable temporary directory in this sandbox; no product permissions or OS protections were weakened. Source-level defects found during development included missing CSS import types and event-boundary instantaneous output convention; both were corrected before publication.

## Numerical verification

- Analytic source exponential across the full output grid and nonzero-initial-state analytic thermal equilibrium.
- Independent Python RK4 at model times 20, 60 and 300, with step 0.01, both linear baseline and generic derating 0.15; native step 0.1 maximum state-error assertion below 0.003 in normalized units. Halving native step to 0.05 must reduce combined hot/cool error by at least 40%.
- All four scenarios, cooling factors, exact event boundaries, right-hand output at restoration, generic derating, source-off and finite positive states.
- Discrete energy ledger tolerance, exact output grid and immutable content IDs.
- Hypothesis samples reviewed parameter combinations; invalid/nonfinite/boolean/out-of-range settings and malformed native numeric tokens are rejected independently.

## Boundary and user testing

Tests exercise actual native subprocesses, real loopback HTTP sockets, SQLite triggers/transactions and CLI exports. Corrupt/missing/timed-out/nonzero workers cannot produce plausible successful evidence. Host/origin rebinding, traversal/encoded paths, symlink escape, duplicate/excessive queries, unsafe download names, mutations and resource failures are covered. Reports preserve data, HTML is inert, CSV contains no arbitrary formula-bearing labels, exports refuse overwrite and histories refuse tampering or a 101st distinct run.

Browser tests use the built production assets and production handler, not mocked successful simulation data. Three engines check no unsolicited external requests, current applied settings, baseline comparison, timeline playback, actual JSON/CSV/HTML downloads, failed service retry, aborted stale requests, blocked preferences and desktop/390px mobile accessibility. Automated axe checks are useful but not a full manual accessibility audit or WCAG certification. Local visual QA is saved in `docs/images/workbench.jpg`.

## Hosted gates

Validation: Linux Python 3.12/3.14, Windows/macOS Python 3.14; compiled C++ on each, Python coverage, style/types/inventory, browser engines, audits, Clang ASan+UBSan, GCC production line coverage and three frozen platform smoke builds. CodeQL analyzes C++, Python and JavaScript/TypeScript with security-and-quality queries. Manual release packaging additionally requires those exact-SHA checks to pass.

Workflow links and final release evidence will be recorded after actual hosted completion. A green test is not a physical validation, guarantee against unknown defects, or certification for nuclear operations.

## Measured numerical and performance report

[`reports/numerical-validation.json`](reports/numerical-validation.json) contains measured independent-reference errors and worker identity. Regenerate with `python -m tools.measure` after a native build. The recorded Windows AMD64/Python 3.14.6 observation used nine cold/warm repetitions: median complete 600-unit experiment/reference evidence generation was about 65.8 ms cold and 10.9 ms warm. This includes process startup for cold runs and JSON decoding/content hashing even when warm. It is a single-host observation, not a speed guarantee or physical validation. Largest sampled residual for the reported cooling-dip run was approximately `9.67e-11` normalized energy units. Source/thermal errors and refinement results are reported separately so conservation is not mistaken for solution accuracy.
