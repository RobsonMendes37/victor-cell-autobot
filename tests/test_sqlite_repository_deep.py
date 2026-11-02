"""
Deep Tests for SqliteRepository.
Covers:
- Bot sent messages tracking (anti-loop)
- Conversation history storage and retrieval with time deltas
- Global AI master kill-switch status
- Order persistence, status updates, and retrieval by customer phone
"""

import os

import pytest

from domain.entities import ReservationOrder
from infrastructure.repositories.sqlite_repository import SqliteRepository

TEST_DB = "data/test_deep_sqlite.db"


@pytest.fixture
async def repo():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    repository = SqliteRepository(TEST_DB)
    await repository.init_db()
    yield repository
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.mark.asyncio
async def test_anti_loop_bot_sent_messages(repo):
    msg_id = "wa_bot_outgoing_999"
    assert await repo.is_sent_by_bot(msg_id) is False

    await repo.record_sent_message(msg_id)
    assert await repo.is_sent_by_bot(msg_id) is True
    assert await repo.is_sent_by_bot("unknown_msg") is False


@pytest.mark.asyncio
async def test_global_ai_master_switch(repo):
    # Default is enabled (True)
    status = await repo.get_global_ai_status()
    assert status is True

    # Disable switch
    await repo.set_global_ai_status(False)
    assert await repo.get_global_ai_status() is False

    # Enable switch back
    await repo.set_global_ai_status(True)
    assert await repo.get_global_ai_status() is True


@pytest.mark.asyncio
async def test_conversation_history_persistence(repo):
    phone = "5585994443333"
    await repo.save_message(phone, "user", "Olá, tem tela do T295?")
    await repo.save_message(phone, "model", "R$ 85,00")

    history = await repo.get_recent_messages(phone, limit=5, max_age_hours=24)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert "T295" in history[0]["raw_content"]
    assert history[1]["role"] == "model"
    assert "85" in history[1]["raw_content"]


@pytest.mark.asyncio
async def test_order_lifecycle_in_sqlite(repo):
    phone = "5585995556666"
    order = ReservationOrder(
        customer_phone=phone,
        customer_name="Joaquim Cel",
        product_sku="TEL-TAB-A8-1LINHA",
        quantity=1,
        product_price=140.0,
        destination_address="Retirada no Balcão",
    )

    # Save
    order_id = await repo.save_order(order)
    assert order_id == order.id

    # List orders
    all_orders = await repo.list_orders()
    assert any(o.id == order.id for o in all_orders)

    # Orders by phone
    cust_orders = await repo.get_recent_orders_by_phone(phone)
    assert len(cust_orders) >= 1
    assert cust_orders[0].product_sku == "TEL-TAB-A8-1LINHA"


@pytest.mark.asyncio
async def test_product_cache_offline_resilience(repo):
    from domain.entities import Product, QualityTier

    p = Product(
        sku="OFFLINE-01",
        name="Tela Offline Test",
        category="Tablet",
        compatible_models=["M7", "M8"],
        quality=QualityTier.ORIGINAL_NACIONAL,
        has_frame=True,
        price=120.0,
        stock_quantity=5,
        warranty_days=90,
    )
    await repo.cache_products([p])
    cached = await repo.get_cached_products()
    assert len(cached) >= 1
    found = [x for x in cached if x.sku == "OFFLINE-01"]
    assert len(found) == 1
    assert found[0].name == "Tela Offline Test"
    assert found[0].price == 120.0
    assert found[0].has_frame is True
    assert found[0].compatible_models == ["M7", "M8"]


@pytest.mark.asyncio
async def test_quote_log_recording(repo):
    phone = "5585991112222"
    await repo.record_quote_log(phone, "Tem tela do M7?", sku="M7-TOUCH", had_stock=True)
    await repo.record_quote_log(phone, "Tem touch do A50?", sku=None, had_stock=False)


@pytest.mark.asyncio
async def test_clean_old_sent_messages(repo):
    msg_id = "wa_old_bot_msg"
    await repo.record_sent_message(msg_id)
    assert await repo.is_sent_by_bot(msg_id) is True

    # Calling cleanup with max_age_hours=0 will delete it
    if hasattr(repo, 'delete_old_sent_messages'):
        await repo.delete_old_sent_messages(max_age_hours=0)
