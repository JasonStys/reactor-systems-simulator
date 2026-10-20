/** Production browser, accessibility, export and resilience tests by Jason Stys.
 * Functions: test callbacks. Variables: real page/downloads/routes. Map: docs/CODE_INDEX.md.
 */
import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFile } from "node:fs/promises";

test("local-only initial experiment and explicit model boundary", async ({ page }) => {
  const foreign: string[] = [];
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  page.on("request", (request) => {
    if (!request.url().startsWith("http://127.0.0.1:") && !request.url().startsWith("data:"))
      foreign.push(request.url());
  });
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  await expect(page.locator("#run-id")).toHaveText(/^[a-f0-9]{64}$/);
  await expect(page.locator("#temperature-chart .series")).toHaveCount(4);
  await expect(
    page.getByRole("heading", { name: "A learning tool. Not a reactor model." }),
  ).toBeVisible();
  expect(foreign).toEqual([]);
  expect(errors).toEqual([]);
});

test("applied parameters, timeline, reference comparison and real downloads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  const original = await page.locator("#run-id").textContent();
  await page.locator("#scenario").selectOption("cooling-dip");
  await page.locator("#cooling").selectOption("0.5");
  await page.locator("#duration").selectOption("300");
  await expect(page.locator("#run-id")).toHaveText(original!);
  await page.getByRole("button", { name: "Run experiment" }).click();
  await expect(page.locator("#run-label")).toHaveText("COOLING-DIP");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  await page.getByLabel("Model time", { exact: true }).fill("240");
  await expect(page.locator("#clock")).toHaveText("240");
  await expect(page.locator("#event")).toHaveText("Cooling × 0.35");
  await page.getByRole("button", { name: "Play model timeline", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Pause model timeline", exact: true }),
  ).toBeVisible();
  await expect(page.locator("#clock")).not.toHaveText("240");
  await page.getByRole("button", { name: "Pause model timeline", exact: true }).click();
  for (const format of ["json", "csv", "html"]) {
    console.info(`Verifying real ${format.toUpperCase()} download`);
    const pending = page.waitForEvent("download");
    await page.locator(`#${format}`).click();
    const download = await pending;
    const payload = await readFile((await download.path())!, "utf8");
    expect(download.suggestedFilename()).toContain(`.${format}`);
    if (format === "json") {
      const report = JSON.parse(payload);
      expect(report.settings.cooling).toBe(0.5);
      expect(report.settings.duration).toBe(300);
      expect(report.experiment.samples).toHaveLength(301);
      expect(report.provenance.units).toBe("dimensionless");
    } else if (format === "csv") expect(payload.split("\n")).toHaveLength(604);
    else expect(payload).toContain("Content-Security-Policy");
  }
  await page.reload();
  await expect(page.locator("#cooling")).toHaveValue("0.5");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  await page.getByRole("button", { name: "Reset to reference" }).click();
  await expect(page.locator("#run-id")).toHaveText(original!);
});

test("failure disables exports and retry recovers", async ({ page }) => {
  await page.route("**/api/run?**", (route) => route.fulfill({ status: 500, body: "unavailable" }));
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Could not run");
  await expect(page.locator("#play")).toBeDisabled();
  await expect(page.locator("#json")).not.toHaveAttribute("href");
  await page.unroute("**/api/run?**");
  await page.getByRole("button", { name: "Retry experiment" }).click();
  await expect(page.getByRole("status")).toContainText("Experiment ready");
});

test("obsolete requests cannot replace the applied experiment", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  await page.route("**/api/run?scenario=cooling-dip&**", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    try {
      await route.continue();
    } catch {
      /* Superseded aborted request is expected. */
    }
  });
  await page.locator("#scenario").selectOption("cooling-dip");
  await page.locator("#apply").click();
  await page.locator("#scenario").selectOption("source-off");
  await page.locator("#apply").click();
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  await expect(page.locator("#run-label")).toHaveText("SOURCE-OFF");
  await expect(page.locator("#json")).toHaveAttribute("href", /scenario=source-off/);
});

test("desktop and mobile accessibility with no horizontal overflow", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  for (const width of [1280, 390]) {
    await page.setViewportSize({ width, height: 900 });
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(
      true,
    );
    const scan = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(scan.violations).toEqual([]);
  }
  await page.getByLabel("Model time", { exact: true }).focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator("#clock")).toHaveText("1");
  await page.getByRole("link", { name: "How it works" }).click();
  await expect(page.locator("#guide")).toBeInViewport();
});

test("blocked or corrupt storage does not prevent experiments", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, "localStorage", {
      get() {
        throw new Error("denied");
      },
    });
  });
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  await expect(page.locator("#scenario")).toHaveValue("baseline");
});

test("rapid pause/play owns at most one animation frame", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("status")).toContainText("Experiment ready");
  const observed = await page.evaluate(() => {
    const originalRequest = window.requestAnimationFrame;
    const originalCancel = window.cancelAnimationFrame;
    const pending = new Set<number>();
    window.requestAnimationFrame = (callback) => {
      const id = originalRequest.call(window, callback);
      pending.add(id);
      return id;
    };
    window.cancelAnimationFrame = (id) => {
      pending.delete(id);
      originalCancel.call(window, id);
    };
    const button = document.getElementById("play")!;
    try {
      // Same-task events reproduce a pause/restart before the previous frame can fire.
      button.click();
      button.click();
      button.click();
      const afterRestart = pending.size;
      button.click();
      return { afterRestart, afterStop: pending.size };
    } finally {
      window.requestAnimationFrame = originalRequest;
      window.cancelAnimationFrame = originalCancel;
    }
  });
  expect(observed).toEqual({ afterRestart: 1, afterStop: 0 });
});
