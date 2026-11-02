import { describe, expect, it } from "vitest";
import { calculatePagination, renderPaginationHtml } from "./Pagination.js";

describe("Pagination Shared Component", () => {
  it("calculates correct pagination state for middle page", () => {
    const state = calculatePagination(58, 3, 10);
    expect(state.totalItems).toBe(58);
    expect(state.totalPages).toBe(6);
    expect(state.currentPage).toBe(3);
    expect(state.startIndex).toBe(20);
    expect(state.endIndex).toBe(30);
    expect(state.hasNext).toBe(true);
    expect(state.hasPrev).toBe(true);
  });

  it("handles first page boundaries correctly", () => {
    const state = calculatePagination(58, 1, 10);
    expect(state.currentPage).toBe(1);
    expect(state.startIndex).toBe(0);
    expect(state.endIndex).toBe(10);
    expect(state.hasPrev).toBe(false);
    expect(state.hasNext).toBe(true);
  });

  it("handles last page with partial count correctly", () => {
    const state = calculatePagination(58, 6, 10);
    expect(state.currentPage).toBe(6);
    expect(state.startIndex).toBe(50);
    expect(state.endIndex).toBe(58);
    expect(state.hasNext).toBe(false);
    expect(state.hasPrev).toBe(true);
  });

  it("clamps invalid out of range requested pages", () => {
    const stateUnder = calculatePagination(58, -5, 10);
    expect(stateUnder.currentPage).toBe(1);

    const stateOver = calculatePagination(58, 999, 10);
    expect(stateOver.currentPage).toBe(6);
  });

  it("handles 0 items gracefully", () => {
    const state = calculatePagination(0, 1, 10);
    expect(state.totalItems).toBe(0);
    expect(state.totalPages).toBe(1);
    expect(state.startIndex).toBe(0);
    expect(state.endIndex).toBe(0);
    expect(state.hasNext).toBe(false);
    expect(state.hasPrev).toBe(false);
  });

  it("renders valid semantic HTML string with buttons and counters", () => {
    const state = calculatePagination(58, 2, 10);
    const html = renderPaginationHtml(state, {
      onPageChangeFunctionName: "changeCatalogPage",
      itemNoun: "peças",
      containerId: "catalog-pagination-bar",
    });

    expect(html).toContain('id="catalog-pagination-bar"');
    expect(html).toContain("Mostrando 11 a 20 de 58 peças");
    expect(html).toContain("2 / 6");
    expect(html).toContain("onclick=\"changeCatalogPage(-1)\"");
    expect(html).toContain("onclick=\"changeCatalogPage(1)\"");
    expect(html).not.toContain('disabled');
  });
});
