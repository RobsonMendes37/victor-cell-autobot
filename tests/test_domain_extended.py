"""
Extended Domain and Business Rules Tests.
Covers 100% of:
- Conversation state machine and AI authorization rules
- Product stock availability rules
- Reservation order expiration logic
- Store business hours (Domingo, antes da abertura, durante expediente, após expediente, sábado e sexta)
"""

from datetime import datetime, timedelta, timezone

import pytz

from domain.entities import (
    Conversation,
    ConversationState,
    OrderStatus,
    Product,
    QualityTier,
    ReservationOrder,
)
from infrastructure.config import settings


def test_conversation_state_machine_branches():
    conv = Conversation(id="test_conv_1", customer_phone="5585991112222")
    assert conv.is_ai_allowed() is True

    # 1. Closed state
    conv.state = ConversationState.CLOSED
    assert conv.is_ai_allowed() is False

    # 2. Human active inside timeout window
    conv.state = ConversationState.HUMAN_ACTIVE
    conv.human_silence_duration_hours = 3
    conv.human_resumed_at = datetime.now(timezone.utc) - timedelta(hours=1)
    assert conv.is_ai_allowed() is False

    # 3. Human active past timeout window (auto-resumes to AI_ACTIVE)
    conv.human_resumed_at = datetime.now(timezone.utc) - timedelta(hours=4)
    assert conv.is_ai_allowed() is True
    assert conv.state == ConversationState.AI_ACTIVE
    assert conv.human_resumed_at is None

    # 4. Explicit pause and resume
    conv.pause_for_human(duration_hours=2)
    assert conv.state == ConversationState.HUMAN_ACTIVE
    assert conv.human_silence_duration_hours == 2
    assert conv.is_ai_allowed() is False

    conv.resume_ai()
    assert conv.state == ConversationState.AI_ACTIVE
    assert conv.is_ai_allowed() is True


def test_product_stock_properties():
    p1 = Product(
        sku="P1",
        name="Touch Teste",
        category="Tab",
        compatible_models=[],
        quality=QualityTier.ORIGINAL_NACIONAL,
        has_frame=False,
        price=50.0,
        stock_quantity=5,
        has_stock=True,
    )
    assert p1.is_in_stock is True

    # Stock zero
    p1.stock_quantity = 0
    assert p1.is_in_stock is False

    # Stock quantity > 0 but has_stock flag False
    p1.stock_quantity = 10
    p1.has_stock = False
    assert p1.is_in_stock is False


def test_reservation_order_expiry():
    order = ReservationOrder(
        customer_phone="5585991113333",
        customer_name="Cliente Teste",
        product_sku="TEL-TAB-A8-1LINHA",
        quantity=1,
        product_price=140.0,
        destination_address="Balcão",
    )
    assert order.is_expired is False

    # Past expiration
    order.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    assert order.is_expired is True

    # If already delivered or cancelled, is_expired is False
    order.status = OrderStatus.DELIVERED
    assert order.is_expired is False


def test_store_schedule_all_branches():
    tz = pytz.timezone(settings.STORE_TIMEZONE)

    # 1. Domingo
    sun_dt = datetime(2026, 11, 1, 14, 0, tzinfo=tz)  # Domingo 14:00
    st_sun = settings.get_store_schedule_status(sun_dt)
    assert st_sun["is_open"] is False
    assert st_sun["is_sunday"] is True
    assert "domingo" in st_sun["short_notice"].lower()

    # 2. Segunda-feira antes da abertura (07:30)
    mon_early = datetime(2026, 11, 2, 7, 30, tzinfo=tz)
    st_early = settings.get_store_schedule_status(mon_early)
    assert st_early["is_open"] is False
    assert "abre hoje" in st_early["reopen_desc"].lower()

    # 3. Terça-feira durante o expediente (14:00)
    tue_open = datetime(2026, 11, 3, 14, 0, tzinfo=tz)
    st_open = settings.get_store_schedule_status(tue_open)
    assert st_open["is_open"] is True

    # 4. Quarta-feira após o fechamento (19:00)
    wed_late = datetime(2026, 11, 4, 19, 0, tzinfo=tz)
    st_late = settings.get_store_schedule_status(wed_late)
    assert st_late["is_open"] is False
    assert "abre amanhã" in st_late["short_notice"].lower()

    # 5. Sexta-feira após o fechamento (18:30 -> reabre sábado)
    fri_late = datetime(2026, 11, 6, 18, 30, tzinfo=tz)
    st_fri = settings.get_store_schedule_status(fri_late)
    assert st_fri["is_open"] is False
    assert "sábado" in st_fri["reopen_desc"].lower()

    # 6. Sábado após o fechamento (13:30 -> reabre segunda)
    sat_late = datetime(2026, 11, 7, 13, 30, tzinfo=tz)
    st_sat = settings.get_store_schedule_status(sat_late)
    assert st_sat["is_open"] is False
    assert "segunda" in st_sat["reopen_desc"].lower()


def test_staff_phone_list_clean():
    phones = settings.get_staff_phone_list()
    assert isinstance(phones, list)
    assert len(phones) >= 1
    assert all(p.isdigit() for p in phones)
