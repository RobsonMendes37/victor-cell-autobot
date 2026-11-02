"""
Pluggable Inventory Module for Victor Cell (Ports & Adapters).
"""

from infrastructure.inventory.base import InventoryProvider
from infrastructure.inventory.cached_proxy import CachedInventoryProxy
from infrastructure.inventory.google_sheets_adapter import GoogleSheetsInventoryAdapter
from infrastructure.inventory.bling_v3_adapter import BlingV3InventoryAdapter
from infrastructure.inventory.memory_adapter import MemoryInventoryAdapter
from infrastructure.inventory.factory import create_inventory_provider

__all__ = [
    "InventoryProvider",
    "CachedInventoryProxy",
    "GoogleSheetsInventoryAdapter",
    "BlingV3InventoryAdapter",
    "MemoryInventoryAdapter",
    "create_inventory_provider",
]
