/* Bounded native JSON worker by Jason Stys.
 * Functions: number, integer, emit, main. Variables: parsed Config and immutable Report.
 * No file/network/shell interfaces. Argument and state lines: docs/CODE_INDEX.md.
 */
#include "model.hpp"
#include <charconv>
#include <exception>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string_view>

namespace {
/** Parse a full numeric token without locale, partial acceptance or exceptions from strtod. */
double number(std::string_view token) {
    double value = 0.0;
    const auto result = std::from_chars(token.data(), token.data() + token.size(), value);
    if (result.ec != std::errc{} || result.ptr != token.data() + token.size())
        throw std::invalid_argument("Invalid numeric token");
    return value;
}
/** Parse an integral duration; fractional or overflowing text is rejected. */
int integer(std::string_view token) {
    int value = 0;
    const auto result = std::from_chars(token.data(), token.data() + token.size(), value);
    if (result.ec != std::errc{} || result.ptr != token.data() + token.size())
        throw std::invalid_argument("Invalid duration");
    return value;
}
/** Serialize only fixed keys and validated finite numeric output; no request text is echoed. */
void emit(const reactor::Report& report) {
    std::cout << std::setprecision(17) << "{\"max_balance_error\":" << report.max_balance_error << ",\"samples\":[";
    bool first = true;
    for (const auto& sample : report.samples) {
        if (!first) std::cout << ',';
        first = false;
        std::cout << "{\"time\":" << sample.time << ",\"source\":" << sample.source
            << ",\"hot\":" << sample.hot << ",\"cool\":" << sample.cool
            << ",\"useful\":" << sample.useful << ",\"input_energy\":" << sample.input_energy
            << ",\"rejected_energy\":" << sample.rejected_energy
            << ",\"stored_change\":" << sample.stored_change
            << ",\"balance_error\":" << sample.balance_error << '}';
    }
    std::cout << "]}\n";
}
} // namespace

/** Run one reviewed worker invocation; invalid input returns 2 with a fixed safe error message. */
int main(int argc, char* argv[]) {
    try {
        if (argc != 8) throw std::invalid_argument("Expected seven model arguments");
        reactor::Config config;
        config.scenario = argv[1];
        config.duration = integer(argv[2]);
        config.demand = number(argv[3]);
        config.cooling = number(argv[4]);
        config.inertia = number(argv[5]);
        config.feedback = number(argv[6]);
        config.step = number(argv[7]);
        emit(reactor::simulate(config));
        return 0;
    } catch (const std::exception&) {
        std::cerr << "Invalid model arguments or unavailable numerical result\n";
        return 2;
    }
}
