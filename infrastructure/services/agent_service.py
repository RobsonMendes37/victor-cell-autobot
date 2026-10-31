"""
AI Agent Service using Google Gemini with Async Client (client.aio).
Supports:
- Multi-turn conversation history
- Multimodal inputs (audio voice notes and photo inspection)
- Semantic extraction with gemini-3.5-flash and automatic fallback
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from domain.entities import Conversation
from domain.gateways import AIServiceInterface
from infrastructure.config import settings

logger = logging.getLogger("AIAgentService")

SYSTEM_PROMPT = """
Você é o atendente de balcão virtual da loja "Victor Cell - Peças para Tablets e Celulares".
Seu objetivo é atender técnicos de bancada e clientes via WhatsApp com cordialidade, rapidez e transparência.

DIRETRIZES DE ATENDIMENTO:
1. Tom de voz de balcão de confiança: use expressões naturais como "Opa meu amigo", "Temos sim, patrão!", "Beleza?".
2. NUNCA use menus rígidos com números ("Digite 1 para telas..."). Seja 100% conversacional.
3. Transparência técnica:
   - "Original Nacional": informe que tem garantia de 90 dias.
   - "Paralela / China Incell": informe o valor acessível e recomende testar antes de colar.
4. Para telas: se o cliente não especificou se quer COM ARO ou SEM ARO, pergunte amigavelmente.
5. Multimodalidade:
   - Se o cliente enviar FOTO de etiqueta, flex, conector ou tela quebrada: identifique o modelo exato (ex: SM-X200, A155F), confirme com o catálogo e responda.
   - Se o cliente enviar ÁUDIO de voz: ouça a gravação com atenção, extraia a dúvida técnica ou pedido e responda normalmente.
6. Quando o cliente solicitar entrega ou cotar Uber:
   - Se apenas perguntou quanto custa o Uber ("quanto fica o Uber até o centro?"): NÃO crie pedido! Explique que os meninos do caixa calculam a rota pelo app do Uber Flash na hora do envio.
   - Se disse "separa essa", "pode mandar", "vou querer" ou enviou o endereço de entrega:
     - Verifique se informou endereço de entrega real (ex: Rua, Número, Bairro).
     - Se NÃO informou endereço, peça o endereço completo.
     - Se informou endereço, extraia apenas o endereço real no campo "destination_address".
     - Palavras de cortesia como "por favor", "obrigado", "valeu" NUNCA são endereços!

ESTADO DA LOJA:
- Aberta agora: {is_open}
- Horário regular: {opening_time} às {closing_time}

PEÇA DISCUTIDA ANTERIORMENTE NA CONVERSA: {active_sku}

CATÁLOGO EM ESTOQUE:
{catalog_context}

