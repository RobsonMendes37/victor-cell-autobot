"""
Memory Inventory Adapter.
Fast, in-memory implementation seeded with the official Victor Cell catalog.
Ideal for development, staging, testing, and zero-dependency environments.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from domain.entities import Product, QualityTier
from infrastructure.inventory.base import InventoryProvider


class MemoryInventoryAdapter(InventoryProvider):
    def __init__(self, seed_products: Optional[List[Product]] = None):
        self._products: Dict[str, Product] = {}
        if seed_products:
            for p in seed_products:
                self._products[p.sku] = p
        else:
            self._seed_default_catalog()

    def get_provider_name(self) -> str:
        return "Memory (Fast In-Memory / Staging)"

    def _seed_default_catalog(self):
        """Catalogo oficial de bancada Victor Cell."""
        items = [
            Product(
                sku="TEL-SAM-A15-ORIG",
                name="Tela Samsung A15 Original Nacional",
                category="Samsung",
                compatible_models=["A15", "A155", "A156"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=True,
                price=190.0,
                stock_quantity=4,
                has_stock=True,
                location="Gaveta A1",
            ),
            Product(
                sku="T2040-TOUCH",
                name="Touch Tablet M7 3G Plus / T2040",
                category="Multilaser",
                compatible_models=["M7", "T2040", "M7 3G"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=False,
                price=45.0,
                stock_quantity=10,
                has_stock=True,
                location="Gaveta B2",
            ),
            Product(
                sku="T290-DISP-ORIG",
                name="Display LCD Tablet Samsung Galaxy Tab A 8.0 T290 / T295",
                category="Samsung",
                compatible_models=["T290", "T295", "Tab A 8.0"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=False,
                price=130.0,
                stock_quantity=3,
                has_stock=True,
                location="Gaveta C1",
            ),
            Product(
                sku="T290-TOUCH-ORIG",
                name="Touch Screen Tablet Samsung Galaxy Tab A 8.0 T290 / T295",
                category="Samsung",
                compatible_models=["T290", "T295"],
                quality=QualityTier.ORIGINAL_NACIONAL,
                has_frame=False,
                price=65.0,
                stock_quantity=5,
                has_stock=True,
                location="Gaveta C2",
            ),
        ]
        for p in items:
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
            if q in p.name.lower() or any(q in m.lower() for m in p.compatible_models) or q in p.sku.lower():
                if quality and p.quality != quality:
                    continue
                if has_frame is not None and p.has_frame != has_frame:
                    continue
                matches.append(p)
        return matches

    async def update_stock(self, sku: str, new_quantity: int) -> bool:
        if sku in self._products:
            self._products[sku].stock_quantity = new_quantity
            self._products[sku].has_stock = new_quantity > 0
            self._products[sku].last_updated_at = datetime.now(timezone.utc)
            return True
        return False

    async def decrement_stock(self, sku: str, quantity: int = 1) -> bool:
        if sku in self._products:
            current = self._products[sku].stock_quantity
            if current >= quantity:
                self._products[sku].stock_quantity = current - quantity
                self._products[sku].has_stock = self._products[sku].stock_quantity > 0
                return True
        return False

    async def increment_stock(self, sku: str, quantity: int = 1) -> bool:
        if sku in self._products:
            self._products[sku].stock_quantity += quantity
            self._products[sku].has_stock = True
            return True
        return False
