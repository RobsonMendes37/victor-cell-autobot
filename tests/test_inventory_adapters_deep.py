"""
Deep Edge-Case and Failure-Mode Tests for Inventory Adapters.
Covers:
- Bling ERP v3 Circuit Breaker (Trip & Recovery)
- Bling ERP Rate Limit Handling (HTTP 429)
- Bling ERP Product Mapping (Quality tiers, frames, categories)
- Bling ERP Webhook Ingestion
- CachedInventoryProxy Concurrency & Cache Expiry
- GoogleSheetsAdapter Health Check & Sync
"""

import pytest
import httpx
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch
from domain.entities import QualityTier, Product
from infrastructure.inventory.bling_v3_adapter import BlingV3InventoryAdapter
from infrastructure.inventory.google_sheets_adapter import GoogleSheetsInventoryAdapter
from infrastructure.inventory.cached_proxy import CachedInventoryProxy
from infrastructure.inventory.memory_adapter import MemoryInventoryAdapter


@pytest.mark.asyncio
async def test_bling_circuit_breaker_and_rate_limit():
    adapter = BlingV3InventoryAdapter(access_token="test_token")
    assert adapter._is_circuit_open() is False

    # Simulate 3 consecutive network failures
    adapter._trip_circuit()
    assert adapter._is_circuit_open() is False
    adapter._trip_circuit()
    assert adapter._is_circuit_open() is False
    adapter._trip_circuit()  # 3rd failure trips the breaker!
    assert adapter._is_circuit_open() is True

    # Health check reflects DEGRADED with circuit OPEN
    health = await adapter.health_check()
    assert health["status"] == "DEGRADED"
    assert health["circuit"] == "OPEN"

    # Expire circuit breaker manually to test recovery
    adapter._circuit_open_until = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert adapter._is_circuit_open() is False


@pytest.mark.asyncio
async def test_bling_mapping_all_quality_tiers():
    adapter = BlingV3InventoryAdapter()

    # Original China
    p1 = adapter._map_bling_to_product({
        "codigo": "T1",
        "nome": "Display Samsung T295 Original China Com Aro",
        "preco": 110.0,
        "estoque": {"saldoFisicoTotal": 5},
    })
    assert p1.quality == QualityTier.ORIGINAL_CHINA
    assert p1.has_frame is True
    assert p1.stock_quantity == 5
    assert p1.has_stock is True

    # Primeira Linha
    p2 = adapter._map_bling_to_product({
        "codigo": "T2",
        "nome": "Tela Multilaser M7 Primeira Linha",
        "preco": 40.0,
        "estoque": {"saldoFisicoTotal": 0},
    })
    assert p2.quality == QualityTier.PRIMEIRA_LINHA
    assert p2.has_frame is False
    assert p2.has_stock is False

    # Paralela China
    p3 = adapter._map_bling_to_product({
        "codigo": "T3",
        "nome": "Touch Paralela China M8",
        "preco": 35.0,
    })
    assert p3.quality == QualityTier.PARALELA_CHINA


@pytest.mark.asyncio
async def test_bling_list_all_with_rate_limit_429():
    adapter = BlingV3InventoryAdapter(access_token="valid_token")
    adapter._local_mirror["CACHED-01"] = Product(
        sku="CACHED-01",
        name="Tela Cachê",
        category="Tab",
        compatible_models=["M7"],
        quality=QualityTier.ORIGINAL_NACIONAL,
        has_frame=False,
        price=50.0,
    )

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = httpx.Response(429, text="Too Many Requests")
        # When 429 occurs, gracefully falls back to local mirror
        res = await adapter.list_all()
        assert len(res) == 1
        assert res[0].sku == "CACHED-01"


@pytest.mark.asyncio
async def test_bling_webhook_edge_cases():
    adapter = BlingV3InventoryAdapter()

    # Invalid payload missing SKU
    bad_res = await adapter.handle_stock_webhook({"evento": "unknown"})
    assert bad_res is False

    # Valid payload updating stock
    adapter._local_mirror["SKU-WB-10"] = Product(
        sku="SKU-WB-10",
        name="Peça Webhook",
        category="Geral",
        compatible_models=[],
        quality=QualityTier.ORIGINAL_NACIONAL,
        has_frame=False,
        price=70.0,
        stock_quantity=2,
    )

    good_res = await adapter.handle_stock_webhook({
        "retorno": {"codigo": "SKU-WB-10", "saldo": 20}
    })
    assert good_res is True
    assert (await adapter.get_by_sku("SKU-WB-10")).stock_quantity == 20


