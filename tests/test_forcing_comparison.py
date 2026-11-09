"""Independent dimensionless matched-forcing comparisons by Jason Stys.

Functions: series and test_*; variables: hand-written signed differences and constant-forcing controls.
No reactor physics or physical accuracy is inferred. Exact lines: docs/CODE_INDEX.md.
"""

from simulator.comparison import forcing_comparison
from simulator.engine import Settings, build_run


def series(values: list[float]) -> dict:
    """Use equal fictitious values for four display states on an integer model-time grid."""
    return {
        "samples": [
            {"time": tick, "source": value, "hot": value, "cool": value, "useful": value}
            for tick, value in enumerate(values)
        ]
    }


def test_hand_derived_signed_peak_and_first_difference():
    """Differences0,+2,-3,0 have first1, signed peak-3 at2 and zero terminal deviation."""
    rows = forcing_comparison(series([0, 2, -3, 0]), series([0, 0, 0, 0]))
    assert len(rows) == 4
    for row in rows:
        assert row["peak_absolute_difference"] == 3 and row["peak_signed_difference"] == -3
        assert row["peak_sample_time"] == 2 and row["first_difference_time"] == 1
        assert row["end_difference"] == 0


def test_matched_constant_case_changes_only_forcing():
    """Nondefault coefficients still have zero matched deviation in a constant-source lesson."""
    baseline = build_run(Settings(demand=1.25, cooling=0.5, inertia=1.25, feedback=0.15))
    assert all(
        row["peak_absolute_difference"] == 0 and row["first_difference_time"] is None
        for row in baseline["forcing_comparison"]
    )
    assert baseline["experiment"]["samples"] != baseline["reference"]["samples"]
    for scenario, earliest in (("demand-step", 120), ("cooling-dip", 180), ("source-off", 240)):
        run = build_run(Settings(scenario=scenario))
        assert all(
            row["first_difference_time"] is None or row["first_difference_time"] >= earliest
            for row in run["forcing_comparison"]
        )
        assert run["matched_reference"]["max_balance_error"] < 1e-7
