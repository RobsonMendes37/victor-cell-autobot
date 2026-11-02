import { describe, expect, it } from "vitest";
import {
  escapeHtml,
  formatCurrencyBR,
  formatOrderStatusBadge,
  formatPhoneBR,
  hexToRgba,
} from "./formatters.js";

describe("formatPhoneBR", () => {
  it("deve formatar número celular BR de 13 dígitos com DDI", () => {
    expect(formatPhoneBR("5585999990001")).toBe("(85) 99999-0001");
  });

  it("deve formatar número celular BR de 11 dígitos sem DDI", () => {
    expect(formatPhoneBR("85999990001")).toBe("(85) 99999-0001");
  });

  it("deve formatar telefone fixo BR de 10 dígitos", () => {
    expect(formatPhoneBR("8532223344")).toBe("(85) 3222-3344");
  });

  it("deve retornar traço para valor nulo ou vazio", () => {
    expect(formatPhoneBR("")).toBe("--");
    expect(formatPhoneBR(null)).toBe("--");
  });
});

describe("formatCurrencyBR", () => {
  it("deve formatar valores monetários em R$", () => {
    const formatted = formatCurrencyBR(135.5).replace(/\s+/g, " ");
    expect(formatted).toMatch(/R\$\s?135,50/);
  });

  it("deve tratar valor zero", () => {
    const formatted = formatCurrencyBR(0).replace(/\s+/g, " ");
    expect(formatted).toMatch(/R\$\s?0,00/);
  });
});

describe("hexToRgba", () => {
  it("deve converter hex de 6 caracteres para rgba", () => {
    expect(hexToRgba("#F71963", 0.25)).toBe("rgba(247, 25, 99, 0.25)");
  });

  it("deve converter hex curto de 3 caracteres para rgba", () => {
    expect(hexToRgba("#FFF", 0.5)).toBe("rgba(255, 255, 255, 0.5)");
  });
});

describe("escapeHtml", () => {
  it("deve sanitizar caracteres perigosos de injeção XSS", () => {
    const dangerous = '<script>alert("xss & hack")</script>';
    const escaped = escapeHtml(dangerous);
    expect(escaped).not.toContain("<script>");
    expect(escaped).toContain("&lt;script&gt;");
    expect(escaped).toContain("&amp;");
    expect(escaped).toContain("&quot;");
  });

  it("deve tratar nulos ou vazios", () => {
    expect(escapeHtml("")).toBe("");
    expect(escapeHtml(null)).toBe("");
  });
});

describe("formatOrderStatusBadge", () => {
  it("deve renderizar status CONFIRMED em português", () => {
    const badge = formatOrderStatusBadge("CONFIRMED");
    expect(badge).toContain("✓ Separando / Confirmado");
    expect(badge).toContain("status-pill");
  });

  it("deve renderizar status DISPATCHED_UBER em português", () => {
    const badge = formatOrderStatusBadge("DISPATCHED_UBER");
    expect(badge).toContain("🚗 Em Rota Uber Flash");
  });

  it("deve renderizar status WAITING_CONFIRMATION em português", () => {
    const badge = formatOrderStatusBadge("WAITING_CONFIRMATION");
    expect(badge).toContain("⏳ Aguardando Confirmação");
  });
});
