"""
Test Suite for Enterprise Features:
- StoreProfile (Whitelabel / Multi-tenant Commercial Configuration)
- AuditLogEntry & Structured Audit Logging (Observability & Compliance)
- StaffNotificationDispatcher (Pluggable Multi-Channel Staff Alerting)
- PostgresRepository Interface & Factory
- API Endpoints (/api/audit/logs, /api/system/profile)
"""

import os
import json
import pytest
import aiosqlite
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from domain.entities import (
    StoreProfile,
    AuditLogEntry,
    Conversation,
    ConversationState,
    ReservationOrder,
    OrderStatus,
)
from infrastructure.repositories.sqlite_repository import SqliteRepository
from infrastructure.repositories.database_factory import create_database_repository
from infrastructure.notifiers.base import (
    StaffNotificationChannel,
    NotificationPayload,
    NotificationPriority,
)
from infrastructure.notifiers.dispatcher import StaffNotificationDispatcher
from infrastructure.notifiers.ntfy_channel import NtfyNotificationChannel
from infrastructure.notifiers.call_channel import PhoneCallNotificationChannel


# --- 1. Testes de Entidade de Domínio ---

def test_store_profile_default_and_customization():
    default_p = StoreProfile()
    assert default_p.store_name == "Victor Cell"
    assert "fortaleza" in default_p.city.lower()
    assert "iphone" in default_p.out_of_scope_keywords
    assert "celular" in default_p.out_of_scope_keywords
    assert default_p.is_out_of_scope("amigo tem tela de iphone 11?") is True
    assert default_p.is_out_of_scope("quanto tá a tela do tab a8?") is False

    custom_p = StoreProfile(
        store_id="tenant_sp",
        store_name="Alpha Peças SP",
        city="São Paulo/SP",
        niche_description="Peças exclusivas de notebook",
        out_of_scope_keywords=["celular", "tablet", "videogame"],
        rejection_message="Só peças de notebook",
    )
    assert custom_p.is_out_of_scope("você conserta tablet?") is True
    assert custom_p.is_out_of_scope("tem tela de notebook dell?") is False


def test_audit_log_entry_creation():
    entry = AuditLogEntry(
        action="TEST_ACTION",
        component="AI_ENGINE",
        level="INFO",
        actor="system",
        details={"model": "gemini-2.5", "tokens": 42},
        duration_ms=120.5,
        status="SUCCESS",
    )
    assert entry.id is not None
    assert entry.level == "INFO"
    assert entry.details["model"] == "gemini-2.5"
    assert entry.duration_ms == 120.5


# --- 2. Testes de Persistência no Repositório SQLite ---

@pytest.mark.asyncio
async def test_sqlite_store_profile_crud(tmp_path):
    db_file = str(tmp_path / "test_store_profile.db")
    repo = SqliteRepository(db_path=db_file)
    await repo.init_db()

    # Busca perfil padrão gerado na ausência de registro prévio
    profile = await repo.get_store_profile("default")
    assert profile.store_id == "default"
    assert profile.store_name == "Victor Cell"

    # Atualiza perfil
    profile.store_name = "Mega Tablets Brasil"
    profile.city = "Recife/PE"
    profile.out_of_scope_keywords = ["carro", "moto", "celular"]
    profile.rejection_message = "Trabalhamos apenas com tablets"
    await repo.save_store_profile(profile)

    # Reabre e valida persistência
    saved = await repo.get_store_profile("default")
    assert saved.store_name == "Mega Tablets Brasil"
    assert saved.city == "Recife/PE"
    assert "carro" in saved.out_of_scope_keywords
    assert saved.rejection_message == "Trabalhamos apenas com tablets"


@pytest.mark.asyncio
async def test_sqlite_audit_logs_persistence_and_filtering(tmp_path):
    db_file = str(tmp_path / "test_audit.db")
    repo = SqliteRepository(db_path=db_file)
    await repo.init_db()

    # Grava 3 entradas com diferentes níveis e componentes
    e1 = AuditLogEntry(
        action="QUOTE_GENERATED",
        component="AI_ENGINE",
        level="INFO",
        actor="5585999990001",
        details={"sku": "TEL-SAM-A8"},
        duration_ms=85.0,
    )
    e2 = AuditLogEntry(
        action="HUMAN_HANDOFF_TRIGGERED",
        component="ROUTER",
        level="WARN",
        actor="5585999990002",
        details={"reason": "preço alto"},
        duration_ms=12.0,
    )
    e3 = AuditLogEntry(
        action="PAYMENT_GATEWAY_TIMEOUT",
        component="ERP_SYNC",
        level="ERROR",
        actor="system",
        details={"error": "timeout"},
        duration_ms=5000.0,
        status="FAILURE",
    )

    await repo.record_audit_log(e1)
    await repo.record_audit_log(e2)
    await repo.record_audit_log(e3)

    # Lista todos
    all_logs = await repo.list_audit_logs(limit=50)
    assert len(all_logs) == 3

    # Filtra por nível ERROR
    error_logs = await repo.list_audit_logs(level="ERROR")
    assert len(error_logs) == 1
    assert error_logs[0].action == "PAYMENT_GATEWAY_TIMEOUT"

    # Filtra por componente ROUTER
    router_logs = await repo.list_audit_logs(component="ROUTER")
    assert len(router_logs) == 1
    assert router_logs[0].action == "HUMAN_HANDOFF_TRIGGERED"


