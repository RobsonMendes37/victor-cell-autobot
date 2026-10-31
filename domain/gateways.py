"""
Gateway Interfaces for external communication (Messaging, AI).
Supports multi-turn dialog and multimodal media (audio/image).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

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

    @abstractmethod
    async def fetch_media_bytes(self, message_obj: Dict[str, Any]) -> Optional[tuple[bytes, str]]:
        """Fetches raw media bytes and mimetype from incoming media message."""
        pass


class AIServiceInterface(ABC):
    @abstractmethod
    async def process_and_reply(
        self,
        conversation: Conversation,
        user_message: str,
        catalog_context: str,
        history: Optional[List[Dict[str, str]]] = None,
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Processes inbound message with context, multi-turn history, and optional media.
        Returns AI response and structured actions.
        """
        pass
