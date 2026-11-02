/**
 * Componente Reutilizável de Gestão de Paleta de Cores e Constantes Hexadecimais
 * Victor Cell Enterprise
 */

export interface SystemPalette {
  primary: string;       // Cor Primária (Botões de Ação, Tabs, Logo)
  secondary: string;     // Cor Secundária (Gráficos, Info, Destaques)
  tertiary: string;      // Cor Terciária (Sucesso, Estoque Disponível)
  quaternary: string;    // Cor Quaternária (Alertas, Logística Uber Flash)
  filters: string;       // Fundo de Chips e Filtros Rápidos
  primaryHover?: string;
}

export const DEFAULT_PALETTE: SystemPalette = {
  primary: "#F71963",
  secondary: "#6366F1",
  tertiary: "#10B981",
  quaternary: "#F59E0B",
  filters: "#334155",
  primaryHover: "#E00E54",
};

/**
 * Valida se a string é uma cor hexadecimal válida (#RGB ou #RRGGBB).
 */
export function isValidHex(hex: string): boolean {
  if (!hex) return false;
  const clean = hex.trim();
  return /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.test(clean);
}

/**
 * Normaliza um código hexadecimal para o formato padrão maiúsculo #RRGGBB.
 */
export function normalizeHex(raw: string, fallback: string = "#000000"): string {
  if (!raw) return fallback.toUpperCase();
  let clean = raw.trim();
  if (!clean.startsWith("#")) {
    clean = "#" + clean;
  }
  if (!isValidHex(clean)) {
    return fallback.toUpperCase();
  }
  if (clean.length === 4) {
    const r = clean[1];
    const g = clean[2];
    const b = clean[3];
    clean = `#${r}${r}${g}${g}${b}${b}`;
  }
  return clean.toUpperCase();
}

/**
 * Converte código hexadecimal para RGBA com canal alpha especificado.
 */
export function hexToRgba(hex: string, alpha: number): string {
  const normalized = normalizeHex(hex);
  const num = parseInt(normalized.slice(1), 16);
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Gera o dicionário de variáveis CSS injetadas no :root.
 */
export function generateCssVariables(palette: Partial<SystemPalette>): Record<string, string> {
  const p = { ...DEFAULT_PALETTE, ...palette };
  const primary = normalizeHex(p.primary, DEFAULT_PALETTE.primary);
  const secondary = normalizeHex(p.secondary, DEFAULT_PALETTE.secondary);
  const tertiary = normalizeHex(p.tertiary, DEFAULT_PALETTE.tertiary);
  const quaternary = normalizeHex(p.quaternary, DEFAULT_PALETTE.quaternary);
  const filters = normalizeHex(p.filters, DEFAULT_PALETTE.filters);
  const hover = normalizeHex(p.primaryHover || "", DEFAULT_PALETTE.primaryHover!);

  return {
    "--primary": primary,
    "--vtex-pink": primary,
    "--tenant-brand": primary,
    "--tenant-brand-hover": hover,
    "--tenant-brand-glow": hexToRgba(primary, 0.25),
    "--secondary-color": secondary,
    "--tenant-secondary": secondary,
    "--tertiary-color": tertiary,
    "--tenant-tertiary": tertiary,
    "--emerald": tertiary,
    "--quaternary-color": quaternary,
    "--tenant-quaternary": quaternary,
    "--amber": quaternary,
    "--tenant-filter-bg": filters,
  };
}

export interface ColorCardOptions {
  idPrefix: string;
  label: string;
  colorValue: string;
  helperText: string;
}

/**
 * Gera a estrutura HTML do card seletor com sincronização Hex <-> Picker.
 */
export function renderColorCardHtml(options: ColorCardOptions): string {
  const hex = normalizeHex(options.colorValue);
  const pickerId = `${options.idPrefix}-color`;
  const textId = `${options.idPrefix}-color-text`;

  return `
    <div class="color-picker-card">
      <label style="font-size: 0.775rem; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 0.35rem;">
        ${options.label}
      </label>
      <div style="display: flex; gap: 8px; align-items: center;">
        <input type="color" id="${pickerId}" value="${hex}" oninput="syncColorPicker('${pickerId}', '${textId}')" style="width: 44px; height: 38px; border: none; border-radius: 6px; cursor: pointer; background: transparent;">
        <input type="text" id="${textId}" value="${hex}" maxlength="7" placeholder="${hex}" oninput="syncColorText('${textId}', '${pickerId}')" class="input-styled" style="flex: 1; padding: 0.55rem 0.75rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;">
      </div>
      <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; display: block;">${options.helperText}</span>
    </div>
  `.trim();
}
