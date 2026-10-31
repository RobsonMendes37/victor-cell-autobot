"""
Unit tests for Pure Domain Entities.
"""

from datetime import datetime, timedelta, timezone

from domain.entities import (
    Conversation,
    ConversationState,
    Product,
    QualityTier,
    ReservationOrder,
)


def test_product_in_stock():
    p = Product(
        sku="TEST-01",
        name="Tela Teste",
        category="Tela",
        compatible_models=["A15"],
        quality=QualityTier.ORIGINAL_NACIONAL,
        has_frame=True,
        price=150.0,
        stock_quantity=3,
    )
    assert p.is_in_stock is True

    p.stock_quantity = 0
    assert p.is_in_stock is False


def test_conversation_pause_and_timeout():
    conv = Conversation(id="conv_1", customer_phone="5585991234567")
    assert conv.is_ai_allowed() is True

    # Dono assumiu
    conv.pause_for_human(duration_hours=2)
    assert conv.state == ConversationState.HUMAN_ACTIVE
    assert conv.is_ai_allowed() is False

    # Timeout expirou (simula 3 horas no passado)
    conv.human_resumed_at = datetime.now(timezone.utc) - timedelta(hours=3)
    assert conv.is_ai_allowed() is True
    assert conv.state == ConversationState.AI_ACTIVE


def test_conversation_manual_resume():
    conv = Conversation(id="conv_1", customer_phone="5585991234567")
    conv.pause_for_human(duration_hours=5)
    assert conv.is_ai_allowed() is False

    # Comando #bot
    conv.resume_ai()
    assert conv.is_ai_allowed() is True
    assert conv.state == ConversationState.AI_ACTIVE


def test_order_expiration():
    order = ReservationOrder(
        customer_phone="5585991234567",
        customer_name="João",
        product_sku="TEL-SAM-A15-ORIG",
        quantity=1,
        product_price=190.0,
        destination_address="Rua A, 100",
    )
    assert order.is_expired is False

    # Simula 3 horas no passado
    order.expires_at = datetime.now(timezone.utc) - timedelta(minutes=10)
    assert order.is_expired is True
