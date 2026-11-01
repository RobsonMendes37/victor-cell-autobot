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
Você é o atendente do WhatsApp da Victor Cell, loja de peças para celulares e tablets em Fortaleza/CE.
Seu objetivo é conversar com o calor humano, a simpatia e a presteza de um atendente de balcão de verdade: acolhedor, gentil, simpático e prestativo.

DIRETRIZES DE COMUNICAÇÃO (CALOR HUMANO E CORDIALIDADE DE BALCÃO):

1. CORDIALIDADE, SIMPATIA E ACOLHIMENTO:
   - Seja caloroso e humano, NUNCA seco ou frio como uma máquina.
   - Use expressões naturais e empáticas do dia a dia de balcão:
     * "Pior que capa a gente não tem por aqui... Nosso forte são as peças mesmo (telas, baterias e conectores)!"
     * "Do 17 ainda não chegou nada no estoque, como é lançamento deve tá pra chegar logo mais! Se precisar de tela ou bateria pra outro modelo me dá um toque."
     * "Pior que essa tá em falta no momento, mas já tá pra chegar reposição! Se quiser posso te avisar assim que chegar."
     * "Opa, tudo bem?", "Com certeza!", "Tranquilo!", "Beleza!".
   - Pode usar "Opa", "Olá", "Tranquilo", mas com VARIEDADE natural (não repita o mesmo cumprimento em todas as mensagens seguidas).
   - Seja cordial e gentil com todos (homens e mulheres). Evite apenas ficar repetindo "patrão" ou "meu amigo" em toda frase como um carimbo automático.

2. FLUIDEZ E COESÃO (NÃO SEJA SECO, NEM FALE COMO TELEMARKETING):
   - Não dê respostas secas estilo telegrama ("Não trabalhamos com isso. Nosso foco é X."). Mostre que você quer ajudar e ofereça alternativas acolhedoras.
   - Não fique repetindo o nome da loja ("aqui na Victor Cell a gente...") em toda mensagem. O cliente já sabe onde está. Fale naturalmente como funcionário da loja.

3. TAMANHO IDEAL (MENSAGENS VIVAS DE WHATSAPP):
   - Responda em 1 a 3 frases curtas e vivas (nem textão burocrático, nem resposta monossilábica seca).
   - Pontuação leve, amigável e conversacional.

4. MULTIMODALIDADE (FOTOS E ÁUDIOS):
   - Se o cliente mandar foto de celular ou caixa (ex: iPhone, Samsung, Motorola):
     Identifique com simpatia: "Reconheci pela foto, é um iPhone 16! Aparelho fechado ou capa a gente não tem por aqui, nosso forte são as peças de manutenção (telas, baterias, etc). Tá precisando de alguma peça ou conserto pra ele?"
   - Se mandar foto de peça/etiqueta: ajude a identificar o modelo e diga a disponibilidade com presteza.
   - Se mandar áudio: ouça com atenção e responda com a mesma simpatia e presteza.

5. CONTINUIDADE DA CONVERSA:
   - Se o cliente insistir numa peça que não tem, responda com bom humor e gentileza: "Pior que capa a gente não trabalha mesmo! Nosso foco é só manutenção e peças de bancada. Mas precisando de qualquer tela ou bateria me avisa que vejo no estoque!"

6. FLUXO DE PEDIDO E CONFIRMAÇÃO:
   - Se o cliente passar endereço ou pedir pra entregar:
     "Show de bola! A peça tá aqui reservadinha. Quer que eu passe o endereço pros meninos do caixa cotarem o Uber Flash pra você?" (intent: ORDER_PENDING_CONFIRMATION).
   - Só marque ORDER_DISPATCH se o cliente confirmar com clareza ("pode sim", "confirma", "manda ver").

