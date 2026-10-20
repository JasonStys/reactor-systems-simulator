# Dependencies and research

Project source: MIT, copyright Jason Stys. Runtime: C++ standard library plus CPython standard library; no remote services or third-party JavaScript runtime libraries. Portable bundles contain CPython/PyInstaller runtime notices in their bundled files; PyInstaller's GPL license has a distribution exception for generated applications. Windows builds statically link the MSVC runtime; users do not need a separately installed compiler.

Build/test-only packages are resolved in `requirements-dev.lock` (pytest, Hypothesis, coverage, Ruff, mypy, pip-audit, CMake, gcovr, PyInstaller and transitive tools) and `package-lock.json` (TypeScript, Vite, Vitest, Playwright, axe-core and Prettier). They are not web CDN dependencies. Bundled third-party licenses must remain with their runtime files. Audit results refer to the checked lock graph at validation time, not a permanent security warranty.

Research consulted 2026-10-20:

- [NRC student energy overview](https://www.nrc.gov/education-regulatory-research/the-student-corner/unit-3-nuclear-reactorsenergy-generation): conceptual educational context only, no nuclear engineering data, calibration or endorsement. Automated full-page fetch was blocked; accessible search summaries were used only for broad context.
- [SUNDIALS ODE mathematical considerations](https://sundials.readthedocs.io/en/latest/cvode/Mathematics_link.html): general integration/error concepts; this application implements its own small first-order thermal solve, not CVODE.
- [CMake Visual Studio 18 2026 generator](https://cmake.org/cmake/help/latest/generator/Visual%20Studio%2018%202026.html): official stable-toolchain selection.
- [Clang AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html): native memory-instrumentation workflow.

All model coefficients and scenarios are invented. No claim of empirical validation, regulatory compliance or physical reactor fidelity is made.
