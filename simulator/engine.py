"""Bounded C++ thermal-worker adapter and reproducible evidence by Jason Stys.

Classes/functions: Settings, catalog, binary_path, compute, build_run, run_id.
Variables: reviewed choices, model parameters, worker samples and provenance.
All symbol/variable locations: docs/CODE_INDEX.md. No nuclear physics or hardware interfaces.
"""

import hashlib
import json
import math
import subprocess
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from simulator import VERSION

SCENARIOS = {
    "baseline": "Constant source",
    "demand-step": "Source demand step at 120",
    "cooling-dip": "Cooling dip from 180 to 300",
    "source-off": "Source input off at 240",
}
CHOICES: dict[str, tuple[int | float, ...]] = {
    "duration": (300, 600),
    "demand": (0.75, 1.0, 1.25),
    "cooling": (0.5, 1.0, 1.5),
    "inertia": (0.75, 1.0, 1.25),
    "feedback": (0.0, 0.15),
}
FIELDS = (
    "time",
    "source",
    "hot",
    "cool",
    "useful",
    "input_energy",
    "rejected_energy",
    "stored_change",
    "balance_error",
)
LIMITATION = (
    "Fictional dimensionless thermal analogy, not reactor physics. No fuel, neutron, "
    "criticality, radiation, dose, decay-heat, real-plant safety or hardware model. "
    "Source-off is not nuclear shutdown. Not for design, control, monitoring or safety decisions."
)


@dataclass(frozen=True)
class Settings:
    """Reviewed public experiment choices; values are normalized, never physical plant inputs."""

    scenario: str = "baseline"
    duration: int = 600
    demand: float = 1.0
    cooling: float = 1.0
    inertia: float = 1.0
    feedback: float = 0.0

    def __post_init__(self) -> None:
        """Reject booleans, nonfinite values and values outside the finite public catalog."""
        if self.scenario not in SCENARIOS:
            raise ValueError("Unknown experiment")
        for key, choices in CHOICES.items():
            value = getattr(self, key)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or value not in choices
            ):
                raise ValueError("Unsupported experiment parameter")
        if not isinstance(self.duration, int):
            raise ValueError("Duration must be an integer")


def catalog() -> dict[str, Any]:
    """Return detached finite choices and the model boundary for API/UI consumers."""
    return {
        "scenarios": [{"id": key, "label": label} for key, label in SCENARIOS.items()],
        "choices": dict(CHOICES),
        "defaults": asdict(Settings()),
        "limitation": LIMITATION,
    }


def binary_path() -> Path:
    """Select only the built-in owned worker; HTTP cannot choose a path or command."""
    name = "reactor_core.exe" if sys.platform == "win32" else "reactor_core"
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "native" / name
    root = Path(__file__).resolve().parents[1] / "native-build"
    return root / "Release" / name if sys.platform == "win32" else root / name


def decode_worker(raw: bytes, duration: int) -> dict[str, Any]:
    """Validate worker schema, exact sample grid, finite values and conservation before display."""
    if len(raw) > 2_000_000:
        raise RuntimeError("Worker response exceeds limit")
    try:
        report = json.loads(raw)
        samples = report["samples"]
        maximum = report["max_balance_error"]
        if set(report) != {"samples", "max_balance_error"} or len(samples) != duration + 1:
            raise ValueError("Invalid sample count")
        errors = []
        for index, sample in enumerate(samples):
            if set(sample) != set(FIELDS) or sample["time"] != index:
                raise ValueError("Invalid sample grid")
            if any(
                type(sample[key]) not in (int, float) or not math.isfinite(sample[key])
                for key in FIELDS
            ):
                raise ValueError("Nonfinite sample")
            ledger = sample["input_energy"] - sample["rejected_energy"] - sample["stored_change"]
            if abs(ledger - sample["balance_error"]) > 1e-9:
                raise ValueError("Invalid energy ledger")
            if any(sample[key] < -1e-12 for key in ("source", "hot", "cool", "useful")):
                raise ValueError("Negative state")
            errors.append(abs(sample["balance_error"]))
        if type(maximum) not in (int, float) or not math.isfinite(maximum):
            raise ValueError("Invalid residual")
        if maximum < max(errors) or maximum > 1e-7:
            raise ValueError("Conservation check failed")
        return dict(report)
    except (ValueError, KeyError, TypeError, OverflowError) as error:
        raise RuntimeError("Invalid worker evidence") from error


@lru_cache(maxsize=32)
def compute(settings: Settings) -> str:
    """Run a bounded fixed worker, then cache serialized immutable evidence (32 runs maximum)."""
    binary = binary_path()
    try:
        result = subprocess.run(
            [
                str(binary),
                settings.scenario,
                str(settings.duration),
                str(settings.demand),
                str(settings.cooling),
                str(settings.inertia),
                str(settings.feedback),
                "0.1",
            ],
            capture_output=True,
            check=True,
            timeout=10,
        )
        report = decode_worker(result.stdout, settings.duration)
        with binary.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
    except (OSError, subprocess.SubprocessError) as error:
        raise RuntimeError(
            "Native worker unavailable; build the reviewed C++ source first"
        ) from error
    report["worker_sha256"] = digest
    return json.dumps(report, allow_nan=False, separators=(",", ":"))


def run_id(run: dict[str, Any]) -> str:
    """Hash actual content except its own ID; no wall-clock time or personal information."""
    payload = {key: value for key, value in run.items() if key != "id"}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def build_run(settings: Settings | None = None) -> dict[str, Any]:
    """Assemble detached experiment/reference series, explicit assumptions and content identity."""
    settings = settings or Settings()
    experiment = json.loads(compute(settings))
    reference = json.loads(compute(Settings(duration=settings.duration)))
    run = {
        "schema": "reactor-thermal-evidence/1",
        "author": "Jason Stys",
        "scenario": settings.scenario,
        "settings": asdict(settings),
        "provenance": {
            "version": VERSION,
            "model": "fictional-thermal-v1",
            "units": "dimensionless",
            "time": "normalized model time (not physical seconds)",
            "step": 0.1,
            "method": "exact source relaxation + implicit-Euler two-node heat balance",
            "coefficients": {
                "hot_capacity": 6,
                "cool_capacity": 12,
                "transfer": 1.2,
                "rejection": 0.8,
                "source_lag": 8,
                "useful_fraction": 0.3,
            },
            "worker_sha256": experiment["worker_sha256"],
            "limitation": LIMITATION,
            "accuracy": "First-order thermal integration; see convergence evidence. Not calibrated.",
        },
        "experiment": experiment,
        "reference": reference,
        "events": {
            "baseline": [],
            "demand-step": [{"time": 120, "label": "Demand × 1.2"}],
            "cooling-dip": [
                {"time": 180, "label": "Cooling × 0.35"},
                {"time": 300, "label": "Cooling restored"},
            ],
            "source-off": [{"time": 240, "label": "Source input removed (not nuclear shutdown)"}],
        }[settings.scenario],
    }
    run["id"] = run_id(run)
    return run
