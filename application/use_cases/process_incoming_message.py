"""
Use Case: ProcessIncomingMessageUseCase
Core orchestrator following Clean Architecture.
Features:
- Multi-turn conversation history persistence
- Multimodal support (audio/image)
- Stock deduction upon reservation
- Local Fortaleza timezone alerts
- Loop protection (anti-echo)
"""

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import pytz

from application.use_cases.catalog_search_service import CatalogSearchService
from domain.entities import (
    ConversationState,
    QualityTier,
    ReservationOrder,
)
from domain.gateways import AIServiceInterface, MessagingGatewayInterface
from domain.repositories import (
    ConversationRepositoryInterface,
    OrderRepositoryInterface,
    ProductRepositoryInterface,
)
from infrastructure.config import settings
from infrastructure.services.metrics_service import metrics_collector

logger = logging.getLogger("ProcessIncomingMessageUseCase")


class ProcessIncomingMessageUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryInterface,
        product_repo: ProductRepositoryInterface,
        order_repo: OrderRepositoryInterface,
        messaging_gateway: MessagingGatewayInterface,
        ai_service: AIServiceInterface,
        sqlite_repo=None,
        staff_dispatcher=None,
    ):
        self.conversation_repo = conversation_repo
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.messaging_gateway = messaging_gateway
        self.ai_service = ai_service
        self.sqlite_repo = sqlite_repo
        self.staff_dispatcher = staff_dispatcher

    async def execute(
        self,
        customer_phone: str,
        message_text: str,
        from_me: bool = False,
        push_name: Optional[str] = None,
        message_id: Optional[str] = None,
        media_bytes: Optional[bytes] = None,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        exec_start_time = time.time()
        metrics_collector.record_received()
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        if not clean_phone:
            return {"status": "INVALID_PHONE"}

        # 1. Proteção contra Loop: Se foi enviado pelo próprio bot, ignora o eco
        if from_me and message_id and self.sqlite_repo:
            if await self.sqlite_repo.is_sent_by_bot(message_id):
                logger.debug(f"Eco de mensagem própria do bot ignorado ({message_id})")
                return {"status": "SKIPPED_BOT_ECHO"}

        conversation = await self.conversation_repo.get_or_create(clean_phone)
        if push_name and push_name != "Cliente" and (not conversation.customer_name or conversation.customer_name in ["Cliente WhatsApp", "Cliente"]):
            conversation.customer_name = push_name
            await self.conversation_repo.save(conversation)

        # 2. Se a mensagem foi enviada pelo dono no celular pessoal ou WhatsApp Web
        if from_me:
            if "#bot" in message_text.lower():
                conversation.resume_ai()
                await self.conversation_repo.save(conversation)
                logger.info(f"IA reativada manualmente para {clean_phone} pelo comando #bot.")
                return {"status": "AI_RESUMED"}

            logger.info(
                f"Intervenção humana detectada no chat de {clean_phone}. Silenciando IA por 3 horas."
            )
            conversation.pause_for_human(duration_hours=3)
            await self.conversation_repo.save(conversation)
            return {"status": "PAUSED_BY_HUMAN_INTERVENTION"}

        # 3. Se a IA estiver silenciada por atendimento humano em curso
        if not conversation.is_ai_allowed():
            logger.info(
                f"Mensagem de {clean_phone} recebida, mas IA está pausada (humano no controle)."
            )
            return {"status": "SKIPPED_HUMAN_IN_CONTROL"}

        # 4. Timeout de sessão e contexto (limpa após 2 horas de inatividade)
        now_utc = datetime.now(timezone.utc)
        if conversation.last_activity_at:
            time_since_last = now_utc - conversation.last_activity_at
            if time_since_last > timedelta(hours=settings.ACTIVE_SKU_TIMEOUT_HOURS):
                logger.info(
                    f"Sessão expirada para {clean_phone} após {time_since_last}. "
                    "Resetando contexto ativo (peça, confirmações pendentes e notas)."
                )
                conversation.active_sku = None
                if conversation.state == ConversationState.WAITING_CONFIRMATION:
                    conversation.state = ConversationState.AI_ACTIVE
                conversation.notes = None

        conversation.last_activity_at = now_utc

        # 5. Carrega histórico recente da sessão ativa (Multi-Turn limitado a 2 horas)
        recent_history = []
        if hasattr(self.conversation_repo, "get_recent_messages"):
            recent_history = await self.conversation_repo.get_recent_messages(
                clean_phone, limit=8, max_age_hours=settings.ACTIVE_SKU_TIMEOUT_HOURS
            )
        # 6. Carrega catálogo atualizado
        catalog = await self.product_repo.list_all()
        catalog_lines = []
        for p in catalog:
            frame_str = "com aro" if p.has_frame else "sem aro"
            status_str = "DISPONÍVEL (TEM EM ESTOQUE)" if p.is_in_stock else "ESGOTADO (EM FALTA NO MOMENTO)"
            catalog_lines.append(
                f"- SKU: {p.sku} | {p.name} | {p.quality.value} ({frame_str}) | Preço: R$ {p.price:.2f} | Status: {status_str}"
            )
        catalog_context = "\n".join(catalog_lines)

        # 6.1 Recupera pedidos recentes para contextualizar rastreio/pós-venda
        customer_orders_context = None
        recent_orders = []
        if hasattr(self.order_repo, "get_recent_orders_by_phone"):
            recent_orders = await self.order_repo.get_recent_orders_by_phone(clean_phone, limit=3)
        elif self.sqlite_repo and hasattr(self.sqlite_repo, "get_recent_orders_by_phone"):
            recent_orders = await self.sqlite_repo.get_recent_orders_by_phone(clean_phone, limit=3)

        if recent_orders:
            order_lines = []
            for o in recent_orders:
                order_lines.append(
                    f"Pedido #{o.id} - SKU: {o.product_sku} - Status: {o.status.value} - Destino: {o.destination_address or 'Balcão'}"
                )
            customer_orders_context = chr(10).join(order_lines)

        # 6.2 Recupera StoreProfile dinâmico para Whitelabel / Multi-tenant
        store_profile = None
        if self.sqlite_repo and hasattr(self.sqlite_repo, "get_store_profile"):
            try:
                store_profile = await self.sqlite_repo.get_store_profile("default")
            except Exception:
                pass

        # 7. Processamento Cognitivo via Gemini
        ai_decision = await self.ai_service.process_and_reply(
            conversation=conversation,
            user_message=message_text,
            catalog_context=catalog_context,
            history=recent_history,
            media_bytes=media_bytes,
            mime_type=mime_type,
            customer_orders_context=customer_orders_context,
            store_profile=store_profile,
        )

        reply_text = ai_decision.get("reply_text", "")
        intent = ai_decision.get("intent", "GENERAL_QUESTION")
        ai_decision.get("requires_staff_alert", False)
        target_sku = ai_decision.get("target_sku") or conversation.active_sku
        destination_address = ai_decision.get("destination_address")

        # Fallback semântico inteligente: se a IA cotou mas omitiu o SKU, busca correspondência com CatalogSearchService e fuzzy matching
        if not target_sku and intent in ["QUOTE", "ORDER_PENDING_CONFIRMATION"]:
            fuzzy_matches = CatalogSearchService.search_best_matches(catalog, message_text, min_threshold=0.65)
            if fuzzy_matches:
                target_sku = fuzzy_matches[0][0].sku
            else:
                stop_words = {"quanto", "valor", "preço", "preco", "amigo", "patrão", "patrao", "bom", "dia", "tarde", "noite", "olá", "ola", "você", "voce", "tem", "essa", "pode", "separar", "manda", "uber"}
                tokens = [w.strip("?,.!:;") for w in message_text.split() if len(w) >= 3 and w.lower() not in stop_words]
                for token in tokens:
                    matches = await self.product_repo.search(token)
                    if matches:
                        if any(k in message_text.lower() for k in ["tela", "display"]):
                            matches = [m for m in matches if any(t in m.name.lower() for t in ["tela", "display", "touch"])]
                        elif "touch" in message_text.lower():
                            matches = [m for m in matches if "touch" in m.name.lower()]
                        elif "bateria" in message_text.lower():
                            matches = [m for m in matches if "bateria" in m.name.lower()]

                        if "original" in message_text.lower():
                            matches = [m for m in matches if getattr(m, 'quality', None) == QualityTier.ORIGINAL_NACIONAL]
                        elif "paralela" in message_text.lower():
                            matches = [m for m in matches if getattr(m, 'quality', None) == QualityTier.PARALELA_CHINA]

                        if len(matches) == 1:
                            target_sku = matches[0].sku
                            break

        # Regra de Ouro: Transbordo para atendimento humano NUNCA responde nada ao cliente. É só passar!
        if intent == "HUMAN_HANDOFF":
            reply_text = ""

        if target_sku:
            conversation.active_sku = target_sku

        # 8. Persiste a mensagem do cliente e a resposta no histórico multi-turn
        if hasattr(self.conversation_repo, "save_message"):
            await self.conversation_repo.save_message(clean_phone, "user", message_text)
            if reply_text:
                await self.conversation_repo.save_message(clean_phone, "model", reply_text)

        # 9. Envia resposta ao cliente
        if reply_text:
            await self.messaging_gateway.send_text(clean_phone, reply_text)

        # Ao realizar nova cotação ou pergunta geral, garante que a conversa está em AI_ACTIVE e limpa notas antigas
        if intent in ["QUOTE", "GENERAL_QUESTION"]:
            conversation.state = ConversationState.AI_ACTIVE
            if intent == "QUOTE":
                conversation.notes = None

        # 10. Proteção de Ouro: ORDER_DISPATCH EXIGE que a conversa estivesse em WAITING_CONFIRMATION
        # NUNCA cria pedido na primeira menção ou sem confirmação prévia explícita
        if intent == "ORDER_DISPATCH":
            if conversation.state != ConversationState.WAITING_CONFIRMATION or (not destination_address and not conversation.notes):
                logger.info(
                    f"Downgrade ORDER_DISPATCH -> ORDER_PENDING_CONFIRMATION para {clean_phone} (estado={conversation.state.value}, sem confirmação em 2 etapas)"
                )
                intent = "ORDER_PENDING_CONFIRMATION"

        order_created = False
        if intent == "ORDER_PENDING_CONFIRMATION":
            conversation.state = ConversationState.WAITING_CONFIRMATION
            conversation.active_sku = target_sku or conversation.active_sku
            if destination_address:
                conversation.notes = destination_address
            order_created = False
            logger.info(f"Conversa com {clean_phone} em WAITING_CONFIRMATION (endereço pré-anotado: {destination_address})")

            # Se o cliente pediu para deixar no balcão ou separar, notifica o celular do atendente
            if any(w in message_text.lower() for w in ["balcão", "balcao", "buscar", "pegar", "passo aí", "passo ai", "separa", "separar"]):
                sku_desc = target_sku or conversation.active_sku or "Peça consultada"
                balcao_alert = (
                    f"📦 *CLIENTE PEDINDO PRA SEPARAR NO BALCÃO!*\n"
                    f"• Cliente: {push_name or 'Cliente'} ({clean_phone})\n"
                    f"• Peça: {sku_desc}\n"
                    f'• Mensagem do cliente: "{message_text}"\n'
                    f"👉 *Verifique na bancada e assuma a conversa no WhatsApp!*"
                )
                await self.messaging_gateway.send_internal_staff_alert(
                    alert_text=balcao_alert,
                    title=f"📦 SEPARAR BALCÃO: {push_name or 'Cliente'}",
                    customer_phone=clean_phone,
                    priority="urgent",
                    tags="package,person,bell",
                )
                if self.staff_dispatcher:
                    try:
                        await self.staff_dispatcher.notify_handoff(
                            customer_phone=clean_phone,
                            reason="Separação no Balcão Solicitada",
                            raw_message=message_text,
                            customer_name=push_name,
                        )
                    except Exception as e:
                        logger.warning(f"Erro no staff_dispatcher balcão: {e}")

        # 11. Se o cliente CONFIRMOU explicitamente e fechou o pedido de separação
        elif intent == "ORDER_DISPATCH":
            final_sku = target_sku or conversation.active_sku or "TEL-SAM-A15-ORIG"
            target_sku = final_sku
            final_address = destination_address or conversation.notes or "Retirada no Balcão"
            product = await self.product_repo.get_by_sku(final_sku)
            prod_name = product.name if product else "Peça solicitada pelo cliente"
            prod_price = product.price if product else 0.0

            order = ReservationOrder(
                customer_phone=clean_phone,
                customer_name=push_name or "Cliente WhatsApp",
                product_sku=final_sku,
                quantity=1,
                product_price=prod_price,
                destination_address=final_address,
            )
            await self.order_repo.save_order(order)
            order_created = True

            # Baixa automática do estoque
            await self.product_repo.decrement_stock(final_sku, quantity=1)

            # Formata validade da reserva no Fuso Horário de Fortaleza (UTC-3)
            fortaleza_tz = pytz.timezone(settings.STORE_TIMEZONE)
            expires_local = order.expires_at.astimezone(fortaleza_tz)
            expires_str = expires_local.strftime("%H:%M")

            alert_msg = (
                f"🚨 *NOVO DESPACHO VIA UBER FLASH CONFIRMADO PELO CLIENTE!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• *ID Pedido:* #{order.id}\n"
                f"• *Cliente:* {order.customer_name} ({clean_phone})\n"
                f"• *Peça a Separar:* {prod_name} (R$ {prod_price:.2f})\n"
                f"• *Endereço Entrega:* {order.destination_address}\n"
                f"• *Validade Reserva:* 2 Horas (até {expires_str})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 *AÇÃO DOS MENINOS DO CAIXA:*\n"
                f"1. Cotar corrida no app do Uber Flash.\n"
                f"2. Mandar o valor do frete e a chave Pix pro cliente.\n"
                f"3. Separar a peça na bancada de saída."
            )
            await self.messaging_gateway.send_internal_staff_alert(
                alert_text=alert_msg,
                title=f"📦 SEPARAR PEÇA: {prod_name}",
                customer_phone=clean_phone,
                priority="urgent",
                tags="package,rotating_light,motorcycle",
            )
            if self.staff_dispatcher:
                try:
                    await self.staff_dispatcher.notify_dispatch_order(
                        order_id=order.id,
                        customer_phone=clean_phone,
                        product_desc=f"{prod_name} (R$ {prod_price:.2f})",
                        destination_address=final_address,
                        customer_name=order.customer_name,
                    )
                except Exception as e:
                    logger.warning(f"Erro no staff_dispatcher dispatch: {e}")
            conversation.state = ConversationState.WAITING_DISPATCH
            conversation.notes = None

        elif intent == "HUMAN_HANDOFF":
            conversation.pause_for_human(duration_hours=3)
            handoff_alert = (
                f"⚠️ *ATENDIMENTO HUMANO SOLICITADO (TRANSFERÊNCIA DIRETA)*\n"
                f"• Cliente: {push_name or 'Cliente'} ({clean_phone})\n"
                f"• Motivo: {ai_decision.get('handoff_reason', 'Negociação ou Dúvida Técnica')}\n"
                f'• Mensagem do cliente: "{message_text}"\n'
                f"👉 *A IA NÃO respondeu ao cliente. Por favor, assuma e responda diretamente no WhatsApp!*"
            )
            await self.messaging_gateway.send_internal_staff_alert(
                alert_text=handoff_alert,
                title=f"⚠️ ATENDIMENTO: {push_name or 'Cliente'}",
                customer_phone=clean_phone,
                priority="urgent",
                tags="warning,phone,person",
            )
            if self.staff_dispatcher:
                try:
                    await self.staff_dispatcher.notify_handoff(
                        customer_phone=clean_phone,
                        reason=ai_decision.get("handoff_reason", "Negociação ou Dúvida Técnica"),
                        raw_message=message_text,
                        customer_name=push_name,
                    )
                except Exception as e:
                    logger.warning(f"Erro no staff_dispatcher handoff: {e}")

        await self.conversation_repo.save(conversation)

        exec_duration = time.time() - exec_start_time
        metrics_collector.record_processed(exec_duration, replied_by_ai=True)
        if intent == "HUMAN_HANDOFF":
            metrics_collector.record_handoff()
        if order_created:
            metrics_collector.record_order_created()

        return {
            "status": "SUCCESS",
            "intent": intent,
            "replied": bool(reply_text),
            "reply": reply_text,
            "order_created": order_created,
            "target_sku": target_sku,
        }
