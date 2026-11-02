"""
Test Suite for Overbooking Audit and Metrics Recording.
Validates that blocked overbooking events increment telemetry counters and record audit logs.
"""

from unittest.mock import AsyncMock

import pytest

from application.use_cases.process_incoming_message import ProcessIncomingMessageUseCase
from domain.entities import Conversation, ConversationState, Product, QualityTier
from domain.gateways import AIServiceInterface, MessagingGatewayInterface
from domain.repositories import (
    ConversationRepositoryInterface,
    OrderRepositoryInterface,
    ProductRepositoryInterface,
)
from infrastructure.services.metrics_service import metrics_collector


class DummyConvRepo(ConversationRepositoryInterface):
    def __init__(self):
        self.conv = Conversation(
            id="c-1",
            customer_phone="5585988880001",
            state=ConversationState.WAITING_CONFIRMATION,
            active_sku="SKU-DEPLETED",
        )

    async def get_or_create(self, phone):
        return self.conv

    async def save(self, c):
        pass

    async def save_message(self, phone, role, content):
        pass

    async def get_recent_messages(self, phone, limit=15, max_age_hours=48):
        return []


class DummyOrderRepo(OrderRepositoryInterface):
    async def save_order(self, order):
        return order.id

    async def list_orders(self):
        return []

    async def get_recent_orders_by_phone(self, phone, limit=3):
        return []


class DepletedProductRepo(ProductRepositoryInterface):
    async def list_all(self):
        return []

    async def get_by_sku(self, sku):
        return Product(
            sku=sku,
            name="Peça Esgotada",
            category="Tablet",
            compatible_models=["T1"],
            quality=QualityTier.ORIGINAL_NACIONAL,
            has_frame=False,
            price=150.0,
            stock_quantity=0,
        )

    async def search(self, query, quality=None, has_frame=None):
        return []

    async def decrement_stock(self, sku, quantity=1):
        # Falha de estoque (0 saldo)
        return False

    async def increment_stock(self, sku, quantity=1):
        return True

    async def update_stock(self, sku, new_quantity):
        return True


@pytest.mark.asyncio
async def test_overbooking_blocked_increments_metric_and_audit():
    initial_count = metrics_collector.overbooking_blocked_total

    conv_repo = DummyConvRepo()
    order_repo = DummyOrderRepo()
    prod_repo = DepletedProductRepo()

    mock_sqlite = AsyncMock()
    mock_sqlite.record_audit_event = AsyncMock()
    mock_sqlite.get_store_profile = AsyncMock(return_value=None)

    mock_gateway = AsyncMock(spec=MessagingGatewayInterface)
    mock_ai = AsyncMock(spec=AIServiceInterface)
    mock_ai.process_and_reply.return_value = {
        "intent": "ORDER_DISPATCH",
        "reply_text": "Separando.",
        "target_sku": "SKU-DEPLETED",
        "destination_address": "Rua Central 50",
    }

    use_case = ProcessIncomingMessageUseCase(
        conversation_repo=conv_repo,
        product_repo=prod_repo,
        order_repo=order_repo,
        messaging_gateway=mock_gateway,
        ai_service=mock_ai,
        sqlite_repo=mock_sqlite,
    )

    res = await use_case.execute(
        customer_phone="5585988880001",
        push_name="Técnico Carlos",
        message_text="Pode mandar!",
        from_me=False,
    )

    assert res["status"] == "OUT_OF_STOCK"
    assert res["order_created"] is False
    # Verifica incremento de métricas
    assert metrics_collector.overbooking_blocked_total == initial_count + 1
    # Verifica registro na trilha de auditoria
    mock_sqlite.record_audit_event.assert_called_once()
    called_entry = mock_sqlite.record_audit_event.call_args[0][0]
    assert called_entry.action == "OVERBOOKING_BLOCKED"
    assert called_entry.level == "WARN"
    assert called_entry.details["sku"] == "SKU-DEPLETED"
