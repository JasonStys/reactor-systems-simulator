# Architecture and decision record

Status: accepted. Author: Jason Stys. Scope: local educational software, not industrial control.

```text
TypeScript / HTML / CSS browser
  → same-origin, read-only loopback Python service
    → finite Settings → fixed C++ executable → checked JSON
    → evidence / reference / SHA-256 → JSON, CSV, inert HTML
CLI export → optional local SQLite history (never an HTTP path)
```

C++20 owns numerical state and the two-by-two solve: explicit value types, finite workload bounds, no shared mutable simulation state, standard-library-only native runtime. Python standard library owns HTTP, process supervision, evidence formatting and transactional SQLite. TypeScript owns accessible interaction, chart projections and state cancellation. HTML/CSS provide semantic layout without a framework or third-party runtime scripts. SQL defines immutable history invariants. Languages have clear boundaries rather than duplicating a production solver in each language.

Alternatives considered: a Python-only numerical UI (simpler but less explicit native boundary), a hosted database/app (unneeded privacy/maintenance), arbitrary plugins/plant interfaces (outside scope), and a heavy webview installer (larger trust/runtime surface). A fixed local web app plus portable platform bundle best fits offline reproducibility and reviewability. Browser-only static hosting cannot run the C++/Python worker; GitHub Pages is not a substitute server.

The native interface is seven fixed arguments; no shell, uploaded source, dynamic compilation, user-selected executable or network address. Worker failure is a controlled server error, never a plausible zero result. Evidence validation rejects malformed grids, nonfinite numbers, negative thermal states, mismatched ledgers and excessive residuals. This is defense in depth around a trusted packaged worker, not an untrusted-code sandbox.

HTTP is GET-only, bound to IPv4 loopback, with exact Host/same-origin checks and no CORS. Only built index/hash-named asset files are exposed. The client displays text with textContent and builds SVG from numeric coordinates. Optional settings are finite and nonpersonal. A request generation counter plus abort controller prevents stale responses replacing the applied experiment. Applied configuration owns exports until the next successful run.

Trade-offs: portable bundles are unsigned; a console owns lifetime; no background daemon, public service, authentication, native mobile installer or persisted browser report store. CPU work runs in a subprocess with a timeout and finite inputs. A 32-entry serialized LRU is bounded, but concurrent local requests can duplicate cold work. The HTTP server is not a production multiuser server or a denial-of-service boundary against a local malicious process.

Rollback: stop the app and use a previous reviewed release in a separate folder. No migrations operate on user data automatically. Optional history databases are CLI-only and should be backed up before moving versions. Numeric schema changes require a new model/schema version and corresponding reference tests.
