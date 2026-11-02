/**
 * Componente Reutilizável de Paginação de Listagens (Shared Component)
 * Victor Cell Enterprise
 */

export interface PaginationState {
  currentPage: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
  startIndex: number;
  endIndex: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export function calculatePagination(
  totalItems: number,
  requestedPage: number = 1,
  pageSize: number = 10
): PaginationState {
  const safeTotal = Math.max(0, totalItems);
  const safePageSize = Math.max(1, pageSize);
  const totalPages = Math.max(1, Math.ceil(safeTotal / safePageSize));

  let currentPage = requestedPage;
  if (currentPage < 1) currentPage = 1;
  if (currentPage > totalPages) currentPage = totalPages;

  const startIndex = safeTotal === 0 ? 0 : (currentPage - 1) * safePageSize;
  const endIndex = Math.min(startIndex + safePageSize, safeTotal);

  return {
    currentPage,
    pageSize: safePageSize,
    totalItems: safeTotal,
    totalPages,
    startIndex,
    endIndex,
    hasNext: currentPage < totalPages,
    hasPrev: currentPage > 1,
  };
}

export interface RenderPaginationOptions {
  containerId?: string;
  onPageChangeFunctionName: string;
  itemNoun?: string;
}

export function renderPaginationHtml(
  state: PaginationState,
  options: RenderPaginationOptions
): string {
  const itemNoun = options.itemNoun || "itens";
  const infoText =
    state.totalItems > 0
      ? `Mostrando ${state.startIndex + 1} a ${state.endIndex} de ${state.totalItems} ${itemNoun}`
      : `0 ${itemNoun} encontrados`;

  const prevDisabled = !state.hasPrev ? "disabled" : "";
  const nextDisabled = !state.hasNext ? "disabled" : "";

  return `
    <div class="pagination-bar" ${options.containerId ? `id="${options.containerId}"` : ""}>
      <div style="font-size: 0.8rem; color: var(--text-muted);">${infoText}</div>
      <div style="display: flex; gap: 0.5rem; align-items: center;">
        <button class="pagination-btn" onclick="${options.onPageChangeFunctionName}(-1)" ${prevDisabled}>
          ← Anterior
        </button>
        <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-main); padding: 0 0.5rem;">
          ${state.currentPage} / ${state.totalPages}
        </span>
        <button class="pagination-btn" onclick="${options.onPageChangeFunctionName}(1)" ${nextDisabled}>
          Próxima →
        </button>
      </div>
    </div>
  `.trim();
}
