"""
Test Suite for Intelligent AI Reopening.
Validates that:
1. When store is closed, AI auto-resumes to provide quotation and closed notice.
2. When human attendant paused AI, but 30 minutes elapsed and client asks for a new quote, AI resumes.
3. When inside the grace period with non-quote messages, AI remains silent for human operator.
"""

from datetime import datetime, timedelta, timezone

from domain.entities import Conversation, ConversationState


def test_ai_reopens_when_store_is_closed():
    conv = Conversation(
        id="conv-001",
        customer_phone="5585999990001",
        state=ConversationState.HUMAN_ACTIVE,
        human_resumed_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        human_silence_duration_hours=3,
    )

    # Durante o dia com loja aberta: respeita pausa humana
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="olá") is False

    # Loja fechada (noite ou domingo): auto-reabre para informar horário e passar cotações
    assert conv.is_ai_allowed(is_store_open=False, incoming_message="quanto tá a tela do t220?") is True
    assert conv.state == ConversationState.AI_ACTIVE
    assert conv.human_resumed_at is None


def test_ai_reopens_after_grace_period_with_new_quote_request():
    conv = Conversation(
        id="conv-002",
        customer_phone="5585999990002",
        state=ConversationState.HUMAN_ACTIVE,
        human_resumed_at=datetime.now(timezone.utc) - timedelta(minutes=35),  # 35 min atrás (> 30m)
        human_silence_duration_hours=3,
    )

    # Mensagem genérica não-cotação não reabre antes do timeout completo de 3h
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="obrigado amigo") is False

    # Mensagem de cotação de nova peça após a tolerância de 30 minutos: auto-reabre!
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="amigo tem a tela do tab a8?") is True
    assert conv.state == ConversationState.AI_ACTIVE
    assert conv.human_resumed_at is None


def test_ai_remains_paused_inside_grace_period():
    conv = Conversation(
        id="conv-003",
        customer_phone="5585999990003",
        state=ConversationState.HUMAN_ACTIVE,
        human_resumed_at=datetime.now(timezone.utc) - timedelta(minutes=5),  # Apenas 5 min atrás
        human_silence_duration_hours=3,
    )

    # Atendente acabou de falar: robô deve ficar em silêncio mesmo se o cliente cotar
    assert conv.is_ai_allowed(is_store_open=True, incoming_message="quanto tá a tela?") is False
    assert conv.state == ConversationState.HUMAN_ACTIVE
