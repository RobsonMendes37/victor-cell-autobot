import type { TenantConfig } from "../types/tenant.js";

/**
 * Serviço de comunicação da camada de White-Label e Multi-Tenancy.
 */
export async function fetchTenantConfig(
  apiFetch: typeof fetch = fetch
): Promise<TenantConfig | null> {
  try {
    const res = await apiFetch("/api/tenant/config");
    if (!res.ok) {
      throw new Error(`Falha HTTP ao carregar configuração: ${res.status}`);
    }
    const data: TenantConfig = await res.json();
    return data;
  } catch (err) {
    console.warn("Erro ao buscar tenant config:", err);
    return null;
  }
}

export async function saveTenantConfig(
  config: TenantConfig,
  apiFetch: typeof fetch = fetch
): Promise<{ success: boolean; message: string }> {
  try {
    const res = await apiFetch("/api/tenant/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(config),
    });
    const data = await res.json();
    if (res.ok && data.status === "success") {
      return { success: true, message: data.message || "Salvo com sucesso" };
    }
    return { success: false, message: data.message || "Erro ao salvar" };
  } catch (err) {
    return { success: false, message: String(err) };
  }
}
