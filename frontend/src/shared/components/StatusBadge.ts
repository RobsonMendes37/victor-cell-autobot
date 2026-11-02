/**
 * Componente Reutilizável de Badges e Indicadores Visuais de Status (Shared Component)
 * Victor Cell Enterprise
 */

import { escapeHtml } from "../../utils/formatters.js";

export function renderQualityBadgeHtml(quality?: string | null): string {
  const qUp = (quality || "").toUpperCase();
  if (qUp.includes("ORIGINAL_NACIONAL") || qUp.includes("ORIGINAL NACIONAL")) {
    return '<span style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); color:#34D399; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">Original Nacional (90d)</span>';
  } else if (qUp.includes("ORIGINAL_CHINA") || qUp.includes("ORIGINAL CHINA")) {
    return '<span style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">Original China</span>';
  } else if (qUp.includes("PRIMEIRA") || qUp.includes("1ª")) {
    return '<span style="background:rgba(168,85,247,0.15); border:1px solid rgba(168,85,247,0.3); color:#C084FC; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">⭐ 1ª Linha Premium</span>';
  } else {
    return '<span style="background:rgba(251,146,60,0.15); border:1px solid rgba(251,146,60,0.3); color:#FB923C; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">⚡ Paralela Incell</span>';
  }
}

export interface StockInfo {
  hasStock: boolean;
  stockQuantity?: number | null;
}

export function renderStockBadgeHtml(info: StockInfo | number): string {
  const isAvail =
    typeof info === "object"
      ? info.hasStock !== false &&
        (info.stockQuantity === undefined ||
          info.stockQuantity === null ||
          info.stockQuantity > 0 ||
          info.hasStock === true)
      : info > 0;

  const qty =
    typeof info === "object" && typeof info.stockQuantity === "number"
      ? info.stockQuantity
      : null;

  if (!isAvail) {
    return '<span style="background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); color:#F87171; padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#EF4444; display:inline-block;"></span> Esgotado</span>';
  }

  if (qty !== null && qty <= 2 && qty > 0) {
    return `<span class="badge-stock-critical" style="padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#F59E0B; display:inline-block;"></span> ⚠️ Últimas ${qty} un!</span>`;
  }

  return '<span style="background:rgba(16,185,129,0.18); border:1px solid rgba(16,185,129,0.4); color:#34D399; padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#10B981; display:inline-block;"></span> Em Estoque</span>';
}

export function renderOrderStatusBadgeHtml(status?: string | null): string {
  const s = String(status || "").toUpperCase();
  if (s === "CONFIRMED") {
    return '<span class="status-pill" style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3);">✓ Confirmado</span>';
  } else if (s === "PENDING_SEPARATION" || s === "SEPARATING") {
    return '<span class="status-pill" style="background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3);">🔧 Em Separação</span>';
  } else if (s === "WAITING_CONFIRMATION") {
    return '<span class="status-pill" style="background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3);">⏳ Aguardando Confirmação</span>';
  } else if (s === "READY_TO_PICKUP" || s === "READY") {
    return '<span class="status-pill" style="background: rgba(6, 182, 212, 0.15); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.3);">📦 Pronto Balcão</span>';
  } else if (s === "DISPATCHED_UBER") {
    return '<span class="status-pill" style="background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3);">🚗 Em Rota Uber Flash</span>';
  } else if (s === "DELIVERED") {
    return '<span class="status-pill" style="background: rgba(6, 182, 212, 0.15); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.3);">📦 Entregue / Concluído</span>';
  } else if (s === "CANCELLED") {
    return '<span class="status-pill" style="background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3);">✕ Cancelado</span>';
  }
  return `<span class="status-pill status-robot">${escapeHtml(status || "")}</span>`;
}
