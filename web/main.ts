/** Applied-experiment controller by Jason Stys.
 * Functions: element, settings, stop, render, graph, load, tick. Variables: run, cursor,
 * request generation and abort controller prevent stale results. Exact lines: docs/CODE_INDEX.md.
 * All API data is local reviewed evidence; text uses textContent, never remote HTML.
 */
import "./style.css";
import {
  defaults,
  number,
  path,
  readSettings,
  type Run,
  type Sample,
  type Settings,
} from "./display";

/** Obtain an authored required element; missing markup fails immediately during testing. */
function element<T extends HTMLElement>(id: string): T {
  const value = document.getElementById(id);
  if (!value) throw new Error(`Missing UI element: ${id}`);
  return value as T;
}
const form = element<HTMLFormElement>("settings");
const timeline = element<HTMLInputElement>("timeline");
const play = element<HTMLButtonElement>("play");
const status = element("status");
let run: Run | undefined;
let cursor = 0;
let playing = false;
let last = 0;
let generation = 0;
let request: AbortController | undefined;
const startup = readSettings();
for (const [key, value] of Object.entries(startup))
  element<HTMLSelectElement>(key).value = String(value);

/** Read finite select values; the Python service independently enforces the same allowlist. */
function settings(): Settings {
  return Object.fromEntries(
    Object.keys(defaults).map((key) => [
      key,
      key === "scenario"
        ? element<HTMLSelectElement>(key).value
        : Number(element<HTMLSelectElement>(key).value),
    ]),
  ) as unknown as Settings;
}

/** Pause playback without leaving an active animation-frame chain. */
function stop(): void {
  playing = false;
  play.textContent = "▶ Play";
  play.setAttribute("aria-label", "Play model timeline");
  document.body.classList.add("paused");
}

/** Show selected integer-time observations and a readable experiment/reference data table. */
function render(): void {
  if (!run) return;
  const index = Math.min(run.settings.duration, Math.max(0, Math.floor(cursor)));
  const sample = run.experiment.samples[index]!;
  const reference = run.reference.samples[index]!;
  timeline.value = String(index);
  element("clock").textContent = String(index);
  for (const key of ["source", "hot", "cool", "useful"] as const) {
    element(`${key}-value`).textContent = number(sample[key]);
    if (key !== "source") element(`${key}-svg`).textContent = number(sample[key]);
  }
  element("energy-in").textContent = number(sample.input_energy);
  element("energy-out").textContent = number(sample.rejected_energy);
  element("energy-stored").textContent = number(sample.stored_change);
  element("event").textContent =
    run.events.filter((event) => event.time <= index).at(-1)?.label ??
    (index === 0
      ? "Initial state · all nodes start at zero."
      : "Before any scenario event · source relaxation and heat transfer.");
  const rows = (["source", "hot", "cool", "useful", "balance_error"] as const).map((key) => {
    const row = document.createElement("tr");
    const heading = document.createElement("th");
    heading.scope = "row";
    heading.textContent = key.replaceAll("_", " ");
    row.append(heading);
    for (const observation of [sample, reference]) {
      const cell = document.createElement("td");
      cell.textContent = number(observation[key], 6);
      row.append(cell);
    }
    return row;
  });
  element("sample-table").replaceChildren(...rows);
}

/** Draw bounded native SVG curves; only numeric path coordinates enter SVG attributes. */
function graph(): void {
  if (!run) return;
  const chart = document.getElementById("temperature-chart")!;
  const ns = "http://www.w3.org/2000/svg";
  chart.replaceChildren();
  const maximum =
    Math.max(
      1,
      ...run.experiment.samples.map((sample) => sample.hot),
      ...run.reference.samples.map((sample) => sample.hot),
    ) * 1.1;
  for (let fraction = 0; fraction <= 1; fraction += 0.25) {
    const y = 184 - fraction * 160;
    const line = document.createElementNS(ns, "path");
    line.setAttribute("d", `M36 ${y}H664`);
    line.setAttribute("class", "grid");
    chart.append(line);
    const label = document.createElementNS(ns, "text");
    label.setAttribute("x", "0");
    label.setAttribute("y", String(y + 4));
    label.textContent = number(maximum * fraction, 1);
    chart.append(label);
  }
  for (const [samples, reference] of [
    [run.reference.samples, true],
    [run.experiment.samples, false],
  ] as const) {
    for (const key of ["hot", "cool"] as const) {
      const curve = document.createElementNS(ns, "path");
      curve.setAttribute("d", path(samples as Sample[], key, maximum));
      curve.setAttribute("class", `series ${key} ${reference ? "reference" : ""}`);
      chart.append(curve);
    }
  }
  for (const [x, value] of [
    [36, "0"],
    [620, String(run.settings.duration)],
  ] as const) {
    const label = document.createElementNS(ns, "text");
    label.setAttribute("x", String(x));
    label.setAttribute("y", "212");
    label.textContent = value;
    chart.append(label);
  }
}

