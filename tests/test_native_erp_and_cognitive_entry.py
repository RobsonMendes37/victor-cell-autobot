import os
import tempfile

import pytest
from starlette.testclient import TestClient

from application.use_cases.cognitive_stock_entry import CognitiveStockEntryUseCase
from domain.entities import MovementType, StockMovement, Supplier
from infrastructure.config import settings
from infrastructure.inventory.native_erp_adapter import NativeErpInventoryAdapter
from infrastructure.repositories.sqlite_repository import SqliteRepository
from presentation.api import app, create_session_token


@pytest.fixture
def temp_sqlite_repo():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    repo = SqliteRepository(db_path=db_path)
    yield repo
    if os.path.exists(db_path):
        os.remove(db_path)


def test_supplier_lgpd_masking():
    # Valida conformidade com a LGPD (Lei 13.709/2018)
    sup_cpf = Supplier(name="Técnico João", document="12345678901")
    assert sup_cpf.masked_document == "***.456.789-**"

    sup_cnpj = Supplier(name="Distribuidora Peças LTDA", document="12345678000199")
    assert sup_cnpj.masked_document == "12.***.***/0001-**"

    sup_empty = Supplier(name="Sem Doc", document=None)
    assert sup_empty.masked_document == ""


@pytest.mark.asyncio
async def test_native_erp_adapter_lifecycle(temp_sqlite_repo):
    adapter = NativeErpInventoryAdapter(repository=temp_sqlite_repo)

    # 1. Lista produtos (semeia catálogo padrão de bancada)
    products = await adapter.list_all()
    assert len(products) > 0
    sku = products[0].sku

    # 2. Busca por SKU
    p = await adapter.get_by_sku(sku)
    assert p is not None
    initial_stock = p.stock_quantity

    # 3. Incremento e Decremento
    await adapter.increment_stock(sku, 5)
    p_after_inc = await adapter.get_by_sku(sku)
    assert p_after_inc is not None
    assert p_after_inc.stock_quantity == initial_stock + 5

    await adapter.decrement_stock(sku, 2)
    p_after_dec = await adapter.get_by_sku(sku)
    assert p_after_dec is not None
    assert p_after_dec.stock_quantity == initial_stock + 3

    # 4. Fornecedor
    sup = Supplier(name="Fornecedor Central", document="11222333000144", phone="85999998888")
    saved = await adapter.save_supplier(sup)
    assert saved is True
    sups = await adapter.list_suppliers()
    assert len(sups) == 1
    assert sups[0].name == "Fornecedor Central"

    # 5. Registro de Movimentação de Entrada
    mov = StockMovement(
        sku=sku,
        movement_type=MovementType.ENTRADA_COMPRA,
        quantity=10,
        unit_cost=80.0,
        unit_price=150.0,
        invoice_number="NF-9988",
        operator_name="BALCAO_TEST",
    )
    rec = await adapter.record_movement(mov)
    assert rec is True

    # Valida que o estoque subiu em 10
    p_final = await adapter.get_by_sku(sku)
    assert p_final is not None
    assert p_final.stock_quantity == initial_stock + 13

    # Lista movimentações
    movs = await adapter.list_movements(sku=sku)
    assert len(movs) >= 1
    assert movs[0].invoice_number == "NF-9988"

    # Métricas
    metrics = await adapter.get_inventory_metrics()
    assert metrics["total_skus"] > 0
    assert metrics["total_units"] > 0
    assert metrics["total_cost_value"] > 0


@pytest.mark.asyncio
async def test_cognitive_stock_entry_use_case(temp_sqlite_repo):
    adapter = NativeErpInventoryAdapter(repository=temp_sqlite_repo)
    use_case = CognitiveStockEntryUseCase(
        inventory_provider=adapter,
        ai_client=None,  # Testa fallback determinístico
        audit_repo=temp_sqlite_repo,
    )

    # 1. Simula entrada por voz
    audio_text = "Entraram 5 telas do Tab A8 a 110 e 2 conectores do T295 a 15 do fornecedor Peças Brasil, NF 1234"
    proposal = await use_case.parse_voice_stock_entry(audio_content=audio_text, operator_name="MARCOS_BALCAO")

    assert proposal["status"] == "AWAITING_CONFIRMATION"
    assert proposal["source"] == "VOICE"
    assert len(proposal["items"]) > 0
    assert proposal["total_units"] > 0

    # 2. Confirmação da entrada de estoque
    res = await use_case.confirm_stock_entry(proposal=proposal, operator_name="MARCOS_BALCAO")
    assert res["status"] == "SUCCESS"
    assert res["processed_items"] > 0

    # 3. Valida extrato de movimentações geradas
    movements = await adapter.list_movements()
    assert len(movements) >= 1

    # 4. Valida trilha de auditoria e-Gov
    audit_logs = await temp_sqlite_repo.list_audit_logs()
    inflow_logs = [log for log in audit_logs if log.action == "STOCK_INFLOW"]
    assert len(inflow_logs) == 1
    assert inflow_logs[0].actor == "MARCOS_BALCAO"


def test_erp_api_endpoints():
    client = TestClient(app)
    token = create_session_token("admin", settings.DASHBOARD_SECRET_KEY)
    client.cookies.set("victor_session", token)

    # 1. Resumo do estoque ERP
    res_summary = client.get("/api/erp/stock/summary")
    assert res_summary.status_code == 200
    data_summary = res_summary.json()
    assert "total_skus" in data_summary
    assert "total_units" in data_summary

    # 2. Entrada por Voz
    res_voice = client.post(
        "/api/erp/stock/voice-entry",
        json={"audio_content": "Chegou 4 telas do Galaxy A15 a 120 reais", "operator_name": "TESTE_API"},
    )
    assert res_voice.status_code == 200
    proposal = res_voice.json()
    assert proposal["status"] == "AWAITING_CONFIRMATION"
    assert len(proposal["items"]) > 0

    # 3. Confirmação da Entrada
    res_confirm = client.post(
        "/api/erp/stock/confirm-entry",
        json={"proposal": proposal, "operator_name": "TESTE_API"},
    )
    assert res_confirm.status_code == 200
    assert res_confirm.json()["status"] == "SUCCESS"

    # 4. Listagem de Movimentações
    res_movs = client.get("/api/erp/stock/movements")
    assert res_movs.status_code == 200
    assert isinstance(res_movs.json(), list)

    # 5. Cadastro e Listagem de Fornecedores com LGPD
    res_sup_post = client.post(
        "/api/erp/suppliers",
        json={
            "name": "Fornecedor Teste API",
            "document": "12345678000199",
            "phone": "85999990000",
            "notes": "Parceiro Oficial",
        },
    )
    assert res_sup_post.status_code == 200
    assert res_sup_post.json()["status"] == "SUCCESS"

    res_sup_list = client.get("/api/erp/suppliers")
    assert res_sup_list.status_code == 200
    sups = res_sup_list.json()
    assert len(sups) >= 1
    # Valida que o documento veio mascarado conforme a LGPD
    assert sups[0]["masked_document"] != ""
