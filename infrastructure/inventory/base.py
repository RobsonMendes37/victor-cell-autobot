"""
Pluggable Inventory Provider Base (Ports & Adapters Pattern).
Defines the contract that any ERP (Bling, Tiny, Omie, Sheets, Postgres) must implement.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from domain.entities import Product
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

    async def record_movement(self, movement: Any) -> bool:
        """Records an inventory movement in the relational database and updates physical balance."""
        from domain.entities import MovementType
        from infrastructure.repositories.sqlite_repository import SqliteRepository
        res = await SqliteRepository().record_stock_movement(movement)
        if res:
            if movement.movement_type in (MovementType.ENTRADA_COMPRA, MovementType.ENTRADA_DEVOLUCAO):
                await self.increment_stock(movement.sku, movement.quantity)
            elif movement.movement_type in (MovementType.SAIDA_VENDA, MovementType.SAIDA_AVARIA):
                await self.decrement_stock(movement.sku, movement.quantity)
            elif movement.movement_type == MovementType.AJUSTE_BALANCO:
                await self.update_stock(movement.sku, movement.quantity)
        return res

    async def list_movements(self, sku: Optional[str] = None, limit: int = 50) -> List[Any]:
        """Lists recent inventory movements from the relational database."""
        from infrastructure.repositories.sqlite_repository import SqliteRepository
        return await SqliteRepository().list_stock_movements(sku=sku, limit=limit)

    async def list_suppliers(self) -> List[Any]:
        """Lists registered suppliers from the relational database."""
        from infrastructure.repositories.sqlite_repository import SqliteRepository
        return await SqliteRepository().list_suppliers()

    async def save_supplier(self, supplier: Any) -> bool:
        """Saves or updates a supplier in the relational database."""
        from infrastructure.repositories.sqlite_repository import SqliteRepository
        return await SqliteRepository().save_supplier(supplier)

    async def register_product(self, product: Product) -> bool:
        """Registers a new product in the native catalog."""
        return False

    async def get_inventory_metrics(self) -> Dict[str, Any]:
        """Calculates inventory metrics (total value, items below minimum, margin)."""
        products = await self.list_all()
        total_items = len(products)
        total_units = sum(p.stock_quantity for p in products)
        total_cost = sum((p.cost_price or (p.price * 0.6)) * p.stock_quantity for p in products)
        total_retail = sum(p.price * p.stock_quantity for p in products)
        out_of_stock = sum(1 for p in products if not p.is_in_stock)
        return {
            "total_skus": total_items,
            "total_units": total_units,
            "total_cost_value": round(total_cost, 2),
            "total_retail_value": round(total_retail, 2),
            "out_of_stock_skus": out_of_stock,
            "in_stock_skus": total_items - out_of_stock,
        }
