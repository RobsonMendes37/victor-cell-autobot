import os
import tempfile

import pytest
from starlette.testclient import TestClient

from application.use_cases.catalog_search_service import CatalogSearchService
from application.use_cases.cognitive_stock_entry import CognitiveStockEntryUseCase
from application.use_cases.fast_faq_cache import FastFaqCacheService
from domain.entities import (
    Conversation,
    ConversationState,
    MovementType,
    StockMovement,
    Supplier,
)
from infrastructure.inventory.native_erp_adapter import NativeErpInventoryAdapter
from infrastructure.repositories.sqlite_repository import SqliteRepository
from presentation.api import app


@pytest.fixture
def temp_sqlite_repo():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    repo = SqliteRepository(db_path=db_path)
    yield repo
    if os.path.exists(db_path):
        os.remove(db_path)


# =============================================================================
# 1. TESTES NEGATIVOS E DE BORDA: DOMÍNIO E LGPD
# =============================================================================

def test_supplier_lgpd_edge_cases():
    # Documento nulo
    s1 = Supplier(name="Sem Doc", document=None)
    assert s1.masked_document == ""

    # Documento vazio
    s2 = Supplier(name="Vazio", document="")
    assert s2.masked_document == ""

    # Documento com caracteres estranhos ou tamanho inesperado
    s3 = Supplier(name="Inválido", document="ABC-123")
    assert s3.masked_document == "***"

    s4 = Supplier(name="Tamanho 8", document="12345678")
    assert s4.masked_document == "***"


def test_conversation_reopen_boundaries():
    conv = Conversation(id="conv-edge", customer_phone="5585999990001")
    conv.pause_for_human(duration_hours=3)

    # 1. Estado CLOSED nunca permite IA
    conv.state = ConversationState.CLOSED
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="quanto tá a tela") is False

    # 2. Reabertura em loja fechada mesmo se pausado
    conv.state = ConversationState.HUMAN_ACTIVE
    assert conv.is_ai_allowed(is_store_open=False, incoming_message="quanto tá a tela") is True

    # 3. Loja aberta mas dentro da tolerância (<30min) com mensagem comum
    conv.pause_for_human(duration_hours=3)
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="bom dia amigo", grace_period_minutes=30) is False

    # 4. Mensagem sem termos de cotação após 30m -> permanece pausado
    import datetime
    conv.human_resumed_at = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=35)
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="beleza, obrigado", grace_period_minutes=30) is False

    # 5. Nova cotação após 30m -> reativa IA
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="quanto tá o touch do t295?", grace_period_minutes=30) is True
    assert conv.state == ConversationState.AI_ACTIVE


# =============================================================================
# 2. TESTES NEGATIVOS: ERP NATIVO E PROTEÇÃO CONTRA OVERDRAFT
# =============================================================================

@pytest.mark.asyncio
async def test_native_erp_overdraft_prevention(temp_sqlite_repo):
    adapter = NativeErpInventoryAdapter(repository=temp_sqlite_repo)
    products = await adapter.list_all()
    p = products[0]

    # Ajusta saldo para exatamente 2 unidades
    await adapter.update_stock(p.sku, 2)
    p_check = await adapter.get_by_sku(p.sku)
    assert p_check.stock_quantity == 2

    # Tenta decrementar 3 unidades (overdraft)
    success = await adapter.decrement_stock(p.sku, 3)
    assert success is False

    # Valida que o saldo não ficou negativo (-1) e permaneceu intacto em 2
    p_after = await adapter.get_by_sku(p.sku)
    assert p_after.stock_quantity == 2
    assert p_after.has_stock is True

    # Movimentação de saída maior que saldo não deve zerar saldo de forma inconsistente
    mov = StockMovement(
        sku=p.sku,
        movement_type=MovementType.SAIDA_AVARIA,
        quantity=5,  # Excede 2
        operator_name="TESTE_OVERDRAFT",
    )
    await adapter.record_movement(mov)
    # Operação de decremento falhou internamente
    p_final = await adapter.get_by_sku(p.sku)
    assert p_final.stock_quantity == 2


# =============================================================================
# 3. TESTES DE RESILIÊNCIA: BUSCA FUZZY E ENTRADAS MALFORMADAS
# =============================================================================

def test_catalog_search_malformed_and_injection():
    search_service = CatalogSearchService()

    # Injeção de SQL ou strings maliciosas
    res_sql = search_service.detect_model_alias("'; DROP TABLE cached_products; --")
    assert res_sql is None

    # String com caracteres especiais e espaços gigantes
    res_spaces = search_service.detect_model_alias("   ???!!!   ")
    assert res_spaces is None

    # Termo aleatório sem correspondência
    res_garbage = search_service.search_best_matches([], "xyz999qwerty")
    assert len(res_garbage) == 0


# =============================================================================
# 4. TESTES NEGATIVOS: FAST FAQ CACHE (PIX E COTAÇÕES MISTAS)
# =============================================================================

def test_fast_faq_cache_edge_cases():
    faq = FastFaqCacheService()

    # Pergunta de Pix NUNCA pode ser respondida pelo FAQ
    assert faq.match_faq("me passa a chave pix do balcão") is None
    assert faq.match_faq("qual o pix?") is None
    assert faq.match_faq("manda a chave pix") is None

    # Pergunta mista contendo endereço E cotação de peça -> não intercepta
    assert faq.match_faq("qual o endereço da loja e quanto tá a tela do a8?") is None
    assert faq.match_faq("onde fica e quanto custa a bateria?") is None

    # Pergunta de endereço pura -> responde instantaneamente
    reply_addr = faq.match_faq("onde fica a loja de vocês?")
    assert reply_addr is not None
    assert "Barão do Rio Branco" in reply_addr["reply_text"]


# =============================================================================
# 5. TESTES DE SEGURANÇA E AUTENTICAÇÃO (OWASP TOP 10)
# =============================================================================

def test_api_security_unauthorized_access():
    client = TestClient(app)

    # 1. Sem cookie de autenticação -> 401 Unauthorized
    assert client.get("/api/erp/stock/summary").status_code == 401
    assert client.get("/api/erp/stock/movements").status_code == 401
    assert client.get("/api/erp/suppliers").status_code == 401
    assert client.post("/api/erp/stock/voice-entry", json={"audio_content": "test"}).status_code == 401
    assert client.post("/api/erp/stock/confirm-entry", json={"proposal": {}}).status_code == 401

    # 2. Com cookie inválido/adulterado -> 401 Unauthorized
    client.cookies.set("victor_session", "admin:9999999999:fake_signature_hash")
    assert client.get("/api/erp/stock/summary").status_code == 401


# =============================================================================
# 6. TESTES NEGATIVOS: ENTRADA COGNITIVA MALFORMADA
# =============================================================================

@pytest.mark.asyncio
async def test_cognitive_stock_entry_empty_proposal(temp_sqlite_repo):
    adapter = NativeErpInventoryAdapter(repository=temp_sqlite_repo)
    use_case = CognitiveStockEntryUseCase(inventory_provider=adapter, audit_repo=temp_sqlite_repo)

    # Proposta vazia sem itens
    res = await use_case.confirm_stock_entry(proposal={"items": []})
    assert res["status"] == "ERROR"

    # Proposta com item sem SKU
    res_nosku = await use_case.confirm_stock_entry(proposal={"items": [{"model_name": "Incompleto"}]})
    assert res_nosku["status"] == "SUCCESS"
    assert res_nosku["processed_items"] == 0
