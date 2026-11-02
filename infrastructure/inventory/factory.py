"""
Inventory Provider Factory.
Instantiates and configures the appropriate inventory provider based on application settings.
"""

import os
import logging
from typing import Optional
from infrastructure.inventory.base import InventoryProvider
from infrastructure.inventory.cached_proxy import CachedInventoryProxy
from infrastructure.inventory.google_sheets_adapter import GoogleSheetsInventoryAdapter
from infrastructure.inventory.bling_v3_adapter import BlingV3InventoryAdapter
from infrastructure.inventory.memory_adapter import MemoryInventoryAdapter

logger = logging.getLogger(__name__)


def create_inventory_provider(
    provider_name: Optional[str] = None,
    enable_cache: bool = True,
    cache_ttl_seconds: int = 300,
) -> InventoryProvider:
    """
    Factory that instantiates the active inventory provider.
    Supported providers:
    - 'GOOGLE_SHEETS': Google Sheets integration via API key or service account.
    - 'BLING_V3': Bling ERP v3 REST API & Webhooks.
    - 'MEMORY': In-memory catalog for testing, development, and offline mode.
    """
    from infrastructure.config import settings

    target = (provider_name or getattr(settings, 'INVENTORY_PROVIDER', 'GOOGLE_SHEETS')).upper()
    logger.info(f"[InventoryFactory] Inicializando provedor de estoque: '{target}'")

    provider: InventoryProvider

    if target == "BLING_V3" or target == "BLING":
        client_id = getattr(settings, 'BLING_CLIENT_ID', None) or os.getenv('BLING_CLIENT_ID')
        client_secret = getattr(settings, 'BLING_CLIENT_SECRET', None) or os.getenv('BLING_CLIENT_SECRET')
        access_token = getattr(settings, 'BLING_ACCESS_TOKEN', None) or os.getenv('BLING_ACCESS_TOKEN')
        refresh_token = getattr(settings, 'BLING_REFRESH_TOKEN', None) or os.getenv('BLING_REFRESH_TOKEN')

        provider = BlingV3InventoryAdapter(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    elif target == "MEMORY" or target == "TEST":
        provider = MemoryInventoryAdapter()

    else:
        # Default: Google Sheets
        provider = GoogleSheetsInventoryAdapter()

    # Wrap in high-speed cached proxy
    if enable_cache:
        return CachedInventoryProxy(target_provider=provider, ttl_seconds=cache_ttl_seconds)

    return provider
