"""
Gateway Interfaces for external communication (Messaging, AI).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from domain.entities import Conversation


class MessagingGatewayInterface(ABC):
    @abstractmethod
    async def send_text(self, to_phone: str, text: str) -> bool:
        """Sends a text message via WhatsApp."""
        pass

    @abstractmethod
    async def send_internal_staff_alert(self, alert_text: str) -> bool:
        """Sends an urgent alert to the store cashier/dispatch team WhatsApp."""
        pass


class AIServiceInterface(ABC):
    @abstractmethod
    async def process_and_reply(
        self,
        conversation: Conversation,
        user_message: str,
        catalog_context: str
    ) -> Dict[str, Any]:
        """
        Processes inbound message with context, calls tools if needed,
        and returns AI response and structured actions.
        """
        pass
