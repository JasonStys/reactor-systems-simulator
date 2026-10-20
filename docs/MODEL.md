# Model, assumptions and limits

This is a generic dimensionless thermal analogy, not a nuclear-reactor simulator in the engineering sense. No coefficient comes from a plant, fuel, material property, nuclear database or operating procedure. It teaches numerical discipline, energy bookkeeping and delayed responses. Do not interpret plotted values as degrees, watts, seconds, radiation or safe operating conditions.

## Fictional equations

Let `S` be the relaxing generic source rate, `H` and `C` be offsets of two thermal nodes from a fixed zero environment. Model time is `t`. With demand `D`, cooling factor `f`, inertia factor `m`, and optional generic derating `g`:

```text
Ch = 6 m; Cc = 12 m; K = 1.2; U = 0.8 f; lag = 8
target = D / (1 + g H)
dS/dt = (target - S) / lag
Ch dH/dt = S - K (H - C)
Cc dC/dt = K (H - C) - U C
useful proxy = 0.3 U C
```

The 30% proxy is an arbitrary partition of **already rejected** energy, not an additional sink or actual turbine efficiency. The other 70% is a remainder. These equations also describe a generic heater/cooling-loop analogy; no nuclear interpretation is supported.

All UI/HTTP experiments start at `S=H=C=0`. Native tests additionally exercise finite initial states and analytic equilibrium. Public demand choices are 0.75, 1, 1.25; cooling 0.5, 1, 1.5; inertia 0.75, 1, 1.25; derating 0 or 0.15; horizons 300 or 600.

## Integration and event convention

The public internal step is 0.1; output occurs at integer model times. The source target is frozen using the hot-node state at each substep start. Source relaxation and its deposited energy integral are solved analytically over that substep. A two-by-two implicit Euler solve updates both thermal nodes with equal/opposite transfer. Heat rejection is accumulated with the same implicit cool-node state.

Scenarios are right-continuous: a demand factor of 1.2 starts at 120; a cooling factor of 0.35 applies on `[180,300)`; source demand becomes zero at 240. States at an event time are continuous and represent completed preceding intervals. The instantaneous useful proxy uses the new right-hand cooling factor. The plotted state response begins over the following interval.

The ledger is `input energy − rejected energy − (stored energy − initial stored energy)`. `max_balance_error` is the largest absolute residual over the integer output grid, not over every internal substep. Small residuals check discrete consistency, **not physical fidelity**. Backward Euler introduces first-order numerical damping. Frozen-target derating is a first-order split; only the constant-target source step is exact. Independent RK4 comparison and step refinement test discretization error in the defined analogy. SUNDIALS' [ODE-method documentation](https://sundials.readthedocs.io/en/latest/cvode/Mathematics_link.html) informed general implicit-method/error terminology; this project does not use SUNDIALS or claim its solver capabilities.

## Analytic verification and cost

With baseline demand and zero initial source, `S(t)=1−exp(−t/8)`. At constant unit source equilibrium, `C=1/0.8` and `H=C+1/1.2`. Native tests check both independently of the transient loop.

For horizon `T`, step `h`, and output count `N=T+1`, runtime is `O(T/h + N)` and retained worker data is `O(N)`. The native worker has no external dependencies. Python's LRU holds at most 32 serialized runs; responses are decoded into detached objects. Each response includes a fixed baseline reference. Cache equality does not imply bitwise reproducibility across compilers/platforms: run IDs include actual results and worker-binary SHA-256, so different builds can have different IDs. Scientific comparisons use tolerances.

## Deliberately absent

Fuel type/loading, rod counts/positions, geometry, neutron transport, kinetics, reactivity, criticality, nuclear reactions, fission products, decay heat, radiation/dose, coolant materials/phase changes, pressure, realistic equipment behavior, plant interlocks, real telemetry and control. Source-off retains only fictional source lag and stored thermal energy; it must never be described as nuclear shutdown or decay-heat prediction.

The NRC's [student energy-generation overview](https://www.nrc.gov/education-regulatory-research/the-student-corner/unit-3-nuclear-reactorsenergy-generation) provides broad educational context only, not a calibration dataset or endorsement. This repo cannot answer questions about real-plant power, radiation or safety. It is not certified for engineering, training operators or monitoring facilities.
