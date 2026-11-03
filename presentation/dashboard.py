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
  <link rel="stylesheet" href="/static/css/dashboard.css?v=20261102_05">
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
        <button class="nav-tab" onclick="switchTab('orders')" title="Separação & Balcão">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
          <span>Separação & Balcão</span>
          <span class="tab-badge" id="badge-orders-count">0</span>
        </button>
        <button class="nav-tab" onclick="switchTab('customers')" title="Clientes">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          <span>Clientes</span>
          <span class="tab-badge" id="badge-customers-count">0</span>
        </button>

        <!-- GRUPO 2: ESTOQUE & ERP NATIVO -->
        <div class="nav-section-label">Estoque & ERP Nativo</div>
        <button class="nav-tab" onclick="switchTab('overview')" title="Métricas Operacionais">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          <span>Métricas Operacionais</span>
        </button>
        <button class="nav-tab" onclick="switchTab('reports')" title="Relatórios & Demanda">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
          <span>Relatórios & Demanda</span>
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
          <button class="btn-top-action" id="btn-theme-toggle" onclick="toggleTheme()" title="Alternar Modo Claro / Escuro">
            <span id="theme-toggle-icon">☀️</span>
            <span id="theme-toggle-label">Modo Claro</span>
          </button>
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
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 85%;"></div></td><td><div class="skeleton-table-cell" style="width: 70%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td></tr>
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 45%;"></div></td><td><div class="skeleton-table-cell" style="width: 80%;"></div></td><td><div class="skeleton-table-cell" style="width: 75%;"></div></td><td><div class="skeleton-table-cell" style="width: 55%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td></tr>
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 55%;"></div></td><td><div class="skeleton-table-cell" style="width: 70%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td></tr>
            </tbody>
          </table>
        </div>

        <!-- Visualização Mobile (Cards Touch Fáceis de Clicar) -->
        <div class="mobile-card-deck" id="convs-cards-mobile">
          <div style="text-align: center; padding: 2rem; color: var(--text-muted);"><span class="skeleton-box" style="width: 80%; height: 20px;"></span></div>
        </div>
      </div>
    </div>

    <!-- TAB 2: SEPARAÇÃO DE PEÇAS & BALCÃO DE SAÍDA -->
    <div class="tab-pane" id="tab-orders">
      <div class="section-card">
        <div class="section-toolbar">
          <div class="section-title-group">
            <h2 class="section-title">Separação & Balcão</h2>
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
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 40%;"></div></td><td><div class="skeleton-table-cell" style="width: 75%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td><td><div class="skeleton-table-cell" style="width: 55%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td></tr>
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 45%;"></div></td><td><div class="skeleton-table-cell" style="width: 70%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td><td><div class="skeleton-table-cell" style="width: 55%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td></tr>
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 38%;"></div></td><td><div class="skeleton-table-cell" style="width: 80%;"></div></td><td><div class="skeleton-table-cell" style="width: 55%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 70%;"></div></td><td><div class="skeleton-table-cell" style="width: 55%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td></tr>
            </tbody>
          </table>
        </div>

        <div class="mobile-card-deck" id="orders-cards-mobile"></div>
      </div>
    </div>

    <!-- TAB: ASSISTÊNCIAS TÉCNICAS & CLIENTES (MÓDULO INDEPENDENTE) -->
    <div class="tab-pane" id="tab-customers">
      <!-- 4 KPIS DO MÓDULO DE CLIENTES -->
      <div class="kpi-grid" style="margin-bottom: 1.25rem;">
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Total de Assistências</span>
            <div class="kpi-icon" style="background: rgba(99, 102, 241, 0.12); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-cust-total" style="color: #818CF8;">0</div>
          <div class="kpi-sub">Parceiros cadastrados na base</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Alta Recorrência (VIPs)</span>
            <div class="kpi-icon" style="background: rgba(16, 185, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-cust-recurrent" style="color: #34D399;">0</div>
          <div class="kpi-sub">Recompra semanal garantida</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">LTV Médio por Oficina</span>
            <div class="kpi-icon" style="background: rgba(245, 158, 11, 0.12); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-cust-ltv" style="color: #FBBF24;">R$ 0,00</div>
          <div class="kpi-sub">Gasto acumulado por parceiro</div>
        </div>

        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Entregas por Uber Flash</span>
            <div class="kpi-icon" style="background: rgba(6, 182, 212, 0.12); color: #06B6D4; border: 1px solid rgba(6, 182, 212, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-cust-uber" style="color: #38BDF8;">0</div>
          <div class="kpi-sub">Despachadas sem deslocamento</div>
        </div>
      </div>

      <!-- TABELA DINÂMICA DE CLIENTES & ASSISTÊNCIAS -->
      <div class="section-card">
        <div class="section-toolbar" style="flex-direction: column; align-items: stretch; gap: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
            <div class="section-title-group">
              <h2 class="section-title" style="display: flex; align-items: center; gap: 8px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #818CF8;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                Clientes
              </h2>
              <span class="badge-count" id="customers-counter">0 assistências</span>
            </div>
            <div class="toolbar-actions" style="gap: 0.5rem;">
              <input type="text" id="customers-search" placeholder="Buscar cliente, telefone ou bairro..." class="search-input" oninput="filterCustomersTable()" style="min-width: 260px;">
              <button class="btn btn-primary btn-sm" onclick="openNewCustomerModal()" style="display: inline-flex; align-items: center; gap: 5px;">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                + Novo Cliente
              </button>
              <button class="btn btn-secondary btn-sm" onclick="fetchCustomers()"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -1px; margin-right: 4px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Atualizar</button>
            </div>
          </div>

          <!-- CONTROLES AVANÇADOS: ORDENAÇÃO POR RECORRÊNCIA, FAIXA E TIERS -->
          <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; padding-top: 0.5rem; border-top: 1px solid var(--border-subtle); align-items: center; justify-content: space-between;">
            <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
              <!-- SELECT DE ORDENAÇÃO DINÂMICA -->
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 600;">Ordenar por:</span>
                <select id="cust-sort-select" onchange="applyCustomerSort(this.value)" class="select-styled" style="font-size: 0.78rem; padding: 0.35rem 1.8rem 0.35rem 0.65rem;">
                  <option value="recurrence_desc">🔄 Maior Recorrência (Mais Pedidos)</option>
                  <option value="recurrence_asc">🔄 Menor Recorrência (Menos Pedidos)</option>
                  <option value="spent_desc">💰 Maior Faturamento (R$ LTV)</option>
                  <option value="spent_asc">💰 Menor Faturamento (R$ LTV)</option>
                  <option value="name_asc">🔤 Nome da Oficina (A - Z)</option>
                  <option value="name_desc">🔤 Nome da Oficina (Z - A)</option>
                  <option value="uber_desc">🚗 Mais Entregas Uber Flash</option>
                </select>
              </div>

              <!-- SELECT DE FAIXA DE RECORRÊNCIA -->
              <div style="display: flex; align-items: center; gap: 6px;">
                <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 600;">Faixa de Recorrência:</span>
                <select id="cust-recurrence-bracket" onchange="setCustomerRecurrenceBracket(this.value)" class="select-styled" style="font-size: 0.78rem; padding: 0.35rem 1.8rem 0.35rem 0.65rem;">
                  <option value="all">Todas as Frequências</option>
                  <option value="vip_heavy">🔥 Super Recorrente (15+ pedidos)</option>
                  <option value="high">⭐ Alta Recorrência (5 - 14 pedidos)</option>
                  <option value="medium">⚡ Recorrência Média (2 - 4 pedidos)</option>
                  <option value="new">🌱 Primeira Compra (1 pedido)</option>
                  <option value="zero">💤 Sem Compras Recentes (0 pedidos)</option>
                </select>
              </div>
            </div>

            <!-- CHIPS DE FILTRO RÁPIDO DE FIDELIDADE -->
            <div style="display: flex; flex-wrap: wrap; gap: 0.45rem; align-items: center;">
              <span style="font-size: 0.75rem; color: #94A3B8; font-weight: 600; margin-right: 0.25rem;">Fidelidade:</span>
              <button class="catalog-filter-btn active" data-cust-tier="all" onclick="setCustomerTierFilter('all', this)">Todas</button>
              <button class="catalog-filter-btn" data-cust-tier="VIP_PLATINUM" onclick="setCustomerTierFilter('VIP_PLATINUM', this)">👑 Platinum</button>
              <button class="catalog-filter-btn" data-cust-tier="OURO_RECORRENTE" onclick="setCustomerTierFilter('OURO_RECORRENTE', this)">🥇 Ouro</button>
              <button class="catalog-filter-btn" data-cust-tier="PRATA_ATIVO" onclick="setCustomerTierFilter('PRATA_ATIVO', this)">🥈 Prata</button>
              <button class="catalog-filter-btn" data-cust-tier="NOVO_PARCEIRO" onclick="setCustomerTierFilter('NOVO_PARCEIRO', this)">🌱 Novos</button>
            </div>
          </div>
        </div>

        <!-- TABELA DE CLIENTES (DESKTOP) COM ORDENAÇÃO POR COLUNAS -->
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th onclick="toggleCustomerColumnSort('name')" style="cursor: pointer; user-select: none;" title="Clique para ordenar por Nome">
                  Assistência Técnica / Oficina <span id="sort-icon-name" class="sort-icon">⇅</span>
                </th>
                <th onclick="toggleCustomerColumnSort('phone')" style="cursor: pointer; user-select: none;" title="Clique para ordenar por Telefone">
                  Telefone WhatsApp <span id="sort-icon-phone" class="sort-icon">⇅</span>
                </th>
                <th onclick="toggleCustomerColumnSort('tier')" style="cursor: pointer; user-select: none;" title="Clique para ordenar por Fidelidade">
                  Nível de Fidelidade <span id="sort-icon-tier" class="sort-icon">⇅</span>
                </th>
                <th onclick="toggleCustomerColumnSort('orders_count')" style="cursor: pointer; user-select: none; text-align: center;" title="Clique para ordenar por Recorrência de Pedidos">
                  Pedidos Fechados (Recorrência) <span id="sort-icon-orders_count" class="sort-icon active">▼</span>
                </th>
                <th onclick="toggleCustomerColumnSort('total_spent')" style="cursor: pointer; user-select: none;" title="Clique para ordenar por Volume Total">
                  Volume Total (R$) <span id="sort-icon-total_spent" class="sort-icon">⇅</span>
                </th>
                <th onclick="toggleCustomerColumnSort('uber_deliveries')" style="cursor: pointer; user-select: none;" title="Clique para ordenar por Entregas Uber">
                  Entregas Uber <span id="sort-icon-uber_deliveries" class="sort-icon">⇅</span>
                </th>
                <th style="text-align: center;">Ações de Balcão</th>
              </tr>
            </thead>
            <tbody id="customers-tbody">
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 70%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 40%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td></tr>
            </tbody>
          </table>
        </div>

        <!-- PAGINAÇÃO DE CLIENTES (10 POR PÁGINA) -->
        <div class="pagination-bar" id="customers-pagination-bar">
          <div style="font-size: 0.8rem; color: var(--text-muted);" id="customers-pagination-info">
            Mostrando 1 a 10 de 0 assistências
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <button class="pagination-btn" id="btn-cust-prev" onclick="changeCustomerPage(-1)" disabled>
              ← Anterior
            </button>
            <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-main); padding: 0 0.5rem;" id="customers-page-number">1 / 1</span>
            <button class="pagination-btn" id="btn-cust-next" onclick="changeCustomerPage(1)" disabled>
              Próxima →
            </button>
          </div>
        </div>

        <div class="mobile-card-deck" id="customers-cards-mobile"></div>
      </div>
    </div>

    <!-- TAB 3: VISÃO GERAL & KPIS -->
    <div class="tab-pane" id="tab-overview">

      <!-- KPIS PRINCIPAIS (CONSOLIDADOS EM MÉTRICAS & RELATÓRIOS) -->
      <div class="kpi-grid">
      <div class="kpi-card clickable-card" onclick="navigateWithFilter('orders', { status: 'CONFIRMED' })" title="Clique para ver Pedidos Confirmados">
        <div class="kpi-header">
          <span class="kpi-title">Faturamento em Pedidos</span>
          <div class="kpi-icon" style="background: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-revenue" style="color: #34D399;">R$ 0,00</div>
        <div class="kpi-sub"><span style="color: #10B981; font-weight: 700;">● Confirmados</span> no balcão e Uber ↗</div>
      </div>

      <div class="kpi-card clickable-card" onclick="navigateWithFilter('conversations', {})" title="Clique para ver Atendimentos no WhatsApp">
        <div class="kpi-header">
          <span class="kpi-title">Atendimentos no WhatsApp</span>
          <div class="kpi-icon" style="background: rgba(99, 102, 241, 0.12); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-active-chats" style="color: #A5B4FC;">0</div>
        <div class="kpi-sub" id="kpi-ai-status">Atendimento Automático Ativo ↗</div>
      </div>

      <div class="kpi-card clickable-card" onclick="navigateWithFilter('orders', { status: 'DISPATCHED_UBER' })" title="Clique para ver Entregas Uber Flash">
        <div class="kpi-header">
          <span class="kpi-title">Saídas Balcão & Uber</span>
          <div class="kpi-icon" style="background: rgba(245, 158, 11, 0.12); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13"></rect><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon><circle cx="5.5" cy="18.5" r="2.5"></circle><circle cx="18.5" cy="18.5" r="2.5"></circle></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-uber" style="color: #FBBF24;">0%</div>
        <div class="kpi-sub" id="kpi-uber-count">0 pedidos para entrega ↗</div>
      </div>

      <div class="kpi-card clickable-card" onclick="navigateWithFilter('catalog', {})" title="Clique para abrir Catálogo de Peças">
        <div class="kpi-header">
          <span class="kpi-title">Peças no Catálogo</span>
          <div class="kpi-icon" style="background: rgba(6, 182, 212, 0.12); color: #06B6D4; border: 1px solid rgba(6, 182, 212, 0.25);">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
          </div>
        </div>
        <div class="kpi-val" id="kpi-stock-items" style="color: #38BDF8;">0</div>
        <div class="kpi-sub">Sincronizado c/ Google Sheets ↗</div>
      </div>
    </div>



      <!-- AUDITORIA & CATEGORIZAÇÃO DE MENSAGENS DO WHATSAPP (TEMPO REAL) -->
      <div class="card banner-card-gradient" style="margin-bottom: 1.25rem;">
        <div class="card-header" style="padding: 1rem 1.25rem 0.5rem 1.25rem;">
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
        <div class="card-body" style="padding: 1rem 1.25rem 1.25rem 1.25rem;">
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.85rem;" id="wa-categories-grid">
            <div class="wa-cat-card clickable-card" onclick="navigateWithFilter('conversations', { search: 'quanto' })" style="border-left: 3px solid #F59E0B;" title="Clique para ver cotações">
              <div class="wa-cat-card-header"><span>Cotações de Peças</span><span>💬</span></div>
              <div style="display: flex; align-items: baseline; gap: 8px;">
                <div class="wa-cat-card-val" style="color: #FBBF24;" id="cat-val-quotes">815</div>
                <span id="cat-pct-quotes" style="font-size: 0.725rem; color: #F59E0B; font-weight: 700;">80.4%</span>
              </div>
              <div class="wa-cat-card-sub">Preços e modelos consultados ↗</div>
            </div>
            <div class="wa-cat-card clickable-card" onclick="navigateWithFilter('orders', { status: 'CONFIRMED' })" style="border-left: 3px solid #10B981;" title="Clique para ver pedidos fechados">
              <div class="wa-cat-card-header"><span>Pedidos Fechados</span><span>🛒</span></div>
              <div style="display: flex; align-items: baseline; gap: 8px;">
                <div class="wa-cat-card-val" style="color: #34D399;" id="cat-val-orders">58</div>
                <span id="cat-pct-orders" style="font-size: 0.725rem; color: #10B981; font-weight: 700;">5.7%</span>
              </div>
              <div class="wa-cat-card-sub">Balcão e Uber Flash ↗</div>
            </div>
            <div class="wa-cat-card clickable-card" onclick="navigateWithFilter('reports', {})" style="border-left: 3px solid #EF4444;" title="Clique para ver relatório de faltas">
              <div class="wa-cat-card-header"><span>Sem Saldo / Ruptura</span><span>⚠️</span></div>
              <div style="display: flex; align-items: baseline; gap: 8px;">
                <div class="wa-cat-card-val" style="color: #F87171;" id="cat-val-ruptures">111</div>
                <span id="cat-pct-ruptures" style="font-size: 0.725rem; color: #EF4444; font-weight: 700;">10.9%</span>
              </div>
              <div class="wa-cat-card-sub">Demanda não atendida em estoque ↗</div>
            </div>
            <div class="wa-cat-card clickable-card" onclick="navigateWithFilter('conversations', { search: 'atendente' })" style="border-left: 3px solid #818CF8;" title="Clique para ver transbordos para atendente">
              <div class="wa-cat-card-header"><span>Transbordo p/ Balcão</span><span>👤</span></div>
              <div style="display: flex; align-items: baseline; gap: 8px;">
                <div class="wa-cat-card-val" style="color: #A5B4FC;" id="cat-val-handoffs">12</div>
                <span id="cat-pct-handoffs" style="font-size: 0.725rem; color: #818CF8; font-weight: 700;">1.2%</span>
              </div>
              <div class="wa-cat-card-sub">Assumido por atendente humano ↗</div>
            </div>
            <div class="wa-cat-card clickable-card" onclick="navigateWithFilter('conversations', { search: 'recusa' })" style="border-left: 3px solid #64748B;" title="Clique para ver fora de escopo">
              <div class="wa-cat-card-header"><span>Fora de Escopo</span><span>🚫</span></div>
              <div style="display: flex; align-items: baseline; gap: 8px;">
                <div class="wa-cat-card-val" style="color: #94A3B8;" id="cat-val-outofscope">18</div>
                <span id="cat-pct-outofscope" style="font-size: 0.725rem; color: #94A3B8; font-weight: 700;">1.8%</span>
              </div>
              <div class="wa-cat-card-sub">Celulares, serviços ou recusas ↗</div>
            </div>
          </div>

          <!-- DISTRIBUIÇÃO PROPORCIONAL SLEEK -->
          <div style="margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.45rem; font-size: 0.735rem; color: #94A3B8;">
              <span style="font-weight: 600;">Distribuição Proporcional das Mensagens</span>
              <span id="wa-categories-total-count" style="font-weight: 700; color: #CBD5E1;">1.014 interações registradas</span>
            </div>
            <div style="background: rgba(255,255,255,0.06); border-radius: 999px; height: 6px; overflow: hidden; display: flex;" id="wa-categories-bar" title="Distribuição percentual das mensagens">
              <div style="width: 80.4%; background: #F59E0B;" title="Cotações: 80.4%"></div>
              <div style="width: 5.7%; background: #10B981;" title="Pedidos: 5.7%"></div>
              <div style="width: 10.9%; background: #EF4444;" title="Rupturas: 10.9%"></div>
              <div style="width: 1.2%; background: #818CF8;" title="Transbordo: 1.2%"></div>
              <div style="width: 1.8%; background: #64748B;" title="Fora de Escopo: 1.8%"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 4 KPIS DO FUNIL DE WHATSAPP -->
      <div class="kpis-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1.25rem; margin-bottom: 1.5rem;">
        <div class="kpi-card" style="padding: 1.35rem 1.4rem;">
          <div class="kpi-label">Pedidos que Saíram (Fechados)</div>
          <div class="kpi-value" style="color: #10B981;" id="kpi-chat-closed">58</div>
          <div class="kpi-subtext" style="color: #34D399;">Taxa de conversão: <strong id="kpi-chat-conv-rate">34.3%</strong></div>
        </div>
        <div class="kpi-card" style="padding: 1.35rem 1.4rem;">
          <div class="kpi-label">Perdidos por Falta de Estoque</div>
          <div class="kpi-value" style="color: #EF4444;" id="kpi-chat-lost">111</div>
          <div class="kpi-subtext" style="color: #F87171;">Demanda reprimida (Ruptura no balcão)</div>
        </div>
        <div class="kpi-card" style="padding: 1.35rem 1.4rem;">
          <div class="kpi-label">Taxa de Recorrência (Recompra)</div>
          <div class="kpi-value" style="color: #818CF8;" id="kpi-chat-recurrence">81.1%</div>
          <div class="kpi-subtext" style="color: #A5B4FC;"><strong id="kpi-chat-workshops">30 de 37</strong> oficinas voltam a pedir</div>
        </div>
        <div class="kpi-card" style="padding: 1.35rem 1.4rem;">
          <div class="kpi-label">Cotações Mineradas no Zap</div>
          <div class="kpi-value" style="color: #F59E0B;" id="kpi-chat-volume">984</div>
          <div class="kpi-subtext" style="color: #FCD34D;">58 modelos de tablet monitorados</div>
        </div>
      </div>

      <!-- GRID DE 4 CARDS (3 GRÁFICOS + LISTAGEM DE TOP ASSISTÊNCIAS) -->
      <div class="charts-grid" style="margin-bottom: 1.25rem;">
        <div class="chart-card">
          <h3>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #F59E0B;"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a10 10 0 0 1 10 10"></path></svg>
            Original vs. Paralela
          </h3>
          <div class="chart-canvas-wrapper">
            <canvas id="chartQuality"></canvas>
          </div>
        </div>
        <div class="chart-card">
          <h3>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #6366F1;"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>
            Distribuição de Vendas por Categoria
          </h3>
          <div class="chart-canvas-wrapper">
            <canvas id="chartCategory"></canvas>
          </div>
        </div>
        <div class="chart-card">
          <h3>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #10B981;"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
            Resultados do Funil de Vendas
          </h3>
          <div class="chart-canvas-wrapper">
            <canvas id="chartChatFunnel"></canvas>
          </div>
        </div>
        <div class="chart-card clickable-card" onclick="navigateWithFilter('customers', {})" style="display: flex; flex-direction: column; cursor: pointer;" title="Clique para abrir o módulo de Assistências & Clientes">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <h3 style="margin-bottom: 0; display: flex; align-items: center; gap: 8px;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #818CF8;"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
              Distribuição de Clientes & Fidelidade
            </h3>
            <span class="badge-count" style="font-size: 0.75rem; color: var(--primary); font-weight: 700;">Ver Lista ↗</span>
          </div>
          <div class="chart-canvas-wrapper">
            <canvas id="chartCustomersShare"></canvas>
            <div id="top-assistencias-list" style="display: none;"></div>
          </div>
        </div>
      </div>
    </div> <!-- /tab-overview -->

    <!-- TAB: RELATÓRIOS & DEMANDA (VENDAS, RUPTURAS E RANKING) -->
    <div class="tab-pane" id="tab-reports">
      <div class="section-card" style="margin-bottom: 1.5rem;">
        <div class="section-toolbar" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
          <div class="section-title-group">
            <h2 class="section-title" style="display: flex; align-items: center; gap: 8px;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: #6366F1;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              Relatórios de Demanda & Vendas (WhatsApp)
            </h2>
            <span style="font-size: 0.82rem; color: var(--text-muted);">Filtre por período e analise saídas, rupturas de estoque e comportamento das assistências técnicas</span>
          </div>
          <div class="toolbar-actions">
            <button class="btn btn-secondary btn-sm" onclick="exportReportsCsv()" style="display: inline-flex; align-items: center; gap: 6px;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Exportar Relatório CSV
            </button>
          </div>
        </div>

        <!-- BARRA DE FILTROS INTERATIVOS -->
        <div class="toolbar-filter-panel">
          <!-- Filtro de Período -->
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <span style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Período:</span>
            <div class="filter-pill-group">
              <button class="filter-btn" data-period="today" onclick="setAnalyticsPeriod('today', this)">Hoje</button>
              <button class="filter-btn" data-period="7d" onclick="setAnalyticsPeriod('7d', this)">7 Dias</button>
              <button class="filter-btn" data-period="30d" onclick="setAnalyticsPeriod('30d', this)">30 Dias</button>
              <button class="filter-btn active" data-period="all" onclick="setAnalyticsPeriod('all', this)">Histórico Completo</button>
            </div>
          </div>

          <!-- Filtro de Categoria -->
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <span style="font-size: 0.75rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">Peça:</span>
            <div class="filter-pill-group">
              <button class="filter-btn active" data-cat="all" onclick="setAnalyticsCategory('all', this)">Todas</button>
              <button class="filter-btn" data-cat="tela" onclick="setAnalyticsCategory('tela', this)">Telas</button>
              <button class="filter-btn" data-cat="touch" onclick="setAnalyticsCategory('touch', this)">Touch</button>
              <button class="filter-btn" data-cat="bateria" onclick="setAnalyticsCategory('bateria', this)">Baterias</button>
            </div>
          </div>

          <!-- Busca por Modelo -->
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-grow: 1; min-width: 200px; max-width: 320px;">
            <input type="text" id="analytics-search-input" placeholder="Filtrar por modelo (ex: M8, T295, A15)..." oninput="debounceAnalyticsSearch()" style="width: 100%; padding: 0.45rem 0.75rem; font-size: 0.82rem; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.14); border-radius: 8px; color: #fff;">
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
      <div class="section-card banner-sheets-gradient" style="margin-bottom: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; padding: 0.25rem;">
          <div style="display: flex; align-items: center; gap: 0.85rem;">
            <div style="width: 44px; height: 44px; border-radius: 12px; background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.35); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>
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
            <button class="btn btn-secondary btn-sm" onclick="syncGoogleSheets()" id="btn-sync-sheets" style="display: inline-flex; align-items: center; gap: 6px;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="sync-icon"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
              Sincronizar Agora
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
        <div class="kpi-card clickable-card" onclick="setBrandFilter('all')" title="Ver todas as peças ativas">
          <div class="kpi-header">
            <span class="kpi-title">Total de Peças Ativas</span>
            <div class="kpi-icon" style="background: rgba(99, 102, 241, 0.12); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-catalog-total" style="color: #818CF8;">0</div>
          <div class="kpi-sub">Sincronizadas com Google Sheets ↗</div>
        </div>

        <div class="kpi-card clickable-card" onclick="filterCatalogStock('in')" title="Filtrar peças com saldo em estoque">
          <div class="kpi-header">
            <span class="kpi-title">Disponíveis em Balcão</span>
            <div class="kpi-icon" style="background: rgba(16, 185, 129, 0.12); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-catalog-healthy" style="color: #34D399;">0</div>
          <div class="kpi-sub">Pronta entrega imediata ↗</div>
        </div>

        <div class="kpi-card clickable-card" onclick="filterCatalogStock('out')" title="Filtrar peças esgotadas">
          <div class="kpi-header">
            <span class="kpi-title">Esgotadas em Loja</span>
            <div class="kpi-icon" style="background: rgba(239, 68, 68, 0.12); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-catalog-out" style="color: #F87171;">0</div>
          <div class="kpi-sub">Peças com saldo zero ↗</div>
        </div>

        <div class="kpi-card clickable-card" onclick="navigateWithFilter('audit', { action: 'OVERBOOKING' })" title="Ver logs de proteção contra overbooking">
          <div class="kpi-header">
            <span class="kpi-title">Overbooking Bloqueado</span>
            <div class="kpi-icon" style="background: rgba(245, 158, 11, 0.12); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.25);">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
          </div>
          <div class="kpi-val" id="kpi-overbooking-blocked" style="color: #FBBF24;">0</div>
          <div class="kpi-sub">Proteção transacional ativa ↗</div>
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
              <input type="text" id="catalog-search" placeholder="Buscar por nome, modelo (ex: P615, A15), SKU..." class="search-input" oninput="filterCatalogTable()" style="min-width: 260px;">
              <button class="btn btn-secondary btn-sm" onclick="fetchCatalog()"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -1px; margin-right: 4px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg> Atualizar</button>
            </div>
          </div>

          <!-- CHIPS DE FILTRO RÁPIDO (MARCAS & CATEGORIAS) -->
          <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; padding-top: 0.5rem; border-top: 1px solid var(--border-subtle);">
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

        <!-- PAGINAÇÃO DO CATÁLOGO DE PEÇAS (10 ITENS POR PÁGINA) -->
        <div class="pagination-bar" id="catalog-pagination-bar">
          <div style="font-size: 0.8rem; color: var(--text-muted);" id="catalog-pagination-info">
            Mostrando 1 a 10 de 0 peças
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <button class="pagination-btn" id="btn-catalog-prev" onclick="changeCatalogPage(-1)" disabled>
              ← Anterior
            </button>
            <span style="font-size: 0.8rem; font-weight: 600; color: var(--text-main); padding: 0 0.5rem;" id="catalog-page-number">1 / 1</span>
            <button class="pagination-btn" id="btn-catalog-next" onclick="changeCatalogPage(1)" disabled>
              Próxima →
            </button>
          </div>
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
            <span class="chips-label">Consultas Rápidas do Gestor:</span>
            <div class="chips-scroller">
              <button class="quick-chip-btn" onclick="sendQuickPrompt('Faça um resumo executivo direto e conciso de hoje: faturamento, pedidos, estoque e a principal ação.')">📊 Resumo do Dia</button>
              <button class="quick-chip-btn" onclick="sendQuickPrompt('Quais peças precisam de reposição urgente? Responda de forma direta e concisa.')">📦 Estoque & Reposição</button>
              <button class="quick-chip-btn" onclick="sendQuickPrompt('Como foi o volume e faturamento de vendas hoje? Seja direto.')">💰 Faturamento & Ticket</button>
              <button class="quick-chip-btn" onclick="sendQuickPrompt('Qual a situação das entregas via Uber Flash hoje? Seja direto.')">🚗 Entregas Uber Flash</button>
              <button class="quick-chip-btn" onclick="sendQuickPrompt('Qual o status rápido dos atendimentos no WhatsApp agora? Quantos estão com humanos?')">💬 Atendimentos Balcão</button>
              <button class="quick-chip-btn" onclick="sendQuickPrompt('Qual a principal ação prática para aumentar as vendas amanhã? Seja direto e objetivo.')">🎯 Ação p/ Vender Mais</button>
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
                <span>Fallback:</span> <strong style="color: #A5B4FC;" id="ai-fallback-convo">Fast FAQ In-Memory Cache (0ms)</strong>
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
                <div style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted); font-size: 0.875rem;" id="chat-empty-hint">
                  <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">💬</div>
                  Digite uma mensagem abaixo para simular o atendimento do balcão em tempo real.
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
        <div class="audit-toolbar" style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center; padding: 0.75rem 1rem; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); margin-top: 0.5rem;">
          <div class="level-pills">
            <button class="pill-btn active" data-level="" onclick="filterAuditLevel('', this)">Todos</button>
            <button class="pill-btn pill-info" data-level="INFO" onclick="filterAuditLevel('INFO', this)">Informativo</button>
            <button class="pill-btn pill-warn" data-level="WARN" onclick="filterAuditLevel('WARN', this)">Avisos</button>
            <button class="pill-btn pill-error" data-level="ERROR" onclick="filterAuditLevel('ERROR', this)">Erros</button>
          </div>

          <div style="flex: 1; min-width: 180px;">
            <input type="text" id="search-audit" class="search-input" placeholder="Buscar por ação, ator ou detalhe..." oninput="debounceAuditSearch()" style="width: 100%; padding: 0.45rem 0.8rem; font-size: 0.8rem; border-radius: 6px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div>
            <select id="select-audit-component" onchange="fetchAuditLogs()" class="select-styled">
              <option value="">Todos os Componentes</option>
              <option value="AI_ENGINE">Motor de IA (Gemini)</option>
              <option value="ROUTER">Roteador WhatsApp</option>
              <option value="NOTIFIER">Notificador & Alertas</option>
              <option value="REPO">Banco de Dados</option>
              <option value="ADMIN">Painel Administrativo</option>
              <option value="ERP_SYNC">Sincronização ERP</option>
            </select>
          </div>
        </div>

        <!-- TABELA DE LOGS (DESKTOP) -->
        <div class="table-container" style="margin-top: 1rem;">
          <table class="audit-table">
            <thead>
              <tr>
                <th style="width: 140px;">Timestamp</th>
                <th style="width: 90px;">Nível</th>
                <th style="width: 130px;">Componente</th>
                <th style="width: 190px;">Ação</th>
                <th style="width: 130px;">Ator</th>
                <th style="width: 80px;">Latência</th>
                <th>Detalhes & Payload</th>
              </tr>
            </thead>
            <tbody id="audit-table-body">
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 70%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td><td><div class="skeleton-table-cell" style="width: 80%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td><td><div class="skeleton-table-cell" style="width: 45%;"></div></td><td><div class="skeleton-table-cell" style="width: 85%;"></div></td></tr>
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 65%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 60%;"></div></td><td><div class="skeleton-table-cell" style="width: 75%;"></div></td><td><div class="skeleton-table-cell" style="width: 55%;"></div></td><td><div class="skeleton-table-cell" style="width: 40%;"></div></td><td><div class="skeleton-table-cell" style="width: 90%;"></div></td></tr>
              <tr class="skeleton-table-row"><td><div class="skeleton-table-cell" style="width: 75%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 70%;"></div></td><td><div class="skeleton-table-cell" style="width: 65%;"></div></td><td><div class="skeleton-table-cell" style="width: 50%;"></div></td><td><div class="skeleton-table-cell" style="width: 45%;"></div></td><td><div class="skeleton-table-cell" style="width: 75%;"></div></td></tr>
            </tbody>
          </table>
        </div>

        <!-- PAGINAÇÃO DE AUDITORIA (MÁXIMO 10 POR PÁGINA) -->
        <div class="pagination-bar" id="audit-pagination-bar">
          <div style="font-size: 0.8rem; color: var(--text-muted);" id="audit-pagination-info">
            Mostrando 1 a 10 de 0 registros
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: center;">
            <button class="pagination-btn" id="btn-audit-prev" onclick="changeAuditPage(-1)" disabled>
              ← Anterior
            </button>
            <span style="font-size: 0.8rem; font-weight: 600; color: #fff; padding: 0 0.5rem;" id="audit-page-number">1 / 1</span>
            <button class="pagination-btn" id="btn-audit-next" onclick="changeAuditPage(1)" disabled>
              Próxima →
            </button>
          </div>
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
      </div>

      <!-- PERSONALIZAÇÃO VISUAL & WHITE-LABEL (MULTI-TENANCY) -->
      <div class="card" style="margin-bottom: 1.25rem;">
        <div class="card-header">
          <div>
            <div class="card-title" style="display: flex; align-items: center; gap: 0.5rem;">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--tenant-brand);"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a14.5 14.5 0 0 0 0 20 10 10 0 0 0 0-20"></path><path d="M2 12h20"></path></svg>
              <span>Personalização Visual & White-Label (Multi-Tenant)</span>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem;">
              Configure a marca, logo e paleta de cores para customizar a plataforma para novos clientes sem alterar código.
            </p>
          </div>
        </div>

        <form id="tenant-form" onsubmit="saveTenantBranding(event)" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.25rem; margin-top: 1rem;">
          <div class="form-group">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Nome da Marca / Cliente</label>
            <input type="text" id="tenant-brand-name" required class="input-styled" placeholder="Ex: Victor Cell" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Slogan / Subtítulo</label>
            <input type="text" id="tenant-brand-slogan" required class="input-styled" placeholder="Ex: ERP & Balcão Inteligente" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Badge de Versão</label>
            <input type="text" id="tenant-brand-badge" required class="input-styled" placeholder="Ex: PRO ou ENTERPRISE" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">Ícone / Emoji do Logo</label>
            <input type="text" id="tenant-logo-icon" class="input-styled" placeholder="Ex: ⚡ ou 📱 ou 🔧" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <div class="form-group" style="grid-column: 1 / -1;">
            <label style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 0.4rem;">URL do Logo PNG/SVG (Opcional - substitui o ícone)</label>
            <input type="text" id="tenant-logo-url" class="input-styled" placeholder="Ex: /static/brands/minha-loja.png" style="width: 100%; padding: 0.6rem 0.8rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main);">
          </div>

          <!-- PALETA DE CORES CENTRALIZADA (SISTEMA DE 4 CORES + FILTROS) -->
          <div style="grid-column: 1 / -1; margin-top: 0.5rem; padding-top: 1rem; border-top: 1px solid var(--border-subtle);">
            <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.25rem; display: flex; align-items: center; gap: 6px;">
              <span>🎨 Paleta de Cores Centralizada (Constantes do Sistema em Hexadecimal)</span>
            </div>
            <p style="font-size: 0.775rem; color: var(--text-muted); margin-bottom: 1rem;">
              Defina as 4 cores base do sistema no formato hexadecimal (ex: #F71963). O gestor tem controle total da identidade visual.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem;">

              <!-- 1. Cor Primária / Marca Principal -->
              <div class="color-picker-card">
                <label style="font-size: 0.775rem; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 0.35rem;">
                  1. Cor Primária (Principal)
                </label>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <input type="color" id="tenant-primary-color" value="#F71963" oninput="syncColorPicker('tenant-primary-color', 'tenant-primary-color-text')" style="width: 44px; height: 38px; border: none; border-radius: 6px; cursor: pointer; background: transparent;">
                  <input type="text" id="tenant-primary-color-text" value="#F71963" maxlength="7" placeholder="#F71963" oninput="syncColorText('tenant-primary-color-text', 'tenant-primary-color')" class="input-styled" style="flex: 1; padding: 0.55rem 0.75rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;">
                </div>
                <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; display: block;">Botões de ação, tabs ativas e logo</span>
              </div>

              <!-- 2. Cor Secundária -->
              <div class="color-picker-card">
                <label style="font-size: 0.775rem; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 0.35rem;">
                  2. Cor Secundária (Info & Gráficos)
                </label>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <input type="color" id="tenant-secondary-color" value="#6366F1" oninput="syncColorPicker('tenant-secondary-color', 'tenant-secondary-color-text')" style="width: 44px; height: 38px; border: none; border-radius: 6px; cursor: pointer; background: transparent;">
                  <input type="text" id="tenant-secondary-color-text" value="#6366F1" maxlength="7" placeholder="#6366F1" oninput="syncColorText('tenant-secondary-color-text', 'tenant-secondary-color')" class="input-styled" style="flex: 1; padding: 0.55rem 0.75rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;">
                </div>
                <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; display: block;">Gráficos de mix, badges de info</span>
              </div>

              <!-- 3. Cor Terciária -->
              <div class="color-picker-card">
                <label style="font-size: 0.775rem; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 0.35rem;">
                  3. Cor Terciária (Sucesso & Estoque)
                </label>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <input type="color" id="tenant-tertiary-color" value="#10B981" oninput="syncColorPicker('tenant-tertiary-color', 'tenant-tertiary-color-text')" style="width: 44px; height: 38px; border: none; border-radius: 6px; cursor: pointer; background: transparent;">
                  <input type="text" id="tenant-tertiary-color-text" value="#10B981" maxlength="7" placeholder="#10B981" oninput="syncColorText('tenant-tertiary-color-text', 'tenant-tertiary-color')" class="input-styled" style="flex: 1; padding: 0.55rem 0.75rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;">
                </div>
                <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; display: block;">Itens em estoque, vendas fechadas</span>
              </div>

              <!-- 4. Cor Quaternária -->
              <div class="color-picker-card">
                <label style="font-size: 0.775rem; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 0.35rem;">
                  4. Cor Quaternária (Avisos & Logística)
                </label>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <input type="color" id="tenant-quaternary-color" value="#F59E0B" oninput="syncColorPicker('tenant-quaternary-color', 'tenant-quaternary-color-text')" style="width: 44px; height: 38px; border: none; border-radius: 6px; cursor: pointer; background: transparent;">
                  <input type="text" id="tenant-quaternary-color-text" value="#F59E0B" maxlength="7" placeholder="#F59E0B" oninput="syncColorText('tenant-quaternary-color-text', 'tenant-quaternary-color')" class="input-styled" style="flex: 1; padding: 0.55rem 0.75rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;">
                </div>
                <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; display: block;">Uber Flash, cotações e alertas</span>
              </div>

              <!-- 5. Cor dos Filtros -->
              <div class="color-picker-card">
                <label style="font-size: 0.775rem; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 0.35rem;">
                  5. Cor dos Filtros (Chips / Pills)
                </label>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <input type="color" id="tenant-filter-color" value="#334155" oninput="syncColorPicker('tenant-filter-color', 'tenant-filter-color-text')" style="width: 44px; height: 38px; border: none; border-radius: 6px; cursor: pointer; background: transparent;">
                  <input type="text" id="tenant-filter-color-text" value="#334155" maxlength="7" placeholder="#334155" oninput="syncColorText('tenant-filter-color-text', 'tenant-filter-color')" class="input-styled" style="flex: 1; padding: 0.55rem 0.75rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;">
                </div>
                <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; display: block;">Fundo de botões de filtro e chips</span>
              </div>

              <!-- Cor Hover -->
              <div class="color-picker-card">
                <label style="font-size: 0.775rem; font-weight: 700; color: var(--text-main); display: block; margin-bottom: 0.35rem;">
                  Cor Hover de Botões
                </label>
                <div style="display: flex; gap: 8px; align-items: center;">
                  <input type="color" id="tenant-primary-hover" value="#E00E54" oninput="syncColorPicker('tenant-primary-hover', 'tenant-primary-hover-text')" style="width: 44px; height: 38px; border: none; border-radius: 6px; cursor: pointer; background: transparent;">
                  <input type="text" id="tenant-primary-hover-text" value="#E00E54" maxlength="7" placeholder="#E00E54" oninput="syncColorText('tenant-primary-hover-text', 'tenant-primary-hover')" class="input-styled" style="flex: 1; padding: 0.55rem 0.75rem; border-radius: 8px; background: var(--bg-surface-elevated); border: 1px solid var(--border-subtle); color: var(--text-main); font-family: var(--font-mono); font-size: 0.85rem;">
                </div>
                <span style="font-size: 0.7rem; color: var(--text-dim); margin-top: 4px; display: block;">Estado interativo ao passar o mouse</span>
              </div>

            </div>
          </div>

          <!-- PRÉVIA INSTANTÂNEA DA MARCA -->
          <div style="grid-column: 1 / -1;" class="tenant-preview-box">
            <div style="font-size: 0.72rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.6rem; text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: 5px;">
              <span>👁️ Amostra & Pré-visualização da Paleta em Tempo Real</span>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
              <div id="tenant-preview-badge" style="background: var(--tenant-brand); color: #fff; padding: 6px 14px; border-radius: 8px; font-weight: 700; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px var(--tenant-brand-glow);">
                <span id="tenant-preview-icon" style="font-size: 1.1rem;">⚡</span>
                <span id="tenant-preview-name">Victor Cell</span>
                <span id="tenant-preview-tag" class="brand-badge-vtex">PRO</span>
              </div>
              <button type="button" id="tenant-preview-btn" style="background: var(--tenant-brand); color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 0.8rem; cursor: pointer;">
                1. Primária
              </button>
              <button type="button" id="tenant-preview-sec-btn" style="background: var(--primary); color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 0.8rem; cursor: pointer;">
                2. Secundária
              </button>
              <span id="tenant-preview-tert-badge" style="background: var(--emerald); color: #fff; padding: 6px 12px; border-radius: 8px; font-weight: 600; font-size: 0.8rem;">
                3. Terciária
              </span>
              <span id="tenant-preview-quat-badge" style="background: var(--amber); color: #000; padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size: 0.8rem;">
                4. Quaternária
              </span>
              <div style="font-size: 0.75rem; color: var(--text-dim);" id="tenant-preview-slogan">ERP & Balcão Inteligente</div>
            </div>
          </div>

          <div style="grid-column: 1 / -1; display: flex; justify-content: flex-end; gap: 0.75rem;">
            <button type="submit" class="btn" style="background: var(--tenant-brand); color: white; padding: 0.65rem 1.5rem; border-radius: 8px; font-weight: 600;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
              Salvar Personalização White-Label
            </button>
          </div>
        </form>
      </div>
    </div> <!-- /tab-profile -->

    </main> <!-- /main-body -->
    </div> <!-- /content-viewport -->
  </div> <!-- /app-layout -->

  <!-- CHAT DRAWER LATERAL (ATENDIMENTO WHATSAPP AO VIVO - NÍVEL BODY) -->
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
            <select id="np-category" required class="select-styled">
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
            <select id="np-quality" required class="select-styled">
              <option value="PRIMEIRA_LINHA">Primeira Linha (Incell/OLED)</option>
              <option value="ORIGINAL_NACIONAL">Original Nacional</option>
            </select>
          </div>
          <div class="vtex-form-group">
            <label>Possui Aro? *</label>
            <select id="np-has-frame" class="select-styled">
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
        <pre id="json-modal-content" class="json-code-box"></pre>
      </div>
      <div class="vtex-modal-footer">
        <button class="btn btn-secondary" onclick="closeJsonViewer()">Fechar</button>
      </div>
    </div>
  </div>

  <script src="/static/js/dashboard.js?v=20261102_06"></script>
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
