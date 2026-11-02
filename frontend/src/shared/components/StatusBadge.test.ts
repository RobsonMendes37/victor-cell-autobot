import { describe, expect, it } from "vitest";
import {
  renderOrderStatusBadgeHtml,
  renderQualityBadgeHtml,
  renderStockBadgeHtml,
} from "./StatusBadge.js";

describe("StatusBadge Shared Component", () => {
  it("renders quality badges for known tiers", () => {
    expect(renderQualityBadgeHtml("ORIGINAL_NACIONAL")).toContain("Original Nacional (90d)");
    expect(renderQualityBadgeHtml("ORIGINAL_CHINA")).toContain("Original China");
    expect(renderQualityBadgeHtml("PRIMEIRA")).toContain("1ª Linha Premium");
    expect(renderQualityBadgeHtml("INCELL")).toContain("Paralela Incell");
  });

  it("renders stock badges for available and out of stock items", () => {
    const inStock = renderStockBadgeHtml({ hasStock: true, stockQuantity: 10 });
    expect(inStock).toContain("Em Estoque");

    const outStock = renderStockBadgeHtml({ hasStock: false, stockQuantity: 0 });
    expect(outStock).toContain("Esgotado");

    const lowStock = renderStockBadgeHtml({ hasStock: true, stockQuantity: 2 });
    expect(lowStock).toContain("Últimas 2 un!");
  });

  it("renders order status badges for all workflow phases", () => {
    expect(renderOrderStatusBadgeHtml("CONFIRMED")).toContain("Confirmado");
    expect(renderOrderStatusBadgeHtml("PENDING_SEPARATION")).toContain("Em Separação");
    expect(renderOrderStatusBadgeHtml("WAITING_CONFIRMATION")).toContain("Aguardando Confirmação");
    expect(renderOrderStatusBadgeHtml("READY_TO_PICKUP")).toContain("Pronto Balcão");
    expect(renderOrderStatusBadgeHtml("DISPATCHED_UBER")).toContain("Em Rota Uber Flash");
    expect(renderOrderStatusBadgeHtml("DELIVERED")).toContain("Entregue / Concluído");
    expect(renderOrderStatusBadgeHtml("CANCELLED")).toContain("Cancelado");
  });
});
