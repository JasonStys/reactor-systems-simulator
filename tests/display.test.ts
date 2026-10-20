/** Pure presentation regression tests by Jason Stys; symbols/variables: docs/CODE_INDEX.md. */
import { describe, expect, it } from "vitest";
import { defaults, number, parseSettings, path, readSettings, type Sample } from "../web/display";

describe("finite normalized display", () => {
  it.each([
    [1.23456, "1.235"],
    [0, "0.000"],
    [-1.2, "-1.200"],
    [NaN, "Unavailable"],
    [Infinity, "Unavailable"],
  ])("formats %s", (input, expected) => {
    expect(number(input as number)).toBe(expected);
  });
  it("projects exact first/last chart positions", () => {
    const samples = [
      { time: 0, hot: 0 },
      { time: 600, hot: 2 },
    ] as Sample[];
    expect(path(samples, "hot", 2)).toBe("M36.00,184.00 L664.00,24.00");
    expect(path([], "hot", 2)).toBe("");
    expect(path(samples, "hot", NaN)).toBe("");
    expect(path(samples, "hot", 0)).toBe("");
    expect(path([{ time: 0 }, { time: 0 }] as Sample[], "hot", 2)).toBe("");
  });
});
describe("bounded optional preferences", () => {
  it.each([
    null,
    [],
    {},
    { ...defaults, demand: NaN },
    { ...defaults, x: 1 },
    { ...defaults, scenario: "../../x" },
    { ...defaults, cooling: true },
    { ...defaults, toString: "unexpected" },
    JSON.parse(JSON.stringify(defaults).slice(0, -1) + ',"__proto__":{}}'),
  ])("rejects poisoned preferences %#", (value) => {
    expect(parseSettings(value)).toEqual(defaults);
  });
  it("accepts reviewed finite choices without mutation sharing", () => {
    const selected = { ...defaults, scenario: "cooling-dip", cooling: 0.5 };
    expect(parseSettings(selected)).toEqual(selected);
    expect(parseSettings(selected)).not.toBe(selected);
  });
  it("survives an absent browser storage API", () => {
    expect(readSettings()).toEqual(defaults);
  });
});
