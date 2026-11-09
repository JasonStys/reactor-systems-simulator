# Compare a matched forcing lesson

The matched reference is a constant-source scenario with **the same demand, cooling factor, inertia, generic derating and duration** as the selected experiment. It isolates the declared scenario forcing from those settings. The original default-reference curves remain unchanged and separately labeled; they are not this matched control when settings differ from defaults.

For source, hot/cool state and useful-output proxy, the panel shows the largest sampled absolute and signed deviation, its model time, terminal deviation and first difference larger than a numerical1e-9 tolerance. Difference means experiment minus matched constant forcing. These are sampled comparisons, not continuous extrema, physical energy differences or safety thresholds. The complete matched samples and summary are retained in JSON/HTML and immutable CLI history.

All quantities, time and coefficients remain invented and dimensionless. This feature does not add reactor physics, fuel/rod selection, kinetics, criticality, radiation, decay heat, real telemetry, operating recommendations or control. Source-off is not a nuclear shutdown model. The unchanged C++ conservative two-node analogy and its numerical energy/convergence tests remain the only modeled dynamics.
