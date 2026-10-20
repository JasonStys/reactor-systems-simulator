/* Conservative educational thermal analogy by Jason Stys.
 * Functions: validate, forcing, simulate. Variables: fictional coefficients in model.hpp;
 * local matrix/state/energy quantities are indexed in docs/CODE_INDEX.md. No nuclear kinetics.
 */
#include "model.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <stdexcept>

namespace reactor {
/** Validate finite normalized bounds and exact supported output/step grids. */
void validate(const Config& config) {
    const std::array<std::string, 4> scenarios{"baseline", "demand-step", "cooling-dip", "source-off"};
    const std::array<double, 5> steps{0.025, 0.05, 0.1, 0.25, 0.5};
    const std::array<double, 9> values{config.demand, config.cooling, config.inertia,
        config.feedback, config.step, config.initial_source, config.initial_hot,
        config.initial_cool, static_cast<double>(config.duration)};
    if (std::any_of(values.begin(), values.end(), [](double value) { return !std::isfinite(value); }) ||
        std::find(scenarios.begin(), scenarios.end(), config.scenario) == scenarios.end() ||
        std::find(steps.begin(), steps.end(), config.step) == steps.end() ||
        config.duration < 1 || config.duration > 900 ||
        config.demand < 0.0 || config.demand > 2.0 ||
        config.cooling < 0.25 || config.cooling > 2.0 ||
        config.inertia < 0.25 || config.inertia > 2.0 ||
        config.feedback < 0.0 || config.feedback > 0.3 ||
        config.initial_source < 0.0 || config.initial_source > 2.0 ||
        config.initial_hot < 0.0 || config.initial_hot > 20.0 ||
        config.initial_cool < 0.0 || config.initial_cool > 20.0) {
        throw std::invalid_argument("Invalid fictional model configuration");
    }
}

/** Apply documented synthetic right-continuous events at their exact model times. */
std::pair<double, double> forcing(const Config& config, double time) {
    double demand = config.demand;
    double cooling = config.cooling;
    if (config.scenario == "demand-step" && time >= 120.0) demand *= 1.2;
    if (config.scenario == "cooling-dip" && time >= 180.0 && time < 300.0) cooling *= 0.35;
    if (config.scenario == "source-off" && time >= 240.0) demand = 0.0;
    return {demand, cooling};
}

/** Integrate the fictional energy network, retaining integer-time samples and its energy ledger. */
Report simulate(const Config& config) {
    validate(config);
    const double ch = hot_capacity * config.inertia;
    const double cc = cool_capacity * config.inertia;
    const double initial_energy = ch * config.initial_hot + cc * config.initial_cool;
    const int subdivisions = static_cast<int>(std::lround(1.0 / config.step));
    const double h = 1.0 / static_cast<double>(subdivisions);
    double source = config.initial_source;
    double hot = config.initial_hot;
    double cool = config.initial_cool;
    double input_energy = 0.0;
    double rejected_energy = 0.0;
    Report report;
    report.samples.reserve(static_cast<std::size_t>(config.duration) + 1);
    report.samples.push_back({0.0, source, hot, cool,
        conversion_proxy * rejection * config.cooling * cool, 0.0, 0.0, 0.0, 0.0});
    for (int second = 0; second < config.duration; ++second) {
        double removal = rejection * config.cooling;
        for (int sub = 0; sub < subdivisions; ++sub) {
            const double time = static_cast<double>(second) + static_cast<double>(sub) * h;
            const auto [command, cooling] = forcing(config, time);
            removal = rejection * cooling;
            // Generic temperature derating, NOT neutron reactivity feedback or decay heat.
            const double target = command / (1.0 + config.feedback * hot);
            const double fraction = -std::expm1(-h / source_lag);
            const double deposited = target * h + (source - target) * source_lag * fraction;
            source += (target - source) * fraction;

            // Backward Euler: equal/opposite transfer preserves the two-node energy ledger.
            const double a = ch + h * transfer;
            const double b = -h * transfer;
            const double d = cc + h * (transfer + removal);
            const double determinant = a * d - b * b;
            const double rhs_hot = ch * hot + deposited;
            const double rhs_cool = cc * cool;
            hot = (rhs_hot * d - b * rhs_cool) / determinant;
            cool = (a * rhs_cool - b * rhs_hot) / determinant;
            input_energy += deposited;
            rejected_energy += h * removal * cool;
        }
        const double stored_change = ch * hot + cc * cool - initial_energy;
        const double residual = input_energy - rejected_energy - stored_change;
        report.max_balance_error = std::max(report.max_balance_error, std::abs(residual));
        // State is continuous at events; instantaneous rejection uses the new right-hand forcing.
        const double instantaneous_removal = rejection * forcing(config, static_cast<double>(second + 1)).second;
        report.samples.push_back({static_cast<double>(second + 1), source, hot, cool,
            conversion_proxy * instantaneous_removal * cool, input_energy, rejected_energy, stored_change, residual});
    }
    return report;
}
} // namespace reactor
