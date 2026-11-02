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
