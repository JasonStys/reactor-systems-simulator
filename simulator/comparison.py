"""Matched-forcing educational thermal comparison by Jason Stys.

Function: forcing_comparison. Variables: normalized sample differences and explicit peak times.
No nuclear physics, physical units or reactor operating guidance. Lines: docs/CODE_INDEX.md.
"""

from typing import Any


def forcing_comparison(experiment: dict[str, Any], matched: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare each sampled dimensionless state with a constant-forcing case at identical settings.

    Peaks are sampled extrema, not continuous extrema. First difference uses 1e-9 solely as a
    numerical display tolerance, not a safety threshold. The default-reference series is separate.
    """
    rows = []
    for field in ("source", "hot", "cool", "useful"):
        differences = [
            (a["time"], a[field] - b[field])
            for a, b in zip(experiment["samples"], matched["samples"], strict=True)
        ]
        time, peak = max(differences, key=lambda item: abs(item[1]))
        rows.append(
            {
                "field": field,
                "peak_absolute_difference": abs(peak),
                "peak_signed_difference": peak,
                "peak_sample_time": time,
                "end_difference": differences[-1][1],
                "first_difference_time": next(
                    (t for t, value in differences if abs(value) > 1e-9), None
                ),
            }
        )
    return rows
