"""
Composite Staff Notification Dispatcher.
Broadcasts urgent customer escalations and order dispatch notifications across active channels
(Ntfy Push, Automated Phone Calls, Internal Webhooks) and logs every event to the Audit Log.
"""

import logging
from typing import List, Optional

from domain.entities import AuditLogEntry
from infrastructure.notifiers.base import (
    NotificationPayload,
    NotificationPriority,
    StaffNotificationChannel,
)
from infrastructure.notifiers.call_channel import PhoneCallNotificationChannel
from infrastructure.notifiers.ntfy_channel import NtfyNotificationChannel

logger = logging.getLogger(__name__)


class StaffNotificationDispatcher:
    def __init__(
        self,
        channels: Optional[List[StaffNotificationChannel]] = None,
        repository = None,
    ):
        self.channels = channels if channels is not None else [
            NtfyNotificationChannel(),
            PhoneCallNotificationChannel(enabled=False),
        ]
        self.repository = repository

    def add_channel(self, channel: StaffNotificationChannel) -> None:
        self.channels.append(channel)

    async def notify_handoff(
        self,
        customer_phone: str,
        reason: str,
        raw_message: str,
        customer_name: Optional[str] = None,
    ) -> bool:
        """Dispara alerta de transbordo silencioso para atendimento humano."""
        payload = NotificationPayload(
            title="ATENDIMENTO HUMANO REQUISITADO",
            message=(
                f"Cliente: {customer_name or 'Cliente'} ({customer_phone})\n"
                f"Motivo: {reason}\n"
                f'Mensagem: "{raw_message}"\n'
                f"Assuma a conversa no WhatsApp!"
            ),
            customer_phone=customer_phone,
            customer_name=customer_name,
            priority=NotificationPriority.URGENT,
            tags=["warning", "handshake", "phone"],
        )
        return await self.dispatch(payload)

    async def notify_dispatch_order(
        self,
        order_id: str,
        customer_phone: str,
        product_desc: str,
        destination_address: str,
        customer_name: Optional[str] = None,
    ) -> bool:
        """Dispara alerta de novo pedido para separação imediata e cotação de Uber Flash."""
        payload = NotificationPayload(
            title="NOVO PEDIDO PARA SEPARAÇÃO E UBER FLASH",
            message=(
                f"Pedido #{order_id}\n"
                f"Cliente: {customer_name or 'Cliente'} ({customer_phone})\n"
                f"Peça: {product_desc}\n"
                f"Destino: {destination_address}\n"
                f"Ação: Separar peça e solicitar Uber Flash no caixa!"
            ),
            customer_phone=customer_phone,
            customer_name=customer_name,
            order_id=order_id,
            priority=NotificationPriority.URGENT,
            tags=["package", "car", "white_check_mark"],
        )
        return await self.dispatch(payload)

    async def dispatch(self, payload: NotificationPayload) -> bool:
        """Executa disparo em todos os canais disponíveis e grava entrada de auditoria."""
        any_success = False
        dispatched_channels = []

        for ch in self.channels:
            if await ch.is_available():
                success = await ch.dispatch(payload)
                if success:
                    any_success = True
                    dispatched_channels.append(ch.get_channel_name())

        # Registra evento na trilha de auditoria
        if self.repository and hasattr(self.repository, "record_audit_log"):
            entry = AuditLogEntry(
                action="STAFF_NOTIFICATION_DISPATCHED",
                component="NOTIFIER",
                level="INFO" if any_success else "WARN",
                actor=payload.customer_phone,
                details={
                    "title": payload.title,
                    "order_id": payload.order_id,
                    "channels": dispatched_channels,
                    "priority": payload.priority.value,
                },
                status="SUCCESS" if any_success else "FAILURE",
            )
            try:
                await self.repository.record_audit_log(entry)
            except Exception as e:
                logger.error(f"[NotificationDispatcher] Erro ao gravar log de auditoria: {e}")

        return any_success
