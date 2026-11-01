"""
Domain Entities and Value Objects for PecasBot.
Zero external framework dependencies (Pure Python).
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import List, Optional


class ConversationState(str, Enum):
    AI_ACTIVE = "AI_ACTIVE"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"
    HUMAN_ACTIVE = "HUMAN_ACTIVE"
    WAITING_DISPATCH = "WAITING_DISPATCH"
    CLOSED = "CLOSED"


class QualityTier(str, Enum):
    ORIGINAL_NACIONAL = "ORIGINAL_NACIONAL"
    ORIGINAL_CHINA = "ORIGINAL_CHINA"
    PRIMEIRA_LINHA = "PRIMEIRA_LINHA"
    PARALELA_CHINA = "PARALELA_CHINA"


class MessageDirection(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class AuthorType(str, Enum):
    CUSTOMER = "CUSTOMER"
    AI_AGENT = "AI_AGENT"
    STORE_HUMAN = "STORE_HUMAN"


class MediaType(str, Enum):
    TEXT = "TEXT"
    AUDIO = "AUDIO"
    IMAGE = "IMAGE"


class OrderStatus(str, Enum):
    PENDING_SEPARATION = "PENDING_SEPARATION"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class CustomerRole(str, Enum):
    TECHNICIAN = "TECHNICIAN"
    END_CONSUMER = "END_CONSUMER"


@dataclass
class Product:
    sku: str
    name: str
    category: str
    compatible_models: List[str]
    quality: QualityTier
    has_frame: bool  # Com aro / Sem aro
    price: float
    stock_quantity: int
    warranty_days: int = 90
    last_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_in_stock(self) -> bool:
        return self.stock_quantity > 0


@dataclass
class Customer:
    phone_id: str
    name: Optional[str] = None
    role: CustomerRole = CustomerRole.TECHNICIAN
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Message:
    id: str
    conversation_id: str
    direction: MessageDirection
    author_type: AuthorType
    media_type: MediaType
    content: str
    raw_url: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Conversation:
    id: str
    customer_phone: str
    customer_name: Optional[str] = None  # Nome do cliente (push_name ou razão social)
    state: ConversationState = ConversationState.AI_ACTIVE
    last_activity_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    human_resumed_at: Optional[datetime] = None
    human_silence_duration_hours: int = 3
    active_sku: Optional[str] = None  # SKU da última peça cotada/discutida
    notes: Optional[str] = None

    def is_ai_allowed(self) -> bool:
        """Determines if the AI is currently authorized to reply."""
        if self.state == ConversationState.CLOSED:
            return False

        if self.state == ConversationState.HUMAN_ACTIVE:
            if self.human_resumed_at:
                timeout_threshold = self.human_resumed_at + timedelta(
                    hours=self.human_silence_duration_hours
                )
                now = datetime.now(timezone.utc)
                if now < timeout_threshold:
                    return False  # Still inside human silence window
                else:
                    # Timeout expired, AI can resume
                    self.state = ConversationState.AI_ACTIVE
                    self.human_resumed_at = None
                    return True
            return False

        return True

    def pause_for_human(self, duration_hours: int = 3) -> None:
        """Puts the AI into silent mode because an operator/owner intervened."""
        self.state = ConversationState.HUMAN_ACTIVE
        self.human_silence_duration_hours = duration_hours
        self.human_resumed_at = datetime.now(timezone.utc)

    def resume_ai(self) -> None:
        """Re-enables the AI explicitly (e.g. via #bot command)."""
        self.state = ConversationState.AI_ACTIVE
        self.human_resumed_at = None


@dataclass
class ReservationOrder:
    customer_phone: str
    customer_name: str
    product_sku: str
    quantity: int
    product_price: float
    destination_address: str
    id: str = field(default_factory=lambda: f"ped_{uuid.uuid4().hex[:8]}")
    status: OrderStatus = OrderStatus.PENDING_SEPARATION
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=2)
    )

    @property
    def is_expired(self) -> bool:
        return (
            datetime.now(timezone.utc) > self.expires_at
            and self.status == OrderStatus.PENDING_SEPARATION
        )
