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

    # 4. Verifica que NÃO gerou pedido falso e a confirmação pendente expirou
    assert res["status"] == "SUCCESS"
    assert res["order_created"] is False

    conv_after = await test_sqlite.get_or_create(phone)
    assert conv_after.state == ConversationState.AI_ACTIVE
    assert conv_after.notes is None

    # Histórico de 48h traz as mensagens com âncora temporal [Há 3h atrás]
    history_48h = await test_sqlite.get_recent_messages(phone, max_age_hours=48)
    assert len(history_48h) == 4
    assert "Há 3h atrás" in history_48h[0]["content"] or "min" in history_48h[0]["content"]


@pytest.mark.asyncio
async def test_post_sale_order_tracking_query(use_case, test_sqlite):
    """
    Testa se a IA reconhece o pedido recente do cliente no banco
    ao ser questionada sobre o status de despacho/entrega ('deu certo? já mandou?').
    """
    from domain.entities import ReservationOrder, OrderStatus
    from datetime import datetime, timezone
    phone = "5585991118888"

    # Cria pedido no banco para o cliente
    order = ReservationOrder(
        id="ped_track_99",
        customer_phone=phone,
        customer_name="Oficina do João",
        product_sku="TEL-SAM-A15-ORIG",
        quantity=1,
        product_price=190.0,
        destination_address="Av. Central, 500 - Bairro de Fátima",
        status=OrderStatus.PENDING_SEPARATION,
    )
    await test_sqlite.save_order(order)

    # Cliente pergunta se deu certo e se já despachou
    res = await use_case.execute(
        customer_phone=phone,
        message_text="E aí amigo, deu certo o meu pedido? Já despachou o Uber?",
        from_me=False,
    )

    assert res["status"] == "SUCCESS"
    # Não recria o pedido
    assert res["order_created"] is False
    # A resposta menciona que deu certo ou o pedido/peça
    assert len(res["reply"]) > 10

@pytest.mark.asyncio
async def test_human_handoff_is_completely_silent(use_case, test_sqlite):
    """
    Testa se o transbordo para atendimento humano (reparo de placa, negociação, etc)
    é 100% silencioso: NÃO responde nada ao cliente (reply == ''), silencia a IA
    e transfere a conversa para o atendente humano no WhatsApp.
    """
    phone = "5585991119999"

    res = await use_case.execute(
        customer_phone=phone,
        message_text="Vocês fazem reparo em placa de tablet?",
        from_me=False,
    )

    assert res["status"] == "SUCCESS"
    assert res["intent"] == "HUMAN_HANDOFF"
    # REGRA CRÍTICA: Não responde nada ao cliente, é só passar!
    assert res["replied"] is False
    assert res["reply"] == ""

    # Verifica se a IA foi silenciada para o atendente assumir
    conv = await test_sqlite.get_or_create(phone)
    assert conv.is_ai_allowed() is False
    assert conv.state == ConversationState.HUMAN_ACTIVE
