"""
ntfy.sh Mobile Push Notification Channel.
Delivers urgent alerts directly to attendants' smartphones with priority sirens and vibration.
"""

import logging
from typing import Optional

import httpx

from infrastructure.config import settings
from infrastructure.notifiers.base import (
    NotificationPayload,
    NotificationPriority,
    StaffNotificationChannel,
)

logger = logging.getLogger(__name__)


class NtfyNotificationChannel(StaffNotificationChannel):
    def __init__(
        self,
        server_url: Optional[str] = None,
        topic: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        self.server_url = (server_url or settings.NTFY_SERVER).rstrip("/")
        self.topic = topic or settings.NTFY_TOPIC
        self.enabled = enabled if enabled is not None else settings.NTFY_ENABLED

    def get_channel_name(self) -> str:
        return "NtfyPush"

    async def is_available(self) -> bool:
        return bool(self.enabled and self.topic)

    async def dispatch(self, payload: NotificationPayload) -> bool:
        if not await self.is_available():
            return False

        url = f"{self.server_url}/{self.topic}"
        prio_map = {
            NotificationPriority.NORMAL: "3",
            NotificationPriority.HIGH: "4",
            NotificationPriority.URGENT: "5",
        }
        clean_phone = "".join(filter(str.isdigit, payload.customer_phone))
        headers = {
            "Title": payload.title,
            "Priority": prio_map.get(payload.priority, "4"),
            "Tags": ",".join(payload.tags) if payload.tags else "warning,phone",
        }
        if clean_phone:
            wa_link = f"https://wa.me/{clean_phone}"
            headers["Click"] = wa_link
            headers["Actions"] = f"view, Abrir WhatsApp, {wa_link}, clear=true"

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(url, content=payload.message.encode("utf-8"), headers=headers)
                if res.status_code in [200, 201]:
                    logger.info(f"[NtfyChannel] Alerta entregue com sucesso no tópico '{self.topic}'.")
                    return True
                logger.warning(f"[NtfyChannel] Status {res.status_code} ao enviar alerta: {res.text}")
        except Exception as e:
            logger.error(f"[NtfyChannel] Falha de conexão ao enviar alerta: {e}")

        return False
