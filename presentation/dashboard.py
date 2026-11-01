"""
Executive Web Dashboard & Intelligence Hub for Victor Cell.
100% Free, Open-Source & Self-Hosted.
Includes:
- Responsive Mobile-First & Tablet-Optimized Design (Big Tech & Power BI styling)
- Real-time Human vs. AI Control Center with Customer Names, Formatted Phones & Active Parts
- Uber Flash Expedition Queue & Orders Management with 1-click Power BI CSV Export
- Live Google Sheets Catalog viewer & Instant Sync
- Best-Selling Parts Ranking & FAQ Intelligence
- Interactive Chart.js Visualizations (Quality distribution & Category breakdown)
- WhatsApp Live Pairing (QR Code & Status)
- Live Customer Message Simulator with instant bot responses
- Gemini AI Quota Manager, Key Tester & Rate Limit Inspector
"""

from typing import Optional

def render_dashboard_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Victor Cell • Painel Executivo & Balcão Inteligente</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-base: #070A0F;
      --bg-surface: #0E1422;
      --bg-surface-elevated: #141C30;
      --bg-card: rgba(14, 20, 34, 0.88);
      --bg-glass: rgba(20, 28, 48, 0.65);
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-focus: rgba(99, 102, 241, 0.45);
      --primary: #6366F1;
      --primary-hover: #4F46E5;
      --primary-glow: rgba(99, 102, 241, 0.28);
      --emerald: #10B981;
      --emerald-glow: rgba(16, 185, 129, 0.25);
      --amber: #F59E0B;
      --amber-glow: rgba(245, 158, 11, 0.25);
      --cyan: #06B6D4;
      --cyan-glow: rgba(6, 182, 212, 0.25);
      --rose: #F43F5E;
      --purple: #8B5CF6;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
      --radius-sm: 8px;
      --radius-md: 14px;
      --radius-lg: 20px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }

    html {
      overflow-x: hidden;
      max-width: 100vw;
    }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      min-height: 100vh;
      max-width: 100vw;
      overflow-x: hidden;
      display: flex;
      flex-direction: column;
      background-image:
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.14) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.10) 0px, transparent 45%),
        radial-gradient(at 50% 100%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
      background-attachment: fixed;
      font-size: 14px;
      line-height: 1.5;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.25); }

    /* Header Executivo */
    header {
      padding: 0.85rem 1.5rem;
      background: rgba(11, 15, 26, 0.92);
      backdrop-filter: blur(20px);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
      gap: 1rem;
    }

    .brand { display: flex; align-items: center; gap: 0.75rem; text-decoration: none; color: inherit; }
    .brand-icon {
      width: 42px; height: 42px; border-radius: 12px;
      background: linear-gradient(135deg, var(--primary), #4338CA);
      display: flex; align-items: center; justify-content: center;
      font-size: 1.35rem; box-shadow: 0 0 16px var(--primary-glow);
      flex-shrink: 0;
    }
    .brand-text h1 { font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em; display: flex; align-items: center; gap: 0.5rem; }
    .brand-text h1 span { color: var(--emerald); }
    .brand-text p { font-size: 0.725rem; color: var(--text-muted); font-weight: 500; }

    .header-pills { display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap; }
    .pill {
      display: inline-flex; align-items: center; gap: 0.4rem;
      padding: 0.35rem 0.75rem; border-radius: 999px;
      font-size: 0.75rem; font-weight: 600;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      white-space: nowrap;
    }
    .pill-dot { width: 7px; height: 7px; border-radius: 50%; }
    .pill-emerald { color: #34D399; background: rgba(16, 185, 129, 0.12); border-color: rgba(16, 185, 129, 0.3); }
    .pill-emerald .pill-dot { background: #10B981; box-shadow: 0 0 8px #10B981; }
    .pill-amber { color: #FBBF24; background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.3); }
    .pill-amber .pill-dot { background: #F59E0B; box-shadow: 0 0 8px #F59E0B; }

    /* Barra de Navegação em Abas (Scroll Suave no Mobile) */
    .nav-bar-wrapper {
      background: rgba(14, 20, 34, 0.85);
      border-bottom: 1px solid var(--border-subtle);
      position: sticky;
      top: 61px;
      z-index: 40;
      backdrop-filter: blur(16px);
      padding: 0.4rem 1.25rem;
    }
    .nav-tabs {
      display: flex; gap: 0.5rem; overflow-x: auto; scrollbar-width: none;
      -webkit-overflow-scrolling: touch; padding-bottom: 2px;
      max-width: 1400px; margin: 0 auto;
    }
    .nav-tabs::-webkit-scrollbar { display: none; }
    .nav-tab {
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.55rem 1rem; border-radius: 10px;
      background: transparent; border: 1px solid transparent;
      color: var(--text-muted); font-size: 0.825rem; font-weight: 600;
      cursor: pointer; white-space: nowrap; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      flex-shrink: 0;
    }
    .nav-tab:hover { background: rgba(255, 255, 255, 0.05); color: #fff; }
    .nav-tab.active {
      background: rgba(99, 102, 241, 0.18);
      color: #fff;
      border-color: rgba(99, 102, 241, 0.4);
      box-shadow: 0 0 14px var(--primary-glow);
    }
    .tab-badge {
      padding: 0.15rem 0.45rem; border-radius: 6px; font-size: 0.7rem; font-weight: 700;
      background: rgba(255, 255, 255, 0.12); color: #E2E8F0;
    }
    .nav-tab.active .tab-badge { background: var(--primary); color: #fff; }

    /* Container Principal */
    main {
      flex: 1; padding: 1.25rem; max-width: 1400px; width: 100%; margin: 0 auto;
    }

    .tab-pane { display: none; }
    .tab-pane.active { display: block; animation: fadeIn 0.25s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

    /* Grid de KPIs */
    .kpi-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 1rem; margin-bottom: 1.25rem;
    }
    .kpi-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 1.15rem;
      display: flex; flex-direction: column; justify-content: space-between;
      position: relative; overflow: hidden;
      backdrop-filter: blur(12px);
      transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: rgba(255, 255, 255, 0.15); }
    .kpi-card::before {
      content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
      background: var(--primary); opacity: 0; transition: opacity 0.2s;
    }
    .kpi-card:hover::before { opacity: 1; }
    .kpi-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
    .kpi-title { font-size: 0.775rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi-icon {
      width: 34px; height: 34px; border-radius: 9px;
      display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
    }
    .kpi-val { font-size: 1.75rem; font-weight: 800; letter-spacing: -0.03em; color: #fff; margin-bottom: 0.2rem; }
    .kpi-sub { font-size: 0.75rem; color: var(--text-dim); display: flex; align-items: center; gap: 0.35rem; }
    .trend-up { color: #34D399; font-weight: 600; }

    /* Seção / Card Padrão */
    .section-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      overflow: hidden; margin-bottom: 1.25rem;
      backdrop-filter: blur(14px);
    }
    .section-toolbar {
      padding: 1rem 1.25rem; border-bottom: 1px solid var(--border-subtle);
      display: flex; justify-content: space-between; align-items: center;
      gap: 1rem; flex-wrap: wrap; background: rgba(0, 0, 0, 0.15);
    }
    .section-title-group { display: flex; align-items: center; gap: 0.6rem; }
    .section-title { font-size: 1rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 0.45rem; }
    .badge-count {
      padding: 0.15rem 0.55rem; border-radius: 999px;
      font-size: 0.725rem; font-weight: 700; background: rgba(255, 255, 255, 0.08); color: var(--text-muted);
    }
    .toolbar-actions { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }

    /* Inputs e Botões */
    .search-input {
      background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-subtle);
      padding: 0.45rem 0.85rem; border-radius: 8px; color: #fff; font-size: 0.8rem;
      outline: none; transition: all 0.2s; min-width: 180px;
    }
    .search-input:focus { border-color: var(--primary); box-shadow: 0 0 10px var(--primary-glow); background: rgba(0, 0, 0, 0.2); }

    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 0.45rem;
      padding: 0.45rem 0.9rem; border-radius: 8px; font-size: 0.8rem; font-weight: 600;
      border: 1px solid transparent; cursor: pointer; transition: all 0.18s;
      white-space: nowrap; user-select: none;
    }
    .btn-primary { background: var(--primary); color: #fff; box-shadow: 0 2px 8px var(--primary-glow); }
    .btn-primary:hover { background: var(--primary-hover); transform: translateY(-1px); }
    .btn-emerald { background: var(--emerald); color: #000; font-weight: 700; box-shadow: 0 2px 8px var(--emerald-glow); }
    .btn-emerald:hover { background: #059669; color: #fff; }
    .btn-amber { background: rgba(245, 158, 11, 0.18); color: #FBBF24; border-color: rgba(245, 158, 11, 0.35); }
    .btn-amber:hover { background: rgba(245, 158, 11, 0.3); }
    .btn-secondary { background: rgba(255, 255, 255, 0.06); color: #E2E8F0; border-color: var(--border-subtle); }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.12); color: #fff; }
    .btn-sm { padding: 0.3rem 0.65rem; font-size: 0.75rem; border-radius: 6px; }

    /* Dual-Mode: Tabela para Desktop/Tablet e Cards Touch para Mobile */
    .table-container { width: 100%; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    thead th {
      padding: 0.85rem 1rem; font-size: 0.725rem; font-weight: 700;
      color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border-subtle); background: rgba(0, 0, 0, 0.25);
      white-space: nowrap;
    }
    tbody tr {
      border-bottom: 1px solid var(--border-subtle); transition: background-color 0.15s;
    }
    tbody tr:hover { background-color: rgba(255, 255, 255, 0.03); }
    tbody td {
      padding: 0.9rem 1rem; font-size: 0.825rem; color: #CBD5E1; vertical-align: middle;
    }

    /* Card Deck no Mobile */
    .mobile-card-deck { display: none; flex-direction: column; gap: 0.75rem; padding: 0.85rem; }
    .customer-card-mobile {
      background: rgba(255, 255, 255, 0.025);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 0.9rem;
      display: flex; flex-direction: column; gap: 0.65rem;
    }
    .card-mobile-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
    .card-mobile-body { display: flex; flex-direction: column; gap: 0.35rem; }
    .card-mobile-actions { display: flex; gap: 0.5rem; margin-top: 0.25rem; }
    .card-mobile-actions .btn { flex: 1; padding: 0.55rem; font-size: 0.8rem; }

    /* Célula de Cliente Rica */
    .user-profile { display: flex; align-items: center; gap: 0.75rem; }
    .user-avatar {
      width: 38px; height: 38px; border-radius: 10px;
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.3));
      border: 1px solid rgba(99, 102, 241, 0.4);
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 0.85rem; color: #A5B4FC;
      flex-shrink: 0;
    }
    .user-info { display: flex; flex-direction: column; }
    .user-name { font-weight: 700; color: #fff; font-size: 0.875rem; display: flex; align-items: center; gap: 0.35rem; }
    .user-phone {
      font-size: 0.75rem; color: #34D399; font-family: 'JetBrains Mono', monospace;
      text-decoration: none; display: inline-flex; align-items: center; gap: 0.25rem; font-weight: 600;
    }
    .user-phone:hover { text-decoration: underline; color: #6EE7B7; }

    /* Pills e Tags de Peças e Status */
    .part-pill {
      display: inline-flex; align-items: center; gap: 0.35rem;
      padding: 0.25rem 0.6rem; border-radius: 6px;
      font-size: 0.75rem; font-weight: 600;
      background: rgba(99, 102, 241, 0.12); color: #C7D2FE;
      border: 1px solid rgba(99, 102, 241, 0.25);
      max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }
    .status-pill {
      display: inline-flex; align-items: center; gap: 0.35rem;
      padding: 0.25rem 0.65rem; border-radius: 999px;
      font-size: 0.75rem; font-weight: 700; white-space: nowrap;
    }
    .status-robot { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.35); }
    .status-human { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.35); }
    .status-waiting { background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.35); }

    /* Insights Grid */
    .charts-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 1.25rem; margin-bottom: 1.25rem;
    }
    .chart-card {
      background: var(--bg-card); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md); padding: 1.25rem; backdrop-filter: blur(12px);
    }
    .chart-card h3 { font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }

    /* Simulador de Chat */
    .simulator-wrapper {
      display: grid; grid-template-columns: 1fr 340px; gap: 1.25rem;
    }
    .chat-box {
      background: rgba(0, 0, 0, 0.3); border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md); height: 440px; display: flex; flex-direction: column;
    }
    .chat-messages {
      flex: 1; padding: 1rem; overflow-y: auto; display: flex; flex-direction: column; gap: 0.75rem;
    }
    .chat-msg {
      max-width: 80%; padding: 0.65rem 0.95rem; border-radius: 12px;
      font-size: 0.85rem; line-height: 1.45; position: relative; word-break: break-word;
    }
    .chat-msg.user {
      align-self: flex-end; background: #005C4B; color: #E9EDEF; border-bottom-right-radius: 2px;
    }
    .chat-msg.bot {
      align-self: flex-start; background: #202C33; color: #E9EDEF; border-bottom-left-radius: 2px;
    }
    .chat-input-bar {
      padding: 0.75rem; border-top: 1px solid var(--border-subtle);
      display: flex; gap: 0.5rem; background: rgba(14, 20, 34, 0.95);
    }

    /* Toast */
    #toast {
      position: fixed; bottom: 20px; right: 20px; z-index: 9999;
      background: #1E293B; color: #fff; border: 1px solid var(--border-subtle);
      padding: 0.75rem 1.25rem; border-radius: 10px; font-weight: 600; font-size: 0.85rem;
      box-shadow: 0 10px 25px rgba(0,0,0,0.6); display: none; align-items: center; gap: 0.6rem;
    }

    /* Responsividade Detalhada (Mobile & Tablet) */
    @media (max-width: 768px) {
      header { padding: 0.75rem 1rem; flex-direction: column; align-items: stretch; gap: 0.6rem; }
      .header-pills { justify-content: space-between; }
      .nav-bar-wrapper { top: 108px; padding: 0.35rem 0.75rem; }
      main { padding: 0.75rem; }
      .kpi-grid { grid-template-columns: repeat(2, 1fr); gap: 0.65rem; }
      .kpi-card { padding: 0.85rem; }
      .kpi-val { font-size: 1.35rem; }
      .section-toolbar { flex-direction: column; align-items: stretch; gap: 0.75rem; }
      .toolbar-actions { justify-content: stretch; }
      .toolbar-actions .btn, .toolbar-actions .search-input { flex: 1; }
      
      /* Oculta tabelas grandes no celular e ativa os cards touch */
      .table-container { display: none; }
      .mobile-card-deck { display: flex; }

      .charts-grid { grid-template-columns: 1fr; }
      .simulator-wrapper { grid-template-columns: 1fr; }
    }

    @media (min-width: 769px) and (max-width: 1024px) {
      /* Tablet */
      header { padding: 0.85rem 1.25rem; }
      .kpi-grid { grid-template-columns: repeat(2, 1fr); }
      .simulator-wrapper { grid-template-columns: 1fr; }
      .table-container { display: block; }
      .mobile-card-deck { display: none; }
    }
  
    /* --- ESTILOS DO COPILOTO IA DO GESTOR --- */
    .quick-chips-wrapper {
      margin-bottom: 1.25rem;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 0.85rem 1rem;
    }
    .chips-label {
      display: block;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 0.6rem;
    }
    .chips-scroller {
      display: flex;
      gap: 0.6rem;
      overflow-x: auto;
      padding-bottom: 0.25rem;
      -webkit-overflow-scrolling: touch;
    }
    .chips-scroller::-webkit-scrollbar {
      height: 4px;
    }
    .chips-scroller::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
    }
    .catalog-filter-btn {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border-subtle);
      color: #94A3B8;
      border-radius: 999px;
      padding: 0.25rem 0.65rem;
      font-size: 0.725rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .catalog-filter-btn:hover {
      background: rgba(255, 255, 255, 0.1);
      color: #FFFFFF;
      border-color: rgba(255, 255, 255, 0.25);
    }
    .catalog-filter-btn.active {
      background: rgba(16, 185, 129, 0.2);
      border-color: #10B981;
      color: #34D399;
    }
    .chip-btn {
      background: rgba(16, 185, 129, 0.08);
      color: #A7F3D0;
      border: 1px solid rgba(16, 185, 129, 0.25);
      border-radius: 999px;
      padding: 0.45rem 0.95rem;
      font-size: 0.82rem;
      font-weight: 600;
      white-space: nowrap;
      cursor: pointer;
      transition: all 0.2s;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
    }
    .chip-btn:hover {
      background: rgba(16, 185, 129, 0.2);
      border-color: var(--primary);
      color: #FFFFFF;
      transform: translateY(-1px);
    }
    .chip-btn:active {
      transform: translateY(0);
    }

    .copilot-chat-container {
      background: #0B0F19;
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .copilot-chat-container {
      background: #0B0F19;
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
      max-width: 100%;
    }
    .copilot-messages {
      height: clamp(340px, 50vh, 520px);
      overflow-y: auto;
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
      overscroll-behavior-y: contain;
    }
    .copilot-input-bar {
      display: flex;
      gap: 0.75rem;
      padding: 1rem;
      background: #111827;
      border-top: 1px solid var(--border-subtle);
      position: sticky;
      bottom: 0;
      z-index: 10;
    }
    .copilot-msg {
      display: flex;
      gap: 0.85rem;
      max-width: 90%;
      animation: fadeIn 0.3s ease-in-out;
    }
    .copilot-msg.bot {
      align-self: flex-start;
    }
    .copilot-msg.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }
    .copilot-avatar {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(99, 102, 241, 0.25));
      border: 1px solid rgba(16, 185, 129, 0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      flex-shrink: 0;
      box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    .copilot-user-avatar {
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      flex-shrink: 0;
    }
    .copilot-bubble {
      background: #111827;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 14px;
      padding: 1rem 1.25rem;
      color: #E5E7EB;
      font-size: 0.92rem;
      line-height: 1.6;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .copilot-msg.user .copilot-bubble {
      background: rgba(16, 185, 129, 0.12);
      border-color: rgba(16, 185, 129, 0.3);
      color: #FFFFFF;
    }
    .copilot-bubble p {
      margin-bottom: 0.5rem;
    }
    .copilot-bubble p:last-child {
      margin-bottom: 0;
    }
    .copilot-bubble ul, .copilot-bubble ol {
      margin-left: 1.25rem;
      margin-bottom: 0.5rem;
    }
    .copilot-bubble li {
      margin-bottom: 0.25rem;
    }
    .copilot-bubble strong {
      color: #FFFFFF;
    }
    .copilot-input-bar {
      display: flex;
      gap: 0.75rem;
      padding: 1rem;
      background: #111827;
      border-top: 1px solid var(--border-subtle);
    }
    .copilot-input-field {
      flex: 1;
      background: #0B0F19;
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 10px;
      padding: 0.85rem 1.15rem;
      color: #FFFFFF;
      font-family: inherit;
      font-size: 0.95rem;
      transition: all 0.2s;
    }
    .copilot-input-field:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }
    .copilot-loading-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--primary);
      margin-right: 0.5rem;
      animation: pulseDot 1s infinite alternate;
    }
    @keyframes pulseDot {
      0% { opacity: 0.3; transform: scale(0.8); }
      100% { opacity: 1; transform: scale(1.2); }
    }

</style>
</head>
<body>

  <!-- TOAST NOTIFICATION -->
  <div id="toast">
    <span id="toast-icon">✅</span>
    <span id="toast-msg">Ação executada com sucesso!</span>
  </div>

  <!-- HEADER EXECUTIVO -->
  <header>
    <a href="#" class="brand">
      <div class="brand-icon">📱</div>
      <div class="brand-text">
        <h1>Victor Cell <span>Pro</span></h1>
        <p>Painel de Balcão & Inteligência de Expedição</p>
      </div>
    </a>

    <div class="header-pills">
      <div class="pill pill-emerald" id="pill-store">
        <span class="pill-dot"></span>
        <span id="store-status">🟢 Balcão Aberto</span>
      </div>
      <div class="pill pill-emerald" id="pill-wa">
        <span class="pill-dot"></span>
        <span id="wa-status">WhatsApp Conectado</span>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="refreshAll()" title="Recarregar dados">
        🔄 Atualizar
      </button>
      <a href="/logout" class="btn btn-secondary btn-sm" style="color: #EF4444; border-color: rgba(239, 68, 68, 0.3); text-decoration: none;" title="Sair do painel">
        🚪 Sair
      </a>
    </div>
  </header>

  <!-- NAVEGAÇÃO EM ABAS (RESPONSIVA) -->
  <div class="nav-bar-wrapper">
    <div class="nav-tabs">
      <button class="nav-tab active" onclick="switchTab('conversations')">
        💬 Central de Atendimento & Balcão
        <span class="tab-badge" id="badge-convs-count">0</span>
      </button>
      <button class="nav-tab" onclick="switchTab('orders')">
        🛵 Expedição & Entregas Expressas
        <span class="tab-badge" id="badge-orders-count">0</span>
      </button>
      <button class="nav-tab" onclick="switchTab('overview')">
        📈 Indicadores & Vendas
      </button>
      <button class="nav-tab" onclick="switchTab('catalog')">
        🏷️ Catálogo de Peças & Estoque
        <span class="tab-badge" id="badge-catalog-count">0</span>
      </button>
      <button class="nav-tab" onclick="switchTab('copilot')">
        💡 Consultor Executivo de Negócios
      </button>
      <button class="nav-tab" onclick="switchTab('gemini')">
        ⚙️ Configurações & Conectividade
      </button>
    </div>
  </div>

  <!-- CONTEÚDO PRINCIPAL -->
  <main>

    <!-- KPI STAT CARDS (GLOBALMENTE VISÍVEIS) -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Faturamento Estimado</span>
          <div class="kpi-icon" style="background: rgba(16, 185, 129, 0.15); color: #10B981;">💰</div>
        </div>
        <div class="kpi-val" id="kpi-revenue">R$ 0,00</div>
        <div class="kpi-sub"><span class="trend-up">+100%</span> pedidos confirmados</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Atendimentos Ativos</span>
          <div class="kpi-icon" style="background: rgba(99, 102, 241, 0.15); color: #818CF8;">💬</div>
        </div>
        <div class="kpi-val" id="kpi-active-chats">0</div>
        <div class="kpi-sub" id="kpi-ai-status">🟢 Atendimento Automático Ativo</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Despacho Uber Flash</span>
          <div class="kpi-icon" style="background: rgba(245, 158, 11, 0.15); color: #F59E0B;">🛵</div>
        </div>
        <div class="kpi-val" id="kpi-uber">0%</div>
        <div class="kpi-sub" id="kpi-uber-count">0 pedidos para entrega</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-header">
          <span class="kpi-title">Peças em Catálogo</span>
          <div class="kpi-icon" style="background: rgba(6, 182, 212, 0.15); color: #06B6D4;">📦</div>
        </div>
        <div class="kpi-val" id="kpi-stock-items">0</div>
        <div class="kpi-sub">Sincronizado c/ Google Sheets</div>
      </div>
    </div>

    <!-- TAB 1: ATENDIMENTOS AO VIVO (IA VS HUMANO) -->
    <div class="tab-pane active" id="tab-conversations">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">💬 Atendimento ao Vivo • Controle de IA & Balcão</h2>
            <span class="badge-count" id="convs-counter">0 contatos</span>
          </div>
          <div class="toolbar-actions">
            <input type="text" class="search-input" id="search-convs" placeholder="Buscar por nome, telefone ou peça..." oninput="filterConversations()">
            <button class="btn btn-secondary btn-sm" onclick="fetchConversations()">🔄 Atualizar</button>
          </div>
        </div>

        <!-- Visualização Tablet/Desktop (Tabela Rica) -->
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Cliente / Oficina</th>
                <th>Peça Sendo Cotada / Ativa</th>
                <th>Status do Atendimento</th>
                <th>Última Interação</th>
                <th>Ação Rápida do Balcão</th>
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

    <!-- TAB 2: EXPEDIÇÃO & UBER FLASH -->
    <div class="tab-pane" id="tab-orders">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">📦 Fila de Separação & Despacho Uber Flash</h2>
            <span class="badge-count" id="orders-counter">0 pedidos</span>
          </div>
          <div class="toolbar-actions">
            <a href="/api/reports/orders/csv" class="btn btn-emerald btn-sm" download="Pedidos_VictorCell_PowerBI.csv">
              📊 Baixar CSV para Power BI
            </a>
            <button class="btn btn-secondary btn-sm" onclick="fetchStats()">🔄 Atualizar</button>
          </div>
        </div>

        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID / Data</th>
                <th>Cliente</th>
                <th>Peça a Separar</th>
                <th>Valor</th>
                <th>Endereço Uber Flash</th>
                <th>Status</th>
                <th>Validade Reserva</th>
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
      <div class="charts-grid">
        <div class="chart-card">
          <h3>⚖️ Mix de Vendas: Original vs. Paralela</h3>
          <canvas id="chartQuality" height="200"></canvas>
        </div>
        <div class="chart-card">
          <h3>📱 Distribuição por Categoria</h3>
          <canvas id="chartCategory" height="200"></canvas>
        </div>
      </div>

      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">🏆 Peças Mais Procuradas na Bancada</h2>
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
              📊
            </div>
            <div>
              <h3 style="font-size: 1.05rem; font-weight: 700; color: #FFFFFF; display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
                Planilha do Google Sheets • Estoque & Preços
                <span style="font-size: 0.7rem; background: rgba(16, 185, 129, 0.2); color: #34D399; padding: 2px 8px; border-radius: 999px; font-weight: 600;">🟢 Conectada ao Robô</span>
              </h3>
              <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">
                Esta planilha é a fonte oficial do estoque. Qualquer peça, valor ou quantidade que você alterar nela é lida pelo robô do WhatsApp em tempo real.
              </p>
            </div>
          </div>
          <div style="display: flex; gap: 0.6rem; flex-wrap: wrap;">
            <a href="https://docs.google.com/spreadsheets/d/1N2gigR8MmuiBRSbtO1TDLnS9AFQS3dJYhxYEEUs7kZY/edit" target="_blank" class="btn btn-primary btn-sm" style="text-decoration: none; font-weight: 700; background: #10B981; color: #042F2E;">
              🔗 Abrir Planilha no Google Sheets ↗
            </a>
            <button class="btn btn-secondary btn-sm" onclick="syncGoogleSheets()">
              ⚡ Sincronizar Agora
            </button>
            <button class="btn btn-secondary btn-sm" id="btn-toggle-sheet-view" onclick="toggleSheetView()">
              👁️ Visualizar Planilha ao Vivo
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
          <div class="kpi-icon-wrapper" style="background: rgba(59, 130, 246, 0.15); color: #60A5FA;">📦</div>
          <div class="kpi-body">
            <div class="kpi-label">Total de Peças Ativas</div>
            <div class="kpi-value" id="kpi-catalog-total">0</div>
            <div class="kpi-sub">Sincronizadas com Google Sheets</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: rgba(16, 185, 129, 0.15); color: #34D399;">✅</div>
          <div class="kpi-body">
            <div class="kpi-label">Disponíveis em Balcão</div>
            <div class="kpi-value" id="kpi-catalog-healthy" style="color: #34D399;">0</div>
            <div class="kpi-sub">Pronta entrega imediata</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: rgba(245, 158, 11, 0.15); color: #FBBF24;">⚠️</div>
          <div class="kpi-body">
            <div class="kpi-label">Taxa de Disponibilidade</div>
            <div class="kpi-value" id="kpi-catalog-critical" style="color: #60A5FA;">100%</div>
            <div class="kpi-sub">Índice de atendimento</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon-wrapper" style="background: rgba(239, 68, 68, 0.15); color: #F87171;">⛔</div>
          <div class="kpi-body">
            <div class="kpi-label">Esgotadas em Loja</div>
            <div class="kpi-value" id="kpi-catalog-out">0</div>
            <div class="kpi-sub">Ruptura imediata de estoque</div>
          </div>
        </div>
      </div>

      <!-- TABELA DINÂMICA DE PEÇAS & FILTROS -->
      <div class="section-card">
        <div class="section-toolbar" style="flex-direction: column; align-items: stretch; gap: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
            <div class="section-title-group">
              <h2 class="section-title">🏷️ Catálogo de Peças Sincronizadas</h2>
              <span class="badge-count" id="catalog-counter">0 peças</span>
            </div>
            <div class="toolbar-actions" style="gap: 0.5rem;">
              <input type="text" id="catalog-search" placeholder="🔍 Buscar por nome, modelo (ex: P615, A15), SKU..." class="search-input" oninput="filterCatalogTable()" style="min-width: 260px; background: rgba(0,0,0,0.3); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 0.45rem 0.75rem; color: #fff; font-size: 0.85rem;">
              <button class="btn btn-secondary btn-sm" onclick="fetchCatalog()">🔄 Atualizar</button>
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

    <!-- TAB 5: COPILOTO IA DO GESTOR (BUSINESS INTELLIGENCE) -->
    <div class="tab-pane" id="tab-copilot">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">💡 Consultor Executivo de Negócios • Inteligência Victor Cell</h2>
            <p class="section-subtitle">Inteligência analítica em tempo real integrada a vendas, estoque e movimentação do balcão.</p>
          </div>
          <div class="toolbar-actions">
            <div class="pill pill-emerald">
              <span class="pill-dot"></span>
              <span>Análise Operacional Conectada</span>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="clearCopilotChat()">🗑️ Limpar Conversa</button>
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
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1.15rem;">
              <div style="font-size: 0.775rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Gemini 3.5 Flash Lite (Principal)</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #34D399; margin: 0.35rem 0;" id="quota-flash-lite">70 / 500 RPD</div>
              <div style="background: rgba(255,255,255,0.08); height: 8px; border-radius: 999px; overflow: hidden;">
                <div id="quota-progress-bar" style="width: 14%; height: 100%; background: #10B981;"></div>
              </div>
              <div style="font-size: 0.725rem; color: var(--text-dim); margin-top: 0.4rem;">14% consumido hoje • 430 disponíveis</div>
            </div>

            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1.15rem;">
              <div style="font-size: 0.775rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Reserva Gemini 3.1 Flash Lite</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #818CF8; margin: 0.35rem 0;">2 / 500 RPD</div>
              <div style="background: rgba(255,255,255,0.08); height: 8px; border-radius: 999px; overflow: hidden;">
                <div style="width: 1%; height: 100%; background: #6366F1;"></div>
              </div>
              <div style="font-size: 0.725rem; color: var(--text-dim); margin-top: 0.4rem;">498 requisições sobressalentes</div>
            </div>

            <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1.15rem;">
              <div style="font-size: 0.775rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Roteador Multimodal (Áudio de Voz)</div>
              <div style="font-size: 1.6rem; font-weight: 800; color: #FBBF24; margin: 0.35rem 0;">3.6 / 3.8 Flash</div>
              <div style="font-size: 0.75rem; color: var(--text-muted); line-height: 1.5; margin-top: 0.35rem;">
                Áudios de voz são direcionados automaticamente aos modelos com decodificador acústico nativo.
              </div>
            </div>
          </div>

          <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1.25rem;">
            <h3 style="font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 0.85rem;">🔑 Chave de API Google AI Studio</h3>
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
            <h2 class="section-title">🧪 Laboratório de Testes de Atendimento</h2>
          </div>
          <div class="toolbar-actions">
            <button class="btn btn-secondary btn-sm" onclick="clearChat()">🗑️ Limpar Conversa</button>
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
                <button class="btn btn-emerald" onclick="sendChatMessage()">Enviar 📤</button>
              </div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
              <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1rem;">
                <h4 style="font-size: 0.85rem; color: #fff; margin-bottom: 0.5rem;">💡 Dicas de Testes de Balcão:</h4>
                <ul style="font-size: 0.775rem; color: var(--text-muted); padding-left: 1.1rem; line-height: 1.6;">
                  <li><strong>Cotação:</strong> "Quanto tá a tela do A15 com aro?"</li>
                  <li><strong>Pós-Venda / Rastreio:</strong> "E aí amigo, o Uber já saiu com a minha peça?"</li>
                  <li><strong>Memória de Ontem:</strong> "Lembra da tela que perguntei ontem? Quanto é mesmo?"</li>
                  <li><strong>Negociação:</strong> "Faz por R$ 150 no Pix?" (Aciona alerta de humano)</li>
                </ul>
              </div>

              <!-- Conexão WhatsApp Card -->
              <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: 12px; padding: 1rem;">
                <h4 style="font-size: 0.85rem; color: #fff; margin-bottom: 0.5rem;">📲 Conexão WhatsApp Web</h4>
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

  </main>

    <script>
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
        <div class="copilot-user-avatar">👤</div>
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
        btn.innerText = '👁️ Visualizar Planilha ao Vivo';
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

    function switchTab(tabId) {
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const activeBtn = Array.from(document.querySelectorAll('.nav-tab')).find(b => b.getAttribute('onclick').includes(tabId));
      if (activeBtn) activeBtn.classList.add('active');
      const targetPane = document.getElementById('tab-' + tabId);
      if (targetPane) targetPane.classList.add('active');

      if (tabId === 'conversations') fetchConversations();
      if (tabId === 'catalog') fetchCatalog();
      if (tabId === 'orders' || tabId === 'overview') fetchStats();
      if (tabId === 'simulator') fetchWhatsAppQR();
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

        return `
          <tr>
            <td>
              <div class="user-profile">
                <div class="user-avatar">${initials}</div>
                <div class="user-info">
                  <span class="user-name">${escapeHtml(c.customer_name || 'Cliente WhatsApp')}</span>
                  <a href="${waLink}" target="_blank" class="user-phone" title="Abrir no WhatsApp">
                    📱 ${c.formatted_phone || c.phone} ↗
                  </a>
                </div>
              </div>
            </td>
            <td>
              <span class="part-pill" title="${escapeHtml(c.active_sku_name)}">
                📦 ${escapeHtml(c.active_sku_name)}
              </span>
            </td>
            <td>
              ${isActive
                ? `<span class="status-pill status-robot">🟢 Atendimento Automático</span>`
                : `<span class="status-pill status-human">🟡 Balcão (${c.paused_until ? 'até ' + c.paused_until : 'Pausado'})</span>`
              }
            </td>
            <td style="font-size: 0.775rem; color: var(--text-dim); font-family: 'JetBrains Mono', monospace;">
              ${c.last_activity || '--'}
            </td>
            <td>
              ${!isActive
                ? `<button class="btn btn-emerald btn-sm" onclick="resumeConversation('${c.phone}')">▶️ Liberar p/ Automação</button>`
                : `<button class="btn btn-amber btn-sm" onclick="pauseConversation('${c.phone}')">⏸️ Assumir Atendimento</button>`
              }
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

        return `
          <div class="customer-card-mobile">
            <div class="card-mobile-top">
              <div class="user-profile">
                <div class="user-avatar">${initials}</div>
                <div class="user-info">
                  <span class="user-name">${escapeHtml(c.customer_name || 'Cliente WhatsApp')}</span>
                  <a href="${waLink}" target="_blank" class="user-phone">
                    📱 ${c.formatted_phone || c.phone} ↗
                  </a>
                </div>
              </div>
              <div>
                ${isActive
                  ? `<span class="status-pill status-robot">🟢 Automático</span>`
                  : `<span class="status-pill status-human">🟡 Balcão</span>`
                }
              </div>
            </div>

            <div class="card-mobile-body">
              <div style="font-size: 0.725rem; color: var(--text-dim);">Peça Sendo Cotada:</div>
              <span class="part-pill">📦 ${escapeHtml(c.active_sku_name)}</span>
              <div style="font-size: 0.7rem; color: var(--text-dim); margin-top: 0.2rem;">Último contato: ${c.last_activity || '--'}</div>
            </div>

            <div class="card-mobile-actions">
              ${!isActive
                ? `<button class="btn btn-emerald btn-sm" onclick="resumeConversation('${c.phone}')">▶️ Liberar p/ Automação</button>`
                : `<button class="btn btn-amber btn-sm" onclick="pauseConversation('${c.phone}')">⏸️ Assumir Atendimento</button>`
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
        document.getElementById('badge-orders-count').innerText = (data.recent_orders || []).length;
        document.getElementById('orders-counter').innerText = `${(data.recent_orders || []).length} pedidos`;

        // Store status pill
        const storeStatus = document.getElementById('store-status');
        if (data.is_store_open) {
          storeStatus.innerText = '🟢 Balcão Aberto';
          document.getElementById('pill-store').className = 'pill pill-emerald';
        } else {
          storeStatus.innerText = '🌙 Balcão Fechado';
          document.getElementById('pill-store').className = 'pill pill-amber';
        }

        // Tabela de Pedidos
        renderOrders(data.recent_orders || []);

        // Ranking
        renderTopProducts(data.top_products || []);

        // Charts
        renderCharts(data.quality_breakdown || {}, data.category_breakdown || {});
      } catch (err) {
        console.error('Erro ao buscar stats:', err);
      }
    }

    function renderOrders(orders) {
      const tbody = document.getElementById('orders-tbody');
      const mobileDeck = document.getElementById('orders-cards-mobile');

      if (!orders || orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhum pedido de separação no momento.</td></tr>';
        mobileDeck.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhum pedido registrado.</div>';
        return;
      }

      tbody.innerHTML = orders.map(o => `
        <tr>
          <td>
            <div style="font-weight: 700; color: #fff;">#${o.id}</div>
            <div style="font-size: 0.725rem; color: var(--text-dim);">${o.created_at}</div>
          </td>
          <td>
            <div style="font-weight: 600; color: #E2E8F0;">${escapeHtml(o.customer_name)}</div>
            <div style="font-size: 0.725rem; color: #34D399; font-family: monospace;">${o.customer_phone}</div>
          </td>
          <td><span class="part-pill">📦 ${escapeHtml(o.product_sku)}</span></td>
          <td style="font-weight: 700; color: #34D399;">R$ ${(o.product_price || 0).toFixed(2)}</td>
          <td style="max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
            📍 ${escapeHtml(o.destination_address || 'Retirada no Balcão')}
          </td>
          <td>
            <span class="status-pill status-robot">${o.status}</span>
          </td>
          <td style="color: #FBBF24; font-weight: 600;">⏰ Até ${o.expires_at}</td>
        </tr>
      `).join('');

      mobileDeck.innerHTML = orders.map(o => `
        <div class="customer-card-mobile">
          <div class="card-mobile-top">
            <div>
              <div style="font-weight: 700; color: #fff;">#${o.id} • R$ ${(o.product_price || 0).toFixed(2)}</div>
              <div style="font-size: 0.75rem; color: #34D399;">${escapeHtml(o.customer_name)}</div>
            </div>
            <span class="status-pill status-robot">${o.status}</span>
          </div>
          <div class="card-mobile-body">
            <div><strong>Peça:</strong> ${escapeHtml(o.product_sku)}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">📍 ${escapeHtml(o.destination_address || 'Balcão')}</div>
            <div style="font-size: 0.725rem; color: #FBBF24;">Validade: Até ${o.expires_at} (${o.created_at})</div>
          </div>
        </div>
      `).join('');
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
        return '<span style="background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.3); color:#34D399; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">🛡️ Original Nacional (90d)</span>';
      } else if (qUp.includes('ORIGINAL_CHINA') || qUp.includes('ORIGINAL CHINA')) {
        return '<span style="background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.3); color:#38BDF8; padding:2px 7px; border-radius:6px; font-size:0.72rem; font-weight:600;">💎 Original China</span>';
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

    function refreshAll() {
      showToast('Atualizando dados...', 'success');
      fetchConversations();
      fetchStats();
      fetchCatalog();
      fetchWhatsAppQR();
    }

    // Inicialização ao Carregar
    fetchConversations();
    fetchStats();
    fetchCatalog();
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
        error_banner = f'''
        <div class="login-alert">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{error_message}</span>
        </div>
        '''
    return f'''<!DOCTYPE html>
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
        <p>🔒 Autenticação HMAC Criptografada</p>
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
</html>'''
