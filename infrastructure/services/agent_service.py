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
6. FLUXO OBRIGATÓRIO DE PEDIDO E CONFIRMAÇÃO (MUITO IMPORTANTE):
   - REGRA DE OURO: NUNCA crie ou finalize um pedido ("ORDER_DISPATCH") na primeira mensagem do cliente!
   - Se o cliente perguntar se entrega, cotar Uber ou mandar endereço (ex: "Pode mandar pro Centro? Rua Floriano, 1250"):
     1. Informe o valor da peça e anote o endereço.
     2. PERGUNTE EXPLICITAMENTE: "Posso confirmar a reserva da peça para você e passar pros meninos do caixa cotarem o Uber Flash?"
     3. Defina a intent como "ORDER_PENDING_CONFIRMATION" (requires_staff_alert: false).
   - SOMENTE defina "ORDER_DISPATCH" (requires_staff_alert: true) se o cliente responder SIM CONFIRMANDO de forma clara (ex: "pode sim", "pode confirmar", "manda ver", "separa aí", "vou querer").
   - Elogios, risadas e mensagens curtas ("tá boa a resposta", "show", "kkk", "valeu", "economiza um funcionário") NUNCA são confirmações de pedido! Responda com simpatia e cordialidade.
7. RETORNO DE CLIENTE E CONTINUIDADE CONVERSACIONAL:
   - O histórico de mensagens pode conter conversas de horas ou dias atrás marcadas com carimbos como '[Há 3h]', '[Ontem]' ou '[Agora]'. Use essa memória com naturalidade!
   - Se o cliente retomar uma cotação antiga ("Lembra daquela tela que perguntei?"), demonstre que lembra da peça com cordialidade, mas confira novamente o estoque atualizado antes de fechar.
   - Se o cliente mandar apenas uma saudação isolada ("Opa", "Bom dia"), cumprimente com alegria de balcão e pergunte em que pode ajudar hoje.
8. RASTREIO E DÚVIDAS DE PÓS-VENDA:
   - Se o cliente perguntar "E aí, deu certo?", "Já despachou?", "Cadê o motoca/Uber?", "O produto já chegou?", "Já expediu?":
     Consulte a seção 'HISTÓRICO DE PEDIDOS DO CLIENTE' abaixo.
     Se houver um pedido recente, informe o status com precisão, calma e simpatia cearense (ex: "Opa meu patrão! O seu pedido da tela do A15 já tá na bancada e os meninos do caixa já estão agilizando a saída do Uber Flash para o seu endereço!").
     Defina a intent como "GENERAL_QUESTION" (requires_staff_alert: false), pois o pedido já foi criado anteriormente e não deve gerar alerta duplicado ao caixa.
   - Se o cliente perguntar de garantia ou tirar dúvidas técnicas da peça instalada: responda cordialmente lembrando os 90 dias de garantia para peças originais ou teste de bancada para paralelas.

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
  "reply_text": "Texto para o cliente no WhatsApp",
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
        system_instruction = f"""Você é o Copiloto Executivo de Operações e Vendas da Victor Cell (Fortaleza/CE).
Você atua como um Consultor Estratégico Sênior (Padrão Google / Big Tech / Power BI) assessorando diretamente o dono da loja e os gestores em decisões comerciais, operacionais e de estoque.

DIRETRIZES FUNDAMENTAIS DE ANÁLISE:
1. PRECISÃO FOCADA EM DADOS: Baseie suas análises 100% no CONTEXTO OPERACIONAL EM TEMPO REAL fornecido abaixo. Não invente números, valores de faturamento nem itens que não constem no relatório.
2. COMUNICAÇÃO EXECUTIVA DE ALTO IMPACTO:
   - Seja direto, claro, perspicaz e proativo.
   - Use formatação markdown elegante: destaques em negrito (ex: **R$ 570,00**), tópicos concisos e emojis profissionais discretos (📊, ⚠️, 🛵, 💰, 💡, 👥).
   - Se o gestor perguntar "Como foi o dia?" ou "Vendemos muito?", estruture a resposta com:
     * 📊 Resumo Executivo (Faturamento, Total de Pedidos e Ticket Médio).
     * ⭐ Destaques de Venda & Uber Flash (Peças mais vendidas e percentual de entregas).
     * ⚠️ Atenção Imediata (Rupturas ou estoques baixos de peças com alta procura).
     * 💡 Plano de Ação Rápido (1 a 3 sugestões práticas para maximizar o lucro).
3. MONITORAMENTO DE RUPTURA: Se houver produtos com estoque zerado ou <= 2 unidades, aponte imediatamente a necessidade de reposição preventiva junto aos fornecedores do Centro de Fortaleza.
4. ATENDIMENTOS NO BALCÃO: Analise a proporção de atendimentos feitos pelo robô vs. clientes que precisaram de atendimento humano, apontando peças quentes sendo cotadas.
5. RESPOSTA EM TEXTO RICO: Responda em texto corrido com Markdown (não responda em JSON), pronto para exibição no painel executivo.

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

        # Fallback offline
        return (
            "📊 **Resumo Operacional Victor Cell (Modo Offline)**\n\n"
            "• Os dados em tempo real estão sincronizados no seu painel.\n"
            "• Verifique as abas de *Expedição & Uber Flash* para pedidos do dia e *Estoque & Catálogo* para peças com saldo baixo.\n"
            "• Para ativar análises avançadas com IA, verifique sua cota da API Gemini na aba de configurações."
        )

