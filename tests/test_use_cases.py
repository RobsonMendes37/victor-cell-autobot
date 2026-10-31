"""
Integration and Use Case Tests.
Tests regressions for Bug 1 (Context Memory) and Bug 2 (Self-silencing).
"""

import pytest

from domain.entities import ConversationState


@pytest.mark.asyncio
async def test_quote_sets_active_sku(use_case, test_sqlite):
    phone = "5585991112222"
    res = await use_case.execute(
        customer_phone=phone,
        message_text="Opa, você tem a tela do A15 original com aro?",
        from_me=False,
        push_name="Oficina Alpha",
    )
    assert res["status"] == "SUCCESS"
    assert res["intent"] == "QUOTE"
    assert res["target_sku"] == "TEL-SAM-A15-ORIG"

    conv = await test_sqlite.get_or_create(phone)
    assert conv.active_sku == "TEL-SAM-A15-ORIG"


@pytest.mark.asyncio
async def test_order_uses_active_sku_context_bug_fix(use_case, test_sqlite):
    """
    BUG 1 REGRESSION TEST:
    Customer previously asked for A15. Then says "pode separar essa! Rua Floriano 1250".
    The order MUST be created for A15 Original, NOT Tab A8 connector!
    """
    phone = "5585991113333"

    # 1. Cotação do A15
    await use_case.execute(
        customer_phone=phone, message_text="Quanto tá a tela do A15 original?", from_me=False
    )

    # 2. Confirmação sem citar o nome da peça ("pode separar essa")
    res = await use_case.execute(
        customer_phone=phone,
        message_text="Pode separar essa! Manda o Uber pra Rua Floriano Peixoto, 1250 - Centro",
        from_me=False,
    )

    assert res["status"] == "SUCCESS"
    assert res["order_created"] is True
    assert res["target_sku"] == "TEL-SAM-A15-ORIG"

    orders = await test_sqlite.list_orders()
    assert len(orders) >= 1
    latest = orders[0]
    assert latest.product_sku == "TEL-SAM-A15-ORIG"
    assert latest.product_price == 190.00
    assert "Floriano Peixoto" in latest.destination_address


@pytest.mark.asyncio
async def test_bot_echo_does_not_pause_ai_bug_fix(use_case, test_sqlite):
    """
    BUG 2 REGRESSION TEST:
    When Evolution API emits an echo of the bot's own message with fromMe=true,
    the bot MUST NOT pause itself!
    """
    phone = "5585991114444"
    bot_msg_id = "bot_echo_msg_999"

    # Registra que o bot enviou uma mensagem com esse ID
    await test_sqlite.record_sent_message(bot_msg_id)

    # Webhook devolve o eco da mensagem própria
    res = await use_case.execute(
        customer_phone=phone,
        message_text="Opa meu amigo, temos sim!",
        from_me=True,
        message_id=bot_msg_id,
    )

    assert res["status"] == "SKIPPED_BOT_ECHO"
    conv = await test_sqlite.get_or_create(phone)
    assert conv.state == ConversationState.AI_ACTIVE  # Continuou ativa!


@pytest.mark.asyncio
async def test_human_owner_message_pauses_ai(use_case, test_sqlite):
    """
    When the real human owner types from their phone (not sent by bot),
    AI MUST be paused.
    """
    phone = "5585991115555"
    human_msg_id = "human_real_msg_888"

    res = await use_case.execute(
        customer_phone=phone,
        message_text="Oi Marcos, vou verificar aqui na prateleira",
        from_me=True,
        message_id=human_msg_id,
    )

    assert res["status"] == "PAUSED_BY_HUMAN_INTERVENTION"
    conv = await test_sqlite.get_or_create(phone)
    assert conv.state == ConversationState.HUMAN_ACTIVE
    assert conv.is_ai_allowed() is False


@pytest.mark.asyncio
async def test_manual_bot_resume(use_case, test_sqlite):
    phone = "5585991116666"
    conv = await test_sqlite.get_or_create(phone)
    conv.pause_for_human(duration_hours=3)
    await test_sqlite.save(conv)

    res = await use_case.execute(
        customer_phone=phone, message_text="#bot pode assumir", from_me=True
    )
    assert res["status"] == "AI_RESUMED"
    conv_after = await test_sqlite.get_or_create(phone)
    assert conv_after.state == ConversationState.AI_ACTIVE
