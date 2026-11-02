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


