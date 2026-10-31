"""
Integration and Use Case Tests for Victor Cell PecasBot.
Covers:
- Context Memory & Multi-turn history
- Stock deduction upon order creation
- Anti-loop protection for bot echoes
- Owner human takeover & resume
"""

import pytest

from domain.entities import ConversationState, OrderStatus


@pytest.mark.asyncio
async def test_quote_sets_active_sku_and_saves_history(use_case, test_sqlite):
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

    # Verifica se gravou no histórico multi-turn
    history = await test_sqlite.get_recent_messages(phone)
    assert len(history) >= 2  # Mensagem do user + resposta do model
    assert history[0]["role"] == "user"
    assert "A15" in history[0]["content"]
    assert history[1]["role"] == "model"


@pytest.mark.asyncio
async def test_order_deducts_stock_and_uses_active_sku(use_case, test_sqlite, product_repo):
    """
    Testa se o pedido deduz o estoque disponível da peça
    e se associa corretamente à peça ativa discutida.
    """
    phone = "5585991113333"

    # Estoque inicial da Tela A15 Original: 4
    prod_before = await product_repo.get_by_sku("TEL-SAM-A15-ORIG")
    initial_stock = prod_before.stock_quantity
    assert initial_stock == 4

    # 1. Cotação
    await use_case.execute(
        customer_phone=phone,
        message_text="Quanto tá a tela do A15 original?",
        from_me=False,
    )

    # 2. Envio do endereço (Bot pede confirmação explícita antes de gerar pedido)
    res_pending = await use_case.execute(
        customer_phone=phone,
        message_text="Pode separar essa! Manda o Uber pra Rua Floriano Peixoto, 1250 - Centro",
        from_me=False,
    )
    assert res_pending["status"] == "SUCCESS"
    assert res_pending["intent"] == "ORDER_PENDING_CONFIRMATION"
    assert res_pending["order_created"] is False

    # 3. Confirmação explícita do cliente
    res = await use_case.execute(
        customer_phone=phone,
        message_text="Pode confirmar sim, patrão!",
        from_me=False,
    )
    assert res["status"] == "SUCCESS"
    assert res["order_created"] is True
    assert res["target_sku"] == "TEL-SAM-A15-ORIG"

    # Verifica se o estoque diminuiu exatamente em 1 unidade
    prod_after = await product_repo.get_by_sku("TEL-SAM-A15-ORIG")
    assert prod_after.stock_quantity == initial_stock - 1 == 3

    # Verifica se o pedido foi gravado
    orders = await test_sqlite.list_orders()
    assert len(orders) >= 1
    latest = orders[0]
    assert latest.product_sku == "TEL-SAM-A15-ORIG"
    assert latest.status == OrderStatus.PENDING_SEPARATION


@pytest.mark.asyncio
async def test_bot_echo_does_not_pause_ai_bug_fix(use_case, test_sqlite):
    """
    Quando a Evolution API emite o eco da mensagem enviada pelo bot,
    a IA não deve se auto-silenciar.
    """
    phone = "5585991114444"
    bot_msg_id = "bot_echo_msg_999"

    await test_sqlite.record_sent_message(bot_msg_id)

    res = await use_case.execute(
        customer_phone=phone,
        message_text="Opa meu amigo, temos sim!",
        from_me=True,
        message_id=bot_msg_id,
    )

    assert res["status"] == "SKIPPED_BOT_ECHO"
    conv = await test_sqlite.get_or_create(phone)
    assert conv.state == ConversationState.AI_ACTIVE


@pytest.mark.asyncio
async def test_human_owner_message_pauses_ai(use_case, test_sqlite):
    """
    Quando o dono da loja digita do celular pessoal, a IA é pausada por 3 horas.
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
        customer_phone=phone,
        message_text="#bot pode assumir",
        from_me=True,
    )
    assert res["status"] == "AI_RESUMED"
    conv_after = await test_sqlite.get_or_create(phone)
    assert conv_after.state == ConversationState.AI_ACTIVE


@pytest.mark.asyncio
async def test_inactivity_resets_context_and_prevents_stale_orders(use_case, test_sqlite):
    """
    Testa se o silêncio de mais de 2 horas expira o contexto da sessão,
    limpa a peça ativa e impede que uma mensagem aleatória após 2 horas
    seja interpretada como confirmação de pedido pendente.
    """
    from datetime import datetime, timezone, timedelta
    phone = "5585991117777"

    # 1. Cotação
    await use_case.execute(
        customer_phone=phone,
        message_text="Quanto tá a tela do A15 original?",
        from_me=False,
    )
    conv = await test_sqlite.get_or_create(phone)
    assert conv.active_sku == "TEL-SAM-A15-ORIG"

    # 2. Simula passagem do tempo de 3 horas de inatividade na conversa e no histórico
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    conv.last_activity_at = datetime.fromisoformat(past_iso)
    conv.state = ConversationState.WAITING_CONFIRMATION
    conv.notes = "Rua Teste, 100"
    await test_sqlite.save(conv)
    import aiosqlite
    async with aiosqlite.connect(test_sqlite.db_path) as db:
        await db.execute("UPDATE messages SET timestamp = ? WHERE customer_phone = ?", (past_iso, phone))
        await db.commit()

    # 3. Cliente reaparece 3 horas depois dizendo apenas "Beleza"
    res = await use_case.execute(
        customer_phone=phone,
        message_text="Beleza amigo",
        from_me=False,
    )

    # 4. Verifica que NÃO gerou pedido falso e a sessão foi resetada
    assert res["status"] == "SUCCESS"
    assert res["order_created"] is False

    conv_after = await test_sqlite.get_or_create(phone)
    assert conv_after.active_sku is None
    assert conv_after.notes is None

    # Histórico recente com corte de 2 horas não traz as mensagens de 3h atrás
    recent_in_window = await test_sqlite.get_recent_messages(phone, max_age_hours=2)
    # Apenas a mensagem de agora e a resposta do modelo (2 itens)
    assert len(recent_in_window) == 2
    assert "Beleza amigo" in recent_in_window[0]["content"]
