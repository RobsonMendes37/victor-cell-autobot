"""
Unit Tests for the Pluggable Inventory Module (Ports & Adapters).
Verifies:
- Factory creation for all providers
- Cache-Aside / Read-Through decorator behavior
- Stock reservation and decrementing
- Bling ERP v3 mapping and webhook handling
"""

import pytest

from domain.entities import Product, QualityTier
from infrastructure.inventory.bling_v3_adapter import BlingV3InventoryAdapter
from infrastructure.inventory.cached_proxy import CachedInventoryProxy
from infrastructure.inventory.factory import create_inventory_provider
from infrastructure.inventory.memory_adapter import MemoryInventoryAdapter


@pytest.mark.asyncio
async def test_memory_adapter_crud_and_search():
    adapter = MemoryInventoryAdapter()
    assert "Memory" in adapter.get_provider_name()

    # List all
    prods = await adapter.list_all()
    assert len(prods) >= 4

    # Search
    results = await adapter.search("T2040")
    assert len(results) >= 1
    assert results[0].sku == "T2040-TOUCH"

    # Decrement stock
    before = (await adapter.get_by_sku("T2040-TOUCH")).stock_quantity
    ok = await adapter.decrement_stock("T2040-TOUCH", 2)
    assert ok is True
    after = (await adapter.get_by_sku("T2040-TOUCH")).stock_quantity
    assert after == before - 2

    # Increment back
    await adapter.increment_stock("T2040-TOUCH", 2)
    restored = (await adapter.get_by_sku("T2040-TOUCH")).stock_quantity
    assert restored == before


@pytest.mark.asyncio
async def test_cached_proxy_read_through():
    mem = MemoryInventoryAdapter()
    proxy = CachedInventoryProxy(target_provider=mem, ttl_seconds=60)

    # Cache initially empty
    assert len(proxy._cache) == 0

    # First call populates cache (Read-Through)
    prods = await proxy.list_all()
    assert len(prods) >= 4
    assert len(proxy._cache) >= 4

    # Direct query hits cache
    item = await proxy.get_by_sku("TEL-SAM-A15-ORIG")
    assert item is not None
    assert item.price == 190.0

    # Stock update syncs cache and target
    await proxy.update_stock("TEL-SAM-A15-ORIG", 15)
    assert (await proxy.get_by_sku("TEL-SAM-A15-ORIG")).stock_quantity == 15
    assert (await mem.get_by_sku("TEL-SAM-A15-ORIG")).stock_quantity == 15


@pytest.mark.asyncio
async def test_bling_v3_adapter_mapping_and_webhook():
    bling = BlingV3InventoryAdapter(access_token="mock_token")
    assert "Bling" in bling.get_provider_name()

    # Seed mock product
    bling._local_mirror["MOCK-T295"] = Product(
        sku="MOCK-T295",
        name="Tela Touch Tablet T295",
        category="Samsung",
        compatible_models=["T295"],
        quality=QualityTier.ORIGINAL_NACIONAL,
        has_frame=False,
        price=85.0,
        stock_quantity=10,
        has_stock=True,
    )

    # Ingest stock adjustment webhook from Bling
    webhook_payload = {
        "evento": "estoque.alterado",
        "retorno": {
            "codigo": "MOCK-T295",
            "saldo": 7,
        }
    }
    handled = await bling.handle_stock_webhook(webhook_payload)
    assert handled is True

    # Verify stock was updated
    prod = await bling.get_by_sku("MOCK-T295")
    assert prod is not None
    assert prod.stock_quantity == 7


@pytest.mark.asyncio
async def test_inventory_factory_resolution():
    p_mem = create_inventory_provider("MEMORY", enable_cache=True)
    assert isinstance(p_mem, CachedInventoryProxy)
    assert "Memory" in p_mem.get_provider_name()

    p_bling = create_inventory_provider("BLING_V3", enable_cache=False)
    assert isinstance(p_bling, BlingV3InventoryAdapter)

    p_sheets = create_inventory_provider("GOOGLE_SHEETS", enable_cache=False)
    assert "Google Sheets" in p_sheets.get_provider_name()
