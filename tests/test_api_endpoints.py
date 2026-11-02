"""
Integration Tests for Presentation API Endpoints (presentation/api.py).
Tests:
- Authentication, Session Management, Rate Limiting & Lockout
- Protected Dashboard and API Routes (/api/conversations, /api/catalog, /api/reports/stats)
- CSV Export & Analytics Filter (/api/reports/orders.csv, /api/reports/analytics/filter)
- AI Switch Toggle & Conversation Human Override (Pause/Resume)
- Webhook Ingestion (Inbound text, Operator Outbound, ERP Stock Webhook, Ignored Events)
"""

import pytest
from starlette.testclient import TestClient

from infrastructure.config import settings
from presentation.api import SESSION_COOKIE_NAME, app, create_session_token


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_cookies():
    token = create_session_token(settings.DASHBOARD_USERNAME, settings.DASHBOARD_SECRET_KEY)
    return {SESSION_COOKIE_NAME: token}


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_login_page_renders(client):
    res = client.get("/login")
    assert res.status_code == 200
    assert "Victor Cell" in res.text
    assert "Entrar" in res.text or "Victor Cell" in res.text


def test_dashboard_requires_auth(client):
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/login"


def test_login_invalid_credentials_and_rate_limiting(client):
    from presentation.api import LOGIN_ATTEMPTS
    LOGIN_ATTEMPTS.clear()

    # Attempt 1: Wrong password
    res = client.post("/login", data={"username": "admin", "password": "wrongpass"})
    assert res.status_code in [200, 401]
    assert "incorretos" in res.text

    # Attempt 2 to 5
    for _ in range(4):
        res = client.post("/login", data={"username": "admin", "password": "wrongpass"})

    # Attempt 6: Locked out
    res_locked = client.post("/login", data={"username": "admin", "password": "wrongpass"})
    assert "Muitas tentativas incorretas" in res_locked.text


def test_login_valid_credentials_and_session(client):
    from presentation.api import LOGIN_ATTEMPTS
    LOGIN_ATTEMPTS.clear()

    res = client.post(
        "/login",
        data={"username": settings.DASHBOARD_USERNAME, "password": settings.DASHBOARD_PASSWORD},
        follow_redirects=False,
    )
    assert res.status_code == 303
    assert res.headers["location"] == "/dashboard"
    assert SESSION_COOKIE_NAME in res.cookies

    # Access dashboard with session
    cookie_val = res.cookies[SESSION_COOKIE_NAME]
    res_dash = client.get("/dashboard", cookies={SESSION_COOKIE_NAME: cookie_val})
    assert res_dash.status_code == 200
    assert "Victor Cell" in res_dash.text
    assert "Separação & Balcão de Saída" in res_dash.text


