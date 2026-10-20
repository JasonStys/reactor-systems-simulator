/* Native numerical and edge-case regression checks by Jason Stys.
 * Functions: require, close, contracts, main. Variables: analytic source/equilibrium fixtures,
 * refinement errors and normalized energy ledgers. Exact lines: docs/CODE_INDEX.md.
 */
#include "model.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

namespace {
/** Assertions remain active in Release builds; never rely on NDEBUG-sensitive assert(). */
void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
/** Compare absolute numerical error, not a fictional physical accuracy bound. */
void close(double actual, double expected, double tolerance, const std::string& message) {
    require(std::abs(actual - expected) <= tolerance, message);
}
/** Exercise every scenario, reference solutions, conservation, refinement and rejected inputs. */
void contracts() {
    for (const auto& scenario : {"baseline", "demand-step", "cooling-dip", "source-off"}) {
        for (double cooling : {0.5, 1.0, 1.5}) {
            reactor::Config config;
            config.scenario = scenario;
            config.cooling = cooling;
            const auto report = reactor::simulate(config);
            require(report.samples.size() == 601, "Exact integer output grid");
            require(report.max_balance_error < 1e-8, "Energy conservation");
            for (const auto& sample : report.samples) {
                require(std::isfinite(sample.hot) && sample.hot >= 0 && sample.cool >= 0, "Finite positive thermal states");
                require(sample.input_energy >= 0 && sample.rejected_energy >= 0, "Nonnegative energy totals");
                close(sample.input_energy, sample.rejected_energy + sample.stored_change, 1e-8, "Ledger identity");
            }
        }
    }
    reactor::Config config;
    const auto baseline = reactor::simulate(config);
    for (const auto& sample : baseline.samples)
        close(sample.source, 1.0 - std::exp(-sample.time / reactor::source_lag), 2e-13, "Analytic source lag");

    config.initial_source = 1.0;
    config.initial_cool = 1.0 / reactor::rejection;
    config.initial_hot = config.initial_cool + 1.0 / reactor::transfer;
    const auto equilibrium = reactor::simulate(config);
    close(equilibrium.samples.back().hot, config.initial_hot, 1e-11, "Analytic hot equilibrium");
    close(equilibrium.samples.back().cool, config.initial_cool, 1e-11, "Analytic cool equilibrium");

    config = reactor::Config{};
    config.duration = 20;
    config.step = 0.025;
    const double reference = reactor::simulate(config).samples.back().hot;
    config.step = 0.05;
    const double fine_error = std::abs(reactor::simulate(config).samples.back().hot - reference);
    config.step = 0.25;
    const double coarse_error = std::abs(reactor::simulate(config).samples.back().hot - reference);
    require(fine_error < coarse_error && coarse_error < 0.02, "Time refinement convergence");

    config = reactor::Config{};
    config.feedback = 0.15;
    require(reactor::simulate(config).samples.back().hot < baseline.samples.back().hot, "Generic derating response");
    config.feedback = 0;
    config.scenario = "cooling-dip";
    require(reactor::simulate(config).samples[240].hot > baseline.samples[240].hot, "Cooling perturbation response");
    const auto before = reactor::forcing(config, 179.999);
    const auto at = reactor::forcing(config, 180.0);
    const auto restored = reactor::forcing(config, 300.0);
    close(before.second, restored.second, 0, "Exact restoration boundary");
    require(at.second < before.second, "Event applies at boundary");
    config.scenario = "source-off";
    const auto off = reactor::simulate(config);
    require(off.samples.back().source < 1e-12 && off.samples.back().hot < off.samples[240].hot, "Fictional source shutoff");

    for (int error = 0; error < 15; ++error) {
        config = reactor::Config{};
        switch (error) {
            case 0: config.demand = -1; break;
            case 1: config.demand = 3; break;
            case 2: config.cooling = 0; break;
            case 3: config.cooling = 3; break;
            case 4: config.inertia = 0; break;
            case 5: config.inertia = 3; break;
            case 6: config.feedback = -1; break;
            case 7: config.feedback = 1; break;
            case 8: config.duration = 0; break;
            case 9: config.duration = 901; break;
            case 10: config.step = 0.03; break;
            case 11: config.scenario = "unknown"; break;
            case 12: config.demand = std::numeric_limits<double>::quiet_NaN(); break;
            case 13: config.initial_hot = -1; break;
            default: config.initial_cool = std::numeric_limits<double>::infinity(); break;
        }
        bool rejected = false;
        try { reactor::validate(config); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected, "Invalid configuration rejected");
    }
}
} // namespace

/** Return nonzero for any failed numerical contract, including in optimized builds. */
int main() {
    try {
        contracts();
        std::cout << "Native reference, energy, event, positivity, refinement and invalid-input contracts passed\n";
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
