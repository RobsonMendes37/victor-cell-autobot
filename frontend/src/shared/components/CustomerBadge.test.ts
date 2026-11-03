import { describe, it, expect } from "vitest";
import { renderCustomerTierBadgeHtml, renderCustomerCardHtml, CustomerData } from "./CustomerBadge.js";

describe("CustomerBadge Shared Component", () => {
  it("renders Platinum tier badge properly", () => {
    const html = renderCustomerTierBadgeHtml("VIP_PLATINUM");
    expect(html).toContain("badge-tier-platinum");
    expect(html).toContain("VIP Platinum");
  });

  it("renders Ouro Recorrente tier badge properly", () => {
    const html = renderCustomerTierBadgeHtml("OURO_RECORRENTE");
    expect(html).toContain("badge-tier-gold");
    expect(html).toContain("Ouro Recorrente");
  });

  it("renders Prata Ativo tier badge properly", () => {
    const html = renderCustomerTierBadgeHtml("PRATA_ATIVO");
    expect(html).toContain("badge-tier-silver");
    expect(html).toContain("Prata Ativo");
  });

  it("renders Novo Parceiro tier badge properly", () => {
    const html = renderCustomerTierBadgeHtml("NOVO_PARCEIRO");
    expect(html).toContain("badge-tier-bronze");
    expect(html).toContain("Novo Parceiro");
  });

  it("renders mobile customer card with deep link and chat triggers", () => {
    const mockCustomer: CustomerData = {
      id: "cust-1",
      name: "TechFix Celulares",
      phone: "(85) 98888-1111",
      neighborhood: "Montese",
      loyalty_tier: "VIP_PLATINUM",
      orders_count: 24,
      total_spent: 4850.0,
      uber_deliveries: 18,
    };

    const html = renderCustomerCardHtml(mockCustomer);
    expect(html).toContain("TechFix Celulares");
    expect(html).toContain("badge-tier-platinum");
    expect(html).toContain("R$ 4850.00");
    expect(html).toContain("navigateWithFilter('orders'");
    expect(html).toContain("openChatDrawer");
  });
});