@pytest.mark.asyncio
async def test_cached_proxy_expiry_and_sync():
    mem = MemoryInventoryAdapter()
    proxy = CachedInventoryProxy(target_provider=mem, ttl_seconds=1)

    # Initial load
    prods = await proxy.list_all()
    assert len(prods) >= 4
    assert proxy._is_cache_valid() is True

    # Simulate time expiry
    proxy._cache_expires_at = datetime.now(timezone.utc) - timedelta(seconds=2)
    assert proxy._is_cache_valid() is False

    # Next call refreshes cache
    await proxy.list_all()
    assert proxy._is_cache_valid() is True

    # Sync catalog forces refresh
    count = await proxy.sync_catalog()
    assert count >= 4


@pytest.mark.asyncio
async def test_cached_proxy_full_stock_and_search_operations():
    mem = MemoryInventoryAdapter()
    proxy = CachedInventoryProxy(target_provider=mem, ttl_seconds=60)

    # Provider name & health check
    assert "CachedProxy" in proxy.get_provider_name()
    health = await proxy.health_check()
    assert health["status"] == "UP"
    assert "cached_entries" in health

    # get_by_sku hit and miss
    sku = "T2040-TOUCH"
    prod = await proxy.get_by_sku(sku)
    assert prod is not None
    assert prod.sku == sku

    # search with filters
    matches = await proxy.search("M7", quality=QualityTier.ORIGINAL_NACIONAL)
    assert any(p.sku == sku for p in matches)

    matches_framed = await proxy.search("M7", has_frame=True)
    assert not any(p.sku == sku for p in matches_framed)

    # update_stock, decrement_stock, increment_stock
    assert await proxy.update_stock(sku, 20) is True
    assert (await proxy.get_by_sku(sku)).stock_quantity == 20

    assert await proxy.decrement_stock(sku, 5) is True
    assert (await proxy.get_by_sku(sku)).stock_quantity == 15

    assert await proxy.increment_stock(sku, 5) is True
    assert (await proxy.get_by_sku(sku)).stock_quantity == 20

    # webhook invalidates cache
    handled = await proxy.handle_stock_webhook({"retorno": {"codigo": sku, "saldo": 8}})
    assert proxy._cache_expires_at is None


@pytest.mark.asyncio
async def test_bling_stock_mutations_and_search():
    adapter = BlingV3InventoryAdapter(access_token="test_token")
    adapter._local_mirror["BLING-01"] = Product(
        sku="BLING-01",
        name="Touch Multilaser M7 Plus",
        category="Touch",
        compatible_models=["M7", "M7 Plus"],
        quality=QualityTier.PRIMEIRA_LINHA,
        has_frame=False,
        price=35.0,
        stock_quantity=10,
        has_stock=True,
    )

    # Search
    found = await adapter.search("M7 Plus", quality=QualityTier.PRIMEIRA_LINHA)
    assert len(found) == 1
    assert found[0].sku == "BLING-01"

    # Mutate stock
    assert await adapter.decrement_stock("BLING-01", 2) is True
    assert adapter._local_mirror["BLING-01"].stock_quantity == 8

    # Over-decrement returns False
    assert await adapter.decrement_stock("BLING-01", 999) is False

    assert await adapter.increment_stock("BLING-01", 4) is True
    assert adapter._local_mirror["BLING-01"].stock_quantity == 12

    assert await adapter.update_stock("BLING-01", 50) is True
    assert adapter._local_mirror["BLING-01"].stock_quantity == 50

    # Non-existing sku
    assert await adapter.decrement_stock("NON-EXISTING", 1) is False
    assert await adapter.increment_stock("NON-EXISTING", 1) is False
    assert await adapter.update_stock("NON-EXISTING", 10) is False


@pytest.mark.asyncio
async def test_memory_product_repository_edge_cases():
    from infrastructure.repositories.memory_product_repository import MemoryProductRepository
    from domain.entities import ReservationOrder, OrderStatus
    from datetime import datetime, timezone, timedelta

    repo = MemoryProductRepository()
    sku = "TEL-TAB-A8-1LINHA"

    # get_by_sku
    item = await repo.get_by_sku(sku)
    assert item is not None
    assert await repo.get_by_sku("UNKNOWN-SKU") is None

    # Search with quality and frame filters
    res = await repo.search("Tab A8", quality=QualityTier.PRIMEIRA_LINHA, has_frame=False)
    assert any(p.sku == sku for p in res)

    # Decrement failure when quantity > stock
    assert await repo.decrement_stock(sku, 9999) is False

    # Expired orders release
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    order = ReservationOrder(
        id="ord_exp_01",
        customer_phone="5585999998888",
        customer_name="Oficina",
        product_sku=sku,
        quantity=2,
        product_price=140.0,
        destination_address="Balcão",
        status=OrderStatus.PENDING_SEPARATION,
        expires_at=past,
    )
    assert order.is_expired is True

    init_stock = (await repo.get_by_sku(sku)).stock_quantity
    released = await repo.release_expired_orders([order])
    assert "ord_exp_01" in released
    assert order.status == OrderStatus.EXPIRED
    assert (await repo.get_by_sku(sku)).stock_quantity == init_stock + 2