Responda SEMPRE em formato JSON estrito:
{{
  "intent": "QUOTE" | "ORDER_DISPATCH" | "HUMAN_HANDOFF" | "GENERAL_QUESTION",
  "reply_text": "Texto para o cliente no WhatsApp",
  "target_sku": "SKU da peça identificada ou null",
  "requires_staff_alert": true | false,
  "destination_address": "Endereço extraído ou null",
  "handoff_reason": "Motivo caso seja HUMAN_HANDOFF ou null"
}}
"""


class AIAgentService(AIServiceInterface):
    SUPPORTED_MODELS = ["gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            from google import genai

            if self.api_key and self.api_key != "demo_key":
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Google GenAI client inicializado com chave de API real.")
        except Exception as e:
            logger.warning(
                f"Google GenAI client não inicializado ({e}). Operando com fallback semântico seguro."
            )

    async def process_and_reply(
        self,
        conversation: Conversation,
        user_message: str,
        catalog_context: str,
        history: Optional[List[Dict[str, str]]] = None,
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        is_open = settings.is_store_open()

        # Chamada assíncrona ao Gemini com tentativa de modelos flash suportados
        if self._client:
            prompt = SYSTEM_PROMPT.format(
                catalog_context=catalog_context,
                active_sku=conversation.active_sku or "Nenhuma até o momento",
                is_open="SIM" if is_open else "NÃO (Fora do expediente)",
                opening_time=settings.STORE_OPENING_TIME,
                closing_time=settings.STORE_CLOSING_TIME,
            )

            # Constrói o histórico multi-turn
            contents = []
            if history:
                for h in history:
                    role = "user" if h.get("role") == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})

            # Monta o turno atual (com texto e/ou mídia)
            current_turn_parts = []
            if media_bytes and mime_type:
                from google.genai import types

                current_turn_parts.append(
                    types.Part.from_bytes(data=media_bytes, mime_type=mime_type)
                )

            text_content = user_message or (
                "[Mídia enviada pelo cliente]" if media_bytes else "Olá!"
            )
            current_turn_parts.append(
                {
                    "text": f"Peça ativa na sessão: {conversation.active_sku}\nMensagem: {text_content}"
                }
            )

            contents.append({"role": "user", "parts": current_turn_parts})

            for model_name in self.SUPPORTED_MODELS:
                try:
                    response = await self._client.aio.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config={
                            "system_instruction": prompt,
                            "response_mime_type": "application/json",
                        },
                    )
                    cleaned_text = response.text.strip()
                    if cleaned_text.startswith("```"):
                        cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text)
                        cleaned_text = re.sub(r"\s*```$", "", cleaned_text)
                    result = json.loads(cleaned_text)
                    logger.info(
                        f"Resposta gerada com sucesso via {model_name}: intent={result.get('intent')}"
                    )
                    return result
                except Exception as e:
                    logger.warning(
                        f"Tentativa com modelo {model_name} falhou ({e}). Tentando próximo..."
                    )

        # Fallback Semântico Seguro
        return self._semantic_fallback(user_message, conversation, is_open)

    def _extract_real_address(self, text: str) -> str | None:
        pattern = r"\b(rua|r\.|avenida|av\.|travessa|trav\.|alameda|bairro|praça)\b\s+[^,\n]+(?:,\s*\d+)?(?:\s*-\s*[^,\n]+)?"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.start()
            return text[start:].strip()
        return None

    def _semantic_fallback(
        self, user_msg: str, conversation: Conversation, is_open: bool
    ) -> Dict[str, Any]:
        msg = user_msg.lower().strip()

        # 1. Transbordo Humano
        if any(
            w in msg
            for w in [
                "desconto",
                "faz por menos",
                "garantia",
                "defeito",
                "falar com dono",
                "falar com atendente",
            ]
        ):
            return {
                "intent": "HUMAN_HANDOFF",
                "reply_text": "Entendi, meu amigo! Já avisei o gerente aqui na loja para verificar sua solicitação com prioridade. Um minuto que ele já assume a conversa aqui com você!",
                "target_sku": None,
                "requires_staff_alert": True,
                "destination_address": None,
                "handoff_reason": "Negociação ou Garantia",
            }

        # 2. Dúvida sobre frete/Uber sem pedido de compra ("quanto fica o uber?")
        is_only_uber_question = (
            ("quanto fica" in msg or "qual o valor" in msg or "quanto é" in msg)
            and ("uber" in msg or "frete" in msg or "entrega" in msg)
            and not any(
                w in msg for w in ["separa", "separar", "manda essa", "pode mandar", "vou querer"]
            )
        )
        if is_only_uber_question:
            return {
                "intent": "GENERAL_QUESTION",
                "reply_text": (
                    "Opa! O valor do Uber Flash depende da distância da nossa loja até sua assistência. "
                    "Assim que você confirmar a peça e passar o endereço com bairro, os meninos do caixa calculam a rota exata no app e te passam o valor sem acréscimo nenhum, beleza?"
                ),
                "target_sku": conversation.active_sku,
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None,
            }

        real_address = self._extract_real_address(user_msg)

        # 3. Intenção de Pedido / Separação ou Envio de Endereço
        is_order_intent = any(
            w in msg
            for w in [
                "separa",
                "separar",
                "manda entregar",
                "vou querer",
                "fecha essa",
                "manda essa",
                "pode mandar",
                "manda pro",
                "manda pra",
                "manda para",
                "entrega em",
                "entrega na",
                "entrega no",
                "endereço",
                "endereco",
            ]
        ) or (real_address is not None and conversation.active_sku is not None)

        if is_order_intent:
            resolved_sku = conversation.active_sku
            if "a15" in msg:
                resolved_sku = (
                    "TEL-SAM-A15-ORIG"
                    if "original" in msg
                    else (conversation.active_sku or "TEL-SAM-A15-ORIG")
                )
            elif "tab a8" in msg or "x200" in msg:
                resolved_sku = "CON-TAB-A8-ORIG" if "conector" in msg else "TEL-TAB-A8-1LINHA"

            if not resolved_sku:
                return {
                    "intent": "GENERAL_QUESTION",
                    "reply_text": "Com certeza, meu patrão! Me diz só qual modelo e peça você quer que a gente separe para você?",
                    "target_sku": None,
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

            if real_address:
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
                    "target_sku": resolved_sku,
                    "requires_staff_alert": True,
                    "destination_address": real_address,
                    "handoff_reason": None,
                }
            else:
                return {
                    "intent": "ORDER_DISPATCH",
                    "reply_text": (
                        "Opa, perfeito! Já deixo separada aqui no balcão.\n\n"
                        "Para os meninos do caixa cotarem o Uber Flash para você, me manda o endereço completo com número e bairro, por favor!"
                    ),
                    "target_sku": resolved_sku,
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

        # 4. Consulta de Peça: Atualiza o active_sku da conversa
        if "a15" in msg:
            if "original" in msg:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Opa, beleza meu patrão? Temos sim! A tela do A15 Original Nacional com aro tá saindo a R$ 190,00 com 90 dias de garantia. Já quer que eu passe pros meninos deixarem separada?",
                    "target_sku": "TEL-SAM-A15-ORIG",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }
            elif "paralela" in msg or "china" in msg:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Temos sim! A tela do A15 Paralela China (Incell sem aro) tá saindo a R$ 95,00. Recomendo sempre testar antes de colar. Posso separar uma pra você?",
                    "target_sku": "TEL-SAM-A15-CHIN",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
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
                    "handoff_reason": None,
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
                "handoff_reason": None,
            }

        return {
            "intent": "GENERAL_QUESTION",
            "reply_text": "Opa, bom dia meu amigo! Tudo certo? Me diz qual modelo de celular ou tablet você tá precisando de peça hoje que já consulto nosso estoque aqui no balcão!",
            "target_sku": None,
            "requires_staff_alert": False,
            "destination_address": None,
            "handoff_reason": None,
        }
