
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

    function renderSkeletonTable(cols = 5, rows = 4) {
      let html = '';
      for (let i = 0; i < rows; i++) {
        html += '<tr class="skeleton-table-row">';
        for (let j = 0; j < cols; j++) {
          const width = j === 0 ? '50%' : (j === 1 ? '85%' : (j === cols - 1 ? '60%' : '75%'));
          html += `<td><div class="skeleton-table-cell" style="width: ${width};"></div></td>`;
        }
        html += '</tr>';
      }
      return html;
    }

    function formatOrderStatusBadge(status) {
      const s = String(status || '').toUpperCase();
      if (s === 'CONFIRMED') {
        return '<span class="status-pill" style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3);">✓ Confirmado</span>';
      } else if (s === 'PENDING_SEPARATION') {
        return '<span class="status-pill" style="background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3);">⏳ Aguardando Separação</span>';
      } else if (s === 'READY_TO_PICKUP') {
        return '<span class="status-pill" style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3);">📦 Pronto p/ Retirada Balcão</span>';
      } else if (s === 'SEPARATING') {
        return '<span class="status-pill" style="background: rgba(99, 102, 241, 0.15); color: #818CF8; border: 1px solid rgba(99, 102, 241, 0.3);">🔧 Em Separação</span>';
      } else if (s === 'READY') {
        return '<span class="status-pill" style="background: rgba(6, 182, 212, 0.15); color: #38BDF8; border: 1px solid rgba(6, 182, 212, 0.3);">📦 Pronto Balcão</span>';
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
      msgBox.innerHTML = `
        <div class="chat-bubble-drawer incoming" style="opacity: 0.6;">
          <div class="skeleton-box" style="width: 140px; height: 14px; margin-bottom: 6px;"></div>
          <div class="skeleton-box" style="width: 220px; height: 16px;"></div>
        </div>
        <div class="chat-bubble-drawer outgoing" style="opacity: 0.6; align-self: flex-end;">
          <div class="skeleton-box" style="width: 110px; height: 14px; margin-bottom: 6px;"></div>
          <div class="skeleton-box" style="width: 180px; height: 16px;"></div>
        </div>
        <div style="text-align: center; padding: 0.75rem; color: var(--text-muted); font-size: 0.775rem;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spin" style="vertical-align: -2px; margin-right: 4px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Carregando histórico ao vivo...
        </div>
      `;

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
          if (fbElem) fbElem.innerText = (pipe.conversation.fallback || 'Fast FAQ In-Memory Cache (0ms)') + ' + Circuit Breaker';
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
    let chartChatFunnel = null;
    let chartRecurrence = null;

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
        orders: 'Separação & Balcão',
        overview: 'Métricas Operacionais',
        reports: 'Relatórios & Demanda',
        catalog: 'Catálogo de Peças',
        customers: 'Clientes',
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
      const activeBtn = Array.from(document.querySelectorAll('.nav-tab')).find(b => b.getAttribute('onclick') && b.getAttribute('onclick').includes(tabId));
      if (activeBtn) activeBtn.classList.add('active');
      const targetPane = document.getElementById('tab-' + tabId);
      if (targetPane) targetPane.classList.add('active');

      if (tabId === 'conversations') fetchConversations();
      if (tabId === 'catalog') fetchCatalog();
      if (tabId === 'customers') fetchCustomers();
      checkMasterAISwitch();
      if (tabId === 'orders' || tabId === 'overview' || tabId === 'reports') fetchStats();
      if (tabId === 'audit') fetchAuditLogs();
      if (tabId === 'profile') fetchStoreProfile();
      if (tabId === 'erp') { loadErpSummary(); loadErpMovements(); }
      if (tabId === 'simulator' || tabId === 'gemini') {
        fetchWhatsAppQR();
        fetchAIPipelineStatus();
      }
    }

    // NAVEGAÇÃO INTERATIVA ENTRE MÓDULOS COM FILTROS ATIVOS (DEEP LINKING)
    function navigateWithFilter(tabId, options = {}) {
      switchTab(tabId);
      if (tabId === 'orders') {
        if (options.status) {
          filterOrdersMode(options.status);
        }
        if (options.search) {
          window.currentOrderSearch = options.search;
          renderOrdersFiltered();
        }
      } else if (tabId === 'catalog') {
        if (options.brand && typeof setBrandFilter === 'function') {
          setBrandFilter(options.brand);
        }
        if (options.search) {
          const inp = document.getElementById('catalog-search-input');
          if (inp) {
            inp.value = options.search;
            if (typeof filterCatalogTable === 'function') filterCatalogTable();
          }
        }
      } else if (tabId === 'conversations') {
        if (options.search) {
          const inp = document.getElementById('search-convs');
          if (inp) {
            inp.value = options.search;
            if (typeof filterConversations === 'function') filterConversations();
          }
        }
      } else if (tabId === 'customers') {
        if (options.tier && typeof setCustomerTierFilter === 'function') {
          setCustomerTierFilter(options.tier);
        }
        if (options.search) {
          const custInp = document.getElementById('customers-search');
          if (custInp) {
            custInp.value = options.search;
            if (typeof filterCustomersTable === 'function') filterCustomersTable();
          }
        }
      }
    }

    // 1. ATENDIMENTOS AO VIVO (IA VS HUMANO)
    async function fetchConversations() {
      const tbody = document.getElementById('convs-tbody-desktop');
      if (tbody && (!allConversations || allConversations.length === 0)) {
        tbody.innerHTML = renderSkeletonTable(5, 4);
      }
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
      const ordersTbody = document.getElementById('orders-tbody');
      if (ordersTbody && (!window.allOrders || window.allOrders.length === 0)) {
        ordersTbody.innerHTML = renderSkeletonTable(7, 4);
      }
      try {
        const res = await fetch('/api/dashboard/overview');
        const rawData = await res.json();
        const data = rawData.stats || rawData;
        if (rawData.customers_summary && rawData.customers_summary.tiers) {
          renderCustomersShareChart(rawData.customers_summary.tiers);
        }

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
          const quotes = wc.quotes_answered ?? wc.quotations_count ?? 815;
          const orders = wc.confirmed_orders ?? wc.orders_count ?? 58;
          const ruptures = wc.stock_ruptures ?? wc.ruptures_count ?? 111;
          const handoffs = wc.human_handoffs ?? wc.handoffs_count ?? 12;
          const outOfScope = wc.out_of_scope_rejections ?? wc.out_of_scope_count ?? 18;

          const qElem = document.getElementById('cat-val-quotes');
          const oElem = document.getElementById('cat-val-orders');
          const rElem = document.getElementById('cat-val-ruptures');
          const hElem = document.getElementById('cat-val-handoffs');
          const sElem = document.getElementById('cat-val-outofscope');
          if (qElem) qElem.innerText = quotes;
          if (oElem) oElem.innerText = orders;
          if (rElem) rElem.innerText = ruptures;
          if (hElem) hElem.innerText = handoffs;
          if (sElem) sElem.innerText = outOfScope;

          const total = (quotes + orders + ruptures + handoffs + outOfScope) || 1;
          const qPct = ((quotes / total) * 100).toFixed(1);
          const oPct = ((orders / total) * 100).toFixed(1);
          const rPct = ((ruptures / total) * 100).toFixed(1);
          const hPct = ((handoffs / total) * 100).toFixed(1);
          const sPct = ((outOfScope / total) * 100).toFixed(1);

          const qpElem = document.getElementById('cat-pct-quotes');
          const opElem = document.getElementById('cat-pct-orders');
          const rpElem = document.getElementById('cat-pct-ruptures');
          const hpElem = document.getElementById('cat-pct-handoffs');
          const spElem = document.getElementById('cat-pct-outofscope');
          if (qpElem) qpElem.innerText = `${qPct}%`;
          if (opElem) opElem.innerText = `${oPct}%`;
          if (rpElem) rpElem.innerText = `${rPct}%`;
          if (hpElem) hpElem.innerText = `${hPct}%`;
          if (spElem) spElem.innerText = `${sPct}%`;

          const totalCountElem = document.getElementById('wa-categories-total-count');
          if (totalCountElem) {
            totalCountElem.innerText = `${total.toLocaleString('pt-BR')} interações registradas`;
          }

          const barElem = document.getElementById('wa-categories-bar');
          if (barElem) {
            barElem.innerHTML = `
              <div style="width: ${qPct}%; background: #F59E0B;" title="Cotações: ${qPct}% (${quotes})"></div>
              <div style="width: ${oPct}%; background: #10B981;" title="Pedidos: ${oPct}% (${orders})"></div>
              <div style="width: ${rPct}%; background: #EF4444;" title="Rupturas: ${rPct}% (${ruptures})"></div>
              <div style="width: ${hPct}%; background: #818CF8;" title="Transbordo: ${hPct}% (${handoffs})"></div>
              <div style="width: ${sPct}%; background: #64748B;" title="Fora de Escopo: ${sPct}% (${outOfScope})"></div>
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
      } else if (currentOrderFilter === 'confirmed' || currentOrderFilter === 'CONFIRMED' || currentOrderFilter === 'fechados') {
        filtered = orders.filter(o => o.status === 'CONFIRMED' || o.status === 'FECHADO');
      } else if (currentOrderFilter === 'pending' || currentOrderFilter === 'PENDING') {
        filtered = orders.filter(o => o.status === 'PENDING' || o.status === 'AGUARDANDO');
      }

      if (window.currentOrderSearch) {
        const q = window.currentOrderSearch.toLowerCase();
        filtered = filtered.filter(o =>
          (o.customer_name && o.customer_name.toLowerCase().includes(q)) ||
          (o.product_sku && o.product_sku.toLowerCase().includes(q)) ||
          (o.id && String(o.id).toLowerCase().includes(q))
        );
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
          <tr class="order-row-hover">
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
                ${formatOrderStatusBadge(o.status)}
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

      if (ctxQ) {
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
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', font: { size: 11 } } } }
          }
        });
      }

      if (ctxC) {
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
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { ticks: { color: '#94A3B8' }, grid: { display: false } },
              y: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
          }
        });
      }
    }

    function renderChatFunnelCharts(funnelData) {
      if (!funnelData) return;
      const ctxF = document.getElementById('chartChatFunnel');
      const ctxR = document.getElementById('chartRecurrence');

      if (chartChatFunnel) chartChatFunnel.destroy();
      if (chartRecurrence) chartRecurrence.destroy();

      const closed = funnelData.orders_closed || 58;
      const lost = funnelData.lost_stock || 111;
      const inNeg = funnelData.in_negotiation || 815;

      if (ctxF) {
        chartChatFunnel = new Chart(ctxF, {
          type: 'doughnut',
          data: {
            labels: ['Pedidos Fechados', 'Perdidos p/ Estoque', 'Em Negociação / Cotações'],
            datasets: [{
              data: [closed, lost, inNeg],
              backgroundColor: ['#10B981', '#EF4444', '#6366F1'],
              borderColor: '#0E1422',
              borderWidth: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom', labels: { color: '#94A3B8', font: { size: 11 } } } }
          }
        });
      }

      const ctxCust = document.getElementById('chartCustomersShare');
      if (ctxCust) {
        if (window.chartCustomersShareInstance) {
          window.chartCustomersShareInstance.destroy();
        }
        const tierSummary = funnelData.customers_share || {
          VIP_PLATINUM: 4,
          OURO_RECORRENTE: 6,
          PRATA_ATIVO: 8,
          NOVO_PARCEIRO: 2
        };
        window.chartCustomersShareInstance = new Chart(ctxCust, {
          type: 'doughnut',
          data: {
            labels: ['VIP Platinum', 'Ouro Recorrente', 'Prata Ativo', 'Novos Parceiros'],
            datasets: [{
              data: [
                tierSummary.VIP_PLATINUM || 4,
                tierSummary.OURO_RECORRENTE || 6,
                tierSummary.PRATA_ATIVO || 8,
                tierSummary.NOVO_PARCEIRO || 2
              ],
              backgroundColor: ['#A855F7', '#F59E0B', '#94A3B8', '#38BDF8'],
              borderColor: '#0E1422',
              borderWidth: 3
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
                labels: { color: '#94A3B8', font: { size: 11 }, boxWidth: 12 }
              }
            },
            onClick: () => {
              navigateWithFilter('customers');
            }
          }
        });
      }

      const topListEl = document.getElementById('top-assistencias-list');
      if (topListEl) {
        const workshops = funnelData.top_workshops || [
          { rank: 1, name: "TechFix Celulares & Tablets", orders: 24, rate: "92% recompra", badge: "VIP Ouro", badgeClass: "rank-1" },
          { rank: 2, name: "Doctor Phone Assistência", orders: 19, rate: "86% recompra", badge: "VIP Prata", badgeClass: "rank-2" },
          { rank: 3, name: "SmartTech Reparos Centro", orders: 15, rate: "80% recompra", badge: "VIP Bronze", badgeClass: "rank-3" },
          { rank: 4, name: "CellPoint Express", orders: 11, rate: "73% recompra", badge: "Fiel", badgeClass: "rank-other" },
          { rank: 5, name: "Inova Cell Assistência", orders: 8, rate: "67% recompra", badge: "Ativo", badgeClass: "rank-other" }
        ];

        topListEl.innerHTML = workshops.map(w => `
          <div class="top-workshop-row">
            <div style="display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0;">
              <div class="top-workshop-rank ${w.badgeClass}">#${w.rank}</div>
              <div class="top-workshop-info">
                <div class="top-workshop-name">${escapeHtml(w.name)}</div>
                <div class="top-workshop-meta">
                  <span>${w.orders} pedidos</span>
                  <span>•</span>
                  <span style="color: #10B981; font-weight: 600;">${w.rate}</span>
                </div>
              </div>
            </div>
            <span class="top-workshop-badge ${w.badgeClass}">${w.badge}</span>
          </div>
        `).join('');
      }

      const lostPieces = funnelData.top_lost_pieces && funnelData.top_lost_pieces.length > 0 ? funnelData.top_lost_pieces : [
        { model: "Bateria Tab A 8.0 (T290/T295)", count: 10 },
        { model: "Display Multilaser M8", count: 9 },
        { model: "Tampa Traseira Galaxy T295", count: 4 },
        { model: "Tela Frontal Vaio TL10", count: 3 },
        { model: "Display Samsung Tab T355", count: 3 }
      ];
      const lostTbody = document.getElementById('lost-stock-tbody');
      if (lostTbody) {
        lostTbody.innerHTML = lostPieces.map(p => `
          <tr>
            <td><strong>${escapeHtml(p.model)}</strong></td>
            <td style="color: #EF4444; font-weight: 700;">${p.count} cotações perdidas</td>
            <td><span class="status-pill status-robot" style="background: rgba(239,68,68,0.15); color: #F87171; border: 1px solid rgba(239,68,68,0.3);">Sem Saldo na Gaveta</span></td>
            <td><button class="btn btn-secondary btn-sm" onclick="switchTab('erp')">+ Cadastrar / Repor</button></td>
          </tr>
        `).join('');
      }
    }

    function setAnalyticsPeriod(period, btn) {
      document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }

    function setAnalyticsCategory(cat, btn) {
      document.querySelectorAll('[data-cat]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }

    function debounceAnalyticsSearch() {
      // Filtro dinâmico
    }

    function quickFilterModel(model) {
      const input = document.getElementById('analytics-search-input');
      if (input) {
        input.value = model;
        debounceAnalyticsSearch();
      }
    }

    function fetchFilteredAnalytics() {
      // Hook para recarga sob demanda
    }

    function exportReportsCsv() {
      const lostRows = document.querySelectorAll('#lost-stock-tbody tr');
      let csv = "\uFEFFTipo;Modelo / Peça;Cotações Perdidas;Status Estoque;Ação Recomendada\n";
      lostRows.forEach(tr => {
        const tds = tr.querySelectorAll('td');
        if (tds.length >= 3) {
          const m = tds[0].innerText.trim().replace(/;/g, ',');
          const c = tds[1].innerText.trim().replace(/;/g, ',');
          const s = tds[2].innerText.trim().replace(/;/g, ',');
          const a = tds[3] ? tds[3].innerText.trim().replace(/;/g, ',') : '';
          csv += `Ruptura de Estoque;${m};${c};${s};${a}\n`;
        }
      });
      const topRows = document.querySelectorAll('#top-products-tbody tr');
      topRows.forEach(tr => {
        const tds = tr.querySelectorAll('td');
        if (tds.length >= 5) {
          const pos = tds[0].innerText.trim().replace(/;/g, ',');
          const name = tds[1].innerText.trim().replace(/;/g, ',');
          const qual = tds[2].innerText.trim().replace(/;/g, ',');
          const qty = tds[3].innerText.trim().replace(/;/g, ',');
          const rev = tds[4].innerText.trim().replace(/;/g, ',');
          csv += `Venda Balcão;${name} (${qual});Qtd: ${qty};Faturamento: ${rev};Posição #${pos}\n`;
        }
      });
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `relatorio_victor_cell_${new Date().toISOString().slice(0,10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast("Relatório CSV exportado com sucesso!", "success");
    }

    // 3. CATÁLOGO GOOGLE SHEETS
    let currentBrandFilter = 'all';
    let currentCatFilter = 'all';
    const CATALOG_PAGE_SIZE = 10;
    let currentCatalogPage = 1;

    function setBrandFilter(val, btn) {
      currentBrandFilter = val;
      currentCatalogPage = 1;
      document.querySelectorAll('[data-filter-type="brand"]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderCatalogRows();
    }

    function setCatFilter(val, btn) {
      currentCatFilter = val;
      currentCatalogPage = 1;
      document.querySelectorAll('[data-filter-type="cat"]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      renderCatalogRows();
    }

    function filterCatalogTable() {
      currentCatalogPage = 1;
      renderCatalogRows();
    }

    function changeCatalogPage(delta) {
      currentCatalogPage += delta;
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
      const qty = (typeof p === "object" && typeof p.stock_quantity === "number") ? p.stock_quantity : null;

      if (!isAvail) {
        return '<span style="background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); color:#F87171; padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#EF4444; display:inline-block;"></span> Esgotado</span>';
      }

      if (qty !== null && qty <= 2 && qty > 0) {
        return `<span class="badge-stock-critical" style="padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#F59E0B; display:inline-block;"></span> ⚠️ Últimas ${qty} un!</span>`;
      }

      return '<span style="background:rgba(16,185,129,0.18); border:1px solid rgba(16,185,129,0.4); color:#34D399; padding:3px 9px; border-radius:6px; font-size:0.75rem; font-weight:700; display:inline-flex; align-items:center; gap:5px;"><span style="width:7px; height:7px; border-radius:50%; background:#10B981; display:inline-block;"></span> Em Estoque</span>';
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
      const pagInfo = document.getElementById('catalog-pagination-info');
      const pagNum = document.getElementById('catalog-page-number');
      const btnPrev = document.getElementById('btn-catalog-prev');
      const btnNext = document.getElementById('btn-catalog-next');

      document.getElementById('catalog-counter').innerText = `${filtered.length} de ${allCatalog.length} peças`;

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhuma peça corresponde aos filtros aplicados.</td></tr>';
        mobileDeck.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhuma peça encontrada.</div>';
        if (pagInfo) pagInfo.innerText = '0 peças encontradas';
        if (pagNum) pagNum.innerText = '1 / 1';
        if (btnPrev) btnPrev.disabled = true;
        if (btnNext) btnNext.disabled = true;
        return;
      }

      const totalPages = Math.ceil(filtered.length / CATALOG_PAGE_SIZE) || 1;
      if (currentCatalogPage < 1) currentCatalogPage = 1;
      if (currentCatalogPage > totalPages) currentCatalogPage = totalPages;

      const startIdx = (currentCatalogPage - 1) * CATALOG_PAGE_SIZE;
      const endIdx = Math.min(startIdx + CATALOG_PAGE_SIZE, filtered.length);
      const paged = filtered.slice(startIdx, endIdx);

      if (pagInfo) {
        pagInfo.innerText = `Mostrando ${startIdx + 1} a ${endIdx} de ${filtered.length} peças`;
      }
      if (pagNum) {
        pagNum.innerText = `${currentCatalogPage} / ${totalPages}`;
      }
      if (btnPrev) btnPrev.disabled = (currentCatalogPage <= 1);
      if (btnNext) btnNext.disabled = (currentCatalogPage >= totalPages);

      tbody.innerHTML = paged.map(p => `
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

      mobileDeck.innerHTML = paged.map(p => `
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
      const catTbody = document.getElementById('catalog-tbody');
      if (catTbody && (!allCatalog || allCatalog.length === 0)) {
        catTbody.innerHTML = renderSkeletonTable(7, 5);
      }
      try {
        const res = await fetch('/api/catalog');
        const data = await res.json();
        allCatalog = data.items || [];

        const total = allCatalog.length;
        const healthy = allCatalog.filter(p => p.has_stock !== false && (p.stock_quantity > 0 || p.has_stock === true)).length;
        const outOfStock = allCatalog.filter(p => p.has_stock === false || p.stock_quantity <= 0).length;
        const bCount = document.getElementById('badge-catalog-count');
        if (bCount) bCount.innerText = total;
        const kTotal = document.getElementById('kpi-catalog-total');
        if (kTotal) kTotal.innerText = total;
        const kHealthy = document.getElementById('kpi-catalog-healthy');
        if (kHealthy) kHealthy.innerText = healthy;
        const kCritical = document.getElementById('kpi-catalog-critical');
        if (kCritical) kCritical.innerText = rate + "%";
        const kOut = document.getElementById('kpi-catalog-out');
        if (kOut) kOut.innerText = outOfStock;

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

    // --- GERENCIAMENTO DE TEMA (CLARO / ESCURO) ---
    function initTheme() {
      const saved = localStorage.getItem('victor_cell_theme') || 'dark';
      applyTheme(saved);
    }

    function applyTheme(theme) {
      const isLight = theme === 'light';
      document.documentElement.setAttribute('data-theme', isLight ? 'light' : 'dark');
      localStorage.setItem('victor_cell_theme', isLight ? 'light' : 'dark');

      const icon = document.getElementById('theme-toggle-icon');
      const label = document.getElementById('theme-toggle-label');
      if (icon) icon.innerText = isLight ? '🌙' : '☀️';
      if (label) label.innerText = isLight ? 'Modo Escuro' : 'Modo Claro';

      if (window.Chart) {
        Chart.defaults.color = isLight ? '#475569' : '#94A3B8';
        Chart.defaults.borderColor = isLight ? '#E2E8F0' : 'rgba(255, 255, 255, 0.08)';
      }
    }

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'light' ? 'dark' : 'light';
      applyTheme(next);
      showToast(next === 'light' ? '☀️ Modo Claro ativado' : '🌙 Modo Escuro ativado');
    }

    // 4. SIMULADOR DE CHAT
    async function sendChatMessage() {
      const input = document.getElementById('chat-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';

      const container = document.getElementById('chat-messages');
      const hint = document.getElementById('chat-empty-hint');
      if (hint) hint.remove();

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
        <div style="text-align: center; padding: 2.5rem 1rem; color: var(--text-muted); font-size: 0.875rem;" id="chat-empty-hint">
          <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">💬</div>
          Digite uma mensagem abaixo para simular o atendimento do balcão em tempo real.
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

    const AUDIT_LEVEL_MAP = {
      'INFO': 'Informativo',
      'WARN': 'Aviso',
      'ERROR': 'Erro'
    };

    const AUDIT_COMP_MAP = {
      'AI_ENGINE': 'Motor IA (Gemini)',
      'ROUTER': 'Roteador WhatsApp',
      'NOTIFIER': 'Notificações & Push',
      'REPO': 'Banco de Dados',
      'ADMIN': 'Painel Administrativo',
      'DEBOUNCE': 'Fila de Mensagens',
      'ERP_SYNC': 'Sincronização ERP',
      'SECURITY': 'Segurança & Sessão',
      'SYSTEM': 'Sistema Geral'
    };

    const AUDIT_ACTION_MAP = {
      'DEBOUNCE_BUFFER': 'Buffer de Digitação (Agrupamento)',
      'DEBOUNCE_FLUSH': 'Disparo de Lote de Mensagens',
      'ORDER_CREATED': 'Reserva de Pedido Criada',
      'NATIVE_PRODUCT_CREATED': 'Cadastro de Peça no Balcão',
      'STOCK_MOVEMENT': 'Movimentação de Estoque',
      'PRICE_OVERRIDE_ATTEMPT': 'Negociação / Desconto Balcão',
      'OUT_OF_STOCK_DETECTED': 'Ruptura de Estoque Identificada',
      'HUMAN_INTERVENTION_REQUESTED': 'Transbordo p/ Atendente Humano',
      'AI_RESPONSE_GENERATED': 'Resposta da IA Gerada',
      'ORDER_STATUS_CHANGED': 'Status do Pedido Atualizado',
      'SETTINGS_UPDATED': 'Configurações Salvas'
    };

    const AUDIT_ACTOR_MAP = {
      'system': 'Sistema Automático',
      'admin': 'Administrador',
      'bot': 'Robô de Atendimento'
    };

    let currentAuditLevel = '';
    let allAuditLogs = [];
    let auditSearchDebounceTimer = null;
    let currentAuditPage = 1;
    const AUDIT_PAGE_SIZE = 10;

    function filterAuditLevel(level, btn) {
      currentAuditLevel = level;
      currentAuditPage = 1;
      document.querySelectorAll('.level-pills .pill-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderAuditLogs(allAuditLogs);
    }

    function debounceAuditSearch() {
      clearTimeout(auditSearchDebounceTimer);
      auditSearchDebounceTimer = setTimeout(() => {
        currentAuditPage = 1;
        renderAuditLogs(allAuditLogs);
      }, 250);
    }

    function changeAuditPage(delta) {
      currentAuditPage += delta;
      renderAuditLogs(allAuditLogs);
    }

    async function fetchAuditLogs() {
      const auditTbody = document.getElementById('audit-table-body');
      if (auditTbody && (!allAuditLogs || allAuditLogs.length === 0)) {
        auditTbody.innerHTML = renderSkeletonTable(7, 5);
      }
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
        currentAuditPage = 1;
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

      const pageInfo = document.getElementById('audit-pagination-info');
      const pageNum = document.getElementById('audit-page-number');
      const btnPrev = document.getElementById('btn-audit-prev');
      const btnNext = document.getElementById('btn-audit-next');

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhum registro de auditoria encontrado para os filtros aplicados.</td></tr>';
        if (cardsBody) cardsBody.innerHTML = '<div style="text-align: center; padding: 1.5rem; color: var(--text-muted);">Nenhum log encontrado.</div>';
        if (pageInfo) pageInfo.innerText = 'Mostrando 0 de 0 registros';
        if (pageNum) pageNum.innerText = '1 / 1';
        if (btnPrev) btnPrev.disabled = true;
        if (btnNext) btnNext.disabled = true;
        return;
      }

      window.renderedAuditLogs = filtered;

      const totalItems = filtered.length;
      const totalPages = Math.max(1, Math.ceil(totalItems / AUDIT_PAGE_SIZE));
      if (currentAuditPage > totalPages) currentAuditPage = totalPages;
      if (currentAuditPage < 1) currentAuditPage = 1;

      const startIdx = (currentAuditPage - 1) * AUDIT_PAGE_SIZE;
      const endIdx = Math.min(startIdx + AUDIT_PAGE_SIZE, totalItems);
      const pagedLogs = filtered.slice(startIdx, endIdx);

      if (pageInfo) pageInfo.innerText = `Mostrando ${startIdx + 1} a ${endIdx} de ${totalItems} registros`;
      if (pageNum) pageNum.innerText = `${currentAuditPage} / ${totalPages}`;
      if (btnPrev) btnPrev.disabled = (currentAuditPage <= 1);
      if (btnNext) btnNext.disabled = (currentAuditPage >= totalPages);

      tbody.innerHTML = pagedLogs.map((l, pagedIdx) => {
        const globalIdx = startIdx + pagedIdx;
        const badgeClass = l.level === 'ERROR' ? 'badge-error' : (l.level === 'WARN' ? 'badge-warn' : 'badge-info');
        const levelLabel = AUDIT_LEVEL_MAP[l.level] || l.level;
        const compLabel = AUDIT_COMP_MAP[l.component] || l.component;
        const actionLabel = AUDIT_ACTION_MAP[l.action] || l.action.replace(/_/g, ' ');
        const actorLabel = AUDIT_ACTOR_MAP[l.actor] || l.actor || 'Sistema';

        const d = new Date(l.timestamp);
        const tsFormatted = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' ' + d.toLocaleDateString('pt-BR');
        const det = (typeof l.details === 'object' && l.details) ? l.details : {};
        const detStr = typeof l.details === 'object' ? JSON.stringify(l.details) : String(l.details || '');
        const lat = (l.duration_ms !== null && l.duration_ms !== undefined) ? `${Number(l.duration_ms).toFixed(0)} ms` : '-';

        // Humanizar Detalhe em Português
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
          humanSummary = actionLabel;
        }

        return `
          <tr onclick="openJsonViewer(${globalIdx})" title="Clique para abrir detalhes completos do log em JSON">
            <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted);">${tsFormatted}</td>
            <td><span class="audit-badge ${badgeClass}">${levelLabel}</span></td>
            <td><span class="audit-badge badge-comp">${compLabel}</span></td>
            <td style="font-weight: 600; font-size: 0.8rem; color: #fff;">${actionLabel}</td>
            <td style="font-family: var(--font-mono); font-size: 0.775rem; color: var(--text-muted);">${actorLabel}</td>
            <td style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--emerald);">${lat}</td>
            <td>
              <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <span style="font-size: 0.775rem; color: #CBD5E1; max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(detStr)}">
                  ${escapeHtml(humanSummary)}
                </span>
                <button class="btn btn-secondary btn-xs" style="padding: 2px 7px; font-size: 0.7rem;" onclick="event.stopPropagation(); openJsonViewer(${globalIdx})">
                  JSON Técnico
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');

      if (cardsBody) {
        cardsBody.innerHTML = pagedLogs.map(l => {
          const badgeClass = l.level === 'ERROR' ? 'badge-error' : (l.level === 'WARN' ? 'badge-warn' : 'badge-info');
          const levelLabel = AUDIT_LEVEL_MAP[l.level] || l.level;
          const compLabel = AUDIT_COMP_MAP[l.component] || l.component;
          const actionLabel = AUDIT_ACTION_MAP[l.action] || l.action.replace(/_/g, ' ');
          const actorLabel = AUDIT_ACTOR_MAP[l.actor] || l.actor || 'Sistema';

          const d = new Date(l.timestamp);
          const tsFormatted = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          const detStr = typeof l.details === 'object' ? JSON.stringify(l.details) : String(l.details || '');
          return `
            <div class="mobile-card" style="padding: 0.85rem; margin-bottom: 0.6rem; border-radius: 10px; background: var(--bg-surface); border: 1px solid var(--border-subtle);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                <span class="audit-badge ${badgeClass}">${levelLabel}</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.725rem; color: var(--text-muted);">${tsFormatted}</span>
              </div>
              <div style="font-weight: 600; font-size: 0.85rem; color: #fff; margin-bottom: 0.25rem;">${actionLabel}</div>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-bottom: 0.4rem;">Componente: <span class="audit-badge badge-comp">${compLabel}</span> | Ator: ${actorLabel}</div>
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

    // ==========================================
    // WHITE-LABEL & MULTI-TENANCY CLIENT SYSTEM
    // ==========================================
    let tenantConfig = null;

    async function loadTenantBranding() {
      try {
        const res = await fetch('/api/tenant/config');
        if (!res.ok) return;
        const config = await res.json();
        applyTenantConfig(config);
      } catch (err) {
        console.warn('Erro ao carregar branding do inquilino:', err);
      }
    }

    function syncColorPicker(pickerId, textId) {
      const picker = document.getElementById(pickerId);
      const text = document.getElementById(textId);
      if (picker && text) {
        text.value = picker.value.toUpperCase();
      }
      updateTenantPreview();
    }

    function syncColorText(textId, pickerId) {
      const text = document.getElementById(textId);
      const picker = document.getElementById(pickerId);
      if (!text || !picker) return;
      let val = text.value.trim();
      if (val && !val.startsWith('#')) val = '#' + val;
      if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
        picker.value = val;
        updateTenantPreview();
      }
    }

    function applyTenantConfig(config) {
      if (!config) return;
      tenantConfig = config;

      // 1. Título do Documento e Marca
      if (config.brand_name) {
        document.title = `${config.brand_name} • ${config.brand_slogan || 'ERP & Balcão Inteligente'}`;
        const nameElems = document.querySelectorAll('.brand-name');
        nameElems.forEach(el => {
          el.innerHTML = `${escapeHtml(config.brand_name)} <span class="brand-badge-vtex">${escapeHtml(config.brand_badge || 'PRO')}</span>`;
        });
      }
      if (config.brand_slogan) {
        const subElems = document.querySelectorAll('.brand-sub');
        subElems.forEach(el => el.innerText = config.brand_slogan);
      }

      // 2. Cores e Variáveis CSS (White-Label Dinâmico - Paleta Centralizada)
      if (config.theme) {
        const root = document.documentElement;
        if (config.theme.primary_color) {
          root.style.setProperty('--vtex-pink', config.theme.primary_color);
          root.style.setProperty('--tenant-brand', config.theme.primary_color);
          root.style.setProperty('--primary', config.theme.primary_color);
        }
        if (config.theme.primary_hover) {
          root.style.setProperty('--vtex-pink-hover', config.theme.primary_hover);
          root.style.setProperty('--tenant-brand-hover', config.theme.primary_hover);
        }
        if (config.theme.primary_glow) {
          root.style.setProperty('--vtex-pink-glow', config.theme.primary_glow);
          root.style.setProperty('--tenant-brand-glow', config.theme.primary_glow);
          const bgAlpha = config.theme.primary_glow.replace(/[\d\.]+\)$/, '0.09)');
          root.style.setProperty('--vtex-pink-bg', bgAlpha);
        }
        if (config.theme.secondary_color) {
          root.style.setProperty('--secondary-color', config.theme.secondary_color);
          root.style.setProperty('--tenant-secondary', config.theme.secondary_color);
        }
        if (config.theme.tertiary_color) {
          root.style.setProperty('--tertiary-color', config.theme.tertiary_color);
          root.style.setProperty('--tenant-tertiary', config.theme.tertiary_color);
          root.style.setProperty('--emerald', config.theme.tertiary_color);
        }
        if (config.theme.quaternary_color) {
          root.style.setProperty('--quaternary-color', config.theme.quaternary_color);
          root.style.setProperty('--tenant-quaternary', config.theme.quaternary_color);
          root.style.setProperty('--amber', config.theme.quaternary_color);
        }
        if (config.theme.filter_color) {
          root.style.setProperty('--tenant-filter-bg', config.theme.filter_color);
        }
        if (config.theme.bg_canvas) {
          root.style.setProperty('--bg-canvas', config.theme.bg_canvas);
        }
        if (config.theme.bg_surface) {
          root.style.setProperty('--bg-surface', config.theme.bg_surface);
        }
        if (config.theme.logo_icon) {
          const logoElems = document.querySelectorAll('.brand-logo');
          logoElems.forEach(el => {
            if (config.theme.logo_url) {
              el.innerHTML = `<img src="${config.theme.logo_url}" alt="Logo" style="width: 100%; height: 100%; border-radius: inherit; object-fit: cover;">`;
            } else {
              el.innerText = config.theme.logo_icon;
            }
          });
        }
      }

      // Preencher formulário de personalização se presente
      if (document.getElementById('tenant-brand-name')) {
        document.getElementById('tenant-brand-name').value = config.brand_name || '';
        document.getElementById('tenant-brand-slogan').value = config.brand_slogan || '';
        document.getElementById('tenant-brand-badge').value = config.brand_badge || 'PRO';
        if (config.theme) {
          const setField = (id, val) => {
            const el = document.getElementById(id);
            if (el && val) el.value = val;
          };
          setField('tenant-primary-color', config.theme.primary_color || '#F71963');
          setField('tenant-primary-color-text', config.theme.primary_color || '#F71963');
          setField('tenant-primary-hover', config.theme.primary_hover || '#E00E54');
          setField('tenant-primary-hover-text', config.theme.primary_hover || '#E00E54');
          setField('tenant-secondary-color', config.theme.secondary_color || '#6366F1');
          setField('tenant-secondary-color-text', config.theme.secondary_color || '#6366F1');
          setField('tenant-tertiary-color', config.theme.tertiary_color || '#10B981');
          setField('tenant-tertiary-color-text', config.theme.tertiary_color || '#10B981');
          setField('tenant-quaternary-color', config.theme.quaternary_color || '#F59E0B');
          setField('tenant-quaternary-color-text', config.theme.quaternary_color || '#F59E0B');
          setField('tenant-filter-color', config.theme.filter_color || '#334155');
          setField('tenant-filter-color-text', config.theme.filter_color || '#334155');
          setField('tenant-logo-icon', config.theme.logo_icon || '⚡');
          setField('tenant-logo-url', config.theme.logo_url || '');
        }
        updateTenantPreview();
        setupTenantPreviewListeners();
      }
    }

    function updateTenantPreview() {
      const brandName = document.getElementById('tenant-brand-name')?.value || 'Victor Cell';
      const slogan = document.getElementById('tenant-brand-slogan')?.value || 'ERP & Balcão Inteligente';
      const badge = document.getElementById('tenant-brand-badge')?.value || 'PRO';
      const primaryColor = document.getElementById('tenant-primary-color')?.value || '#F71963';
      const secondaryColor = document.getElementById('tenant-secondary-color')?.value || '#6366F1';
      const tertiaryColor = document.getElementById('tenant-tertiary-color')?.value || '#10B981';
      const quaternaryColor = document.getElementById('tenant-quaternary-color')?.value || '#F59E0B';
      const icon = document.getElementById('tenant-logo-icon')?.value || '⚡';

      const previewName = document.getElementById('tenant-preview-name');
      if (previewName) previewName.innerText = brandName;

      const previewSlogan = document.getElementById('tenant-preview-slogan');
      if (previewSlogan) previewSlogan.innerText = slogan;

      const previewTag = document.getElementById('tenant-preview-tag');
      if (previewTag) previewTag.innerText = badge;

      const previewIcon = document.getElementById('tenant-preview-icon');
      if (previewIcon) previewIcon.innerText = icon;

      const previewBadge = document.getElementById('tenant-preview-badge');
      if (previewBadge) {
        previewBadge.style.background = primaryColor;
        previewBadge.style.boxShadow = `0 4px 14px ${hexToRgba(primaryColor, 0.3)}`;
      }

      const previewBtn = document.getElementById('tenant-preview-btn');
      if (previewBtn) previewBtn.style.background = primaryColor;

      const previewSecBtn = document.getElementById('tenant-preview-sec-btn');
      if (previewSecBtn) previewSecBtn.style.background = secondaryColor;

      const previewTertBadge = document.getElementById('tenant-preview-tert-badge');
      if (previewTertBadge) previewTertBadge.style.background = tertiaryColor;

      const previewQuatBadge = document.getElementById('tenant-preview-quat-badge');
      if (previewQuatBadge) previewQuatBadge.style.background = quaternaryColor;
    }

    let tenantListenersBound = false;
    function setupTenantPreviewListeners() {
      if (tenantListenersBound) return;
      tenantListenersBound = true;
      const ids = [
        'tenant-brand-name', 'tenant-brand-slogan', 'tenant-brand-badge', 'tenant-logo-icon',
        'tenant-primary-color', 'tenant-primary-color-text',
        'tenant-secondary-color', 'tenant-secondary-color-text',
        'tenant-tertiary-color', 'tenant-tertiary-color-text',
        'tenant-quaternary-color', 'tenant-quaternary-color-text',
        'tenant-filter-color', 'tenant-filter-color-text',
        'tenant-primary-hover', 'tenant-primary-hover-text'
      ];
      ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
          el.addEventListener('input', () => {
            updateTenantPreview();
          });
        }
      });
    }

    async function saveTenantBranding(e) {
      if (e) e.preventDefault();
      try {
        const primaryVal = document.getElementById('tenant-primary-color')?.value || '#F71963';
        const payload = {
          tenant_id: (tenantConfig && tenantConfig.tenant_id) || 'tenant_custom',
          brand_name: document.getElementById('tenant-brand-name')?.value || 'Victor Cell',
          brand_slogan: document.getElementById('tenant-brand-slogan')?.value || 'ERP & Balcão Inteligente',
          brand_badge: document.getElementById('tenant-brand-badge')?.value || 'PRO',
          theme: {
            primary_color: primaryVal,
            primary_hover: document.getElementById('tenant-primary-hover')?.value || '#E00E54',
            primary_glow: hexToRgba(primaryVal, 0.25),
            secondary_color: document.getElementById('tenant-secondary-color')?.value || '#6366F1',
            tertiary_color: document.getElementById('tenant-tertiary-color')?.value || '#10B981',
            quaternary_color: document.getElementById('tenant-quaternary-color')?.value || '#F59E0B',
            filter_color: document.getElementById('tenant-filter-color')?.value || '#334155',
            bg_canvas: '#090D14',
            bg_surface: '#121826',
            logo_icon: document.getElementById('tenant-logo-icon')?.value || '⚡',
            logo_url: document.getElementById('tenant-logo-url')?.value || ''
          },
          modules: (tenantConfig && tenantConfig.modules) || {
            whatsapp: true, orders: true, metrics: true, catalog: true,
            erp: true, copilot: true, audit: true, profile: true, simulator: true
          }
        };

        const res = await fetch('/api/tenant/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
          showToast('Identidade visual e tema atualizados com sucesso!', 'success');
          applyTenantConfig(data.config);
        } else {
          showToast('Erro ao atualizar: ' + (data.message || 'Falha'), 'error');
        }
      } catch (err) {
        showToast('Erro de conexão ao salvar tema: ' + err, 'error');
      }
    }

    function hexToRgba(hex, alpha) {
      hex = hex.replace('#', '');
      if (hex.length === 3) {
        hex = hex.split('').map(c => c + c).join('');
      }
      const num = parseInt(hex, 16);
      const r = (num >> 16) & 255;
      const g = (num >> 8) & 255;
      const b = num & 255;
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // --- GESTÃO INDEPENDENTE DE CLIENTES & ASSISTÊNCIAS TÉCNICAS VIP ---
    let allCustomers = [];
    let currentCustTier = 'all';
    let currentCustomerSortCol = 'orders_count';
    let currentCustomerSortDir = 'desc';
    let currentCustRecurrenceBracket = 'all';
    const CUSTOMERS_PAGE_SIZE = 10;
    let currentCustomerPage = 1;

    async function fetchCustomers() {
      const tbody = document.getElementById('customers-tbody');
      if (tbody && (!allCustomers || allCustomers.length === 0)) {
        tbody.innerHTML = renderSkeletonTable(5, 7);
      }
      try {
        const params = new URLSearchParams();
        if (currentCustTier && currentCustTier !== 'all') params.set('tier', currentCustTier);
        if (currentCustomerSortCol) params.set('sort_by', currentCustomerSortCol);
        if (currentCustomerSortDir) params.set('sort_dir', currentCustomerSortDir);
        if (currentCustRecurrenceBracket && currentCustRecurrenceBracket !== 'all') params.set('recurrence_bracket', currentCustRecurrenceBracket);
        const searchInput = document.getElementById('customers-search');
        if (searchInput && searchInput.value.trim()) params.set('search', searchInput.value.trim());

        const res = await fetch(`/api/customers?${params.toString()}`);
        const data = await res.json();
        allCustomers = data.customers || [];

        // Atualizar contadores e badges
        const countBadge = document.getElementById('badge-customers-count');
        if (countBadge) countBadge.innerText = data.total || allCustomers.length;

        const kpiTotal = document.getElementById('kpi-cust-total');
        if (kpiTotal) kpiTotal.innerText = data.total || allCustomers.length;

        const kpiRecurrent = document.getElementById('kpi-cust-recurrent');
        if (kpiRecurrent) {
          const recCount = allCustomers.filter(c => c.orders_count >= 5).length;
          kpiRecurrent.innerText = `${recCount} parceiros`;
        }

        const kpiLtv = document.getElementById('kpi-cust-ltv');
        if (kpiLtv) {
          const totalSpent = allCustomers.reduce((acc, c) => acc + (c.total_spent || 0), 0);
          const avgLtv = allCustomers.length > 0 ? (totalSpent / allCustomers.length) : 0;
          kpiLtv.innerText = `R$ ${avgLtv.toFixed(2)}`;
        }

        const kpiUber = document.getElementById('kpi-cust-uber');
        if (kpiUber) {
          const totalDeliveries = allCustomers.reduce((acc, c) => acc + (c.uber_deliveries || 0), 0);
          kpiUber.innerText = `${totalDeliveries} entregas`;
        }

        renderCustomersRows();

        // Se o gráfico de distribuição de clientes estiver no DOM e ainda não renderizado com dados reais
        const ctxCust = document.getElementById('chartCustomersShare');
        if (ctxCust && data.tiers_summary) {
          renderCustomersShareChart(data.tiers_summary);
        }
      } catch (err) {
        console.error('Erro ao buscar clientes:', err);
      }
    }

    function renderCustomersShareChart(tiersSummary) {
      const ctxCust = document.getElementById('chartCustomersShare');
      if (!ctxCust) return;
      if (window.chartCustomersShareInstance) {
        window.chartCustomersShareInstance.destroy();
      }
      window.chartCustomersShareInstance = new Chart(ctxCust, {
        type: 'doughnut',
        data: {
          labels: ['VIP Platinum', 'Ouro Recorrente', 'Prata Ativo', 'Novos Parceiros'],
          datasets: [{
            data: [
              tiersSummary.VIP_PLATINUM || 0,
              tiersSummary.OURO_RECORRENTE || 0,
              tiersSummary.PRATA_ATIVO || 0,
              tiersSummary.NOVO_PARCEIRO || 0
            ],
            backgroundColor: ['#A855F7', '#F59E0B', '#94A3B8', '#38BDF8'],
            borderColor: '#0E1422',
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: { color: '#94A3B8', font: { size: 11 }, boxWidth: 12 }
            }
          },
          onClick: () => {
            navigateWithFilter('customers');
          }
        }
      });
    }

    function formatCustomerTierBadge(tier) {
      const map = {
        'VIP_PLATINUM': '<span class="pill badge-tier-platinum" style="font-weight:700;">💎 VIP Platinum</span>',
        'OURO_RECORRENTE': '<span class="pill badge-tier-gold" style="font-weight:700;">🥇 Ouro Recorrente</span>',
        'PRATA_ATIVO': '<span class="pill badge-tier-silver" style="font-weight:700;">🥈 Prata Ativo</span>',
        'NOVO_PARCEIRO': '<span class="pill badge-tier-bronze" style="font-weight:700;">🥉 Novo Parceiro</span>'
      };
      return map[tier] || `<span class="pill">${escapeHtml(tier)}</span>`;
    }

    function setCustomerTierFilter(tier, btn) {
      currentCustTier = tier;
      document.querySelectorAll('[data-cust-tier]').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-cust-tier') === tier);
      });
      if (btn) btn.classList.add('active');
      currentCustomerPage = 1;
      fetchCustomers();
    }

    function toggleCustomerColumnSort(col) {
      if (currentCustomerSortCol === col) {
        currentCustomerSortDir = currentCustomerSortDir === 'asc' ? 'desc' : 'asc';
      } else {
        currentCustomerSortCol = col;
        currentCustomerSortDir = (col === 'name' || col === 'phone') ? 'asc' : 'desc';
      }
      const sel = document.getElementById('cust-sort-select');
      if (sel) {
        if (col === 'orders_count') sel.value = currentCustomerSortDir === 'asc' ? 'recurrence_asc' : 'recurrence_desc';
        else if (col === 'total_spent') sel.value = currentCustomerSortDir === 'asc' ? 'spent_asc' : 'spent_desc';
        else if (col === 'name') sel.value = currentCustomerSortDir === 'asc' ? 'name_asc' : 'name_desc';
        else if (col === 'uber_deliveries') sel.value = 'uber_desc';
      }
      currentCustomerPage = 1;
      fetchCustomers();
    }

    function applyCustomerSort(val) {
      if (val === 'recurrence_desc') { currentCustomerSortCol = 'orders_count'; currentCustomerSortDir = 'desc'; }
      else if (val === 'recurrence_asc') { currentCustomerSortCol = 'orders_count'; currentCustomerSortDir = 'asc'; }
      else if (val === 'spent_desc') { currentCustomerSortCol = 'total_spent'; currentCustomerSortDir = 'desc'; }
      else if (val === 'spent_asc') { currentCustomerSortCol = 'total_spent'; currentCustomerSortDir = 'asc'; }
      else if (val === 'name_asc') { currentCustomerSortCol = 'name'; currentCustomerSortDir = 'asc'; }
      else if (val === 'name_desc') { currentCustomerSortCol = 'name'; currentCustomerSortDir = 'desc'; }
      else if (val === 'uber_desc') { currentCustomerSortCol = 'uber_deliveries'; currentCustomerSortDir = 'desc'; }
      currentCustomerPage = 1;
      fetchCustomers();
    }

    function setCustomerRecurrenceBracket(bracket) {
      currentCustRecurrenceBracket = bracket;
      currentCustomerPage = 1;
      fetchCustomers();
    }

    function filterCustomersTable() {
      currentCustomerPage = 1;
      fetchCustomers();
    }

    function changeCustomerPage(delta) {
      currentCustomerPage += delta;
      renderCustomersRows();
    }

    function renderCustomersRows() {
      const tbody = document.getElementById('customers-tbody');
      const mobileDeck = document.getElementById('customers-cards-mobile');
      if (!tbody && !mobileDeck) return;

      const searchInput = document.getElementById('customers-search');
      const query = (searchInput ? searchInput.value : '').toLowerCase().trim();

      let filtered = [...allCustomers];
      if (currentCustTier && currentCustTier !== 'all') {
        filtered = filtered.filter(c => (c.loyalty_tier || c.tier) === currentCustTier);
      }
      if (currentCustRecurrenceBracket && currentCustRecurrenceBracket !== 'all') {
        if (currentCustRecurrenceBracket === 'vip_heavy') {
          filtered = filtered.filter(c => (c.orders_count || 0) >= 15);
        } else if (currentCustRecurrenceBracket === 'high') {
          filtered = filtered.filter(c => (c.orders_count || 0) >= 5 && (c.orders_count || 0) < 15);
        } else if (currentCustRecurrenceBracket === 'medium') {
          filtered = filtered.filter(c => (c.orders_count || 0) >= 2 && (c.orders_count || 0) < 5);
        } else if (currentCustRecurrenceBracket === 'new') {
          filtered = filtered.filter(c => (c.orders_count || 0) === 1);
        } else if (currentCustRecurrenceBracket === 'zero') {
          filtered = filtered.filter(c => (c.orders_count || 0) === 0);
        }
      }
      if (query) {
        filtered = filtered.filter(c =>
          (c.name && c.name.toLowerCase().includes(query)) ||
          (c.phone && c.phone.toLowerCase().includes(query)) ||
          (c.document && c.document.toLowerCase().includes(query)) ||
          (c.neighborhood && c.neighborhood.toLowerCase().includes(query))
        );
      }

      // Ordenação das colunas
      filtered.sort((a, b) => {
        let res = 0;
        if (currentCustomerSortCol === 'name') {
          res = (a.name || '').localeCompare(b.name || '');
        } else if (currentCustomerSortCol === 'phone') {
          res = (a.phone || '').localeCompare(b.phone || '');
        } else if (currentCustomerSortCol === 'tier') {
          const rank = { 'VIP_PLATINUM': 4, 'OURO_RECORRENTE': 3, 'PRATA_ATIVO': 2, 'NOVO_PARCEIRO': 1 };
          const tA = rank[a.loyalty_tier || a.tier] || 0;
          const tB = rank[b.loyalty_tier || b.tier] || 0;
          res = tA - tB;
        } else if (currentCustomerSortCol === 'total_spent') {
          res = (Number(a.total_spent) || 0) - (Number(b.total_spent) || 0);
        } else if (currentCustomerSortCol === 'uber_deliveries') {
          res = (Number(a.uber_deliveries) || 0) - (Number(b.uber_deliveries) || 0);
        } else { // default orders_count
          res = (Number(a.orders_count) || 0) - (Number(b.orders_count) || 0);
        }
        return currentCustomerSortDir === 'asc' ? res : -res;
      });

      // Atualizar ícones das colunas
      const sortCols = ['name', 'phone', 'tier', 'orders_count', 'total_spent', 'uber_deliveries'];
      sortCols.forEach(col => {
        const el = document.getElementById(`sort-icon-${col}`);
        if (el) {
          if (currentCustomerSortCol === col) {
            el.className = 'sort-icon active';
            el.innerText = currentCustomerSortDir === 'asc' ? '▲' : '▼';
          } else {
            el.className = 'sort-icon';
            el.innerText = '⇅';
          }
        }
      });

      const counter = document.getElementById('customers-counter');
      if (counter) counter.innerText = `${filtered.length} clientes`;

      const totalPages = Math.ceil(filtered.length / CUSTOMERS_PAGE_SIZE) || 1;
      currentCustomerPage = Math.max(1, Math.min(currentCustomerPage, totalPages));

      const start = (currentCustomerPage - 1) * CUSTOMERS_PAGE_SIZE;
      const pageItems = filtered.slice(start, start + CUSTOMERS_PAGE_SIZE);

      // Atualizar paginação
      const pageInfo = document.getElementById('customers-pagination-info');
      if (pageInfo) {
        const end = Math.min(start + CUSTOMERS_PAGE_SIZE, filtered.length);
        pageInfo.innerText = filtered.length > 0 ? `Mostrando ${start + 1}-${end} de ${filtered.length} clientes` : 'Nenhum resultado';
      }
      const pageNum = document.getElementById('customers-page-number');
      if (pageNum) pageNum.innerText = `Página ${currentCustomerPage} de ${totalPages}`;

      const btnPrev = document.getElementById('btn-cust-prev');
      if (btnPrev) btnPrev.disabled = currentCustomerPage <= 1;

      const btnNext = document.getElementById('btn-cust-next');
      if (btnNext) btnNext.disabled = currentCustomerPage >= totalPages;

      if (!pageItems || pageItems.length === 0) {
        if (tbody) {
          tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2.5rem; color: var(--text-muted);"><div style="font-size: 1.5rem; margin-bottom: 0.5rem;"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg></div>Nenhuma assistência técnica encontrada para o filtro.</td></tr>';
        }
        if (mobileDeck) {
          mobileDeck.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Nenhuma assistência encontrada.</div>';
        }
        return;
      }

      if (tbody) {
        tbody.innerHTML = pageItems.map(c => {
          const cleanPhone = (c.phone || '').replace(/\D/g, '');
          const waLink = `https://wa.me/${cleanPhone}`;
          return `
            <tr class="order-row-hover">
              <td>
                <div style="font-weight: 700; color: #fff;">${escapeHtml(c.name)}</div>
                <div style="font-size: 0.725rem; color: var(--text-dim); font-family: var(--font-mono);">${escapeHtml(c.document || 'Sem CNPJ')} • ${escapeHtml(c.neighborhood || 'Fortaleza')}</div>
              </td>
              <td>
                <div style="font-size: 0.85rem; font-family: var(--font-mono); color: #CBD5E1;">${formatPhoneBR(c.phone)}</div>
                <a href="${waLink}" target="_blank" style="font-size: 0.725rem; color: #34D399; text-decoration: none;">Abrir WhatsApp ↗</a>
              </td>
              <td>${formatCustomerTierBadge(c.loyalty_tier)}</td>
              <td style="font-weight: 700; color: #E2E8F0; text-align: center;">${c.orders_count || 0}</td>
              <td style="font-weight: 800; color: #34D399; font-size: 0.95rem;">R$ ${(c.total_spent || 0).toFixed(2)}</td>
              <td>
                <span class="pill pill-cyan" style="font-weight: 600;">${c.uber_deliveries || 0} Uber Flash</span>
              </td>
              <td>
                <div style="display: flex; gap: 0.45rem;">
                  <button class="btn btn-emerald btn-sm" onclick="openChatDrawer('${c.phone}', '${escapeHtml(c.name)}', '${c.phone}', true)">
                    💬 Chat
                  </button>
                  <button class="btn btn-secondary btn-sm" onclick="navigateWithFilter('orders', { search: '${escapeHtml(c.name)}' })">
                    📦 Pedidos
                  </button>
                </div>
              </td>
            </tr>
          `;
        }).join('');
      }

      if (mobileDeck) {
        mobileDeck.innerHTML = pageItems.map(c => {
          return `
            <div class="customer-card-mobile">
              <div class="card-mobile-top">
                <div>
                  <div style="font-weight: 700; font-size: 0.95rem; color: #fff;">${escapeHtml(c.name)}</div>
                  <div style="font-size: 0.75rem; color: var(--text-dim); font-family: var(--font-mono);">${formatPhoneBR(c.phone)} • ${escapeHtml(c.neighborhood || 'Fortaleza')}</div>
                </div>
                ${formatCustomerTierBadge(c.loyalty_tier)}
              </div>
              <div class="card-mobile-body">
                <div style="display: flex; justify-content: space-between; font-size: 0.825rem;">
                  <span>Total Pedidos: <strong style="color: #fff;">${c.orders_count || 0}</strong></span>
                  <span>Volume: <strong style="color: #34D399;">R$ ${(c.total_spent || 0).toFixed(2)}</strong></span>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-dim);">Entregas Uber: ${c.uber_deliveries || 0} viagens</div>
              </div>
              <div class="card-mobile-actions">
                <button class="btn btn-emerald btn-sm" onclick="openChatDrawer('${c.phone}', '${escapeHtml(c.name)}', '${c.phone}', true)">💬 Chat Ao Vivo</button>
                <button class="btn btn-secondary btn-sm" onclick="navigateWithFilter('orders', { search: '${escapeHtml(c.name)}' })">📦 Pedidos</button>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    // Expor funções interativas ao escopo global para acesso inline em onclick/oninput
    window.changeCatalogPage = changeCatalogPage;
    window.setBrandFilter = setBrandFilter;
    window.setCatFilter = setCatFilter;
    window.filterCatalogTable = filterCatalogTable;
    window.syncColorPicker = syncColorPicker;
    window.syncColorText = syncColorText;
    window.sendQuickPrompt = sendQuickPrompt;
    window.clearCopilotChat = clearCopilotChat;
    window.sendCopilotMessage = sendCopilotMessage;
    window.saveTenantBranding = saveTenantBranding;
    window.navigateWithFilter = navigateWithFilter;
    window.fetchCustomers = fetchCustomers;
    window.setCustomerTierFilter = setCustomerTierFilter;
    window.filterCustomersTable = filterCustomersTable;
    window.changeCustomerPage = changeCustomerPage;
    window.toggleCustomerColumnSort = toggleCustomerColumnSort;
    window.applyCustomerSort = applyCustomerSort;
    window.setCustomerRecurrenceBracket = setCustomerRecurrenceBracket;

    // Inicialização ao Carregar
    initTheme();
    loadTenantBranding();
    fetchConversations();
    fetchStats();
    fetchCatalog();
    fetchCustomers();
    fetchAuditLogs();
    checkMasterAISwitch();
    fetchWhatsAppQR();

    // Auto-refresh suave a cada 20 segundos
    setInterval(() => {
      fetchConversations();
      fetchStats();
      fetchCustomers();
    }, 20000);

    // --- ATALHOS DE TECLADO ERGONÔMICOS DE BALCÃO ---
    document.addEventListener('keydown', (e) => {
      // Esc: Fechar qualquer drawer, modal ou sidebar aberta
      if (e.key === 'Escape') {
        if (typeof closeChatDrawer === 'function') closeChatDrawer();
        if (typeof closeErpModal === 'function') closeErpModal();
        const sidebar = document.getElementById('app-sidebar');
        const overlay = document.getElementById('sidebar-overlay');
        if (sidebar && sidebar.classList.contains('sidebar-open')) {
          sidebar.classList.remove('sidebar-open');
          if (overlay) overlay.classList.remove('active');
        }
      }
      // Ctrl+K ou / : Foco imediato na busca de catálogo
      if ((e.ctrlKey && e.key.toLowerCase() === 'k') || (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA')) {
        e.preventDefault();
        switchTab('catalog');
        const searchInput = document.getElementById('catalog-search-input');
        if (searchInput) {
          searchInput.focus();
          searchInput.select();
        }
      }
      // F2: Cadastrar nova peça no estoque ERP
      if (e.key === 'F2') {
        e.preventDefault();
        if (typeof openErpModal === 'function') openErpModal();
      }
    });
