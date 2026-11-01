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
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import pytz

from domain.entities import (
    ConversationState,
    ReservationOrder,
)
from domain.gateways import AIServiceInterface, MessagingGatewayInterface
from domain.repositories import (
    ConversationRepositoryInterface,
    OrderRepositoryInterface,
    ProductRepositoryInterface,
)
from infrastructure.config import settings

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
    ):
        self.conversation_repo = conversation_repo
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.messaging_gateway = messaging_gateway
        self.ai_service = ai_service
        self.sqlite_repo = sqlite_repo

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

        # 7. Processamento Cognitivo via Gemini
        ai_decision = await self.ai_service.process_and_reply(
            conversation=conversation,
            user_message=message_text,
            catalog_context=catalog_context,
            history=recent_history,
            media_bytes=media_bytes,
            mime_type=mime_type,
        )

        reply_text = ai_decision.get("reply_text", "")
        intent = ai_decision.get("intent", "GENERAL_QUESTION")
        requires_staff_alert = ai_decision.get("requires_staff_alert", False)
        target_sku = ai_decision.get("target_sku") or conversation.active_sku
        destination_address = ai_decision.get("destination_address")

        if ai_decision.get("target_sku"):
            conversation.active_sku = ai_decision["target_sku"]

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
                requires_staff_alert = False

        order_created = False
        if intent == "ORDER_PENDING_CONFIRMATION":
            conversation.state = ConversationState.WAITING_CONFIRMATION
            conversation.active_sku = target_sku or conversation.active_sku
            if destination_address:
                conversation.notes = destination_address
            order_created = False
            logger.info(f"Conversa com {clean_phone} em WAITING_CONFIRMATION (endereço pré-anotado: {destination_address})")

        # 11. Se o cliente CONFIRMOU explicitamente e fechou o pedido de separação
        elif intent == "ORDER_DISPATCH" and requires_staff_alert:
            final_sku = target_sku or conversation.active_sku or "TEL-SAM-A15-ORIG"
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
            await self.messaging_gateway.send_internal_staff_alert(alert_msg)
            conversation.state = ConversationState.WAITING_DISPATCH
            conversation.notes = None

        elif intent == "HUMAN_HANDOFF":
            conversation.pause_for_human(duration_hours=2)
            handoff_alert = (
                f"⚠️ *ATENDIMENTO HUMANO SOLICITADO*\n"
                f"• Cliente: {push_name or 'Cliente'} ({clean_phone})\n"
                f"• Motivo: {ai_decision.get('handoff_reason', 'Negociação ou Dúvida Técnica')}\n"
                f'• Última mensagem: "{message_text}"'
            )
            await self.messaging_gateway.send_internal_staff_alert(handoff_alert)

        await self.conversation_repo.save(conversation)

        return {
            "status": "SUCCESS",
            "intent": intent,
            "replied": bool(reply_text),
            "reply": reply_text,
            "order_created": order_created,
            "target_sku": target_sku,
        }
