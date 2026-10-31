"""
AI Agent Service using Google Gemini with Async Client (client.aio).
Implements AIServiceInterface with full conversational memory and active SKU awareness.
"""

import json
import logging
from typing import Any, Dict

from domain.entities import Conversation
from domain.gateways import AIServiceInterface
from infrastructure.config import settings

logger = logging.getLogger("AIAgentService")

SYSTEM_PROMPT = """
Você é o atendente de balcão virtual da loja "Victor Cell - Peças para Tablets e Celulares".
Seu objetivo é atender técnicos de bancada e clientes via WhatsApp com cordialidade, rapidez e transparência.

DIRETRIZES FUNDAMENTAIS:
1. Tom de voz de balcão de confiança: use expressões naturais como "Opa meu amigo", "Temos sim, patrão!", "Beleza?".
2. NUNCA use menus rígidos com números ("Digite 1 para telas..."). Seja 100% conversacional.
3. Transparência técnica obrigatória:
   - Se for "Original Nacional", informe que tem garantia de 90 dias.
   - Se for "Paralela / China Incell", informe o valor acessível e recomende testar antes de colar.
4. Para telas: se o cliente não especificou se quer COM ARO ou SEM ARO, pergunte amigavelmente antes de fechar.
5. Quando o cliente disser "separa essa", "pode mandar", ou pedir envio por UBER FLASH:
   - Use o SKU da peça que estava sendo discutida na conversa (ACTIVE_SKU: {active_sku}).
   - Peça o endereço completo de entrega (rua, número, bairro).
   - Avise que os meninos do caixa já vão cotar o Uber Flash e passar o Pix para liberação.
   - Se a loja estiver FECHADA agora, informe que a peça já fica reservada para envio na primeira hora da manhã seguinte.

ESTADO DA LOJA:
- Loja física aberta agora: {is_open}
- Horário regular: {opening_time} às {closing_time}

PEÇA ATUALMENTE EM DISCUSSÃO: {active_sku}

CATÁLOGO ATUALIZADO EM ESTOQUE:
{catalog_context}

Responda SEMPRE em formato JSON estrito:
{{
  "intent": "QUOTE" | "ORDER_DISPATCH" | "HUMAN_HANDOFF" | "GENERAL_QUESTION",
  "reply_text": "Texto que será enviado ao cliente no WhatsApp",
  "target_sku": "SKU da peça identificada ou null",
  "requires_staff_alert": true | false,
  "destination_address": "Endereço extraído se o cliente informou ou null",
  "handoff_reason": "Motivo caso seja HUMAN_HANDOFF ou null"
}}
"""


