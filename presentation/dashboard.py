from typing import Optional


def render_dashboard_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Victor Cell • ERP & Balcão Inteligente (VTEX Enterprise Console)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-canvas: #090D14;
      --bg-sidebar: #0D121D;
      --bg-surface: #121826;
      --bg-surface-elevated: #172033;
      --bg-surface-hover: #1C273E;
      --border-subtle: rgba(255, 255, 255, 0.07);
      --border-medium: rgba(255, 255, 255, 0.12);
      --vtex-pink: #F71963;
      --vtex-pink-hover: #E00E54;
      --vtex-pink-glow: rgba(247, 25, 99, 0.25);
      --vtex-pink-bg: rgba(247, 25, 99, 0.09);
      --primary: #6366F1;
      --primary-hover: #4F46E5;
      --primary-glow: rgba(99, 102, 241, 0.22);
      --emerald: #10B981;
      --emerald-glow: rgba(16, 185, 129, 0.2);
      --amber: #F59E0B;
      --amber-glow: rgba(245, 158, 11, 0.2);
      --rose: #EF4444;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
      --radius-sm: 6px;
      --radius-md: 10px;
      --radius-lg: 14px;
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    html, body {
      background-color: var(--bg-canvas);
      color: var(--text-main);
      font-family: var(--font-sans);
      min-height: 100vh;
      font-size: 13.5px;
      line-height: 1.5;
      overflow-x: hidden;
    }

    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-canvas); }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.22); }

    /* LAYOUT PRINCIPAL (VTEX ADMIN 2-COLUMN) */
    .app-layout {
      display: flex;
      min-height: 100vh;
      width: 100vw;
      background: var(--bg-canvas);
    }

    /* SIDEBAR LATERAL RETRÁTIL */
    .app-sidebar {
      width: 270px;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
      z-index: 100;
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .sidebar-brand {
      padding: 1.25rem 1.25rem 1.1rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(0, 0, 0, 0.12);
    }

    .brand-logo {
      width: 36px;
      height: 36px;
      border-radius: 9px;
      background: linear-gradient(135deg, var(--vtex-pink), #BD0043);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 14px var(--vtex-pink-glow);
      flex-shrink: 0;
    }

    .brand-info {
      flex: 1;
      min-width: 0;
    }

    .brand-name {
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      color: var(--text-main);
    }

    .brand-badge-vtex {
      font-size: 0.65rem;
      font-weight: 800;
      background: var(--vtex-pink-bg);
      color: #FF5A8D;
      padding: 1px 6px;
      border-radius: 4px;
      border: 1px solid rgba(247, 25, 99, 0.3);
      letter-spacing: 0.05em;
    }

    .brand-sub {
      font-size: 0.72rem;
      color: var(--text-dim);
      font-weight: 500;
      margin-top: 1px;
    }

    .sidebar-close-btn {
      display: none;
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 4px;
    }

    .sidebar-nav {
      padding: 0.85rem 0.65rem 1.5rem;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 0.15rem;
    }

    .nav-section-label {
      font-size: 0.68rem;
      font-weight: 700;
      color: var(--text-dim);
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 0.85rem 0.6rem 0.35rem;
    }

    .sidebar-nav .nav-tab {
      display: flex;
      align-items: center;
      gap: 0.7rem;
      padding: 0.6rem 0.75rem;
      border-radius: var(--radius-sm);
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-size: 0.84rem;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      transition: all 0.15s ease;
      text-align: left;
      width: 100%;
      position: relative;
    }

    .sidebar-nav .nav-tab:hover {
      background: var(--bg-surface);
      color: var(--text-main);
    }

    .sidebar-nav .nav-tab.active {
      background: var(--vtex-pink-bg);
      color: #FFF;
      font-weight: 600;
      box-shadow: inset 3px 0 0 var(--vtex-pink);
    }

    .sidebar-nav .nav-tab.active svg {
      color: var(--vtex-pink);
    }

    .sidebar-nav .nav-tab svg {
      flex-shrink: 0;
      color: var(--text-dim);
      transition: color 0.15s;
    }

    .sidebar-nav .nav-tab:hover svg {
      color: var(--text-main);
    }

    .sidebar-nav .tab-badge {
      margin-left: auto;
      font-size: 0.7rem;
      font-weight: 700;
      font-family: var(--font-mono);
      padding: 1px 6px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.07);
      color: var(--text-dim);
    }

    .sidebar-nav .nav-tab.active .tab-badge {
      background: rgba(247, 25, 99, 0.2);
      color: #FF5A8D;
    }

    .sidebar-footer {
      padding: 0.9rem 1.1rem;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(0, 0, 0, 0.15);
    }

    .user-profile {
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }

    .user-avatar {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.75rem;
      font-weight: 800;
      color: var(--text-muted);
    }

    .user-meta .user-name {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-main);
    }

    .user-meta .user-role {
      font-size: 0.7rem;
      color: var(--text-dim);
    }

    .sidebar-logout {
      color: var(--text-dim);
      transition: all 0.15s;
      display: flex;
      align-items: center;
      text-decoration: none;
      padding: 6px;
      border-radius: 6px;
    }

    .sidebar-logout:hover {
      color: #EF4444;
      background: rgba(239, 68, 68, 0.12);
    }

    /* BACKDROP OVERLAY */
    .sidebar-overlay {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.65);
      backdrop-filter: blur(4px);
      z-index: 90;
    }

    /* CONTENT VIEWPORT */
    .content-viewport {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      background: var(--bg-canvas);
    }

    /* TOP HEADER EXECUTIVO */
    .top-header {
      height: 58px;
      background: rgba(14, 19, 31, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 40;
      gap: 1rem;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 0.9rem;
    }

    .sidebar-toggle {
      display: none;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      cursor: pointer;
      padding: 6px;
      border-radius: 6px;
    }

    .breadcrumb {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      font-size: 0.85rem;
    }

    .bc-root {
      color: var(--text-dim);
      font-weight: 500;
    }

    .bc-sep {
      color: var(--border-medium);
      font-size: 0.8rem;
    }

    .bc-active {
      color: var(--text-main);
      font-weight: 600;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      flex-wrap: wrap;
    }

    .btn-top-action {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.4rem 0.75rem;
      border-radius: var(--radius-sm);
      border: 1px solid var(--border-subtle);
      background: var(--bg-surface);
      color: var(--text-muted);
      font-size: 0.78rem;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.15s;
    }

    .btn-top-action:hover {
      background: var(--bg-surface-elevated);
      color: var(--text-main);
      border-color: rgba(255, 255, 255, 0.15);
    }

    .main-body {
      flex: 1;
      padding: 1.5rem 1.75rem 3rem;
      max-width: 1600px;
      width: 100%;
      margin: 0 auto;
    }

    /* TOAST & BANNERS */
    #toast {
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      background: #111827;
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
      border-radius: 8px;
      padding: 0.75rem 1.1rem;
      display: none;
      align-items: center;
      gap: 0.6rem;
      z-index: 9999;
      font-size: 0.85rem;
      font-weight: 500;
    }

    #banner-ai-emergency {
      display: none;
      background: rgba(239, 68, 68, 0.12);
      border-bottom: 1px solid rgba(239, 68, 68, 0.3);
      color: #FCA5A5;
      padding: 0.6rem 1rem;
      text-align: center;
      font-size: 0.8rem;
    }

    .btn-emergency-resume {
      background: #EF4444;
      color: white;
      border: none;
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      font-weight: 600;
      font-size: 0.75rem;
      cursor: pointer;
      margin-left: 0.5rem;
    }

    /* HARDWARE SWITCH */
    .master-switch-wrapper {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 999px;
      padding: 0.3rem 0.7rem;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s;
    }
    .hardware-track {
      width: 28px;
      height: 16px;
      background: #374151;
      border-radius: 999px;
      position: relative;
      transition: background 0.2s;
    }
    .hardware-thumb {
      width: 12px;
      height: 12px;
      background: #fff;
      border-radius: 50%;
      position: absolute;
      top: 2px;
      left: 2px;
      transition: transform 0.2s;
    }
    .master-switch-on .hardware-track { background: var(--emerald); }
    .master-switch-on .hardware-thumb { transform: translateX(12px); }
    .master-switch-label { font-size: 0.75rem; font-weight: 600; color: var(--text-main); }

    /* STATUS PILLS */
    .pill {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.35rem 0.7rem;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 600;
    }
    .pill-emerald {
      background: rgba(16, 185, 129, 0.1);
      color: #34D399;
      border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .pill-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: currentColor;
    }

    /* KPI GRID */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }

    .kpi-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s, border-color 0.15s;
    }
    .kpi-card:hover {
      border-color: var(--border-medium);
      transform: translateY(-2px);
    }

    .kpi-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }
    .kpi-title {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-muted);
    }
    .kpi-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .kpi-val {
      font-size: 1.6rem;
      font-weight: 800;
      font-family: var(--font-mono);
      font-feature-settings: 'tnum';
      font-variant-numeric: tabular-nums;
      letter-spacing: -0.02em;
      margin-bottom: 0.3rem;
    }
    .kpi-sub {
      font-size: 0.72rem;
      color: var(--text-dim);
    }

    /* CARDS & CONTAINERS */
    .card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 1.25rem;
      margin-bottom: 1.25rem;
      box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }
    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border-subtle);
      gap: 0.75rem;
      flex-wrap: wrap;
    }
    .card-title-group {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .card-icon {
      width: 34px;
      height: 34px;
      border-radius: 8px;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--vtex-pink);
    }
    .card-title {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--text-main);
    }
    .card-subtitle {
      font-size: 0.75rem;
      color: var(--text-dim);
    }


    /* CHAT DRAWER LATERAL (WHATSAPP AO VIVO) */
    .drawer-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(4px);
      z-index: 9998;
      display: none;
      opacity: 0;
      transition: opacity 0.25s ease;
    }
    .drawer-overlay.active {
      display: block;
      opacity: 1;
    }
    .chat-drawer {
      position: fixed;
      top: 0;
      right: -480px;
      width: 460px;
      max-width: 95vw;
      height: 100vh;
      background: #0E1422;
      border-left: 1px solid var(--border-subtle);
      box-shadow: -8px 0 32px rgba(0, 0, 0, 0.7);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      transition: right 0.28s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .chat-drawer.active {
      right: 0;
    }
    .chat-drawer-header {
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--border-subtle);
      background: rgba(0, 0, 0, 0.35);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .drawer-close-btn {
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      color: var(--text-muted);
      cursor: pointer;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.9rem;
      transition: all 0.15s;
    }
    .drawer-close-btn:hover {
      background: rgba(239, 68, 68, 0.2);
      color: #F87171;
    }
    .chat-drawer-body {
      flex: 1;
      padding: 1.25rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      background: radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.7), #07090E);
    }
    .chat-bubble-drawer {
      max-width: 82%;
      padding: 0.65rem 0.85rem;
      border-radius: 12px;
      font-size: 0.825rem;
      line-height: 1.45;
      position: relative;
      word-break: break-word;
    }
    .chat-bubble-drawer.incoming {
      align-self: flex-start;
      background: #1E293B;
      color: #E2E8F0;
      border-bottom-left-radius: 3px;
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .chat-bubble-drawer.outgoing {
      align-self: flex-end;
      background: linear-gradient(135deg, #10593B, #0E4830);
      color: #F0FDF4;
      border-bottom-right-radius: 3px;
      border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .chat-bubble-meta {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 4px;
      margin-top: 4px;
      font-size: 0.675rem;
      color: rgba(255, 255, 255, 0.5);
      font-family: var(--font-mono);
    }
    .chat-drawer-footer {
      padding: 0.9rem 1.25rem;
      border-top: 1px solid var(--border-subtle);
      background: rgba(0, 0, 0, 0.25);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
    }

    /* VTEX MODALS (PRODUTO ERP & JSON VIEWER) */
    .vtex-modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(5px);
      z-index: 10000;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1rem;
      opacity: 0;
      transition: opacity 0.2s ease;
    }
    .vtex-modal-overlay.active {
      display: flex;
      opacity: 1;
    }
    .vtex-modal {
      background: #0E1422;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      box-shadow: 0 20px 48px -8px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.08);
      width: 100%;
      max-width: 620px;
      max-height: 90vh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: modalZoomIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes modalZoomIn {
      from { transform: scale(0.96); opacity: 0; }
      to { transform: scale(1); opacity: 1; }
    }
    .vtex-modal-header {
      padding: 1.1rem 1.25rem;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(0, 0, 0, 0.25);
    }
    .vtex-modal-title {
      font-size: 1rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .vtex-modal-body {
      padding: 1.25rem;
      overflow-y: auto;
      flex: 1;
    }
    .vtex-modal-footer {
      padding: 0.9rem 1.25rem;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 0.75rem;
      background: rgba(0, 0, 0, 0.25);
    }
    .vtex-form-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }
    .vtex-form-group {
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }
    .vtex-form-group.col-span-2 {
      grid-column: span 2;
    }
    .vtex-form-group label {
      font-size: 0.78rem;
      font-weight: 600;
      color: #94A3B8;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .vtex-form-group input, .vtex-form-group select {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 0.55rem 0.75rem;
      color: #fff;
      font-size: 0.85rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s;
    }
    .vtex-form-group input:focus, .vtex-form-group select:focus {
      border-color: var(--vtex-pink);
      box-shadow: 0 0 0 2px rgba(247, 25, 99, 0.2);
    }

    /* CARDS DE CATEGORIZAÇÃO WHATSAPP */
    .wa-cat-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 0.85rem 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
      transition: transform 0.15s, border-color 0.15s;
    }
    .wa-cat-card:hover {
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.2);
    }
    .wa-cat-card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
    }
    .wa-cat-card-val {
      font-size: 1.45rem;
      font-weight: 800;
      font-family: var(--font-mono);
    }
    .wa-cat-card-sub {
      font-size: 0.72rem;
      color: var(--text-dim);
    }

    /* CARDS DA PIPELINE DE IA */
    .pipeline-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }
    .pipeline-card-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
    }
    .pipeline-endpoint {
      font-family: var(--font-mono);
      font-size: 0.725rem;
      color: #94A3B8;
      background: rgba(0, 0, 0, 0.35);
      padding: 0.35rem 0.6rem;
      border-radius: 6px;
      border: 1px solid rgba(255, 255, 255, 0.05);
      word-break: break-all;
    }
    .pipeline-fallback {
      font-size: 0.735rem;
      color: #64748B;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    /* TAB PANES */
    .tab-pane {
      display: none;
      animation: fadeIn 0.15s ease;
    }
    .tab-pane.active {
      display: block;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* DATA TABLES */
    .table-responsive {
      overflow-x: auto;
      border-radius: var(--radius-sm);
    }
    .data-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      font-size: 0.84rem;
    }
    .data-table th {
      background: #0E1422;
      color: var(--text-dim);
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      padding: 0.75rem 0.9rem;
      border-bottom: 1px solid var(--border-subtle);
      text-align: left;
    }
    .data-table td {
      padding: 0.85rem 0.9rem;
      border-bottom: 1px solid var(--border-subtle);
      vertical-align: middle;
      font-feature-settings: 'tnum';
      font-variant-numeric: tabular-nums;
    }
    .data-table tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }

    /* BUTTONS */
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.55rem 1rem;
      border-radius: var(--radius-sm);
      font-size: 0.82rem;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      border: none;
      transition: all 0.15s;
      text-decoration: none;
    }
    .btn-primary {
      background: var(--vtex-pink);
      color: #fff;
    }
    .btn-primary:hover {
      background: var(--vtex-pink-hover);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px var(--vtex-pink-glow);
    }
    .btn-secondary {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
    }
    .btn-secondary:hover {
      background: var(--bg-surface-hover);
      border-color: var(--border-medium);
    }
    .btn-sm {
      padding: 0.35rem 0.65rem;
      font-size: 0.75rem;
    }

    /* INPUTS & FORMS */
    .search-input, .input-styled {
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      color: var(--text-main);
      padding: 0.5rem 0.8rem;
      font-size: 0.85rem;
      font-family: inherit;
      outline: none;
      transition: border-color 0.15s;
    }
    .search-input:focus, .input-styled:focus {
      border-color: var(--vtex-pink);
    }

    /* STAT CARDS */
    .stat-card {
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 1rem 1.15rem;
    }
    .stat-label {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-bottom: 0.3rem;
    }
    .stat-value {
      font-size: 1.35rem;
      font-weight: 800;
      font-family: var(--font-mono);
      font-variant-numeric: tabular-nums;
    }

    /* COPILOT CHAT & SIMULATOR */
    .copilot-container {
      display: flex;
      flex-direction: column;
      height: calc(100vh - 280px);
      min-height: 450px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      overflow: hidden;
    }
    .copilot-messages, .chat-messages {
      flex: 1;
      padding: 1.25rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }
    .copilot-input-bar {
      padding: 0.85rem 1.25rem;
      background: var(--bg-surface-elevated);
      border-top: 1px solid var(--border-subtle);
      display: flex;
      gap: 0.75rem;
      align-items: center;
    }
    .copilot-input-field {
      flex: 1;
      background: var(--bg-canvas);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.65rem 1rem;
      color: var(--text-main);
      font-family: inherit;
      font-size: 0.85rem;
      outline: none;
    }
    .copilot-input-field:focus {
      border-color: var(--vtex-pink);
    }

    /* RESPONSIVE */
    @media (max-width: 1024px) {
      .app-sidebar {
        position: fixed;
        left: 0;
        top: 0;
        transform: translateX(-100%);
      }
      .app-sidebar.sidebar-open {
        transform: translateX(0);
      }
      .sidebar-overlay.active {
        display: block;
      }
      .sidebar-toggle {
        display: inline-flex;
      }
      .sidebar-close-btn {
        display: inline-flex;
      }
      .main-body {
        padding: 1rem;
      }
    }
  </style>
