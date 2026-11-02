# Native ERP Inventory Adapter
import logging
from typing import List, Optional

from domain.entities import MovementType, Product, QualityTier, StockMovement, Supplier
from infrastructure.inventory.base import InventoryProvider
from infrastructure.inventory.memory_adapter import MemoryInventoryAdapter
from infrastructure.repositories.sqlite_repository import SqliteRepository

logger = logging.getLogger("NativeErpAdapter")


class NativeErpInventoryAdapter(InventoryProvider):
    """
    Enterprise Native ERP Provider.
    Implements InventoryProvider directly on relational database with full compliance.
    """

    def __init__(self, repository: Optional[SqliteRepository] = None):
        self.repo = repository or SqliteRepository()
        self._seeded = False

    def get_provider_name(self) -> str:
        return "Native ERP (Relational DB)"

    async def _ensure_seeded(self) -> None:
        if self._seeded:
            return
        prods = await self.repo.list_native_products()
        if not prods:
            logger.info("[NativeErpAdapter] Banco de dados vazio. Semeando catálogo padrão de bancada...")
            seed = MemoryInventoryAdapter()._products.values()
            for p in seed:
                await self.repo.save_native_product(p)
        self._seeded = True

    async def list_all(self) -> List[Product]:
        await self._ensure_seeded()
        return await self.repo.list_native_products()

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        await self._ensure_seeded()
        return await self.repo.get_native_product(sku)

    async def search(
        self,
        query: str,
        quality: Optional[QualityTier] = None,
        has_frame: Optional[bool] = None,
    ) -> List[Product]:
        products = await self.list_all()
        q = query.lower().strip()
        matches = []
        for p in products:
            if q in p.name.lower() or any(q in m.lower() for m in p.compatible_models) or q in p.sku.lower():
                if quality and p.quality != quality:
                    continue
                if has_frame is not None and p.has_frame != has_frame:
                    continue
                matches.append(p)
        return matches

    async def update_stock(self, sku: str, new_quantity: int) -> bool:
        await self._ensure_seeded()
        return await self.repo.update_native_stock(sku, new_quantity)

    async def decrement_stock(self, sku: str, quantity: int = 1) -> bool:
        await self._ensure_seeded()
        return await self.repo.decrement_native_stock(sku, quantity)

    async def increment_stock(self, sku: str, quantity: int = 1) -> bool:
        await self._ensure_seeded()
        return await self.repo.increment_native_stock(sku, quantity)

    async def register_product(self, product: Product) -> bool:
        await self._ensure_seeded()
        return await self.repo.save_native_product(product)

    async def record_movement(self, movement: StockMovement) -> bool:
        await self._ensure_seeded()
        success = await self.repo.record_stock_movement(movement)
        if not success:
            return False

        if movement.movement_type in (MovementType.ENTRADA_COMPRA, MovementType.ENTRADA_DEVOLUCAO):
            await self.increment_stock(movement.sku, movement.quantity)
        elif movement.movement_type in (MovementType.SAIDA_VENDA, MovementType.SAIDA_AVARIA):
            await self.decrement_stock(movement.sku, movement.quantity)
        elif movement.movement_type == MovementType.AJUSTE_BALANCO:
            await self.update_stock(movement.sku, movement.quantity)

        logger.info(
            f"[NativeErpAdapter] Movimentação registrada: {movement.movement_type.value} | "
            f"SKU: {movement.sku} | Qtd: {movement.quantity} | Operador: {movement.operator_name}"
        )
        return True

    async def list_movements(self, sku: Optional[str] = None, limit: int = 50) -> List[StockMovement]:
        await self._ensure_seeded()
        return await self.repo.list_stock_movements(sku=sku, limit=limit)

    async def list_suppliers(self) -> List[Supplier]:
        await self._ensure_seeded()
        return await self.repo.list_suppliers()

    async def save_supplier(self, supplier: Supplier) -> bool:
        await self._ensure_seeded()
        return await self.repo.save_supplier(supplier)
