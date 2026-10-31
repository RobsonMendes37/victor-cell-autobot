"""
Modern Web Dashboard & Power BI Analytics Hub for Victor Cell.
Provides real-time business KPIs, Chart.js visualizations, order tracking,
Google Sheets sync status, and WhatsApp Evolution API connection QR code pairing.
"""

def render_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Victor Cell - Painel Power BI & Expedição</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg-base: #0B0F19;
      --bg-surface: #111827;
      --bg-card: rgba(17, 24, 39, 0.7);
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

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }

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

    .brand {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .brand-icon {
      width: 42px;
      height: 42px;
      border-radius: 12px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.2rem;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }

    .brand-text h1 {
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .brand-text p {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .status-badges {
      display: flex;
      gap: 0.75rem;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      padding: 0.35rem 0.8rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      border: 1px solid var(--border-color);
      background: rgba(255, 255, 255, 0.04);
    }

    .badge-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .badge-success .badge-dot { background-color: var(--success); box-shadow: 0 0 8px var(--success); }
    .badge-warning .badge-dot { background-color: var(--warning); box-shadow: 0 0 8px var(--warning); }
    .badge-primary .badge-dot { background-color: var(--primary); box-shadow: 0 0 8px var(--primary); }

    main {
      flex: 1;
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
    }

    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
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

    .card:hover {
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.15);
    }

    .kpi-title {
      font-size: 0.85rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
    }

    .kpi-value {
      font-size: 2.25rem;
      font-weight: 800;
      letter-spacing: -0.03em;
    }

    .kpi-desc {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.4rem;
    }

    .action-bar {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-bottom: 2rem;
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 1.25rem;
      border-radius: 16px;
      align-items: center;
      justify-content: space-between;
    }

    .action-group {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.65rem 1.25rem;
      border-radius: 10px;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      text-decoration: none;
      transition: all 0.2s;
      border: none;
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--primary), var(--accent));
      color: white;
      box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    .btn-primary:hover {
      opacity: 0.95;
      transform: translateY(-1px);
    }

    .btn-secondary {
      background: rgba(255, 255, 255, 0.06);
      color: var(--text-main);
      border: 1px solid var(--border-color);
    }

    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    .charts-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .chart-card {
      height: 340px;
      display: flex;
      flex-direction: column;
    }

    .chart-card h3 {
      font-size: 1rem;
      font-weight: 700;
      margin-bottom: 1rem;
    }

    .chart-wrapper {
      flex: 1;
      position: relative;
    }

    .table-section {
      margin-top: 1rem;
    }

    .table-section h3 {
      font-size: 1.15rem;
      font-weight: 700;
      margin-bottom: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .table-container {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.875rem;
    }

    th {
      background: rgba(255, 255, 255, 0.03);
      padding: 1rem 1.25rem;
      color: var(--text-muted);
      font-weight: 600;
      border-bottom: 1px solid var(--border-color);
    }

    td {
      padding: 1rem 1.25rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }

    tr:last-child td {
      border-bottom: none;
    }

    .order-status {
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
    }

    .status-confirmed { background: rgba(16, 185, 129, 0.2); color: #34D399; }
    .status-pending { background: rgba(245, 158, 11, 0.2); color: #FBBF24; }
    .status-cancelled { background: rgba(239, 68, 68, 0.2); color: #F87171; }

    /* Modal de Conexão WhatsApp */
    .modal-overlay {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.8);
      backdrop-filter: blur(8px);
      z-index: 100;
      align-items: center;
      justify-content: center;
    }

    .modal-content {
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 20px;
      padding: 2rem;
      max-width: 440px;
      width: 90%;
      text-align: center;
    }

    #qr-container {
      margin: 1.5rem auto;
      padding: 1rem;
      background: white;
      border-radius: 12px;
      display: inline-block;
      min-width: 200px;
      min-height: 200px;
    }

    #qr-container img {
      max-width: 220px;
      display: block;
    }

    footer {
      text-align: center;
      padding: 1.5rem;
      font-size: 0.8rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border-color);
      margin-top: auto;
    }
  </style>
</head>
<body>

  <header>
    <div class="brand">
      <div class="brand-icon">⚡</div>
      <div class="brand-text">
        <h1>Victor Cell • Power BI & Despacho</h1>
        <p>Painel Gerencial de Atendimento Autônomo WhatsApp</p>
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
    <!-- KPIs -->
    <div class="kpi-grid">
      <div class="card">
        <div class="kpi-title">Faturamento Estimado</div>
        <div class="kpi-value" id="kpi-revenue">R$ 0,00</div>
        <div class="kpi-desc">Total acumulado de pedidos</div>
      </div>
      <div class="card">
        <div class="kpi-title">Total de Pedidos</div>
        <div class="kpi-value" id="kpi-orders">0</div>
        <div class="kpi-desc">Reservas e despachos gerados</div>
      </div>
      <div class="card">
        <div class="kpi-title">Despachos Uber Flash</div>
        <div class="kpi-value" id="kpi-uber">0</div>
        <div class="kpi-desc">Entregas solicitadas ao caixa</div>
      </div>
      <div class="card">
        <div class="kpi-title">Itens em Catálogo</div>
        <div class="kpi-value" id="kpi-products">0</div>
        <div class="kpi-desc">Produtos sincronizados no Sheets</div>
      </div>
    </div>

    <!-- Barra de Ações Power BI & WhatsApp -->
    <div class="action-bar">
      <div>
        <h4 style="font-size: 1rem; margin-bottom: 0.25rem;">Integrações & Conexões</h4>
        <p style="font-size: 0.8rem; color: var(--text-muted);">Exporte os relatórios ou integre diretamente com o Power BI Desktop</p>
      </div>
      <div class="action-group">
        <button class="btn btn-primary" onclick="openWhatsAppModal()">
          📱 Conectar WhatsApp (QR Code)
        </button>
        <a href="/api/reports/orders.csv" class="btn btn-secondary" download="Logs_Expedicao_PowerBI.csv">
          📥 Baixar CSV Power BI
        </a>
        <button class="btn btn-secondary" onclick="copyPowerBIUrl()">
          🔗 Copiar URL da API para Power BI
        </button>
        <button class="btn btn-secondary" onclick="syncSheets()">
          🔄 Sincronizar Google Sheets
        </button>
      </div>
    </div>

    <!-- Gráficos -->
    <div class="charts-grid">
      <div class="card chart-card">
        <h3>Vendas por Procedência / Qualidade</h3>
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
              <th>Endereço Uber Flash</th>
              <th>Status</th>
              <th>Validade</th>
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
          Carregando conexão da Evolution API...
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
    Victor Cell Automação • Desenvolvido com Google Gemini 3.5 & FastAPI • Fuso Horário: America/Fortaleza
  </footer>

  <script>
    let qualityChart, categoryChart;

    async function loadData() {
      try {
        const res = await fetch('/api/reports/stats');
        if (!res.ok) return;
        const data = await res.json();

        // Atualizar KPIs
        document.getElementById('kpi-revenue').textContent = `R$ ${data.total_revenue.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
        document.getElementById('kpi-orders').textContent = data.total_orders;
        document.getElementById('kpi-uber').textContent = data.uber_orders;
        document.getElementById('kpi-products').textContent = data.total_products;
        document.getElementById('store-status').textContent = data.is_store_open ? 'Loja Aberta' : 'Loja Fechada';

        // Atualizar Tabela
        renderTable(data.recent_orders);

        // Atualizar Gráficos
        renderCharts(data.quality_breakdown, data.category_breakdown);
      } catch (err) {
        console.error('Erro ao carregar dados:', err);
      }
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
          plugins: {
            legend: { position: 'bottom', labels: { color: '#9CA3AF' } }
          }
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
            label: 'Pedidos',
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

    function copyPowerBIUrl() {
      const url = `${window.location.origin}/api/reports/orders.csv`;
      navigator.clipboard.writeText(url).then(() => {
        alert('URL para Power BI copiada com sucesso!\n\nNo Power BI Desktop:\n1. Obter Dados -> Da Web\n2. Cole a URL: ' + url);
      });
    }

    async function syncSheets() {
      try {
        const res = await fetch('/api/reports/sync-sheets', { method: 'POST' });
        const data = await res.json();
        alert(`Sincronização com Google Sheets concluída!\n${data.total_items} produtos carregados.`);
        loadData();
      } catch (err) {
        alert('Erro ao sincronizar com Google Sheets: ' + err);
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
          container.innerHTML = `<div style="color: #EF4444; padding: 1rem;">${data.message || 'Instância ainda não iniciada. Certifique-se de que o container Evolution API está rodando.'}</div>`;
        }
      } catch (e) {
        container.innerHTML = `<div style="color: #EF4444; padding: 1rem;">Erro de conexão com Evolution API. Verifique a porta 8085.</div>`;
      }
    }

    // Carregar inicialmente e atualizar a cada 10 segundos
    loadData();
    setInterval(loadData, 10000);
  </script>
</body>
</html>"""
