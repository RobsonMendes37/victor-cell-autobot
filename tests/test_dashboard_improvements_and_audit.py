import pytest
from starlette.testclient import TestClient

from presentation.api import SESSION_COOKIE_NAME, app


@pytest.fixture
def auth_client():
    client = TestClient(app)
    # Login to acquire session
    res = client.post("/login", data={"username": "admin", "password": "victorcell2026"}, follow_redirects=False)
    assert res.status_code == 303
    cookie_val = res.cookies[SESSION_COOKIE_NAME]
    client.cookies[SESSION_COOKIE_NAME] = cookie_val
    return client

def test_api_conversations_with_last_message(auth_client):
    res = auth_client.get("/api/conversations")
    assert res.status_code == 200
    data = res.json()
    assert "conversations" in data
    assert len(data["conversations"]) > 0
    first = data["conversations"][0]
    assert "last_message" in first
    assert "formatted_phone" in first
    assert "last_message_role" in first

def test_get_conversation_messages_history(auth_client):
    res_convs = auth_client.get("/api/conversations")
    phone = res_convs.json()["conversations"][0]["phone"]

    res = auth_client.get(f"/api/conversations/{phone}/messages")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "messages" in data
    assert "formatted_phone" in data

def test_get_ai_pipeline_status(auth_client):
    res = auth_client.get("/api/ai/pipeline-status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "active_models" in data
    assert "chat" in data["active_models"]
    assert "voice" in data["active_models"]
    assert "vision" in data["active_models"]
    assert "circuit_breaker" in data
    assert "daily_usage" in data
    assert data["daily_usage"]["daily_quota"] == 1500
    assert "requests_today" in data["daily_usage"]

def test_create_native_product_manual(auth_client):
    sku = "TEST-MANUAL-TAB-M10"
    payload = {
        "sku": sku,
        "name": "Tela Tablet Multilaser M10A 3G",
        "category": "Tela Frontal",
        "quality": "Primeira Linha / Incell",
        "cost_price": 95.0,
        "price": 160.0,
        "stock_quantity": 4,
        "supplier_name": "Fornecedor Central SP",
        "location": "Gaveta B4"
    }
    res = auth_client.post("/api/erp/products", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["product"]["sku"] == sku

def test_whatsapp_categorized_metrics(auth_client):
    res = auth_client.get("/api/reports/stats")
    assert res.status_code == 200
    data = res.json()
    assert "whatsapp_categorization" in data
    cat = data["whatsapp_categorization"]
    assert "total_messages" in cat
    assert "quotes_answered" in cat
    assert "confirmed_orders" in cat
    assert "stock_ruptures" in cat

def test_dashboard_html_ergonomics_and_static_assets(auth_client):
    res = auth_client.get("/dashboard")
    assert res.status_code == 200
    html = res.text
    # Verificação de contenção dos gráficos (Fim do bug de 200% da tela)
    assert "chart-canvas-wrapper" in html
    # Desacoplamento de CSS e JS para /static/ (com suporte a cache-busting)
    assert '/static/css/dashboard.css' in html
    assert '/static/js/dashboard.js' in html
    # Ausência de alucinação de modelos legados
    assert "Gemini 1.5 Pro" not in html
    # Separação de Métricas e Relatórios
    assert 'id="tab-reports"' in html
    assert 'id="audit-pagination-bar"' in html
    # Controles de tema e novas listagens intuitivas
    assert 'id="btn-theme-toggle"' in html
    assert 'id="top-assistencias-list"' in html
    assert "Original vs. Paralela" in html
    assert "Resultados do Funil de Vendas" in html
    # Limpeza do simulador: sem introdução robótica imposta
    assert 'id="chat-empty-hint"' in html
    assert "Olá. Balcão Victor Cell. Informe o modelo" not in html
    assert "Opa meu patrão" not in html

    # Validação do CSS servido como arquivo estático
    res_css = auth_client.get("/static/css/dashboard.css")
    assert res_css.status_code == 200
    assert "--tenant-brand" in res_css.text
    assert '[data-theme="light"]' in res_css.text
    assert ".mobile-cards-container" in res_css.text
    assert ".top-workshop-row" in res_css.text
    assert ".chart-canvas-wrapper" in res_css.text
    assert ".filter-pill-group" in res_css.text
    assert ".filter-btn" in res_css.text
    assert ".pagination-bar" in res_css.text

    # Validação do JS servido como arquivo estático
    res_js = auth_client.get("/static/js/dashboard.js")
    assert res_js.status_code == 200
    assert "maintainAspectRatio: false" in res_js.text
    assert "loadTenantBranding" in res_js.text
    assert "initTheme" in res_js.text
    assert "PENDING_SEPARATION" in res_js.text
    assert "READY_TO_PICKUP" in res_js.text
    assert "top-assistencias-list" in res_js.text
    assert "Escape" in res_js.text
    assert "ctrlKey" in res_js.text
    assert "AUDIT_PAGE_SIZE = 10" in res_js.text
    assert "exportReportsCsv" in res_js.text
    assert "AUDIT_MAPPER" in res_js.text or "AUDIT_LEVEL_MAP" in res_js.text
    assert "Opa meu patrão" not in res_js.text


def test_tenant_config_get_and_post(auth_client):
    # 1. GET inicial
    res_get = auth_client.get("/api/tenant/config")
    assert res_get.status_code == 200
    data = res_get.json()
    assert "tenant_id" in data
    assert "brand_name" in data
    assert "theme" in data
    assert "primary_color" in data["theme"]

    # 2. POST de atualização (White-Label)
    payload = {
        "tenant_id": "forta_cell_test",
        "brand_name": "Forta Cell Parts",
        "brand_slogan": "Distribuidora de Peças e Telas",
        "brand_badge": "ENTERPRISE",
        "theme": {
            "primary_color": "#06B6D4",
            "primary_hover": "#0891B2",
            "primary_glow": "rgba(6, 182, 212, 0.25)",
            "bg_canvas": "#0B0F19",
            "bg_surface": "#111827",
            "logo_icon": "🔧",
            "logo_url": ""
        },
        "modules": {
            "whatsapp": True,
            "orders": True,
            "metrics": True,
            "catalog": True,
            "erp": True,
            "copilot": True,
            "audit": True,
            "profile": True,
            "simulator": False
        }
    }
    res_post = auth_client.post("/api/tenant/config", json=payload)
    assert res_post.status_code == 200
    res_data = res_post.json()
    assert res_data["status"] == "success"
    assert res_data["config"]["brand_name"] == "Forta Cell Parts"

    # 3. GET para confirmar persistência
    res_verify = auth_client.get("/api/tenant/config")
    assert res_verify.status_code == 200
    assert res_verify.json()["brand_name"] == "Forta Cell Parts"

    # 4. Restaura configuração padrão Victor Cell
    default_payload = {
        "tenant_id": "victor_cell",
        "brand_name": "Victor Cell",
        "brand_slogan": "ERP & Balcão Inteligente",
        "brand_badge": "PRO",
        "theme": {
            "primary_color": "#F71963",
            "primary_hover": "#E00E54",
            "primary_glow": "rgba(247, 25, 99, 0.25)",
            "bg_canvas": "#090D14",
            "bg_surface": "#121826",
            "logo_icon": "⚡",
            "logo_url": ""
        },
        "modules": {
            "whatsapp": True,
            "orders": True,
            "metrics": True,
            "catalog": True,
            "erp": True,
            "copilot": True,
            "audit": True,
            "profile": True,
            "simulator": True
        }
    }
    auth_client.post("/api/tenant/config", json=default_payload)


def test_tenant_config_with_centralized_palette(auth_client):
    payload = {
        "tenant_id": "victor_cell",
        "brand_name": "Victor Cell Enterprise",
        "brand_slogan": "ERP & Balcão Inteligente",
        "brand_badge": "VIP",
        "theme": {
            "primary_color": "#F71963",
            "primary_hover": "#E00E54",
            "primary_glow": "rgba(247, 25, 99, 0.25)",
            "secondary_color": "#6366F1",
            "tertiary_color": "#10B981",
            "quaternary_color": "#F59E0B",
            "filter_color": "#334155",
            "bg_canvas": "#090D14",
            "bg_surface": "#121826",
            "logo_icon": "⚡",
            "logo_url": ""
        },
        "modules": {
            "whatsapp": True, "orders": True, "metrics": True, "catalog": True,
            "erp": True, "copilot": True, "audit": True, "profile": True, "simulator": True
        }
    }
    res_post = auth_client.post("/api/tenant/config", json=payload)
    assert res_post.status_code == 200
    theme = res_post.json()["config"]["theme"]
    assert theme["secondary_color"] == "#6366F1"
    assert theme["tertiary_color"] == "#10B981"
    assert theme["quaternary_color"] == "#F59E0B"
    assert theme["filter_color"] == "#334155"


def test_api_orders_rest_endpoints(auth_client):
    # 1. Listagem com paginação e filtros
    res_list = auth_client.get("/api/orders?limit=10&offset=0")
    assert res_list.status_code == 200
    data = res_list.json()
    assert "orders" in data
    assert "total" in data
    assert "limit" in data
    assert data["limit"] == 10

    # 2. Get por ID
    if len(data["orders"]) > 0:
        first_id = data["orders"][0]["id"]
        res_get = auth_client.get(f"/api/orders/{first_id}")
        assert res_get.status_code == 200
        order_data = res_get.json()
        assert order_data["order"]["id"] == first_id

    # 3. 404 para ID inexistente
    res_not_found = auth_client.get("/api/orders/order-non-existent-999")
    assert res_not_found.status_code == 404


def test_api_catalog_by_sku_rest_endpoint(auth_client):
    res_catalog = auth_client.get("/api/catalog")
    assert res_catalog.status_code == 200
    items = res_catalog.json().get("items", [])
    if len(items) > 0:
        sku = items[0]["sku"]
        res_sku = auth_client.get(f"/api/catalog/{sku}")
        assert res_sku.status_code == 200
        assert res_sku.json()["product"]["sku"] == sku

    # 404 para SKU inexistente
    res_404 = auth_client.get("/api/catalog/SKU-NON-EXISTENT-XYZ")
    assert res_404.status_code == 404


def test_dashboard_html_palette_and_catalog_pagination(auth_client):
    res = auth_client.get("/dashboard")
    assert res.status_code == 200
    html = res.text
    # Catalog pagination elements
    assert "catalog-pagination-bar" in html
    assert "btn-catalog-prev" in html
    assert "btn-catalog-next" in html
    assert "catalog-pagination-info" in html
    # Centralized Palette elements
    assert "tenant-secondary-color" in html
    assert "tenant-tertiary-color" in html
    assert "tenant-quaternary-color" in html
    assert "tenant-filter-color" in html
    assert "tenant-preview-sec-btn" in html
    assert "tenant-preview-tert-badge" in html
    assert "tenant-preview-quat-badge" in html
    # Copilot chips and chat elements
    assert "quick-chip-btn" in html
    assert "copilot-chat-container" in html


def test_customers_rest_endpoints(auth_client):
    # 1. Listagem completa e sumário
    res = auth_client.get("/api/customers")
    assert res.status_code == 200
    data = res.json()
    assert "customers" in data
    assert "total" in data
    assert "tiers_summary" in data
    assert data["total"] >= 15
    assert "VIP_PLATINUM" in data["tiers_summary"]

    # 2. Filtro por Tier
    res_vip = auth_client.get("/api/customers?tier=VIP_PLATINUM")
    assert res_vip.status_code == 200
    vip_data = res_vip.json()
    for cust in vip_data["customers"]:
        assert cust["loyalty_tier"] == "VIP_PLATINUM"

    # 3. Busca por Nome ou Bairro
    res_search = auth_client.get("/api/customers?search=TechFix")
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert len(search_data["customers"]) >= 1
    assert "TechFix" in search_data["customers"][0]["name"]

    # 4. Detalhes do Cliente por ID ou Alias
    first_cust_id = data["customers"][0]["id"]
    res_detail = auth_client.get(f"/api/customers/{first_cust_id}")
    assert res_detail.status_code == 200
    detail_data = res_detail.json()
    assert detail_data["customer"]["id"] == first_cust_id
    assert "orders" in detail_data

    res_alias = auth_client.get("/api/customers/cust-1")
    assert res_alias.status_code == 200

    # 5. Cadastro/Atualização de Parceiro
    new_customer = {
        "id": "cust-test-novo",
        "name": "Nova Era Smart Reparos",
        "phone": "(85) 99777-4444",
        "document": "33.444.555/0001-99",
        "neighborhood": "Fátima",
        "loyalty_tier": "NOVO_PARCEIRO",
        "orders_count": 1,
        "total_spent": 180.0,
        "uber_deliveries": 1
    }
    res_post = auth_client.post("/api/customers", json=new_customer)
    assert res_post.status_code == 200
    post_data = res_post.json()
    assert post_data["status"] == "success"
    assert post_data["customer"]["name"] == "Nova Era Smart Reparos"


def test_dashboard_html_customers_and_catalog_fixes(auth_client):
    res = auth_client.get("/dashboard")
    assert res.status_code == 200
    html = res.text

    # Novo Módulo de Clientes independente
    assert 'id="tab-customers"' in html
    assert 'id="customers-tbody"' in html
    assert 'id="customers-search"' in html
    assert 'id="customers-pagination-bar"' in html
    assert 'id="customers-cards-mobile"' in html

    # Gráfico de Distribuição no Overview
    assert 'id="chartCustomersShare"' in html
    assert "Distribuição de Clientes & Fidelidade" in html

    # Deep linking interativo
    assert "clickable-card" in html
    assert "navigateWithFilter" in html

    # Verificação de remoção de elemento feio no catálogo e sincronização
    assert "Sincronizar Agora" in html
    # O botão de sincronizar não deve ter o emoji relâmpago de texto solto
    assert "⚡ Sincronizar Agora" not in html

    # CSS e JS verificações
    res_css = auth_client.get("/static/css/dashboard.css")
    assert ".clickable-card" in res_css.text
    assert ".kpi-icon-wrapper" in res_css.text
    assert ".badge-tier-platinum" in res_css.text

    res_js = auth_client.get("/static/js/dashboard.js")
    assert "fetchCustomers" in res_js.text
    assert "navigateWithFilter" in res_js.text
    assert "setCustomerTierFilter" in res_js.text
    assert "renderCustomersShareChart" in res_js.text
    assert "toggleCustomerColumnSort" in res_js.text
    assert "applyCustomerSort" in res_js.text
    assert "setCustomerRecurrenceBracket" in res_js.text

    # Verificação de títulos concisos e controles avançados de ordenação / recorrência
    assert "Separação & Balcão" in html
    assert "Fila de Separação de Peças & Balcão de Saída" not in html
    assert 'id="cust-sort-select"' in html
    assert 'id="cust-recurrence-bracket"' in html
    assert "sort-icon" in html
    assert ".sort-icon" in res_css.text

    # Verificação da API de Categorização do WhatsApp com baseline não-zerado
    res_stats = auth_client.get("/api/reports/stats")
    assert res_stats.status_code == 200
    stats_data = res_stats.json()
    assert "whatsapp_categorization" in stats_data
    wa = stats_data["whatsapp_categorization"]
    assert wa.get("quotes_answered", 0) > 0 or wa.get("quotations_count", 0) > 0
    assert wa.get("confirmed_orders", 0) > 0 or wa.get("orders_count", 0) > 0


def test_sonarqube_cicd_configuration():
    import os

    # 1. Verifica presença e conteúdo do sonar-project.properties
    assert os.path.exists("sonar-project.properties"), "Arquivo sonar-project.properties deve existir na raiz"
    with open("sonar-project.properties", "r", encoding="utf-8") as f:
        sonar_cfg = f.read()

    assert "sonar.projectKey=victor-cell-pecasbot" in sonar_cfg
    assert "sonar.sources=" in sonar_cfg
    assert "sonar.python.coverage.reportPaths=coverage.xml" in sonar_cfg
    assert "sonar.javascript.lcov.reportPaths=coverage/lcov.info" in sonar_cfg

    # 2. Verifica presença do SonarQube no workflow do GitHub Actions
    workflow_path = ".github/workflows/deploy.yml"
    assert os.path.exists(workflow_path), "Workflow do GitHub Actions deve existir"
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_content = f.read()

    assert "sonarqube-quality-gate" in workflow_content
    assert "SonarSource/sonarqube-scan-action" in workflow_content
    assert "SONAR_TOKEN" in workflow_content

    # 3. Verifica requirements.txt com pytest-cov
    with open("requirements.txt", "r", encoding="utf-8") as f:
        reqs = f.read()
    assert "pytest-cov" in reqs


def test_unified_dashboard_overview_bff_endpoint(auth_client):
    """Testa o endpoint consolidado BFF (/api/dashboard/overview)."""
    res = auth_client.get("/api/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "kpis" in data
    assert "stats" in data
    assert "whatsapp_categorization" in data
    assert "stock_summary" in data
    assert "customers_summary" in data
    assert "pipeline_ai" in data
    assert "tenant_config" in data
    assert "recent_orders" in data
    assert data["kpis"]["total_revenue"] >= 0


def test_customers_server_side_sorting_and_recurrence_filtering(auth_client):
    """Testa se a ordenação e filtros de recorrência são processados pelo servidor."""
    # 1. Ordenação por recorrência decrescente
    res_desc = auth_client.get("/api/customers?sort_by=orders_count&sort_dir=desc")
    assert res_desc.status_code == 200
    custs_desc = res_desc.json()["customers"]
    if len(custs_desc) >= 2:
        assert custs_desc[0]["orders_count"] >= custs_desc[-1]["orders_count"]

    # 2. Ordenação por recorrência crescente
    res_asc = auth_client.get("/api/customers?sort_by=orders_count&sort_dir=asc")
    assert res_asc.status_code == 200
    custs_asc = res_asc.json()["customers"]
    if len(custs_asc) >= 2:
        assert custs_asc[0]["orders_count"] <= custs_asc[-1]["orders_count"]

    # 3. Filtro de faixa de recorrência: apenas alta recorrência (5 a 14)
    res_high = auth_client.get("/api/customers?recurrence_bracket=high")
    assert res_high.status_code == 200
    custs_high = res_high.json()["customers"]
    for c in custs_high:
        assert 5 <= c["orders_count"] <= 14

    # 4. Filtro por nome alfabético A-Z
    res_name = auth_client.get("/api/customers?sort_by=name&sort_dir=asc")
    assert res_name.status_code == 200
    custs_name = res_name.json()["customers"]
    if len(custs_name) >= 2:
        assert custs_name[0]["name"].lower() <= custs_name[-1]["name"].lower()