</head>
<body>

  <!-- TOAST NOTIFICATION -->
  <div id="toast">
    <span id="toast-icon">✅</span>
    <span id="toast-msg">Ação executada com sucesso!</span>
  </div>

  <!-- BANNER DE EMERGÊNCIA - ATENDIMENTO MANUAL ATIVO (ZERO EMOJIS) -->
  <div id="banner-ai-emergency">
    <div style="display: inline-flex; align-items: center; justify-content: center; gap: 8px;">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F87171" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <span><strong>Atendimento Automático Pausado:</strong> As respostas da IA estão desativadas para todas as conversas do WhatsApp (Modo Manual).</span>
      <button class="btn-emergency-resume" onclick="toggleMasterAISwitch()">Reativar Atendimento</button>
    </div>
  </div>

  <div class="app-layout">
    <!-- SIDEBAR LATERAL RETRÁTIL (ESTILO VTEX ADMIN CONSOLE) -->
    <aside class="app-sidebar" id="app-sidebar">
      <div class="sidebar-brand">
        <div class="brand-logo">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>
        </div>
        <div class="brand-info">
          <div class="brand-name">Victor Cell <span class="brand-badge-vtex">PRO</span></div>
          <div class="brand-sub">ERP & Balcão WhatsApp</div>
        </div>
        <button class="sidebar-close-btn" onclick="toggleSidebar()" aria-label="Fechar Menu">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <!-- GRUPO 1: OPERAÇÃO DE BALCÃO -->
        <div class="nav-section-label">Operação de Balcão</div>
        <button class="nav-tab active" onclick="switchTab('conversations')" title="Atendimentos WhatsApp">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span>Atendimentos WhatsApp</span>
          <span class="tab-badge" id="badge-convs-count">0</span>
        </button>
        <button class="nav-tab" onclick="switchTab('orders')" title="Separação & Balcão de Saída">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
          <span>Separação & Balcão de Saída</span>
          <span class="tab-badge" id="badge-orders-count">0</span>
        </button>

        <!-- GRUPO 2: ESTOQUE & ERP NATIVO -->
        <div class="nav-section-label">Estoque & ERP Nativo</div>
        <button class="nav-tab" onclick="switchTab('overview')" title="Métricas & Relatórios">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          <span>Métricas & Relatórios</span>
        </button>
        <button class="nav-tab" onclick="switchTab('catalog')" title="Catálogo de Peças">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          <span>Catálogo de Peças</span>
          <span class="tab-badge" id="badge-catalog-count">0</span>
        </button>
        <button class="nav-tab" onclick="switchTab('erp')" title="ERP & Entrada de Estoque">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
          <span>ERP & Entrada de Estoque</span>
        </button>

        <!-- GRUPO 3: INTELIGÊNCIA ARTIFICIAL -->
        <div class="nav-section-label">Inteligência Artificial</div>
        <button class="nav-tab" onclick="switchTab('copilot')" title="Copiloto de Gestão">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
          <span>Copiloto de Gestão</span>
        </button>
        <button class="nav-tab" onclick="switchTab('gemini')" title="Simulador WhatsApp Sandbox">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
          <span>Simulador WhatsApp Sandbox</span>
        </button>

        <!-- GRUPO 4: GOVERNANÇA & SISTEMA -->
        <div class="nav-section-label">Governança & Sistema</div>
        <button class="nav-tab" onclick="switchTab('audit')" title="Auditoria & Logs">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
          <span>Auditoria & Logs</span>
          <span class="tab-badge" id="badge-audit-count">0</span>
        </button>
        <button class="nav-tab" onclick="switchTab('profile')" title="Perfil da Loja">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>Perfil da Loja</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="user-avatar">ADM</div>
          <div class="user-meta">
            <div class="user-name">Administrador</div>
            <div class="user-role">Balcão & Gestão</div>
          </div>
        </div>
        <a href="/logout" class="sidebar-logout" title="Sair do painel">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>
        </a>
      </div>
    </aside>

    <!-- BACKDROP OVERLAY FOR MOBILE -->
    <div class="sidebar-overlay" id="sidebar-overlay" onclick="toggleSidebar()"></div>

    <!-- VIEWPORT DE CONTEÚDO PRINCIPAL -->
    <div class="content-viewport">
      <!-- TOP HEADER EXECUTIVO -->
      <header class="top-header">
        <div class="header-left">
          <button class="sidebar-toggle" onclick="toggleSidebar()" aria-label="Abrir Menu Lateral">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
          </button>
          <div class="breadcrumb">
            <span class="bc-root">Victor Cell</span>
            <span class="bc-sep">/</span>
            <span class="bc-active" id="bc-current-title">Atendimentos WhatsApp</span>
          </div>
        </div>

        <div class="header-right">
          <!-- DISJUNTOR GERAL DA IA -->
          <div id="btn-master-ai" class="master-switch-wrapper master-switch-on" onclick="toggleMasterAISwitch()" title="Alternar Atendimento Automático IA ou Manual">
            <div class="hardware-track"><div class="hardware-thumb"></div></div>
            <span class="master-switch-label" id="label-master-ai">IA Ativa</span>
          </div>

          <div class="pill pill-emerald" id="pill-store">
            <span class="pill-dot"></span>
            <span id="store-status">Balcão Aberto</span>
          </div>
          <div class="pill pill-emerald" id="pill-wa">
            <span class="pill-dot"></span>
            <span id="wa-status">WhatsApp Conectado</span>
          </div>
          <a href="https://ntfy.sh/victor-cell-balcao-alertas" target="_blank" class="btn-top-action" title="Receber alertas com alarme no celular">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
            Alertas Push
          </a>
          <button class="btn-top-action" onclick="refreshAll()" title="Recarregar dados">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
            Atualizar
          </button>
        </div>
      </header>

      <!-- CORPO PRINCIPAL COM AS ABAS -->
      <main class="main-body">

