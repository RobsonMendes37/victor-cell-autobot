"""
Executive Web Dashboard & Intelligence Hub for Victor Cell.
100% Free, Open-Source & Self-Hosted.
Includes:
- Business KPIs (Revenue, Avg Ticket, Uber Flash %, Catalog Items)
- Integrated Orders & Dispatch Management with direct Power BI CSV Export in table toolbar
- Live Google Sheets Catalog viewer & instant synchronization
- Top Best-Selling Replacement Parts Ranking & FAQ Intelligence
- Interactive Chart.js Visualizations (Quality distribution & Category breakdown)
- WhatsApp Live QR Code Pairing & Connection Monitor
- Live Customer Message Simulator with instant bot responses
- Gemini AI Quota Manager, Key Tester & Rate Limit Inspector
"""

def render_dashboard_html() -> str:
    return r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Victor Cell • Painel Executivo & Inteligência de Balcão</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-base: #070A0F;
      --bg-surface: #0E1420;
      --bg-surface-elevated: #141C2E;
      --bg-card: rgba(14, 20, 32, 0.78);
      --border-subtle: rgba(255, 255, 255, 0.07);
      --border-focus: rgba(99, 102, 241, 0.4);
      --primary: #6366F1;
      --primary-hover: #4F46E5;
      --primary-glow: rgba(99, 102, 241, 0.25);
      --emerald: #10B981;
      --emerald-glow: rgba(16, 185, 129, 0.25);
      --amber: #F59E0B;
      --amber-glow: rgba(245, 158, 11, 0.25);
      --cyan: #06B6D4;
      --rose: #F43F5E;
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image:
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 45%),
        radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.08) 0px, transparent 40%),
        radial-gradient(at 50% 100%, rgba(6, 182, 212, 0.06) 0px, transparent 50%);
      background-attachment: fixed;
    }

    /* Top Bar Header */
    header {
      padding: 1rem 2rem;
      background: rgba(11, 15, 25, 0.88);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand { display: flex; align-items: center; gap: 0.9rem; }

    .brand-icon {
      width: 44px; height: 44px; border-radius: 12px;
      background: linear-gradient(135deg, #6366F1, #8B5CF6);
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.25rem; color: #fff;
      box-shadow: 0 4px 16px var(--primary-glow);
      letter-spacing: -0.02em;
    }

    .brand-text h1 { font-size: 1.15rem; font-weight: 800; letter-spacing: -0.02em; color: #fff; }
    .brand-text p { font-size: 0.75rem; color: var(--text-muted); font-weight: 500; }

    .header-center {
      display: flex; align-items: center; gap: 1rem;
    }

    .live-clock {
      display: flex; align-items: center; gap: 0.5rem;
      font-size: 0.8rem; font-weight: 600; color: var(--text-muted);
      background: rgba(255, 255, 255, 0.03);
      padding: 0.4rem 0.85rem; border-radius: 9999px;
      border: 1px solid var(--border-subtle);
    }
    .clock-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--emerald); animation: pulse 2s infinite; }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
      70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
      100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    .header-actions { display: flex; align-items: center; gap: 0.75rem; }

    .badge {
      display: inline-flex; align-items: center; gap: 0.45rem;
      padding: 0.4rem 0.8rem; border-radius: 9999px;
      font-size: 0.75rem; font-weight: 600;
      border: 1px solid var(--border-subtle);
      background: rgba(255, 255, 255, 0.03);
      transition: all 0.2s;
    }
    .badge-dot { width: 7px; height: 7px; border-radius: 50%; }
    .badge-emerald { color: #34D399; border-color: rgba(16, 185, 129, 0.25); background: rgba(16, 185, 129, 0.08); }
    .badge-emerald .badge-dot { background: #10B981; box-shadow: 0 0 8px #10B981; }
    .badge-amber { color: #FBBF24; border-color: rgba(245, 158, 11, 0.25); background: rgba(245, 158, 11, 0.08); }
    .badge-amber .badge-dot { background: #F59E0B; box-shadow: 0 0 8px #F59E0B; }
    .badge-primary { color: #A5B4FC; border-color: rgba(99, 102, 241, 0.25); background: rgba(99, 102, 241, 0.08); }
    .badge-primary .badge-dot { background: #6366F1; box-shadow: 0 0 8px #6366F1; }

    /* Modern Navigation Tabs */
    .tab-bar-wrapper {
      background: rgba(14, 20, 32, 0.65);
      border-bottom: 1px solid var(--border-subtle);
      backdrop-filter: blur(12px);
      padding: 0.5rem 2rem;
      display: flex; justify-content: space-between; align-items: center;
    }

    .tabs {
      display: flex; gap: 0.5rem;
    }

    .tab-btn {
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.65rem 1.15rem; border-radius: 10px;
      font-size: 0.85rem; font-weight: 600;
      color: var(--text-muted); background: transparent;
      border: 1px solid transparent; cursor: pointer;
      transition: all 0.2s ease;
    }

    .tab-btn:hover {
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }

    .tab-btn.active {
      color: #fff;
      background: var(--bg-surface-elevated);
      border-color: rgba(255, 255, 255, 0.1);
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    .tab-btn .tab-count {
      background: rgba(255, 255, 255, 0.08);
      padding: 0.15rem 0.45rem; border-radius: 6px;
      font-size: 0.7rem; font-weight: 700;
    }

    /* Buttons */
    .btn {
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.6rem 1.15rem; border-radius: 10px;
      font-size: 0.825rem; font-weight: 600;
      cursor: pointer; text-decoration: none;
      transition: all 0.2s ease; border: none; outline: none;
    }
    .btn-primary {
      background: linear-gradient(135deg, var(--primary), #8B5CF6);
      color: #fff; box-shadow: 0 4px 14px var(--primary-glow);
    }
    .btn-primary:hover { opacity: 0.93; transform: translateY(-1px); }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.04);
      color: var(--text-main); border: 1px solid var(--border-subtle);
    }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.15); }
    .btn-emerald {
      background: linear-gradient(135deg, #10B981, #059669);
      color: #fff; box-shadow: 0 4px 14px var(--emerald-glow);
    }
    .btn-emerald:hover { opacity: 0.93; transform: translateY(-1px); }
    .btn-sm { padding: 0.45rem 0.85rem; font-size: 0.78rem; border-radius: 8px; }

    /* Layout & Cards */
    main {
      flex: 1; padding: 2rem; max-width: 1440px; margin: 0 auto; width: 100%;
    }

    .tab-content { display: none; }
    .tab-content.active { display: block; animation: fadeIn 0.25s ease; }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .card {
      background: var(--bg-card);
      backdrop-filter: blur(14px);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      padding: 1.5rem;
      position: relative;
      overflow: hidden;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .card:hover {
      border-color: rgba(255, 255, 255, 0.12);
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }

    /* KPI Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }

    .kpi-card {
      display: flex; flex-direction: column; justify-content: space-between;
    }
    .kpi-header {
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;
    }
    .kpi-title {
      font-size: 0.775rem; color: var(--text-muted);
      font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
    }
    .kpi-icon {
      width: 34px; height: 34px; border-radius: 9px;
      display: flex; align-items: center; justify-content: center;
      font-size: 1.1rem;
    }
    .icon-emerald { background: rgba(16, 185, 129, 0.15); color: #34D399; }
    .icon-primary { background: rgba(99, 102, 241, 0.15); color: #818CF8; }
    .icon-amber { background: rgba(245, 158, 11, 0.15); color: #FBBF24; }
    .icon-cyan { background: rgba(6, 182, 212, 0.15); color: #38BDF8; }

    .kpi-value { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 0.5rem; }
    .kpi-footer {
      font-size: 0.775rem; color: var(--text-muted); display: flex; align-items: center; gap: 0.35rem;
    }
    .kpi-tag-success { color: #34D399; font-weight: 600; }

    /* Orders Section & Integrated Toolbar */
    .table-container-card {
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 16px;
      overflow: hidden;
      margin-bottom: 2rem;
    }

    .table-toolbar {
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid var(--border-subtle);
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center;
      gap: 1rem; background: rgba(255, 255, 255, 0.015);
    }

    .table-title-area {
      display: flex; align-items: center; gap: 0.75rem;
    }
    .table-title { font-size: 1.1rem; font-weight: 700; color: #fff; }
    .table-badge {
      background: rgba(99, 102, 241, 0.15); color: #818CF8;
      padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;
    }

    .table-controls {
      display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem;
    }

    .search-box {
      position: relative; display: flex; align-items: center;
    }
    .search-input {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      border-radius: 9px; padding: 0.55rem 0.85rem 0.55rem 2.2rem;
      color: #fff; font-size: 0.825rem; outline: none; width: 260px;
      transition: all 0.2s;
    }
    .search-input:focus { border-color: var(--primary); width: 300px; background: rgba(255, 255, 255, 0.07); }
    .search-icon {
      position: absolute; left: 0.75rem; font-size: 0.85rem; color: var(--text-muted); pointer-events: none;
    }

    .filter-pills {
      display: flex; background: rgba(255, 255, 255, 0.03);
      padding: 0.25rem; border-radius: 9px; border: 1px solid var(--border-subtle);
    }
    .filter-btn {
      padding: 0.35rem 0.75rem; border-radius: 7px; border: none; background: transparent;
      color: var(--text-muted); font-size: 0.775rem; font-weight: 600; cursor: pointer; transition: all 0.15s;
    }
    .filter-btn.active {
      background: rgba(255, 255, 255, 0.1); color: #fff;
    }

    /* Data Table */
    .table-responsive { width: 100%; overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; text-align: left; }
    thead th {
      padding: 0.9rem 1.25rem; font-size: 0.75rem; font-weight: 700;
      color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;
      border-bottom: 1px solid var(--border-subtle); background: rgba(0, 0, 0, 0.2);
      white-space: nowrap;
    }
    tbody tr {
      border-bottom: 1px solid var(--border-subtle);
      transition: background-color 0.15s;
    }
    tbody tr:hover { background-color: rgba(255, 255, 255, 0.02); }
    tbody td {
      padding: 1rem 1.25rem; font-size: 0.85rem; color: #CBD5E1; vertical-align: middle;
      white-space: nowrap;
    }

    .customer-cell { display: flex; flex-direction: column; }
    .customer-name { font-weight: 600; color: #fff; }
    .customer-wa {
      font-size: 0.75rem; color: #34D399; text-decoration: none; display: inline-flex; align-items: center; gap: 0.25rem;
    }
    .customer-wa:hover { text-decoration: underline; }

    .tag-quality {
      display: inline-block; padding: 0.2rem 0.55rem; border-radius: 6px;
      font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    }
    .tag-original { background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .tag-paralela { background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3); }

    .status-badge {
      display: inline-flex; align-items: center; gap: 0.35rem;
      padding: 0.25rem 0.65rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700;
    }
    .status-pending { background: rgba(245, 158, 11, 0.15); color: #FBBF24; }
    .status-ready { background: rgba(16, 185, 129, 0.15); color: #34D399; }
    .status-delivered { background: rgba(99, 102, 241, 0.15); color: #818CF8; }
    .status-cancelled { background: rgba(244, 63, 94, 0.15); color: #FB7185; }

    /* Insights Grid */
    .insights-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 1.5rem; margin-bottom: 2rem;
    }
    .insight-card h3 {
      font-size: 1.05rem; font-weight: 700; margin-bottom: 1.25rem;
      display: flex; align-items: center; gap: 0.6rem; color: #fff;
    }
    .ranking-list { display: flex; flex-direction: column; gap: 0.85rem; }
    .ranking-item {
      display: flex; align-items: center; justify-content: space-between;
      padding: 0.9rem 1.15rem; background: rgba(255, 255, 255, 0.025);
      border: 1px solid var(--border-subtle); border-radius: 12px;
    }
    .ranking-info { display: flex; align-items: center; gap: 0.85rem; }
    .ranking-badge {
      width: 32px; height: 32px; border-radius: 9px;
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 0.85rem;
    }
    .ranking-badge.top-1 { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.35); }
    .ranking-badge.top-2 { background: rgba(156, 163, 175, 0.2); color: #E2E8F0; border: 1px solid rgba(156, 163, 175, 0.35); }
    .ranking-badge.top-3 { background: rgba(217, 119, 6, 0.2); color: #FCD34D; border: 1px solid rgba(217, 119, 6, 0.35); }
    .ranking-badge.top-other { background: rgba(99, 102, 241, 0.15); color: #818CF8; }

    .faq-item { margin-bottom: 1.15rem; }
    .faq-header { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.4rem; }
    .progress-bar-bg {
      height: 8px; width: 100%; background: rgba(255, 255, 255, 0.05);
      border-radius: 9999px; overflow: hidden;
    }
    .progress-bar-fill {
      height: 100%; border-radius: 9999px;
      background: linear-gradient(90deg, #6366F1, #8B5CF6);
      transition: width 0.6s ease;
    }

    .charts-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 1.5rem; margin-bottom: 2rem;
    }
    .chart-card h3 { font-size: 1rem; font-weight: 700; margin-bottom: 1rem; color: #fff; }
    .chart-wrapper { height: 260px; position: relative; }

    /* Simulator Widget */
    .simulator-card {
      background: linear-gradient(180deg, rgba(20, 28, 46, 0.8) 0%, rgba(14, 20, 32, 0.95) 100%);
      border: 1px solid rgba(99, 102, 241, 0.2);
      border-radius: 16px; padding: 1.75rem; margin-bottom: 2rem;
    }
    .sim-header { margin-bottom: 1.25rem; }
    .sim-header h3 { font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: 0.35rem; }
    .sim-header p { font-size: 0.825rem; color: var(--text-muted); }
    .sim-input-box { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
    .sim-input {
      flex: 1; background: rgba(0, 0, 0, 0.3); border: 1px solid var(--border-subtle);
      border-radius: 10px; padding: 0.75rem 1rem; color: #fff; font-size: 0.9rem; outline: none;
    }
    .sim-input:focus { border-color: var(--primary); }
    .sim-response-box {
      background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border-subtle);
      border-radius: 12px; padding: 1.25rem; min-height: 80px; font-size: 0.9rem;
      color: #E2E8F0; line-height: 1.5; display: none; white-space: pre-wrap;
    }

    /* AI Quota & Limits Card */
    .quota-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1.5rem; margin-bottom: 2rem;
    }
    .quota-card {
      background: var(--bg-card); border: 1px solid var(--border-subtle);
      border-radius: 16px; padding: 1.75rem;
    }
    .quota-card h4 { font-size: 1.05rem; font-weight: 700; margin-bottom: 1rem; color: #fff; display: flex; align-items: center; gap: 0.5rem; }
    .quota-row { display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--border-subtle); font-size: 0.85rem; }
    .quota-row span:first-child { color: var(--text-muted); }
    .quota-row span:last-child { font-weight: 600; color: #fff; }

    /* Modal */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px); display: none; align-items: center; justify-content: center;
      z-index: 100;
    }
    .modal-box {
      background: #0E1420; border: 1px solid var(--border-subtle);
      border-radius: 20px; padding: 2rem; max-width: 480px; width: 90%;
      text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.6);
      position: relative;
    }
    .modal-close {
      position: absolute; top: 1.25rem; right: 1.25rem; background: transparent;
      border: none; color: var(--text-muted); font-size: 1.25rem; cursor: pointer;
    }

    /* Toast */
    #toast {
      position: fixed; bottom: 2rem; right: 2rem;
      background: #141C2E; border: 1px solid var(--border-subtle);
      border-radius: 12px; padding: 1rem 1.5rem; color: #fff; font-size: 0.85rem;
      font-weight: 600; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      display: none; align-items: center; gap: 0.75rem; z-index: 200;
    }
  </style>
</head>
<body>

  <!-- Top Bar Header -->
  <header>
    <div class="brand">
      <div class="brand-icon">VC</div>
      <div class="brand-text">
        <h1>VICTOR CELL</h1>
        <p>Inteligência de Balcão & Expedição Autônoma</p>
      </div>
    </div>

    <div class="header-center">
      <div class="live-clock">
        <span class="clock-dot"></span>
        <span id="live-clock-text">--:--:-- • Fortaleza (GMT-3)</span>
      </div>
    </div>

    <div class="header-actions">
      <div class="badge badge-emerald" id="store-badge">
        <span class="badge-dot"></span>
        <span id="store-status">Loja Aberta</span>
      </div>
      <div class="badge badge-primary" id="sheets-badge">
        <span class="badge-dot"></span>
        <span id="sheets-status">Google Sheets Ativo</span>
      </div>
      <div class="badge badge-amber" id="wa-badge">
        <span class="badge-dot"></span>
        <span id="wa-status">WhatsApp Conectado</span>
      </div>
      <button class="btn btn-primary btn-sm" onclick="openWhatsAppModal()">
        📱 WhatsApp QR
      </button>
      <button class="btn btn-secondary btn-sm" onclick="syncSheets()">
        🔄 Sincronizar
      </button>
    </div>
  </header>

  <!-- Navigation Tabs -->
  <div class="tab-bar-wrapper">
    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('overview', this)">
        📊 Visão Geral
      </button>
      <button class="tab-btn" onclick="switchTab('orders', this)">
        📦 Expedição & Pedidos <span class="tab-count" id="tab-orders-count">0</span>
      </button>
      <button class="tab-btn" onclick="switchTab('catalog', this)">
        📋 Catálogo Google Sheets <span class="tab-count" id="tab-catalog-count">0</span>
      </button>
      <button class="tab-btn" onclick="switchTab('insights', this)">
        📈 Inteligência de Vendas
      </button>
      <button class="tab-btn" onclick="switchTab('ai-quota', this)">
        ⚡ IA Gemini & Cotas
      </button>
    </div>
  </div>

  <main>
    <!-- TAB 1: VISÃO GERAL -->
    <div class="tab-content active" id="tab-overview">
      <!-- KPIs Principais -->
      <div class="kpi-grid">
        <div class="card kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Faturamento Acumulado</span>
            <div class="kpi-icon icon-emerald">💰</div>
          </div>
          <div class="kpi-value" id="kpi-revenue" style="color: #34D399;">R$ 0,00</div>
          <div class="kpi-footer">
            <span class="kpi-tag-success">↑ Ativo</span>
            <span>vendas geradas via WhatsApp</span>
          </div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Ticket Médio de Balcão</span>
            <div class="kpi-icon icon-primary">🏷️</div>
          </div>
          <div class="kpi-value" id="kpi-avg-ticket">R$ 0,00</div>
          <div class="kpi-footer"><span>Média por pedido reservado</span></div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Total de Pedidos</span>
            <div class="kpi-icon icon-amber">📦</div>
          </div>
          <div class="kpi-value" id="kpi-orders">0</div>
          <div class="kpi-footer"><span>Reservas confirmadas para o caixa</span></div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Despachos Uber Flash</span>
            <div class="kpi-icon icon-cyan">⚡</div>
          </div>
          <div class="kpi-value" id="kpi-uber" style="color: #38BDF8;">0</div>
          <div class="kpi-footer"><span id="kpi-uber-pct">0% das saídas via motoboy</span></div>
        </div>

        <div class="card kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Catálogo Lote Ativo</span>
            <div class="kpi-icon icon-primary">📋</div>
          </div>
          <div class="kpi-value" id="kpi-products">0</div>
          <div class="kpi-footer"><span>Peças lidas do Google Sheets</span></div>
        </div>
      </div>

      <!-- Simulador de Conversa Rápido -->
      <div class="simulator-card">
        <div class="sim-header">
          <h3>🧪 Testador do Robô em Tempo Real</h3>
          <p>Envie uma mensagem de teste como se fosse um cliente no WhatsApp para ver a resposta imediata da IA:</p>
        </div>
        <div class="sim-input-box">
          <input type="text" id="sim-query" class="sim-input" placeholder="Ex: Bom dia amigo, tem tela do A15 original? Qual a diferença pra paralela?" onkeydown="if(event.key==='Enter') testSimulate()" />
          <button class="btn btn-primary" onclick="testSimulate()">Enviar Pergunta</button>
        </div>
        <div class="sim-response-box" id="sim-response"></div>
      </div>
    </div>

    <!-- TAB 2: EXPEDIÇÃO & PEDIDOS (COM CSV INTEGRADO) -->
    <div class="tab-content" id="tab-orders">
      <div class="table-container-card">
        <!-- Toolbar Integrada com Botão CSV no Lugar Certo -->
        <div class="table-toolbar">
          <div class="table-title-area">
            <h2 class="table-title">Expedição, Reservas & Saídas de Peças</h2>
            <span class="table-badge" id="table-badge-count">0 pedidos</span>
          </div>

          <div class="table-controls">
            <div class="search-box">
              <span class="search-icon">🔍</span>
              <input type="text" class="search-input" id="order-search" placeholder="Buscar cliente, telefone, SKU..." onkeyup="filterOrders()">
            </div>

            <div class="filter-pills">
              <button class="filter-btn active" onclick="setStatusFilter('ALL', this)">Todos</button>
              <button class="filter-btn" onclick="setStatusFilter('PENDING_SEPARATION', this)">Pendentes</button>
              <button class="filter-btn" onclick="setStatusFilter('READY_FOR_PICKUP', this)">Prontos</button>
              <button class="filter-btn" onclick="setStatusFilter('DELIVERED', this)">Entregues</button>
            </div>

            <!-- Botão de Download CSV Elegantemente Integrado -->
            <a href="/api/reports/orders.csv" class="btn btn-emerald btn-sm" download="Logs_Expedicao_PowerBI.csv">
              📥 Baixar Relatório CSV (Power BI)
            </a>

            <button class="btn btn-secondary btn-sm" onclick="fetchStats()">
              🔄 Atualizar
            </button>
          </div>
        </div>

        <!-- Tabela Formatada -->
        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>ID Pedido</th>
                <th>Horário (Fortaleza)</th>
                <th>Cliente & WhatsApp</th>
                <th>Peça / SKU</th>
                <th>Qtd</th>
                <th>Total (R$)</th>
                <th>Destino Uber Flash</th>
                <th>Status</th>
                <th>Validade Reserva</th>
              </tr>
            </thead>
            <tbody id="orders-tbody">
              <tr>
                <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 3rem;">
                  Carregando pedidos de expedição...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Controle de Conversas & Atendimento Silencioso -->
      <div class="table-container-card">
        <div class="table-toolbar">
          <div class="table-title-area">
            <h2 class="table-title">💬 Controle de Atendimento (Humano vs Robô IA)</h2>
            <span class="table-badge" id="convs-badge-count">0 conversas</span>
          </div>
          <div class="table-controls">
            <button class="btn btn-secondary btn-sm" onclick="fetchConversations()">
              🔄 Atualizar Conversas
            </button>
          </div>
        </div>

        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Cliente / WhatsApp</th>
                <th>Status da IA</th>
                <th>Última Interação</th>
                <th>Silêncio até</th>
                <th>Ação (100% Silenciosa sem o cliente ver)</th>
              </tr>
            </thead>
            <tbody id="convs-tbody">
              <tr>
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                  Carregando conversas...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 3: CATÁLOGO GOOGLE SHEETS -->
    <div class="tab-content" id="tab-catalog">
      <div class="table-container-card">
        <div class="table-toolbar">
          <div class="table-title-area">
            <h2 class="table-title">Peças em Estoque (Sincronizadas com Google Sheets)</h2>
            <span class="table-badge" id="catalog-badge-count">0 peças</span>
          </div>
          <div class="table-controls">
            <a href="https://docs.google.com/spreadsheets/d/1N2gigR8MmuiBRSbtO1TDLnS9AFQS3dJYhxYEEUs7kZY/edit" target="_blank" class="btn btn-secondary btn-sm">
              🔗 Abrir Planilha Google Sheets
            </a>
            <button class="btn btn-primary btn-sm" onclick="syncSheets()">
              🔄 Forçar Sincronização Agora
            </button>
          </div>
        </div>

        <div class="table-responsive">
          <table>
            <thead>
              <tr>
                <th>SKU</th>
                <th>Nome / Descrição da Peça</th>
                <th>Categoria</th>
                <th>Qualidade</th>
                <th>Aro</th>
                <th>Preço Balcão (R$)</th>
                <th>Estoque</th>
                <th>Garantia</th>
              </tr>
            </thead>
            <tbody id="catalog-tbody">
              <tr>
                <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 3rem;">
                  Carregando catálogo do Google Sheets...
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: INTELIGÊNCIA DE VENDAS -->
    <div class="tab-content" id="tab-insights">
      <div class="insights-grid">
        <!-- Ranking das Mais Vendidas -->
        <div class="card insight-card">
          <h3>🏆 Peças Mais Vendidas / Procuradas</h3>
          <div class="ranking-list" id="ranking-container">
            <div style="color: var(--text-muted); font-size: 0.85rem; padding: 1.5rem 0;">
              Carregando ranking...
            </div>
          </div>
        </div>

        <!-- Dúvidas Frequentes -->
        <div class="card insight-card">
          <h3>💬 Dúvidas Mais Frequentes dos Clientes</h3>
          <div id="faq-container">
            <div style="color: var(--text-muted); font-size: 0.85rem; padding: 1.5rem 0;">
              Carregando intenções dos clientes...
            </div>
          </div>
        </div>
      </div>

      <!-- Gráficos -->
      <div class="charts-grid">
        <div class="card chart-card">
          <h3>Distribuição por Qualidade (Original vs. Paralela)</h3>
          <div class="chart-wrapper"><canvas id="qualityChart"></canvas></div>
        </div>
        <div class="card chart-card">
          <h3>Vendas por Categoria de Peça</h3>
          <div class="chart-wrapper"><canvas id="categoryChart"></canvas></div>
        </div>
      </div>
    </div>

    <!-- TAB 5: IA GEMINI & COTAS -->
    <div class="tab-content" id="tab-ai-quota">
      <div class="quota-grid">
        <!-- Guia de Cotas e Limites -->
        <div class="quota-card">
          <h4>⚡ Limites & Cotas da API Gemini</h4>
          <div class="quota-row">
            <span>Plano Atual</span>
            <span id="ai-plan-label" style="color: #34D399;">Google AI Studio (Gratuito)</span>
          </div>
          <div class="quota-row">
            <span>Limite RPM (Por Minuto)</span>
            <span>15 requisições / minuto</span>
          </div>
          <div class="quota-row">
            <span>Limite Diário (Free Tier)</span>
            <span>20 a 1.500 req/dia</span>
          </div>
          <div class="quota-row">
            <span>Limite Diário (Pay-as-you-go)</span>
            <span style="color: #34D399;">Ilimitado (1.000 RPM)</span>
          </div>
          <div class="quota-row">
            <span>Chave Configurada</span>
            <span id="ai-masked-key">Carregando...</span>
          </div>
          <div style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 0.6rem;">
            <a href="https://ai.dev/rate-limit" target="_blank" class="btn btn-secondary btn-sm" style="justify-content: center;">
              📊 Monitorar Limite ao Vivo (ai.dev/rate-limit)
            </a>
            <a href="https://aistudio.google.com/app/plan_information" target="_blank" class="btn btn-secondary btn-sm" style="justify-content: center;">
              🔍 Ver Detalhes do Plano no Google AI Studio
            </a>
            <a href="https://aistudio.google.com/app/apikey" target="_blank" class="btn btn-secondary btn-sm" style="justify-content: center;">
              🔑 Gerar Nova Chave Grátis no Google AI Studio
            </a>
          </div>
        </div>

        <!-- Atualizar Chave Gemini Instantaneamente -->
        <div class="quota-card">
          <h4>🔑 Atualizar Chave da API Gemini</h4>
          <p style="font-size: 0.825rem; color: var(--text-muted); margin-bottom: 1.25rem; line-height: 1.5;">
            Se sua chave gratuita atingir o limite de 20 requisições diárias, gere uma nova chave no Google AI Studio ou vincule um projeto de faturamento no GCP e cole-a abaixo:
          </p>
          <div style="display: flex; flex-direction: column; gap: 0.75rem;">
            <label style="font-size: 0.75rem; color: var(--text-muted); font-weight: 700; text-transform: uppercase;">Nova Chave Gemini API (AIza...)</label>
            <input type="password" id="new-gemini-key" class="sim-input" placeholder="Cole sua nova chave aqui..." />
            <button class="btn btn-primary" onclick="updateGeminiKey()">
              💾 Salvar & Ativar Chave Imediatamente
            </button>
            <p id="key-update-status" style="font-size: 0.8rem; margin-top: 0.5rem;"></p>
          </div>
        </div>

        <!-- Guia de Pausa Humana -->
        <div class="quota-card">
          <h4>🛡️ Pausa Automática por Intervenção Humana</h4>
          <p style="font-size: 0.825rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.5;">
            Como funciona o controle entre o robô e o atendente do balcão:
          </p>
          <div style="display: flex; flex-direction: column; gap: 0.85rem; font-size: 0.825rem;">
            <div style="background: rgba(255,255,255,0.03); padding: 0.85rem; border-radius: 10px; border-left: 3px solid #10B981;">
              <strong style="color: #fff;">1. Você responde no WhatsApp:</strong><br>
              Assim que qualquer atendente digitar no WhatsApp Web ou celular, a IA é <strong>silenciada automaticamente por 3 horas</strong> para aquele cliente.
            </div>
            <div style="background: rgba(255,255,255,0.03); padding: 0.85rem; border-radius: 10px; border-left: 3px solid #6366F1;">
              <strong style="color: #fff;">2. Reativar na hora (#bot):</strong><br>
              Se você quiser devolver a conversa para o robô antes das 3 horas, envie a palavra <code>#bot</code> no chat.
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- Modal WhatsApp QR Code -->
  <div class="modal-overlay" id="wa-modal">
    <div class="modal-box">
      <button class="modal-close" onclick="closeWhatsAppModal()">&times;</button>
      <h3 style="font-size: 1.25rem; font-weight: 800; margin-bottom: 0.5rem; color: #fff;">
        📱 Conectar WhatsApp
      </h3>
      <p style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1.5rem;">
        Abra o WhatsApp no celular &gt; Aparelhos Conectados &gt; Conectar um Aparelho:
      </p>
      <div id="qr-container" style="min-height: 260px; display: flex; align-items: center; justify-content: center;">
        <div style="color: var(--text-muted);">Buscando QR Code...</div>
      </div>
      <div style="margin-top: 1.25rem;">
        <button class="btn btn-secondary btn-sm" onclick="loadWhatsAppQR()">🔄 Atualizar QR Code</button>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toast"></div>

  <script>
    let allOrders = [];
    let currentStatusFilter = 'ALL';
    let qualityChartInst = null;
    let categoryChartInst = null;

    // Relógio ao Vivo de Fortaleza
    function updateClock() {
      const now = new Date();
      const options = { timeZone: 'America/Fortaleza', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
      const timeStr = new Intl.DateTimeFormat('pt-BR', options).format(now);
      const el = document.getElementById('live-clock-text');
      if (el) el.innerText = `${timeStr} • Fortaleza (GMT-3)`;
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Tab Navigation
    function switchTab(tabId, btn) {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));

      if (btn) btn.classList.add('active');
      const target = document.getElementById('tab-' + tabId);
      if (target) target.classList.add('active');

      if (tabId === 'orders') fetchConversations();
      if (tabId === 'catalog') fetchCatalog();
      if (tabId === 'ai-quota') fetchAiQuota();
    }

    // Toast
    function showToast(msg, type = 'success') {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.borderColor = type === 'success' ? '#10B981' : '#F43F5E';
      t.style.display = 'flex';
      setTimeout(() => { t.style.display = 'none'; }, 4000);
    }

    // Carregar Métricas e Pedidos
    async function fetchStats() {
      try {
        const res = await fetch('/api/reports/stats');
        const data = await res.json();

        // KPIs
        document.getElementById('kpi-revenue').innerText = (data.total_revenue || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        document.getElementById('kpi-avg-ticket').innerText = (data.avg_ticket || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        document.getElementById('kpi-orders').innerText = data.total_orders || 0;
        document.getElementById('kpi-uber').innerText = data.uber_orders || 0;
        document.getElementById('kpi-uber-pct').innerText = `${Math.round(data.uber_percentage || 0)}% das saídas via Uber Flash`;
        document.getElementById('kpi-products').innerText = data.total_products || 0;

        document.getElementById('tab-orders-count').innerText = data.total_orders || 0;
        document.getElementById('table-badge-count').innerText = `${data.total_orders || 0} pedidos`;
        document.getElementById('tab-catalog-count').innerText = data.total_products || 0;

        // Status da Loja
        const sBadge = document.getElementById('store-badge');
        const sText = document.getElementById('store-status');
        if (data.is_store_open) {
          sBadge.className = 'badge badge-emerald';
          sText.innerText = 'Loja Aberta';
        } else {
          sBadge.className = 'badge badge-amber';
          sText.innerText = 'Fora do Expediente';
        }

        // Tabela de Pedidos
        allOrders = data.recent_orders || [];
        renderOrdersTable(allOrders);

        // Ranking
        renderRanking(data.top_products || []);

        // Intenções FAQ
        renderFaq(data.frequent_intents || []);

        // Gráficos
        renderCharts(data.quality_breakdown || {}, data.category_breakdown || {});

      } catch (err) {
        console.error('Erro ao buscar stats:', err);
      }
    }

    // Renderizar Tabela de Pedidos
    function renderOrdersTable(orders) {
      const tbody = document.getElementById('orders-tbody');
      if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">Nenhum pedido registrado nesta categoria.</td></tr>`;
        return;
      }

      tbody.innerHTML = orders.map(o => {
        const cleanPhone = (o.customer_phone || '').replace(/\D/g, '');
        const waLink = cleanPhone ? `https://wa.me/${cleanPhone}` : '#';
        const isUber = !!o.destination_address;

        let statusClass = 'status-pending';
        let statusLabel = 'Pendente';
        if (o.status === 'READY_FOR_PICKUP') { statusClass = 'status-ready'; statusLabel = 'Pronto p/ Retirada'; }
        else if (o.status === 'DELIVERED') { statusClass = 'status-delivered'; statusLabel = 'Entregue / Concluído'; }
        else if (o.status === 'CANCELLED') { statusClass = 'status-cancelled'; statusLabel = 'Cancelado'; }

        return `
          <tr>
            <td style="font-family: monospace; font-size: 0.8rem; color: #818CF8;">#${(o.id || '').substring(0, 8)}</td>
            <td>${o.created_at || '--'}</td>
            <td>
              <div class="customer-cell">
                <span class="customer-name">${o.customer_name || 'Cliente'}</span>
                <a href="${waLink}" target="_blank" class="customer-wa">📱 ${o.customer_phone || ''}</a>
              </div>
            </td>
            <td>
              <strong>${o.product_sku || '--'}</strong>
            </td>
            <td><span style="font-weight: 700;">${o.quantity}</span></td>
            <td><strong style="color: #34D399;">${(o.product_price * o.quantity).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</strong></td>
            <td>
              ${isUber ? `<span>🛵 ${o.destination_address}</span>` : `<span style="color: var(--text-dim);">🏪 Balcão</span>`}
            </td>
            <td><span class="status-badge ${statusClass}">${statusLabel}</span></td>
            <td><span style="color: #FBBF24; font-size: 0.8rem;">⏰ Até ${o.expires_at || '--'}</span></td>
          </tr>
        `;
      }).join('');
    }

    // Filtros de Pedidos
    function setStatusFilter(status, btn) {
      currentStatusFilter = status;
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterOrders();
    }

    function filterOrders() {
      const q = (document.getElementById('order-search').value || '').toLowerCase();
      const filtered = allOrders.filter(o => {
        const matchesStatus = (currentStatusFilter === 'ALL') || (o.status === currentStatusFilter);
        const matchesSearch = !q ||
          (o.customer_name || '').toLowerCase().includes(q) ||
          (o.customer_phone || '').includes(q) ||
          (o.product_sku || '').toLowerCase().includes(q) ||
          (o.destination_address || '').toLowerCase().includes(q);
        return matchesStatus && matchesSearch;
      });
      renderOrdersTable(filtered);
    }

    // Ranking
    function renderRanking(list) {
      const container = document.getElementById('ranking-container');
      if (!list || list.length === 0) {
        container.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">Nenhuma venda registrada ainda.</div>`;
        return;
      }
      container.innerHTML = list.map((item, idx) => {
        const badgeClass = idx === 0 ? 'top-1' : idx === 1 ? 'top-2' : idx === 2 ? 'top-3' : 'top-other';
        const medal = idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${idx+1}`;
        const isOrig = (item.quality || '').includes('ORIGINAL');
        const tagClass = isOrig ? 'tag-original' : 'tag-paralela';
        return `
          <div class="ranking-item">
            <div class="ranking-info">
              <div class="ranking-badge ${badgeClass}">${medal}</div>
              <div>
                <div style="font-weight: 700; color: #fff;">${item.name}</div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem;">
                  <span class="tag-quality ${tagClass}">${item.quality || 'PEÇA'}</span> • SKU: ${item.sku}
                </div>
              </div>
            </div>
            <div style="text-align: right;">
              <div style="font-weight: 800; color: #34D399; font-size: 0.95rem;">${item.quantity} saídas</div>
              <div style="font-size: 0.75rem; color: var(--text-dim);">${item.revenue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</div>
            </div>
          </div>
        `;
      }).join('');
    }

    // FAQ
    function renderFaq(intents) {
      const container = document.getElementById('faq-container');
      if (!intents || intents.length === 0) return;
      container.innerHTML = intents.map(i => `
        <div class="faq-item">
          <div class="faq-header">
            <span style="font-weight: 600; color: #E2E8F0;">${i.title}</span>
            <span style="color: #818CF8; font-weight: 700;">${i.count} ocorrências</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${i.percentage}%;"></div>
          </div>
          <div style="font-size: 0.725rem; color: var(--text-dim); margin-top: 0.3rem;">${i.example || ''}</div>
        </div>
      `).join('');
    }

    // Gráficos Chart.js
    function renderCharts(qualityData, categoryData) {
      if (qualityChartInst) qualityChartInst.destroy();
      const qCtx = document.getElementById('qualityChart').getContext('2d');
      qualityChartInst = new Chart(qCtx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(qualityData),
          datasets: [{
            data: Object.values(qualityData),
            backgroundColor: ['#F59E0B', '#6366F1', '#10B981'],
            borderColor: '#0E1420',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 11 } } } }
        }
      });

      if (categoryChartInst) categoryChartInst.destroy();
      const cCtx = document.getElementById('categoryChart').getContext('2d');
      categoryChartInst = new Chart(cCtx, {
        type: 'bar',
        data: {
          labels: Object.keys(categoryData).length ? Object.keys(categoryData) : ['Telas Frontais'],
          datasets: [{
            label: 'Unidades Vendidas',
            data: Object.keys(categoryData).length ? Object.values(categoryData) : [1],
            backgroundColor: '#6366F1',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: { ticks: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 10 } }, grid: { display: false } },
            y: { ticks: { color: '#94A3B8', font: { family: 'Plus Jakarta Sans', size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
          },
          plugins: { legend: { display: false } }
        }
      });
    }

    // Catálogo Google Sheets
    async function fetchCatalog() {
      try {
        const res = await fetch('/api/catalog');
        const data = await res.json();
        const tbody = document.getElementById('catalog-tbody');
        document.getElementById('catalog-badge-count').innerText = `${data.total || 0} peças cadastradas`;

        if (!data.items || data.items.length === 0) {
          tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2rem;">Nenhuma peça encontrada na planilha.</td></tr>`;
          return;
        }

        tbody.innerHTML = data.items.map(p => {
          const isOrig = (p.quality || '').includes('ORIGINAL');
          const tagClass = isOrig ? 'tag-original' : 'tag-paralela';
          return `
            <tr>
              <td style="font-family: monospace; font-weight: 700; color: #818CF8;">${p.sku}</td>
              <td><strong style="color: #fff;">${p.name}</strong></td>
              <td><span style="color: var(--text-muted); font-size: 0.8rem;">${p.category}</span></td>
              <td><span class="tag-quality ${tagClass}">${p.quality}</span></td>
              <td>${p.has_frame ? 'Com Aro' : 'Sem Aro'}</td>
              <td><strong style="color: #34D399;">${p.price.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</strong></td>
              <td>
                <span style="font-weight: 700; color: ${p.stock_quantity > 0 ? '#34D399' : '#F43F5E'}">
                  ${p.stock_quantity > 0 ? p.stock_quantity + ' em estoque' : 'Esgotado'}
                </span>
              </td>
              <td><span style="color: var(--text-muted); font-size: 0.8rem;">${p.warranty_days} dias</span></td>
            </tr>
          `;
        }).join('');
      } catch (err) {
        console.error('Erro ao buscar catálogo:', err);
      }
    }

    // Sincronizar Google Sheets
    async function syncSheets() {
      showToast('Sincronizando com Google Sheets...', 'success');
      try {
        const res = await fetch('/api/reports/sync-sheets', { method: 'POST' });
        const data = await res.json();
        showToast(`Google Sheets sincronizado! (${data.total_items || 0} peças atualizadas)`, 'success');
        fetchStats();
        fetchCatalog();
      } catch (err) {
        showToast('Erro ao sincronizar com Google Sheets', 'error');
      }
    }

    // Simulador
    async function testSimulate() {
      const input = document.getElementById('sim-query');
      const box = document.getElementById('sim-response');
      const msg = input.value.trim();
      if (!msg) return;

      box.style.display = 'block';
      box.innerText = 'Consultando estoque e inteligência do balcão...';

      try {
        const res = await fetch('/api/simulator/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        box.innerText = data.reply || 'Sem resposta.';
      } catch (err) {
        box.innerText = 'Erro na simulação: ' + err;
      }
    }

    // Cotas e Chave Gemini
    async function fetchAiQuota() {
      try {
        const res = await fetch('/api/ai/quota-info');
        const data = await res.json();
        document.getElementById('ai-masked-key').innerText = data.masked_key || 'Não configurada';
      } catch (err) {
        console.error('Erro ao buscar info de cotas:', err);
      }
    }

    async function updateGeminiKey() {
      const input = document.getElementById('new-gemini-key');
      const statusEl = document.getElementById('key-update-status');
      const key = input.value.trim();

      if (!key) {
        statusEl.innerText = 'Cole uma chave válida primeiro.';
        statusEl.style.color = '#F43F5E';
        return;
      }

      statusEl.innerText = 'Validando e testando chave com Google GenAI...';
      statusEl.style.color = '#818CF8';

      try {
        const res = await fetch('/api/ai/update-key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ new_key: key })
        });
        const data = await res.json();

        if (res.ok) {
          statusEl.innerText = data.message || 'Chave ativada com sucesso!';
          statusEl.style.color = '#34D399';
          input.value = '';
          showToast('Chave Gemini atualizada com sucesso!', 'success');
          fetchAiQuota();
        } else {
          statusEl.innerText = data.detail || 'Erro ao validar chave.';
          statusEl.style.color = '#F43F5E';
        }
      } catch (err) {
        statusEl.innerText = 'Erro ao enviar chave: ' + err;
        statusEl.style.color = '#F43F5E';
      }
    }

    // Modal WhatsApp QR Code
    function openWhatsAppModal() {
      document.getElementById('wa-modal').style.display = 'flex';
      loadWhatsAppQR();
    }
    function closeWhatsAppModal() {
      document.getElementById('wa-modal').style.display = 'none';
    }

    async function loadWhatsAppQR() {
      const container = document.getElementById('qr-container');
      container.innerHTML = '<div style="color: var(--text-muted);">Buscando status do WhatsApp...</div>';
      try {
        const res = await fetch('/api/whatsapp/qrcode');
        const data = await res.json();
        if (data.status === 'connected') {
          container.innerHTML = `
            <div style="padding: 2rem;">
              <div style="font-size: 3rem; margin-bottom: 0.5rem;">✅</div>
              <h4 style="font-weight: 800; color: #34D399; font-size: 1.15rem;">WhatsApp Conectado!</h4>
              <p style="font-size: 0.825rem; color: var(--text-muted); margin-top: 0.5rem;">
                Instância victor-cell-01 ativa e pronta para responder no balcão.
              </p>
            </div>
          `;
          document.getElementById('wa-badge').className = 'badge badge-emerald';
          document.getElementById('wa-status').innerText = 'WhatsApp Conectado';
        } else if (data.status === 'qrcode' && data.qrcode) {
          container.innerHTML = `<img src="${data.qrcode}" style="max-width: 260px; border-radius: 12px; background: white; padding: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);" />`;
          document.getElementById('wa-status').innerText = 'Aguardando Escaneamento';
        } else {
          container.innerHTML = `<div style="color: var(--text-muted); padding: 1rem;">${data.message || 'Instância em inicialização...'}</div>`;
        }
      } catch (err) {
        container.innerHTML = `<div style="color: #F43F5E;">Erro ao conectar à Evolution API: ${err}</div>`;
      }
    }

    // Controle de Conversas
    async function fetchConversations() {
      try {
        const res = await fetch('/api/conversations');
        const data = await res.json();
        const tbody = document.getElementById('convs-tbody');
        const convs = data.conversations || [];
        document.getElementById('convs-badge-count').innerText = `${convs.length} conversas`;

        if (convs.length === 0) {
          tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">Nenhuma conversa registrada ainda.</td></tr>`;
          return;
        }

        tbody.innerHTML = convs.map(c => {
          const cleanPhone = (c.phone || '').replace(/\D/g, '');
          const waLink = cleanPhone ? `https://wa.me/${cleanPhone}` : '#';
          const isActive = c.is_ai_active;

          return `
            <tr>
              <td>
                <a href="${waLink}" target="_blank" class="customer-wa" style="font-size: 0.9rem; font-weight: 700;">
                  📱 ${c.phone}
                </a>
              </td>
              <td>
                ${isActive
                  ? `<span class="badge badge-emerald"><span class="badge-dot"></span> 🤖 Robô Respondendo</span>`
                  : `<span class="badge badge-amber"><span class="badge-dot"></span> ⏸️ Humano no Controle (Silenciado)</span>`
                }
              </td>
              <td>${c.last_activity || '--'}</td>
              <td>
                ${c.paused_until
                  ? `<span style="color: #FBBF24; font-weight: 600;">⏰ Até ${c.paused_until}</span>`
                  : `<span style="color: var(--text-dim);">Automático</span>`
                }
              </td>
              <td>
                ${!isActive
                  ? `<button class="btn btn-emerald btn-sm" onclick="resumeConversation('${c.phone}')">🤖 Reativar IA Agora (Silencioso)</button>`
                  : `<button class="btn btn-secondary btn-sm" onclick="pauseConversation('${c.phone}')">⏸️ Pausar IA por 3h</button>`
                }
              </td>
            </tr>
          `;
        }).join('');
      } catch (err) {
        console.error('Erro ao buscar conversas:', err);
      }
    }

    async function resumeConversation(phone) {
      try {
        const res = await fetch(`/api/conversations/${phone}/resume`, { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'IA reativada para o cliente!', 'success');
        fetchConversations();
      } catch (err) {
        showToast('Erro ao reativar IA: ' + err, 'error');
      }
    }

    async function pauseConversation(phone) {
      try {
        const res = await fetch(`/api/conversations/${phone}/pause`, { method: 'POST' });
        const data = await res.json();
        showToast(data.message || 'IA pausada por 3h!', 'success');
        fetchConversations();
      } catch (err) {
        showToast('Erro ao pausar IA: ' + err, 'error');
      }
    }

    // Inicialização
    fetchStats();
    fetchConversations();
  </script>
</body>
</html>
"""
