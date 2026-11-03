/**
 * Componente Reutilizável de Badges e Cards de Clientes / Assistências Técnicas (Shared Component)
 * Victor Cell Enterprise
 */

import { escapeHtml } from "../../utils/formatters.js";

export interface CustomerData {
  id: string;
  name: string;
  phone: string;
  document?: string;
  neighborhood?: string;
  loyalty_tier: string;
  orders_count: number;
  total_spent: number;
  uber_deliveries: number;
}

export function renderCustomerTierBadgeHtml(tier?: string | null): string {
  const t = String(tier || "").toUpperCase();
  if (t === "VIP_PLATINUM" || t.includes("PLATINUM")) {
    return '<span class="pill badge-tier-platinum" style="font-weight:700;">💎 VIP Platinum</span>';
  } else if (t === "OURO_RECORRENTE" || t.includes("OURO")) {
    return '<span class="pill badge-tier-gold" style="font-weight:700;">🥇 Ouro Recorrente</span>';
  } else if (t === "PRATA_ATIVO" || t.includes("PRATA")) {
    return '<span class="pill badge-tier-silver" style="font-weight:700;">🥈 Prata Ativo</span>';
  } else if (t === "NOVO_PARCEIRO" || t.includes("NOVO") || t.includes("BRONZE")) {
    return '<span class="pill badge-tier-bronze" style="font-weight:700;">🥉 Novo Parceiro</span>';
  }
  return `<span class="pill">${escapeHtml(tier || "Parceiro")}</span>`;
}

export function renderCustomerCardHtml(cust: CustomerData): string {
  const cleanPhone = (cust.phone || "").replace(/\D/g, "");
  return `
    <div class="customer-card-mobile" data-customer-id="${escapeHtml(cust.id)}">
      <div class="card-mobile-top">
        <div>
          <div style="font-weight: 700; font-size: 0.95rem; color: #fff;">${escapeHtml(cust.name)}</div>
          <div style="font-size: 0.75rem; color: var(--text-dim); font-family: var(--font-mono);">${escapeHtml(cust.phone)} • ${escapeHtml(cust.neighborhood || "Fortaleza")}</div>
        </div>
        ${renderCustomerTierBadgeHtml(cust.loyalty_tier)}
      </div>
      <div class="card-mobile-body">
        <div style="display: flex; justify-content: space-between; font-size: 0.825rem;">
          <span>Total Pedidos: <strong style="color: #fff;">${cust.orders_count}</strong></span>
          <span>Volume: <strong style="color: #34D399;">R$ ${cust.total_spent.toFixed(2)}</strong></span>
        </div>
        <div style="font-size: 0.75rem; color: var(--text-dim);">Entregas Uber: ${cust.uber_deliveries} viagens</div>
      </div>
      <div class="card-mobile-actions">
        <button class="btn btn-emerald btn-sm" onclick="openChatDrawer('${cust.phone}', '${escapeHtml(cust.name)}', '${cleanPhone}', true)">💬 Chat Ao Vivo</button>
        <button class="btn btn-secondary btn-sm" onclick="navigateWithFilter('orders', { search: '${escapeHtml(cust.name)}' })">📦 Pedidos</button>
      </div>
    </div>
  `.trim();
}
