"""
Evolution API Client Gateway (WhatsApp Provider).
Implements MessagingGatewayInterface.
Supports multi-recipient staff alerts, sent message tracking, and media decoding.
"""

import base64
import logging
from typing import Any, Dict, Optional, Tuple

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

    async def send_presence(self, to_phone: str, presence: str = "composing", delay_ms: int = 2000) -> bool:
        """Envia status de 'digitando...' para o WhatsApp para simular digitação humana real."""
        clean_number = "".join(filter(str.isdigit, to_phone))
        url = f"{self.base_url}/chat/sendPresence/{self.instance}"
        payload = {
            "number": clean_number,
            "presence": presence,
            "delay": delay_ms,
        }
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(url, json=payload, headers=self.headers)
                return res.status_code in [200, 201]
        except Exception as e:
            logger.debug(f"Aviso ao enviar sendPresence para {clean_number}: {e}")
            return False

    async def send_text(self, to_phone: str, text: str, simulate_typing: bool = True) -> bool:
        clean_number = "".join(filter(str.isdigit, to_phone))

        if simulate_typing and text:
            # Cadência humana de digitação: calcula tempo natural (1.8s a 3.8s)
            # Mostra 'digitando...' no WhatsApp antes de entregar a resposta
            calc_delay = min(max(int(len(text) * 35), 1800), 3800)
            await self.send_presence(clean_number, "composing", delay_ms=calc_delay)
            await asyncio.sleep(calc_delay / 1000.0)

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

    async def fetch_media_bytes(
        self, message_obj: Dict[str, Any], key_obj: Optional[Dict[str, Any]] = None
    ) -> Optional[Tuple[bytes, str]]:
        """
        Extrai os bytes brutos e o mimetype de uma mensagem de imagem ou áudio.
        Se já vier em base64 no webhook (webhookBase64=True), decodifica diretamente.
        Caso contrário, busca na Evolution API via getBase64FromMediaMessage passando key e message.
        """
        try:
            mime_type = None
            raw_base64 = None

            if "imageMessage" in message_obj:
                img_data = message_obj["imageMessage"]
                mime_type = img_data.get("mimetype", "image/jpeg")
                raw_base64 = img_data.get("base64")
            elif "audioMessage" in message_obj:
                audio_data = message_obj["audioMessage"]
                mime_type = audio_data.get("mimetype", "audio/ogg")
                raw_base64 = audio_data.get("base64")

            # Se já veio no payload em base64
            if raw_base64:
                logger.info(f"Mídia decodificada diretamente do base64 do webhook ({mime_type})")
                return base64.b64decode(raw_base64), mime_type

            # Se não veio no payload, busca na Evolution API via getBase64FromMediaMessage
            url = f"{self.base_url}/chat/getBase64FromMediaMessage/{self.instance}"
            payload = {
                "message": {
                    "key": key_obj or {},
                    "message": message_obj,
                },
                "convertToMp4": False,
            }
            async with httpx.AsyncClient(timeout=12.0) as client:
                res = await client.post(url, json=payload, headers=self.headers)
                if res.status_code in [200, 201]:
                    data = res.json()
                    b64_str = data.get("base64")
                    if b64_str:
                        logger.info(f"Mídia obtida com sucesso via getBase64FromMediaMessage ({mime_type})")
                        return base64.b64decode(b64_str), mime_type
                else:
                    logger.warning(f"Evolution API getBase64FromMediaMessage retornou status {res.status_code}: {res.text}")
        except Exception as e:
            logger.warning(f"Não foi possível obter bytes da mídia: {e}")

        return None
