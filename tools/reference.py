"""Independent small RK4 reference by Jason Stys.

Function: rk4 and stage helpers. Variables: normalized state, slopes, step and optional derating.
Test/evidence only, never the production solver. Exact lines: docs/CODE_INDEX.md.
"""


def rk4(duration=60, step=0.01, feedback=0.0):
    """Independent fourth-order ODE reference for the constant-source analogy (no native integrator reuse)."""
    state = (0.0, 0.0, 0.0)

    def derivative(value):
        """Dimensionless source/hot/cool differential equations from the documented thermal analogy."""
        source, hot, cool = value
        return (
            (1 / (1 + feedback * hot) - source) / 8,
            (source - 1.2 * (hot - cool)) / 6,
            (1.2 * (hot - cool) - 0.8 * cool) / 12,
        )

    def offset(value, slope, multiplier):
        """Form a reference RK stage without any C++ state or energy-ledger implementation."""
        return tuple(x + multiplier * step * dx for x, dx in zip(value, slope, strict=True))

    for _ in range(round(duration / step)):
        a = derivative(state)
        b = derivative(offset(state, a, 0.5))
        c = derivative(offset(state, b, 0.5))
        d = derivative(offset(state, c, 1))
        state = tuple(
            x + step * (da + 2 * db + 2 * dc + dd) / 6
            for x, da, db, dc, dd in zip(state, a, b, c, d, strict=True)
        )
    return state
