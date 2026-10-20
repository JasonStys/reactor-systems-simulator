"""Independent numerical and worker-boundary validation by Jason Stys.

Functions: native, rk4, test_* contracts. Variables: analytic/reference solutions,
finite normalized inputs, errors, forged worker records. Exact lines: docs/CODE_INDEX.md.
"""

import json
import math
import subprocess
from dataclasses import replace

import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st

from simulator.engine import (
    FIELDS,
    SCENARIOS,
    Settings,
    binary_path,
    build_run,
    catalog,
    compute,
    decode_worker,
    run_id,
)
from tools.reference import rk4


def native(step="0.1", duration=300, **options):
    """Execute the actual compiled CLI with an explicit reviewed test configuration."""
    values = {"scenario": "baseline", "demand": 1, "cooling": 1, "inertia": 1, "feedback": 0}
    values.update(options)
    result = subprocess.run(
        [
            str(binary_path()),
            values["scenario"],
            str(duration),
            *(str(values[key]) for key in ("demand", "cooling", "inertia", "feedback")),
            step,
        ],
        capture_output=True,
        check=True,
        timeout=10,
    )
    return decode_worker(result.stdout, duration)


@pytest.mark.parametrize("duration", [20, 60, 300])
@pytest.mark.parametrize("feedback", [0.0, 0.15])
def test_independent_reference_and_convergence(duration, feedback):
    """Compare with independent RK4; refinement improves error rather than claiming physical accuracy."""
    expected = rk4(duration, feedback=feedback)
    coarse = native("0.1", duration, feedback=feedback)["samples"][-1]
    fine = native("0.05", duration, feedback=feedback)["samples"][-1]
    errors = [
        abs(coarse[key] - value)
        for key, value in zip(("source", "hot", "cool"), expected, strict=True)
    ]
    fine_error = abs(fine["hot"] - expected[1]) + abs(fine["cool"] - expected[2])
    assert max(errors) < 0.003
    assert fine_error < (errors[1] + errors[2]) * 0.6


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_scenarios(scenario):
    """All scenarios preserve finite positive states, exact grid and the discrete energy balance."""
    run = build_run(Settings(scenario=scenario))
    series = run["experiment"]["samples"]
    assert len(series) == 601
    assert series[0]["hot"] == 0
    assert run["experiment"]["max_balance_error"] < 1e-8
    assert all(sample["input_energy"] >= sample["stored_change"] - 1e-9 for sample in series)
    assert run["provenance"]["units"] == "dimensionless"
    assert "not" in run["provenance"]["limitation"].lower()
    assert run["id"] == run_id(run)


def test_analytic_and_events():
    """Check analytic source lag, exact boundary continuity, instantaneous cooling and source-off behavior."""
    baseline = build_run()["experiment"]["samples"]
    for sample in baseline:
        assert sample["source"] == pytest.approx(1 - math.exp(-sample["time"] / 8), abs=2e-13)
    step = build_run(Settings(scenario="demand-step"))["experiment"]["samples"]
    assert step[120]["source"] == baseline[120]["source"]
    assert step[121]["source"] > baseline[121]["source"]
    dip = build_run(Settings(scenario="cooling-dip"))["experiment"]["samples"]
    assert dip[180]["hot"] == baseline[180]["hot"]
    assert dip[180]["useful"] == pytest.approx(baseline[180]["useful"] * 0.35)
    assert dip[300]["useful"] == pytest.approx(0.3 * 0.8 * dip[300]["cool"])
    off = build_run(Settings(scenario="source-off"))["experiment"]["samples"]
    assert off[600]["source"] < 1e-12
    assert off[600]["hot"] < off[240]["hot"]