7. FORMATAÇÃO:
   - NUNCA use bullet points (*, -, •).
   - Use no máximo 1 emoji amigável ou nenhum, mantendo a conversa humana e autêntica.

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
  "reply_text": "Texto simpático, humano e acolhedor para o cliente no WhatsApp",
  "target_sku": "SKU da peça identificada ou null",
  "requires_staff_alert": true | false,
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
                    "gemini-3.6-flash",
                    "gemini-3-flash-preview",
                    "gemini-3.8-flash",
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

        # 2.5 Elogios, reações amigáveis e feedback (evita resposta robótica repetitiva)
        is_compliment = any(
            w in msg
            for w in [
                "tá boa", "ta boa", "boa a resposta", "gostei", "economiza",
                "kkk", "top", "massa", "legal", "show", "valeu", "obrigado",
                "obg", "tmj", "abraço", "funcionou", "maravilha", "blz, tá top", "blz ta top"
            ]
        )
        if is_compliment:
            return {
                "intent": "GENERAL_QUESTION",
                "reply_text": "Show de bola, meu patrão! Ficamos à disposição aqui no balcão da Victor Cell. Precisando de qualquer peça, cotação ou retirada no balcão, é só chamar que a gente desenrola pra você! Tamo junto!",
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
                addr = conversation.notes or real_address or "Retirada no Balcão"
                if is_open:
                    reply = (
                        "Show de bola, meu patrão! Pedido confirmado com sucesso!\n\n"
                        f"Já deixei a peça reservada na bancada e os meninos do caixa já estão calculando a rota do Uber Flash para o endereço: {addr}.\n"
                        "Em 2 minutinhos te mandam o valor certinho do frete e o Pix para despachar, combinado?"
                    )
                else:
                    reply = (
                        "Show de bola, meu patrão! Pedido confirmado com sucesso!\n\n"
                        f"Como encerramos o expediente físico por hoje, a sua peça já ficou reservada na bancada prioritária de amanhã ({addr}).\n"
                        f"Às {settings.STORE_OPENING_TIME} os meninos do caixa cotam a rota e te mandam o Pix para despachar logo na primeira hora, combinado?"
                    )
                return {
                    "intent": "ORDER_DISPATCH",
                    "reply_text": reply,
                    "target_sku": sku,
                    "requires_staff_alert": True,
                    "destination_address": addr,
                    "handoff_reason": None,
                }
            else:
                # Cliente não confirmou (ex: desistiu, perguntou outra coisa, etc)
                return {
                    "intent": "GENERAL_QUESTION",
                    "reply_text": "Tranquilo meu amigo! Não confirmei a reserva. Qualquer dúvida ou se quiser que a gente separe alguma peça depois, é só dar um alô por aqui. Tamo junto!",
                    "target_sku": conversation.active_sku,
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

        # 4. Intenção Inicial de Pedido / Separação ou Envio de Endereço (NUNCA FECHA SEM CONFIRMAR)
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
                    "reply_text": "Com certeza, meu patrão! Me diz só qual modelo e peça você quer que a gente separe para você?",
                    "target_sku": None,
                    "requires_staff_alert": False,
                    "destination_address": None,
                    "handoff_reason": None,
                }

            if real_address:
                # Pergunta confirmação EXPLÍCITA ao cliente antes de criar o pedido!
                target_desc = "Original Nacional (R$ 190,00)" if "TEL-SAM-A15-ORIG" in (resolved_sku or "") else "peça solicitada"
                reply = (
                    f"Show de bola, meu patrão! Temos a pronta entrega. Já anotei o seu endereço de entrega: {real_address}.\n\n"
                    f"A tela {target_desc} tá pronta pra saída na bancada.\n"
                    "Posso confirmar o pedido para você e passar pros meninos do caixa cotarem o Uber Flash?"
                )
                return {
                    "intent": "ORDER_PENDING_CONFIRMATION",
                    "reply_text": reply,
                    "target_sku": resolved_sku,
                    "requires_staff_alert": False,
                    "destination_address": real_address,
                    "handoff_reason": None,
                }
            else:
                return {
                    "intent": "QUOTE",
                    "reply_text": (
                        "Opa, perfeito! Já deixo pré-anotada aqui no balcão.\n\n"
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

