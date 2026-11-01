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

from domain.entities import Conversation, ConversationState
from domain.gateways import AIServiceInterface
from infrastructure.config import settings

logger = logging.getLogger("AIAgentService")

SYSTEM_PROMPT = """
Você é o atendente de balcão da Victor Cell no WhatsApp (Fortaleza/CE).
Você responde EXATAMENTE como um atendente humano de balcão de assistência técnica responde no WhatsApp: ultra-curto, direto, objetivo, sem enrolação e com ZERO cara de inteligência artificial.

PROIBIÇÃO TOTAL DE ECO E RESPOSTAS ARTIFICIAIS DE CHATBOT (ZERO CARA DE IA):
- NUNCA use saudações formais longas ("Olá! Seja bem-vindo à Victor Cell", "Opa, tudo bem? Como posso te ajudar hoje?", "Agradecemos o contato").
- NUNCA use justificativas prolixas ("Infelizmente no momento não dispomos...", "Pior que capa a gente não tem por aqui, nosso forte são peças...").
- NUNCA use frases de telemarketing ou entusiasmo falso ("Show de bola!", "Maravilha!", "A peça está aqui reservadinha").
- NUNCA use emojis decorativos no texto.
- EXTENSÃO DA RESPOSTA: 1 a 6 palavras no máximo (estilo rápido e seco de balcão).

REGRA DE CERTEZA 100% E TRANSBORDO PARA O BALCÃO HUMANO:
- Se você tiver CERTEZA ABSOLUTA da peça no catálogo e ela estiver DISPONÍVEL: passe direto o valor da peça. Ex: "R0", "Touch 25", "300 frontal completa".
- Se a peça estiver ESGOTADA no catálogo: responda direto: "Tem não", "Tenho não patrão" ou "Chega próxima semana".
- Se a foto ou mensagem do cliente não der CERTEZA de 100% do modelo (ex: tela apagada, só frente, ou modelo com mais de uma versão):
  Peça a foto da traseira: "Foto dele parte trás" ou "Qual a versão do touch?".
- Se a peça NÃO estiver no catálogo, envolver conserto técnico de placa, negociação de preço, garantia de produto antigo ou você tiver QUALQUER DÚVIDA:
  NÃO invente, NÃO chute e NÃO tente enrolar o cliente.
  Transfira imediatamente para o atendente humano de balcão:
  intent: "HUMAN_HANDOFF"
  reply_text: "Vou ver com os meninos no balcão e te passo"
  requires_staff_alert: true
  handoff_reason: "Dúvida técnica / peça fora do catálogo / balcão"

EXEMPLOS REAIS MINERADOS DAS CONVERSAS DO BALCÃO DA VICTOR CELL (FEW-SHOT):
- Cliente: "Quanto tá o touch do T2040?"
  Atendente: "R0" (intent: QUOTE, target_sku: "TOU-POS-T2040")
- Cliente: "Tem a tela do x205?"
  Atendente: "R00 frontal completa" (intent: QUOTE, target_sku: "TEL-SAM-X205")
- Cliente: "Touch tablet m7 plus tem?"
  Atendente: "25" (intent: QUOTE, target_sku: "TOU-MUL-M7P")
- Cliente: "Bateria T295 tem?"
  Atendente: "Tem não" (intent: QUOTE, target_sku: "BAT-SAM-T295")
- Cliente: "Tem a tela do tablet Multilaser M8?"
  Atendente: "Display 150\nTouch 70" (intent: QUOTE)
- Cliente: "Original?"
  Atendente: "Original China" (intent: GENERAL_QUESTION)
- Cliente: "Tem alguma garantia?"
  Atendente: "Garantia só de teste" (intent: GENERAL_QUESTION)
- Cliente: [Foto da frente do tablet apagado] "Tem essa tela?"
  Atendente: "Foto dele parte trás" (intent: GENERAL_QUESTION)
- Cliente: "Vocês consertam placa ou tem placa do A50?"
  Atendente: "Vou ver com os meninos no balcão e te passo" (intent: HUMAN_HANDOFF, requires_staff_alert: true)
- Cliente: "Faz por menos? Tem desconto se levar 3?"
  Atendente: "Vou ver com o gerente e já te aviso" (intent: HUMAN_HANDOFF, requires_staff_alert: true)
- Cliente: "Separa aí, manda pelo Uber Flash"
  Atendente: "Passa o endereço pra calcular o Uber" (intent: ORDER_PENDING_CONFIRMATION)
- Cliente: "Separa aí, manda pelo Uber Flash pro endereço Rua Floriano Peixoto 1250 Centro"
  Atendente: "Passa o endereço pra calcular o Uber" ou se já passou o endereço: "Posso confirmar o envio pelo Uber Flash?" (intent: ORDER_PENDING_CONFIRMATION, destination_address: "Rua Floriano Peixoto 1250 Centro")
- Cliente: "Pode confirmar sim, patrão!" ou "Pode mandar", "Confirma", "Manda ver":
  Atendente: "Certo, separando aqui" (intent: ORDER_DISPATCH, requires_staff_alert: true, destination_address: [endereço da conversa])

HISTÓRICO DE PEDIDOS DO CLIENTE:
{customer_orders_context}

ESTADO DA LOJA:
- Aberta agora: {is_open}
- Horário regular: {opening_time} às {closing_time}

PEÇA DISCUTIDA ANTERIORMENTE NA CONVERSA: {active_sku}

CATÁLOGO EM ESTOQUE:
{catalog_context}

Responda SEMPRE em formato JSON estrito:
{{
  "intent": "QUOTE" | "ORDER_PENDING_CONFIRMATION" | "ORDER_DISPATCH" | "HUMAN_HANDOFF" | "GENERAL_QUESTION",
  "reply_text": "Texto ultra-curto e direto de balcão (1 a 6 palavras)",
  "target_sku": "SKU da peça identificada ou null",
  "requires_staff_alert": true (SEMPRE true em ORDER_DISPATCH e HUMAN_HANDOFF, false nos demais),
  "destination_address": "Endereço extraído ou null",
  "handoff_reason": "Motivo caso seja HUMAN_HANDOFF ou null"
}}
"""

