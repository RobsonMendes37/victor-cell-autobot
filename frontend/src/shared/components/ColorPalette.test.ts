import { describe, expect, it } from "vitest";
import {
  DEFAULT_PALETTE,
  generateCssVariables,
  hexToRgba,
  isValidHex,
  normalizeHex,
  renderColorCardHtml,
} from "./ColorPalette.js";

describe("ColorPalette Shared Component", () => {
  it("validates hex color strings accurately", () => {
    expect(isValidHex("#F71963")).toBe(true);
    expect(isValidHex("#6366f1")).toBe(true);
    expect(isValidHex("#FFF")).toBe(true);
    expect(isValidHex("#123")).toBe(true);
    expect(isValidHex("F71963")).toBe(false);
    expect(isValidHex("#ZZZZZZ")).toBe(false);
    expect(isValidHex("#12345")).toBe(false);
  });

  it("normalizes 3-char and un-prefixed hex codes", () => {
    expect(normalizeHex("#fff")).toBe("#FFFFFF");
    expect(normalizeHex("f71963")).toBe("#F71963");
    expect(normalizeHex("#10B981")).toBe("#10B981");
    expect(normalizeHex("invalid", "#000000")).toBe("#000000");
  });

  it("converts hex to rgba correctly", () => {
    expect(hexToRgba("#F71963", 0.5)).toBe("rgba(247, 25, 99, 0.5)");
    expect(hexToRgba("#000000", 1)).toBe("rgba(0, 0, 0, 1)");
    expect(hexToRgba("#FFFFFF", 0.25)).toBe("rgba(255, 255, 255, 0.25)");
  });

  it("generates complete CSS variables dictionary for theme", () => {
    const vars = generateCssVariables({
      primary: "#F71963",
      secondary: "#6366F1",
      tertiary: "#10B981",
      quaternary: "#F59E0B",
      filters: "#334155",
    });

    expect(vars["--primary"]).toBe("#F71963");
    expect(vars["--tenant-brand"]).toBe("#F71963");
    expect(vars["--secondary-color"]).toBe("#6366F1");
    expect(vars["--tertiary-color"]).toBe("#10B981");
    expect(vars["--emerald"]).toBe("#10B981");
    expect(vars["--quaternary-color"]).toBe("#F59E0B");
    expect(vars["--amber"]).toBe("#F59E0B");
    expect(vars["--tenant-filter-bg"]).toBe("#334155");
    expect(vars["--tenant-brand-glow"]).toContain("rgba(247, 25, 99, 0.25)");
  });

  it("falls back to default palette when values omitted", () => {
    const vars = generateCssVariables({});
    expect(vars["--primary"]).toBe(DEFAULT_PALETTE.primary);
    expect(vars["--secondary-color"]).toBe(DEFAULT_PALETTE.secondary);
    expect(vars["--tertiary-color"]).toBe(DEFAULT_PALETTE.tertiary);
    expect(vars["--quaternary-color"]).toBe(DEFAULT_PALETTE.quaternary);
    expect(vars["--tenant-filter-bg"]).toBe(DEFAULT_PALETTE.filters);
  });

  it("renders color card HTML with picker and text synchronization", () => {
    const html = renderColorCardHtml({
      idPrefix: "tenant-secondary",
      label: "2. Cor Secundária (Info & Gráficos)",
      colorValue: "#6366F1",
      helperText: "Gráficos de mix, badges de info",
    });

    expect(html).toContain('id="tenant-secondary-color"');
    expect(html).toContain('id="tenant-secondary-color-text"');
    expect(html).toContain("syncColorPicker('tenant-secondary-color', 'tenant-secondary-color-text')");
    expect(html).toContain("syncColorText('tenant-secondary-color-text', 'tenant-secondary-color')");
    expect(html).toContain("2. Cor Secundária (Info & Gráficos)");
    expect(html).toContain("#6366F1");
  });
});
