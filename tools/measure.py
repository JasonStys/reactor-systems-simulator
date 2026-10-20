"""Regenerate local numerical/performance evidence by Jason Stys.

Functions: main. Variables: duration, reference, errors, timings and residuals.
Run as python -m tools.measure. Generated reports are observations, not physical validation.
Exact lines: docs/CODE_INDEX.md. No private file paths or machine identifiers are exported.
"""

import json
import platform
import statistics
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from simulator.engine import Settings, binary_path, build_run, compute, decode_worker
from tools.reference import rk4


def main() -> None:
    """Measure independent-reference errors and cold-worker/warm-evidence wall time on this host."""
    rows = []
    for duration in (20, 60, 300):
        for feedback in (0.0, 0.15):
            reference = rk4(duration, feedback=feedback)
            errors = {}
            for step in (0.1, 0.05):
                process = subprocess.run(
                    [
                        str(binary_path()),
                        "baseline",
                        str(duration),
                        "1",
                        "1",
                        "1",
                        str(feedback),
                        str(step),
                    ],
                    check=True,
                    capture_output=True,
                    timeout=10,
                )
                final = decode_worker(process.stdout, duration)["samples"][-1]
                errors[str(step)] = {
                    key: abs(final[key] - value)
                    for key, value in zip(("source", "hot", "cool"), reference, strict=True)
                }
            rows.append({"time": duration, "derating": feedback, "absolute_errors": errors})
    cold, warm = [], []
    for _ in range(9):
        compute.cache_clear()
        start = perf_counter()
        run = build_run(Settings(scenario="cooling-dip"))
        cold.append((perf_counter() - start) * 1000)
        start = perf_counter()
        build_run(Settings(scenario="cooling-dip"))
        warm.append((perf_counter() - start) * 1000)
    report = {
        "author": "Jason Stys",
        "measured_utc": datetime.now(UTC).isoformat(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "model": "fictional-thermal-v1",
        "units": "dimensionless",
        "physical_validation": False,
        "reference": "independent Python RK4 h=0.01, constant source, optional generic derating",
        "comparisons": rows,
        "max_sampled_balance_residual": run["experiment"]["max_balance_error"],
        "worker_sha256": run["provenance"]["worker_sha256"],
        "benchmark": {
            "repeats": 9,
            "horizon": 600,
            "median_cold_evidence_ms": statistics.median(cold),
            "median_warm_evidence_ms": statistics.median(warm),
            "scope": "two subprocesses for cold experiment/reference; warm still decodes and hashes evidence",
            "caveat": "single host observation, includes process startup, not a performance guarantee",
        },
    }
    output = Path(__file__).resolve().parents[1] / "docs/reports/numerical-validation.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