# --- 3. Testes do Notificador Modular Multi-Canal ---

class MockSuccessChannel(StaffNotificationChannel):
    def get_channel_name(self) -> str:
        return "MOCK_SUCCESS"

    async def is_available(self) -> bool:
        return True

    async def dispatch(self, payload: NotificationPayload) -> bool:
        return True


class MockFailingChannel(StaffNotificationChannel):
    def get_channel_name(self) -> str:
        return "MOCK_FAILING"

    async def is_available(self) -> bool:
        return True

    async def dispatch(self, payload: NotificationPayload) -> bool:
        return False


@pytest.mark.asyncio
async def test_staff_notification_dispatcher_dispatches_and_records_audit(tmp_path):
    db_file = str(tmp_path / "test_notifier_audit.db")
    repo = SqliteRepository(db_path=db_file)
    await repo.init_db()

    mock_ch = MockSuccessChannel()
    dispatcher = StaffNotificationDispatcher(
        channels=[mock_ch],
        repository=repo,
    )

    success = await dispatcher.notify_dispatch_order(
        order_id="ORD-9988",
        customer_phone="5585999991234",
        product_desc="Tela Samsung Tab A8 Original",
        destination_address="Rua Barão do Rio Branco 1102",
        customer_name="Carlos Silva",
    )
    assert success is True

    # Verifica gravação automática no log de auditoria
    logs = await repo.list_audit_logs(component="NOTIFIER")
    assert len(logs) == 1
    assert logs[0].action == "STAFF_NOTIFICATION_DISPATCHED"
    assert logs[0].actor == "5585999991234"
    assert logs[0].status == "SUCCESS"
    assert "ORD-9988" in logs[0].details["order_id"]


@pytest.mark.asyncio
async def test_staff_notification_dispatcher_handoff():
    mock_ch = MockSuccessChannel()
    dispatcher = StaffNotificationDispatcher(channels=[mock_ch], repository=None)
    res = await dispatcher.notify_handoff(
        customer_phone="5585988887777",
        reason="Dúvida sobre solda de conector",
        raw_message="amigo vocês soldam na hora?",
        customer_name="Roberto",
    )
    assert res is True


# --- 4. Testes de Fábrica de Banco de Dados ---

def test_database_factory_resolution(tmp_path):
    # Sem DATABASE_URL -> Retorna SqliteRepository
    sqlite_instance = create_database_repository(
        database_url=None,
        sqlite_path=str(tmp_path / "factory.db"),
    )
    assert isinstance(sqlite_instance, SqliteRepository)

    # Com Postgres DSN -> Tenta carregar PostgresRepository
    pg_instance = create_database_repository(
        database_url="postgresql://user:pass@localhost:5432/pecasbot_test",
        sqlite_path=str(tmp_path / "fallback.db"),
    )
    from infrastructure.repositories.postgres_repository import PostgresRepository
    assert isinstance(pg_instance, PostgresRepository)


# --- 5. Testes dos Novos Endpoints de API ---

def test_api_audit_and_profile_endpoints():
    from fastapi.testclient import TestClient
    from presentation.api import app, create_session_token
    from infrastructure.config import settings

    client = TestClient(app)
    token = create_session_token(settings.DASHBOARD_USERNAME, settings.DASHBOARD_SECRET_KEY)
    cookies = {"victor_session": token}

    # 1. GET /api/audit/logs
    res = client.get("/api/audit/logs", cookies=cookies)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "logs" in data

    # 2. GET /api/system/profile
    res = client.get("/api/system/profile", cookies=cookies)
    assert res.status_code == 200
    pdata = res.json()
    assert pdata["status"] == "success"
    assert "store_name" in pdata["profile"]

    # 3. POST /api/system/profile
    update_payload = {
        "store_name": "Test Loja Whitelabel",
        "city": "Fortaleza/CE",
        "niche_description": "Tablets e Peças de Reposição",
        "out_of_scope_keywords": ["smartphone", "iphone", "celular"],
        "rejection_message": "Só peças de tablet",
        "delivery_methods": ["Balcão", "Uber Flash"],
        "tone_guidelines": "Respostas secas e objetivas de balcão",
    }
    res = client.post("/api/system/profile", json=update_payload, cookies=cookies)
    assert res.status_code == 200
    up_data = res.json()
    assert up_data["status"] == "success"

    # Confirma que foi gravado log de auditoria para a alteração
    res_logs = client.get("/api/audit/logs?limit=5", cookies=cookies)
    assert res_logs.status_code == 200
    recent_logs = res_logs.json()["logs"]
    assert any(l["action"] == "STORE_PROFILE_UPDATED" for l in recent_logs)
