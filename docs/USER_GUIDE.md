# User guide

Created by Jason Stys. This guide describes a fictional thermal analogy, not reactor operation.

1. Start the portable executable or `python -m simulator serve`. Open the exact printed loopback address if the browser does not open. Keep the console open.
2. Choose an experiment and bounded normalized factors. Select **Run experiment**. Editing a control alone does not change the applied curves or exports.
3. Scrub **Model time** or play at 30 model-time units per wall-clock second. These are not physical seconds. Playback only selects already computed samples; it does not run the solver in real time.
4. Compare solid hot/cool curves with the dashed fixed baseline. The baseline always has unit demand, cooling and inertia, no derating and the same horizon.
5. Inspect the selected-time table and energy ledger. Useful output is part of rejection, not a second sink. A tiny residual is numerical consistency, not proof of real-world accuracy or safety.
6. Download JSON (full evidence), CSV (both sample series) or HTML (inert readable report). Files contain model configuration, invented coefficients, numeric evidence and content identity. There are no real plant readings.

## Suggested learning experiments

| Question                                         | Synthetic setup                        | Inspect                                                             |
| ------------------------------------------------ | -------------------------------------- | ------------------------------------------------------------------- |
| How does a lagged input settle?                  | Constant source, reference factors     | Source relaxation and offsets approaching the analytic equilibrium  |
| How do thermal capacities affect response?       | Compare inertia 0.75 and 1.25          | Early transient shape, not a claim about a material or reactor size |
| What follows a temporary reduction in rejection? | Cooling dip; compare cooling 1 and 0.5 | Hot/cool curves, restoration boundary and accumulated energy        |
| What remains after input is removed?             | Source-off                             | Fictional lag and stored heat only; never nuclear decay heat        |
| What does generic derating change?               | Constant source, derating 0.15         | Lower target as the hot offset rises; not neutron feedback          |

## Troubleshooting and privacy

If computation fails, downloads and playback are disabled. Verify the app console is open, then use **Retry experiment**. Source builds require `python tools/build_native.py` plus `npm run build`. Missing bundled files should be resolved by extracting the complete verified ZIP, not downloading random binaries.

The browser optionally remembers only reviewed parameter settings. Blocked/corrupt storage falls back to defaults. Clear site storage to reset preferences, or use **Reset to reference**. No account, personal upload, remote model, telemetry or external font is used. External GitHub/contact links leave the app only when you choose them.

History is opt-in through `--history path.sqlite3`, never stored by browsing. It rejects tampered reports, updates/deletes and a 101st distinct run. Choose a new database instead of overwriting history. Export destination files are exclusive-create; repeat with a new filename. Saving history and a file is not a cross-file atomic transaction.

Accessibility: use Tab/Shift+Tab, visible focus, native selects, Arrow keys on the timeline and the readable table. Charts use color plus dashed reference lines and text labels. Narrow layouts stack controls above results. Reduced-motion preferences stop decorative flow animation. Contact/support: [Jason Stys](https://github.com/JasonStys), or [open a reproducible issue](https://github.com/JasonStys/reactor-systems-simulator/issues) without personal information.
