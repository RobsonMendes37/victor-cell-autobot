"""
In-Memory Conversation & Order Repository.
Keeps conversation session state and orders for lightweight unit tests.
"""

import uuid
from typing import Dict, List

from domain.entities import Conversation, ConversationState, ReservationOrder
from domain.repositories import ConversationRepositoryInterface, OrderRepositoryInterface


class MemoryConversationRepository(ConversationRepositoryInterface):
    def __init__(self) -> None:
        self._conversations: Dict[str, Conversation] = {}
        self._messages: Dict[str, List[Dict[str, str]]] = {}

    async def get_or_create(self, customer_phone: str) -> Conversation:
        if customer_phone not in self._conversations:
            self._conversations[customer_phone] = Conversation(
                id=str(uuid.uuid4()),
                customer_phone=customer_phone,
                state=ConversationState.AI_ACTIVE,
            )
        return self._conversations[customer_phone]

    async def save(self, conversation: Conversation) -> None:
        self._conversations[conversation.customer_phone] = conversation

    save_conversation = save

    async def save_message(self, customer_phone: str, role: str, content: str) -> None:
        if customer_phone not in self._messages:
            self._messages[customer_phone] = []
        self._messages[customer_phone].append({"role": role, "content": content})

    async def get_recent_messages(
        self, customer_phone: str, limit: int = 15, max_age_hours: int = 48
    ) -> List[Dict[str, str]]:
        msgs = self._messages.get(customer_phone, [])
        return msgs[-limit:]


class MemoryOrderRepository(OrderRepositoryInterface):
    def __init__(self) -> None:
        self._orders: Dict[str, ReservationOrder] = {}

    async def save_order(self, order: ReservationOrder) -> str:
        self._orders[order.id] = order
        return order.id

    async def list_orders(self) -> List[ReservationOrder]:
        return list(self._orders.values())

    async def get_recent_orders_by_phone(
        self, customer_phone: str, limit: int = 3
    ) -> List[ReservationOrder]:
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        matching = [
            o for o in self._orders.values()
            if "".join(filter(str.isdigit, o.customer_phone)) == clean_phone
        ]
        return matching[-limit:]
