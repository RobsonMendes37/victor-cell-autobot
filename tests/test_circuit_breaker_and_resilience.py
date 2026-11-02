"""
Test Suite for Circuit Breaker and Cloud Resilience.
Validates state transitions (CLOSED -> OPEN -> HALF_OPEN -> CLOSED),
fast fallback under outage, and diagnostics reporting.
"""

import time

import pytest

from domain.entities import Conversation
from infrastructure.services.agent_service import AIAgentService
from infrastructure.services.circuit_breaker import (
    CircuitBreaker,
    CircuitState,
)


def test_circuit_breaker_initial_state():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=2.0, name="TestBreaker")
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True
    assert cb.failure_count == 0
    assert cb.total_trips == 0


def test_circuit_breaker_trips_to_open_after_threshold():
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=2.0, name="TestBreaker")

    cb.record_failure(RuntimeError("API Error 1"))
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    cb.record_failure(RuntimeError("API Error 2"))
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # Terceira falha: atinge o threshold e abre o circuito
    cb.record_failure(RuntimeError("API Error 3 (Quota 429)"))
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False
    assert cb.total_trips == 1


def test_circuit_breaker_transitions_to_half_open_after_timeout():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=0.1, name="FastBreaker")

    cb.record_failure(RuntimeError("Fail 1"))
    cb.record_failure(RuntimeError("Fail 2"))
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Aguarda expirar a janela de recuperação
    time.sleep(0.15)

    # Ao checar can_execute(), transita para HALF_OPEN
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN


def test_circuit_breaker_recovers_to_closed_on_half_open_success():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=0.1, name="RecoverBreaker")

    cb.record_failure(RuntimeError("Err 1"))
    cb.record_failure(RuntimeError("Err 2"))
    assert cb.state == CircuitState.OPEN

    time.sleep(0.12)
    assert cb.can_execute() is True  # Transita para HALF_OPEN

    # Sucesso na chamada de teste: recupera o circuito
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0


def test_circuit_breaker_reopens_on_half_open_failure():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=0.1, name="ReopenBreaker")

    cb.record_failure(RuntimeError("Err 1"))
    cb.record_failure(RuntimeError("Err 2"))
    assert cb.state == CircuitState.OPEN

    time.sleep(0.12)
    assert cb.can_execute() is True  # Transita para HALF_OPEN

    # Falha durante teste: reabre imediatamente
    cb.record_failure(RuntimeError("Still Down"))
    assert cb.state == CircuitState.OPEN
    assert cb.total_trips == 2


def test_circuit_breaker_manual_reset_and_stats():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=60.0, name="StatsBreaker")
    cb.record_failure(RuntimeError("Err"))
    cb.record_failure(RuntimeError("Err"))
    assert cb.state == CircuitState.OPEN

    stats = cb.get_stats()
    assert stats["name"] == "StatsBreaker"
    assert stats["state"] == "OPEN"
    assert stats["failure_count"] == 2
    assert stats["can_execute"] is False
    assert stats["remaining_lockout_seconds"] > 0

    cb.reset()
    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True


@pytest.mark.asyncio
async def test_agent_service_uses_circuit_breaker_fast_fallback():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout_seconds=60.0, name="MockBreaker")
    cb.record_failure(RuntimeError("Simulated Quota Limit"))
    assert cb.state == CircuitState.OPEN

    agent = AIAgentService(circuit_breaker=cb)
    conv = Conversation(id="conv-123", customer_phone="5585999990000")

    # Mesmo que a IA remota esteja offline, o circuit breaker desvia instantaneamente pro fallback
    reply = await agent.process_and_reply(
        conversation=conv,
        user_message="quanto tá a tela do a7 lite",
        catalog_context="TELA A7 LITE: R$ 120",
    )

    assert isinstance(reply, dict)
    assert "reply_text" in reply
    assert agent.get_circuit_stats()["state"] == "OPEN"
