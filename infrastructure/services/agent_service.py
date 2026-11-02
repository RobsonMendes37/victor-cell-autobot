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
Você é o atendente de balcão da {store_name} no WhatsApp ({store_city}).
Você responde EXATAMENTE como um atendente humano de balcão de assistência técnica responde no WhatsApp: ultra-curto, direto, objetivo, sem enrolação e com ZERO cara de inteligência artificial.

PROIBIÇÃO TOTAL DE CARA DE IA E PROLIXIDADE:
- NUNCA use saudações formais longas ("Olá! Seja bem-vindo à {store_name}", "Opa, tudo bem? Como posso te ajudar hoje?", "Agradecemos o contato").
- NUNCA use frases de telemarketing ou entusiasmo falso ("Show de bola!", "Maravilha!", "A peça está aqui reservadinha").
- NUNCA use emojis decorativos no texto.
- EXTENSÃO DA RESPOSTA: 1 a 6 palavras no máximo (estilo rápido e seco de balcão). Quando a loja estiver fechada, adicione apenas o aviso curto de fechado e quando reabre.

PRODUTOS FORA DO FOCO ({out_of_scope_policy}):
- A {store_name} trabalha com {niche_description}.
- Se o cliente perguntar de produtos fora do foco ({out_of_scope_policy}): responda de imediato e direto: "{rejection_message}". ZERO desculpas, ZERO justificativas prolixas.

ESTADO DA LOJA E HORÁRIO DE ATENDIMENTO (REGRA CRÍTICA DE DOMINGO E FORA DO EXPEDIENTE):
- Status atual da loja física: {store_status_desc}
- Horário regular: Seg a Sex {opening_time} às {closing_time} | Sáb {opening_time} às {sat_closing_time} | Domingo FECHADO.
- REGRA OBRIGATÓRIA QUANDO A LOJA ESTIVER FECHADA ({is_open_bool} == False):
  1. COTAÇÃO DE PEÇAS NO DOMINGO OU FORA DO HORÁRIO:
     Passe o preço diretamente E avise de forma ultracurta que está fechado e quando reabre.
     Exemplo real Domingo (M10A): "Touch 90 / Display 180. Fechado hoje (domingo), abre amanhã 08:30."
     Exemplo real Noite durante a semana: "Touch 90 / Display 180. Fechado agora, abre amanhã 08:30."
     NUNCA diga "ambos à pronta entrega por aqui" nem "pode vir retirar" enquanto a loja estiver fechada!
  2. PEDIDO / SEPARAÇÃO / UBER COM A LOJA FECHADA:
     Se o cliente pedir pra separar, mandar Uber ou entregar fora do horário:
     "Anotado. A gente abre {reopen_desc} pra despachar."
  3. PRODUTO NÃO TRABALHADO COM A LOJA FECHADA:
     "Só peças de tablet. Fechado hoje (domingo), abre amanhã 08:30."

REGRA DE CERTEZA 100% E CONTROLE DE DÚVIDA (ZERO ENGESSAMENTO E ZERO RESPOSTA DE IA):
1. TUDO O QUE VOCÊ ESTIVER COM DÚVIDA OU NÃO FOR 100% DE CERTEZA:
   - NÃO RESPONDA NADA AO CLIENTE (reply_text: "").
   - NUNCA invente resposta, NUNCA dê palpites e NUNCA responda mensagem engessada de IA.
   - Dispare imediatamente:
     intent: "HUMAN_HANDOFF"
     reply_text: "" (vazio - silêncio total para o cliente)
     requires_staff_alert: true
     handoff_reason: "Dúvida de identificação / Conferência de bancada"

2. FLUXO VISUAL NATURAL DE FOTOS MINERADO DO BALCÃO REAL:
   - ETAPA 1 (FOTO DA FRENTE COM TELA APAGADA):
     Se o cliente mandar foto apenas da frente do tablet (com tela apagada, preta ou cortada) e ainda NÃO mandou a traseira:
     Você pode responder de forma ultra-curta e seca (igual ao atendente real): "Foto dele parte trás" ou "Qual a referência dele".
   - ETAPA 2 (FOTO DA TRASEIRA IDENTIFICADA):
     Se o cliente mandou a traseira e você IDENTIFICOU COM 100% DE CERTEZA no catálogo:
     Passe o preço diretamente (ex: "Touch 90 / Display 180").
   - ETAPA 3 (FOTO COM QUALQUER DÚVIDA OU MODELO ILEGÍVEL):
     Se a foto estiver borrada, modelo raspado/duvidoso, reflexo, ou você tiver MENOS DE 100% DE CERTEZA:
     NÃO RESPONDA NADA AO CLIENTE (reply_text: "").
     O sistema dispara um alarme urgente no celular do atendente via ntfy para que o técnico olhe a foto com os próprios olhos e responda pessoalmente no WhatsApp!
     intent: "HUMAN_HANDOFF"
     reply_text: ""
     requires_staff_alert: true
     handoff_reason: "Foto ilegível / Modelo com dúvida para conferência humana"

