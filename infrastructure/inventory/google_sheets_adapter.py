"""
Google Sheets Inventory Adapter.
Adapts the existing GoogleSheetsRepository into the unified InventoryProvider interface.
"""

import logging
from typing import Any, Dict, List, Optional
from domain.entities import Product, QualityTier
from infrastructure.repositories.google_sheets_repository import GoogleSheetsRepository
from infrastructure.inventory.base import InventoryProvider

logger = logging.getLogger(__name__)


class GoogleSheetsInventoryAdapter(InventoryProvider):
    """
    Adapter for Google Sheets spreadsheet inventory.
    Useful for small repair shops or stores that maintain their price list in Google Sheets.
    """

    def __init__(self, sheets_repo: Optional[GoogleSheetsRepository] = None):
        self.repo = sheets_repo or GoogleSheetsRepository()

    def get_provider_name(self) -> str:
        return "Google Sheets (Spreadsheet Sync)"

    async def health_check(self) -> Dict[str, Any]:
        try:
            prods = await self.repo.list_all()
            return {
                "status": "UP" if prods else "DEGRADED",
                "provider": self.get_provider_name(),
                "total_items": len(prods),
            }
        except Exception as e:
            return {"status": "DOWN", "provider": self.get_provider_name(), "error": str(e)}

    async def list_all(self) -> List[Product]:
        return await self.repo.list_all()

    async def search(
        self,
        query: str,
        quality: Optional[QualityTier] = None,
        has_frame: Optional[bool] = None,
    ) -> List[Product]:
        return await self.repo.search(query, quality, has_frame)

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        return await self.repo.get_by_sku(sku)

    async def update_stock(self, sku: str, new_quantity: int) -> bool:
        return await self.repo.update_stock(sku, new_quantity)

    async def decrement_stock(self, sku: str, quantity: int = 1) -> bool:
        return await self.repo.decrement_stock(sku, quantity)

    async def increment_stock(self, sku: str, quantity: int = 1) -> bool:
        return await self.repo.increment_stock(sku, quantity)

    async def sync_catalog(self) -> int:
        if hasattr(self.repo, '_last_cache_update'):
            self.repo._last_cache_update = None
        prods = await self.repo.list_all()
        return len(prods)