<!-- TAB 1: ATENDIMENTOS AO VIVO (IA VS HUMANO) -->
    <div class="tab-pane active" id="tab-conversations">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">Atendimento ao Vivo • Controle de IA & Balcão</h2>
            <span class="badge-count" id="convs-counter">0 contatos</span>
          </div>
          <div class="toolbar-actions">
            <input type="text" class="search-input" id="search-convs" placeholder="Buscar por nome, telefone ou peça..." oninput="filterConversations()">
            <button class="btn btn-secondary btn-sm" onclick="fetchConversations()"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -1px; margin-right: 4px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Atualizar</button>
          </div>
        </div>

        <!-- Visualização Tablet/Desktop (Tabela Rica) -->
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Cliente / Oficina</th>
                <th>Última Mensagem & Horário</th>
                <th>Peça Sendo Cotada</th>
                <th>Status do Atendimento</th>
                <th>Ações de Balcão</th>
              </tr>
            </thead>
            <tbody id="convs-tbody-desktop">
              <tr><td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">Carregando atendimentos...</td></tr>
            </tbody>
          </table>
        </div>

        <!-- Visualização Mobile (Cards Touch Fáceis de Clicar) -->
        <div class="mobile-card-deck" id="convs-cards-mobile">
          <div style="text-align: center; padding: 2rem; color: var(--text-muted);">Carregando atendimentos no celular...</div>
        </div>
      </div>
    </div>

    <!-- TAB 2: SEPARAÇÃO DE PEÇAS & BALCÃO DE SAÍDA -->
    <div class="tab-pane" id="tab-orders">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">Fila de Separação de Peças & Balcão de Saída</h2>
            <span class="badge-count" id="orders-counter">0 pedidos</span>
          </div>
          <div class="toolbar-actions">
            <!-- Filtro de Modalidade (Balcão vs Uber Flash) -->
            <div class="filter-pill-group" style="display: flex; gap: 4px; margin-right: 6px;">
              <button class="filter-btn active" data-order-filter="all" onclick="filterOrdersMode('all', this)">Todos</button>
              <button class="filter-btn" data-order-filter="balcao" onclick="filterOrdersMode('balcao', this)">Retirada Balcão</button>
              <button class="filter-btn" data-order-filter="uber" onclick="filterOrdersMode('uber', this)">Uber Flash</button>
            </div>
            <a href="/api/reports/orders/csv" class="btn btn-emerald btn-sm" download="Pedidos_VictorCell_PowerBI.csv">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -1px; margin-right: 4px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> Exportar CSV
            </a>
            <button class="btn btn-secondary btn-sm" onclick="fetchStats()"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -1px; margin-right: 4px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Atualizar</button>
          </div>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Pedido & Data</th>
                <th>Cliente (WhatsApp)</th>
                <th>Peça Solicitada no Balcão</th>
                <th>Valor</th>
                <th>Modalidade / Destino</th>
                <th>Status do Pedido</th>
                <th>Reserva de Estoque (30 min)</th>
              </tr>
            </thead>
            <tbody id="orders-tbody">
              <tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Carregando pedidos de separação...</td></tr>
            </tbody>
          </table>
        </div>

        <div class="mobile-card-deck" id="orders-cards-mobile"></div>
      </div>
    </div>

    <!-- TAB 3: VISÃO GERAL & KPIS -->
    <div class="tab-pane" id="tab-overview">

      <!-- KPIS PRINCIPAIS (CONSOLIDADOS EM MÉTRICAS & RELATÓRIOS) -->
      <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Faturamento em Pedidos</span>
          <div class="kpi-icon" style="background: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-revenue" style="color: #34D399;">R$ 0,00</div>
        <div class="kpi-sub"><span style="color: #10B981; font-weight: 700;">● Confirmados</span> no balcão e Uber</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Atendimentos no WhatsApp</span>
          <div class="kpi-icon" style="background: rgba(99, 102, 241, 0.12); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-active-chats" style="color: #A5B4FC;">0</div>
        <div class="kpi-sub" id="kpi-ai-status">Atendimento Automático Ativo</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Saídas Balcão & Uber</span>
          <div class="kpi-icon" style="background: rgba(245, 158, 11, 0.12); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-uber" style="color: #FBBF24;">0%</div>
        <div class="kpi-sub" id="kpi-uber-count">0 pedidos para entrega</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Peças no Catálogo</span>
          <div class="kpi-icon" style="background: rgba(6, 182, 212, 0.12); color: #06B6D4; border: 1px solid rgba(6, 182, 212, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-stock-items" style="color: #38BDF8;">0</div>
        <div class="kpi-sub">Sincronizado c/ Google Sheets</div>
      </div>
    </div>



      <!-- AUDITORIA & CATEGORIZAÇÃO DE MENSAGENS DO WHATSAPP (TEMPO REAL) -->
      <div class="card" style="margin-bottom: 1.25rem; background: linear-gradient(135deg, rgba(14, 20, 34, 0.95), rgba(99, 102, 241, 0.05)); border-color: rgba(99, 102, 241, 0.25);">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-icon" style="background: rgba(99, 102, 241, 0.12); color: #818CF8;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <div>
              <div class="card-title">Auditoria de Interações no WhatsApp • Categorização de Demandas</div>
              <div class="card-subtitle">Classificação em tempo real de mensagens recebidas: cotações, pedidos, rupturas e transbordos</div>
            </div>
          </div>
          <span class="badge-count" id="wa-audit-updated">Atualizado em tempo real</span>
        </div>
        <div class="card-body" style="padding: 1.1rem 1.25rem;">
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.75rem; margin-bottom: 1rem;" id="wa-categories-grid">
            <div class="wa-cat-card" style="border-left: 3px solid #F59E0B;">
              <div class="wa-cat-card-header"><span>Cotações de Peças</span><span>💬</span></div>
              <div class="wa-cat-card-val" style="color: #FBBF24;" id="cat-val-quotes">0</div>
              <div class="wa-cat-card-sub">Preços e modelos consultados</div>
            </div>
            <div class="wa-cat-card" style="border-left: 3px solid #10B981;">
              <div class="wa-cat-card-header"><span>Pedidos Fechados</span><span>🛒</span></div>
              <div class="wa-cat-card-val" style="color: #34D399;" id="cat-val-orders">0</div>
              <div class="wa-cat-card-sub">Balcão e Uber Flash</div>
            </div>
            <div class="wa-cat-card" style="border-left: 3px solid #EF4444;">
              <div class="wa-cat-card-header"><span>Sem Saldo / Ruptura</span><span>⚠️</span></div>
              <div class="wa-cat-card-val" style="color: #F87171;" id="cat-val-ruptures">0</div>
              <div class="wa-cat-card-sub">Demanda não atendida em estoque</div>
            </div>
            <div class="wa-cat-card" style="border-left: 3px solid #818CF8;">
              <div class="wa-cat-card-header"><span>Transbordo p/ Balcão</span><span>👤</span></div>
              <div class="wa-cat-card-val" style="color: #A5B4FC;" id="cat-val-handoffs">0</div>
              <div class="wa-cat-card-sub">Assumido por atendente humano</div>
            </div>
            <div class="wa-cat-card" style="border-left: 3px solid #64748B;">
              <div class="wa-cat-card-header"><span>Fora de Escopo</span><span>🚫</span></div>
              <div class="wa-cat-card-val" style="color: #94A3B8;" id="cat-val-outofscope">0</div>
              <div class="wa-cat-card-sub">Celulares, serviços ou recusas</div>
            </div>
          </div>
          <div style="background: rgba(255,255,255,0.06); border-radius: 999px; height: 10px; overflow: hidden; display: flex;" id="wa-categories-bar" title="Distribuição percentual das mensagens">
            <div style="width: 45%; background: #F59E0B;" title="Cotações"></div>
            <div style="width: 25%; background: #10B981;" title="Pedidos"></div>
            <div style="width: 15%; background: #EF4444;" title="Rupturas"></div>
            <div style="width: 10%; background: #818CF8;" title="Transbordo"></div>
            <div style="width: 5%; background: #64748B;" title="Fora de Escopo"></div>
          </div>
        </div>
      </div>

      <!-- SEÇÃO DE INTELIGÊNCIA COMERCIAL DE WHATSAPP -->
      <div class="section-card" style="margin-bottom: 1.5rem; background: linear-gradient(135deg, rgba(14, 20, 34, 0.95), rgba(99, 102, 241, 0.05)); border-color: rgba(99, 102, 241, 0.25);">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #6366F1;"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
              Inteligência de Vendas no WhatsApp (37 Assistências / 3.752 Mensagens)
            </h2>
            <span style="font-size: 0.82rem; color: var(--text-muted);">Filtre por produto, período (dia/histórico) e analise saídas e rupturas</span>
          </div>
        </div>

        <!-- BARRA DE FILTROS INTERATIVOS -->
        <div style="background: rgba(14, 20, 34, 0.6); padding: 0.85rem 1rem; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08); margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; justify-content: space-between;">
          <!-- Filtro de Período -->
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <span style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Período:</span>
            <div class="filter-pill-group" style="display: flex; gap: 4px;">
              <button class="filter-btn" data-period="today" onclick="setAnalyticsPeriod('today', this)">Hoje</button>
              <button class="filter-btn" data-period="7d" onclick="setAnalyticsPeriod('7d', this)">7 Dias</button>
              <button class="filter-btn" data-period="30d" onclick="setAnalyticsPeriod('30d', this)">30 Dias</button>
              <button class="filter-btn active" data-period="all" onclick="setAnalyticsPeriod('all', this)">Histórico Completo</button>
            </div>
          </div>

          <!-- Filtro de Categoria -->
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <span style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Peça:</span>
            <div class="filter-pill-group" style="display: flex; gap: 4px;">
              <button class="filter-btn active" data-cat="all" onclick="setAnalyticsCategory('all', this)">Todas</button>
              <button class="filter-btn" data-cat="tela" onclick="setAnalyticsCategory('tela', this)">Telas</button>
              <button class="filter-btn" data-cat="touch" onclick="setAnalyticsCategory('touch', this)">Touch</button>
              <button class="filter-btn" data-cat="bateria" onclick="setAnalyticsCategory('bateria', this)">Baterias</button>
            </div>
          </div>

          <!-- Busca por Modelo -->
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-grow: 1; min-width: 200px; max-width: 320px;">
            <input type="text" id="analytics-search-input" placeholder="Filtrar por modelo (ex: M8, T295, A15)..." oninput="debounceAnalyticsSearch()" style="width: 100%; padding: 0.42rem 0.75rem; font-size: 0.82rem; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.14); border-radius: 8px; color: #fff;">
          </div>
        </div>

        <!-- ATALHOS RÁPIDOS (CHIPS DE MODELOS POPULARES) -->
        <div style="display: flex; align-items: center; gap: 0.45rem; flex-wrap: wrap; margin-bottom: 1.25rem;">
          <span style="font-size: 0.72rem; color: #64748B; font-weight: 600;">Modelos Populares:</span>
          <button class="quick-chip-btn" onclick="quickFilterModel('M8')">Multilaser M8</button>
          <button class="quick-chip-btn" onclick="quickFilterModel('T295')">Samsung Tab A 8.0 (T295)</button>
          <button class="quick-chip-btn" onclick="quickFilterModel('T2040')">Positivo T2040</button>
          <button class="quick-chip-btn" onclick="quickFilterModel('IPAD 9')">iPad 9ª Geração</button>
          <button class="quick-chip-btn" onclick="quickFilterModel('TAB S6')">Tab S6 Lite</button>
          <button class="quick-chip-btn" onclick="quickFilterModel('VISION TAB 7')">Positivo Vision Tab 7</button>
          <button class="quick-chip-btn" onclick="quickFilterModel('A15')">Samsung A15</button>
          <button class="quick-chip-btn" onclick="quickFilterModel('')" style="color: #F87171; border-color: rgba(239, 68, 68, 0.3);">Limpar Filtro</button>
        </div>

        <!-- 4 KPIS DO FUNIL DE WHATSAPP -->
        <div class="kpis-grid" style="grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); margin-bottom: 1.25rem;">
          <div class="kpi-card">
            <div class="kpi-label">Pedidos que Saíram (Fechados)</div>
            <div class="kpi-value" style="color: #10B981;" id="kpi-chat-closed">58</div>
            <div class="kpi-subtext" style="color: #34D399;">Taxa de conversão: <strong id="kpi-chat-conv-rate">34.3%</strong></div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Perdidos por Falta de Estoque</div>
            <div class="kpi-value" style="color: #EF4444;" id="kpi-chat-lost">111</div>
            <div class="kpi-subtext" style="color: #F87171;">Demanda reprimida (Ruptura no balcão)</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Taxa de Recorrência (Recompra)</div>
            <div class="kpi-value" style="color: #818CF8;" id="kpi-chat-recurrence">81.1%</div>
            <div class="kpi-subtext" style="color: #A5B4FC;"><strong id="kpi-chat-workshops">30 de 37</strong> oficinas voltam a pedir</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Cotações Mineradas no Zap</div>
            <div class="kpi-value" style="color: #F59E0B;" id="kpi-chat-volume">984</div>
            <div class="kpi-subtext" style="color: #FCD34D;">58 modelos de tablet monitorados</div>
          </div>
        </div>

        <!-- GRÁFICOS 1 & 2: PRODUTOS MAIS SAÍDOS E LINHA DO TEMPO POR DIA -->
        <div class="charts-grid" style="margin-bottom: 1.25rem;">
          <div class="chart-card">
            <h3 style="display: flex; align-items: center; gap: 6px;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #38BDF8;"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>
              Produtos que Mais Saíram no Período Selecionado
            </h3>
            <canvas id="chartTopProductsPeriod" height="200"></canvas>
          </div>
          <div class="chart-card">
            <h3 style="display: flex; align-items: center; gap: 6px;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #F59E0B;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
              Evolução das Saídas por Dia (Linha do Tempo)
            </h3>
            <canvas id="chartDailyTimeline" height="200"></canvas>
          </div>
        </div>

        <!-- GRÁFICOS 3 & 4: FUNIL E RECORRÊNCIA -->
        <div class="charts-grid" style="margin-bottom: 1.25rem;">
          <div class="chart-card">
            <h3 style="display: flex; align-items: center; gap: 6px;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #10B981;"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
              Desfecho das Cotações (Pedidos que Saíram vs Perdidos)
            </h3>
            <canvas id="chartChatFunnel" height="200"></canvas>
          </div>
          <div class="chart-card">
            <h3 style="display: flex; align-items: center; gap: 6px;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #818CF8;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
              Top Assistências por Recorrência de Pedidos
            </h3>
            <canvas id="chartRecurrence" height="200"></canvas>
          </div>
        </div>

        <!-- TABELA DE RUPTURAS CRÍTICAS -->
        <div style="margin-top: 1rem;">
          <h4 style="font-size: 0.88rem; font-weight: 700; color: #F87171; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 6px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
            Peças Mais Cotadas Perdidas por Falta de Estoque (Demanda Reprimida para Repor)
          </h4>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Modelo de Tablet / Peça</th>
                  <th>Cotações Perdidas</th>
                  <th>Status no WhatsApp</th>
                  <th>Ação Recomendada de Compra</th>
                </tr>
              </thead>
              <tbody id="lost-stock-tbody">
                <tr><td colspan="4" style="text-align: center; padding: 1rem; color: var(--text-muted);">Carregando métricas de demanda...</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <h3>⚖️ Mix de Vendas: Original vs. Paralela</h3>
          <canvas id="chartQuality" height="200"></canvas>
        </div>
        <div class="chart-card">
          <h3>Distribuição por Categoria</h3>
          <canvas id="chartCategory" height="200"></canvas>
        </div>
      </div>

      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">Peças Mais Demandadas na Bancada</h2>
          </div>
        </div>
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Posição</th>
                <th>Peça / Descrição</th>
                <th>Qualidade</th>
                <th>Qtd Vendida</th>
                <th>Faturamento Total</th>
              </tr>
            </thead>
            <tbody id="top-products-tbody">
              <tr><td colspan="5" style="text-align: center; padding: 1.5rem; color: var(--text-muted);">Carregando ranking...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: ESTOQUE GOOGLE SHEETS -->
    <div class="tab-pane" id="tab-catalog">
      <!-- GOOGLE SHEETS LIVE BANNER & CONTROLS -->
      <div class="section-card" style="margin-bottom: 1.25rem; background: linear-gradient(135deg, rgba(14, 20, 34, 0.95), rgba(16, 185, 129, 0.08)); border-color: rgba(16, 185, 129, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 0.25rem;">
          <div style="display: flex; align-items: center; gap: 0.85rem;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0;">

            </div>
            <div>
              <h3 style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                Planilha do Google Sheets • Estoque & Preços
                <span style="font-size: 0.7rem; background: rgba(16, 185, 129, 0.2); color: #34D399; padding: 2px 8px; border-radius: 999px; font-weight: 600;">Conectada ao Robô</span>
              </h3>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                Esta planilha é a fonte oficial do estoque. Qualquer peça, valor ou quantidade que você alterar nela é lida pelo robô do WhatsApp em tempo real.
              </p>
            </div>
          </div>
          <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
            <a href="https://docs.google.com/spreadsheets/d/1N2gigR8MmuiBRSbtO1TDLnS9AFQS3dJYhxYEEUs7kZY/edit" target="_blank" class="btn btn-primary btn-sm" style="text-decoration: none; font-weight: 700; background: #10B981; color: #042F2E;">
              Abrir no Google Sheets ↗
            </a>
            <button class="btn btn-secondary btn-sm" onclick="syncGoogleSheets()">
              ⚡ Sincronizar Agora
            </button>
            <button class="btn btn-secondary btn-sm" id="btn-toggle-sheet-view" onclick="toggleSheetView()">
              Visualizar Planilha
            </button>
          </div>
        </div>

        <!-- IFRAME EMBED DA PLANILHA (TOGGLE) -->
        <div id="sheet-embed-container" style="display: none; margin-top: 1.25rem; border-top: 1px solid var(--border-subtle); padding-top: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span style="font-size: 0.8rem; color: var(--text-muted);">Visualização oficial das células do Google Sheets (Aba: <strong>Estoque</strong>):</span>
            <a href="https://docs.google.com/spreadsheets/d/1N2gigR8MmuiBRSbtO1TDLnS9AFQS3dJYhxYEEUs7kZY/edit" target="_blank" style="font-size: 0.75rem; color: #34D399; text-decoration: none;">Editar Células ↗</a>
          </div>
          <iframe src="https://docs.google.com/spreadsheets/d/1N2gigR8MmuiBRSbtO1TDLnS9AFQS3dJYhxYEEUs7kZY/preview?widget=true&headers=false" style="width: 100%; height: 480px; border: 1px solid var(--border-subtle); border-radius: 10px; background: #ffffff;"></iframe>
        </div>
      </div>

      <!-- KPIS RÁPIDOS DO INVENTÁRIO -->
      <div class="kpi-grid" style="margin-bottom: 1.25rem;">
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: rgba(59, 130, 246, 0.15); color: #60A5FA;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></div>
          <div class="kpi-body">
            <div class="kpi-label">Total de Peças Ativas</div>
            <div class="kpi-value" id="kpi-catalog-total">0</div>
            <div class="kpi-sub">Sincronizadas com Google Sheets</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: rgba(16, 185, 129, 0.15); color: #34D399;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg></div>
          <div class="kpi-body">
            <div class="kpi-label">Disponíveis em Balcão</div>
            <div class="kpi-value" id="kpi-catalog-healthy" style="color: #34D399;">0</div>
            <div class="kpi-sub">Pronta entrega imediata</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: rgba(239, 68, 68, 0.15); color: #F87171;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg></div>
          <div class="kpi-body">
            <div class="kpi-label">Esgotadas em Loja</div>
            <div class="kpi-value" id="kpi-catalog-out">0</div>
            <div class="kpi-sub">Peças Esgotadas (Sem Saldo)</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: rgba(245, 158, 11, 0.15); color: #FBBF24;"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
          <div class="kpi-body">
            <div class="kpi-label">Overbooking Bloqueado</div>
            <div class="kpi-value" id="kpi-overbooking-blocked" style="color: #FBBF24;">0</div>
            <div class="kpi-sub">Proteção transacional ativa</div>
          </div>
        </div>
      </div>

      <!-- TABELA DINÂMICA DE PEÇAS & FILTROS -->
      <div class="section-card">
        <div class="section-toolbar" style="flex-direction: column; align-items: stretch; gap: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
            <div class="section-title-group">
              <h2 class="section-title">Catálogo de Peças</h2>
              <span class="badge-count" id="catalog-counter">0 peças</span>
            </div>
            <div class="toolbar-actions" style="gap: 0.5rem;">
              <input type="text" id="catalog-search" placeholder="Buscar por nome, modelo (ex: P615, A15), SKU..." class="search-input" oninput="filterCatalogTable()" style="min-width: 260px; background: rgba(0,0,0,0.3); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 0.45rem 0.75rem; color: #fff; font-size: 0.85rem;">
              <button class="btn btn-secondary btn-sm" onclick="fetchCatalog()"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -1px; margin-right: 4px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Atualizar</button>
            </div>
          </div>

          <!-- CHIPS DE FILTRO RÁPIDO (MARCAS & CATEGORIAS) -->
          <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; padding-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.06);">
            <div style="display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap;">
              <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; margin-right: 0.25rem;">Marca:</span>
              <button class="catalog-filter-btn active" data-filter-type="brand" data-filter-val="all" onclick="setBrandFilter('all', this)">Todas</button>
              <button class="catalog-filter-btn" data-filter-type="brand" data-filter-val="samsung" onclick="setBrandFilter('samsung', this)">Samsung (Galaxy/Tab)</button>
              <button class="catalog-filter-btn" data-filter-type="brand" data-filter-val="motorola" onclick="setBrandFilter('motorola', this)">Motorola</button>
              <button class="catalog-filter-btn" data-filter-type="brand" data-filter-val="xiaomi" onclick="setBrandFilter('xiaomi', this)">Xiaomi / Redmi</button>
              <button class="catalog-filter-btn" data-filter-type="brand" data-filter-val="apple" onclick="setBrandFilter('apple', this)">Apple / iPhone</button>
            </div>
            <div style="display: flex; align-items: center; gap: 0.35rem; flex-wrap: wrap;">
              <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; margin-right: 0.25rem;">Categoria:</span>
              <button class="catalog-filter-btn active" data-filter-type="cat" data-filter-val="all" onclick="setCatFilter('all', this)">Todas</button>
              <button class="catalog-filter-btn" data-filter-type="cat" data-filter-val="tela" onclick="setCatFilter('tela', this)">Telas Frontais</button>
              <button class="catalog-filter-btn" data-filter-type="cat" data-filter-val="bateria" onclick="setCatFilter('bateria', this)">Baterias</button>
              <button class="catalog-filter-btn" data-filter-type="cat" data-filter-val="conector" onclick="setCatFilter('conector', this)">Conectores de Carga</button>
            </div>
          </div>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Peça / Modelos Compatíveis</th>
                <th>Categoria</th>
                <th>Aro</th>
                <th>Qualidade</th>
                <th>Preço</th>
                <th>Estoque em Loja</th>
              </tr>
            </thead>
            <tbody id="catalog-tbody">
              <tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Carregando catálogo...</td></tr>
            </tbody>
          </table>
        </div>

        <div class="mobile-card-deck" id="catalog-cards-mobile"></div>
      </div>
    </div>

    <!-- TAB ERP: ESTOQUE NATIVO & ENTRADA COGNITIVA COM IA -->
    <div class="tab-pane" id="tab-erp">
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-header">
          <div class="card-title-group">
            <div class="card-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="22"/></svg>
            </div>
            <div>
              <div class="card-title">Entrada Rápida de Estoque com IA (Voz & OCR)</div>
              <div class="card-subtitle">Fale no microfone ou envie foto da etiqueta do fornecedor para extração automática</div>
            </div>
          </div>
          <div>
            <button class="btn btn-emerald" onclick="openNewProductModal()"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="vertical-align: -2px; margin-right: 4px;"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg> + Nova Peça no Estoque</button>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-top: 1rem;">
          <!-- Entrada por Voz -->
          <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 8px; padding: 1rem;">
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
              Entrada por Voz ou Ditado do Balcão
            </div>
            <textarea id="erp-voice-input" rows="3" style="width: 100%; background: #0c0f17; border: 1px solid var(--border); color: #fff; padding: 0.6rem; border-radius: 6px; font-size: 0.85rem; resize: vertical;" placeholder="Ex: Entraram 10 telas do Tab A8 a 110 do fornecedor Peças Brasil e 5 conectores do T295 a 15, NF 4580..."></textarea>
            <div style="display: flex; gap: 0.5rem; margin-top: 0.75rem;">
              <button class="btn btn-primary" onclick="submitVoiceStockEntry()" id="btn-process-voice" style="font-size: 0.85rem;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                Processar com IA
              </button>
              <button class="btn btn-secondary" onclick="demoVoiceStockEntry()" style="font-size: 0.85rem;">
                Exemplo Rápido
              </button>
            </div>
          </div>

          <!-- Entrada por Foto / OCR -->
          <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: 8px; padding: 1rem;">
            <div style="font-weight: 600; font-size: 0.9rem; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
              Foto da Etiqueta / Código de Barras (OCR)
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">
              Selecione a foto da embalagem ou etiqueta do lote de peças recebido:
            </div>
            <input type="file" id="erp-photo-input" accept="image/*" style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem; width: 100%;" />
            <button class="btn btn-secondary" onclick="submitOcrStockEntry()" id="btn-process-ocr" style="font-size: 0.85rem;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              Ler Etiqueta com IA
            </button>
          </div>
        </div>

        <!-- Área de Conferência Humana -->
        <div id="erp-proposal-card" style="display: none; margin-top: 1.25rem; background: rgba(37, 211, 102, 0.05); border: 1px solid rgba(37, 211, 102, 0.2); border-radius: 8px; padding: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div style="font-weight: 600; font-size: 0.95rem; color: var(--success); display: flex; align-items: center; gap: 0.5rem;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              Proposta de Entrada Pré-Preenchida pela IA (Conferência Humana)
            </div>
            <button class="btn btn-primary" onclick="confirmCurrentStockEntry()" id="btn-confirm-stock" style="background: var(--success); border-color: var(--success); font-size: 0.85rem;">
              Confirmar Entrada no Estoque
            </button>
          </div>
          <div id="erp-proposal-details" style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.75rem;"></div>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Modelo</th>
                  <th>Categoria</th>
                  <th>Qtd Entrada</th>
                  <th>Estoque Atual</th>
                  <th>Estoque Pós</th>
                  <th>Custo Unit.</th>
                  <th>Preço Sugerido</th>
                </tr>
              </thead>
              <tbody id="erp-proposal-tbody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- CARDS DE BALANÇO E MÉTRICAS DO ERP -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="stat-card">
          <div class="stat-label">Total de SKUs</div>
          <div class="stat-value" id="erp-total-skus">-</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total de Unidades Físicas</div>
          <div class="stat-value" id="erp-total-units">-</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Custo Total Imobilizado</div>
          <div class="stat-value" id="erp-total-cost" style="color: var(--primary);">-</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Faturamento Projetado</div>
          <div class="stat-value" id="erp-total-retail" style="color: var(--success);">-</div>
        </div>
      </div>

      <!-- TABELA DE MOVIMENTAÇÕES FISCAIS / HISTÓRICO -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">Extrato de Movimentações Físicas (Rastreabilidade e-Gov / SPED)</div>
          <button class="btn btn-secondary" onclick="loadErpMovements()" style="font-size: 0.8rem;">
            Atualizar Extrato
          </button>
        </div>
        <div class="table-responsive">
          <table class="data-table">
            <thead>
              <tr>
                <th>Data/Hora</th>
                <th>Tipo</th>
                <th>SKU</th>
                <th>Qtd</th>
                <th>Custo</th>
                <th>Lote / NF</th>
                <th>Operador</th>
                <th>Observações</th>
              </tr>
            </thead>
            <tbody id="erp-movements-tbody">
              <tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding: 1.5rem;">Carregando extrato de movimentações...</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 5: COPILOTO IA DO GESTOR (BUSINESS INTELLIGENCE) -->
    <div class="tab-pane" id="tab-copilot">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">Consultor Executivo • Inteligência Victor Cell</h2>
            <p class="section-subtitle">Inteligência analítica em tempo real integrada a vendas, estoque e movimentação do balcão.</p>
          </div>
          <div class="toolbar-actions">
            <div class="pill pill-emerald">
              <span class="pill-dot"></span>
              <span>Análise Operacional Conectada</span>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="clearCopilotChat()">Limpar Conversa</button>
          </div>
        </div>

        <div style="padding: 1.25rem;">
          <!-- CHIPS DE PERGUNTAS RÁPIDAS -->
          <div class="quick-chips-wrapper">
            <span class="chips-label">Consultas Rápidas:</span>
            <div class="chips-scroller">
              <button class="chip-btn" onclick="sendQuickPrompt('Faça um resumo executivo direto e conciso de hoje: faturamento, pedidos, estoque e a principal ação.')">Resumo do Dia</button>
              <button class="chip-btn" onclick="sendQuickPrompt('Quais peças precisam de reposição urgente? Responda de forma direta e concisa.')">Estoque & Reposição</button>
              <button class="chip-btn" onclick="sendQuickPrompt('Como foi o volume e faturamento de vendas hoje? Seja direto.')">Volume de Vendas</button>
              <button class="chip-btn" onclick="sendQuickPrompt('Qual a situação das entregas via Uber Flash hoje? Seja direto.')">Entregas Uber Flash</button>
              <button class="chip-btn" onclick="sendQuickPrompt('Qual o status rápido dos atendimentos no WhatsApp agora? Quantos estão com humanos?')">Atendimentos no Balcão</button>
              <button class="chip-btn" onclick="sendQuickPrompt('Qual a principal ação prática para aumentar as vendas amanhã? Seja direto e objetivo.')">Ação para Vender Mais</button>
            </div>
          </div>

          <!-- ÁREA DO CHAT COPILOTO -->
          <div class="copilot-chat-container">
            <div class="copilot-messages" id="copilot-messages">
              <div class="copilot-msg bot">
                <div class="copilot-avatar">✦</div>
                <div class="copilot-bubble">
                  <p><strong>Consultor Estratégico Victor Cell</strong></p>
                  <p>Painel de inteligência de negócios ativo. Monitoro em tempo real o fluxo financeiro, pedidos confirmados, logística via Uber Flash e níveis de estoque para subsidiar decisões táticas.</p>
                  <p style="margin-top: 0.5rem; font-size: 0.85rem; color: #9CA3AF;">Selecione uma das consultas executivas acima ou insira uma diretriz no campo abaixo para gerar um relatório analítico.</p>
                </div>
              </div>
            </div>

            <!-- BARRA DE INPUT -->
            <div class="copilot-input-bar">
              <input type="text" id="copilot-input" class="copilot-input-field" placeholder="Pergunte sobre vendas, peças em falta, Uber Flash ou balcão..." onkeydown="if(event.key==='Enter') sendCopilotMessage()">
              <button class="btn btn-primary" id="copilot-send-btn" onclick="sendCopilotMessage()">
                <span>Enviar</span>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 6: GOOGLE GEMINI & COTAS -->
    <div class="tab-pane" id="tab-gemini">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">⚡ Capacidade Operacional do Motor de Atendimento</h2>
          </div>
        </div>

        <div style="padding: 1.25rem;">
          <!-- PIPELINE MULTIMODAL DE IA EM TEMPO REAL & CONSUMO REAL (SQLITE) -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
            <!-- Card 1: Consumo Real Dinâmico -->
            <div class="pipeline-card" style="border-left: 3px solid #10B981;">
              <div class="pipeline-card-title">
                <span>Consumo Real de Requisições</span>
                <span class="pill pill-emerald" style="font-size: 0.65rem;">SQLite Vivo</span>
              </div>
              <div style="font-size: 1.7rem; font-weight: 800; color: #34D399; font-family: var(--font-mono);" id="ai-real-requests">-- req / dia</div>
              <div style="background: rgba(255,255,255,0.08); height: 8px; border-radius: 999px; overflow: hidden;">
                <div id="ai-quota-bar" style="width: 2%; height: 100%; background: #10B981; transition: width 0.3s ease;"></div>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.725rem; color: var(--text-dim);" id="ai-quota-subtext">
                <span>Calculado dinamicamente</span>
                <span id="ai-quota-pct">0% da cota</span>
              </div>
            </div>

            <!-- Card 2: Conversação & Atendimento -->
            <div class="pipeline-card" style="border-left: 3px solid #6366F1;">
              <div class="pipeline-card-title">
                <span>Motor de Conversação</span>
                <span class="pill pill-indigo" style="font-size: 0.65rem;" id="ai-model-convo">Gemini 2.5 Flash</span>
              </div>
              <div class="pipeline-endpoint" id="ai-endpoint-convo">/v1beta/models/gemini-2.5-flash:generateContent</div>
              <div class="pipeline-fallback">
                <span>Fallback:</span> <strong style="color: #A5B4FC;" id="ai-fallback-convo">Gemini 1.5 Pro + Fast FAQ Cache</strong>
              </div>
            </div>

            <!-- Card 3: Áudio e Visão OCR -->
            <div class="pipeline-card" style="border-left: 3px solid #F59E0B;">
              <div class="pipeline-card-title">
                <span>Multimodal (Voz & OCR)</span>
                <span class="pill pill-amber" style="font-size: 0.65rem;">Nativo</span>
              </div>
              <div class="pipeline-endpoint">Áudio: Multimodal OGG / Foto: Vision JPEG</div>
              <div class="pipeline-fallback">
                <span>Circuit Breaker:</span> <strong style="color: #34D399;" id="ai-circuit-status">OPERACIONAL (0 falhas)</strong>
              </div>
            </div>
          </div>

          <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1.25rem;">
            <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 0.85rem;">Chave de Acesso API Google AI Studio</h3>
            <div style="display: flex; gap: 0.5rem; max-width: 600px; flex-wrap: wrap;">
              <input type="password" id="gemini-key-input" class="search-input" style="flex: 1; min-width: 260px;" placeholder="Cole sua nova chave AIzaSy...">
              <button class="btn btn-primary" onclick="saveGeminiKey()">Salvar Chave</button>
            </div>
          </div>
        </div>
      </div>
      <!-- SIMULADOR DE TESTE INTEGRADO AO GEMINI -->
      <div style="margin-top: 1.5rem;">


      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">Simulador de Atendimento WhatsApp</h2>
          </div>
          <div class="toolbar-actions">
            <button class="btn btn-secondary btn-sm" onclick="clearChat()">Limpar Conversa</button>
          </div>
        </div>

        <div style="padding: 1.25rem;">
          <div class="simulator-wrapper">
            <div class="chat-box">
              <div class="chat-messages" id="chat-messages">
                <div class="chat-msg bot">
                  Opa meu patrão! Tudo beleza? Aqui é da Victor Cell Peças. Pode mandar sua dúvida ou cotação de tela/peça que já vejo no estoque pra você!
                </div>
              </div>
              <div class="chat-input-bar">
                <input type="text" id="chat-input" class="search-input" style="flex: 1;" placeholder="Digite como cliente (ex: 'Tem a tela do A15 original?')..." onkeydown="if(event.key==='Enter') sendChatMessage()">
                <button class="btn btn-emerald" onclick="sendChatMessage()">Enviar</button>
              </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
              <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1rem;">
                <h4 style="font-size: 0.85rem; color: #fff; margin-bottom: 0.5rem;">Cenários de Teste de Balcão:</h4>
                <ul style="font-size: 0.775rem; color: var(--text-muted); padding-left: 1.1rem; line-height: 1.6;">
                  <li><strong>Cotação:</strong> "Quanto tá a tela do A15 com aro?"</li>
                  <li><strong>Pós-Venda / Rastreio:</strong> "E aí amigo, o Uber já saiu com a minha peça?"</li>
                  <li><strong>Memória de Ontem:</strong> "Lembra da tela que perguntei ontem? Quanto é mesmo?"</li>
                  <li><strong>Negociação:</strong> "Faz por R$ 150 no Pix?" (Aciona alerta de humano)</li>
                </ul>
              </div>

              <!-- Conexão WhatsApp Card -->
              <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1rem;">
                <h4 style="font-size: 0.85rem; color: #fff; margin-bottom: 0.5rem;">Conexão WhatsApp (Evolution API)</h4>
                <div id="wa-qr-container" style="text-align: center; padding: 0.5rem;">
                  <div style="font-size: 0.8rem; color: var(--text-muted);">Verificando instância...</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      </div>

    </div>


    <!-- TAB 7: AUDITORIA & OBSERVABILIDADE TÉCNICA -->
    <div class="tab-pane" id="tab-audit">
      <div class="card" style="margin-bottom: 1.25rem;">
        <div class="card-header" style="flex-wrap: wrap; gap: 0.75rem;">
          <div>
            <div class="card-title" style="display: flex; align-items: center; gap: 0.5rem;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary);"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>
              <span>Trilha de Auditoria & Observabilidade de Sistema</span>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
              Registro imutável de todas as decisões cognitivas, alertas de equipe, despachos e alterações cadastrais.
            </p>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <button class="btn-refresh" onclick="fetchAuditLogs()" title="Atualizar Logs">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              Atualizar
            </button>
          </div>
        </div>

        <!-- FILTROS DE AUDITORIA -->
        <div class="audit-toolbar" style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; padding: 0.75rem 1rem; background: rgba(0,0,0,0.2); border-radius: var(--radius-sm); margin-top: 0.5rem;">
          <div class="level-pills" style="display: flex; gap: 0.4rem;">
            <button class="pill-btn active" data-level="" onclick="filterAuditLevel('', this)">Todos</button>
            <button class="pill-btn pill-info" data-level="INFO" onclick="filterAuditLevel('INFO', this)">INFO</button>
            <button class="pill-btn pill-warn" data-level="WARN" onclick="filterAuditLevel('WARN', this)">WARN</button>
            <button class="pill-btn pill-error" data-level="ERROR" onclick="filterAuditLevel('ERROR', this)">ERROR</button>
          </div>

          <div style="flex: 1; min-width: 180px;">
            <input type="text" id="search-audit" class="search-input" placeholder="Buscar por ação, ator ou detalhe..." oninput="debounceAuditSearch()" style="width: 100%; padding: 0.45rem 0.8rem; font-size: 0.8rem; border-radius: 6px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div>
            <select id="select-audit-component" onchange="fetchAuditLogs()" style="padding: 0.45rem 0.8rem; font-size: 0.8rem; border-radius: 6px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
              <option value="">Todos os Componentes</option>
              <option value="AI_ENGINE">AI_ENGINE</option>
              <option value="ROUTER">ROUTER</option>
              <option value="NOTIFIER">NOTIFIER</option>
              <option value="REPO">REPO</option>
              <option value="ADMIN">ADMIN</option>
              <option value="ERP_SYNC">ERP_SYNC</option>
            </select>
          </div>
        </div>

        <!-- TABELA DE LOGS (DESKTOP) -->
        <div class="table-container" style="margin-top: 1rem;">
          <table class="audit-table">
            <thead>
              <tr>
                <th style="width: 140px;">Timestamp</th>
                <th style="width: 80px;">Nível</th>
                <th style="width: 110px;">Componente</th>
                <th style="width: 190px;">Ação</th>
                <th style="width: 130px;">Ator</th>
                <th style="width: 80px;">Latência</th>
                <th>Detalhes & Payload</th>
              </tr>
            </thead>
            <tbody id="audit-table-body">
              <tr>
                <td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                  Carregando trilha de auditoria...
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- LISTA EM CARDS PARA MOBILE -->
        <div class="mobile-cards-container" id="audit-cards-body" style="margin-top: 1rem;">
        </div>
      </div>
    </div>

    <!-- TAB 8: PERFIL DA LOJA & DIRETRIZES COMERCIAIS (WHITELABEL) -->
    <div class="tab-pane" id="tab-profile">
      <div class="card" style="margin-bottom: 1.25rem;">
        <div class="card-header">
          <div>
            <div class="card-title" style="display: flex; align-items: center; gap: 0.5rem;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary);"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              <span>Diretrizes Comerciais & Identidade da Loja</span>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
              Personalize o nome da empresa, polo regional, regras de escopo e mensagens da IA sem reiniciar a API.
            </p>
          </div>
        </div>

        <form id="profile-form" onsubmit="saveStoreProfile(event)" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.25rem; margin-top: 1rem;">
          <div class="form-group">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Nome da Loja / Tenant</label>
            <input type="text" id="prof-store-name" required class="input-styled" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Cidade e Estado (Polo Regional)</label>
            <input type="text" id="prof-city" required class="input-styled" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group" style="grid-column: 1 / -1;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Nicho de Atuação da Loja</label>
            <input type="text" id="prof-niche" required class="input-styled" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group" style="grid-column: 1 / -1;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Palavras-Chave Fora de Escopo (separadas por vírgula)</label>
            <input type="text" id="prof-keywords" required class="input-styled" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
            <span style="font-size: 0.725rem; color: var(--text-dim); margin-top: 0.25rem; display: block;">Exemplo: iphone, celular, smartphone, capinha, película</span>
          </div>

          <div class="form-group" style="grid-column: 1 / -1;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Mensagem Padrão de Recusa Polida (1 a 6 palavras)</label>
            <input type="text" id="prof-rejection" required class="input-styled" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group" style="grid-column: 1 / -1;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Modalidades de Despacho Aceitas (separadas por vírgula)</label>
            <input type="text" id="prof-delivery" required class="input-styled" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group" style="grid-column: 1 / -1;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Diretrizes de Tom e Postura da IA</label>
            <textarea id="prof-tone" rows="3" class="input-styled" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: inherit; font-size: 0.85rem; resize: vertical;"></textarea>
          </div>

          <div style="grid-column: 1 / -1; display: flex; justify-content: flex-end; gap: 0.75rem;">
            <button type="submit" class="btn-refresh" style="background: var(--primary); color: white; padding: 0.65rem 1.5rem; border-radius: 8px; font-weight: 600;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
              Salvar Diretrizes Comerciais
            </button>
          </div>
        </form>

        <!-- EXEMPLOS CANÔNICOS DE TOM DE BALCÃO (GOLDEN DIALOGUES - 36 CONVERSAS MINERADAS) -->
        <div style="margin-top: 1.5rem; padding-top: 1.25rem; border-top: 1px solid var(--border-subtle);">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.85rem;">
            <div>
              <h4 style="font-size: 0.92rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #F59E0B;"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                Padrões Canônicos de Tom de Balcão (Golden Dialogues das 36 Conversas Reais)
              </h4>
              <p style="font-size: 0.775rem; color: var(--text-muted); margin-top: 2px;">
                A IA é calibrada estritamente com estes diálogos reais de assistências técnicas do Centro de Fortaleza.
              </p>
            </div>
            <span class="badge-count">Calibrado com 36 chats</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
            <!-- Exemplo 1: Cotação Direta -->
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 1rem;">
              <div style="font-size: 0.75rem; font-weight: 700; color: #34D399; text-transform: uppercase; margin-bottom: 0.5rem;">Cenário 1: Cotação com Preço e Aro</div>
              <div style="font-size: 0.775rem; color: #94A3B8; margin-bottom: 0.35rem;"><strong>Cliente:</strong> "bom dia amigo tem tela do moto g22?"</div>
              <div style="font-size: 0.775rem; color: #F0FDF4; background: rgba(16, 185, 129, 0.1); padding: 0.5rem 0.65rem; border-radius: 6px; border-left: 2px solid #10B981;">
                <strong>Victor Cell:</strong> "Bom dia amigo! Temos sim, primeira linha com aro por R$ 130 à vista no Pix. Quer que separe pro motoboy buscar ou você vem retirar no balcão?"
              </div>
            </div>

            <!-- Exemplo 2: Ruptura com Alternativa -->
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 1rem;">
              <div style="font-size: 0.75rem; font-weight: 700; color: #FBBF24; text-transform: uppercase; margin-bottom: 0.5rem;">Cenário 2: Peça sem Estoque (Ruptura c/ Alternativa)</div>
              <div style="font-size: 0.775rem; color: #94A3B8; margin-bottom: 0.35rem;"><strong>Cliente:</strong> "tem tela a15 original nacional?"</div>
              <div style="font-size: 0.775rem; color: #FFFBEB; background: rgba(245, 158, 11, 0.1); padding: 0.5rem 0.65rem; border-radius: 6px; border-left: 2px solid #F59E0B;">
                <strong>Victor Cell:</strong> "A original esgotou hoje cedo amigo. Mas tenho a primeira linha premium com garantia por R$ 140. Separo uma pra você?"
              </div>
            </div>

            <!-- Exemplo 3: Domingo / Fechado (Zero Parênteses) -->
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-subtle); border-radius: 10px; padding: 1rem;">
              <div style="font-size: 0.75rem; font-weight: 700; color: #818CF8; text-transform: uppercase; margin-bottom: 0.5rem;">Cenário 3: Domingo / Fora de Horário (Zero Parênteses)</div>
              <div style="font-size: 0.775rem; color: #94A3B8; margin-bottom: 0.35rem;"><strong>Cliente:</strong> "boa tarde tá funcionando hoje?"</div>
              <div style="font-size: 0.775rem; color: #EEF2FF; background: rgba(99, 102, 241, 0.1); padding: 0.5rem 0.65rem; border-radius: 6px; border-left: 2px solid #6366F1;">
                <strong>Victor Cell:</strong> "Fechado hoje domingo, abrimos amanhã às 08:00 no centro. Deixe a peça que você precisa anotada que logo cedo respondemos sua cotação!"
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>


    <!-- CHAT DRAWER LATERAL (ATENDIMENTO WHATSAPP AO VIVO) -->
    <div id="drawer-chat-overlay" class="drawer-overlay" onclick="closeChatDrawer()"></div>
    <div id="drawer-chat" class="chat-drawer">
      <div class="chat-drawer-header">
        <div class="user-profile">
          <div class="user-avatar" id="drawer-avatar">CL</div>
          <div class="user-info">
            <span class="user-name" id="drawer-name">Cliente WhatsApp</span>
            <span class="user-phone" id="drawer-phone">--</span>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="status-pill status-robot" id="drawer-status-pill">IA Ativa</span>
          <button class="drawer-close-btn" onclick="closeChatDrawer()" aria-label="Fechar">✕</button>
        </div>
      </div>
      <div class="chat-drawer-body" id="drawer-messages">
        <div style="text-align: center; padding: 2rem; color: var(--text-muted);">Carregando histórico...</div>
      </div>
      <div class="chat-drawer-footer">
        <button class="btn btn-amber btn-sm" id="drawer-action-btn" onclick="toggleDrawerConversationMode()">⏸️ Assumir Atendimento</button>
        <a href="#" target="_blank" id="drawer-wa-link" class="btn btn-secondary btn-sm">Abrir no Zap ↗</a>
      </div>
    </div>

    <!-- MODAL VTEX ADMIN: CADASTRAR NOVA PEÇA NO ESTOQUE (ERP NATIVO) -->
    <div id="modal-new-product" class="vtex-modal-overlay">
      <div class="vtex-modal">
        <div class="vtex-modal-header">
          <div class="vtex-modal-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: var(--vtex-pink);"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
            <span>Cadastrar Nova Peça no Estoque (ERP Nativo)</span>
          </div>
          <button class="drawer-close-btn" onclick="closeNewProductModal()">✕</button>
        </div>
        <form id="form-new-product" onsubmit="submitNewProduct(event)" class="vtex-modal-body">
          <div class="vtex-form-grid">
            <div class="vtex-form-group col-span-2">
              <label>SKU / Código Único *</label>
              <input type="text" id="np-sku" required placeholder="Ex: TELA-MOTO-G22-PRETA" style="font-family: var(--font-mono);">
            </div>
            <div class="vtex-form-group col-span-2">
              <label>Modelo Compatível & Descrição *</label>
              <input type="text" id="np-model" required placeholder="Ex: Motorola Moto G22 (XT2231)">
            </div>
            <div class="vtex-form-group">
              <label>Categoria *</label>
              <select id="np-category" required>
                <option value="Telas Frontais">Telas Frontais</option>
                <option value="Baterias">Baterias</option>
                <option value="Conectores de Carga">Conectores de Carga</option>
                <option value="Tampas Traseiras">Tampas Traseiras</option>
                <option value="Câmeras">Câmeras</option>
                <option value="Outros">Outros</option>
              </select>
            </div>
            <div class="vtex-form-group">
              <label>Qualidade *</label>
              <select id="np-quality" required>
                <option value="PRIMEIRA_LINHA">Primeira Linha (Incell/OLED)</option>
                <option value="ORIGINAL_NACIONAL">Original Nacional</option>
              </select>
            </div>
            <div class="vtex-form-group">
              <label>Possui Aro? *</label>
              <select id="np-has-frame">
                <option value="true">Sim (Com Aro)</option>
                <option value="false">Não (Sem Aro)</option>
              </select>
            </div>
            <div class="vtex-form-group">
              <label>Quantidade Inicial *</label>
              <input type="number" id="np-quantity" required min="1" value="5">
            </div>
            <div class="vtex-form-group">
              <label>Preço de Venda Balcão (R$) *</label>
              <input type="number" id="np-price" required step="0.01" min="0.01" placeholder="120.00">
            </div>
            <div class="vtex-form-group">
              <label>Custo Unitário (R$)</label>
              <input type="number" id="np-cost" step="0.01" min="0" placeholder="65.00">
            </div>
            <div class="vtex-form-group">
              <label>Fornecedor</label>
              <input type="text" id="np-supplier" placeholder="Ex: Distribuidora Central">
            </div>
            <div class="vtex-form-group">
              <label>Localização / Gaveta</label>
              <input type="text" id="np-location" placeholder="Ex: Gaveta G-12">
            </div>
          </div>
          <div class="vtex-modal-footer" style="margin-top: 1.25rem; padding-bottom: 0;">
            <button type="button" class="btn btn-secondary" onclick="closeNewProductModal()">Cancelar</button>
            <button type="submit" class="btn btn-emerald" id="btn-save-product">Salvar Peça no Estoque</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL VTEX ADMIN: INSPEÇÃO DE JSON TÉCNICO (AUDITORIA) -->
    <div id="modal-json-viewer" class="vtex-modal-overlay">
      <div class="vtex-modal" style="max-width: 680px;">
        <div class="vtex-modal-header">
          <div class="vtex-modal-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #818CF8;"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            <span id="json-modal-title">Payload JSON Técnico</span>
          </div>
          <button class="drawer-close-btn" onclick="closeJsonViewer()">✕</button>
        </div>
        <div class="vtex-modal-body">
          <pre id="json-modal-content" style="background: rgba(0,0,0,0.5); padding: 1rem; border-radius: 8px; font-family: var(--font-mono); font-size: 0.775rem; color: #A5B4FC; overflow-x: auto; max-height: 480px;"></pre>
        </div>
        <div class="vtex-modal-footer">
          <button class="btn btn-secondary" onclick="closeJsonViewer()">Fechar</button>
        </div>
      </div>
    </div>

    </main>
    </div> <!-- /content-viewport -->
  </div> <!-- /app-layout -->

