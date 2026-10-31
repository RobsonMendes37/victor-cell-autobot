"""
Use Case: ProcessIncomingMessageUseCase
Core orchestrator following Clean Architecture.
Resolves:
- Self-silencing loop prevention via is_sent_by_bot check
- Conversational memory via active_sku persistence
- Order creation with exact quoted item and hold expiration
"""

import logging
from typing import Any, Dict, Optional

from domain.entities import ConversationState, ReservationOrder
from domain.gateways import AIServiceInterface, MessagingGatewayInterface
from domain.repositories import (
    ConversationRepositoryInterface,
    OrderRepositoryInterface,
    ProductRepositoryInterface,
)

logger = logging.getLogger("ProcessIncomingMessageUseCase")


class ProcessIncomingMessageUseCase:
    def __init__(
        self,
        conversation_repo: ConversationRepositoryInterface,
        product_repo: ProductRepositoryInterface,
        order_repo: OrderRepositoryInterface,
        messaging_gateway: MessagingGatewayInterface,
        ai_service: AIServiceInterface,
        sqlite_repo = None
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
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes business flow when an event arrives from WhatsApp.
        """
        clean_phone = "".join(filter(str.isdigit, customer_phone))
        if not clean_phone:
            return {"status": "INVALID_PHONE"}

        # 1. Proteção contra Loop: Se foi enviado pelo próprio bot, ignora o eco do webhook
        if from_me and message_id and self.sqlite_repo:
            if await self.sqlite_repo.is_sent_by_bot(message_id):
                logger.debug(f"Eco de mensagem própria do bot ignorado ({message_id})")
                return {"status": "SKIPPED_BOT_ECHO"}

        conversation = await self.conversation_repo.get_or_create(clean_phone)

        # 2. Se a mensagem foi enviada pelo dono/operador humano (celular da loja ou WhatsApp Web)
        if from_me:
            # Comando explícito de reativação da IA pelo dono
            if "#bot" in message_text.lower():
                conversation.resume_ai()
                await self.conversation_repo.save(conversation)
                logger.info(f"IA reativada manualmente para {clean_phone} pelo comando #bot.")
                return {"status": "AI_RESUMED"}

            # Qualquer outra mensagem enviada pelo humano silencia o bot imediatamente
            logger.info(f"Intervenção humana detectada no chat de {clean_phone}. Silenciando IA por 3 horas.")
            conversation.pause_for_human(duration_hours=3)
            await self.conversation_repo.save(conversation)
            return {"status": "PAUSED_BY_HUMAN_INTERVENTION"}

        # 3. Se a IA estiver em modo de silenciamento ativo (atendente humano no comando)
        if not conversation.is_ai_allowed():
            logger.info(f"Mensagem de {clean_phone} recebida, mas IA está pausada (atendimento humano em curso).")
            return {"status": "SKIPPED_HUMAN_IN_CONTROL"}

        # 4. Busca catálogo atualizado para fornecer contexto de estoque
        catalog = await self.product_repo.list_all()
        catalog_lines = []
        for p in catalog:
            frame_str = "com aro" if p.has_frame else "sem aro"
            catalog_lines.append(
                f"- SKU: {p.sku} | {p.name} | {p.quality.value} ({frame_str}) | Preço: R$ {p.price:.2f} | Estoque: {p.stock_quantity} un."
            )
        catalog_context = "\n".join(catalog_lines)

        # 5. Processamento Cognitivo via IA
        ai_decision = await self.ai_service.process_and_reply(
            conversation=conversation,
            user_message=message_text,
            catalog_context=catalog_context
        )

        reply_text = ai_decision.get("reply_text", "")
        intent = ai_decision.get("intent", "GENERAL_QUESTION")
        requires_staff_alert = ai_decision.get("requires_staff_alert", False)
        target_sku = ai_decision.get("target_sku") or conversation.active_sku
        destination_address = ai_decision.get("destination_address")

        # Atualiza a memória de peça em discussão se uma foi identificada
        if ai_decision.get("target_sku"):
            conversation.active_sku = ai_decision["target_sku"]

        # 6. Envia resposta cordial ao cliente
        if reply_text:
            await self.messaging_gateway.send_text(clean_phone, reply_text)

        # 7. Se o cliente fechou pedido de separação / Uber Flash, dispara alerta ao caixa
        order_created = False
        if intent == "ORDER_DISPATCH" and requires_staff_alert:
            final_sku = target_sku or conversation.active_sku or "TEL-SAM-A15-ORIG"
            product = await self.product_repo.get_by_sku(final_sku)
            prod_name = product.name if product else "Peça solicitada pelo cliente"
            prod_price = product.price if product else 0.0

            order = ReservationOrder(
                customer_phone=clean_phone,
                customer_name=push_name or "Cliente WhatsApp",
                product_sku=final_sku,
                quantity=1,
                product_price=prod_price,
                destination_address=destination_address or "A combinar pelo WhatsApp"
            )
            await self.order_repo.save_order(order)
            order_created = True

            # Notificação estruturada para os funcionários do balcão/caixa
            alert_msg = (
                f"🚨 *NOVO DESPACHO VIA UBER FLASH REQUISITADO!*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• *ID Pedido:* #{order.id}\n"
                f"• *Cliente:* {order.customer_name} ({clean_phone})\n"
                f"• *Peça a Separar:* {prod_name} (R$ {prod_price:.2f})\n"
                f"• *Endereço Entrega:* {order.destination_address}\n"
                f"• *Validade Reserva:* 2 Horas (até {order.expires_at.strftime('%H:%M')})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 *AÇÃO DOS MENINOS DO CAIXA:*\n"
                f"1. Cotar corrida no app do Uber Flash.\n"
                f"2. Mandar o valor do frete e a chave Pix pro cliente.\n"
                f"3. Separar a peça na bancada de saída."
            )
            await self.messaging_gateway.send_internal_staff_alert(alert_msg)
            conversation.state = ConversationState.WAITING_DISPATCH

        # 8. Se houve gatilho de transbordo (reclamação/desconto agressivo)
        elif intent == "HUMAN_HANDOFF":
            conversation.pause_for_human(duration_hours=2)
            handoff_alert = (
                f"⚠️ *ATENDIMENTO HUMANO SOLICITADO*\n"
                f"• Cliente: {push_name or 'Cliente'} ({clean_phone})\n"
                f"• Motivo: {ai_decision.get('handoff_reason', 'Negociação ou Dúvida Técnica')}\n"
                f"• Última mensagem: \"{message_text}\""
            )
            await self.messaging_gateway.send_internal_staff_alert(handoff_alert)

        # Salva estado atualizado da conversa
        await self.conversation_repo.save(conversation)

        return {
            "status": "SUCCESS",
            "intent": intent,
            "replied": bool(reply_text),
            "order_created": order_created,
            "target_sku": target_sku
        }