class AIAgentService(AIServiceInterface):
    SUPPORTED_MODELS = [
        "gemini-3.5-flash-lite",      # Prioridade 1: 500 req/dia (15 RPM - Super rápido, texto e visão)
        "gemini-3.1-flash-lite",      # Prioridade 2: 500 req/dia (15 RPM - Super rápido, texto e visão)
        "gemini-3-flash-preview",     # Prioridade 3: 20 req/dia (5 RPM - Multimodal completo)
        "gemini-3.8-flash",           # Prioridade 4: 20 req/dia (5 RPM - Multimodal completo)
        "gemini-3.6-flash",           # Prioridade 5: 20 req/dia (5 RPM - Multimodal completo)
        "gemini-flash-latest",        # Prioridade 6: Transbordo automático
        "gemma-4-26b-a4b-it",         # Prioridade 7: 14.400 req/dia (Reserva massiva)
    ]

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
        customer_orders_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        is_open = settings.is_store_open()

        # Chamada assíncrona ao Gemini com tentativa de modelos flash suportados
        if self._client:
            prompt = SYSTEM_PROMPT.format(
                catalog_context=catalog_context,
                customer_orders_context=customer_orders_context or "Nenhum pedido recente registrado neste número.",
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

            # Seleção Inteligente de Modelos por Tipo de Mídia (Smart Media Router)
            if media_bytes and mime_type and mime_type.startswith("audio/"):
                # Áudio requer decodificador acústico nativo (Flash Multimodal de Voz)
                models_to_try = [
                    "gemini-3.8-flash",
                    "gemini-3-flash-preview",
                    "gemini-3.5-flash-lite",
                    "gemini-3.1-flash-lite",
                    "gemini-3.6-flash",
                    "gemini-flash-latest",
                ]
            elif media_bytes and mime_type and mime_type.startswith("image/"):
                # Fotos de peças/etiquetas: modelos ultra-rápidos com visão computacional (500 req/dia)
                models_to_try = [
                    "gemini-3.5-flash-lite",
                    "gemini-3.1-flash-lite",
                    "gemini-3-flash-preview",
                    "gemini-3.8-flash",
                    "gemini-3.6-flash",
                ]
            else:
                # Mensagens de texto: prioriza 1.000 req/dia gratuitos do Flash Lite + fallbacks e Gemma
                models_to_try = self.SUPPORTED_MODELS

            for model_name in models_to_try:
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

        # 1. Transbordo Humano (Negociação, placa, garantia ou atendente humano)
        if any(
            w in msg
            for w in [
                "desconto",
                "faz por menos",
                "garantia",
                "defeito",
                "falar com dono",
                "falar com atendente",
                "placa",
                "conserto",
                "reparo",
            ]
        ):
            return {
                "intent": "HUMAN_HANDOFF",
                "reply_text": "Vou ver com os meninos no balcão e te passo",
                "target_sku": None,
                "requires_staff_alert": True,
                "destination_address": None,
                "handoff_reason": "Dúvida técnica / negociação / balcão",
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
                "reply_text": "Passa o endereço pra calcular o Uber",
                "target_sku": conversation.active_sku,
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None,
            }

        # 2.5 Elogios, reações amigáveis e feedback
        is_compliment = any(
            w in msg
            for w in [
                "tá boa", "ta boa", "boa a resposta", "gostei", "economiza",
                "kkk", "top", "massa", "legal", "show", "valeu", "obrigado",
                "obg", "tmj", "abraço", "funcionou", "maravilha", "blz, tá top", "blz ta top",
                "blz", "ok", "certo"
            ]
        )
        if is_compliment:
            return {
                "intent": "GENERAL_QUESTION",
                "reply_text": "Valeu, precisando tamo aí!",
                "target_sku": conversation.active_sku,
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None,
            }

        real_address = self._extract_real_address(user_msg)

        # 3. Se a conversa está AGUARDANDO CONFIRMAÇÃO DO CLIENTE para fechar o pedido
        if conversation.state == ConversationState.WAITING_CONFIRMATION:
            is_confirmed = any(
                w in msg
                for w in [
                    "sim", "pode", "confirma", "manda", "separa", "vou querer",
                    "bora", "pode ser", "isso", "blz pode", "show pode", "ok",
                    "manda ver", "fecha", "com certeza", "positivo", "pode mandar"
                ]
            )
            if is_confirmed:
                sku = conversation.active_sku or "TEL-SAM-A15-ORIG"
                addr = conversation.notes or real_address or "Balcão"
                return {
                    "intent": "ORDER_DISPATCH",
                    "reply_text": f"Certo, separando aqui pra mandar pelo Uber Flash pro endereço: {addr}. Já te passo o Pix.",
                    "target_sku": sku,
                    "requires_staff_alert": True,
                    "destination_address": addr,
                    "handoff_reason": None,
                }
            else:
                return {
                    "intent": "GENERAL_QUESTION",
                    "reply_text": "Tranquilo, precisando só chamar",
                    "target_sku": conversation.active_sku,
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

        # 4. Intenção Inicial de Pedido / Separação ou Envio de Endereço
        is_order_intent = any(
            w in msg
            for w in [
                "separa", "separar", "manda entregar", "vou querer", "fecha essa",
                "manda essa", "pode mandar", "manda pro", "manda pra", "manda para",
                "entrega em", "entrega na", "entrega no", "endereço", "endereco"
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
                    "reply_text": "Qual peça você quer que separe?",
                    "target_sku": None,
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

            if real_address:
                return {
                    "intent": "ORDER_PENDING_CONFIRMATION",
                    "reply_text": f"Anotado: {real_address}. Posso confirmar o envio pelo Uber Flash?",
                    "target_sku": resolved_sku,
                    "requires_staff_alert": False,
                    "destination_address": real_address,
                    "handoff_reason": None,
                }
            else:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Passa o endereço pra calcular o Uber",
                    "target_sku": resolved_sku,
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

        # 5. Consulta de Peça: Atualiza o active_sku da conversa
        if "a15" in msg:
            if "original" in msg:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Original com aro R$ 190",
                    "target_sku": "TEL-SAM-A15-ORIG",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }
            elif "paralela" in msg or "china" in msg:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Paralela China R$ 95",
                    "target_sku": "TEL-SAM-A15-CHIN",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }
            else:
                return {
                    "intent": "QUOTE",
                    "reply_text": "Original 190 / China 95",
                    "target_sku": "TEL-SAM-A15-ORIG",
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

        if "tab a8" in msg or "x200" in msg:
            sku = "CON-TAB-A8-ORIG" if "conector" in msg else "TEL-TAB-A8-1LINHA"
            return {
                "intent": "QUOTE",
                "reply_text": "Tela R$ 140 / Conector R$ 25",
                "target_sku": sku,
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None,
            }

        return {
            "intent": "GENERAL_QUESTION",
            "reply_text": "Qual modelo e peça você precisa?",
            "target_sku": None,
            "requires_staff_alert": False,
            "destination_address": None,
            "handoff_reason": None,
        }

    async def ask_copilot(
        self,
        manager_question: str,
        operational_context: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Copiloto Executivo do Gestor com inteligência analítica em tempo real (Padrão Google / BI).
        Analisa faturamento, ruptura de estoque, gargalos de entrega e produtividade do balcão.
        """
        system_instruction = f"""Você é o Consultor Estratégico de Operações e Negócios da Victor Cell (Fortaleza/CE).
Você assessora diretamente o proprietário e a liderança executiva da loja com análises financeiras e operacionais de alta precisão, seguindo rigorosamente o padrão executivo do Google (Google Executive Briefing / Gemini Enterprise).

DIRETRIZES DO PADRÃO GOOGLE (DIRETO, CONCISO E EM PROSA - 150 A 250 PALAVRAS):
1. CONCISÃO E OBJETIVIDADE EXTREMA (MÁXIMO 2 A 3 PARÁGRAFOS CURTOS):
   - Seja direto ao ponto. Elimine introduções longas, rodeios formais e enrolação.
   - O gestor precisa ler e entender em 30 segundos. Vá direto aos fatos, números e decisões.

2. PROSA FLUÍDA (RIGOROSAMENTE ZERO BULLET POINTS E ZERO EMOJIS):
   - NUNCA use listas com marcadores (*, -, •). Redija em prosa contínua com parágrafos compactos.
   - NUNCA use emojis decorativos (como 📊, ⚠️, 💡, 💰, 🛵). Mantenha sobriedade corporativa absoluta.

3. ESTRUTURA COMPACTA DO BRIEFING:
   Estruture a resposta em 2 ou 3 blocos rápidos com títulos em Markdown (###):
   - ### Diagnóstico
     Faturamento de hoje, volume de pedidos, ticket médio e entregas Uber Flash (1 parágrafo curto de 2 a 3 linhas).
   - ### Estoque e Operação
     Status de peças críticas/em falta e volume de atendimentos no WhatsApp (1 parágrafo curto de 2 a 3 linhas).
   - ### Ação Recomendada
     A principal diretriz prática imediata para o dono agir (1 parágrafo curto de 1 a 2 linhas).

4. DESTAQUE SELETIVO EM NEGRITO:
   - Destaque apenas os dados essenciais (**R$ 570,00**, **3 pedidos**, **Tela Samsung A15**) para leitura imediata.
   - Baseie-se 100% no CONTEXTO OPERACIONAL abaixo.

CONTEXTO OPERACIONAL EM TEMPO REAL:
{operational_context}
"""

        contents = []
        if chat_history:
            for turn in chat_history[-6:]:
                role = "user" if turn.get("role") in ["user", "manager"] else "model"
                contents.append({"role": role, "parts": [{"text": turn.get("content", "")}]})

        contents.append({"role": "user", "parts": [{"text": manager_question}]})

        if self._client:
            for model_name in self.SUPPORTED_MODELS:
                try:
                    response = await self._client.aio.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config={
                            "system_instruction": system_instruction,
                        },
                    )
                    reply_text = response.text.strip()
                    logger.info(f"Resposta do Copiloto gerada via {model_name}")
                    return reply_text
                except Exception as e:
                    logger.warning(f"Falha no modelo {model_name} para Copiloto: {e}. Tentando próximo...")
                    continue

        # Fallback offline (Padrão Google Executive)
        return (
            "### Diagnóstico Operacional Victor Cell\n\n"
            "Os indicadores operacionais e financeiros permanecem sincronizados no painel executivo em tempo real. "
            "Recomenda-se a conferência da aba de Expedição & Logística para acompanhamento dos pedidos despachados via Uber Flash, "
            "bem como a auditoria do Catálogo para identificação de peças com estoque reduzido.\n\n"
            "Para a geração de análises analíticas aprofundadas com a inteligência Gemini, verifique a cota de sua chave de API nas configurações do sistema."
        )

