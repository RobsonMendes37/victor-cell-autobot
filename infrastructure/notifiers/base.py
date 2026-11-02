"""
Base abstractions for Staff Notification and Escalation Channels.
Decouples attendant alerts (ntfy push, phone call, webhook buzzer) into modular channels.
Follows the Observer / Ports & Adapters pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class NotificationPriority(str, Enum):
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationPayload:
    title: str
    message: str
    customer_phone: str
    customer_name: Optional[str] = None
    order_id: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.HIGH
    tags: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class StaffNotificationChannel(ABC):
    """Contrato abstrato para qualquer canal de notificação da equipe física."""

    @abstractmethod
    def get_channel_name(self) -> str:
        """Nome legível do canal (ex: 'NtfyPush', 'PhoneCall', 'WebhookBuzzer')."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Indica se o canal está habilitado e operacional."""
        pass

    @abstractmethod
    async def dispatch(self, payload: NotificationPayload) -> bool:
        """Dispara a notificação de forma assíncrona. Retorna True em caso de sucesso."""
        pass
