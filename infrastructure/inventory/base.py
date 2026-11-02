"""
Pluggable Inventory Provider Base (Ports & Adapters Pattern).
Defines the contract that any ERP (Bling, Tiny, Omie, Sheets, Postgres) must implement.
"""

from abc import abstractmethod
from typing import Any, Dict

from domain.repositories import ProductRepositoryInterface


class InventoryProvider(ProductRepositoryInterface):
    """
    Enterprise Port for Inventory Operations.
    Inherits from ProductRepositoryInterface and adds enterprise features:
    - Real-time stock reservation with TTL
    - Webhook event handling for stock adjustments
    - Periodic cache synchronization
    - Provider health check and circuit breaking
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the identifier name of this inventory provider (e.g. 'Bling v3', 'Google Sheets')."""
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Verifies if the connection to the ERP/Stock source is healthy."""
        return {"status": "UP", "provider": self.get_provider_name()}

    async def reserve_stock(
        self,
        sku: str,
        quantity: int,
        order_id: str,
        ttl_seconds: int = 7200,
    ) -> bool:
        """
        Reserves available stock for a pending customer order with an automatic lease timeout (default 2 hours).
        Default implementation calls decrement_stock, but ERP adapters can call native reservation endpoints.
        """
        return await self.decrement_stock(sku, quantity)

    async def release_reservation(self, order_id: str, sku: str, quantity: int = 1) -> bool:
        """Restores reserved stock back to available inventory (e.g. timeout or cancelled pickup)."""
        return await self.increment_stock(sku, quantity)

    async def handle_stock_webhook(self, payload: Dict[str, Any]) -> bool:
        """
        Handles an incoming webhook from the ERP (e.g. Bling stock adjustment event).
        Returns True if the event was successfully ingested.
        """
        return False

    async def sync_catalog(self) -> int:
        """Forces a full refresh of the catalog from the upstream ERP into local memory/cache."""
        products = await self.list_all()
        return len(products)
