"""
Domain Entities and Value Objects for PecasBot.
Zero external framework dependencies (Pure Python).
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


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
    stock_quantity: int = 1
    warranty_days: int = 90
    has_stock: bool = True  # Controle Booleano: TEM em estoque vs NÃO TEM (Esgotado)
    location: Optional[str] = None  # Localização física (ex: Gaveta A3)
    cost_price: Optional[float] = None  # Preço de custo
    last_updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_in_stock(self) -> bool:
        if not self.has_stock:
            return False
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

    def is_ai_allowed(
        self,
        is_store_open: bool = True,
        incoming_message: Optional[str] = None,
        grace_period_minutes: int = 30,
    ) -> bool:
        """
        Determines if the AI is currently authorized to reply.
        Enterprise features:
        - If physical store is closed, AI auto-resumes to quote and notify schedule.
        - If grace_period_minutes (default 30m) elapsed since operator typed and customer
          submits a new quote request, AI auto-resumes.
        """
        if self.state == ConversationState.CLOSED:
            return False

        if self.state == ConversationState.HUMAN_ACTIVE:
            # 1. Se a loja física estiver fechada, a equipe não está presente: IA assume
            if not is_store_open:
                self.state = ConversationState.AI_ACTIVE
                self.human_resumed_at = None
                return True

            if self.human_resumed_at:
                now = datetime.now(timezone.utc)
                elapsed_minutes = (now - self.human_resumed_at).total_seconds() / 60.0

                # 2. Reabertura inteligente após janela de tolerância de 30m se for cotação
                if elapsed_minutes >= grace_period_minutes and incoming_message:
                    msg = incoming_message.lower()
                    quote_triggers = [
                        "quanto", "valor", "preço", "preco", "tem a tela", "tem tela",
                        "tem o touch", "tem touch", "tem display", "display", "bateria",
                        "t220", "t295", "x200", "m10a", "m7"
                    ]
                    if any(t in msg for t in quote_triggers):
                        self.state = ConversationState.AI_ACTIVE
                        self.human_resumed_at = None
                        return True

                timeout_threshold = self.human_resumed_at + timedelta(
                    hours=self.human_silence_duration_hours
                )
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


@dataclass
class StoreProfile:
    """
    Perfil Comercial e Configuração do Estabelecimento (Domain-Agnostic Tenant).
    Permite comercializar a solução para autopeças, farmácias, oficinas ou outros varejos especializados.
    """
    store_id: str = "default"
    store_name: str = "Victor Cell"
    city: str = "Fortaleza/CE"
    niche_description: str = "peças e manutenção de tablets (telas, touch, display, baterias, conectores)"
    out_of_scope_keywords: List[str] = field(
        default_factory=lambda: ["iphone", "celular", "smartphone", "capa", "capinha", "pelicula", "película"]
    )
    rejection_message: str = "Só peças de tablet"
    delivery_methods: List[str] = field(default_factory=lambda: ["Uber Flash", "Balcão"])
    tone_guidelines: str = "ultra-curto, direto, objetivo, 1 a 6 palavras no máximo, zero emojis"
    address: str = "Rua Barão do Rio Branco 1102, Centro"
    pix_key: str = "85999990001 (Celular / Victor Cell)"
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_out_of_scope(self, text: str) -> bool:
        t = text.lower()
        return any(k.lower() in t for k in self.out_of_scope_keywords)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "store_id": self.store_id,
            "store_name": self.store_name,
            "city": self.city,
            "niche_description": self.niche_description,
            "out_of_scope_keywords": self.out_of_scope_keywords,
            "rejection_message": self.rejection_message,
            "delivery_methods": self.delivery_methods,
            "tone_guidelines": self.tone_guidelines,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoreProfile":
        keywords = data.get("out_of_scope_keywords", [])
        if isinstance(keywords, str):
            keywords = [k.strip().lower() for k in keywords.split(",") if k.strip()]

        delivery = data.get("delivery_methods", [])
        if isinstance(delivery, str):
            delivery = [d.strip() for d in delivery.split(",") if d.strip()]

        updated = datetime.now(timezone.utc)
        if "updated_at" in data and isinstance(data["updated_at"], str):
            try:
                updated = datetime.fromisoformat(data["updated_at"])
            except Exception:
                pass

        return cls(
            store_id=data.get("store_id", "default"),
            store_name=data.get("store_name", "Victor Cell"),
            city=data.get("city", "Fortaleza/CE"),
            niche_description=data.get(
                "niche_description",
                "peças e manutenção de tablets (telas, touch, display, baterias, conectores)",
            ),
            out_of_scope_keywords=keywords or ["iphone", "celular", "smartphone", "capa", "capinha", "pelicula", "película"],
            rejection_message=data.get("rejection_message", "Só peças de tablet"),
            delivery_methods=delivery or ["Uber Flash", "Balcão"],
            tone_guidelines=data.get(
                "tone_guidelines",
                "ultra-curto, direto, objetivo, 1 a 6 palavras no máximo, zero emojis",
            ),
            updated_at=updated,
        )


@dataclass
class AuditLogEntry:
    """
    Entrada estruturada de auditoria e observabilidade técnica.
    Registra detalhadamente cada ação crítica do sistema.
    """
    action: str
    id: str = field(default_factory=lambda: f"log_{uuid.uuid4().hex[:10]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    level: str = "INFO"  # INFO, WARN, ERROR, CRITICAL
    component: str = "SYSTEM"  # AI, WEBHOOK, INVENTORY, ORDER, AUTH, DISPATCH, NOTIFIER
    actor: str = "SYSTEM"  # Telefone do cliente, staff, bot, api
    details: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    status: str = "SUCCESS"  # SUCCESS, FAILURE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "component": self.component,
            "action": self.action,
            "actor": self.actor,
            "details": self.details,
            "duration_ms": self.duration_ms,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogEntry":
        ts = datetime.now(timezone.utc)
        if "timestamp" in data and isinstance(data["timestamp"], str):
            try:
                ts = datetime.fromisoformat(data["timestamp"])
            except Exception:
                pass
        return cls(
            action=data.get("action", ""),
            id=data.get("id", f"log_{uuid.uuid4().hex[:10]}"),
            timestamp=ts,
            level=data.get("level", "INFO"),
            component=data.get("component", "SYSTEM"),
            actor=data.get("actor", "SYSTEM"),
            details=data.get("details", {}) or {},
            duration_ms=data.get("duration_ms"),
            status=data.get("status", "SUCCESS"),
        )
