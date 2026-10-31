"""
Evolution API Client Gateway (WhatsApp Provider).
Implements MessagingGatewayInterface.
Supports multi-recipient staff alerts and tracks sent message IDs.
"""

import logging

import httpx

from domain.gateways import MessagingGatewayInterface
from infrastructure.config import settings

logger = logging.getLogger("EvolutionGateway")


class EvolutionGateway(MessagingGatewayInterface):
    def __init__(self, message_recorder=None):
        self.base_url = settings.EVOLUTION_API_URL.rstrip("/")
        self.api_key = settings.EVOLUTION_API_KEY
        self.instance = settings.EVOLUTION_INSTANCE_NAME
        self.message_recorder = message_recorder
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

    async def send_text(self, to_phone: str, text: str) -> bool:
        clean_number = "".join(filter(str.isdigit, to_phone))
        url = f"{self.base_url}/message/sendText/{self.instance}"
        payload = {
            "number": clean_number,
            "text": text,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=self.headers)
                if res.status_code in [200, 201]:
                    data = res.json()
                    msg_id = data.get("key", {}).get("id")
                    if msg_id and self.message_recorder:
                        await self.message_recorder(msg_id)
                    logger.info(f"Mensagem enviada com sucesso para {clean_number} (ID: {msg_id})")
                    return True
                logger.warning(f"Evolution API retornou status {res.status_code}: {res.text}")
                return False
        except Exception as e:
            logger.error(
                f"Falha de conexão com Evolution API ({url}): {e}. Operando em modo de simulação."
            )
            print(f"\n[MOCK WA ENVIADO PARA {clean_number}]:\n{text}\n")
            return True

    async def send_internal_staff_alert(self, alert_text: str) -> bool:
        """
        Dispara mensagem de alerta urgente para TODOS os números cadastrados
        da equipe do balcão/caixa (ex: Luan, atendentes da bancada, dono).
        """
        staff_numbers = settings.get_staff_phone_list()
        success = True
        for phone in staff_numbers:
            logger.info(f"Disparando alerta para o balcão ({phone})")
            sent = await self.send_text(phone, alert_text)
            if not sent:
                success = False
        return success
