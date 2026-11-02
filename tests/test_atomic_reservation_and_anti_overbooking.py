"""
Test Suite for Atomic Reservation Guard and Anti-Overbooking Protection.
Validates that if a piece runs out of stock right as the customer confirms,
no order is created and an immediate out-of-stock notice is returned.
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


class MockOrderRepo(OrderRepositoryInterface):
    def __init__(self):
        self.saved_orders = []

    async def save_order(self, order):
        self.saved_orders.append(order)
        return order.id

    async def list_orders(self):
        return self.saved_orders

    async def get_recent_orders_by_phone(self, customer_phone: str, limit: int = 3):
        return [o for o in self.saved_orders if o.customer_phone == customer_phone][:limit]


class MockConversationRepo(ConversationRepositoryInterface):
    def __init__(self):
        self.conversations = {}

    async def get_or_create(self, customer_phone):
        if customer_phone not in self.conversations:
            self.conversations[customer_phone] = Conversation(
                id=f"conv-{customer_phone}",
                customer_phone=customer_phone,
                state=ConversationState.WAITING_CONFIRMATION,
                active_sku="TEL-SAM-A15-ORIG",
            )
        return self.conversations[customer_phone]

    async def save(self, conversation):
        self.conversations[conversation.customer_phone] = conversation

    async def save_message(self, customer_phone: str, role: str, content: str) -> None:
        pass

    async def get_recent_messages(self, customer_phone: str, limit: int = 15, max_age_hours: int = 48):
        return []


class MockProductRepo(ProductRepositoryInterface):
    def __init__(self, initial_stock: int = 1):
        self.stock = initial_stock
        self.product = Product(
            sku="TEL-SAM-A15-ORIG",
            name="Tela Samsung A15",
            category="Tablet",
            compatible_models=["A15"],
            quality=QualityTier.ORIGINAL_NACIONAL,
            has_frame=True,
            price=190.0,
            stock_quantity=self.stock,
        )

    async def list_all(self):
        return [self.product]

    async def get_by_sku(self, sku: str):
        return self.product if sku == self.product.sku else None

    async def search(self, query: str, quality=None, has_frame=None):
        return [self.product]

    async def decrement_stock(self, sku: str, quantity: int = 1) -> bool:
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False

    async def increment_stock(self, sku: str, quantity: int = 1) -> bool:
        self.stock += quantity
        return True

    async def update_stock(self, sku: str, new_quantity: int) -> bool:
        self.stock = new_quantity
        return True


@pytest.mark.asyncio
async def test_atomic_reservation_success_when_in_stock():
    conv_repo = MockConversationRepo()
    order_repo = MockOrderRepo()
    prod_repo = MockProductRepo(initial_stock=1)

    mock_gateway = AsyncMock(spec=MessagingGatewayInterface)
    mock_ai = AsyncMock(spec=AIServiceInterface)
    mock_ai.process_and_reply.return_value = {
        "intent": "ORDER_DISPATCH",
        "reply_text": "Separando a tela. Aguarde o Uber.",
        "target_sku": "TEL-SAM-A15-ORIG",
        "destination_address": "Rua Central 100",
    }

    use_case = ProcessIncomingMessageUseCase(
        conversation_repo=conv_repo,
        product_repo=prod_repo,
        order_repo=order_repo,
        messaging_gateway=mock_gateway,
        ai_service=mock_ai,
    )

    res = await use_case.execute(
        customer_phone="5585999990001",
        push_name="Técnico João",
        message_text="Pode mandar o Uber!",
        from_me=False,
    )

    assert res["status"] == "SUCCESS"
    assert res["order_created"] is True
    assert prod_repo.stock == 0
    assert len(order_repo.saved_orders) == 1


@pytest.mark.asyncio
async def test_anti_overbooking_guards_when_out_of_stock():
    conv_repo = MockConversationRepo()
    order_repo = MockOrderRepo()
    # Estoque zerado (peça esgotou antes da confirmação)
    prod_repo = MockProductRepo(initial_stock=0)

    mock_gateway = AsyncMock(spec=MessagingGatewayInterface)
    mock_ai = AsyncMock(spec=AIServiceInterface)
    mock_ai.process_and_reply.return_value = {
        "intent": "ORDER_DISPATCH",
        "reply_text": "Separando a tela.",
        "target_sku": "TEL-SAM-A15-ORIG",
        "destination_address": "Rua Central 100",
    }

    use_case = ProcessIncomingMessageUseCase(
        conversation_repo=conv_repo,
        product_repo=prod_repo,
        order_repo=order_repo,
        messaging_gateway=mock_gateway,
        ai_service=mock_ai,
    )

    res = await use_case.execute(
        customer_phone="5585999990002",
        push_name="Técnico Maria",
        message_text="Sim, confirma o envio!",
        from_me=False,
    )

    # Não deve criar pedido
    assert res["status"] == "OUT_OF_STOCK"
    assert res["order_created"] is False
    assert len(order_repo.saved_orders) == 0
    assert "acabou de esgotar" in res["reply"]
    # Cliente é notificado diretamente no WhatsApp
    mock_gateway.send_text.assert_called_with("5585999990002", "Essa peça acabou de esgotar aqui no estoque.")
