"""
Repository Interfaces (Inversion of Control).
Domain layer does not know if data comes from Google Sheets, Postgres or SQLite.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from domain.entities import (
    Conversation,
    Product,
    QualityTier,
    ReservationOrder,
)


class ProductRepositoryInterface(ABC):
    @abstractmethod
    async def list_all(self) -> List[Product]:
        """Returns all products in catalog."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        quality: Optional[QualityTier] = None,
        has_frame: Optional[bool] = None,
    ) -> List[Product]:
        """Searches products by model or name with optional quality/frame filter."""
        pass

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Fetches a specific product by unique SKU."""
        pass

    @abstractmethod
    async def update_stock(self, sku: str, new_quantity: int) -> bool:
        """Updates stock quantity for a product."""
        pass

    @abstractmethod
    async def decrement_stock(self, sku: str, quantity: int = 1) -> bool:
        """Deducts reserved quantity from available stock."""
        pass

    @abstractmethod
    async def increment_stock(self, sku: str, quantity: int = 1) -> bool:
        """Restores quantity back to stock (e.g. expired/cancelled reservation)."""
        pass


class ConversationRepositoryInterface(ABC):
    @abstractmethod
    async def get_or_create(self, customer_phone: str) -> Conversation:
        """Fetches active conversation session or creates a new one."""
        pass

    @abstractmethod
    async def save(self, conversation: Conversation) -> None:
        """Persists state changes of a conversation."""
        pass

    @abstractmethod
    async def save_message(self, customer_phone: str, role: str, content: str) -> None:
        """Saves a message turn to conversation history."""
        pass

    @abstractmethod
    async def get_recent_messages(
        self, customer_phone: str, limit: int = 15, max_age_hours: int = 48
    ) -> List[Dict[str, str]]:
        """Retrieves recent conversation turns for multi-turn context."""
        pass


class OrderRepositoryInterface(ABC):
    @abstractmethod
    async def save_order(self, order: ReservationOrder) -> str:
        """Saves a new reservation order and returns the generated order ID."""
        pass

    @abstractmethod
    async def list_orders(self) -> List[ReservationOrder]:
        """Lists existing orders."""
        pass

    @abstractmethod
    async def get_recent_orders_by_phone(
        self, customer_phone: str, limit: int = 3
    ) -> List[ReservationOrder]:
        """Retrieves recent orders by customer phone for tracking context."""
        pass
