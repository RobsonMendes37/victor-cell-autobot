"""
In-Memory Product Repository with Stock Control and Reservation Expiration.
Implements ProductRepositoryInterface.
"""

from datetime import datetime, timezone
from typing import List, Optional

from domain.entities import OrderStatus, Product, QualityTier, ReservationOrder
from domain.repositories import ProductRepositoryInterface


class MemoryProductRepository(ProductRepositoryInterface):
    def __init__(self):
        self._products: dict[str, Product] = {}
        self._seed_default_catalog()

    def _seed_default_catalog(self) -> None:
        """Seeds typical tablet and phone parts for instant testing."""
        sample_items = [
            Product(
                sku="TEL-SAM-A15-ORIG",
                name="Tela Frontal Samsung Galaxy A15",
                category="Tela Frontal",
                compatible_models=["Galaxy A15", "A15 4G", "A15 5G", "SM-A155F", "SM-A156B"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=True,
                price=190.00,
                stock_quantity=4,
                warranty_days=90,
            ),
            Product(
                sku="TEL-SAM-A15-CHIN",
                name="Tela Frontal Samsung Galaxy A15",
                category="Tela Frontal",
                compatible_models=["Galaxy A15", "A15 4G", "A15 5G", "SM-A155F", "SM-A156B"],
                quality=QualityTier.PARALELA_CHINA,
                has_frame=False,
                price=95.00,
                stock_quantity=12,
                warranty_days=30,
            ),
            Product(
                sku="TEL-TAB-A8-1LINHA",
                name="Tela Frontal Samsung Tab A8 10.5",
                category="Tela Frontal",
                compatible_models=["Tab A8", "SM-X200", "SM-X205"],
                quality=QualityTier.PRIMEIRA_LINHA,
                has_frame=False,
                price=140.00,
                stock_quantity=3,
                warranty_days=60,
            ),
            Product(
                sku="CON-TAB-A8-ORIG",
                name="Conector de Carga Placa Sub Tab A8",
                category="Conector de Carga",
                compatible_models=["Tab A8", "SM-X200", "SM-X205"],
                quality=QualityTier.PRIMEIRA_LINHA,
                has_frame=False,
                price=25.00,
                stock_quantity=15,
                warranty_days=90,
            ),
            Product(
                sku="BAT-SAM-A15-ORIG",
                name="Bateria Samsung Galaxy A15",
                category="Bateria",
                compatible_models=["Galaxy A15", "A15 4G", "A15 5G"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=False,
                price=110.00,
                stock_quantity=5,
                warranty_days=90,
            ),
        ]
        for p in sample_items:
            self._products[p.sku] = p

    async def list_all(self) -> List[Product]:
        return list(self._products.values())

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        return self._products.get(sku)

    async def search(
        self,
        query: str,
        quality: Optional[QualityTier] = None,
        has_frame: Optional[bool] = None,
    ) -> List[Product]:
        q = query.lower().strip()
        matches = []
        for p in self._products.values():
            name_match = q in p.name.lower()
            model_match = any(q in m.lower() for m in p.compatible_models)
            category_match = q in p.category.lower()

            if name_match or model_match or category_match:
                if quality and p.quality != quality:
                    continue
                if has_frame is not None and p.has_frame != has_frame:
                    continue
                matches.append(p)
        return matches

    async def update_stock(self, sku: str, new_quantity: int) -> bool:
        if sku in self._products:
            self._products[sku].stock_quantity = new_quantity
            self._products[sku].last_updated_at = datetime.now(timezone.utc)
            return True
        return False

    async def decrement_stock(self, sku: str, quantity: int = 1) -> bool:
        """Decrements available stock when an item is reserved."""
        if sku in self._products:
            current = self._products[sku].stock_quantity
            if current >= quantity:
                self._products[sku].stock_quantity = current - quantity
                self._products[sku].last_updated_at = datetime.now(timezone.utc)
                return True
        return False

    async def increment_stock(self, sku: str, quantity: int = 1) -> bool:
        """Restores stock when a reservation is cancelled or expired."""
        if sku in self._products:
            self._products[sku].stock_quantity += quantity
            self._products[sku].last_updated_at = datetime.now(timezone.utc)
            return True
        return False

    async def release_expired_orders(self, orders: List[ReservationOrder]) -> List[str]:
        """Scans for expired orders and restores stock."""
        released_ids = []
        for o in orders:
            if o.status == OrderStatus.PENDING_SEPARATION and o.is_expired:
                o.status = OrderStatus.EXPIRED
                await self.increment_stock(o.product_sku, o.quantity)
                released_ids.append(o.id)
        return released_ids
