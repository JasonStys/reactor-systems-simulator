/**
 * Frozen fictional matched-forcing lesson acceptance by Jason Stys.
 * Function: runNativeJourney callback; variables: dimensionless sample differences and observed peaks.
 * No reactor physics, physical inputs, hardware control or operating guidance.
 * Symbol locations: docs/CODE_INDEX.md.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { expect } from "@playwright/test";
import { runNativeJourney } from "./native_browser.mjs";

await runNativeJourney(async ({ page, request }) => {
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  await expect(page.locator("#forcing-comparison")).toContainText("invented and dimensionless");
  const baselineResponse = await request.get("/api/run?scenario=baseline&demand=1.25&cooling=0.5");
  assert.equal(baselineResponse.status(), 200);
  const baseline = await baselineResponse.json();
  assert.ok(baseline.forcing_comparison.every((row) => row.peak_absolute_difference === 0));
  await page.locator("#scenario").selectOption("cooling-dip");
  await page.getByRole("button", { name: "Run experiment" }).click();
  await expect(page.locator("#run-label")).toHaveText("COOLING-DIP");
  await expect(page.locator("#forcing-comparison")).toContainText("experiment − matched");
  const response = await request.get("/api/run?scenario=cooling-dip");
  assert.equal(response.status(), 200);
  const report = await response.json();
  assert.equal(report.provenance.units, "dimensionless");
  assert.equal(report.forcing_comparison.length, 4);
  for (const row of report.forcing_comparison) {
    const differences = report.experiment.samples.map((sample, index) => ({
      time: sample.time,
      value: sample[row.field] - report.matched_reference.samples[index][row.field],
    }));
    const peak = differences.reduce((best, sample) =>
      Math.abs(sample.value) > Math.abs(best.value) ? sample : best,
    );
    assert.equal(row.peak_absolute_difference, Math.abs(peak.value));
    assert.equal(row.peak_signed_difference, peak.value);
    assert.equal(row.peak_sample_time, peak.time);
    assert.equal(row.end_difference, differences.at(-1).value);
  }
  assert.ok(
    report.forcing_comparison.find((row) => row.field === "hot").peak_absolute_difference > 0,
  );
  const pending = page.waitForEvent("download");
  await page.locator("#json").click();
  const downloaded = await pending;
  assert.deepEqual(
    JSON.parse(await readFile(await downloaded.path(), "utf8")).forcing_comparison,
    report.forcing_comparison,
  );
});
