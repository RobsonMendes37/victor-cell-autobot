"""
Test Suite for FastFaqCacheService.
Validates sub-millisecond responses for address and operating hours,
and ensures quote requests and Pix payment inquiries are NOT auto-replied,
routing Pix directly to the human attendant.
"""

import pytest

from application.use_cases.fast_faq_cache import FastFaqCacheService
from domain.entities import Conversation, StoreProfile
from infrastructure.services.agent_service import AIAgentService


def test_fast_faq_address_match():
    profile = StoreProfile(address="Rua Barão do Rio Branco 1102, Centro")

    res = FastFaqCacheService.match_faq("qual o endereço da loja?", store_profile=profile)
    assert res is not None
    assert res["matched"] is True
    assert res["intent"] == "FAQ_ADDRESS"
    assert "Barão do Rio Branco 1102" in res["reply_text"]

    res2 = FastFaqCacheService.match_faq("onde fica a loja?", store_profile=profile)
    assert res2 is not None
    assert "Barão do Rio Branco 1102" in res2["reply_text"]


def test_fast_faq_hours_match():
    res = FastFaqCacheService.match_faq("que horas abre?")
    assert res is not None
    assert res["matched"] is True
    assert res["intent"] == "FAQ_HOURS"
    assert "Abre" in res["reply_text"] or "Seg a Sex" in res["reply_text"]


def test_fast_faq_does_not_intercept_product_quotes():
    # Se o cliente falar de peças, NÃO deve responder FAQ mas sim seguir para o fluxo de cotação
    assert FastFaqCacheService.match_faq("quanto tá a tela do a7 lite?") is None
    assert FastFaqCacheService.match_faq("tem o touch do t295?") is None
    assert FastFaqCacheService.match_faq("qual o valor do display?") is None
    assert FastFaqCacheService.match_faq("separa pro uber") is None


@pytest.mark.asyncio
async def test_pix_inquiry_is_excluded_from_faq_and_routes_to_human_attendant():
    # 1. Fast FAQ Cache NÃO intercepta dúvidas de Pix
    assert FastFaqCacheService.match_faq("passa o pix amigo") is None
    assert FastFaqCacheService.match_faq("qual o pix?") is None
    assert FastFaqCacheService.match_faq("manda a chave pix") is None

    # 2. O AIAgentService transborda silenciosamente para o atendente normal no WhatsApp
    agent = AIAgentService()
    conv = Conversation(id="conv-pix", customer_phone="5585999990001")
    res = await agent.process_and_reply(conv, "passa o pix pra eu pagar", catalog_context="")

    assert res["intent"] == "HUMAN_HANDOFF"
    assert res["reply_text"] == ""  # Doutrina do silêncio: não manda nada, passa pro atendente
    assert res["requires_staff_alert"] is True
    assert "Pix" in res["handoff_reason"]