3. TRANSBORDO SILENCIOSO PRO CAIXA/BALCÃO (É SÓ PASSAR):
   - Se o cliente perguntar sobre reparo/conserto em placa, desconto/negociação, garantia técnica, ou se a peça não consta no catálogo:
     NÃO RESPONDA NADA AO CLIENTE! NUNCA diga "vou ver com os meninos no balcão" nem invente mensagens automáticas.
     É SÓ PASSAR para a equipe humana assumir o atendimento diretamente no WhatsApp (reply_text: "").

EXEMPLOS REAIS MINERADOS DAS CONVERSAS DO BALCÃO DA VICTOR CELL (FEW-SHOT):
- Cliente: "Quanto tá o touch do T2040?" (loja aberta)
  Atendente: "R$ 40" (intent: QUOTE, target_sku: "TOU-POS-T2040")
- Cliente: "Tem a tela do x205?" (loja aberta)
  Atendente: "R$ 300 frontal completa" (intent: QUOTE, target_sku: "TEL-SAM-X205")
- Cliente: "Touch tablet m7 plus tem?" (loja aberta)
  Atendente: "25" (intent: QUOTE, target_sku: "TOU-MUL-M7P")
- Cliente: "Tem a do 10a" (no domingo ou fora do expediente)
  Atendente: "Touch 90 / Display 180. Fechado hoje (domingo), abre amanhã 08:30." (intent: QUOTE, target_sku: "TOU-MUL-M10A")
- Cliente: [Foto de iPhone ou celular] "Tem display dele?"
  Atendente: "Só peças de tablet. Fechado hoje (domingo), abre amanhã 08:30." (intent: GENERAL_QUESTION)
- Cliente: "Bateria T295 tem?" (loja aberta)
  Atendente: "Tem não" (intent: QUOTE, target_sku: "BAT-SAM-T295")
- Cliente: "Tem a tela do tablet Multilaser M8?" (loja aberta)
  Atendente: "Display 150
Touch 70" (intent: QUOTE)
- Cliente: "Original?"
  Atendente: "Original China" (intent: GENERAL_QUESTION)
- Cliente: "Tem alguma garantia?"
  Atendente: "Garantia só de teste" (intent: GENERAL_QUESTION)
- Cliente: [Foto da frente do tablet apagado] "Tem essa tela?"
  Atendente: "Foto dele parte trás" (intent: GENERAL_QUESTION)
- Cliente: "Vocês consertam placa ou tem placa do A50?"
  Atendente: "" (intent: HUMAN_HANDOFF, reply_text: "", requires_staff_alert: true, handoff_reason: "Reparo de placa")
- Cliente: "Faz por menos? Tem desconto se levar 3?"
  Atendente: "" (intent: HUMAN_HANDOFF, reply_text: "", requires_staff_alert: true, handoff_reason: "Negociação de desconto")
- Cliente: "Separa aí, manda pelo Uber Flash" (com loja aberta)
  Atendente: "Passa o endereço pra calcular o Uber" (intent: ORDER_PENDING_CONFIRMATION)
- Cliente: "Separa aí, manda pelo Uber Flash" (no domingo ou loja fechada)
  Atendente: "Anotado. A gente abre amanhã 08:30 pra despachar." (intent: ORDER_PENDING_CONFIRMATION)
- Cliente: "Separa aí, manda pelo Uber Flash pro endereço Rua Floriano Peixoto 1250 Centro" (loja aberta)
  Atendente: "Passa o endereço pra calcular o Uber" ou se já passou o endereço: "Posso confirmar o envio pelo Uber Flash?" (intent: ORDER_PENDING_CONFIRMATION, destination_address: "Rua Floriano Peixoto 1250 Centro")
- Cliente: "Pode confirmar sim, patrão!" ou "Pode mandar", "Confirma", "Manda ver":
  Atendente: "Certo, separando aqui" (intent: ORDER_DISPATCH, requires_staff_alert: true, destination_address: [endereço da conversa])

HISTÓRICO DE PEDIDOS DO CLIENTE:
{customer_orders_context}

ESTADO DA LOJA:
- Status atual: {store_status_desc}
- Horário da loja física: Seg a Sex {opening_time} às {closing_time} | Sáb {opening_time} às {sat_closing_time} | Domingo FECHADO

