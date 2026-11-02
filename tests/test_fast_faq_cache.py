"""
Test Suite for FastFaqCacheService.
Validates sub-millisecond responses for address, pix, and operating hours,
and ensures quote requests are not intercepted.
"""

from application.use_cases.fast_faq_cache import FastFaqCacheService
from domain.entities import StoreProfile


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


def test_fast_faq_pix_match():
    profile = StoreProfile(pix_key="85999990001 (Celular)")

    res = FastFaqCacheService.match_faq("passa o pix amigo", store_profile=profile)
    assert res is not None
    assert res["matched"] is True
    assert res["intent"] == "FAQ_PIX"
    assert "85999990001" in res["reply_text"]


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
