/** Typed thermal evidence and pure chart helpers by Jason Stys.
 * Interfaces: Sample, Settings, Run. Functions: number, path, readSettings, parseSettings.
 * Variables/locations: docs/CODE_INDEX.md. All plotted quantities are dimensionless.
 */
export interface Sample {
  time: number;
  source: number;
  hot: number;
  cool: number;
  useful: number;
  input_energy: number;
  rejected_energy: number;
  stored_change: number;
  balance_error: number;
}
export interface Settings {
  scenario: string;
  duration: number;
  demand: number;
  cooling: number;
  inertia: number;
  feedback: number;
}
export interface Run {
  id: string;
  settings: Settings;
  experiment: { samples: Sample[]; max_balance_error: number };
  reference: { samples: Sample[] };
  provenance: { worker_sha256: string; limitation: string; method: string };
  events: { time: number; label: string }[];
}
export const defaults: Settings = {
  scenario: "baseline",
  duration: 600,
  demand: 1,
  cooling: 1,
  inertia: 1,
  feedback: 0,
};

/** Format finite display values; never hide unavailable data behind a misleading zero. */
export function number(value: number, digits = 3): string {
  return Number.isFinite(value) ? value.toFixed(digits) : "Unavailable";
}

/** Map finite samples into a bounded SVG viewport, retaining each integer-time observation. */
export function path(samples: Sample[], key: keyof Sample, maximum: number): string {
  if (samples.length < 2 || !Number.isFinite(maximum) || maximum <= 0) return "";
  const duration = samples.at(-1)!.time;
  if (duration <= 0) return "";
  return samples
    .map((sample, index) => {
      const x = 36 + (sample.time / duration) * 628;
      const y = 184 - (sample[key] / maximum) * 160;
      return `${index ? "L" : "M"}${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
}

/** Validate only finite reviewed local preference choices; reject unknown keys and poisoned state. */
export function parseSettings(value: unknown): Settings {
  if (!value || typeof value !== "object" || Array.isArray(value)) return { ...defaults };
  const item = value as Record<string, unknown>;
  const choices: Record<string, unknown[]> = {
    scenario: ["baseline", "demand-step", "cooling-dip", "source-off"],
    duration: [300, 600],
    demand: [0.75, 1, 1.25],
    cooling: [0.5, 1, 1.5],
    inertia: [0.75, 1, 1.25],
    feedback: [0, 0.15],
  };
  if (
    Object.keys(item).some((key) => !Object.hasOwn(choices, key)) ||
    Object.entries(choices).some(([key, values]) => !values.includes(item[key]))
  ) {
    return { ...defaults };
  }
  return { ...item } as unknown as Settings;
}

/** Read local preferences only; missing/corrupt/blocked storage uses documented defaults. */
export function readSettings(): Settings {
  try {
    return parseSettings(JSON.parse(localStorage.getItem("thermal-settings-v1") ?? "null"));
  } catch {
    return { ...defaults };
  }
}