def test_logout_clears_session(client, auth_cookies):
    res = client.get("/logout", cookies=auth_cookies, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/login"


def test_protected_api_routes_require_auth(client):
    for endpoint in ["/api/conversations", "/api/catalog", "/api/reports/stats"]:
        res = client.get(endpoint)
        assert res.status_code == 401


def test_api_conversations_with_auth(client, auth_cookies):
    res = client.get("/api/conversations", cookies=auth_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "conversations" in data or isinstance(data, list)


def test_api_catalog_with_auth(client, auth_cookies):
    res = client.get("/api/catalog", cookies=auth_cookies)
    assert res.status_code == 200
    data = res.json()
    items = data.get("items", data) if isinstance(data, dict) else data
    assert isinstance(items, list)
    assert len(items) > 0


def test_api_reports_stats(client, auth_cookies):
    res = client.get("/api/reports/stats", cookies=auth_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "total_revenue" in data
    assert "total_orders" in data


def test_api_reports_sync_sheets(client, auth_cookies):
    res = client.post("/api/reports/sync-sheets", cookies=auth_cookies)
    assert res.status_code == 200
    assert res.json()["status"] == "synced"


def test_api_reports_orders_csv(client, auth_cookies):
    res = client.get("/api/reports/orders.csv", cookies=auth_cookies)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "ID Pedido" in res.text


def test_api_system_ai_switch_toggle(client, auth_cookies):
    # Check current switch
    res = client.get("/api/system/ai-switch", cookies=auth_cookies)
    assert res.status_code == 200
    initial_state = res.json()["global_ai_enabled"]

    # Toggle switch
    res_toggle = client.post("/api/system/ai-switch/toggle", cookies=auth_cookies)
    assert res_toggle.status_code == 200
    assert res_toggle.json()["global_ai_enabled"] != initial_state

    # Restore to True so other webhook tests pass without being blocked by kill switch
    client.post("/api/system/ai-switch/toggle", json={"enabled": True}, cookies=auth_cookies)


def test_api_conversation_pause_and_resume(client, auth_cookies):
    phone = "5585991118888"
    # Pause for human
    res_pause = client.post(f"/api/conversations/{phone}/pause", cookies=auth_cookies)
    assert res_pause.status_code == 200
    assert res_pause.json()["status"] == "success"

    # Resume AI
    res_resume = client.post(f"/api/conversations/{phone}/resume", cookies=auth_cookies)
    assert res_resume.status_code == 200
    assert res_resume.json()["status"] == "success"


def test_api_reports_analytics_filter(client, auth_cookies):
    res = client.get("/api/reports/analytics/filter?period=today", cookies=auth_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "closed_orders" in data
    assert "top_products" in data


def test_webhook_erp_stock(client):
    payload = {
        "evento": "estoque.alterado",
        "retorno": {
            "codigo": "TEL-SAM-A15-ORIG",
            "saldo": 12,
        }
    }
    res = client.post("/webhook/erp/stock", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "received"


def test_webhook_inbound_message(client):
    import asyncio

    from presentation.api import sqlite_repo
    asyncio.run(sqlite_repo.set_global_ai_status(True))

    # Isolated phone number: 5585988881111
    payload = {
        "event": "messages.upsert",
        "instance": "victor-cell-01",
        "data": {
            "key": {
                "remoteJid": "5585988881111@s.whatsapp.net",
                "fromMe": False,
                "id": "test_msg_unique_inbound_001",
            },
            "pushName": "Tecnico Carlos",
            "message": {
                "conversation": "Boa tarde, tem tela do A15?",
            },
        },
    }
    res = client.post("/webhook", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "queued_in_debounce"


def test_webhook_operator_outbound(client):
    # Isolated phone number: 5585988882222
    payload = {
        "event": "messages.upsert",
        "instance": "victor-cell-01",
        "data": {
            "key": {
                "remoteJid": "5585988882222@s.whatsapp.net",
                "fromMe": True,
                "id": "test_msg_unique_operator_002",
            },
            "message": {
                "conversation": "Opa Carlos, aqui é o Victor, vou separar pra você.",
            },
        },
    }
    res = client.post("/webhook", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "ai_paused"


def test_webhook_ignored_event(client):
    payload = {
        "event": "connection.update",
        "data": {"state": "open"},
    }
    res = client.post("/webhook", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "ignored"


def test_api_whatsapp_qrcode_endpoint(client, auth_cookies):
    res = client.get("/api/whatsapp/qrcode", cookies=auth_cookies)
    # May return error or status depending on Evolution API connection, but shouldn't 500
    assert res.status_code in [200, 502, 503]


def test_api_ai_quota_info(client, auth_cookies):
    res = client.get("/api/ai/quota-info", cookies=auth_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert "masked_key" in data


def test_api_ai_update_key_invalid(client, auth_cookies):
    res = client.post("/api/ai/update-key", json={"api_key": ""}, cookies=auth_cookies)
    assert res.status_code in [400, 422]


def test_api_pipeline_chats_summary(client, auth_cookies):
    res = client.get("/api/pipeline/chats-summary", cookies=auth_cookies)
    assert res.status_code in [200, 404]


def test_api_simulator_chat_inbound(client, auth_cookies):
    payload = {
        "message": "Tem touch do M7?",
    }
    res = client.post("/api/simulator/chat", json=payload, cookies=auth_cookies)
    assert res.status_code == 200
    data = res.json()
    assert "intent" in data or "reply" in data or "status" in data


def test_api_copilot_chat(client, auth_cookies):
    payload = {"message": "Qual a peça mais vendida?"}
    res = client.post("/api/copilot/chat", json=payload, cookies=auth_cookies)
    assert res.status_code == 200
    assert "reply" in res.json()


def test_api_products_endpoint(client):
    res = client.get("/products")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_api_ai_update_key_valid(client, auth_cookies):
    valid_key = "AIzaSyB1234567890abcdefghijklmnopqrstuvwxyz"
    res = client.post("/api/ai/update-key", json={"new_key": valid_key}, cookies=auth_cookies)
    assert res.status_code == 200
    assert res.json()["status"] == "success"
