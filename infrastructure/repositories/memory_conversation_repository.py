"""
In-Memory Conversation & Order Repository.
Keeps conversation session state and orders.
"""

import uuid
from typing import Dict

from domain.entities import Conversation, ConversationState, ReservationOrder
from domain.repositories import ConversationRepositoryInterface, OrderRepositoryInterface


class MemoryConversationRepository(ConversationRepositoryInterface):
    def __init__(self):
        self._conversations: Dict[str, Conversation] = {}

    async def get_or_create(self, customer_phone: str) -> Conversation:
        if customer_phone not in self._conversations:
            self._conversations[customer_phone] = Conversation(
                id=str(uuid.uuid4()),
                customer_phone=customer_phone,
                state=ConversationState.AI_ACTIVE
            )
        return self._conversations[customer_phone]

    async def save(self, conversation: Conversation) -> None:
        self._conversations[conversation.customer_phone] = conversation


class MemoryOrderRepository(OrderRepositoryInterface):
    def __init__(self):
        self._orders: Dict[str, ReservationOrder] = {}

    async def save_order(self, order: ReservationOrder) -> str:
        self._orders[order.id] = order
        return order.id

    def list_orders(self) -> list[ReservationOrder]:
        return list(self._orders.values())
