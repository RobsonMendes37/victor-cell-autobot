"""
Deep Unit & Integration Tests for:
1. AI File Import (CognitiveStockEntryUseCase.parse_file_stock_entry)
2. Confirmation & Batch Google Sheets Ingestion (confirm_file_import)
3. GoogleSheetsRepository append_product & append_products_batch
4. Corporate Blue & White Palette endpoints & Tenant Branding
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from application.use_cases.cognitive_stock_entry import CognitiveStockEntryUseCase
from domain.entities import Product, QualityTier
from infrastructure.config import settings
from infrastructure.inventory.memory_adapter import MemoryInventoryAdapter
from infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository
from presentation.api import SESSION_COOKIE_NAME, app, create_session_token


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def auth_cookies():
    token = create_session_token(settings.DASHBOARD_USERNAME, settings.DASHBOARD_SECRET_KEY)
    return {SESSION_COOKIE_NAME: token}


@pytest.mark.asyncio
async def test_parse_file_stock_entry_heuristic():
    """Validates heuristic parsing for CSV text when Gemini is offline."""
    inventory = MemoryInventoryAdapter()
    use_case = CognitiveStockEntryUseCase(inventory_provider=inventory, ai_client=None)

    csv_data = (
        "SKU;Modelo;Quantidade;Custo;Preco\n"
        "TEL-A15;Tela Samsung Galaxy A15 4G;10;85.00;145.00\n"
        "BAT-IP11;Bateria iPhone 11;5;60.00;120.00\n"
    )

    proposal = await use_case.parse_file_stock_entry(
        file_content=csv_data,
        filename="nota_teste.csv",
        mime_type="text/csv",
        operator_name="TEST_OPERATOR",
    )

    assert proposal["status"] == "AWAITING_CONFIRMATION"
    assert proposal["source"] == "FILE_IMPORT_AI"
    assert proposal["filename"] == "nota_teste.csv"
    assert len(proposal["items"]) >= 2
    assert "ai_questions" in proposal
    assert len(proposal["ai_questions"]) >= 1
    assert proposal["sync_to_sheets"] is True


@pytest.mark.asyncio
async def test_parse_file_stock_entry_with_mocked_gemini():
    """Validates AI extraction when Gemini responds with structured JSON."""
    inventory = MemoryInventoryAdapter()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '''{
      "supplier_name": "Mega Peças SP",
      "invoice_number": "NF-9988",
      "batch_number": "LOTE-20261102",
      "summary": "Extração de 2 peças de alto giro",
      "ai_questions": [
        {"id": "q1", "question": "Garantia de 90 dias confirmada?", "default_answer": "SIM", "type": "boolean"}
      ],
      "items": [
        {
          "model_name": "Tela Samsung Galaxy S23",
          "category": "Tela Frontal",
          "quality": "ORIGINAL_NACIONAL",
          "quantity": 4,
          "unit_cost": 320.0,
          "suggested_price": 540.0
        }
      ]
    }'''
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)

    use_case = CognitiveStockEntryUseCase(inventory_provider=inventory, ai_client=mock_client)
    proposal = await use_case.parse_file_stock_entry(
        file_content="Texto de nota fiscal qualquer...",
        filename="danfe.pdf",
        mime_type="application/pdf",
        operator_name="GESTOR",
    )

    assert proposal["supplier_name"] == "Mega Peças SP"
    assert proposal["invoice_number"] == "NF-9988"
    assert len(proposal["items"]) == 1
    assert proposal["items"][0]["model_name"] == "Tela Samsung Galaxy S23"
    assert proposal["items"][0]["quantity"] == 4
    assert proposal["ai_questions"][0]["question"] == "Garantia de 90 dias confirmada?"


@pytest.mark.asyncio
async def test_google_sheets_repository_append_product_and_batch():
    """Tests that append_product and append_products_batch update cache and return success."""
    repo = GoogleSheetsRepository(sheet_id="mock_test_sheet")
    prod = Product(
        sku="TEL-TEST-01",
        name="Tela de Teste Unitario",
        category="Tela Frontal",
        compatible_models=["Test Model"],
        quality=QualityTier.ORIGINAL_NACIONAL,
        has_frame=True,
        price=150.0,
        stock_quantity=10,
        warranty_days=90,
        cost_price=80.0,
    )

    res = await repo.append_product(prod)
    assert res is True
    assert "TEL-TEST-01" in repo._cached_products

    prod2 = Product(
        sku="BAT-TEST-02",
        name="Bateria de Teste",
        category="Bateria",
        compatible_models=["Test Bat"],
        quality=QualityTier.PRIMEIRA_LINHA,
        has_frame=False,
        price=80.0,
        stock_quantity=15,
        warranty_days=90,
        cost_price=40.0,
    )
    count = await repo.append_products_batch([prod, prod2])
    assert count == 2
    assert "BAT-TEST-02" in repo._cached_products


@pytest.mark.asyncio
async def test_api_import_file_ai_endpoint(auth_cookies):
    """Tests the /api/erp/stock/import-file-ai endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", cookies=auth_cookies) as ac:
        payload = {
            "file_content": "10 Telas Tab A8 a 110 por 180\n5 Baterias iPhone 11 a 60 por 120",
            "filename": "cotacao.txt",
            "mime_type": "text/plain",
            "operator_name": "TESTE",
        }
        res = await ac.post("/api/erp/stock/import-file-ai", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert "proposal_id" in data
        assert len(data["items"]) >= 1
        assert "ai_questions" in data


@pytest.mark.asyncio
async def test_api_confirm_file_import_endpoint(auth_cookies):
    """Tests the /api/erp/stock/confirm-file-import endpoint with Google Sheets sync."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", cookies=auth_cookies) as ac:
        proposal = {
            "proposal_id": "test_prop_123",
            "source": "FILE_IMPORT_AI",
            "operator_name": "BALCAO",
            "supplier_name": "Distribuidora Master",
            "invoice_number": "NF-5050",
            "batch_number": "LOTE-UNIT-01",
            "items": [
                {
                    "sku": "TEST-IMPORT-SKU-01",
                    "model_name": "Tela Frontal Teste Importação",
                    "category": "Tela Frontal",
                    "quality": "ORIGINAL_NACIONAL",
                    "quantity": 5,
                    "unit_cost": 75.0,
                    "suggested_price": 130.0,
                }
            ],
            "total_items": 1,
            "total_units": 5,
            "total_cost": 375.0,
        }

        req = {
            "proposal": proposal,
            "sync_to_sheets": True,
            "operator_name": "BALCAO",
        }

        res = await ac.post("/api/erp/stock/confirm-file-import", json=req)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "processed_items" in data
        assert "sheets_synced" in data


@pytest.mark.asyncio
async def test_tenant_palette_config_persistence(auth_cookies):
    """Tests updating and reading executive color palette configuration."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", cookies=auth_cookies) as ac:
        # 1. Get current config
        get_res = await ac.get("/api/tenant/config")
        assert get_res.status_code == 200
        cfg = get_res.json()
        assert "theme" in cfg

        # 2. Update with ERP Blue executive preset
        cfg["theme"]["primary_color"] = "#1E40AF"
        cfg["theme"]["secondary_color"] = "#2563EB"
        post_res = await ac.post("/api/tenant/config", json=cfg)
        assert post_res.status_code == 200

        # 3. Verify updated config
        get_res2 = await ac.get("/api/tenant/config")
        data2 = get_res2.json()
        assert data2["theme"]["primary_color"] == "#1E40AF"
        assert data2["theme"]["secondary_color"] == "#2563EB"

