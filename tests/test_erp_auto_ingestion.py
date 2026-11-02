"""
Test Suite for ERP Webhook Auto-Ingestion.
Validates that new products received via Bling v3 webhook are automatically ingested
into the active catalog mirror and can be queried immediately.
"""

import pytest

from domain.entities import QualityTier
from infrastructure.inventory.bling_v3_adapter import BlingV3InventoryAdapter
from infrastructure.inventory.memory_adapter import MemoryInventoryAdapter


@pytest.mark.asyncio
async def test_bling_auto_ingests_new_product_from_webhook():
    adapter = BlingV3InventoryAdapter()

    # Webhook payload do Bling v3 com peça nova inexistente no catálogo
    payload = {
        "evento": "estoque.alterado",
        "retorno": {
            "idProduto": 998877,
            "codigo": "DISP-TAB-A9-X110-ORIG",
            "descricao": "Tela Frontal Samsung Tab A9 X110 Original Nacional com aro",
            "saldo": 7,
            "preco": 240.0,
        },
    }

    # Verifica que não existia antes
    assert await adapter.get_by_sku("DISP-TAB-A9-X110-ORIG") is None

    # Processa o webhook
    handled = await adapter.handle_stock_webhook(payload)
    assert handled is True

    # Verifica se foi auto-ingerido com os dados corretos
    product = await adapter.get_by_sku("DISP-TAB-A9-X110-ORIG")
    assert product is not None
    assert product.sku == "DISP-TAB-A9-X110-ORIG"
    assert product.name == "Tela Frontal Samsung Tab A9 X110 Original Nacional com aro"
    assert product.stock_quantity == 7
    assert product.price == 240.0
    assert product.quality == QualityTier.ORIGINAL_NACIONAL
    assert product.has_frame is True
    assert product.has_stock is True


@pytest.mark.asyncio
async def test_memory_adapter_auto_ingests_and_updates_stock():
    adapter = MemoryInventoryAdapter()

    # 1. Ingestão de produto novo
    new_item_payload = {
        "retorno": {
            "codigo": "TOUCH-ML-M8-4G",
            "descricao": "Touch Tablet Multilaser M8 4G",
            "saldo": 15,
            "preco": 50.0,
        }
    }
    handled = await adapter.handle_stock_webhook(new_item_payload)
    assert handled is True
    p = await adapter.get_by_sku("TOUCH-ML-M8-4G")
    assert p is not None
    assert p.stock_quantity == 15

    # 2. Atualização subsequente de estoque do mesmo item
    update_payload = {
        "retorno": {
            "codigo": "TOUCH-ML-M8-4G",
            "saldo": 12,
        }
    }
    handled_update = await adapter.handle_stock_webhook(update_payload)
    assert handled_update is True
    p_updated = await adapter.get_by_sku("TOUCH-ML-M8-4G")
    assert p_updated is not None
    assert p_updated.stock_quantity == 12
