import type { OrderStatus } from "../types/orders.js";

/**
 * Formata números de telefone brasileiros (10, 11, 12 e 13 dígitos com DDI 55).
 */
export function formatPhoneBR(raw?: string | null): string {
  if (!raw) return "--";
  const digits = String(raw).replace(/\D/g, "");
  if (digits.length === 13 && digits.startsWith("55")) {
    return `(${digits.slice(2, 4)}) ${digits.slice(4, 9)}-${digits.slice(9)}`;
  } else if (digits.length === 12 && digits.startsWith("55")) {
    return `(${digits.slice(2, 4)}) ${digits.slice(4, 8)}-${digits.slice(8)}`;
  } else if (digits.length === 11) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  } else if (digits.length === 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }
  return raw;
}

/**
 * Formata valores numéricos para moeda Real Brasileiro (R$).
 */
export function formatCurrencyBR(value: number): string {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
  }).format(value || 0);
}

/**
 * Converte cor hexadecimal para RGBA com canal alpha.
 */
export function hexToRgba(hex: string, alpha: number): string {
  let cleaned = hex.replace("#", "");
  if (cleaned.length === 3) {
    cleaned = cleaned
      .split("")
      .map((c) => c + c)
      .join("");
  }
  const num = parseInt(cleaned, 16);
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Sanitiza texto prevenindo injeções de XSS.
 */
export function escapeHtml(text?: string | null): string {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Retorna pill HTML padronizada e semântica para o status do pedido.
 */
export function formatOrderStatusBadge(status?: OrderStatus | string | null): string {
  const s = String(status || "").toUpperCase();
  if (s === "CONFIRMED") {
    return '<span class="status-pill" style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3);">✓ Separando / Confirmado</span>';
  } else if (s === "WAITING_CONFIRMATION") {
    return '<span class="status-pill" style="background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3);">⏳ Aguardando Confirmação</span>';
  } else if (s === "DISPATCHED_UBER") {
    return '<span class="status-pill" style="background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3);">🚗 Em Rota Uber Flash</span>';
  } else if (s === "DELIVERED") {
    return '<span class="status-pill" style="background: rgba(6, 182, 212, 0.15); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.3);">📦 Entregue / Concluído</span>';
  } else if (s === "CANCELLED") {
    return '<span class="status-pill" style="background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3);">✕ Cancelado</span>';
  }
  return `<span class="status-pill status-robot">${escapeHtml(status || "")}</span>`;
}
