/* Fictional thermal-network contracts by Jason Stys; NOT reactor physics or plant controls.
 * Types/functions: Config, Sample, Report, validate, forcing, simulate.
 * Variables: normalized capacities, conductances, lag and conversion proxy; docs/CODE_INDEX.md has exact lines.
 */
#pragma once
#include <string>
#include <utility>
#include <vector>

namespace reactor {
// Dimensionless teaching coefficients: no material, fuel, geometry or plant calibration.
inline constexpr double hot_capacity = 6.0;
inline constexpr double cool_capacity = 12.0;
inline constexpr double transfer = 1.2;
inline constexpr double rejection = 0.8;
inline constexpr double source_lag = 8.0;
inline constexpr double conversion_proxy = 0.3;

/** A bounded synthetic experiment; initial values are normalized test-only state. */
struct Config {
    std::string scenario = "baseline";
    int duration = 600;
    double demand = 1.0;
    double cooling = 1.0;
    double inertia = 1.0;
    double feedback = 0.0;
    double step = 0.1;
    double initial_source = 0.0;
    double initial_hot = 0.0;
    double initial_cool = 0.0;
};

/** One integer model-time sample; energy ledger accounts for initial stored energy. */
struct Sample {
    double time;
    double source;
    double hot;
    double cool;
    double useful;
    double input_energy;
    double rejected_energy;
    double stored_change;
    double balance_error;
};

/** Complete normalized trajectory and maximum numerical conservation residual. */
struct Report {
    std::vector<Sample> samples;
    double max_balance_error = 0.0;
};

/** Reject invalid metadata, nonfinite values, unbounded workloads and unsupported step grids. */
void validate(const Config& config);
/** Return right-continuous synthetic source demand and cooling multiplier at the given time. */
std::pair<double, double> forcing(const Config& config, double time);
/** Integrate exact frozen-target source energy and conservative implicit two-node heat exchange. */
Report simulate(const Config& config);
} // namespace reactor