<script>

    // --- UTILITÁRIOS DE FORMATAÇÃO E USABILIDADE ---
    function formatPhoneBR(raw) {
      if (!raw) return '--';
      const digits = String(raw).replace(/\D/g, '');
      if (digits.length === 13 && digits.startsWith('55')) {
        return `(${digits.slice(2, 4)}) ${digits.slice(4, 9)}-${digits.slice(9)}`;
      } else if (digits.length === 12 && digits.startsWith('55')) {
        return `(${digits.slice(2, 4)}) ${digits.slice(4, 8)}-${digits.slice(8)}`;
      } else if (digits.length === 11) {
        return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
      } else if (digits.length === 10) {
        return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
      }
      return raw;
    }

    function formatOrderStatusBadge(status) {
      const s = String(status || '').toUpperCase();
      if (s === 'CONFIRMED') {
        return '<span class="status-pill" style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3);">✓ Separando / Confirmado</span>';
      } else if (s === 'WAITING_CONFIRMATION') {
        return '<span class="status-pill" style="background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3);">⏳ Aguardando Confirmação</span>';
      } else if (s === 'DISPATCHED_UBER') {
        return '<span class="status-pill" style="background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3);">🚗 Em Rota Uber Flash</span>';
      } else if (s === 'DELIVERED') {
        return '<span class="status-pill" style="background: rgba(6, 182, 212, 0.15); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.3);">📦 Entregue / Concluído</span>';
      } else if (s === 'CANCELLED') {
        return '<span class="status-pill" style="background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3);">✕ Cancelado</span>';
      }
      return `<span class="status-pill status-robot">${escapeHtml(status)}</span>`;
    }

    // --- CHAT DRAWER DE ATENDIMENTO AO VIVO (WHATSAPP) ---
    let currentDrawerPhone = null;
    let currentDrawerActive = true;

    async function openChatDrawer(phone, name, formattedPhone, isActive) {
      currentDrawerPhone = phone;
      currentDrawerActive = isActive;
      const cleanPhone = (phone || '').replace(/\D/g, '');
      const initials = getInitials(name || 'Cliente');

      document.getElementById('drawer-avatar').innerText = initials;
      document.getElementById('drawer-name').innerText = name || 'Cliente WhatsApp';
      document.getElementById('drawer-phone').innerText = formatPhoneBR(formattedPhone || phone);
      document.getElementById('drawer-wa-link').href = cleanPhone ? `https://wa.me/${cleanPhone}` : '#';

      const pill = document.getElementById('drawer-status-pill');
      const actionBtn = document.getElementById('drawer-action-btn');
      if (isActive) {
        pill.className = 'status-pill status-robot';
        pill.innerText = 'IA Ativa';
        actionBtn.className = 'btn btn-amber btn-sm';
        actionBtn.innerText = '⏸️ Assumir Atendimento';
      } else {
        pill.className = 'status-pill status-human';
        pill.innerText = 'Balcão Manual';
        actionBtn.className = 'btn btn-emerald btn-sm';
        actionBtn.innerText = '▶️ Liberar p/ IA';
      }

      document.getElementById('drawer-chat-overlay').classList.add('active');
      document.getElementById('drawer-chat').classList.add('active');

      const msgBox = document.getElementById('drawer-messages');
      msgBox.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Carregando histórico ao vivo...</div>';

      try {
        const res = await fetch(`/api/conversations/${cleanPhone}/messages`);
        const data = await res.json();
        const messages = data.messages || [];

        if (messages.length === 0) {
          msgBox.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhuma mensagem registrada nesta conversa ainda.</div>';
          return;
        }

        msgBox.innerHTML = messages.map(m => {
          const isUser = m.role === 'user';
          const senderLabel = isUser ? 'Cliente' : (m.role === 'system' ? 'Sistema Balcão' : 'Victor Cell (IA)');
          const bubbleClass = isUser ? 'incoming' : 'outgoing';
          const time = m.created_at || '';

          return `
            <div class="chat-bubble-drawer ${bubbleClass}">
              <div style="font-size: 0.68rem; font-weight: 700; opacity: 0.75; margin-bottom: 2px;">${senderLabel}</div>
              <div style="white-space: pre-wrap;">${escapeHtml(m.content)}</div>
              <div class="chat-bubble-meta">
                <span>${time}</span>
                ${!isUser ? '<span>✓✓</span>' : ''}
              </div>
            </div>
          `;
        }).join('');
        msgBox.scrollTop = msgBox.scrollHeight;
      } catch (err) {
        msgBox.innerHTML = '<div style="text-align: center; padding: 2rem; color: #F87171;">Erro ao carregar mensagens: ' + escapeHtml(err.message) + '</div>';
      }
    }

    function closeChatDrawer() {
      document.getElementById('drawer-chat-overlay').classList.remove('active');
      document.getElementById('drawer-chat').classList.remove('active');
      currentDrawerPhone = null;
    }

    async function toggleDrawerConversationMode() {
      if (!currentDrawerPhone) return;
      if (currentDrawerActive) {
        await pauseConversation(currentDrawerPhone);
        currentDrawerActive = false;
        document.getElementById('drawer-status-pill').className = 'status-pill status-human';
        document.getElementById('drawer-status-pill').innerText = 'Balcão Manual';
        document.getElementById('drawer-action-btn').className = 'btn btn-emerald btn-sm';
        document.getElementById('drawer-action-btn').innerText = '▶️ Liberar p/ IA';
      } else {
        await resumeConversation(currentDrawerPhone);
        currentDrawerActive = true;
        document.getElementById('drawer-status-pill').className = 'status-pill status-robot';
        document.getElementById('drawer-status-pill').innerText = 'IA Ativa';
        document.getElementById('drawer-action-btn').className = 'btn btn-amber btn-sm';
        document.getElementById('drawer-action-btn').innerText = '⏸️ Assumir Atendimento';
      }
    }

    // --- MODAL DE CADASTRO MANUAL DE PRODUTOS NO ESTOQUE (ERP NATIVO) ---
    function openNewProductModal() {
      document.getElementById('modal-new-product').classList.add('active');
      document.getElementById('np-sku').focus();
    }

    function closeNewProductModal() {
      document.getElementById('modal-new-product').classList.remove('active');
      document.getElementById('form-new-product').reset();
    }

    async function submitNewProduct(e) {
      e.preventDefault();
      const btn = document.getElementById('btn-save-product');
      btn.disabled = true;
      btn.innerText = 'Salvando no estoque...';

      const payload = {
        sku: document.getElementById('np-sku').value.trim().toUpperCase(),
        model: document.getElementById('np-model').value.trim(),
        category: document.getElementById('np-category').value,
        quality: document.getElementById('np-quality').value,
        has_frame: document.getElementById('np-has-frame').value === 'true',
        price: parseFloat(document.getElementById('np-price').value),
        cost: document.getElementById('np-cost').value ? parseFloat(document.getElementById('np-cost').value) : null,
        initial_quantity: parseInt(document.getElementById('np-quantity').value, 10),
        supplier: document.getElementById('np-supplier').value.trim() || null,
        location: document.getElementById('np-location').value.trim() || null
      };

      try {
        const res = await fetch('/api/erp/products', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Falha ao cadastrar peça');

        showToast(`Peça ${payload.sku} cadastrada com ${payload.initial_quantity} un no estoque!`, 'success');
        closeNewProductModal();
        fetchCatalog();
        loadErpSummary();
        loadErpMovements();
      } catch (err) {
        showToast('Erro ao cadastrar peça: ' + err.message, 'error');
      } finally {
        btn.disabled = false;
        btn.innerText = 'Salvar Peça no Estoque';
      }
    }

    // --- TOGGLE PLANILHA GOOGLE SHEETS ---
    function toggleGoogleSheetsFrame() {
      const container = document.getElementById('sheets-frame-container');
      const textSpan = document.getElementById('toggle-sheets-btn-text');
      if (!container) return;
      if (container.style.display === 'none' || !container.style.display) {
        container.style.display = 'block';
        if (textSpan) textSpan.innerText = 'Ocultar Planilha';
      } else {
        container.style.display = 'none';
        if (textSpan) textSpan.innerText = 'Exibir Planilha Google Sheets';
      }
    }

    // --- MODAL DE INSPEÇÃO JSON TÉCNICO (AUDITORIA) ---
    function openJsonViewer(index) {
      const log = (window.renderedAuditLogs || [])[index];
      if (!log) return;
      document.getElementById('json-modal-title').innerText = `Auditoria #${log.id || index} • ${log.action}`;
      document.getElementById('json-modal-content').innerText = JSON.stringify(log, null, 2);
      document.getElementById('modal-json-viewer').classList.add('active');
    }

    function closeJsonViewer() {
      document.getElementById('modal-json-viewer').classList.remove('active');
    }

    // --- STATUS DA PIPELINE COGNITIVA MULTIMODAL (IA EM TEMPO REAL) ---
    async function fetchAIPipelineStatus() {
      try {
        const res = await fetch('/api/ai/pipeline-status');
        if (!res.ok) return;
        const data = await res.json();

        // 1. Consumo Real
        const usage = data.usage || {};
        const reqCount = usage.real_daily_requests || 0;
        const reqElem = document.getElementById('ai-real-requests');
        if (reqElem) reqElem.innerText = `${reqCount} / ${usage.quota_limit || 1500} RPD`;

        const pct = Math.min(100, Math.max(1, Math.round(usage.percentage || 0)));
        const barElem = document.getElementById('ai-quota-bar');
        if (barElem) barElem.style.width = pct + '%';

        const pctElem = document.getElementById('ai-quota-pct');
        if (pctElem) pctElem.innerText = `${pct}% da cota diária`;

        // 2. Modelos & Endpoints
        const pipe = data.pipeline || {};
        if (pipe.conversation) {
          const mElem = document.getElementById('ai-model-convo');
          if (mElem) mElem.innerText = pipe.conversation.model || 'Gemini 2.5 Flash';
          const epElem = document.getElementById('ai-endpoint-convo');
          if (epElem) epElem.innerText = pipe.conversation.endpoint || '/v1beta/models/gemini-2.5-flash:generateContent';
          const fbElem = document.getElementById('ai-fallback-convo');
          if (fbElem) fbElem.innerText = (pipe.conversation.fallback || 'Gemini 1.5 Pro') + ' + Fast FAQ Cache';
        }

        // 3. Circuit Breaker
        if (pipe.circuit_breaker) {
          const cbElem = document.getElementById('ai-circuit-status');
          const cb = pipe.circuit_breaker;
          if (cbElem) {
            cbElem.innerText = `${cb.state || 'CLOSED'} (${cb.failures || 0} falhas)`;
            cbElem.style.color = (cb.state === 'CLOSED') ? '#34D399' : '#F87171';
          }
        }
      } catch (err) {
        console.error('Erro ao buscar status da pipeline de IA:', err);
      }
    }


    // Interceptor global: Redireciona imediatamente para o login se a sessão expirar
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
      try {
        const response = await originalFetch.apply(this, args);
        if (response.status === 401 && !window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        return response;
      } catch (err) {
        throw err;
      }
    };

    // Variáveis Globais
    let allConversations = [];
    let allOrders = [];
    let allCatalog = [];
    let chartQuality = null;
    let chartCategory = null;

    // --- JAVASCRIPT DO CONSULTOR EXECUTIVO DE NEGÓCIOS (COPILOTO IA) ---
    let copilotHistory = [];

    function clearCopilotChat() {
      copilotHistory = [];
      const messagesDiv = document.getElementById('copilot-messages');
      if (messagesDiv) {
        messagesDiv.innerHTML = `
          <div class="copilot-msg bot">
            <div class="copilot-avatar">✦</div>
            <div class="copilot-bubble">
              <p><strong>Sessão de Análise Reiniciada</strong></p>
              <p>Pronto para examinar novos indicadores de faturamento, pedidos e estoque da Victor Cell. Qual métrica ou diagnóstico deseja consultar?</p>
            </div>
          </div>
        `;
      }
    }

    function sendQuickPrompt(promptText) {
      const input = document.getElementById('copilot-input');
      if (input) {
        input.value = promptText;
        sendCopilotMessage();
      }
    }

    function formatMarkdownText(rawText) {
      if (!rawText) return '';
      let formatted = rawText
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1);padding:2px 5px;border-radius:4px;font-family:monospace;">$1</code>');

      const lines = formatted.split('\n');
      let htmlOut = '';
      let inList = false;

      for (let line of lines) {
        line = line.trim();
        if (line.startsWith('### ')) {
          if (inList) { htmlOut += '</ul>'; inList = false; }
          htmlOut += `<h4 style="margin: 1.15rem 0 0.45rem 0; font-size: 0.95rem; font-weight: 700; color: #93C5FD; letter-spacing: 0.03em; text-transform: uppercase;">${line.substring(4)}</h4>`;
        } else if (line.startsWith('## ')) {
          if (inList) { htmlOut += '</ul>'; inList = false; }
          htmlOut += `<h3 style="margin: 1.3rem 0 0.55rem 0; font-size: 1.05rem; font-weight: 700; color: #F3F4F6;">${line.substring(3)}</h3>`;
        } else if (line.startsWith('# ')) {
          if (inList) { htmlOut += '</ul>'; inList = false; }
          htmlOut += `<h2 style="margin: 1.5rem 0 0.65rem 0; font-size: 1.15rem; font-weight: 700; color: #FFFFFF;">${line.substring(2)}</h2>`;
        } else if (line.startsWith('• ') || line.startsWith('- ') || line.startsWith('* ')) {
          if (!inList) {
            htmlOut += '<ul style="margin: 0.5rem 0; padding-left: 1.25rem; display: flex; flex-direction: column; gap: 0.35rem;">';
            inList = true;
          }
          htmlOut += `<li style="line-height: 1.6; color: #E5E7EB;">${line.substring(2)}</li>`;
        } else {
          if (inList) {
            htmlOut += '</ul>';
            inList = false;
          }
          if (line) {
            htmlOut += `<p style="margin-bottom: 0.75rem; line-height: 1.65; color: #E5E7EB;">${line}</p>`;
          }
        }
      }
      if (inList) htmlOut += '</ul>';
      return htmlOut;
    }

    async function sendCopilotMessage() {
      const input = document.getElementById('copilot-input');
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;

      input.value = '';

      const messagesDiv = document.getElementById('copilot-messages');
      if (!messagesDiv) return;

      // 1. Mensagem do Gestor
      const userMsg = document.createElement('div');
      userMsg.className = 'copilot-msg user';
      userMsg.innerHTML = `
        <div class="copilot-user-avatar">Atendente</div>
        <div class="copilot-bubble">
          <p>${text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>
        </div>
      `;
      messagesDiv.appendChild(userMsg);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;

      // 2. Balão de Carregando (Typing Indicator)
      const loadingMsg = document.createElement('div');
      loadingMsg.className = 'copilot-msg bot loading-msg';
      loadingMsg.innerHTML = `
        <div class="copilot-avatar">✦</div>
        <div class="copilot-bubble">
          <span class="copilot-loading-dot"></span> Analisando dados da loja em tempo real...
        </div>
      `;
      messagesDiv.appendChild(loadingMsg);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;

      try {
        const res = await fetch('/api/copilot/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, history: copilotHistory })
        });
        const data = await res.json();
        loadingMsg.remove();

        const botMsg = document.createElement('div');
        botMsg.className = 'copilot-msg bot';
        const formatted = formatMarkdownText(data.reply || 'Sem resposta do assistente.');
        botMsg.innerHTML = `
          <div class="copilot-avatar">✦</div>
          <div class="copilot-bubble">${formatted}</div>
        `;
        messagesDiv.appendChild(botMsg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

        copilotHistory.push({ role: 'user', content: text });
        copilotHistory.push({ role: 'model', content: data.reply || '' });
        if (copilotHistory.length > 8) copilotHistory = copilotHistory.slice(-8);

      } catch (err) {
        loadingMsg.remove();
        const errorMsg = document.createElement('div');
        errorMsg.className = 'copilot-msg bot';
        errorMsg.innerHTML = `
          <div class="copilot-avatar">✦</div>
          <div class="copilot-bubble" style="border-color: rgba(239, 68, 68, 0.4);">
            <p style="color: #F87171;">⚠️ Erro ao consultar o Consultor de Negócios. Verifique sua conexão e tente novamente.</p>
          </div>
        `;
        messagesDiv.appendChild(errorMsg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
      }
    }

    // --- FUNÇÕES DA ABA GOOGLE SHEETS & CATÁLOGO ---
    function toggleSheetView() {
      const container = document.getElementById('sheet-embed-container');
      const btn = document.getElementById('btn-toggle-sheet-view');
      if (!container || !btn) return;
      if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.innerText = '✕ Fechar Visualização da Planilha';
      } else {
        container.style.display = 'none';
        btn.innerText = 'Visualizar Planilha';
      }
    }

    function filterCatalogTable() {
      const searchEl = document.getElementById('catalog-search');
      const query = (searchEl ? searchEl.value : '').toLowerCase().trim();
      const rows = document.querySelectorAll('#catalog-tbody tr');
      rows.forEach(r => {
        const text = r.innerText.toLowerCase();
        r.style.display = text.includes(query) ? '' : 'none';
      });
      const cards = document.querySelectorAll('#catalog-cards-mobile .customer-card-mobile');
      cards.forEach(c => {
        const text = c.innerText.toLowerCase();
        c.style.display = text.includes(query) ? '' : 'none';
      });
    }


    function showToast(msg, type = 'success') {
      const toast = document.getElementById('toast');
      const icon = document.getElementById('toast-icon');
      const text = document.getElementById('toast-msg');
      icon.innerText = type === 'success' ? '✅' : '⚠️';
      text.innerText = msg;
      toast.style.display = 'flex';
      setTimeout(() => { toast.style.display = 'none'; }, 3500);
    }


    function toggleSidebar() {
      const sidebar = document.getElementById('app-sidebar');
      const overlay = document.getElementById('sidebar-overlay');
      if (sidebar) sidebar.classList.toggle('sidebar-open');
      if (overlay) overlay.classList.toggle('active');
    }
    function switchTab(tabId) {
      const tabTitles = {
        conversations: 'Atendimentos WhatsApp',
        orders: 'Separação & Balcão de Saída',
        overview: 'Métricas & Relatórios',
        catalog: 'Catálogo de Peças',
        erp: 'ERP & Entrada de Estoque',
        copilot: 'Copiloto de Gestão',
        audit: 'Auditoria & Logs',
        profile: 'Perfil da Loja',
        gemini: 'Simulador WhatsApp Sandbox'
      };
      const titleElem = document.getElementById('bc-current-title');
      if (titleElem && tabTitles[tabId]) {
        titleElem.textContent = tabTitles[tabId];
      }
      const sidebar = document.getElementById('app-sidebar');
      const overlay = document.getElementById('sidebar-overlay');
      if (sidebar && window.innerWidth < 1024) {
        sidebar.classList.remove('sidebar-open');
        if (overlay) overlay.classList.remove('active');
      }
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const activeBtn = Array.from(document.querySelectorAll('.nav-tab')).find(b => b.getAttribute('onclick').includes(tabId));
      if (activeBtn) activeBtn.classList.add('active');
      const targetPane = document.getElementById('tab-' + tabId);
      if (targetPane) targetPane.classList.add('active');

      if (tabId === 'conversations') fetchConversations();
      if (tabId === 'catalog') fetchCatalog();
    checkMasterAISwitch();
      if (tabId === 'orders' || tabId === 'overview') fetchStats();
      if (tabId === 'audit') fetchAuditLogs();
      if (tabId === 'profile') fetchStoreProfile();
      if (tabId === 'erp') { loadErpSummary(); loadErpMovements(); }
      if (tabId === 'simulator' || tabId === 'gemini') {
        fetchWhatsAppQR();
        fetchAIPipelineStatus();
      }
    }

    // 1. ATENDIMENTOS AO VIVO (IA VS HUMANO)
    async function fetchConversations() {
      try {
        const res = await fetch('/api/conversations');
        const data = await res.json();
        allConversations = data.conversations || [];
        document.getElementById('badge-convs-count').innerText = allConversations.length;
        document.getElementById('convs-counter').innerText = `${allConversations.length} atendimentos`;
        document.getElementById('kpi-active-chats').innerText = allConversations.length;

        renderConversations(allConversations);
      } catch (err) {
        console.error('Erro ao carregar atendimentos:', err);
      }
    }

    function filterConversations() {
      const q = (document.getElementById('search-convs').value || '').toLowerCase().trim();
      if (!q) {
        renderConversations(allConversations);
        return;
      }
      const filtered = allConversations.filter(c =>
        (c.customer_name || '').toLowerCase().includes(q) ||
        (c.phone || '').includes(q) ||
        (c.formatted_phone || '').includes(q) ||
        (c.active_sku_name || '').toLowerCase().includes(q) ||
        (c.active_sku || '').toLowerCase().includes(q)
      );
      renderConversations(filtered);
    }

    function renderConversations(convs) {
      const tbodyDesktop = document.getElementById('convs-tbody-desktop');
      const deckMobile = document.getElementById('convs-cards-mobile');

      if (!convs || convs.length === 0) {
        const emptyHtml = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhum atendimento registrado no momento.</div>';
        tbodyDesktop.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">Nenhum atendimento registrado no momento.</td></tr>';
        deckMobile.innerHTML = emptyHtml;
        return;
      }

      // Render Desktop & Tablet
      tbodyDesktop.innerHTML = convs.map(c => {
        const cleanPhone = (c.phone || '').replace(/\D/g, '');
        const waLink = cleanPhone ? `https://wa.me/${cleanPhone}` : '#';
        const isActive = c.is_ai_active;
        const initials = getInitials(c.customer_name);
        const lastMsg = c.last_message || 'Iniciando conversa...';
        const lastMsgRole = c.last_message_role === 'assistant' ? 'IA' : 'Cliente';
        const snippet = lastMsg.length > 50 ? lastMsg.slice(0, 50) + '...' : lastMsg;
        const roleBadge = c.last_message_role === 'assistant'
          ? '<span style="color: #34D399; font-weight: 700; font-size: 0.7rem;">IA:</span>'
          : '<span style="color: #60A5FA; font-weight: 700; font-size: 0.7rem;">Cliente:</span>';

        return `
          <tr>
            <td>
              <div class="user-profile">
                <div class="user-avatar">${initials}</div>
                <div class="user-info">
                  <span class="user-name">${escapeHtml(c.customer_name || 'Cliente WhatsApp')}</span>
                  <a href="${waLink}" target="_blank" class="user-phone" title="Abrir no WhatsApp">
                    ${formatPhoneBR(c.formatted_phone || c.phone)} ↗
                  </a>
                </div>
              </div>
            </td>
            <td>
              <div style="font-size: 0.8rem; color: #E2E8F0; line-height: 1.35; max-width: 280px;" title="${escapeHtml(lastMsg)}">
                ${roleBadge} ${escapeHtml(snippet)}
              </div>
              <div style="font-size: 0.7rem; color: var(--text-dim); font-family: var(--font-mono); margin-top: 3px;">
                ⏰ ${c.last_activity || '--'}
              </div>
            </td>
            <td>
              <span class="part-pill" title="${escapeHtml(c.active_sku_name)}">
                ${escapeHtml(c.active_sku_name)}
              </span>
            </td>
            <td>
              ${isActive
                ? `<span class="status-pill status-robot">IA Ativa</span>`
                : `<span class="status-pill status-human">Balcão Manual</span>`
              }
            </td>
            <td>
              <div style="display: flex; gap: 6px; align-items: center;">
                <button class="btn btn-secondary btn-sm" onclick="openChatDrawer('${c.phone}', '${escapeHtml(c.customer_name || 'Cliente')}', '${c.formatted_phone || c.phone}', ${isActive})">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align: -2px; margin-right: 3px;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg> Ver Chat
                </button>
                ${!isActive
                  ? `<button class="btn btn-emerald btn-sm" onclick="resumeConversation('${c.phone}')">▶️ Liberar</button>`
                  : `<button class="btn btn-amber btn-sm" onclick="pauseConversation('${c.phone}')">⏸️ Assumir</button>`
                }
              </div>
            </td>
          </tr>
        `;
      }).join('');

      // Render Mobile Card Deck
      deckMobile.innerHTML = convs.map(c => {
        const cleanPhone = (c.phone || '').replace(/\D/g, '');
        const waLink = cleanPhone ? `https://wa.me/${cleanPhone}` : '#';
        const isActive = c.is_ai_active;
        const initials = getInitials(c.customer_name);
        const lastMsg = c.last_message || 'Iniciando conversa...';
        const snippet = lastMsg.length > 55 ? lastMsg.slice(0, 55) + '...' : lastMsg;

        return `
          <div class="customer-card-mobile">
            <div class="card-mobile-top">
              <div class="user-profile">
                <div class="user-avatar">${initials}</div>
                <div class="user-info">
                  <span class="user-name">${escapeHtml(c.customer_name || 'Cliente WhatsApp')}</span>
                  <a href="${waLink}" target="_blank" class="user-phone">
                    ${formatPhoneBR(c.formatted_phone || c.phone)} ↗
                  </a>
                </div>
              </div>
              <div>
                ${isActive
                  ? `<span class="status-pill status-robot">IA Ativa</span>`
                  : `<span class="status-pill status-human">Balcão Manual</span>`
                }
              </div>
            </div>

            <div class="card-mobile-body">
              <div style="font-size: 0.775rem; color: #CBD5E1; background: rgba(0,0,0,0.3); padding: 0.5rem 0.65rem; border-radius: 6px; margin-bottom: 0.4rem;">
                💬 ${escapeHtml(snippet)}
              </div>
              <div style="font-size: 0.725rem; color: var(--text-dim);">Peça Sendo Cotada: <span class="part-pill">${escapeHtml(c.active_sku_name)}</span></div>
              <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 0.2rem;">Último contato: ${c.last_activity || '--'}</div>
            </div>

            <div class="card-mobile-actions" style="display: flex; gap: 6px;">
              <button class="btn btn-secondary btn-sm" style="flex: 1;" onclick="openChatDrawer('${c.phone}', '${escapeHtml(c.customer_name || 'Cliente')}', '${c.formatted_phone || c.phone}', ${isActive})">
                💬 Abrir Chat Live
              </button>
              ${!isActive
                ? `<button class="btn btn-emerald btn-sm" onclick="resumeConversation('${c.phone}')">▶️ Liberar</button>`
                : `<button class="btn btn-amber btn-sm" onclick="pauseConversation('${c.phone}')">⏸️ Assumir</button>`
              }
            </div>
          </div>
        `;
      }).join('');
    }

    async function resumeConversation(phone) {
      try {
        const res = await fetch(`/api/conversations/${phone}/resume`, { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'IA reativada com sucesso!', 'success');
        fetchConversations();
      } catch (err) {
        showToast('Erro ao reativar IA: ' + err, 'error');
      }
    }

    async function pauseConversation(phone) {
      try {
        const res = await fetch(`/api/conversations/${phone}/pause`, { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'IA pausada por 3 horas!', 'success');
        fetchConversations();
      } catch (err) {
        showToast('Erro ao pausar IA: ' + err, 'error');
      }
    }

    // 2. STATS, PEDIDOS & CHARTS
    async function fetchStats() {
      try {
        const res = await fetch('/api/reports/stats');
        const data = await res.json();

        // KPIs
        document.getElementById('kpi-revenue').innerText = 'R$ ' + (data.total_revenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        document.getElementById('kpi-uber').innerText = Math.round(data.uber_percentage || 0) + '%';
        document.getElementById('kpi-uber-count').innerText = `${data.uber_orders || 0} de ${data.total_orders || 0} pedidos`;
        document.getElementById('kpi-stock-items').innerText = data.total_products || 0;
        const obElem = document.getElementById('kpi-overbooking-blocked');
        if (obElem) obElem.innerText = data.overbooking_blocked_total || 0;
        document.getElementById('badge-orders-count').innerText = (data.recent_orders || []).length;
        document.getElementById('orders-counter').innerText = `${(data.recent_orders || []).length} pedidos`;

        // Store status pill
        const storeStatus = document.getElementById('store-status');
        if (data.store_schedule) {
          storeStatus.innerText = data.store_schedule.badge_text;
          document.getElementById('pill-store').className = data.store_schedule.is_open ? 'pill pill-emerald' : (data.store_schedule.is_sunday ? 'pill pill-rose' : 'pill pill-amber');
        } else if (data.is_store_open) {
          storeStatus.innerText = 'Loja Aberta';
          document.getElementById('pill-store').className = 'pill pill-emerald';
        } else {
          storeStatus.innerText = 'Loja Fechada';
          document.getElementById('pill-store').className = 'pill pill-amber';
        }

        // Tabela de Pedidos
        renderOrders(data.recent_orders || []);

        // Atualizar Categorização de Mensagens do WhatsApp
        if (data.whatsapp_categorization) {
          const wc = data.whatsapp_categorization;
          const qElem = document.getElementById('cat-val-quotes');
          const oElem = document.getElementById('cat-val-orders');
          const rElem = document.getElementById('cat-val-ruptures');
          const hElem = document.getElementById('cat-val-handoffs');
          const sElem = document.getElementById('cat-val-outofscope');
          if (qElem) qElem.innerText = wc.quotations_count || 0;
          if (oElem) oElem.innerText = wc.orders_count || 0;
          if (rElem) rElem.innerText = wc.ruptures_count || 0;
          if (hElem) hElem.innerText = wc.handoffs_count || 0;
          if (sElem) sElem.innerText = wc.out_of_scope_count || 0;

          const total = (wc.quotations_count || 0) + (wc.orders_count || 0) + (wc.ruptures_count || 0) + (wc.handoffs_count || 0) + (wc.out_of_scope_count || 0) || 1;
          const qPct = Math.round(((wc.quotations_count || 0) / total) * 100);
          const oPct = Math.round(((wc.orders_count || 0) / total) * 100);
          const rPct = Math.round(((wc.ruptures_count || 0) / total) * 100);
          const hPct = Math.round(((wc.handoffs_count || 0) / total) * 100);
          const sPct = Math.max(0, 100 - (qPct + oPct + rPct + hPct));

          const barElem = document.getElementById('wa-categories-bar');
          if (barElem) {
            barElem.innerHTML = `
              <div style="width: ${qPct}%; background: #F59E0B;" title="Cotações: ${qPct}%"></div>
              <div style="width: ${oPct}%; background: #10B981;" title="Pedidos: ${oPct}%"></div>
              <div style="width: ${rPct}%; background: #EF4444;" title="Rupturas: ${rPct}%"></div>
              <div style="width: ${hPct}%; background: #818CF8;" title="Transbordo: ${hPct}%"></div>
              <div style="width: ${sPct}%; background: #64748B;" title="Fora de Escopo: ${sPct}%"></div>
            `;
          }
        }

        // Ranking
        renderTopProducts(data.top_products || []);

        // Charts
        renderCharts(data.quality_breakdown || {}, data.category_breakdown || {});
        renderChatFunnelCharts(data.chat_funnel_stats);
        fetchFilteredAnalytics();
      } catch (err) {
        console.error('Erro ao buscar stats:', err);
      }
    }

    let currentOrderFilter = 'all';

    function filterOrdersMode(mode, btn) {
      currentOrderFilter = mode;
      document.querySelectorAll('[data-order-filter]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderOrdersFiltered();
    }

    function renderOrders(orders) {
      window.allOrders = orders || [];
      renderOrdersFiltered();
    }

    function renderOrdersFiltered() {
      const orders = window.allOrders || [];
      const tbody = document.getElementById('orders-tbody');
      const mobileDeck = document.getElementById('orders-cards-mobile');

      let filtered = orders;
      if (currentOrderFilter === 'balcao') {
        filtered = orders.filter(o => !o.destination_address || o.destination_address.toLowerCase().includes('balc') || o.destination_address.toLowerCase().includes('retirada'));
      } else if (currentOrderFilter === 'uber') {
        filtered = orders.filter(o => o.destination_address && !o.destination_address.toLowerCase().includes('balc') && !o.destination_address.toLowerCase().includes('retirada'));
      }

      const counter = document.getElementById('orders-counter');
      if (counter) counter.innerText = `${filtered.length} de ${orders.length} pedidos`;

      if (!filtered || filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-muted);"><div style="font-size: 1.5rem; margin-bottom: 0.5rem;"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg></div>Nenhum pedido encontrado para o filtro selecionado.</td></tr>';
        mobileDeck.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhum pedido encontrado.</div>';
        return;
      }

      tbody.innerHTML = filtered.map(o => {
        const isBalcao = !o.destination_address || o.destination_address.toLowerCase().includes('balc') || o.destination_address.toLowerCase().includes('retirada');
        const modalPill = isBalcao
          ? `<span class="pill pill-cyan" style="font-weight: 700;">Retirada no Balcão</span>`
          : `<span class="pill pill-amber" style="font-weight: 700;" title="${escapeHtml(o.destination_address)}">Uber Flash: ${escapeHtml(o.destination_address.length > 25 ? o.destination_address.slice(0, 25) + '...' : o.destination_address)}</span>`;

        const waLink = `https://wa.me/${(o.customer_phone || '').replace(/\D/g, '')}`;

        return `
          <tr>
            <td>
              <div style="font-weight: 700; color: #fff;">#${o.id}</div>
              <div style="font-size: 0.725rem; color: var(--text-dim); font-family: var(--font-mono);">${o.created_at}</div>
            </td>
            <td>
              <div style="font-weight: 600; color: #E2E8F0;">${escapeHtml(o.customer_name)}</div>
              <a href="${waLink}" target="_blank" style="font-size: 0.75rem; color: #34D399; font-family: var(--font-mono); text-decoration: none; display: inline-flex; align-items: center; gap: 3px;">
                ${formatPhoneBR(o.customer_phone)} ↗
              </a>
            </td>
            <td><span class="part-pill" style="font-weight: 700;">${escapeHtml(o.product_sku)}</span></td>
            <td style="font-weight: 800; color: #34D399; font-size: 0.95rem;">R$ ${(o.product_price || 0).toFixed(2)}</td>
            <td>${modalPill}</td>
            <td>${formatOrderStatusBadge(o.status)}</td>
            <td style="color: #FBBF24; font-weight: 600; font-size: 0.8rem;" title="Garante a peça por 30 minutos sem risco de venda duplicada">⏰ Até ${o.expires_at}</td>
          </tr>
        `;
      }).join('');

      mobileDeck.innerHTML = filtered.map(o => {
        const isBalcao = !o.destination_address || o.destination_address.toLowerCase().includes('balc') || o.destination_address.toLowerCase().includes('retirada');
        const modalPill = isBalcao
          ? `<span class="pill pill-cyan" style="font-weight: 700;">Balcão</span>`
          : `<span class="pill pill-amber" style="font-weight: 700;">Uber Flash</span>`;
        const waLink = `https://wa.me/${(o.customer_phone || '').replace(/\D/g, '')}`;

        return `
          <div class="customer-card-mobile" style="border-left: 3px solid ${isBalcao ? '#38BDF8' : '#F59E0B'};">
            <div class="card-mobile-top">
              <div>
                <div style="font-weight: 700; color: #fff;">#${o.id} • R$ ${(o.product_price || 0).toFixed(2)}</div>
                <a href="${waLink}" target="_blank" style="font-size: 0.75rem; color: #34D399; text-decoration: none;">${escapeHtml(o.customer_name)} (${o.customer_phone}) ↗</a>
              </div>
              <div style="display: flex; gap: 4px;">
                ${modalPill}
                <span class="status-pill status-robot">${o.status}</span>
              </div>
            </div>
            <div class="card-mobile-body">
              <div><strong>Peça:</strong> ${escapeHtml(o.product_sku)}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(o.destination_address || 'Retirada no Balcão')}</div>
              <div style="font-size: 0.725rem; color: #FBBF24; margin-top: 4px;">⏰ Validade: Até ${o.expires_at} (${o.created_at})</div>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderTopProducts(products) {
      const tbody = document.getElementById('top-products-tbody');
      if (!products || products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 1.5rem; color: var(--text-muted);">Nenhuma venda registrada ainda.</td></tr>';
        return;
      }
      tbody.innerHTML = products.map((p, idx) => `
        <tr>
          <td style="font-weight: 800; color: ${idx === 0 ? '#FBBF24' : '#fff'};">#${idx + 1}</td>
          <td><strong>${escapeHtml(p.name)}</strong> <span style="font-size: 0.725rem; color: var(--text-dim); font-family: monospace;">(${p.sku})</span></td>
          <td><span class="part-pill">${p.quality}</span></td>
          <td style="font-weight: 700;">${p.quantity} un.</td>
          <td style="font-weight: 700; color: #34D399;">R$ ${(p.revenue || 0).toFixed(2)}</td>
        </tr>
      `).join('');
    }

    function renderCharts(qualityData, categoryData) {
      const ctxQ = document.getElementById('chartQuality');
      const ctxC = document.getElementById('chartCategory');

      if (chartQuality) chartQuality.destroy();
      if (chartCategory) chartCategory.destroy();

      chartQuality = new Chart(ctxQ, {
        type: 'doughnut',
        data: {
          labels: Object.keys(qualityData),
          datasets: [{
            data: Object.values(qualityData),
            backgroundColor: ['#F59E0B', '#6366F1', '#10B981'],
            borderColor: '#0E1422',
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', font: { size: 11 } } } }
        }
      });

      chartCategory = new Chart(ctxC, {
        type: 'bar',
        data: {
          labels: Object.keys(categoryData),
          datasets: [{
            label: 'Unidades Vendidas',
            data: Object.values(categoryData),
            backgroundColor: '#6366F1',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#94A3B8' }, grid: { display: false } },
            y: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
          }
        }
      });
    }

    // 3. CATÁLOGO GOOGLE SHEETS
    let currentBrandFilter = 'all';
    let currentCatFilter = 'all';

    function setBrandFilter(val, btn) {
      currentBrandFilter = val;
      document.querySelectorAll('[data-filter-type="brand"]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderCatalogRows();
    }

    function setCatFilter(val, btn) {
      currentCatFilter = val;
      document.querySelectorAll('[data-filter-type="cat"]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderCatalogRows();
    }

    function filterCatalogTable() {
      renderCatalogRows();
    }

    function renderQualityBadge(q) {
      const qUp = (q || '').toUpperCase();
      if (qUp.includes('ORIGINAL_NACIONAL') || qUp.includes('ORIGINAL NACIONAL')) {
        return '<span style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); color:#34D399; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">Original Nacional (90d)</span>';
      } else if (qUp.includes('ORIGINAL_CHINA') || qUp.includes('ORIGINAL CHINA')) {
        return '<span style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">Original China</span>';
      } else if (qUp.includes('PRIMEIRA') || qUp.includes('1ª')) {
        return '<span style="background:rgba(168,85,247,0.15); border:1px solid rgba(168,85,247,0.3); color:#C084FC; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">⭐ 1ª Linha Premium</span>';
      } else {
        return '<span style="background:rgba(251,146,60,0.15); border:1px solid rgba(251,146,60,0.3); color:#FB923C; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">⚡ Paralela Incell</span>';
      }
    }

    function renderStockBadge(p) {
      const isAvail = (typeof p === "object") ? (p.has_stock !== false && (p.stock_quantity > 0 || p.has_stock === true)) : (p > 0);
      if (isAvail) {
        return '<span style="background:rgba(16,185,129,0.18); border:1px solid rgba(16,185,129,0.4); color:#34D399; padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#10B981; display:inline-block;"></span> Em Estoque</span>';
      } else {
        return '<span style="background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); color:#F87171; padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#EF4444; display:inline-block;"></span> Esgotado</span>';
      }
    }

    function renderCatalogRows() {
      const searchEl = document.getElementById('catalog-search');
      const query = (searchEl ? searchEl.value : '').toLowerCase().trim();

      const filtered = (allCatalog || []).filter(p => {
        // Filtro de Texto (Nome, SKU, Modelos Compatíveis, Categoria)
        const nameMatch = (p.name || '').toLowerCase().includes(query);
        const skuMatch = (p.sku || '').toLowerCase().includes(query);
        const catMatch = (p.category || '').toLowerCase().includes(query);
        const modelsMatch = (p.compatible_models || []).some(m => m.toLowerCase().includes(query));
        const matchesQuery = !query || nameMatch || skuMatch || catMatch || modelsMatch;

        // Filtro de Marca
        let matchesBrand = true;
        if (currentBrandFilter !== 'all') {
          const fullStr = `${p.name} ${p.sku} ${(p.compatible_models || []).join(' ')}`.toLowerCase();
          if (currentBrandFilter === 'samsung') matchesBrand = fullStr.includes('samsung') || fullStr.includes('galaxy') || fullStr.includes('tab') || fullStr.includes('sam');
          else if (currentBrandFilter === 'motorola') matchesBrand = fullStr.includes('moto') || fullStr.includes('motorola');
          else if (currentBrandFilter === 'xiaomi') matchesBrand = fullStr.includes('redmi') || fullStr.includes('xiaomi') || fullStr.includes('poco');
          else if (currentBrandFilter === 'apple') matchesBrand = fullStr.includes('iphone') || fullStr.includes('apple') || fullStr.includes('foxconn');
        }

        // Filtro de Categoria
        let matchesCat = true;
        if (currentCatFilter !== 'all') {
          const fullStr = `${p.category} ${p.name}`.toLowerCase();
          if (currentCatFilter === 'tela') matchesCat = fullStr.includes('tela') || fullStr.includes('frontal') || fullStr.includes('touch');
          else if (currentCatFilter === 'bateria') matchesCat = fullStr.includes('bateria');
          else if (currentCatFilter === 'conector') matchesCat = fullStr.includes('conector') || fullStr.includes('placa sub') || fullStr.includes('carga');
        }

        return matchesQuery && matchesBrand && matchesCat;
      });

      const tbody = document.getElementById('catalog-tbody');
      const mobileDeck = document.getElementById('catalog-cards-mobile');
      document.getElementById('catalog-counter').innerText = `${filtered.length} de ${allCatalog.length} peças`;

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhuma peça corresponde aos filtros aplicados.</td></tr>';
        mobileDeck.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhuma peça encontrada.</div>';
        return;
      }

      tbody.innerHTML = filtered.map(p => `
        <tr>
          <td style="font-family: 'JetBrains Mono', monospace; font-size: 0.775rem; color: var(--primary);">${p.sku}</td>
          <td>
            <strong>${escapeHtml(p.name)}</strong>
            ${p.compatible_models && p.compatible_models.length ? `<div style="font-size: 0.72rem; color: #94A3B8; margin-top: 3px;">Modelos: ${escapeHtml(p.compatible_models.join(', '))}</div>` : ''}
          </td>
          <td><span style="font-size: 0.8rem; color: var(--text-dim);">${escapeHtml(p.category || 'Peça')}</span></td>
          <td>${p.has_frame ? '<span style="color:#34D399; font-size: 0.8rem; font-weight: 600;">Com aro</span>' : '<span style="color:var(--text-dim); font-size: 0.8rem;">Sem aro</span>'}</td>
          <td>${renderQualityBadge(p.quality)}</td>
          <td style="font-weight: 700; color: #34D399; font-size: 0.95rem;">R$ ${(p.price || 0).toFixed(2)}</td>
          <td>${renderStockBadge(p)}</td>
        </tr>
      `).join('');

      mobileDeck.innerHTML = filtered.map(p => `
        <div class="customer-card-mobile">
          <div class="card-mobile-top">
            <div>
              <strong>${escapeHtml(p.name)}</strong>
              <div style="font-size: 0.725rem; color: var(--primary); font-family: monospace;">${p.sku}</div>
              ${p.compatible_models && p.compatible_models.length ? `<div style="font-size: 0.7rem; color: #94A3B8; margin-top: 2px;">Compatível: ${escapeHtml(p.compatible_models.join(', '))}</div>` : ''}
            </div>
            <span style="font-weight: 700; color: #34D399; font-size: 1rem;">R$ ${(p.price || 0).toFixed(2)}</span>
          </div>
          <div class="card-mobile-body" style="font-size: 0.75rem; display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
            <div>${renderQualityBadge(p.quality)}</div>
            <div>${renderStockBadge(p)}</div>
          </div>
        </div>
      `).join('');
    }

    async function fetchCatalog() {
      try {
        const res = await fetch('/api/catalog');
        const data = await res.json();
        allCatalog = data.items || [];

        const total = allCatalog.length;
        const healthy = allCatalog.filter(p => p.has_stock !== false && (p.stock_quantity > 0 || p.has_stock === true)).length;
        const outOfStock = allCatalog.filter(p => p.has_stock === false || p.stock_quantity <= 0).length;
        const rate = total > 0 ? Math.round((healthy / total) * 100) : 100;

        document.getElementById('badge-catalog-count').innerText = total;
        document.getElementById('kpi-catalog-total').innerText = total;
        document.getElementById('kpi-catalog-healthy').innerText = healthy;
        document.getElementById('kpi-catalog-critical').innerText = rate + "%";
        document.getElementById('kpi-catalog-out').innerText = outOfStock;

        renderCatalogRows();
      } catch (err) {
        console.error('Erro ao buscar catálogo:', err);
      }
    }

    async function syncGoogleSheets() {
      try {
        showToast('Sincronizando com Google Sheets...', 'success');
        const res = await fetch('/api/sync-sheets', { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'Estoque sincronizado com sucesso!', 'success');
        fetchCatalog();
    checkMasterAISwitch();
        fetchStats();
      } catch (err) {
        showToast('Erro ao sincronizar: ' + err, 'error');
      }
    }

    // 4. SIMULADOR DE CHAT
    async function sendChatMessage() {
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';

      const container = document.getElementById('chat-messages');
      container.innerHTML += `<div class="chat-msg user">${escapeHtml(text)}</div>`;
      container.scrollTop = container.scrollHeight;

      try {
        const res = await fetch('/api/simulator/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        const reply = data.reply || 'Nenhuma resposta gerada.';
        container.innerHTML += `<div class="chat-msg bot">${escapeHtml(reply)}</div>`;
        container.scrollTop = container.scrollHeight;
      } catch (err) {
        container.innerHTML += `<div class="chat-msg bot" style="color: #F43F5E;">Erro na simulação: ${err}</div>`;
        container.scrollTop = container.scrollHeight;
      }
    }

    function clearChat() {
      document.getElementById('chat-messages').innerHTML = `
        <div class="chat-msg bot">
          Opa meu patrão! Tudo beleza? Aqui é da Victor Cell Peças. Pode mandar sua dúvida ou cotação de tela/peça que já vejo no estoque pra você!
        </div>
      `;
    }

    // 5. WHATSAPP QR CODE
    async function fetchWhatsAppQR() {
      const container = document.getElementById('wa-qr-container');
      try {
        const res = await fetch('/api/whatsapp/qrcode');
        const data = await res.json();
        if (data.status === 'connected') {
          container.innerHTML = `
            <div style="padding: 1rem; color: #34D399; font-weight: 700;">
              ✅ Conectado à Evolution API
            </div>
          `;
          document.getElementById('wa-status').innerText = 'WhatsApp Conectado';
          document.getElementById('pill-wa').className = 'pill pill-emerald';
        } else if (data.qrcode) {
          container.innerHTML = `<img src="${data.qrcode}" style="max-width: 220px; border-radius: 10px; background: white; padding: 8px;" />`;
          document.getElementById('wa-status').innerText = 'Escanear QR Code';
          document.getElementById('pill-wa').className = 'pill pill-amber';
        } else {
          container.innerHTML = `<div style="font-size: 0.8rem; color: var(--text-muted);">${data.message || 'Instância em inicialização...'}</div>`;
        }
      } catch (err) {
        container.innerHTML = `<div style="color: #F43F5E; font-size: 0.8rem;">Erro na conexão: ${err}</div>`;
      }
    }

    // 6. CHAVE GEMINI
    async function saveGeminiKey() {
      const input = document.getElementById('gemini-key-input');
      const key = input.value.trim();
      if (!key) {
        showToast('Digite uma chave válida do Google AI Studio!', 'error');
        return;
      }
      try {
        const res = await fetch('/api/settings/gemini-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ key: key })
        });
        const data = await res.json();
        showToast(data.message || 'Chave atualizada com sucesso!', 'success');
        input.value = '';
      } catch (err) {
        showToast('Erro ao atualizar chave: ' + err, 'error');
      }
    }

    // Auxiliares
    function getInitials(name) {
      if (!name) return 'VC';
      const parts = name.trim().split(/\s+/);
      if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }


    // --- DISJUNTOR GERAL DA IA (HARDWARE TOGGLE SWITCH - ZERO EMOJIS) ---
    let isMasterAIActive = true;

    async function checkMasterAISwitch() {
      try {
        const res = await fetch("/api/system/ai-switch");
        const data = await res.json();
        isMasterAIActive = Boolean(data.global_ai_enabled);
        updateMasterAIUI(isMasterAIActive);
      } catch (err) {
        console.error("Erro ao verificar status do disjuntor da IA:", err);
      }
    }

    function updateMasterAIUI(isActive) {
      const btn = document.getElementById("btn-master-ai");
      const label = document.getElementById("label-master-ai");
      const banner = document.getElementById("banner-ai-emergency");

      if (!btn) return;

      if (isActive) {
        btn.className = "master-switch-wrapper master-switch-on";
        btn.title = "Atendimento Automático Ativo. Clique para pausar a IA e assumir no manual.";
        if (label) label.textContent = "IA Automática Ativa";
        if (banner) banner.style.display = "none";
      } else {
        btn.className = "master-switch-wrapper master-switch-off";
        btn.title = "Atendimento Automático Pausado. Clique para reativar as respostas da IA.";
        if (label) label.textContent = "Atendimento Pausado (Manual)";
        if (banner) banner.style.display = "block";
      }
    }

    async function toggleMasterAISwitch() {
      if (isMasterAIActive) {
        const confirmed = confirm(
          "Pausar Atendimento Automático da IA?\n\n" +
          "• Nenhuma resposta automática será enviada no WhatsApp.\n" +
          "• Todas as mensagens recebidas aguardarão resposta manual da equipe.\n\n" +
          "Deseja pausar a IA agora?"
        );
        if (!confirmed) return;
      }

      try {
        showToast("Atualizando estado da IA...", "success");
        const res = await fetch("/api/system/ai-switch/toggle", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ enabled: !isMasterAIActive })
        });
        const data = await res.json();
        isMasterAIActive = Boolean(data.global_ai_enabled);
        updateMasterAIUI(isMasterAIActive);

        if (isMasterAIActive) {
          showToast("Atendimento da IA reativado com sucesso.", "success");
        } else {
          showToast("Atendimento automático pausado. Modo 100% manual ativo.", "error");
        }
      } catch (err) {
        showToast("Erro ao atualizar estado da IA: " + err, "error");
      }
    }

    let currentAuditLevel = '';
    let allAuditLogs = [];
    let auditSearchDebounceTimer = null;

    function filterAuditLevel(level, btn) {
      currentAuditLevel = level;
      document.querySelectorAll('.level-pills .pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderAuditLogs(allAuditLogs);
    }

    function debounceAuditSearch() {
      clearTimeout(auditSearchDebounceTimer);
      auditSearchDebounceTimer = setTimeout(() => {
        renderAuditLogs(allAuditLogs);
      }, 250);
    }

    async function fetchAuditLogs() {
      try {
        const compElem = document.getElementById('select-audit-component');
        const comp = compElem ? compElem.value : '';
        let url = '/api/audit/logs?limit=100';
        if (comp) url += '&component=' + encodeURIComponent(comp);
        const res = await fetch(url);
        const data = await res.json();
        allAuditLogs = data.logs || [];
        const badge = document.getElementById('badge-audit-count');
        if (badge) badge.innerText = allAuditLogs.length;
        renderAuditLogs(allAuditLogs);
      } catch (err) {
        console.error('Erro ao carregar logs de auditoria:', err);
      }
    }

    function renderAuditLogs(logs) {
      const tbody = document.getElementById('audit-table-body');
      const cardsBody = document.getElementById('audit-cards-body');
      if (!tbody) return;

      const qElem = document.getElementById('search-audit');
      const q = (qElem ? qElem.value : '').toLowerCase().trim();
      const filtered = logs.filter(l => {
        if (currentAuditLevel && l.level !== currentAuditLevel) return false;
        if (q) {
          const hay = (l.action + ' ' + (l.actor || '') + ' ' + (l.component || '') + ' ' + JSON.stringify(l.details || {})).toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhum registro de auditoria encontrado para os filtros aplicados.</td></tr>';
        if (cardsBody) cardsBody.innerHTML = '<div style="text-align: center; padding: 1.5rem; color: var(--text-muted);">Nenhum log encontrado.</div>';
        return;
      }

      window.renderedAuditLogs = filtered;

      tbody.innerHTML = filtered.map((l, idx) => {
        const badgeClass = l.level === 'ERROR' ? 'badge-error' : (l.level === 'WARN' ? 'badge-warn' : 'badge-info');
        const d = new Date(l.timestamp);
        const tsFormatted = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' ' + d.toLocaleDateString('pt-BR');
        const det = (typeof l.details === 'object' && l.details) ? l.details : {};
        const detStr = typeof l.details === 'object' ? JSON.stringify(l.details) : String(l.details || '');
        const lat = (l.duration_ms !== null && l.duration_ms !== undefined) ? `${Number(l.duration_ms).toFixed(0)} ms` : '-';

        // Humanizar Ação e Detalhe
        let humanSummary = '';
        const act = l.action || '';
        if (act.includes('DEBOUNCE')) {
          humanSummary = 'Buffer WhatsApp: Mensagem agrupada na janela de digitação';
        } else if (act.includes('ORDER_CREATED') || act.includes('RESERVATION')) {
          humanSummary = `Reserva criada: Peça ${det.sku || ''} para cliente ${formatPhoneBR(det.customer_phone)}`;
        } else if (act.includes('NATIVE_PRODUCT')) {
          humanSummary = `Cadastro de Peça: ${det.sku || ''} (${det.quantity || 0} un no balcão)`;
        } else if (act.includes('STOCK_MOVEMENT')) {
          humanSummary = `Estoque: ${det.movement_type || 'ENTRADA'} de ${det.quantity || 0} un (${det.sku || ''})`;
        } else if (act.includes('PRICE_OVERRIDE')) {
          humanSummary = `Negociação de Preço: Oferta de R$ ${det.offered_price || ''} abaixo do balcão`;
        } else if (act.includes('OUT_OF_STOCK')) {
          humanSummary = `Ruptura: Peça indisponível consultada (${det.sku || ''})`;
        } else if (act.includes('HUMAN_INTERVENTION')) {
          humanSummary = `Transbordo: Balcão solicitado para ${formatPhoneBR(det.customer_phone)}`;
        } else if (act.includes('AI_RESPONSE')) {
          humanSummary = `Resposta da IA gerada (${det.model || 'Gemini 2.5 Flash'})`;
        } else {
          humanSummary = act.replace(/_/g, ' ');
        }

        return `
          <tr>
            <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">${tsFormatted}</td>
            <td><span class="audit-badge ${badgeClass}">${l.level}</span></td>
            <td><span class="audit-badge badge-comp">${l.component}</span></td>
            <td style="font-weight: 600; font-size: 0.8rem; color: #fff;">${l.action}</td>
            <td style="font-family: var(--font-mono); font-size: 0.775rem; color: var(--text-muted);">${l.actor || '-'}</td>
            <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--emerald);">${lat}</td>
            <td>
              <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <span style="font-size: 0.775rem; color: #CBD5E1; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(detStr)}">
                  ${escapeHtml(humanSummary)}
                </span>
                <button class="btn btn-secondary btn-xs" style="padding: 2px 7px; font-size: 0.7rem;" onclick="openJsonViewer(${idx})">
                  JSON Técnico
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');

      if (cardsBody) {
        cardsBody.innerHTML = filtered.map(l => {
          const badgeClass = l.level === 'ERROR' ? 'badge-error' : (l.level === 'WARN' ? 'badge-warn' : 'badge-info');
          const d = new Date(l.timestamp);
          const tsFormatted = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          const detStr = typeof l.details === 'object' ? JSON.stringify(l.details) : String(l.details || '');
          return `
            <div class="mobile-card" style="padding: 0.85rem; margin-bottom: 0.6rem; border-radius: 10px; background: var(--bg-surface); border: 1px solid var(--border-subtle);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span class="audit-badge ${badgeClass}">${l.level}</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.725rem; color: var(--text-muted);">${tsFormatted}</span>
              </div>
              <div style="font-weight: 600; font-size: 0.85rem; color: #fff; margin-bottom: 0.25rem;">${l.action}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.4rem;">Componente: <span class="audit-badge badge-comp">${l.component}</span> | Ator: ${l.actor || '-'}</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #94A3B8; background: rgba(0,0,0,0.3); padding: 0.5rem; border-radius: 6px; word-break: break-all;">${detStr}</div>
            </div>
          `;
        }).join('');
      }
    }

    async function fetchStoreProfile() {
      try {
        const res = await fetch('/api/system/profile');
        const data = await res.json();
        if (data.status === 'success' && data.profile) {
          const p = data.profile;
          if (document.getElementById('prof-store-name')) document.getElementById('prof-store-name').value = p.store_name || '';
          if (document.getElementById('prof-city')) document.getElementById('prof-city').value = p.city || '';
          if (document.getElementById('prof-niche')) document.getElementById('prof-niche').value = p.niche_description || '';
          if (document.getElementById('prof-keywords')) document.getElementById('prof-keywords').value = (p.out_of_scope_keywords || []).join(', ');
          if (document.getElementById('prof-rejection')) document.getElementById('prof-rejection').value = p.rejection_message || '';
          if (document.getElementById('prof-delivery')) document.getElementById('prof-delivery').value = (p.delivery_methods || []).join(', ');
          if (document.getElementById('prof-tone')) document.getElementById('prof-tone').value = p.tone_guidelines || '';
        }
      } catch (err) {
        console.error('Erro ao carregar perfil da loja:', err);
      }
    }

    async function saveStoreProfile(e) {
      if (e) e.preventDefault();
      try {
        const payload = {
          store_name: document.getElementById('prof-store-name').value,
          city: document.getElementById('prof-city').value,
          niche_description: document.getElementById('prof-niche').value,
          out_of_scope_keywords: document.getElementById('prof-keywords').value,
          rejection_message: document.getElementById('prof-rejection').value,
          delivery_methods: document.getElementById('prof-delivery').value,
          tone_guidelines: document.getElementById('prof-tone').value,
        };
        const res = await fetch('/api/system/profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        const data = await res.json();
        if (data.status === 'success') {
          showToast('Diretrizes comerciais salvas com sucesso!', 'success');
          fetchAuditLogs();
        } else {
          showToast('Erro ao salvar: ' + (data.message || 'Falha'), 'error');
        }
      } catch (err) {
        showToast('Erro de conexão ao salvar diretrizes: ' + err, 'error');
      }
    }

    // ==========================================
    // ERP NATIVO & ENTRADA COGNITIVA DE ESTOQUE
    // ==========================================
    let currentErpProposal = null;

    function demoVoiceStockEntry() {
      const input = document.getElementById('erp-voice-input');
      if (input) {
        input.value = 'Entraram 10 telas do Tab A8 a 110 do fornecedor Peças Brasil e 5 conectores do T295 a 15, NF 4580';
      }
    }

    async function loadErpSummary() {
      try {
        const res = await fetch('/api/erp/stock/summary');
        const data = await res.json();
        if (data.status === 'success' && data.metrics) {
          const m = data.metrics;
          if (document.getElementById('erp-total-skus')) document.getElementById('erp-total-skus').textContent = m.total_skus || 0;
          if (document.getElementById('erp-total-units')) document.getElementById('erp-total-units').textContent = m.total_units || 0;
          if (document.getElementById('erp-total-cost')) document.getElementById('erp-total-cost').textContent = 'R$ ' + (m.total_cost || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
          if (document.getElementById('erp-total-retail')) document.getElementById('erp-total-retail').textContent = 'R$ ' + (m.total_retail || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 });
        }
      } catch (err) {
        console.error('Erro ao carregar resumo de estoque do ERP:', err);
      }
    }

    async function loadErpMovements() {
      try {
        const res = await fetch('/api/erp/stock/movements?limit=30');
        const data = await res.json();
        const tbody = document.getElementById('erp-movements-tbody');
        if (!tbody) return;

        if (data.status === 'success' && data.movements && data.movements.length > 0) {
          tbody.innerHTML = data.movements.map(m => {
            const dateStr = new Date(m.created_at).toLocaleString('pt-BR');
            const typeBadge = m.movement_type.includes('ENTRADA')
              ? '<span style="background: rgba(16,185,129,0.15); color: #34D399; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">' + m.movement_type + '</span>'
              : '<span style="background: rgba(239,68,68,0.15); color: #F87171; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">' + m.movement_type + '</span>';
            const costFormatted = m.unit_cost ? 'R$ ' + Number(m.unit_cost).toFixed(2) : '-';
            return '<tr>' +
              '<td style="font-size: 0.8rem; color: var(--text-muted);">' + dateStr + '</td>' +
              '<td>' + typeBadge + '</td>' +
              '<td style="font-family: monospace; font-weight: 600;">' + m.sku + '</td>' +
              '<td style="font-weight: 700;">' + m.quantity + '</td>' +
              '<td>' + costFormatted + '</td>' +
              '<td style="font-size: 0.8rem;">' + (m.invoice_number || '-') + '</td>' +
              '<td style="font-size: 0.8rem;">' + (m.operator || 'Sistema') + '</td>' +
              '<td style="font-size: 0.8rem; color: var(--text-muted);">' + (m.notes || '-') + '</td>' +
            '</tr>';
          }).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding: 1.5rem;">Nenhuma movimentação registrada no ERP até o momento.</td></tr>';
        }
      } catch (err) {
        console.error('Erro ao carregar movimentações do ERP:', err);
      }
    }

    async function submitVoiceStockEntry() {
      const input = document.getElementById('erp-voice-input');
      const text = input ? input.value.trim() : '';
      if (!text) {
        showToast('Digite ou fale o texto de entrada de estoque.', 'error');
        return;
      }

      const btn = document.getElementById('btn-process-voice');
      if (btn) btn.disabled = true;
      showToast('Processando entrada com inteligência artificial...', 'success');

      try {
        const res = await fetch('/api/erp/stock/voice-entry', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ spoken_text: text })
        });
        const data = await res.json();
        if (data.status === 'success' && data.proposal) {
          currentErpProposal = data.proposal;
          renderErpProposal(data.proposal);
          showToast('Proposta extraída! Confira os itens abaixo antes de efetivar.', 'success');
        } else {
          showToast('Erro ao interpretar áudio/texto: ' + (data.detail || data.message || 'Falha'), 'error');
        }
      } catch (err) {
        showToast('Erro na requisição: ' + err, 'error');
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    async function submitOcrStockEntry() {
      const fileInput = document.getElementById('erp-photo-input');
      if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        showToast('Selecione uma imagem de etiqueta ou comprovante.', 'error');
        return;
      }
      const file = fileInput.files[0];
      const reader = new FileReader();
      const btn = document.getElementById('btn-process-ocr');
      if (btn) btn.disabled = true;
      showToast('Lendo imagem com OCR e IA multimodal...', 'success');

      reader.onload = async () => {
        try {
          const b64 = reader.result.split(',')[1];
          const res = await fetch('/api/erp/stock/ocr-entry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image_base64: b64 })
          });
          const data = await res.json();
          if (data.status === 'success' && data.proposal) {
            currentErpProposal = data.proposal;
            renderErpProposal(data.proposal);
            showToast('Dados da etiqueta extraídos com sucesso!', 'success');
          } else {
            showToast('Falha no OCR: ' + (data.detail || 'Não foi possível ler a etiqueta'), 'error');
          }
        } catch (err) {
          showToast('Erro ao processar imagem: ' + err, 'error');
        } finally {
          if (btn) btn.disabled = false;
        }
      };
      reader.readAsDataURL(file);
    }

    function renderErpProposal(proposal) {
      const card = document.getElementById('erp-proposal-card');
      const details = document.getElementById('erp-proposal-details');
      const tbody = document.getElementById('erp-proposal-tbody');
      if (!card || !tbody) return;

      if (details) {
        details.innerHTML = '<strong>Fornecedor:</strong> ' + (proposal.supplier_name || 'Não identificado') + ' | <strong>NF / Lote:</strong> ' + (proposal.invoice_number || 'S/N') + ' | <strong>Total de Itens:</strong> ' + proposal.total_items + ' un | <strong>Custo Total:</strong> R$ ' + (proposal.total_cost || 0).toFixed(2);
      }

      if (proposal.items && proposal.items.length > 0) {
        tbody.innerHTML = proposal.items.map(item => '<tr>' +
          '<td style="font-family: monospace; font-weight: 600;">' + item.sku + '</td>' +
          '<td>' + (item.model_name || item.name) + '</td>' +
          '<td><span style="font-size:0.75rem; background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:4px;">' + (item.category || 'Peça') + '</span></td>' +
          '<td style="font-weight: 700; color: #34D399;">+' + item.quantity_to_add + '</td>' +
          '<td>' + (item.current_stock ?? '-') + '</td>' +
          '<td style="font-weight: 700;">' + (item.projected_stock ?? '-') + '</td>' +
          '<td>R$ ' + (item.unit_cost || 0).toFixed(2) + '</td>' +
          '<td style="color: #60A5FA;">R$ ' + (item.suggested_retail_price || 0).toFixed(2) + '</td>' +
        '</tr>').join('');
      } else {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Nenhum item detectado.</td></tr>';
      }

      card.style.display = 'block';
    }

    async function confirmCurrentStockEntry() {
      if (!currentErpProposal) {
        showToast('Nenhuma proposta de entrada ativa para confirmar.', 'error');
        return;
      }
      const btn = document.getElementById('btn-confirm-stock');
      if (btn) btn.disabled = true;

      try {
        const res = await fetch('/api/erp/stock/confirm-entry', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(currentErpProposal)
        });
        const data = await res.json();
        if (data.status === 'success') {
          showToast('Entrada de estoque confirmada e registrada com sucesso!', 'success');
          const card = document.getElementById('erp-proposal-card');
          if (card) card.style.display = 'none';
          currentErpProposal = null;
          const input = document.getElementById('erp-voice-input');
          if (input) input.value = '';
          loadErpSummary();
          loadErpMovements();
          fetchCatalog();
          fetchAuditLogs();
        } else {
          showToast('Erro ao confirmar entrada: ' + (data.message || data.detail || 'Falha'), 'error');
        }
      } catch (err) {
        showToast('Erro de conexão ao confirmar entrada: ' + err, 'error');
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    function refreshAll() {
      fetchAIPipelineStatus();
      showToast('Atualizando dados...', 'success');
      fetchConversations();
      fetchStats();
      fetchCatalog();
    checkMasterAISwitch();
      fetchWhatsAppQR();
    }

    // Inicialização ao Carregar
    fetchConversations();
    fetchStats();
    fetchCatalog();
    fetchAuditLogs();
    checkMasterAISwitch();
    fetchWhatsAppQR();

    // Auto-refresh suave a cada 20 segundos
    setInterval(() => {
      fetchConversations();
      fetchStats();
    }, 20000);
  </script>
</body>
</html>"""


def render_login_html(error_message: Optional[str] = None) -> str:
    error_banner = ""
    if error_message:
        error_banner = f"""
        <div class="login-alert">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{error_message}</span>
        </div>
        """
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Login • Victor Cell Painel Executivo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #0B0F19;
      --card-bg: rgba(17, 24, 39, 0.85);
      --card-border: rgba(255, 255, 255, 0.08);
      --text: #F3F4F6;
      --text-muted: #9CA3AF;
      --primary: #10B981;
      --primary-hover: #059669;
      --danger: #EF4444;
      --danger-bg: rgba(239, 68, 68, 0.12);
      --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: var(--font-sans);
      background-color: var(--bg);
      background-image:
        radial-gradient(at 0% 0%, rgba(16, 185, 129, 0.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.12) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }}
    .login-wrapper {{
      width: 100%;
      max-width: 420px;
    }}
    .login-card {{
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      padding: 2.25rem 2rem;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05);
    }}
    .brand-header {{
      text-align: center;
      margin-bottom: 2rem;
    }}
    .brand-icon {{
      width: 56px;
      height: 56px;
      border-radius: 14px;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(99, 102, 241, 0.2));
      border: 1px solid rgba(16, 185, 129, 0.4);
      display: inline-flex;
      align-items: center;
      justify-content: center;
      font-size: 1.8rem;
      margin-bottom: 1rem;
      box-shadow: 0 0 25px rgba(16, 185, 129, 0.25);
    }}
    .brand-title {{
      font-size: 1.5rem;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #FFFFFF;
    }}
    .brand-title span {{
      color: var(--primary);
    }}
    .brand-subtitle {{
      color: var(--text-muted);
      font-size: 0.85rem;
      margin-top: 0.35rem;
    }}
    .login-alert {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      background: var(--danger-bg);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #FCA5A5;
      padding: 0.85rem 1rem;
      border-radius: 10px;
      font-size: 0.875rem;
      margin-bottom: 1.5rem;
      animation: shake 0.3s ease-in-out;
    }}
    @keyframes shake {{
      0%, 100% {{ transform: translateX(0); }}
      25% {{ transform: translateX(-4px); }}
      75% {{ transform: translateX(4px); }}
    }}
    .form-group {{
      margin-bottom: 1.25rem;
    }}
    .form-label {{
      display: block;
      font-size: 0.8rem;
      font-weight: 600;
      color: #D1D5DB;
      margin-bottom: 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .input-wrapper {{
      position: relative;
    }}
    .input-icon {{
      position: absolute;
      left: 1rem;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      display: flex;
      align-items: center;
      pointer-events: none;
    }}
    .input-field {{
      width: 100%;
      background: rgba(11, 15, 25, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 10px;
      padding: 0.85rem 1rem 0.85rem 2.75rem;
      color: #FFFFFF;
      font-family: inherit;
      font-size: 0.95rem;
      transition: all 0.2s;
    }}
    .input-field:focus {{
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
      background: rgba(11, 15, 25, 0.9);
    }}
    .toggle-pwd {{
      position: absolute;
      right: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      background: transparent;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      padding: 0.25rem;
      display: flex;
      align-items: center;
      border-radius: 6px;
    }}
    .toggle-pwd:hover {{
      color: #FFFFFF;
    }}
    .form-remember {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1.5rem;
      font-size: 0.85rem;
      color: var(--text-muted);
    }}
    .remember-label {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      user-select: none;
    }}
    .remember-label input[type="checkbox"] {{
      accent-color: var(--primary);
      width: 16px;
      height: 16px;
      cursor: pointer;
    }}
    .btn-submit {{
      width: 100%;
      background: var(--primary);
      color: #042F2E;
      border: none;
      border-radius: 10px;
      padding: 0.95rem;
      font-size: 0.95rem;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
      min-height: 48px;
    }}
    .btn-submit:hover {{
      background: var(--primary-hover);
      transform: translateY(-1px);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
    }}
    .btn-submit:active {{
      transform: translateY(0);
    }}
    .login-footer {{
      margin-top: 1.75rem;
      text-align: center;
      font-size: 0.75rem;
      color: #6B7280;
    }}
    .login-footer p {{
      margin-top: 0.25rem;
    }}
  </style>
</head>
<body>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="brand-header">
        <div class="brand-icon">⚡</div>
        <h1 class="brand-title">Victor Cell <span>Pro</span></h1>
        <p class="brand-subtitle">Acesso Restrito ao Gestor & Balcão</p>
      </div>

      {error_banner}

      <form action="/login" method="POST">
        <div class="form-group">
          <label class="form-label" for="username">Usuário</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            </span>
            <input type="text" id="username" name="username" class="input-field" placeholder="Ex: admin" required autofocus autocomplete="username">
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Senha de Acesso</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            </span>
            <input type="password" id="password" name="password" class="input-field" placeholder="••••••••" required autocomplete="current-password">
            <button type="button" class="toggle-pwd" id="toggle-pwd-btn" onclick="togglePasswordVisibility()" aria-label="Mostrar senha">
              <svg id="eye-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
            </button>
          </div>
        </div>

        <div class="form-remember">
          <label class="remember-label">
            <input type="checkbox" name="remember_me" value="true" checked>
            <span>Lembrar neste aparelho</span>
          </label>
        </div>

        <button type="submit" class="btn-submit">
          <span>Entrar no Painel</span>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
        </button>
      </form>

      <div class="login-footer">
        <p>Autenticação HMAC SHA-256 Criptografada</p>
        <p>Victor Cell • Todos os direitos reservados</p>
      </div>
    </div>
  </div>

  <script>
    function togglePasswordVisibility() {{
      const pwdInput = document.getElementById('password');
      const eyeIcon = document.getElementById('eye-icon');
      if (pwdInput.type === 'password') {{
        pwdInput.type = 'text';
        eyeIcon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line>';
      }} else {{
        pwdInput.type = 'password';
        eyeIcon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle>';
      }}
    }}
  </script>
</body>
</html>"""
