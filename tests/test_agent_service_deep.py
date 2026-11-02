"""
Deep Tests for AIAgentService (infrastructure/services/agent_service.py).
Covers:
- Address extraction regex
- Semantic fallback decision engine (Smartphones out-of-scope, Human handoff, Uber dispatch, Quotations)
- Store schedule prompt injection
- Copilot consultation
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from domain.entities import Conversation, ConversationState
from infrastructure.services.agent_service import AIAgentService


def test_extract_real_address():
    svc = AIAgentService()

    # Valid addresses
    addr1 = svc._extract_real_address("Pode mandar o Uber pra Rua Floriano Peixoto, 1250 - Centro")
    assert addr1 is not None
    assert "Rua Floriano Peixoto" in addr1

    addr2 = svc._extract_real_address("Entrega na Av. Bezerra de Menezes, 300")
    assert addr2 is not None
    assert "Av. Bezerra" in addr2

    # No address
    addr_none = svc._extract_real_address("Quanto custa a tela?")
    assert addr_none is None


def test_semantic_fallback_smartphone_out_of_scope():
    svc = AIAgentService()
    conv = Conversation(id="c1", customer_phone="5585991112222")

    res = svc._semantic_fallback("Tem tela de celular iPhone 11?", conv)
    assert res["intent"] == "GENERAL_QUESTION"
    assert "Só peças de tablet" in res["reply_text"]
    assert res["target_sku"] is None


def test_semantic_fallback_human_handoff():
    svc = AIAgentService()
    conv = Conversation(id="c2", customer_phone="5585991112222")

    res = svc._semantic_fallback("Vocês consertam placa em curto?", conv)
    assert res["intent"] == "HUMAN_HANDOFF"
    assert res["reply_text"] == ""  # Regra de Ouro: silêncio total para o cliente
    assert res["requires_staff_alert"] is True


def test_semantic_fallback_order_confirmation():
    svc = AIAgentService()
    conv = Conversation(
        id="c3",
        customer_phone="5585991112222",
        state=ConversationState.WAITING_CONFIRMATION,
        active_sku="TEL-TAB-A8-1LINHA",
        notes="Rua Floriano Peixoto, 100",
    )

    res = svc._semantic_fallback("Pode confirmar sim, patrão!", conv)
    assert res["intent"] == "ORDER_DISPATCH"
    assert res["requires_staff_alert"] is True


@pytest.mark.asyncio
async def test_ask_copilot_fallback():
    svc = AIAgentService()
    # When client is offline or throws, returns fallback copilot analysis
    with patch.object(svc, "_client", None):
        res = await svc.ask_copilot("Como estão as vendas de tela hoje?", operational_context="Faturamento: R$ 380,00, Pedidos: 2")
        assert isinstance(res, str)
        assert len(res) > 20


def test_semantic_fallback_quoting_variations():
    svc = AIAgentService()
    conv = Conversation(id="c_quotes", customer_phone="5585991113333")

    # M10A
    res_m10a = svc._semantic_fallback("Quanto é a tela do m10a?", conv)
    assert res_m10a["intent"] == "QUOTE"
    assert res_m10a["target_sku"] == "TOU-MUL-M10A"

    # A15 original
    res_a15_orig = svc._semantic_fallback("Tem tela do A15 original com aro?", conv)
    assert res_a15_orig["target_sku"] == "TEL-SAM-A15-ORIG"

    # A15 paralela
    res_a15_chin = svc._semantic_fallback("Tem tela do A15 paralela china?", conv)
    assert res_a15_chin["target_sku"] == "TEL-SAM-A15-CHIN"

    # Tab A8 tela e conector
    res_tab_con = svc._semantic_fallback("Tem conector de carga do Tab A8?", conv)
    assert res_tab_con["target_sku"] == "CON-TAB-A8-ORIG"

    res_tab_tela = svc._semantic_fallback("Tem a tela do x200 Tab A8?", conv)
    assert res_tab_tela["target_sku"] == "TEL-TAB-A8-1LINHA"


def test_semantic_fallback_uber_only_and_compliments():
    svc = AIAgentService()
    conv = Conversation(id="c_misc", customer_phone="5585991113333", active_sku="T2040-TOUCH")

    # Uber only
    res_uber = svc._semantic_fallback("Qual o valor do frete uber?", conv)
    assert res_uber["intent"] == "GENERAL_QUESTION"
    assert "endereço" in res_uber["reply_text"].lower()

    # Compliment
    res_comp = svc._semantic_fallback("Valeu meu amigo, show de bola tmj", conv)
    assert res_comp["intent"] == "GENERAL_QUESTION"
    assert "valeu" in res_comp["reply_text"].lower()


def test_semantic_fallback_order_intent_address_and_no_sku():
    svc = AIAgentService()
    # No active sku, asks to separate
    conv_no_sku = Conversation(id="c_nosku", customer_phone="5585991113333")
    res_no_sku = svc._semantic_fallback("Separa aí pra mim", conv_no_sku)
    assert res_no_sku["intent"] == "GENERAL_QUESTION"
    assert "qual peça" in res_no_sku["reply_text"].lower()

    # With active sku and address
    conv_with_sku = Conversation(id="c_sku", customer_phone="5585991113333", active_sku="TEL-TAB-A8-1LINHA")
    res_order_addr = svc._semantic_fallback("Manda entregar na Rua Floriano Peixoto 1250 Centro", conv_with_sku)
    assert res_order_addr["intent"] == "ORDER_PENDING_CONFIRMATION"
    assert res_order_addr["destination_address"] is not None
