import { describe, expect, it, vi } from "vitest";
import { fetchTenantConfig, saveTenantConfig } from "./tenantService.js";
import type { TenantConfig } from "../types/tenant.js";

const mockConfig: TenantConfig = {
  tenant_id: "victor_cell",
  brand_name: "Victor Cell",
  brand_slogan: "ERP & Balcão Inteligente",
  brand_badge: "PRO",
  theme: {
    primary_color: "#F71963",
    primary_hover: "#E00E54",
    primary_glow: "rgba(247, 25, 99, 0.25)",
    bg_canvas: "#090D14",
    bg_surface: "#121826",
    logo_icon: "⚡",
  },
  modules: {
    whatsapp: true,
    orders: true,
    metrics: true,
    catalog: true,
    erp: true,
    copilot: true,
    audit: true,
    profile: true,
    simulator: true,
  },
};

describe("tenantService", () => {
  it("deve carregar configuração de tenant com sucesso", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockConfig,
    });

    const result = await fetchTenantConfig(mockFetch as unknown as typeof fetch);
    expect(result).not.toBeNull();
    expect(result?.brand_name).toBe("Victor Cell");
    expect(result?.theme.primary_color).toBe("#F71963");
    expect(mockFetch).toHaveBeenCalledWith("/api/tenant/config");
  });

  it("deve retornar null em caso de falha de rede no fetchTenantConfig", async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error("Network Error"));
    const result = await fetchTenantConfig(mockFetch as unknown as typeof fetch);
    expect(result).toBeNull();
  });

  it("deve salvar configuração com sucesso via POST", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "success", message: "Salvo" }),
    });

    const res = await saveTenantConfig(mockConfig, mockFetch as unknown as typeof fetch);
    expect(res.success).toBe(true);
    expect(mockFetch).toHaveBeenCalledWith("/api/tenant/config", expect.objectContaining({
      method: "POST",
    }));
  });
});