class AIAgentService(AIServiceInterface):
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            if self.api_key and self.api_key != "demo_key":
                self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            logger.warning(f"Google GenAI client não inicializado ({e}). Operando com fallback contextual.")

    async def process_and_reply(
        self,
        conversation: Conversation,
        user_message: str,
        catalog_context: str
    ) -> Dict[str, Any]:
        """
        Processes inbound message with context using async client.aio.
        """
        is_open = settings.is_store_open()

        # Chamada assíncrona com Gemini quando configurado
        if self._client:
            try:
                prompt = SYSTEM_PROMPT.format(
                    catalog_context=catalog_context,
                    active_sku=conversation.active_sku or "Nenhum no momento",
                    is_open="SIM" if is_open else "NÃO (Fora do expediente)",
                    opening_time=settings.STORE_OPENING_TIME,
                    closing_time=settings.STORE_CLOSING_TIME
                )

                response = await self._client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        {"role": "user", "parts": [{"text": f"Mensagem do cliente:\n{user_message}"}]}
                    ],
                    config={"system_instruction": prompt, "response_mime_type": "application/json"}
                )
                return json.loads(response.text)
            except Exception as e:
                logger.error(f"Erro na chamada do Gemini API (async): {e}. Acionando fallback contextual.")

        # Fallback Heurístico Contextual Inteligente
        return self._contextual_fallback(user_message, conversation, is_open)

    def _contextual_fallback(
        self,
        user_msg: str,
        conversation: Conversation,
        is_open: bool
    ) -> Dict[str, Any]:
        msg = user_msg.lower().strip()

        # 1. Intenção de Pedido / Separação / Uber Flash
        if any(w in msg for w in ["separa", "separar", "uber", "manda entregar", "vou querer", "fecha essa", "manda essa", "pode ser"]):
            # Resolução do Bug 1: Usa o active_sku da conversa se não especificado na mensagem
            resolved_sku = conversation.active_sku
            if "a15" in msg:
                resolved_sku = "TEL-SAM-A15-ORIG" if "original" in msg else (conversation.active_sku or "TEL-SAM-A15-ORIG")
            elif "tab a8" in msg or "x200" in msg:
                resolved_sku = "CON-TAB-A8-ORIG" if "conector" in msg else "TEL-TAB-A8-1LINHA"

            has_address = any(w in msg for w in ["rua", "av", "avenida", "bairro", "número", "n°", "travessa"])

            if has_address:
                if is_open:
                    reply = (
                        "Show de bola, meu patrão! Já anotei o seu endereço e passei a peça para os meninos do caixa.\n\n"
                        "Eles já estão calculando o Uber Flash aqui e em 2 minutinhos te passam o valor certinho "
                        "e a chave Pix para liberar o motorista, beleza?"
                    )
                else:
                    reply = (
                        "Show de bola, meu patrão! Como nossa expedição física já encerrou o expediente por hoje, "
                        "já deixei o seu pedido na fila prioritária de amanhã!\n\n"
                        f"Às {settings.STORE_OPENING_TIME} em ponto os meninos do caixa cotam o Uber Flash e te mandam o Pix para despachar logo na primeira hora, combinado?"
                    )

                return {
                    "intent": "ORDER_DISPATCH",
                    "reply_text": reply,
                    "target_sku": resolved_sku or "TEL-SAM-A15-ORIG",
                    "requires_staff_alert": True,
                    "destination_address": user_msg,
                    "handoff_reason": None
                }
            else:
                return {
                    "intent": "ORDER_DISPATCH",
                    "reply_text": (
                        "Opa, perfeito! Já deixo separada aqui no balcão.\n\n"
                        "Você prefere que a gente chame o Uber Flash aqui da loja? "
                        "Se sim, me manda o endereço completo com ponto de referência que os meninos do caixa já cotam pra você!"
                    ),
                    "target_sku": resolved_sku or "TEL-SAM-A15-ORIG",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None
                }

        # 2. Transbordo Humano
        if any(w in msg for w in ["desconto", "faz por menos", "garantia", "defeito", "falar com dono", "falar com atendente"]):
            return {
                "intent": "HUMAN_HANDOFF",
                "reply_text": "Entendi, meu amigo! Já avisei o gerente aqui na loja para verificar sua solicitação com prioridade. Um minuto que ele já assume a conversa aqui com você!",
                "target_sku": None,
                "requires_staff_alert": True,
                "destination_address": None,
                "handoff_reason": "Negociação ou Garantia"
            }

        # 3. Consulta de Peça: Atualiza o active_sku da conversa!
        if "a15" in msg:
            if "original" in msg:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Opa, beleza meu patrão? Temos sim! A tela do A15 Original Nacional com aro tá saindo a R$ 190,00 com 90 dias de garantia. Já quer que eu passe pros meninos deixarem separada?",
                    "target_sku": "TEL-SAM-A15-ORIG",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None
                }
            elif "paralela" in msg or "china" in msg:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Temos sim! A tela do A15 Paralela China (Incell sem aro) tá saindo a R$ 95,00. Recomendo sempre testar antes de colar. Posso separar uma pra você?",
                    "target_sku": "TEL-SAM-A15-CHIN",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None
                }
            else:
                return {
                    "intent": "QUOTE",
                    "reply_text": (
                        "Opa, temos o A15 sim! Temos duas opções na bancada:\n\n"
                        "1. Original Nacional (com aro): R$ 190,00 (90 dias garantia)\n"
                        "2. Paralela China Incell (sem aro): R$ 95,00\n\n"
                        "Qual das duas você prefere que a gente separe pro seu serviço?"
                    ),
                    "target_sku": "TEL-SAM-A15-ORIG",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None
                }

        if "tab a8" in msg or "x200" in msg:
            sku = "CON-TAB-A8-ORIG" if "conector" in msg else "TEL-TAB-A8-1LINHA"
            return {
                "intent": "QUOTE",
                "reply_text": (
                    "Opa, pro Tab A8 (X200/X205) temos a pronta entrega:\n\n"
                    "• Tela Frontal 1ª Linha: R$ 140,00\n"
                    "• Conector de Carga: R$ 25,00\n\n"
                    "Qual delas você tá precisando no momento?"
                ),
                "target_sku": sku,
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None
            }

        # Resposta padrão cordial
        return {
            "intent": "GENERAL_QUESTION",
            "reply_text": "Opa, bom dia meu amigo! Tudo certo? Me diz qual modelo de celular ou tablet você tá precisando de peça hoje que já consulto nosso estoque aqui no balcão!",
            "target_sku": None,
            "requires_staff_alert": False,
            "destination_address": None,
            "handoff_reason": None
        }