@hypothesis_settings(max_examples=20, deadline=None)
@given(
    scenario=st.sampled_from(tuple(SCENARIOS)),
    demand=st.sampled_from([0.75, 1.0, 1.25]),
    cooling=st.sampled_from([0.5, 1.0, 1.5]),
    inertia=st.sampled_from([0.75, 1.0, 1.25]),
    feedback=st.sampled_from([0.0, 0.15]),
)
def test_reviewed_configuration_properties(scenario, demand, cooling, inertia, feedback):
    """Property checks span reviewed combinations without accepting arbitrary plant parameters."""
    run = build_run(Settings(scenario, 300, demand, cooling, inertia, feedback))
    assert run["experiment"]["max_balance_error"] < 1e-8
    assert run["reference"]["samples"] == build_run(Settings(duration=300))["reference"]["samples"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("scenario", "../x"),
        ("duration", 0),
        ("duration", 300.0),
        ("demand", True),
        ("demand", float("nan")),
        ("cooling", float("inf")),
        ("inertia", -1),
        ("feedback", "0.15"),
    ],
)
def test_settings_rejection(field, value):
    """Nonfinite, boolean, wrong-type and unreviewed inputs fail before starting a process."""
    with pytest.raises(ValueError):
        replace(Settings(), **{field: value})


@pytest.mark.parametrize("token", ["nan", "inf", "1e999", "1x", "-1", "3", "1;whoami", ""])
def test_native_untrusted_number(token):
    """The native command parser independently rejects malformed/nonfinite/out-of-range values."""
    result = subprocess.run(
        [str(binary_path()), "baseline", "300", token, "1", "1", "0", "0.1"],
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 2 and not result.stdout


def test_native_argument_count():
    """Missing arguments fail with a nonzero status rather than reading nonexistent argv slots."""
    assert subprocess.run([str(binary_path())], capture_output=True, timeout=10).returncode == 2


@pytest.mark.parametrize("token", ["300.0", "nan", "901", "-1", "2147483648", "1x"])
def test_native_invalid_duration(token):
    """Native integer parsing rejects fractional, overflowing, partial and out-of-range horizons."""
    result = subprocess.run(
        [str(binary_path()), "baseline", token, "1", "1", "1", "0", "0.1"],
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 2 and not result.stdout


def test_cache_detachment_and_catalog():
    """Caller mutations cannot poison cached scientific evidence or later catalog responses."""
    run = build_run()
    run["experiment"]["samples"][0]["hot"] = 999
    assert build_run()["experiment"]["samples"][0]["hot"] == 0
    choices = catalog()
    choices["defaults"]["demand"] = 999
    assert catalog()["defaults"]["demand"] == 1


@pytest.mark.parametrize(
    "failure",
    [
        OSError("missing"),
        subprocess.TimeoutExpired("worker", 10),
        subprocess.CalledProcessError(2, "worker"),
    ],
)
def test_worker_failure(monkeypatch, failure):
    """Worker startup, timeout and nonzero exit are controlled failures without leaking process text."""
    compute.cache_clear()

    def fail(*args, **kwargs):
        """Replace process execution with the selected boundary failure."""
        raise failure

    monkeypatch.setattr(subprocess, "run", fail)
    with pytest.raises(RuntimeError, match="unavailable"):
        compute(Settings())


@pytest.mark.parametrize(
    "fault", ["count", "time", "nan", "ledger", "negative", "maximum", "type", "keys"]
)
def test_corrupt_worker_evidence(fault):
    """Scientific/schema corruption is detected before any result is displayed or exported."""
    report = native(duration=1)
    sample = report["samples"][-1]
    if fault == "count":
        report["samples"] = []
    elif fault == "time":
        sample["time"] = 9
    elif fault == "nan":
        sample["hot"] = float("nan")
    elif fault == "ledger":
        sample["balance_error"] = 1
    elif fault == "negative":
        sample["cool"] = -1
    elif fault == "maximum":
        report["max_balance_error"] = 1
    elif fault == "type":
        report["max_balance_error"] = "0"
    else:
        sample.pop(FIELDS[0])
    with pytest.raises(RuntimeError, match="evidence"):
        decode_worker(json.dumps(report).encode(), 1)


@pytest.mark.parametrize(
    "raw", [b"bad json", b"[]", b"x" * 2_000_001], ids=["invalid-json", "wrong-shape", "oversized"]
)
def test_invalid_worker_payload(raw):
    """Malformed or oversized worker responses cannot become plausible successful evidence."""
    with pytest.raises(RuntimeError):
        decode_worker(raw, 1)


def test_frozen_path(monkeypatch, tmp_path):
    """Portable bundles resolve their own packaged executable, never PATH or a user-supplied command."""
    monkeypatch.setattr("sys._MEIPASS", str(tmp_path), raising=False)
    assert binary_path().parent == tmp_path / "native"
