# Local API and evidence contract

All routes require the exact `Host: 127.0.0.1:<port>`. An Origin, if present, must be the same HTTP origin; cross-site fetch metadata is rejected. No CORS, accounts or mutation endpoints. This is not an Internet API.

| Route              | Response                                                                      |
| ------------------ | ----------------------------------------------------------------------------- |
| `GET /api/health`  | Local educational service health (does not prove a worker build is available) |
| `GET /api/catalog` | Reviewed choices, defaults, synthetic scenario labels and limitations         |
| `GET /api/run`     | Complete JSON experiment/reference evidence                                   |
| `GET /api/report`  | Same evidence rendered as JSON, CSV or inert HTML attachment                  |

Run/report query keys: `scenario`, `duration`, `demand`, `cooling`, `inertia`, `feedback`. Report additionally accepts `format=json|csv|html`. Defaults match `simulator.engine.Settings`; exact public choices are in [MODEL](MODEL.md) and `/api/catalog`. Unknown, duplicate, empty, nonfinite and unreviewed values fail. At most eight query fields; paths over 1024 characters return 414. Unsupported routes return 404; invalid query 400; origin violation 403; non-GET 405; unavailable worker/resource 500 with generic text. HEAD has no body.

Example: `/api/run?scenario=cooling-dip&duration=300&demand=1&cooling=0.5&inertia=1&feedback=0`. All numbers are dimensionless. There is no input for physical fuel, rods, cooling material or plant data.

Evidence schema `reactor-thermal-evidence/1` contains `id`, `author`, `scenario`, `settings`, `provenance`, `experiment`, `reference`, and `events`. Each series includes integer-time samples with `time`, `source`, `hot`, `cool`, `useful`, `input_energy`, `rejected_energy`, `stored_change`, `balance_error`. Maximum residual is over output samples. The experiment carries worker SHA-256 and a fixed-coefficient model version. Run identity hashes canonical JSON excluding `id` itself, including the actual binary fingerprint and results.

JSON forbids NaN/Infinity. CSV uses generated IDs, fixed series/units and numeric fields; it does not emit arbitrary labels into spreadsheet cells. HTML escapes all JSON and denies scripts/resources through its own CSP. Attachment filenames are fixed, not constructed from query text. The server never accepts file paths, database paths, commands, code or remote URLs.