/** Apply one snapshot atomically; cancellation and generation checks discard obsolete requests. */
async function load(): Promise<void> {
  const current = ++generation;
  request?.abort();
  request = new AbortController();
  stop();
  const selected = settings();
  status.textContent = "Computing reviewed local experiment…";
  play.disabled = true;
  element("retry").hidden = true;
  const query = new URLSearchParams(
    Object.entries(selected).map(([key, value]) => [key, String(value)]),
  );
  try {
    const response = await fetch(`/api/run?${query}`, { signal: request.signal });
    if (!response.ok) throw new Error("Local model unavailable");
    const result = (await response.json()) as Run;
    if (current !== generation) return;
    run = result;
    cursor = 0;
    timeline.max = String(run.settings.duration);
    element("horizon").textContent = `/ ${run.settings.duration}`;
    element("run-label").textContent = run.settings.scenario.toUpperCase();
    element("run-id").textContent = run.id;
    element("residual").textContent = run.experiment.max_balance_error.toExponential(2);
    for (const format of ["json", "csv", "html"]) {
      const link = element<HTMLAnchorElement>(format);
      link.href = `/api/report?${query}&format=${format}`;
      link.classList.remove("disabled");
      link.removeAttribute("aria-disabled");
    }
    try {
      localStorage.setItem("thermal-settings-v1", JSON.stringify(selected));
    } catch {
      /* Storage is optional; a blocked browser must not prevent experiments. */
    }
    status.textContent = "Experiment ready. Changes above apply when you run again.";
    play.disabled = false;
    graph();
    render();
  } catch {
    if (current !== generation) return;
    run = undefined;
    element("run-label").textContent = "NO ACTIVE RESULT";
    element("temperature-chart").replaceChildren();
    element("sample-table").replaceChildren();
    for (const id of [
      "source-value",
      "hot-value",
      "cool-value",
      "useful-value",
      "hot-svg",
      "cool-svg",
      "useful-svg",
      "energy-in",
      "energy-out",
      "energy-stored",
      "residual",
    ]) {
      element(id).textContent = "—";
    }
    element("event").textContent = "No valid experiment is currently loaded.";
    for (const format of ["json", "csv", "html"]) {
      const link = element<HTMLAnchorElement>(format);
      link.removeAttribute("href");
      link.classList.add("disabled");
      link.setAttribute("aria-disabled", "true");
    }
    element("run-id").textContent = "Unavailable";
    status.textContent = "Could not run the local model. Check the app is running, then retry.";
    element("retry").hidden = false;
  }
}

/** Advance at 30 model-time units per wall-clock second; no new physics is calculated in UI. */
function tick(now: number): void {
  if (!playing || !run) return;
  cursor = Math.min(run.settings.duration, cursor + Math.min(100, now - last) * 0.03);
  last = now;
  render();
  if (cursor >= run.settings.duration) stop();
  else requestAnimationFrame(tick);
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  void load();
});
element("reset").addEventListener("click", () => {
  for (const [key, value] of Object.entries(defaults))
    element<HTMLSelectElement>(key).value = String(value);
  void load();
});
element("retry").addEventListener("click", () => {
  void load();
});
timeline.addEventListener("input", () => {
  stop();
  cursor = Number(timeline.value);
  render();
});
play.addEventListener("click", () => {
  if (playing) {
    stop();
    return;
  }
  if (run && cursor >= run.settings.duration) cursor = 0;
  playing = true;
  last = performance.now();
  play.textContent = "Ⅱ Pause";
  play.setAttribute("aria-label", "Pause model timeline");
  document.body.classList.remove("paused");
  requestAnimationFrame(tick);
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden) stop();
});
void load();