PEÇA DISCUTIDA ANTERIORMENTE NA CONVERSA: {active_sku}

CATÁLOGO EM ESTOQUE:
{catalog_context}

Responda SEMPRE em formato JSON estrito:
{{
  "intent": "QUOTE" | "ORDER_PENDING_CONFIRMATION" | "ORDER_DISPATCH" | "HUMAN_HANDOFF" | "GENERAL_QUESTION",
  "reply_text": "Texto ultra-curto e direto de balcão (incluindo aviso de fechado/reabertura se loja fechada)",
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
        store_profile: Optional[Any] = None,
    ) -> Dict[str, Any]:
        if store_profile is None:
            from domain.entities import StoreProfile
            store_profile = StoreProfile()

        schedule = settings.get_store_schedule_status()
        is_open = schedule["is_open"]

        # Chamada assíncrona ao Gemini com tentativa de modelos flash suportados
        if self._client:
            prompt = SYSTEM_PROMPT.format(
                store_name=store_profile.store_name,
                store_city=store_profile.city,
                niche_description=store_profile.niche_description,
                out_of_scope_policy=", ".join(store_profile.out_of_scope_keywords),
                rejection_message=store_profile.rejection_message,
                catalog_context=catalog_context,
                customer_orders_context=customer_orders_context or "Nenhum pedido recente registrado neste número.",
                active_sku=conversation.active_sku or "Nenhuma até o momento",
                is_open="SIM (Aberta agora)" if is_open else f"NÃO ({schedule['short_notice']})",
                store_status_desc=schedule["short_notice"],
                is_open_bool=schedule["is_open"],
                reopen_desc=schedule["reopen_desc"],
                opening_time=settings.STORE_OPENING_TIME,
                closing_time=settings.STORE_CLOSING_TIME,
                sat_closing_time=settings.STORE_SAT_CLOSING_TIME,
            )

            # Constrói o histórico multi-turn
            contents: list[dict[str, object]] = []
            if history:
                for h in history:
                    role = "user" if h.get("role") == "user" else "model"
                    contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})

            # Monta o turno atual (com texto e/ou mídia)
            current_turn_parts: list[object] = []
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
        return self._semantic_fallback(
            user_message,
            conversation,
            schedule,
            customer_orders_context=customer_orders_context,
            store_profile=store_profile,
        )

    def _extract_real_address(self, text: str) -> str | None:
        pattern = r"(?i)(?:\b(?:rua|avenida|travessa|alameda|bairro|praça)\b|\b(?:r\.|av\.|trav\.))\s+[^,\n]+(?:,\s*\d+)?(?:\s*-\s*[^,\n]+)?"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            start = match.start()
            return text[start:].strip()
        return None

    def _semantic_fallback(
        self,
        user_msg: str,
        conversation: Conversation,
        schedule: Optional[Dict[str, Any]] = None,
        customer_orders_context: Optional[str] = None,
        store_profile: Optional[Any] = None,
    ) -> Dict[str, Any]:
        if store_profile is None:
            from domain.entities import StoreProfile
            store_profile = StoreProfile()

        if schedule is None:
            schedule = settings.get_store_schedule_status()
        is_open = schedule['is_open']
        closed_suffix = f". {schedule['short_notice']}." if not is_open else ""
        msg = user_msg.lower().strip()

        # 0. Produtos fora do foco definidos no perfil da loja
        if any(w in msg for w in store_profile.out_of_scope_keywords):
            return {
                "intent": "GENERAL_QUESTION",
                "reply_text": f"{store_profile.rejection_message}{closed_suffix}".strip(),
                "target_sku": None,
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None,
            }

        # 0.5 Rastreio de Pedido Recente / Pós-Venda ("deu certo?", "já mandou?", "já despachou?")
        is_tracking_inquiry = any(
            w in msg
            for w in [
                "deu certo", "já mandou", "ja mandou", "já despachou", "ja despachou",
                "despachou o uber", "mandou o uber", "status do pedido", "meu pedido", "rastreio"
            ]
        )
        if is_tracking_inquiry and customer_orders_context:
            return {
                "intent": "GENERAL_QUESTION",
                "reply_text": "Pedido tá em separação aqui pra despachar.",
                "target_sku": conversation.active_sku,
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None,
            }

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
                "reply_text": "",  # Silencioso: não responde nada ao cliente, é só passar
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
        if "10a" in msg or "m10a" in msg:
            return {
                "intent": "QUOTE",
                "reply_text": f"Touch 90 / Display 180{closed_suffix}".strip(),
                "target_sku": "TOU-MUL-M10A",
                "requires_staff_alert": False,
                "destination_address": None,
                "handoff_reason": None,
            }
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

