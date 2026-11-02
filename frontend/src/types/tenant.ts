export interface TenantTheme {
  primary_color: string;
  primary_hover: string;
  primary_glow: string;
  secondary_color?: string;
  tertiary_color?: string;
  quaternary_color?: string;
  filter_color?: string;
  bg_canvas: string;
  bg_surface: string;
  logo_icon: string;
  logo_url?: string;
}

export interface TenantModules {
  whatsapp: boolean;
  orders: boolean;
  metrics: boolean;
  catalog: boolean;
  erp: boolean;
  copilot: boolean;
  audit: boolean;
  profile: boolean;
  simulator: boolean;
}

export interface TenantConfig {
  tenant_id: string;
  brand_name: string;
  brand_slogan: string;
  brand_badge: string;
  theme: TenantTheme;
  modules: TenantModules;
}
