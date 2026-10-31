"""
Modern Web Dashboard & Analytics Hub for Victor Cell.
100% Free, Open-Source & Self-Hosted (No Microsoft Power BI License needed).
Provides:
- Business KPIs (Revenue, Orders, Uber Flash %, Avg Ticket)
- Top Best-Selling Replacement Parts Ranking
- Most Frequent Customer Questions & Intent Analytics
- Visual Charts (Distribution by Quality & Category)
- WhatsApp Live QR Code Pairing & Connection Monitor
- Live Customer Message Simulator for instant testing
"""

def render_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Victor Cell • Painel Gerencial & Inteligência de Balcão</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-base: #0B0F19;
      --bg-surface: #111827;
      --bg-card: rgba(17, 24, 39, 0.75);
      --border-color: rgba(255, 255, 255, 0.08);
      --primary: #6366F1;
      --primary-hover: #4F46E5;
      --success: #10B981;
      --warning: #F59E0B;
      --danger: #EF4444;
      --accent: #8B5CF6;
      --text-main: #F9FAFB;
      --text-muted: #9CA3AF;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background-image:
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.12) 0px, transparent 50%);
    }

    header {
      padding: 1.25rem 2rem;
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 50;
    }

    .brand { display: flex; align-items: center; gap: 0.75rem; }

    .brand-icon {
      width: 44px; height: 44px; border-radius: 12px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 1.3rem;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }

    .brand-text h1 { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.02em; }
    .brand-text p { font-size: 0.8rem; color: var(--text-muted); }

    .status-badges { display: flex; gap: 0.75rem; }

    .badge {
      display: inline-flex; align-items: center; gap: 0.4rem;
      padding: 0.35rem 0.8rem; border-radius: 9999px;
      font-size: 0.75rem; font-weight: 600;
      border: 1px solid var(--border-color);
      background: rgba(255, 255, 255, 0.04);
    }

    .badge-dot { width: 8px; height: 8px; border-radius: 50%; }
    .badge-success .badge-dot { background-color: var(--success); box-shadow: 0 0 8px var(--success); }
    .badge-warning .badge-dot { background-color: var(--warning); box-shadow: 0 0 8px var(--warning); }
    .badge-primary .badge-dot { background-color: var(--primary); box-shadow: 0 0 8px var(--primary); }

    main {
      flex: 1; padding: 2rem; max-width: 1440px; margin: 0 auto; width: 100%;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2rem;
    }

    .card {
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.5rem;
      position: relative;
      overflow: hidden;
      transition: transform 0.2s, border-color 0.2s;
    }

    .card:hover { transform: translateY(-2px); border-color: rgba(255, 255, 255, 0.15); }

    .kpi-title {
      font-size: 0.8rem; color: var(--text-muted);
      font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
      margin-bottom: 0.4rem;
    }

    .kpi-value { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; }
    .kpi-desc { font-size: 0.8rem; color: var(--text-muted); margin-top: 0.4rem; }

    .action-bar {
      display: flex; flex-wrap: wrap; gap: 1rem;
      margin-bottom: 2rem; background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 1.25rem; border-radius: 16px;
      align-items: center; justify-content: space-between;
    }

    .action-group { display: flex; flex-wrap: wrap; gap: 0.75rem; }

    .btn {
      display: inline-flex; align-items: center; gap: 0.5rem;
      padding: 0.65rem 1.25rem; border-radius: 10px;
      font-size: 0.875rem; font-weight: 600;
      cursor: pointer; text-decoration: none;
      transition: all 0.2s; border: none;
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--primary), var(--accent));
      color: white; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    .btn-primary:hover { opacity: 0.95; transform: translateY(-1px); }

    .btn-secondary {
      background: rgba(255, 255, 255, 0.06);
      color: var(--text-main); border: 1px solid var(--border-color);
    }
    .btn-secondary:hover { background: rgba(255, 255, 255, 0.1); }

    .insights-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .insight-card h3 {
      font-size: 1.05rem; font-weight: 700; margin-bottom: 1.25rem;
      display: flex; align-items: center; gap: 0.5rem;
    }

    .ranking-list { display: flex; flex-direction: column; gap: 0.85rem; }

    .ranking-item {
      display: flex; align-items: center; justify-content: space-between;
      padding: 0.85rem 1rem; background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px;
    }

    .ranking-info { display: flex; align-items: center; gap: 0.75rem; }
    .ranking-badge {
      width: 28px; height: 28px; border-radius: 8px;
      background: rgba(99, 102, 241, 0.2); color: #818CF8;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 0.85rem;
    }

    .ranking-badge.top-1 { background: rgba(245, 158, 11, 0.25); color: #FBBF24; }
    .ranking-badge.top-2 { background: rgba(156, 163, 175, 0.25); color: #E5E7EB; }
    .ranking-badge.top-3 { background: rgba(180, 83, 9, 0.25); color: #FCD34D; }

    .faq-item { margin-bottom: 1rem; }
    .faq-header { display: flex; justify-content: space-between; font-size: 0.875rem; margin-bottom: 0.35rem; }
    .progress-bar-bg {
      height: 8px; width: 100%; background: rgba(255, 255, 255, 0.06);
      border-radius: 9999px; overflow: hidden;
    }
    .progress-bar-fill {
      height: 100%; border-radius: 9999px;
      background: linear-gradient(90deg, var(--primary), var(--accent));
    }

    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .chart-card { height: 320px; display: flex; flex-direction: column; }
    .chart-card h3 { font-size: 1rem; font-weight: 700; margin-bottom: 1rem; }
    .chart-wrapper { flex: 1; position: relative; }

    /* Simulador de Mensagem em Tempo Real */
    .simulator-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }

    .sim-header { margin-bottom: 1rem; }
    .sim-header h3 { font-size: 1.05rem; font-weight: 700; }
    .sim-header p { font-size: 0.8rem; color: var(--text-muted); }

    .sim-input-box { display: flex; gap: 0.75rem; margin-bottom: 1rem; }
    .sim-input {
      flex: 1; padding: 0.75rem 1rem; border-radius: 10px;
      background: rgba(0, 0, 0, 0.3); border: 1px solid var(--border-color);
      color: white; font-size: 0.9rem;
    }
    .sim-input:focus { outline: none; border-color: var(--primary); }

    .sim-response-box {
      background: rgba(0, 0, 0, 0.4); border: 1px solid var(--border-color);
      border-radius: 12px; padding: 1rem; font-size: 0.9rem;
      line-height: 1.5; min-height: 50px; display: none;
    }

    .table-section h3 {
      font-size: 1.15rem; font-weight: 700; margin-bottom: 1rem;
      display: flex; justify-content: space-between; align-items: center;
    }

    .table-container {
      background: var(--bg-card); border: 1px solid var(--border-color);
      border-radius: 16px; overflow-x: auto;
    }

    table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.875rem; }
    th {
      background: rgba(255, 255, 255, 0.03); padding: 1rem 1.25rem;
      color: var(--text-muted); font-weight: 600; border-bottom: 1px solid var(--border-color);
    }
    td { padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }
    tr:last-child td { border-bottom: none; }

    .order-status {
      padding: 0.25rem 0.65rem; border-radius: 6px;
      font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    }

    .status-confirmed { background: rgba(16, 185, 129, 0.2); color: #34D399; }
    .status-pending { background: rgba(245, 158, 11, 0.2); color: #FBBF24; }
    .status-cancelled { background: rgba(239, 68, 68, 0.2); color: #F87171; }

    /* Modal WhatsApp QR Code */
    .modal-overlay {
      display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.8); backdrop-filter: blur(8px);
      z-index: 100; align-items: center; justify-content: center;
    }

    .modal-content {
      background: var(--bg-surface); border: 1px solid var(--border-color);
      border-radius: 20px; padding: 2rem; max-width: 440px; width: 90%;
      text-align: center;
    }

    #qr-container {
      margin: 1.5rem auto; padding: 1rem; background: white;
      border-radius: 12px; display: inline-block; min-width: 200px; min-height: 200px;
    }
    #qr-container img { max-width: 220px; display: block; margin: 0 auto; }

    footer {
      text-align: center; padding: 1.5rem; font-size: 0.8rem;
      color: var(--text-muted); border-top: 1px solid var(--border-color); margin-top: auto;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div class="brand-text">
        <h1>Victor Cell • Painel Gerencial & Inteligência</h1>
        <p>Atendimento Autônomo WhatsApp • Google Sheets Conectado</p>
      </div>
    </div>
    <div class="status-badges">
      <div class="badge badge-success" id="store-badge">
        <span class="badge-dot"></span>
        <span id="store-status">Loja Aberta</span>
      </div>
      <div class="badge badge-primary">
        <span class="badge-dot"></span>
        <span>Google Sheets Ativo</span>
      </div>
      <div class="badge badge-warning" id="wa-badge">
        <span class="badge-dot"></span>
        <span id="wa-status">WhatsApp Aguardando</span>
      </div>
    </div>
  </header>

  <main>
    <!-- KPIs Principais -->
    <div class="kpi-grid">
      <div class="card">
        <div class="kpi-title">Faturamento Acumulado</div>
        <div class="kpi-value" id="kpi-revenue" style="color: #34D399;">R$ 0,00</div>
        <div class="kpi-desc">Total de vendas geradas pelo bot</div>
      </div>
      <div class="card">
        <div class="kpi-title">Ticket Médio</div>
        <div class="kpi-value" id="kpi-avg-ticket">R$ 0,00</div>
        <div class="kpi-desc">Valor médio por saída/pedido</div>
      </div>
      <div class="card">
        <div class="kpi-title">Total de Pedidos</div>
        <div class="kpi-value" id="kpi-orders">0</div>
        <div class="kpi-desc">Reservas de peças confirmadas</div>
      </div>
      <div class="card">
        <div class="kpi-title">Despachos Uber Flash</div>
        <div class="kpi-value" id="kpi-uber" style="color: #818CF8;">0</div>
        <div class="kpi-desc" id="kpi-uber-pct">0% das entregas via Uber</div>
      </div>
      <div class="card">
        <div class="kpi-title">Catálogo Conectado</div>
        <div class="kpi-value" id="kpi-products">0</div>
        <div class="kpi-desc">Peças lidas do Google Sheets</div>
      </div>
    </div>

    <!-- Barra de Ações & Conexões -->
    <div class="action-bar">
      <div>
        <h4 style="font-size: 1rem; margin-bottom: 0.25rem;">Central de Operação & WhatsApp</h4>
        <p style="font-size: 0.8rem; color: var(--text-muted);">
          Conecte o WhatsApp pelo QR Code e sincronize alterações de preços do Google Sheets na hora.
        </p>
      </div>
      <div class="action-group">
        <button class="btn btn-primary" onclick="openWhatsAppModal()">
          📱 Conectar WhatsApp (QR Code)
        </button>
        <button class="btn btn-secondary" onclick="syncSheets()">
          🔄 Sincronizar Google Sheets
        </button>
        <a href="/api/reports/orders.csv" class="btn btn-secondary" download="Logs_Expedicao_PowerBI.csv">
          📥 Baixar CSV dos Pedidos
        </a>
      </div>
    </div>

    <!-- Inteligência de Vendas: Top Peças & Dúvidas mais Frequentes -->
    <div class="insights-grid">
      <!-- Ranking das Peças Mais Vendidas -->
      <div class="card insight-card">
        <h3>🏆 Ranking das Peças Mais Vendidas / Procuradas</h3>
        <div class="ranking-list" id="ranking-container">
          <div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">
            Carregando ranking de peças...
          </div>
        </div>
      </div>

      <!-- Dúvidas & Perguntas Mais Frequentes dos Clientes -->
      <div class="card insight-card">
        <h3>💬 Dúvidas & Intenções Mais Frequentes</h3>
        <div id="faq-container">
          <div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">
            Carregando intenções dos clientes...
          </div>
        </div>
      </div>
    </div>

    <!-- Gráficos Visuais -->
    <div class="charts-grid">
      <div class="card chart-card">
        <h3>Vendas por Qualidade (Original vs. Paralela)</h3>
        <div class="chart-wrapper">
          <canvas id="qualityChart"></canvas>
        </div>
      </div>
      <div class="card chart-card">
        <h3>Vendas por Categoria de Peça</h3>
        <div class="chart-wrapper">
          <canvas id="categoryChart"></canvas>
        </div>
      </div>
    </div>

    <!-- Simulador de Conversa em Tempo Real -->
    <div class="simulator-card">
      <div class="sim-header">
        <h3>🧪 Simulador de Conversa em Tempo Real (Teste Rápido)</h3>
        <p>Digite qualquer pergunta como se fosse um cliente no WhatsApp para ver a resposta imediata da IA:</p>
      </div>
      <div class="sim-input-box">
        <input type="text" id="sim-query" class="sim-input" placeholder="Ex: Bom dia, tem tela do A15 original? Ou qual a diferença pra paralela?" onkeydown="if(event.key==='Enter') testSimulate()" />
        <button class="btn btn-primary" onclick="testSimulate()">Enviar Teste</button>
      </div>
      <div class="sim-response-box" id="sim-response"></div>
    </div>

    <!-- Tabela de Pedidos Recentes -->
    <div class="table-section">
      <h3>
        <span>Histórico de Pedidos & Expedições</span>
        <span style="font-size: 0.85rem; font-weight: 500; color: var(--text-muted);" id="table-count">0 pedidos</span>
      </h3>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID Pedido</th>
              <th>Horário (Fortaleza)</th>
              <th>Cliente</th>
              <th>Peça / SKU</th>
              <th>Qtd</th>
              <th>Valor (R$)</th>
              <th>Destino Uber Flash</th>
              <th>Status</th>
              <th>Validade Reserva</th>
            </tr>
          </thead>
          <tbody id="orders-tbody">
            <tr>
              <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                Nenhum pedido registrado ainda.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </main>

  <!-- Modal WhatsApp QR Code -->
  <div class="modal-overlay" id="wa-modal">
    <div class="modal-content">
      <h3 style="font-size: 1.25rem; margin-bottom: 0.5rem;">Escanear QR Code do WhatsApp</h3>
      <p style="font-size: 0.85rem; color: var(--text-muted);">
        Abra o WhatsApp no celular da Victor Cell ➔ Aparelhos Conectados ➔ Conectar um aparelho.
      </p>
      <div id="qr-container">
        <div style="color: #6B7280; font-size: 0.9rem; padding: 2rem;" id="qr-placeholder">
          Consultando Evolution API...
        </div>
      </div>
      <div>
        <button class="btn btn-secondary" onclick="closeWhatsAppModal()" style="width: 100%;">
          Fechar
        </button>
      </div>
    </div>
  </div>

  <footer>
    Victor Cell Automação • Painel 100% Gratuito & Auto-Hospedado no Docker • Fuso Horário: America/Fortaleza
  </footer>

  <script>
    let qualityChart, categoryChart;

    async function loadData() {
      try {
        const res = await fetch('/api/reports/stats');
        if (!res.ok) return;
        const data = await res.json();

        // 1. Atualizar KPIs
        document.getElementById('kpi-revenue').textContent = `R$ ${data.total_revenue.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById('kpi-avg-ticket').textContent = `R$ ${data.avg_ticket.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById('kpi-orders').textContent = data.total_orders;
        document.getElementById('kpi-uber').textContent = data.uber_orders;
        document.getElementById('kpi-uber-pct').textContent = `${data.uber_percentage.toFixed(0)}% das entregas via Uber`;
        document.getElementById('kpi-products').textContent = data.total_products;
        document.getElementById('store-status').textContent = data.is_store_open ? 'Loja Aberta' : 'Loja Fechada';

        // 2. Ranking de Peças
        renderRanking(data.top_products);

        // 3. Intenções e Perguntas Frequentes
        renderFaqIntents(data.frequent_intents);

        // 4. Gráficos
        renderCharts(data.quality_breakdown, data.category_breakdown);

        // 5. Tabela
        renderTable(data.recent_orders);
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
      }
    }

    function renderRanking(topProducts) {
      const container = document.getElementById('ranking-container');
      if (!topProducts || topProducts.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">Nenhum produto vendido ainda.</div>';
        return;
      }

      container.innerHTML = topProducts.map((p, idx) => {
        const badgeClass = idx === 0 ? 'top-1' : (idx === 1 ? 'top-2' : (idx === 2 ? 'top-3' : ''));
        return `
          <div class="ranking-item">
            <div class="ranking-info">
              <span class="ranking-badge ${badgeClass}">#${idx + 1}</span>
              <div>
                <strong style="font-size: 0.9rem;">${p.name}</strong><br>
                <small style="color: var(--text-muted);">SKU: ${p.sku} • ${p.quality}</small>
              </div>
            </div>
            <div style="text-align: right;">
              <strong style="color: #34D399;">${p.quantity} un</strong><br>
              <small style="color: var(--text-muted);">R$ ${p.revenue.toFixed(2)}</small>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderFaqIntents(intents) {
      const container = document.getElementById('faq-container');
      if (!intents || intents.length === 0) {
        container.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">Aguardando primeiras perguntas.</div>';
        return;
      }

      container.innerHTML = intents.map(i => `
        <div class="faq-item">
          <div class="faq-header">
            <span><strong>${i.title}</strong></span>
            <span style="color: #818CF8; font-weight: 700;">${i.percentage}% (${i.count})</span>
          </div>
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${i.percentage}%;"></div>
          </div>
          <small style="color: var(--text-muted); font-size: 0.75rem; margin-top: 2px; display: block;">${i.example}</small>
        </div>
      `).join('');
    }

    function renderTable(orders) {
      const tbody = document.getElementById('orders-tbody');
      const countSpan = document.getElementById('table-count');
      countSpan.textContent = `${orders.length} pedidos registrados`;

      if (!orders || orders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2rem;">Nenhum pedido registrado ainda.</td></tr>`;
        return;
      }

      tbody.innerHTML = orders.map(o => {
        const statusClass = o.status === 'CONFIRMED' ? 'status-confirmed' : (o.status === 'CANCELLED' ? 'status-cancelled' : 'status-pending');
        return `
          <tr>
            <td style="font-weight: 700;">#${o.id}</td>
            <td>${o.created_at}</td>
            <td><strong>${o.customer_name}</strong><br><small style="color: var(--text-muted);">${o.customer_phone}</small></td>
            <td><code>${o.product_sku}</code></td>
            <td>${o.quantity}x</td>
            <td style="font-weight: 700; color: #34D399;">R$ ${o.product_price.toFixed(2)}</td>
            <td><small>${o.destination_address || 'Retirada no Balcão'}</small></td>
            <td><span class="order-status ${statusClass}">${o.status}</span></td>
            <td><small>${o.expires_at || '-'}</small></td>
          </tr>
        `;
      }).join('');
    }

    function renderCharts(qualityData, categoryData) {
      const ctxQ = document.getElementById('qualityChart').getContext('2d');
      const ctxC = document.getElementById('categoryChart').getContext('2d');

      const qLabels = Object.keys(qualityData);
      const qValues = Object.values(qualityData);

      if (qualityChart) qualityChart.destroy();
      qualityChart = new Chart(ctxQ, {
        type: 'doughnut',
        data: {
          labels: qLabels.length ? qLabels : ['Sem dados'],
          datasets: [{
            data: qValues.length ? qValues : [1],
            backgroundColor: ['#6366F1', '#10B981', '#F59E0B', '#8B5CF6'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom', labels: { color: '#9CA3AF' } } }
        }
      });

      const cLabels = Object.keys(categoryData);
      const cValues = Object.values(categoryData);

      if (categoryChart) categoryChart.destroy();
      categoryChart = new Chart(ctxC, {
        type: 'bar',
        data: {
          labels: cLabels.length ? cLabels : ['Sem dados'],
          datasets: [{
            label: 'Unidades Vendidas',
            data: cValues.length ? cValues : [0],
            backgroundColor: '#8B5CF6',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { ticks: { color: '#9CA3AF', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' } },
            x: { ticks: { color: '#9CA3AF' }, grid: { display: false } }
          },
          plugins: { legend: { display: false } }
        }
      });
    }

    async function syncSheets() {
      try {
        const res = await fetch('/api/reports/sync-sheets', { method: 'POST' });
        const data = await res.json();
        alert(`Sincronização com Google Sheets concluída com sucesso!\n${data.total_items} produtos ativos.`);
        loadData();
      } catch (err) {
        alert('Erro ao sincronizar com Google Sheets: ' + err);
      }
    }

    async function testSimulate() {
      const input = document.getElementById('sim-query');
      const text = input.value.trim();
      if (!text) return;

      const resBox = document.getElementById('sim-response');
      resBox.style.display = 'block';
      resBox.innerHTML = '<span style="color: var(--text-muted);">Robô pensando e consultando catálogo...</span>';

      try {
        const res = await fetch('/api/simulator/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        resBox.innerHTML = `<strong>Victor Cell:</strong><br>${data.reply.replace(/\\n/g, '<br>')}`;
        loadData();
      } catch (err) {
        resBox.innerHTML = '<span style="color: #EF4444;">Erro ao processar mensagem no simulador.</span>';
      }
    }

    function openWhatsAppModal() {
      document.getElementById('wa-modal').style.display = 'flex';
      fetchWhatsAppQR();
    }

    function closeWhatsAppModal() {
      document.getElementById('wa-modal').style.display = 'none';
    }

    async function fetchWhatsAppQR() {
      const container = document.getElementById('qr-container');
      container.innerHTML = '<div style="color: #6B7280; font-size: 0.9rem; padding: 2rem;">Consultando Evolution API...</div>';
      try {
        const res = await fetch('/api/whatsapp/qrcode');
        const data = await res.json();
        if (data.qrcode) {
          container.innerHTML = `<img src="${data.qrcode}" alt="WhatsApp QR Code" />`;
        } else if (data.status === 'connected') {
          container.innerHTML = '<div style="color: #10B981; font-weight: 700; padding: 2rem;">✅ WhatsApp Conectado com Sucesso!</div>';
        } else {
          container.innerHTML = `<div style="color: #EF4444; padding: 1rem;">${data.message || 'Instância ainda não iniciada.'}</div>`;
        }
      } catch (e) {
        container.innerHTML = `<div style="color: #EF4444; padding: 1rem;">Erro de conexão com Evolution API. Verifique se o container está rodando.</div>`;
      }
    }

    // Carregar inicialmente e atualizar a cada 10s
    loadData();
    setInterval(loadData, 10000);
  </script>
</body>
</html>"""
