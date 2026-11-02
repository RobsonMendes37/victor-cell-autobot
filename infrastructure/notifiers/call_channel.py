"""
Automated Voice Calling Channel (Telephony Port).
Allows automated voice calls to attendant phones for enterprises requiring immediate audible escalation.
Can integrate with Twilio Voice, Comtele, TotalVoice or internal VoIP/Asterisk PBX.
"""

import logging
import httpx
from typing import Optional
from infrastructure.notifiers.base import (
    NotificationPayload,
    NotificationPriority,
    StaffNotificationChannel,
)

logger = logging.getLogger(__name__)


class PhoneCallNotificationChannel(StaffNotificationChannel):
    """
    Canal de chamada telefônica automatizada.
    Pode operar em modo webhook simulado ou integrado com gateway de telefonia.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        attendant_phone: Optional[str] = None,
        enabled: bool = False,
    ):
        self.api_url = api_url
        self.auth_token = auth_token
        self.attendant_phone = attendant_phone
        self.enabled = enabled

    def get_channel_name(self) -> str:
        return "PhoneCall"

    async def is_available(self) -> bool:
        return bool(self.enabled and self.attendant_phone)

    async def dispatch(self, payload: NotificationPayload) -> bool:
        """Dispara chamada telefônica para o celular do atendente."""
        if not await self.is_available():
            logger.debug("[PhoneCallChannel] Canal de ligação inativo ou sem telefone configurado.")
            return False

        # Se houver webhook/API de telefonia configurada
        if self.api_url:
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
                data = {
                    "destination": self.attendant_phone,
                    "tts_message": f"Atenção Victor Cell: {payload.title}. {payload.message}",
                    "priority": payload.priority.value,
                }
                async with httpx.AsyncClient(timeout=5.0) as client:
                    res = await client.post(self.api_url, json=data, headers=headers)
                    if res.status_code in [200, 201, 202]:
                        logger.info(f"[PhoneCallChannel] Chamada de voz disparada com sucesso para {self.attendant_phone}.")
                        return True
            except Exception as e:
                logger.error(f"[PhoneCallChannel] Falha ao disparar chamada de voz: {e}")
                return False

        # Modo simulação / mock operacional
        logger.info(f"[PhoneCallChannel] [MOCK] Discando para {self.attendant_phone}: '{payload.title}'")
        return True
